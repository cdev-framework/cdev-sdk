from time import sleep
from typing import Dict

from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import xlambda as simple_lambda
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from cdev.output import print_deployment_step


from ..aws import aws_client as raw_aws_client
from boto3.s3.transfer import TransferConfig


from .lambda_event_deployer import EVENT_TO_HANDLERS
from .lambda_role_deployer import create_role_with_permissions, delete_role_and_permissions, add_policy, delete_policy

from cdev.settings import SETTINGS
import os


log = logger.get_cdev_logger(__name__)

BUCKET = SETTINGS.get("S3_ARTIFACTS_BUCKET")


def _create_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Steps for creating a deployed lambda function
    # 1. Create IAM Role with needed permissions (note this is first to give aws more time to create the role in all regions and be available for use)
    # 2. Upload the artifact to S3 as the archive location
    # 3. Upload dependencies if needed
    # 4. Create the function
    # 5. Create any integrations that are need based on Events passed in
    print_deployment_step("CREATE", f"Creating lambda function resources for lambda {resource.name}")
    
    log.debug(f"Attempting to create {resource}")
    final_info = {
        "ruuid": resource.ruuid,
        "cdev_name": resource.name,
    }



    # Step 1
    role_name = f"lambda_{resource.function_name}"
    permission_info = create_role_with_permissions(role_name, resource.permissions)
    print_deployment_step("CREATE", f"  Create role for lambda function {resource.name}")

    role_arn = permission_info[0]

    final_info['role_name'] = role_name
    final_info['role_id'] = role_arn
    final_info['permissions'] = permission_info[1]

    # Step 2
    keyname = _upload_s3_code_artifact(resource)
    print_deployment_step("CREATE", f"  Upload code for lambda function {resource.name}")
   
    final_info['artifact_bucket'] = BUCKET
    final_info['artifact_key'] = keyname

    # Step 3
    if resource.external_dependencies_info:
        print_deployment_step("CREATE", f"  Creating dependencies for lambda function {resource.name}")
        cloud_dependency_info = []
        rv = _create_dependency(resource, resource.external_dependencies_info)
        cloud_dependency_info.append(rv)

        

        final_info['layers'] = cloud_dependency_info
    
    # Step 4
    # TODO
    print_deployment_step("CREATE", f"  [blink]Waiting for role to finish creating (~10s)[/blink]")
    sleep(10)
    # ughhhh add a retry wrapper because it takes time to generate the IAM roles across all regions so we need to wait a few seconds to create this 
    lambda_function_args = {
        "FunctionName": resource.function_name,
        "Runtime": 'python3.7',
        "Role": role_arn,
        "Handler": resource.configuration.Handler,
        "Code": {"S3Bucket":BUCKET, "S3Key":keyname},
        "Environment": resource.configuration.Environment.dict() if resource.configuration.Environment else {},
        "Layers": [f'{x.get("arn")}:{x.get("version")}' for x in final_info.get('layers')] if final_info.get('layers') else []
    }

    lambda_function_rv = raw_aws_client.run_client_function("lambda", "create_function", lambda_function_args)

    final_info['cloud_id'] = lambda_function_rv.get("FunctionArn")

    # Step 5
    log.debug(f"lambda events -> {resource.events}")
    if resource.events:
        event_hash_to_output = {}
        for event in resource.events:
            log.debug(f"Adding event -> {event}")

            key =  event.event_type
            log.debug(key)
            if not key in EVENT_TO_HANDLERS:
                raise Exception

            
            output = EVENT_TO_HANDLERS.get(key).get("CREATE")(event, final_info.get("cloud_id"))
            event_hash_to_output[event.get_hash()] = output
            print_deployment_step("CREATE", f"  Create event {event.event_type.value} {event.original_resource_name} for lambda {resource.name}")

        final_info['events'] = event_hash_to_output


    cdev_cloud_mapper.add_identifier(identifier)
    cdev_cloud_mapper.update_output_value(identifier, final_info)
    print_deployment_step("CREATE", f"  Created lambda function resources for lambda {resource.name}")
    return True


