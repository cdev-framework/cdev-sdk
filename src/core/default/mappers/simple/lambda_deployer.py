from time import sleep
from typing import Any, Dict, Union
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.output.output_manager import OutputTask
from core.resources.simple import xlambda as simple_xlambda
from core.resources.simple.iam import permission_arn_model, permission_model

from core.utils import paths as core_paths, hasher


from .. import aws_client 
from boto3.s3.transfer import TransferConfig


#from .lambda_event_deployer import EVENT_TO_HANDLERS
from .role_deployer import (
    create_role_with_permissions,
    delete_role_and_permissions,
    add_policy,
    delete_policy,
)

from core.settings import SETTINGS
import os


AssumeRolePolicyDocumentJSON = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""


BUCKET = SETTINGS.get("S3_ARTIFACTS_BUCKET")

###########################
###### Main Handlers
###########################
def _create_simple_lambda(
        transaction_token: str, 
        namespace_token: str, 
        resource: simple_xlambda.simple_function_model, 
        output_task: OutputTask
    ) -> Dict:
    # Steps for creating a deployed lambda function
    # 1. Create IAM Role with needed permissions (note this is first to give aws more time to create the role in all regions and be available for use)
    # 2. Upload the artifact to S3 as the archive location
    # 3. Upload dependencies if needed
    # 4. Create the function
    # 5. Create any integrations that are need based on Events passed in

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    function_name = f"cdev_function_{full_namespace_suffix}"
    output_task.update(
        comment=f"Creating lambda function resources for lambda {function_name}"
    )

    final_info = {
        'function_name': function_name
    }

    output_task.update(
        comment=f"Creating IAM Role w/ permissions {resource.permissions}"
    )
    # Step 1
    role_name = f"role_{function_name}"
    role_arn, permission_info = create_role_with_permissions(role_name, resource.permissions, AssumeRolePolicyDocumentJSON)

    output_task.update(
        comment=f"Create role for lambda function {resource.name}"
    )


    

    final_info["role_name"] = role_name
    final_info["role_id"] = role_arn
    final_info["permissions"] = permission_info

    # Step 2
    output_task.update(
        comment=f"Uploading code for lambda function {resource.name}"
    )

    keyname = _upload_s3_code_artifact(function_name, resource)
    

    final_info["artifact_bucket"] = BUCKET
    final_info["artifact_key"] = keyname

    # Step 3
    if resource.external_dependencies:
        output_task.update(
            comment=f"Creating dependencies for lambda function {resource.name}"
        )

        cloud_dependency_info = [_create_dependency(x) for x in resource.external_dependencies]

        final_info["layers"] = cloud_dependency_info

    # Step 4
    # TODO
    output_task.update(
        comment=f"[blink]Waiting for role to finish creating (~10s)[/blink]"
    )
    sleep(10)
    # ughhhh add a retry wrapper because it takes time to generate the IAM roles across all regions so we need to wait a few seconds to create this
    
    output_task.update(
        comment=f"Create Lambda function"
    )

    lambda_function_args = {
        "FunctionName": function_name,
        "Runtime": "python3.7",
        "Role": role_arn,
        "Handler": resource.configuration.handler,
        "Code": {"S3Bucket": BUCKET, "S3Key": keyname},
        "Environment": {
            "Variables":resource.configuration.environment_variables._d
        }
        if resource.configuration.environment_variables
        else {},
        "Layers": [
            f'{x.get("arn")}:{x.get("version")}' for x in final_info.get("layers")
        ]
        if final_info.get("layers")
        else [],
    }

    lambda_function_rv = aws_client.run_client_function(
        "lambda", "create_function", lambda_function_args
    )

    final_info["cloud_id"] = lambda_function_rv.get("FunctionArn")

    # Step 5
    
    #if resource.events:
    #    event_hash_to_output = {}
    #    for event in resource.events:
    #        
