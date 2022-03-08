import math
import os
from time import sleep
from typing import Any, Dict, FrozenSet, Union, List, Tuple
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.constructs.output_manager import OutputTask
from core.constructs.models import frozendict

from core.default.resources.simple import xlambda as simple_xlambda
from core.default.resources.simple.iam import permission_arn_model, permission_model

from core.utils import paths as core_paths, hasher
from core.utils.logger import log
from core.utils.platforms import lambda_python_environment



from .. import aws_client 
from boto3.s3.transfer import TransferConfig


#from .lambda_event_deployer import EVENT_TO_HANDLERS
from .role_deployer import (
    create_role_with_permissions,
    delete_role_and_permissions,
    add_policy,
    delete_policy,
    detach_policy,
)


from .event_deployer import (
    EVENT_TO_HANDLERS
)


python_environment_to_aws_params: Dict[lambda_python_environment, Tuple] = {
    lambda_python_environment.py37: ('python3.7', 'x86_64'),
    lambda_python_environment.py38_x86_64: ('python3.8', 'x86_64'),
    lambda_python_environment.py38_arm64: ('python3.8', 'arm64'),
    lambda_python_environment.py39_x86_64: ('python3.9', 'x86_64'),
    lambda_python_environment.py39_arm64: ('python3.9', 'arm64'),
    lambda_python_environment.py3_x86_64: ('python3.9', 'x86_64'),
    lambda_python_environment.py3_arm64: ('python3.9', ' arm64'),
}


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


BUCKET = "cdev-demo-project-artifacts"

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
    log.debug("Create lambda %s", resource)
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
    final_info["role_name"] = role_name
    final_info["permissions"] = permission_info

    # Step 2
    output_task.update(
        comment=f"Uploading code for lambda function {resource.name}"
    )

    keyname = _upload_s3_code_artifact(function_name, resource)
    

    final_info["artifact_bucket"] = BUCKET
    final_info["artifact_key"] = keyname

    
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

    runtime, arch = python_environment_to_aws_params.get(resource.platform)
    
    lambda_function_args = {
        "FunctionName": function_name,
        "Runtime": runtime,
        "Architectures": [arch],
        "Role": role_arn,
        "Handler": resource.configuration.handler,
        "Code": {"S3Bucket": BUCKET, "S3Key": keyname},
        "Environment": {
            "Variables":resource.configuration.environment_variables._d
        }
        if resource.configuration.environment_variables
        else {},
        "Layers": list(resource.external_dependencies)
        if resource.external_dependencies
        else [],
    }
    log.debug("lambda configuration %s", lambda_function_args)

    lambda_function_rv = aws_client.run_client_function(
        "lambda", "create_function", lambda_function_args
    )
    final_info["layers"] = resource.external_dependencies
    final_info["cloud_id"] = lambda_function_rv.get("FunctionArn")

    # Step 5
    
    if resource.events:
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

    role_arn = previous_output.get("role_id")
    role_name = previous_output.get("role_name")
    permissions =  previous_output.get("permissions")

    delete_role_and_permissions(role_name, permissions)

    output_task.update(
        comment=f"Deleting permissions for the resource ({cloud_id})"
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
    did_update_src_code = False

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
        permission_output: frozenset[Dict] = previous_output.get("permissions")
        role_name_output = previous_output.get("role_name")

        remove_permissions = previous_resource.permissions.difference(new_resource.permissions)
        create_permissions = new_resource.permissions.difference(previous_resource.permissions)


        for permission in create_permissions:
            
            rv = frozendict(add_policy(role_name_output, permission))
            tmp = list(permission_output)
            tmp.append(rv)
            permission_output = frozenset(tmp)

        for permission in remove_permissions:

            previous_permission_output_list = [x for x in permission_output if x.get('hash') == permission.hash]

            if len(previous_permission_output_list) > 1:
                raise Exception

            previous_permission_output = previous_permission_output_list[0]
            
            delete_policy(
                role_name_output,
                previous_permission_output
            )

            permission_output = frozenset([x for x in permission_output if not x.get('hash') == permission.hash])

        mutable_previous_output['permissions'] = permission_output
        
        did_update_permission = True


    if not previous_resource.src_code_hash == new_resource.src_code_hash:
        sleep(3)
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
        did_update_src_code = True


    if (
        not previous_resource.external_dependencies
        == new_resource.external_dependencies
    ):
        if did_update_src_code:
            output_task.update(
                comment=f"[blink]Waiting for src code update to complete. ~5s[/blink]"
            )
            sleep(5)


        output_task.update(
            comment=f"Update Dependencies"
        )
        
        remove_dependencies = previous_resource.external_dependencies.difference(new_resource.external_dependencies)
        create_dependencies = new_resource.external_dependencies.difference(previous_resource.external_dependencies)
        
        previous_dependency_output: List =  list(mutable_previous_output.get("layers"))

        for dependency in create_dependencies:
            previous_dependency_output.append(dependency)

        for dependency in remove_dependencies:
            previous_dependency_output.remove(dependency)

        aws_client.run_client_function(
            "lambda",
            "update_function_configuration",
            {
                "FunctionName": cloud_id,
                "Layers": previous_dependency_output
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

        available_event_handlers = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)

        previous_event_output: dict = dict(mutable_previous_output.get('events')) if mutable_previous_output.get('events') else {}

       
        for _event in create_events:
            if not _event.originating_resource_type in available_event_handlers:
                raise Exception(f'No handlers for {_event.originating_resource_type} to {simple_xlambda.RUUID} events')            


            output_task.update(
                comment=f"Create Event {_event}"
            )

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

            output_task.update(
                comment=f"Delete Event {event_id}"
            )

            EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(originating_resource_type).get("REMOVE")(
                event_output,  cloud_id
            )

            previous_event_output.pop(event_id)

        mutable_previous_output['events'] = previous_event_output
        
    
    return mutable_previous_output






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
    dependency: simple_xlambda.dependency_layer_model,
    output_task: OutputTask
) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = f"{dependency.name}-{dependency.hash}.zip"

    zip_location = core_paths.get_full_path_from_workspace_base(dependency.artifact_path)

    total_bytes =  os.path.getsize(zip_location)

    if not os.path.isfile(zip_location):
        # TODO better exception
        raise Exception

    config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=10,
        multipart_chunksize=1024 * 25,
        use_threads=True,
    )

    

    def update_progress_bar(x):
        advance_amount = (x/total_bytes) * 4
        output_task.update(advance=advance_amount, comment='[blink]Uploading Package[/blink]')


    object_args = {
        "Bucket": BUCKET,
        "Key": keyname,
        "Filename": zip_location,
        "Callback": update_progress_bar,
        "Config": config,
    }
    aws_client.run_client_function("s3", "upload_file", object_args)

    output_task.update( comment='Uploaded Package')

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
        log.debug("Calling lambda mapper")
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