def _upload_s3_code_artifact(resource: simple_lambda.simple_aws_lambda_function_model) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = resource.function_name + f"-{resource.hash}" + ".zip"
    #original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = resource.filepath
    
    log.debug(f"artifact keyname {keyname}; ondisk location {zip_location}; is valid file {os.path.isfile(zip_location)}")

    if not os.path.isfile(zip_location):
        #TODO better exception
        log.error(f"bad archive local path given {zip_location}")
        raise Exception



    log.debug(f"upload artifact to s3")
    with open(zip_location, "rb") as fh:
        object_args = {
            "Bucket": BUCKET,
            "Key": keyname,
            "Body": fh.read(),

        }
        raw_aws_client.run_client_function("s3", "put_object", object_args)

    return keyname

def _create_dependency(resource: simple_lambda.simple_aws_lambda_function_model, dependency: Dict) -> Dict:
    key_name = _upload_s3_dependency(resource, dependency)

    # key name will always include .zip so remove that part and change '-' into '_'
    layer_name = key_name.replace("-", "_")[:-4]
    dependency_rv = raw_aws_client.run_client_function("lambda", "publish_layer_version", {
        "Content": {
            "S3Bucket": BUCKET,
            "S3Key": key_name
        },
        "LayerName": layer_name,
        "CompatibleRuntimes": [
            "python3.6",
            "python3.7",
            "python3.8",
            
        ]
    })

    return {
        "arn": dependency_rv.get("LayerArn"),
        "S3bucket": BUCKET,
        "S3key": key_name,
        "version": dependency_rv.get("Version"),
        "name": layer_name,
        "hash": dependency.get("hash")
    }


def _remove_dependency(dependency_cloud_info: Dict):
    raw_aws_client.run_client_function("lambda", "delete_layer_version", {
        "LayerName": dependency_cloud_info.get("name"),
        "VersionNumber": dependency_cloud_info.get("version")
    })


def _upload_s3_dependency(resource: simple_lambda.simple_aws_lambda_function_model, dependency: Dict) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = dependency.get('name') + f"-{resource.hash}" + ".zip"
    #original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = dependency.get('artifact_path')
    
    log.debug(f"artifact keyname {keyname}; ondisk location {zip_location}; is valid file {os.path.isfile(zip_location)}")

    if not os.path.isfile(zip_location):
        #TODO better exception
        log.error(f"bad archive local path given {zip_location}")
        raise Exception

    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)


    log.debug(f"upload artifact to s3")
    
    object_args = {
        "Bucket": BUCKET,
        "Key": keyname,
        "Filename": zip_location,
        "Callback": lambda x: print(x),
        "Config": config,
    }
    raw_aws_client.run_client_function("s3", "upload_file", object_args)

    return keyname


def _remove_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Steps:
    # Remove and event that is on the function to make sure resources are properly cleaned up
    # Remove the actual function
    # Remove the role associated with the function
    print_deployment_step("DELETE", f"Removing resources for lambda {resource.name}")
    log.debug(f"Attempting to delete {resource}")
    cloud_id = cdev_cloud_mapper.get_output_value_by_hash(resource.hash, "cloud_id")
    log.debug(f"Current function ARN {cloud_id}")

    for event in resource.events:
        casted_event = simple_lambda.Event(**event)

        key =  casted_event.event_type

        if not key in EVENT_TO_HANDLERS:
            raise Exception
        
        output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(casted_event, resource.hash)
        print_deployment_step("DELETE", f"  Remove event {casted_event.event_type.value} {casted_event.original_resource_name} for lambda {resource.name}")

    raw_aws_client.run_client_function("lambda", "delete_function", {"FunctionName": cloud_id})
    print_deployment_step("DELETE", f"  Remove lambda function {resource.name}")
    log.debug(f"Delete function")

    role_name = cdev_cloud_mapper.get_output_value_by_hash(resource.hash, "role_name")
    permissions = cdev_cloud_mapper.get_output_value_by_hash(resource.hash, "permissions")

    log.debug(f"Attemping to delete role {role_name} and permissions {permissions}")
    delete_role_and_permissions(role_name, [v for _,v in permissions.items()])
    print_deployment_step("DELETE", f"  Remove role for lambda function {resource.name}")

    log.debug(f"Attempting to delete dependencies")
    dependencies_info = cdev_cloud_mapper.get_output_value_by_hash(resource.hash, "layers")
    if dependencies_info:
        for dependency_info in dependencies_info:
            _remove_dependency(dependency_info)

        print_deployment_step("DELETE", f"  Remove dependencies for lambda function {resource.name}")

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    print_deployment_step("DELETE", f"  Removed resources for lambda {resource.name}")
    return True


