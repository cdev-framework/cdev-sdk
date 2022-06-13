import boto3
import json
from typing import Any, Dict
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import relational_db
from core.constructs.output_manager import OutputTask
from core.utils import hasher

from .. import aws_client


RUUID = "cdev::simple::relationaldb"


def _create_simple_relational_db(
    transaction_token: str,
    namespace_token: str,
    resource: relational_db.simple_relational_db_model,
    output_task: OutputTask,
) -> Dict:

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])
    cluster_name = f"cdev-relationaldb-{full_namespace_suffix}"

    output_task.update(comment=f"Creating DB {cluster_name}")

    rv = aws_client.run_client_function(
        "rds",
        "create_db_cluster",
        {
            "DatabaseName": resource.DatabaseName,
            "DBClusterIdentifier": cluster_name,
            "Engine": resource.Engine.value,
            "MasterUsername": resource.MasterUsername,
            "MasterUserPassword": resource.MasterUserPassword,
            "EnableHttpEndpoint": resource.EnableHttpEndpoint,
            "ScalingConfiguration": {
                "MinCapacity": resource.MinCapacity,
                "MaxCapacity": resource.MinCapacity,
                "AutoPause": resource.SecondsToPause != 0,
                "SecondsUntilAutoPause": resource.SecondsToPause
                if not resource.SecondsToPause == 0
                else 300,
            },
            "EngineMode": "serverless",  # Hard Code for this resource type
        },
    )

    output_task.update(comment=f"Creating Secrets for DB")
    # Need to create secret for this information so that it can be used with the data api
    secret_rv = aws_client.run_client_function(
        "secretsmanager",
        "create_secret",
        {
            "Name": f"{cluster_name}-config",
            "SecretString": json.dumps(
                {
                    "dbInstanceIdentifier": cluster_name,
                    "engine": resource.Engine.value,
                    "host": rv.get("DBCluster").get("Endpoint"),
                    "port": rv.get("DBCluster").get("Port"),
                    "resourceId": rv.get("DBCluster").get("DbClusterResourceId"),
                    "username": resource.MasterUsername,
                    "password": resource.MasterUserPassword,
                }
            ),
        },
    )

    output_task.update(
        comment=f"Wating for DB to become available. This might take a minute."
    )
    aws_client.monitor_status(
        boto3.client("rds").describe_db_clusters,
        {
            "DBClusterIdentifier": cluster_name,
        },
        "creating",
        lambda x: x.get("DBClusters")[0].get("Status"),
    )

    output_info = {
        "endpoint": rv.get("DBCluster").get("Endpoint"),
        "secret_arn": secret_rv.get("ARN"),
        "cloud_id": rv.get("DBCluster").get("DBClusterArn"),
        "cluster_arn": rv.get("DBCluster").get("DBClusterArn"),
        "cdev_name": resource.name,
        "cluster_name": cluster_name,
    }

    return output_info


def _update_simple_relational_db(
    transaction_token: str,
    previous_resource: relational_db.simple_relational_db_model,
    new_resource: relational_db.simple_relational_db_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> Dict:
    if not new_resource.Engine.value == previous_resource.Engine:
        raise Exception

    if not new_resource.MasterUsername == previous_resource.MasterUsername:
        raise Exception

    if not new_resource.DatabaseName == previous_resource.DatabaseName:
        raise Exception

    update_args = {"DBClusterIdentifier": previous_output.get("cluster_arn")}

    scaling_config = {}

    update_configuration_secret = False
    if not new_resource.MasterUserPassword == previous_resource.MasterUserPassword:
        update_args["MasterUserPassword"] = new_resource.MasterUserPassword
        update_args["ApplyImmediately"] = True
        update_configuration_secret = True

    if not new_resource.EnableHttpEndpoint == previous_resource.EnableHttpEndpoint:
        update_args["EnableHttpEndpoint"] = new_resource.EnableHttpEndpoint

    if not new_resource.MaxCapacity == previous_resource.MaxCapacity:
        scaling_config["MaxCapacity"] = new_resource.MaxCapacity

    if not new_resource.MinCapacity == previous_resource.MinCapacity:
        scaling_config["MinCapacity"] = new_resource.MinCapacity

    if not new_resource.SecondsToPause == previous_resource.SecondsToPause:
        scaling_config["AutoPause"] = new_resource.SecondsToPause == 0
        scaling_config["SecondsUntilAutoPause"] = (
            new_resource.SecondsToPause if not new_resource.SecondsToPause == 0 else 300
        )

    if scaling_config:
        update_args["ScalingConfiguration"] = scaling_config

    output_task.update(comment=f"Updating DB Configuration")
    aws_client.run_client_function("rds", "modify_db_cluster", update_args)

    if update_configuration_secret:
        # Update the password in the secret
        secret_arn = previous_output.get("secret_arn")

        current_secret_rv = aws_client.run_client_function(
            "secretsmanager", "get_secret_value", {"SecretId": secret_arn}
        )

        current_secret_obj = json.loads(current_secret_rv.get("SecretString"))

        output_task.update(comment=f"Updating DB Secret Configuration")
        aws_client.run_client_function(
            "secretsmanager",
            "put_secret_value",
            {
                "SecretId": secret_arn,
                "SecretString": json.dumps(
                    {
                        "dbInstanceIdentifier": current_secret_obj.get(
                            "dbInstanceIdentifier"
                        ),
                        "engine": current_secret_obj.get("engine"),
                        "host": current_secret_obj.get("host"),
                        "port": current_secret_obj.get("port"),
                        "resourceId": current_secret_obj.get("resourceId"),
                        "username": current_secret_obj.get("username"),
                        "password": new_resource.MasterUserPassword,
                    }
                ),
            },
        )

    # None of the updatable values actually effect the output
    return previous_output


def _remove_simple_relational_db(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    cluster_id = previous_output.get("cluster_name")

    output_task.update(
        comment=f"[blink]Deleting DB. This could take a few minutes[/blink]"
    )

    aws_client.run_client_function(
        "rds",
        "delete_db_cluster",
        {
            "DBClusterIdentifier": cluster_id,
            "SkipFinalSnapshot": True,
        },
    )

    # Update the password in the secret
    secret_arn = previous_output.get("secret_arn")

    output_task.update(comment=f"Deleting DB Secret")

    aws_client.run_client_function(
        "secretsmanager", "delete_secret", {"SecretId": secret_arn}
    )


def handle_simple_relational_db_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_relational_db(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_relational_db(
            transaction_token,
            relational_db.simple_relational_db_model(
                **resource_diff.previous_resource.dict()
            ),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_relational_db(transaction_token, previous_output, output_task)

        return {}
