from time import sleep
import boto3
from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import relational_db 
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client
from cdev.output import print_deployment_step
import json

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

log = logger.get_cdev_logger(__name__)

RUUID = "cdev::simple::relationaldb"

def _create_simple_relational_db(identifier: str, resource: relational_db.simple_relational_db_model) -> bool:
    # Create Table
    print_deployment_step("CREATE", f"[blink]Creating relational db {resource.name} (this will take a few minutes)[/blink]")
    rv = raw_aws_client.run_client_function("rds", "create_db_cluster", {
            "DatabaseName": resource.DatabaseName,
            "DBClusterIdentifier": resource.DBClusterIdentifier,
            "Engine": resource.Engine.value,
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

    print_deployment_step("CREATE", f"  Created database")
    # Need to create secret for this information so that it can be used with the data api
    secret_rv = raw_aws_client.run_client_function("secretsmanager", "create_secret", {
        "Name": f"{resource.DBClusterIdentifier}-config",
        "SecretString": json.dumps({
            "dbInstanceIdentifier": resource.DBClusterIdentifier,
            "engine": resource.Engine.value,
            "host": rv.get("DBCluster").get("Endpoint"),
            "port": rv.get("DBCluster").get("Port"),
            "resourceId": rv.get("DBCluster").get("DbClusterResourceId"),
            "username": resource.MasterUsername,
            "password": resource.MasterUserPassword,
        })
    })

    print_deployment_step("CREATE", f"  Created database configuration secret")
    print_deployment_step("CREATE", f"  Waiting for database to become available")

    raw_aws_client.monitor_status(
        boto3.client("rds").describe_db_clusters, {
            "DBClusterIdentifier": resource.DBClusterIdentifier,
        },
        "creating",
        lambda x: x.get("DBClusters")[0].get("Status")
    )
    

    print_deployment_step("CREATE", f"  {resource.name} is available")

    output_info = {
        "endpoint": rv.get("DBCluster").get("Endpoint") ,
        "secret_arn": secret_rv.get("ARN"),
        "cloud_id": rv.get("DBCluster").get("DBClusterArn"), 
        "arn": rv.get("DBCluster").get("DBClusterArn"), 
        "cdev_name": resource.name,
        "ruuid": resource.ruuid
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)

    return True


def _update_simple_relational_db(previous_resource: relational_db.simple_relational_db_model, new_resource: relational_db.simple_relational_db_model) -> bool:
    if not new_resource.Engine.value == previous_resource.Engine:
        print(f"Cant not update Engine; {previous_resource.Engine} -> {new_resource.Engine}")
        return False

    if not new_resource.MasterUsername == previous_resource.MasterUsername:
        print("Cant update Master Username")
        return False

    if not new_resource.DBClusterIdentifier == previous_resource.DBClusterIdentifier:
        print("Cant update DB cluster info")
        return False

    if not new_resource.DatabaseName == previous_resource.DatabaseName:
        print("Cant update db name")
        return False

    if not new_resource.Port == previous_resource.Port:
        print("Cant update db port")
        return False

    update_args = {
        "DBClusterIdentifier": new_resource.DBClusterIdentifier
    }

    scaling_config = {

    }

    update_configuration_secret = False
    if not new_resource.MasterUserPassword == previous_resource.MasterUserPassword:
        update_args['MasterUserPassword'] = new_resource.MasterUserPassword
        update_args['ApplyImmediately'] = True
        update_configuration_secret = True


    if not new_resource.EnableHttpEndpoint == previous_resource.EnableHttpEndpoint:
        update_args['EnableHttpEndpoint'] = new_resource.EnableHttpEndpoint

    if not new_resource.MaxCapacity == previous_resource.MaxCapacity:
        scaling_config['MaxCapacity'] = new_resource.MaxCapacity

    if not new_resource.MinCapacity == previous_resource.MinCapacity:
        scaling_config["MinCapacity"] = new_resource.MinCapacity

    if not new_resource.SecondsToPause == previous_resource.SecondsToPause:
        scaling_config["AutoPause"] = new_resource.SecondsToPause == 0
        scaling_config["SecondsUntilAutoPause"] = new_resource.SecondsToPause if not new_resource.SecondsToPause == 0 else 300

    
    if scaling_config:
        update_args["ScalingConfiguration"] = scaling_config

    raw_aws_client.run_client_function("rds", "modify_db_cluster", update_args)


    if update_configuration_secret:
        # Update the password in the secret
        secret_arn = cdev_cloud_mapper.get_output_value_by_hash(previous_resource.hash, "secret_arn")


        current_secret_rv = raw_aws_client.run_client_function("secretsmanager", "get_secret_value", {
            "SecretId": secret_arn
        })

        current_secret_obj = json.loads(current_secret_rv.get("SecretString"))

        secret_rv = raw_aws_client.run_client_function("secretsmanager", "put_secret_value", {
            "SecretId": secret_arn,
            "SecretString": json.dumps({
                "dbInstanceIdentifier": current_secret_obj.get("dbInstanceIdentifier"),
                "engine": current_secret_obj.get("engine"),
                "host": current_secret_obj.get("host"),
                "port": current_secret_obj.get("port"),
                "resourceId": current_secret_obj.get("resourceId"),
                "username": current_secret_obj.get("username"),
                "password": new_resource.MasterUserPassword,
            })
        })
        print_deployment_step("UPDATE", f"  Updated configuration secret {new_resource.name}")


    cdev_cloud_mapper.reidentify_cloud_resource(previous_resource.hash, new_resource.hash)
    print_deployment_step("UPDATE", f"  Finished updating relational db {new_resource.name}")

    return True
    
    

def _remove_simple_relational_db(identifier: str, resource: relational_db.simple_relational_db_model) -> bool:
    print_deployment_step("DELETE", f"[blink]Deleting relational db {resource.name} (this will take a few minutes)[/blink]")
    
    raw_aws_client.run_client_function("rds", "delete_db_cluster", {
        "DBClusterIdentifier": resource.DBClusterIdentifier,
        "SkipFinalSnapshot": True
    })


    # Update the password in the secret
    secret_arn = cdev_cloud_mapper.get_output_value_by_hash(resource.hash, "secret_arn")


    raw_aws_client.run_client_function("secretsmanager", "delete_secret", {
        "SecretId": secret_arn
    })
    print_deployment_step("DELETE", f"Removed configuration secret {resource.name}")


    print_deployment_step("DELETE", f"Removed relational db {resource.name}")
    
    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")

    return True



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