def _update_simple_lambda(previous_resource: simple_lambda.simple_aws_lambda_function_model,  new_resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Updates can be of:
    # Update source code or dependencies
    # Update configuration
    # Update events
    print_deployment_step("UPDATE", f"Updating lambda function {new_resource.name}")
    did_update_permission = False
    updated_info = {

    }
    log.debug(previous_resource)
    # TODO all configurations
    if not previous_resource.config_hash == new_resource.config_hash:
        if not previous_resource.configuration.get("Environment") == new_resource.configuration.Environment:
            log.debug(f"UPDATE ENVIRONMENT VARIABLES: {previous_resource.configuration.get('Environment')} -> {new_resource.configuration.Environment}")
            raw_aws_client.run_client_function("lambda", "update_function_configuration", {
                "FunctionName": cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "cloud_id"),
                "Environment": new_resource.configuration.Environment.dict()
            })

            print_deployment_step("UPDATE", f"  Update environment variabels for lambda function {new_resource.name}")
        

    if not previous_resource.permissions_hash == new_resource.permissions_hash:
        did_update_permission = True
        previous_hashes = set([simple_lambda.Permission(**x).get_hash() if "resource" in x else simple_lambda.PermissionArn(**x).get_hash() for x in previous_resource.permissions])
        new_hashes = set([x.get_hash() for x in new_resource.permissions])

        create_permissions = []
        remove_permissions = []


        for permission in new_resource.permissions:
            if not permission.get_hash() in previous_hashes:
                create_permissions.append(permission)


        for permission in previous_resource.permissions:
            previous_resource_permission_hash = simple_lambda.Permission(**permission).get_hash() if "resource" in permission else simple_lambda.PermissionArn(**permission).get_hash()
            if not previous_resource_permission_hash in new_hashes:
                remove_permissions.append(permission)

        log.debug(f"New Permissions -> {create_permissions}")
        log.debug(f"Previous Permissions -> {remove_permissions}")

        permission_output = cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "permissions")
        role_name_output = cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "role_name")
        log.debug(previous_resource.hash)
        log.debug(f"{permission_output}")
        for permission in create_permissions:
            rv = add_policy(role_name_output, permission)
            permission_output[permission.get_hash()] = rv

        for permission in remove_permissions:
            previous_resource_permission_hash = simple_lambda.Permission(**permission).get_hash() if "resource" in permission else simple_lambda.PermissionArn(**permission).get_hash()
            delete_policy(role_name_output, permission_output.get(previous_resource_permission_hash))
            permission_output.pop(previous_resource_permission_hash)

        cdev_cloud_mapper.update_output_by_key(previous_resource.hash, "permissions", permission_output)
        print_deployment_step("UPDATE", f"  Update permissions for lambda function {new_resource.name}") 


    if not previous_resource.src_code_hash == new_resource.src_code_hash:
        log.debug(f"UPDATE SOURCE CODE OF {previous_resource.name}; {previous_resource.src_code_hash} -> {new_resource.src_code_hash}")
        
        keyname = _upload_s3_code_artifact(new_resource)
        updated_info['artifact_key'] = keyname

        raw_aws_client.run_client_function("lambda", "update_function_code", {
            "FunctionName": cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "cloud_id"),
            "S3Key": keyname,
            "S3Bucket": BUCKET,
            "Publish": True
        })
        print_deployment_step("UPDATE", f"  Update source code for lambda function {new_resource.name}")

    if not previous_resource.dependencies_hash == new_resource.dependencies_hash:
        log.debug(f"UPDATE DEPENDENCIES OF {previous_resource.name}; {previous_resource.dependencies_hash} -> {new_resource.dependencies_hash}")
        previous_hashes = set([x.get("hash") for x in previous_resource.dependencies_info])
        new_hashes = set([x.get("hash") for x in new_resource.dependencies_info])

        create_dependencies = []
        remove_dependencies = []

        if previous_resource.dependencies_info:
            for dependency in new_resource.dependencies_info:
                if not dependency.get("hash") in previous_hashes:
                    create_dependencies.append(dependency)
        else:
            create_dependencies = new_resource.dependencies_info

        if new_resource.dependencies_info:
            for dependency in previous_resource.dependencies_info:
                if not dependency.get("hash") in new_hashes:
                    remove_dependencies.append(dependency)
        else:
            remove_dependencies = previous_resource.dependencies_info

        dependencies_info = cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "layers")
        
        if remove_dependencies:
            for dependency in remove_dependencies:
                cloud_info = [x for x in dependencies_info if x.get("hash") == dependency.get("hash")][0]
                _remove_dependency(cloud_info)
                dependencies_info.remove(cloud_info)
                print_deployment_step("UPDATE", f'  Remove dependency {cloud_info.get("name")}')
        
        if create_dependencies:
            for dependency in create_dependencies:
                rv = _create_dependency(new_resource, dependency)
                dependencies_info.append(rv)
                print_deployment_step("UPDATE", f'  Create dependency {rv.get("name")}')

        sleep(5)
        raw_aws_client.run_client_function("lambda", "update_function_configuration", {
                "FunctionName": cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "cloud_id"),
                "Layers": [f'{x.get("arn")}:{x.get("version")}' for x in dependencies_info] if dependencies_info else []
            })

        cdev_cloud_mapper.update_output_by_key(previous_resource.hash, "layers", dependencies_info)


    if not previous_resource.events_hash == new_resource.events_hash:
        log.debug(f"UPDATE EVENT HASH: {previous_resource.events} -> {new_resource.events}")
        if did_update_permission:
            print_deployment_step("UPDATE", "   [blink]Wait for new permissions to take effect (~10s)[blink]")
            sleep(10)

        previous_hashes = set([simple_lambda.Event(**x).get_hash() for x in previous_resource.events])
        new_hashes = set([x.get_hash() for x in new_resource.events])

        create_events = []
        remove_events = []

        event_output = cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "events")
        if not event_output:
            event_output = {}


        for event in new_resource.events:
            if not event.get_hash() in previous_hashes:
                create_events.append(event)

            
        for event in previous_resource.events:
            if not simple_lambda.Event(**event).get_hash() in new_hashes:
                remove_events.append(event)

        log.debug(f"New Events -> {create_events}")
        log.debug(f"Previous Events -> {remove_events}")

        for event in create_events:
            key =  event.event_type
            log.debug(key)
            if not key in EVENT_TO_HANDLERS:
                raise Exception

            output = EVENT_TO_HANDLERS.get(key).get("CREATE")(event, cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "cloud_id"))
            event_output[event.get_hash()] = output
            log.debug(f"Add Event -> {event}")
            print_deployment_step("UPDATE", f"  Create event {event.event_type.value} {event.original_resource_name} for lambda {new_resource.name}") 

        
        for event in remove_events:
            casted_event = simple_lambda.Event(**event)

            key =  casted_event.event_type

            if not key in EVENT_TO_HANDLERS:
                raise Exception

            output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(casted_event, previous_resource.hash)
            event_output.pop(casted_event.get_hash())
            log.debug(f"Remove Event -> {casted_event}")
            print_deployment_step("UPDATE", f"  Remove event {casted_event.event_type.value} {casted_event.original_resource_name} for lambda {new_resource.name}")

        cdev_cloud_mapper.update_output_by_key(previous_resource.hash, "events", event_output)


    cdev_cloud_mapper.reidentify_cloud_resource(previous_resource.hash, new_resource.hash)
    print_deployment_step("UPDATE", f"  Finished updating lambda function {new_resource.name}")
    return True


def handle_simple_lambda_function_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_lambda(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return _update_simple_lambda(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return _remove_simple_lambda(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")