#
    #        key = event.event_type
    #        
    #        if not key in EVENT_TO_HANDLERS:
    #            raise Exception
#
    #        output = EVENT_TO_HANDLERS.get(key).get("CREATE")(
    #            event, final_info.get("cloud_id")
    #        )
    #        event_hash_to_output[event.get_hash()] = output
    #        print_deployment_step(
    #            "CREATE",
    #            f"  Create event {event.event_type.value} {event.original_resource_name} for lambda {resource.name}",
    #        )
#
    #    final_info["events"] = event_hash_to_output

    
    output_task.update(
        comment=f"Created lambda function resources for lambda {resource.name}"
    )
    return final_info


def _remove_simple_lambda(
    transaction_token: str,  previous_output: Dict, output_task: OutputTask
) -> bool:
    # Steps:
    # Remove and event that is on the function to make sure resources are properly cleaned up
    # Remove the actual function
    # Remove the role associated with the function
    
    cloud_id = previous_output.get('cloud_id')
    

    #for event in resource.events:
    #    casted_event = simple_lambda.Event(**event)
#
    #    key = casted_event.event_type
#
    #    if not key in EVENT_TO_HANDLERS:
    #        raise Exception
#
    #    output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(casted_event, resource.hash)
    #    print_deployment_step(
    #        "DELETE",
    #        f"  Remove event {casted_event.event_type.value} {casted_event.original_resource_name} for lambda {resource.name}",
    #    )
#
    output_task.update(
        comment=f"Deleting function resource for {cloud_id}"
    )


    aws_client.run_client_function(
        "lambda", "delete_function", {"FunctionName": cloud_id}
    )

    role_name = previous_output.get("role_name")
    permissions =  previous_output.get("permissions")

    delete_role_and_permissions(role_name, permissions)

    output_task.update(
        comment=f"Deleting permissions for the resource ({cloud_id})"
    )

    dependencies_info = previous_output.get("layers")
    
    if dependencies_info:
        for dependency_info in dependencies_info:
            _remove_dependency(dependency_info)

        output_task.update(
            comment=f"Deleting dependencies for the resource ({cloud_id})"
        )

   
    output_task.update(
        comment=f"Removed resources for lambda {cloud_id}"
    )


