import boto3
from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import relational_db 
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client
from cdev.output import print_deployment_step

log = logger.get_cdev_logger(__name__)

RUUID = "cdev::simple::relationaldb"

def _create_simple_relational_db(identifier: str, resource: relational_db.simple_relational_db_model) -> bool:
    # Create Table
    print_deployment_step("CREATE", f"[blink]Creating relational db {resource.name} (this will take a few minutes)[/blink]")
    rv = raw_aws_client.run_client_function("rds", "create_db_cluster", {
            "DatabaseName": resource.DatabaseName,
            "DBClusterIdentifier": resource.DBClusterIdentifier,
            "Engine": resource.Engine.value,
            "Port": resource.Port,
            "MasterUsername": resource.MasterUsername,
            "MasterUserPassword": resource.MasterUserPassword,
            "EnableHttpEndpoint": resource.EnableHttpEndpoint,
            "ScalingConfiguration": {
                "MinCapacity": resource.MinCapacity,
                "MaxCapacity": resource.MinCapacity,
                "AutoPause": resource.SecondsToPause == 0,
                "SecondsUntilAutoPause": resource.SecondsToPause if not resource.SecondsToPause == 0 else 300
            },
            "EngineMode": "serverless" # Hard Code for this resource type
        }
    )

    raw_aws_client.monitor_status(
        boto3.client("rds").describe_db_clusters, {
            "DBClusterIdentifier": resource.DBClusterIdentifier,
        },
        "creating",
        lambda x: x.get("DBClusters")[0].get("Status")
    )
    
    #raw_aws_client.aws_resource_wait("rds", {
    #        "name": "db_instance_available",
    #        "args": {
    #            "Filters":[
    #                {
    #                "Name": "db-cluster-id",
    #                "Values": [
    #                   rv.get("DBCluster").get("DBClusterArn") ,
    #                ]
    #                }
    #            ]
    #        }
    #    }
    #)

    print_deployment_step("CREATE", f"  Created database {resource.name}")

    output_info = {
        "endpoint": rv.get("DBCluster").get("Endpoint") ,
        "secret_arn": "123",
        "cloud_id": rv.get("DBCluster").get("DBClusterArn"), 
        "arn": rv.get("DBCluster").get("DBClusterArn"), 
        "cdev_name": resource.name,
        "ruuid": resource.ruuid
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)

    return True


def _update_simple_relational_db(previous_resource: relational_db.simple_relational_db_model, new_resource: relational_db.simple_relational_db_model) -> bool:
    pass


def _remove_simple_relational_db(identifier: str, resource: relational_db.simple_relational_db_model) -> bool:
    pass


def handle_simple_relational_db_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_relational_db(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return _update_simple_relational_db(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return _remove_simple_relational_db(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")