###################################
##### Layers
###################################

def _create_simple_layer( 
        transaction_token: str, 
        namespace_token: str, 
        resource: simple_xlambda.dependency_layer_model, 
        output_task: OutputTask
    ):

    output_task.update(
        comment=f"Creating dependencies for lambda function {resource.name}"
    )

    key_name = _upload_s3_dependency(resource, output_task)

    # key name will always include .zip so remove that part and change '-' into '_'
    layer_name = key_name.replace("-", "_")[:-4].replace(".","")
    dependency_rv = aws_client.run_client_function(
        "lambda",
        "publish_layer_version",
        {
            "Content": {"S3Bucket": BUCKET, "S3Key": key_name},
            "LayerName": f"{layer_name}_{namespace_token[:10]}",
            "CompatibleRuntimes": [
                "python3.7",
                "python3.8",
                "python3.9"
            ],
        },
    )

    return {
        "cloud_id": f"{dependency_rv.get('LayerArn')}:{dependency_rv.get('Version')}",
        "arn": dependency_rv.get("LayerArn"),
        "version": dependency_rv.get('Version')
    }

def _update_simple_layer(
        transaction_token: str, 
        namespace_token: str,
        previous_resource: simple_xlambda.dependency_layer_model,
        new_resource: simple_xlambda.dependency_layer_model,
        previous_output: Dict,
        output_task: OutputTask
    ):
    return _create_simple_layer(
        transaction_token,
        namespace_token,
        new_resource,
        output_task
    )
    
def _remove_simple_layer(
        transaction_token,
        resource,
        previous_output,
        output_task
    ):
        aws_client.run_client_function(
            "lambda",
            "delete_layer_version",
            {
                "LayerName": previous_output.get("arn"),
                "VersionNumber": previous_output.get("version"),
            },
        )



def handle_simple_layer_deployment( 
        transaction_token: str, 
        namespace_token: str, 
        resource_diff: Resource_Difference, 
        previous_output: Dict[str, Any],
        output_task: OutputTask
    ) -> Dict:
    try:
        if resource_diff.action_type == Resource_Change_Type.CREATE:
            return _create_simple_layer(
                transaction_token,
                namespace_token,
                resource_diff.new_resource,  
                output_task
            )
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

            return _update_simple_layer(
                transaction_token,
                namespace_token,
                simple_xlambda.dependency_layer_model(**resource_diff.previous_resource.dict()),
                resource_diff.new_resource,
                previous_output,
                output_task
            )

        elif resource_diff.action_type == Resource_Change_Type.DELETE:
            return _remove_simple_layer(
                transaction_token,
                resource_diff.previous_resource,
                previous_output,
                output_task
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