def _update_simple_lambda(
    transaction_token: str, 
    namespace_token: str,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
    previous_output: Dict,
    output_task: OutputTask
) -> bool:
    # Updates can be of:
    # Update source code or dependencies
    # Update configuration
    # Update events
    output_task.update(
        comment=f"Updating lambda function {new_resource.name}"
    )
    
    did_update_permission = False
    updated_info = {}
    
    # TODO all configurations
    if not previous_resource.configuration == new_resource.configuration:
        if (
            not previous_resource.configuration.environment_variables
            == new_resource.configuration.environment_variables
        ):
            output_task.update(
                comment=f"Updating Environment Variables"
            )
            aws_client.run_client_function(
                "lambda",
                "update_function_configuration",
                {
                    "FunctionName": previous_output.get("cloud_id"),
                    "Environment": {
                        "Variables":new_resource.configuration.environment_variables._d
                    }
                },
            )

    if not previous_resource.permissions == new_resource.permissions:
        output_task.update(
            comment=f"Updating Policies"
        )

        did_update_permission = True
        remove_permissions = previous_resource.permissions.difference(new_resource.permissions)
        create_permissions = new_resource.permissions.difference(previous_resource.permissions)


        permission_output: Dict[Union[permission_model, permission_arn_model], str] = previous_output.get("permissions")
        role_name_output = previous_output.get("role_name")
        

        for permission in create_permissions:
            
            rv = add_policy(role_name_output, permission)
            permission_output[permission] = rv

        for permission in remove_permissions:

            delete_policy(
                role_name_output,
                permission_output.get(permission),
            )
            permission_output.pop(permission)


        previous_output['permissions'] = permission_output


    if not previous_resource.src_code_hash == new_resource.src_code_hash:
        output_task.update(
            comment=f"Update Source Code"
        )

        keyname = _upload_s3_code_artifact(previous_output.get('function_name'), new_resource)
        updated_info["artifact_key"] = keyname

        aws_client.run_client_function(
            "lambda",
            "update_function_code",
            {
                "FunctionName": previous_output.get("cloud_id"),
                "S3Key": keyname,
                "S3Bucket": BUCKET,
                "Publish": True,
            },
        )

    if (
        not previous_resource.external_dependencies
        == new_resource.external_dependencies
    ):
        output_task.update(
            comment=f"Update Dependencies"
        )
        
        remove_dependencies = previous_resource.external_dependencies.difference(new_resource.external_dependencies)
        create_dependencies = new_resource.external_dependencies.difference(previous_resource.external_dependencies)
        
        previous_dependency_output =  previous_resource.get("layers")


        for dependency in remove_dependencies:
            _remove_dependency(dependency)

            previous_dependency_output.pop(dependency)



        for dependency in create_dependencies:
            new_layer_rv = _create_dependency(
                dependency
            )

            previous_dependency_output[dependency] = new_layer_rv

        sleep(5)

        aws_client.run_client_function(
            "lambda",
            "update_function_configuration",
            {
                "FunctionName": previous_resource.get("cloud_id"),
            
                "Layers": [
                    f'{x.get("arn")}:{x.get("version")}' for x in previous_dependency_output
                ],
            },
        )

        previous_resource['layers'] = previous_dependency_output

    #if not previous_resource.events_hash == new_resource.events_hash:
    #    log.debug(
    #        f"UPDATE EVENT HASH: {previous_resource.events} -> {new_resource.events}"
    #    )
    #    if did_update_permission:
    #        print_deployment_step(
    #            "UPDATE",
    #            "   [blink]Wait for new permissions to take effect (~10s)[blink]",
    #        )
    #        sleep(10)
#
    #    previous_hashes = set(
    #        [simple_lambda.Event(**x).get_hash() for x in previous_resource.events]
    #    )
    #    new_hashes = set([x.get_hash() for x in new_resource.events])
#
    #    create_events = []
    #    remove_events = []
#
    #    event_output = cdev_cloud_mapper.get_output_value_by_hash(
    #        previous_resource.hash, "events"
    #    )
    #    if not event_output:
    #        event_output = {}
#
    #    for event in new_resource.events:
    #        if not event.get_hash() in previous_hashes:
    #            create_events.append(event)
#
    #    for event in previous_resource.events:
    #        if not simple_lambda.Event(**event).get_hash() in new_hashes:
    #            remove_events.append(event)
#
    #    log.debug(f"New Events -> {create_events}")
    #    log.debug(f"Previous Events -> {remove_events}")
#
    #    for event in create_events:
    #        key = event.event_type
    #        log.debug(key)
    #        if not key in EVENT_TO_HANDLERS:
    #            raise Exception
#
    #        output = EVENT_TO_HANDLERS.get(key).get("CREATE")(
    #            event,
    #            cdev_cloud_mapper.get_output_value_by_hash(
    #                previous_resource.hash, "cloud_id"
    #            ),
    #        )
    #        event_output[event.get_hash()] = output
    #        log.debug(f"Add Event -> {event}")
    #        print_deployment_step(
    #            "UPDATE",
    #            f"  Create event {event.event_type.value} {event.original_resource_name} for lambda {new_resource.name}",
    #        )
#
    #    for event in remove_events:
    #        casted_event = simple_lambda.Event(**event)
#
    #        key = casted_event.event_type
#
    #        if not key in EVENT_TO_HANDLERS:
    #            raise Exception
