import os
from time import sleep
from typing import Any, Dict, List, Tuple, Optional
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.constructs.output_manager import OutputTask
from core.constructs.models import frozendict
from core.constructs.workspace import Workspace

from core.default.resources.simple import xlambda as simple_xlambda

from core.utils import paths as core_paths, hasher
from core.utils.logger import log
from core.utils.platforms import lambda_python_environment


from .. import aws_client
from boto3.s3.transfer import TransferConfig


# from .lambda_event_deployer import EVENT_TO_HANDLERS
from .role_deployer import (
    create_role_with_permissions,
    delete_role_and_permissions,
    add_policy,
    delete_policy,
    detach_policy,
)


from .event_deployer import EVENT_TO_HANDLERS


python_environment_to_aws_params: Dict[lambda_python_environment, Tuple] = {
    lambda_python_environment.py37: ("python3.7", "x86_64"),
    lambda_python_environment.py38_x86_64: ("python3.8", "x86_64"),
    lambda_python_environment.py38_arm64: ("python3.8", "arm64"),
    lambda_python_environment.py39_x86_64: ("python3.9", "x86_64"),
    lambda_python_environment.py39_arm64: ("python3.9", "arm64"),
    lambda_python_environment.py3_x86_64: ("python3.9", "x86_64"),
    lambda_python_environment.py3_arm64: ("python3.9", " arm64"),
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

###########################
###### Main Handlers
###########################


def _create_simple_lambda(
    transaction_token: str,
    namespace_token: str,
    resource: simple_xlambda.simple_function_model,
    output_task: OutputTask,
    artifact_bucket: str,
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

    final_info = {"function_name": function_name}

    output_task.update(
        comment=f"Creating IAM Role w/ permissions {resource.permissions}"
    )
    # Step 1
    role_name = f"role_{function_name}"
    role_arn, permission_info = create_role_with_permissions(
        role_name, resource.permissions, AssumeRolePolicyDocumentJSON
    )

    if role_arn is None:
        output_task.update(comment=f"Failed to create role {role_name} for lambda function {resource.name}")
        raise Exception("DEPLOY FAILED")

    output_task.update(comment=f"Create role for lambda function {resource.name}")

    final_info["role_id"] = role_arn
    final_info["role_name"] = role_name
    final_info["permissions"] = permission_info

    # Step 2
    output_task.update(comment=f"Uploading code for lambda function {resource.name}")

    keyname = _upload_s3_code_artifact(function_name, resource, artifact_bucket)

    final_info["artifact_bucket"] = artifact_bucket
    final_info["artifact_key"] = keyname

    # Step 4
    # TODO
    output_task.update(
        comment=f"[blink]Waiting for role to finish creating (~10s)[/blink]"
    )
    sleep(10)
    # ughhhh add a retry wrapper because it takes time to generate the IAM roles across all regions so we need to wait a few seconds to create this

    output_task.update(comment=f"Create Lambda function")

    runtime, arch = python_environment_to_aws_params.get(resource.platform)

    lambda_function_args = {
        "FunctionName": function_name,
        "Runtime": runtime,
        "Architectures": [arch],
        "Role": role_arn,
        "Handler": resource.configuration.handler,
        "MemorySize": resource.configuration.memory_size,
        "EphemeralStorage": {"Size": resource.configuration.storage},
        "Timeout": resource.configuration.timeout,
        "Code": {"S3Bucket": artifact_bucket, "S3Key": keyname},
        "Environment": {"Variables": resource.configuration.environment_variables._d}
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
                raise Exception(
                    f"No handlers for {event.originating_resource_type} to {simple_xlambda.RUUID} events"
                )

            output = (
                EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)
                .get(event.originating_resource_type)
                .get("CREATE")(event, function_cloud_id)
            )

            event_to_output[event.hash] = output

        final_info["events"] = event_to_output

    return final_info


def _remove_simple_lambda(
    transaction_token: str,
    previous_resource: simple_xlambda.simple_function_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> None:
    # Steps:
    # Remove and event that is on the function to make sure resources are properly cleaned up
    # Remove the actual function
    # Remove the role associated with the function

    cloud_id = previous_output.get("cloud_id")

    if previous_resource.events:
        output_task.update(comment=f"Removing Events")
        event_hashes_to_events = {
            x.get("hash"): x for x in [dict(y) for y in previous_resource.events]
        }

        for event_id, event_output in previous_output.get("events").items():
            originating_resource_type = event_hashes_to_events.get(event_id).get(
                "originating_resource_type"
            )

            EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(
                originating_resource_type
            ).get("REMOVE")(event_output, cloud_id)

    output_task.update(comment=f"Deleting function resource for {cloud_id}")

    aws_client.run_client_function(
        "lambda", "delete_function", {"FunctionName": cloud_id}
    )

    # role_arn = previous_output.get("role_id")
    role_name = previous_output.get("role_name")
    permissions = previous_output.get("permissions")

    delete_role_and_permissions(role_name, permissions)

    output_task.update(comment=f"Deleting permissions for the resource ({cloud_id})")

    output_task.update(comment=f"Removed resources for lambda {cloud_id}")


def _update_simple_lambda(
    transaction_token: str,
    namespace_token: str,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
    previous_output: Dict,
    output_task: OutputTask,
    artifact_bucket: str,
) -> Dict:
    """
    Updates can be of:
      - 1 Configuration
      - 2 Permissions
      - 3 Source code
      - 4 Dependencies
      - 5 Events
    """

    output_task.update(comment=f"Updating lambda function {new_resource.name}")

    function_name = previous_output["cloud_id"]

    mutable_previous_output = dict(previous_output)

    _update_configuration(output_task, function_name, previous_resource, new_resource)

    did_update_permission = _update_permissions(
        output_task,
        mutable_previous_output,
        previous_output,
        previous_resource,
        new_resource,
    )

    did_update_src_code = _update_source_code(
        output_task,
        function_name,
        mutable_previous_output,
        previous_output,
        previous_resource,
        new_resource,
        artifact_bucket,
    )

    _update_dependencies(
        output_task,
        function_name,
        mutable_previous_output,
        did_update_src_code,
        previous_resource,
        new_resource,
    )

    _update_events(
        output_task,
        function_name,
        mutable_previous_output,
        did_update_permission,
        previous_resource,
        new_resource,
    )

    return mutable_previous_output


def _update_configuration(
    output_task: OutputTask,
    function_name: str,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> bool:

    updated_configuration = {}
    __update_configuration_basic(
        updated_configuration,
        previous_resource.configuration,
        new_resource.configuration,
    )

    __update_configuration_environment_variables(
        updated_configuration,
        previous_resource.configuration.environment_variables,
        new_resource.configuration.environment_variables,
    )

    if not updated_configuration:
        log.debug("Simple lambda, configuration didn't change")
        return False

    updated_configuration["FunctionName"] = function_name
    output_task.update(comment=f"Updating configuration")
    aws_client.run_client_function(
        "lambda", "update_function_configuration", updated_configuration
    )

    log.debug("Simple lambda, configuration updated")
    return True


def __update_configuration_basic(
    updated_configuration: Dict,
    previous_configuration: simple_xlambda.simple_function_configuration_model,
    new_configuration: simple_xlambda.simple_function_configuration_model,
) -> None:
    if previous_configuration == new_configuration:
        log.debug("Simple lambda, basic configuration didn't change")
    else:
        log.debug("Simple lambda, basic configuration modified")
        updated_configuration["Handler"] = new_configuration.handler
        updated_configuration["MemorySize"] = new_configuration.memory_size
        updated_configuration["Timeout"] = new_configuration.timeout
        updated_configuration["EphemeralStorage"] = {"Size": new_configuration.storage}


def __update_configuration_environment_variables(
    updated_configuration: Dict,
    previous_environment_variables: frozendict,
    new_resource_environment_variables: frozendict,
) -> None:
    if previous_environment_variables == new_resource_environment_variables:
        log.debug("Simple lambda, environment variables didn't change")
    else:
        log.debug("Simple lambda, environment variables modified")
        updated_configuration["Environment"] = {
            "Variables": new_resource_environment_variables._d
        }


def _update_permissions(
    output_task: OutputTask,
    mutable_previous_output: Dict,
    previous_output: Dict,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> bool:
    if previous_resource.permissions == new_resource.permissions:
        log.debug("Simple lambda, permissions didn't change")
        return False

    permission_output = previous_output.get("permissions")
    role_name_output = previous_output.get("role_name")

    permission_output = __update_permissions_create(
        output_task,
        role_name_output,
        permission_output,
        previous_resource,
        new_resource,
    )
    permission_output = __update_permissions_remove(
        output_task,
        role_name_output,
        permission_output,
        previous_resource,
        new_resource,
    )

    mutable_previous_output["permissions"] = permission_output
    log.debug("Simple lambda, permissions updated")
    return True


def __update_permissions_create(
    output_task: OutputTask,
    role_name_output: str,
    permission_output: "frozenset[Dict]",
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> "frozenset[Dict]":

    create_permissions = new_resource.permissions.difference(
        previous_resource.permissions
    )
    if not create_permissions:
        log.debug("Simple lambda, no new permissions")
        return permission_output

    output_task.update(comment=f"Updating Policies, creating Permissions")
    policies: List[frozendict] = []
    for permission in create_permissions:
        rv = frozendict(add_policy(role_name_output, permission))
        policies.append(rv)

    permission_output = frozenset(list(permission_output) + policies)
    log.debug(f"Simple lambda, added {len(create_permissions)} permissions")
    return permission_output


def __update_permissions_remove(
    output_task: OutputTask,
    role_name_output: str,
    permission_output: "frozenset[Dict]",
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> "frozenset[Dict]":

    remove_permissions = previous_resource.permissions.difference(
        new_resource.permissions
    )
    if not remove_permissions:
        log.debug("Simple lambda, no permissions to remove")
        return permission_output

    output_task.update(comment=f"Updating Policies, removing Permissions")
    for permission in remove_permissions:
        previous_permission_output_list = [
            x for x in permission_output if x.get("hash") == permission.hash
        ]

        if len(previous_permission_output_list) > 1:
            raise Exception

        previous_permission_output = previous_permission_output_list[0]

        delete_policy(role_name_output, previous_permission_output)

        permission_output = frozenset(
            [x for x in permission_output if not x.get("hash") == permission.hash]
        )

    log.debug(f"Simple lambda, removed {len(remove_permissions)} permissions")
    return permission_output


def _update_source_code(
    output_task: OutputTask,
    function_name: str,
    mutable_previous_output: Dict,
    previous_output: Dict,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
    artifact_bucket: str,
) -> bool:

    if previous_resource.src_code_hash == new_resource.src_code_hash:
        log.debug("Simple lambda, source code didn't change")
        return False

    sleep(3)
    output_task.update(comment=f"Update Source Code")

    keyname = _upload_s3_code_artifact(
        previous_output.get("function_name"), new_resource, artifact_bucket
    )

    aws_client.run_client_function(
        "lambda",
        "update_function_code",
        {
            "FunctionName": function_name,
            "S3Key": keyname,
            "S3Bucket": artifact_bucket,
            "Publish": True,
        },
    )

    mutable_previous_output["artifact_key"] = keyname
    log.debug("Simple lambda, source code updated")
    return True


def _update_dependencies(
    output_task: OutputTask,
    function_name: str,
    mutable_previous_output: Dict,
    did_update_src_code: bool,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> bool:

    if previous_resource.external_dependencies == new_resource.external_dependencies:
        log.debug("Simple lambda, dependencies didn't change")
        return False

    create_dependencies = new_resource.external_dependencies.difference(
        previous_resource.external_dependencies
    )
    remove_dependencies = previous_resource.external_dependencies.difference(
        new_resource.external_dependencies
    )

    if not create_dependencies and not remove_dependencies:
        return False

    if did_update_src_code:
        output_task.update(
            comment=f"[blink]Waiting for src code update to complete. ~5s[/blink]"
        )
        sleep(5)

    output_task.update(comment=f"Update Dependencies")
    previous_dependency_output: List = list(mutable_previous_output.get("layers"))

    for dependency in create_dependencies:
        previous_dependency_output.append(dependency)

    for dependency in remove_dependencies:
        previous_dependency_output.remove(dependency)

    aws_client.run_client_function(
        "lambda",
        "update_function_configuration",
        {"FunctionName": function_name, "Layers": previous_dependency_output},
    )

    mutable_previous_output["layers"] = previous_dependency_output
    log.debug(
        f"Simple lambda, dependencies updated. Added {len(create_dependencies)}, removed: {len(remove_dependencies)}"
    )
    return True


def _update_events(
    output_task: OutputTask,
    function_name: str,
    mutable_previous_output: Dict,
    did_update_permission: bool,
    previous_resource: simple_xlambda.simple_function_model,
    new_resource: simple_xlambda.simple_function_model,
) -> bool:
    if previous_resource.events == new_resource.events:
        log.debug("Simple lambda, events didn't change")
        return False

    if did_update_permission:
        # Wait because the updated permission can effect if the event can be bound.
        output_task.update(
            comment=f"[blink]Waiting for policies to complete. ~10s[/blink]"
        )
        sleep(10)

    output_task.update(comment=f"Updating Events")

    create_events = new_resource.events.difference(previous_resource.events)
    remove_events = previous_resource.events.difference(new_resource.events)

    available_event_handlers = EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)

    previous_event_output: dict = (
        dict(mutable_previous_output.get("events"))
        if mutable_previous_output.get("events")
        else {}
    )

    for _event in create_events:
        if _event.originating_resource_type not in available_event_handlers:
            raise Exception(
                f"No handlers for {_event.originating_resource_type} to {simple_xlambda.RUUID} events"
            )

        output_task.update(comment=f"Create Event {_event}")

        output = (
            EVENT_TO_HANDLERS.get(simple_xlambda.RUUID)
            .get(_event.originating_resource_type)
            .get("CREATE")(_event, function_name)
        )

        previous_event_output[_event.hash] = output

    previous_event_hashes_to_output = {
        hash: output
        for hash, output in [
            (y.hash, dict(previous_event_output.get(y.hash)))
            for y in remove_events
            if previous_event_output.get(y.hash)
        ]
    }

    previous_hashes_to_events = {
        x.get("hash"): x for x in [dict(y) for y in remove_events]
    }

    for event_id, event_output in previous_event_hashes_to_output.items():
        originating_resource_type = previous_hashes_to_events.get(event_id).get(
            "originating_resource_type"
        )

        output_task.update(comment=f"Delete Event {event_id}")

        EVENT_TO_HANDLERS.get(simple_xlambda.RUUID).get(originating_resource_type).get(
            "REMOVE"
        )(event_output, function_name)

        previous_event_output.pop(event_id)

    mutable_previous_output["events"] = previous_event_output
    log.debug("Simple lambda, events updated")
    return True


###############################
###### Upload Artifacts to S3
###############################


def _upload_s3_code_artifact(
    function_name: str,
    resource: simple_xlambda.simple_function_model,
    artifact_bucket: str,
) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = function_name + f"-{resource.hash}" + ".zip"
    # original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = core_paths.get_full_path_from_workspace_base(resource.filepath)

    if not os.path.isfile(zip_location):
        # TODO better exception
        raise Exception

    with open(zip_location, "rb") as fh:
        object_args = {
            "Bucket": artifact_bucket,
            "Key": keyname,
            "Body": fh.read(),
        }
        aws_client.run_client_function("s3", "put_object", object_args)

    return keyname


def _upload_s3_dependency(
    dependency: simple_xlambda.dependency_layer_model,
    output_task: OutputTask,
    artifact_bucket: str,
) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = f"{dependency.name}-{dependency.hash}.zip"

    zip_location = core_paths.get_full_path_from_workspace_base(
        dependency.artifact_path
    )

    total_bytes = os.path.getsize(zip_location)

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
        advance_amount = (x / total_bytes) * 4
        output_task.update(
            advance=advance_amount, comment="[blink]Uploading Package[/blink]"
        )

    object_args = {
        "Bucket": artifact_bucket,
        "Key": keyname,
        "Filename": zip_location,
        "Callback": update_progress_bar,
        "Config": config,
    }
    aws_client.run_client_function("s3", "upload_file", object_args)

    output_task.update(comment="Uploaded Package")

    return keyname


#######################
##### Main Entry Point
#######################


def handle_simple_lambda_function_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Optional[Dict]:

    artifact_bucket = _get_artifact_bucket_name()

    try:
        log.debug("Calling lambda mapper")

        if resource_diff.action_type == Resource_Change_Type.CREATE:
            return _create_simple_lambda(
                transaction_token,
                namespace_token,
                resource_diff.new_resource,
                output_task,
                artifact_bucket,
            )
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

            return _update_simple_lambda(
                transaction_token,
                namespace_token,
                simple_xlambda.simple_function_model(
                    **resource_diff.previous_resource.dict()
                ),
                resource_diff.new_resource,
                previous_output,
                output_task,
                artifact_bucket,
            )
        elif resource_diff.action_type == Resource_Change_Type.DELETE:

            return _remove_simple_lambda(
                transaction_token,
                resource_diff.previous_resource,
                previous_output,
                output_task,
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
    output_task: OutputTask,
    artifact_bucket: str,
) -> Dict:

    output_task.update(
        comment=f"Creating dependencies for lambda function {resource.name}"
    )

    key_name = _upload_s3_dependency(resource, output_task, artifact_bucket)

    # key name will always include .zip so remove that part and change '-' into '_'
    layer_name = key_name.replace("-", "_")[:-4].replace(".", "")
    dependency_rv = aws_client.run_client_function(
        "lambda",
        "publish_layer_version",
        {
            "Content": {"S3Bucket": artifact_bucket, "S3Key": key_name},
            "LayerName": f"{layer_name}_{namespace_token[:10]}",
            "CompatibleRuntimes": ["python3.7", "python3.8", "python3.9"],
        },
    )

    return {
        "cloud_id": f"{dependency_rv.get('LayerArn')}:{dependency_rv.get('Version')}",
        "arn": dependency_rv.get("LayerArn"),
        "version": dependency_rv.get("Version"),
    }


def _update_simple_layer(
    transaction_token: str,
    namespace_token: str,
    previous_resource: simple_xlambda.dependency_layer_model,
    new_resource: simple_xlambda.dependency_layer_model,
    previous_output: Dict,
    output_task: OutputTask,
    artifact_bucket: str,
) -> Dict:
    return _create_simple_layer(
        transaction_token, namespace_token, new_resource, output_task, artifact_bucket
    )


def _remove_simple_layer(
    transaction_token, resource, previous_output, output_task
) -> None:
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
    output_task: OutputTask,
) -> Optional[Dict]:

    artifact_bucket = _get_artifact_bucket_name()

    try:
        if resource_diff.action_type == Resource_Change_Type.CREATE:
            return _create_simple_layer(
                transaction_token,
                namespace_token,
                resource_diff.new_resource,
                output_task,
                artifact_bucket,
            )
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

            return _update_simple_layer(
                transaction_token,
                namespace_token,
                simple_xlambda.dependency_layer_model(
                    **resource_diff.previous_resource.dict()
                ),
                resource_diff.new_resource,
                previous_output,
                output_task,
                artifact_bucket,
            )

        elif resource_diff.action_type == Resource_Change_Type.DELETE:
            return _remove_simple_layer(
                transaction_token,
                resource_diff.previous_resource,
                previous_output,
                output_task,
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def _get_artifact_bucket_name() -> str:
    """Get the artifact bucket name from the Workspace

    Raises:
        Exception

    Returns:
        str: Bucket Name
    """
    ws = Workspace.instance()

    if not ws.settings.S3_ARTIFACTS_BUCKET:
        raise Exception(
            "No artifact bucket provided by the Workspace. Need to set the `S3_ARTIFACTS_BUCKET` setting in your workspace."
        )

    return ws.settings.S3_ARTIFACTS_BUCKET
