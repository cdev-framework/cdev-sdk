from time import sleep
from typing import Dict
from uuid import uuid4

from core.default.resources.simple import xlambda as simple_lambda
from core.default.resources.simple import api as simple_api
from core.default.resources.simple import object_store as simple_bucket
from core.default.resources.simple import table as simple_table
from core.default.resources.simple import queue as simple_queue
from core.default.resources.simple import topic as simple_topic

from .. import aws_client

from . import bucket_deployer
from . import topic_deployer


##############################################
###### API GATEWAY ROUTE EVENTS
##############################################
def _handle_adding_api_event(
    event: simple_api.route_event_model, cloud_function_id: str
) -> Dict:
    # Needed info
    #   - Event model
    #   - originating resource output
    #   - responding resource output

    # Returns:
    #   - Info about the deployed stuff

    api_id = event.api_id
    route_id = event.route_id

    args = {
        "IntegrationType": "AWS_PROXY",
        "IntegrationUri": cloud_function_id,
        "PayloadFormatVersion": "2.0",
        "IntegrationMethod": event.verb,
        "ApiId": api_id,
    }

    if event.response_type:
        args.update(
            {
                "ResponseParameters": {
                    "200": {"overwrite:header.Content-Type": event.response_type}
                }
            }
        )

    integration_rv = aws_client.run_client_function(
        "apigatewayv2", "create_integration", args
    )

    # Now that the integration has been created we need to attach it to the apigateway route
    update_info = {
        "ApiId": api_id,
        "RouteId": route_id,
        "Target": f"integrations/{integration_rv.get('IntegrationId')}",
    }

    aws_client.run_client_function("apigatewayv2", "update_route", update_info)

    aws_region = aws_client.get_aws_region()
    aws_account = aws_client.get_account_number()

    # Add permission to lambda to allow apigateway to invoke this function
    stmt_id = f"stmt-{route_id}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "apigateway.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": f"arn:aws:execute-api:{aws_region}:{aws_account}:{api_id}/*/{event.verb}{event.path}",
    }

    aws_client.run_client_function("lambda", "add_permission", permission_model_args)

    return {
        "integration_id": integration_rv.get("IntegrationId"),
        "permission_stmt_id": stmt_id,
        "api_id": api_id,
        "route_id": route_id,
    }


def _handle_deleting_api_event(event: dict, function_cloud_id: str) -> bool:
    cloud_id = function_cloud_id
    integration_id = event.get("integration_id")
    stmt_id = event.get("permission_stmt_id")

    api_id = event.get("api_id")
    route_id = event.get("route_id")

    # Delete the permission on the lambda function
    aws_client.run_client_function(
        "lambda",
        "remove_permission",
        {"FunctionName": cloud_id, "StatementId": stmt_id},
    )

    # To delete a route event from a simple api we need to delete the integration.
    # Leave the target blank so that the route has no integration.
    # Then delete the actual integration cloud obj
    update_info = {"ApiId": api_id, "RouteId": route_id, "Target": ""}

    # Stop Gap Solution
    # When an event is being removed, it can be because of two reasons:
    # 1. The event was removed, but the route still exists
    # 2. The event and route were removed.
    # To accommodate both situations, we need to try to the update the route to remove
    # the integration, but not fail completely when/if the route has already been deleted.

    # We are catching the base exception because to catch a direct exception from boto3, we need to
    # have access to the boto3 client.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#catching-exceptions-when-using-a-resource-client
    try:
        aws_client.run_client_function("apigatewayv2", "update_route", update_info)
    except Exception:
        pass

    aws_client.run_client_function(
        "apigatewayv2",
        "delete_integration",
        {"ApiId": api_id, "IntegrationId": integration_id},
    )


##############################################
##### DYNAMODB TABLE STREAM EVENT
##############################################


def _handle_adding_stream_event(
    event: simple_table.stream_event_model, cloud_function_id
) -> Dict:
    table_name = event.table_name
    view_type = event.view_type
    batch_size = event.batch_size

    rv = aws_client.run_client_function(
        "dynamodb", "describe_table", {"TableName": table_name}
    )

    if not rv.get("Table").get("StreamSpecification"):
        rv = aws_client.run_client_function(
            "dynamodb",
            "update_table",
            {
                "TableName": table_name,
                "StreamSpecification": {
                    "StreamEnabled": True,
                    "StreamViewType": view_type,
                },
            },
        )
        table_data = rv.get("TableDescription")

    else:
        if not rv.get("Table").get("StreamSpecification").get("StreamEnabled"):
            rv = aws_client.run_client_function(
                "dynamodb",
                "update_table",
                {
                    "TableName": table_name,
                    "StreamSpecification": {
                        "StreamEnabled": True,
                        "StreamViewType": view_type,
                    },
                },
            )
            table_data = rv.get("TableDescription")

        else:
            table_data = rv.get("Table")

    stream_arn = table_data.get("LatestStreamArn")

    sleep(5)
    function_response_types = [] if event.batch_failure else ["ReportBatchItemFailures"]

    rv = aws_client.run_client_function(
        "lambda",
        "create_event_source_mapping",
        {
            "EventSourceArn": stream_arn,
            "FunctionName": cloud_function_id,
            "Enabled": True,
            "BatchSize": batch_size,
            "StartingPosition": "LATEST",
            "FunctionResponseTypes": function_response_types,
        },
    )

    uuid = rv.get("UUID")

    return {"stream_arn": stream_arn, "stream_event_id": uuid}


def _handle_deleting_stream_event(event: dict, function_cloud_id: str):
    uuid = event.get("stream_event_id")

    aws_client.run_client_function(
        "lambda", "delete_event_source_mapping", {"UUID": uuid}
    )


##############################################
##### BUCKET EVENT TRIGGER
##############################################


def _handle_adding_bucket_event(
    bucket_event: simple_bucket.bucket_event_model, cloud_function_id: str
) -> Dict:

    bucket_arn = bucket_event.bucket_arn
    bucket_name = bucket_event.bucket_name
    events = [bucket_event.bucket_event_type.value]

    # Add permission to lambda to allow s3 to invoke this function
    stmt_id = f"stmt-{str(uuid4())}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "s3.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": bucket_arn,
    }

    aws_client.run_client_function("lambda", "add_permission", permission_model_args)

    # Add trigger to the bucket... use helper function in the bucket deployer because bucket can send events to sqs and sns also
    print(f"event to add {events}")

    # Wait a few seconds for the newly added permissions to take hold
    # if this happens too fast, it will say the lambda does not have correct permissions to be triggered.
    sleep(5)

    bucket_event_id = bucket_deployer.add_eventsource(
        bucket_name,
        bucket_deployer.event_hander_types.LAMBDA,
        cloud_function_id,
        events,
    )

    return {
        "bucket_event_id": bucket_event_id,
        "permission_stmt_id": stmt_id,
        "bucket_name": bucket_name,
    }


def _handle_deleting_bucket_event(event: dict, function_cloud_id: str):

    bucket_event_id = event.get("bucket_event_id")
    bucket_name = event.get("bucket_name")
    stmt_id = event.get("permission_stmt_id")

    # Delete the permission on the lambda function
    aws_client.run_client_function(
        "lambda",
        "remove_permission",
        {"FunctionName": function_cloud_id, "StatementId": stmt_id},
    )

    bucket_deployer.remove_eventsource(bucket_name, bucket_event_id)


##############################################
##### QUEUE EVENT TRIGGER
##############################################


def _handle_adding_queue_event(
    event: simple_queue.queue_event_model, cloud_function_id
) -> Dict:
    queue_arn = event.queue_arn
    batch_size = event.batch_size

    function_response_types = [] if event.batch_failure else ["ReportBatchItemFailures"]

    rv = aws_client.run_client_function(
        "lambda",
        "create_event_source_mapping",
        {
            "EventSourceArn": queue_arn,
            "FunctionName": cloud_function_id,
            "Enabled": True,
            "BatchSize": batch_size,
            "FunctionResponseTypes": function_response_types,
        },
    )

    uuid = rv.get("UUID")

    return {"queue_event_id": uuid}


def _handle_deleting_queue_event(event: dict, function_cloud_id: str) -> None:
    queue_event_id = event.get("queue_event_id")

    aws_client.run_client_function(
        "lambda", "delete_event_source_mapping", {"UUID": queue_event_id}
    )


##############################################
##### TOPIC EVENT TRIGGER
##############################################


def _handle_adding_topic_subscription(
    event: simple_topic.topic_event_model, cloud_function_id
) -> Dict:
    topic_arn = event.topic_arn

    # Add permission to lambda to allow apigateway to invoke this function
    stmt_id = f"stmt-{str(uuid4())}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "sns.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": topic_arn,
    }

    aws_client.run_client_function("lambda", "add_permission", permission_model_args)

    subscribe_arn = topic_deployer.add_subscriber(
        topic_arn, "lambda", cloud_function_id
    )

    return {"topic_event_id": subscribe_arn, "permission_stmt_id": stmt_id}


def _handle_deleting_topic_subscription(event: dict, function_cloud_id: str) -> bool:
    subscription_arn = event.get("topic_event_id")
    permission_stmt_id = event.get("permission_stmt_id")

    # Delete the permission on the lambda function
    aws_client.run_client_function(
        "lambda",
        "remove_permission",
        {"FunctionName": function_cloud_id, "StatementId": permission_stmt_id},
    )

    # Remove subscription
    topic_deployer.remove_subscriber(subscription_arn)

    return True


EVENT_TO_HANDLERS = {
    simple_lambda.RUUID: {
        simple_api.RUUID: {
            "CREATE": _handle_adding_api_event,
            "REMOVE": _handle_deleting_api_event,
        },
        simple_bucket.RUUID: {
            "CREATE": _handle_adding_bucket_event,
            "REMOVE": _handle_deleting_bucket_event,
        },
        simple_table.RUUID: {
            "CREATE": _handle_adding_stream_event,
            "REMOVE": _handle_deleting_stream_event,
        },
        simple_queue.RUUID: {
            "CREATE": _handle_adding_queue_event,
            "REMOVE": _handle_deleting_queue_event,
        },
        simple_topic.RUUID: {
            "CREATE": _handle_adding_topic_subscription,
            "REMOVE": _handle_deleting_topic_subscription,
        },
    },
}
