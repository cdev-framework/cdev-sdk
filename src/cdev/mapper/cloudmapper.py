import os
from typing import List
import zipfile
from cdev.mapper.backend.aws.aws_lambda_models import create_aws_lambda_function, delete_aws_lambda_function


from cdev.models import Action_Type, Resource_State_Difference
from cdev.constructs import CloudMapper
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper as cdev_cloud_mapper

from .backend.aws import aws_lambda
from .backend.aws import aws_s3, aws_s3_models 

from cdev.resources.aws.s3 import s3_object
from cdev.resources.aws.lambda_function import lambda_function_configuration, lambda_runtime_environments, lambda_function_configuration_environment


class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, component_name: str, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        
        
        if not resource_diff.action_type == Action_Type.DELETE:
            if not resource_diff.new_resource.ruuid in self.get_resource_to_handler():
                # TODO throw error
                print(f"PROVIDER CAN NOT CREATE RESOURCE: {resource_diff.new_resource.ruuid}")

            self.get_resource_to_handler()[resource_diff.new_resource.ruuid](resource_diff)

        else:
            self.get_resource_to_handler()[resource_diff.previous_resource.ruuid](resource_diff)

        print(f"DEPLOYING -> {component_name}:{resource_diff}")


        

        return True


def handle_aws_lambda_deployment(resource_diff: Resource_State_Difference):
    # TODO throw error if resource is not lambda function

    if resource_diff.action_type == Action_Type.CREATE:
        try: 
            filename = os.path.split(resource_diff.new_resource.parsed_path)[1]
            original_zipname = filename[:-3] + ".zip"
            keyname = filename[:-3] + f"-{resource_diff.new_resource.hash}" + ".zip"
            zip_location = os.path.join(os.path.dirname(resource_diff.new_resource.parsed_path), original_zipname )
            
            aws_s3.put_object(put_object_event=aws_s3_models.put_object_event(**{
                "Filename": zip_location,
                "Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                "Key": keyname
            }))

            cdev_cloud_mapper.add_cloud_resource(resource_diff.new_resource.hash, {
            "Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
            "Key": keyname
            })
            


            base_config = lambda_function_configuration(
                Role="arn:aws:iam::369004794337:role/test-lambda-role",
                Handler=filename[:-3]+"."+resource_diff.new_resource.handler_name,
                Description="MyDescription",
                Timeout=60,
                MemorySize=128,
                Environment={"Variables": resource_diff.new_resource.configuration},
                Runtime=lambda_runtime_environments.python3_6,
            )

            event = create_aws_lambda_function(resource_diff.new_resource.hash, s3_object(**{
                                                "S3Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                                                "S3Key": keyname
                                                }),
                                                base_config)

            
            aws_lambda.create_lambda_function(event)

            cdev_cloud_mapper.add_cloud_resource(resource_diff.new_resource.hash, {
                "FunctionName": resource_diff.new_resource.hash,
                "Code": s3_object(**{
                        "S3Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                        "S3Key": keyname
                    }),
                "Configuration": base_config
            })

        except Exception as e:
            print(e)

    elif resource_diff.action_type == Action_Type.DELETE:
        try:
            filename = os.path.split(resource_diff.previous_resource.parsed_path)[1]
            original_zipname = filename[:-3] + ".zip"
            keyname = filename[:-3] + f"-{resource_diff.previous_resource.hash}" + ".zip"
            zip_location = os.path.join(os.path.dirname(resource_diff.previous_resource.parsed_path), original_zipname )


            aws_lambda.delete_lambda_function(delete_aws_lambda_function(
                **{"FunctionName": resource_diff.previous_resource.hash}
            ))

            base_config = lambda_function_configuration(
                Role="arn:aws:iam::369004794337:role/test-lambda-role",
                Handler=filename[:-3]+"."+resource_diff.previous_resource.handler_name,
                Description="MyDescription",
                Timeout=60,
                MemorySize=128,
                Environment={"Variables": resource_diff.previous_resource.configuration},
                Runtime=lambda_runtime_environments.python3_6,
            )

            cdev_cloud_mapper.remove_cloud_resource(resource_diff.previous_resource.hash, 
                {
                "FunctionName": resource_diff.previous_resource.hash,
                "Code": s3_object(**{
                        "S3Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                        "S3Key": keyname
                    }),
                "Configuration": base_config
                }
            )

            cdev_cloud_mapper.remove_cloud_resource(resource_diff.previous_resource.hash, {
            "Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
            "Key": keyname
            })

            cdev_cloud_mapper.remove_indentifier(resource_diff.previous_resource.hash)

        except Exception as e:
            print(e)
        

    

def handle_aws_dynamodb_deployment(resource_diff: Resource_State_Difference):
    # TODO throw error if resource is not lambda function
    if resource_diff.action_type == Action_Type.CREATE:
        cdev_cloud_mapper.add_cloud_resource(resource_diff.new_resource.hash, {"s3key": resource_diff.new_resource.TableName})
    
    print(f"DYNAMODB {resource_diff}")


RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::general::parsed_function": handle_aws_lambda_deployment,
    "cdev::aws::dynamodb": handle_aws_dynamodb_deployment
}