#
    #        output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(
    #            casted_event, previous_resource.hash
    #        )
    #        event_output.pop(casted_event.get_hash())
    #        log.debug(f"Remove Event -> {casted_event}")
    #        print_deployment_step(
    #            "UPDATE",
    #            f"  Remove event {casted_event.event_type.value} {casted_event.original_resource_name} for lambda {new_resource.name}",
    #        )
#
    #    cdev_cloud_mapper.update_output_by_key(
    #        previous_resource.hash, "events", event_output
    #    )
#
    
    return previous_output



##########################
##### Dependencies
##########################
def _create_dependency(
    dependency: Union[simple_xlambda.dependency_layer_model, simple_xlambda.deployed_layer_model],
) -> Dict:

    if isinstance(dependency, simple_xlambda.deployed_layer_model):
        return dependency.dict()

    key_name = _upload_s3_dependency(dependency)

    # key name will always include .zip so remove that part and change '-' into '_'
    layer_name = key_name.replace("-", "_")[:-4]
    dependency_rv = aws_client.run_client_function(
        "lambda",
        "publish_layer_version",
        {
            "Content": {"S3Bucket": BUCKET, "S3Key": key_name},
            "LayerName": layer_name,
            "CompatibleRuntimes": [
                "python3.6",
                "python3.7",
                "python3.8",
            ],
        },
    )

    return {
        "arn": dependency_rv.get("LayerArn"),
        "S3bucket": BUCKET,
        "S3key": key_name,
        "version": dependency_rv.get("Version"),
        "name": layer_name,
        "hash": dependency.get("hash"),
    }


def _remove_dependency(dependency_cloud_info: Dict):
    aws_client.run_client_function(
        "lambda",
        "delete_layer_version",
        {
            "LayerName": dependency_cloud_info.get("name"),
            "VersionNumber": dependency_cloud_info.get("version"),
        },
    )



###############################
###### Upload Artifacts to S3
###############################

def _upload_s3_code_artifact(
    function_name: str, 
    resource: simple_xlambda.simple_function_model,
) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = function_name + f"-{resource.hash}" + ".zip"
    # original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location =  core_paths.get_full_path_from_workspace_base(resource.filepath)

    if not os.path.isfile(zip_location):
        # TODO better exception
        raise Exception

    with open(zip_location, "rb") as fh:
        object_args = {
            "Bucket": BUCKET,
            "Key": keyname,
            "Body": fh.read(),
        }
        aws_client.run_client_function("s3", "put_object", object_args)

    return keyname

def _upload_s3_dependency(
    dependency: simple_xlambda.dependency_layer_model
) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = dependency.name + f"-{dependency.hash}" + ".zip"
    # original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = core_paths.get_full_path_from_workspace_base(dependency.artifact_path)

    if not os.path.isfile(zip_location):
        # TODO better exception
        raise Exception

    config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=10,
        multipart_chunksize=1024 * 25,
        use_threads=True,
    )

    object_args = {
        "Bucket": BUCKET,
        "Key": keyname,
        "Filename": zip_location,
        "Callback": lambda x: print(x),
        "Config": config,
    }
    aws_client.run_client_function("s3", "upload_file", object_args)

    return keyname


#######################
##### Main Entry Point
#######################

def handle_simple_lambda_function_deployment( 
        transaction_token: str, 
        namespace_token: str, 
        resource_diff: Resource_Difference, 
        previous_output: Dict[str, Any],
        output_task: OutputTask
    ) -> Dict:
    try:
        if resource_diff.action_type == Resource_Change_Type.CREATE:
            return _create_simple_lambda(
                transaction_token,
                namespace_token,
                resource_diff.new_resource,  
                output_task
            )
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

            return _update_simple_lambda(
                transaction_token,
                namespace_token,
                simple_xlambda.simple_function_model(**resource_diff.previous_resource.dict()),
                resource_diff.new_resource,
                previous_output,
                output_task
            )
        elif resource_diff.action_type == Resource_Change_Type.DELETE:

            return _remove_simple_lambda(
                transaction_token,
                previous_output,
                output_task
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
