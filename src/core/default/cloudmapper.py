from typing import Dict, List

from ..constructs.resource import Resource_Change_Type, Resource_Reference_Difference, Resource_Difference
from ..constructs.mapper import CloudMapper
from ..settings import SETTINGS

#from .mappers.aws import aws_lambda, dynamodb, iam, s3, sqs, apigatewayv2, apigateway

from ..mappers.simple import api_deployer#, lambda_deployer, dynamodb_deployer, bucket_deployer
#from ..mappers.simple import queue_deployer, topic_deployer, relational_db_deployer, static_site_deployer


class DefaultMapper(CloudMapper):   
    
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, transaction_token: str, namespace_token: str, resource_diff: Resource_Difference, previous_output: Dict) -> Dict:
        ruuid = resource_diff.new_resource.ruuid if resource_diff.new_resource else resource_diff.previous_resource.ruuid

        return self.get_resource_to_handler()[ruuid](transaction_token, namespace_token, resource_diff, previous_output)
        
        


RESOURCE_TO_HANDLER_FUNCTION = {
    #"cdev::aws::lambda_function": aws_lambda.handle_aws_lambda_deployment,
    #"cdev::aws::dynamodb::table": dynamodb.handle_table_deployment,
    #"cdev::aws::iam::policy": iam.handle_policy_deployment,
    #"cdev::aws::iam::role": iam.handle_role_deployment,
    #"cdev::aws::s3::bucket": s3.handle_bucket_deployment,
    #"cdev::aws::sqs::queue": sqs.handle_queue_deployment,
    #"cdev::aws::apigatewayv2::api": apigatewayv2.handle_api_deployment,
    #"cdev::aws::apigatewayv2::route": apigatewayv2.handle_route_deployment,
    #"cdev::aws::apigatewayv2::integration": apigatewayv2.handle_integration_deployment,
    #"cdev::aws::apigatewayv2::stage": apigatewayv2.handle_stage_deployment,
    #"cdev::aws::apigatewayv2::deployment": apigatewayv2.handle_deployment_deployment,
    #"cdev::aws::apigateway::restapi": apigateway.handle_restapi_deployment,
    #"cdev::aws::apigateway::resource":  apigateway.handle_resource_deployment,
    #"cdev::aws::apigateway::deployment":  apigateway.handle_deployment_deployment,
    #"cdev::aws::apigateway::integration":  apigateway.handle_integration_deployment,
    #"cdev::aws::apigateway::stage":  apigateway.handle_stage_deployment,
    #"cdev::aws::apigateway::method": apigateway.handle_method_deployment,
    #"cdev::aws::apigateway::integration_response": apigateway.handle_integrationresponse_deployment,

    "cdev::simple::api": api_deployer.handle_simple_api_deployment,
    #"cdev::simple::lambda_function": lambda_deployer.handle_simple_lambda_function_deployment,
    #"cdev::simple::table": dynamodb_deployer.handle_simple_table_deployment,
    #"cdev::simple::bucket": bucket_deployer.handle_simple_bucket_deployment,
    #"cdev::simple::queue": queue_deployer.handle_simple_queue_deployment,
    #"cdev::simple::topic": topic_deployer.handle_simple_topic_deployment,
    #"cdev::simple::relationaldb": relational_db_deployer.handle_simple_relational_db_deployment,
    #"cdev::simple::staticsite": static_site_deployer.handle_simple_static_site_deployment
}
