from time import sleep
from typing import Any, Dict, Union
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.output.output_manager import OutputTask
from core.resources.simple import xlambda as simple_xlambda
from core.resources.simple.iam import permission_arn_model, permission_model

from core.utils import paths as core_paths, hasher
from core.constructs.models import frozendict


from .. import aws_client 
from boto3.s3.transfer import TransferConfig


#from .lambda_event_deployer import EVENT_TO_HANDLERS
from .role_deployer import (
    create_role_with_permissions,
    delete_role_and_permissions,
    add_policy,
    delete_policy,
)


from .event_deployer import (
    EVENT_TO_HANDLERS
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
    
    if resource.events:
        print(resource.events)
        available_event_handlers = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)
        function_cloud_id = final_info.get("cloud_id")

        event_to_output = {}
        for event in resource.events:

            if not event.originating_resource_type in available_event_handlers:
                raise Exception(f'No handlers for {event.originating_resource_type} to {simple_xlambda.RUUID} events')            


            output = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(event.originating_resource_type).get("CREATE")(
                event, function_cloud_id
            )


            event_to_output[event.hash] = output
            

        final_info["events"] = event_to_output

    return final_info


def _remove_simple_lambda(
    transaction_token: str,  
    previous_resource: simple_xlambda.simple_function_model, 
    previous_output: Dict,
    output_task: OutputTask
) -> bool:
    # Steps:
    # Remove and event that is on the function to make sure resources are properly cleaned up
    # Remove the actual function
    # Remove the role associated with the function
    
    cloud_id = previous_output.get('cloud_id')


    if previous_resource.events:
        output_task.update(
            comment=f"Removing Events"
        )
        event_hashes_to_events = {
            x.get('hash'):x for x in [dict(y) for y in previous_resource.events]
        }


        for event_id, event_output in previous_output.get('events').items():        
            originating_resource_type = event_hashes_to_events.get(event_id).get('originating_resource_type')

            EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(originating_resource_type).get("REMOVE")(
                event_output,  cloud_id
            )
        

    output_task.update(
        comment=f"Deleting function resource for {cloud_id}"
    )


    aws_client.run_client_function(
        "lambda", "delete_function", {"FunctionName": cloud_id}
    )

    #role_name = previous_output.get("role_name")
    #permissions =  previous_output.get("permissions")
#
    #delete_role_and_permissions(role_name, permissions)

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

    cloud_id = previous_output['cloud_id']

    did_update_permission = False

    mutable_previous_output = dict(previous_output)
    
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
                    "FunctionName": cloud_id,
                    "Environment": {
                        "Variables":new_resource.configuration.environment_variables._d
                    }
                },
            )

    if not previous_resource.permissions == new_resource.permissions:
        output_task.update(
            comment=f"Updating Policies"
        )
        permission_output: Dict[Union[permission_model, permission_arn_model], str] = previous_output.get("permissions")
        role_name_output = previous_output.get("role_name")

        
        remove_permissions = previous_resource.permissions.difference(new_resource.permissions)
        create_permissions = new_resource.permissions.difference(previous_resource.permissions)


        for permission in create_permissions:
            
            rv = add_policy(role_name_output, permission)
            permission_output[permission] = rv

        for permission in remove_permissions:

            delete_policy(
                role_name_output,
                permission_output.get(permission),
            )
            permission_output.pop(permission)


        mutable_previous_output['permissions'] = permission_output
        
        did_update_permission = True


    if not previous_resource.src_code_hash == new_resource.src_code_hash:
        output_task.update(
            comment=f"Update Source Code"
        )

        keyname = _upload_s3_code_artifact(previous_output.get('function_name'), new_resource)
        
        aws_client.run_client_function(
            "lambda",
            "update_function_code",
            {
                "FunctionName": cloud_id,
                "S3Key": keyname,
                "S3Bucket": BUCKET,
                "Publish": True,
            },
        )

        mutable_previous_output["artifact_key"] = keyname

    if (
        not previous_resource.external_dependencies
        == new_resource.external_dependencies
    ):
        output_task.update(
            comment=f"Update Dependencies"
        )
        
        remove_dependencies = previous_resource.external_dependencies.difference(new_resource.external_dependencies)
        create_dependencies = new_resource.external_dependencies.difference(previous_resource.external_dependencies)
        
        previous_dependency_output: Dict =  mutable_previous_output.get("layers")

        for dependency in create_dependencies:
            new_layer_rv = _create_dependency(
                dependency
            )

            previous_dependency_output[dependency] = new_layer_rv

        for dependency in remove_dependencies:
            _remove_dependency(dependency)

            previous_dependency_output.pop(dependency)

        sleep(5)

        aws_client.run_client_function(
            "lambda",
            "update_function_configuration",
            {
                "FunctionName": cloud_id,
            
                "Layers": [
                    f'{x.get("arn")}:{x.get("version")}' for x in previous_dependency_output
                ],
            },
        )

        mutable_previous_output['layers'] = previous_dependency_output

    if not previous_resource.events == new_resource.events:
        if did_update_permission:
            # Wait because the updated permission can effect if the event can be bound. 
            output_task.update(
                comment=f"[blink]Waiting for policies to complete. ~10s[/blink]"
            )
            sleep(10)

        output_task.update(
                comment=f"Updating Events"
            )

        create_events = new_resource.events.difference(previous_resource.events)
        remove_events = previous_resource.events.difference(new_resource.events)


        print(f"Create Events -> {create_events}")
        print(f"Remove Events -> {remove_events}")

        available_event_handlers = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)

        previous_event_output: dict = dict(mutable_previous_output.get('events')) if mutable_previous_output.get('events') else {}

       
        for _event in create_events:
            if not _event.originating_resource_type in available_event_handlers:
                raise Exception(f'No handlers for {_event.originating_resource_type} to {simple_xlambda.RUUID} events')            


            output = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(_event.originating_resource_type).get("CREATE")(
                _event, cloud_id
            )


            previous_event_output[_event.hash] = output

        previous_event_hashes_to_output = {
            hash:output for hash, output in [ (y.hash, dict(previous_event_output.get(y.hash))) for y in remove_events if previous_event_output.get(y.hash)]
        }

        previous_hashes_to_events = {
            x.get('hash'):x for x in [dict(y) for y in remove_events]
        }

        for event_id, event_output in previous_event_hashes_to_output.items():        
            originating_resource_type = previous_hashes_to_events.get(event_id).get('originating_resource_type')

            EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(originating_resource_type).get("REMOVE")(
                event_output,  cloud_id
            )

            previous_event_output.pop(event_id)
        
    
    return mutable_previous_output



##########################
##### Dependencies
##########################
def _create_dependency(
    dependency: Union[simple_xlambda.dependency_layer_model, simple_xlambda.deployed_layer_model],
) -> Dict:

    if isinstance(dependency, simple_xlambda.deployed_layer_model):
        return dependency.arn

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
                resource_diff.previous_resource,
                previous_output,
                output_task
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
