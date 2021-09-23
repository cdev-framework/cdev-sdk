from typing import Dict
from cdev.resources.aws.apigatewayv2_models import  IntegrationType
from cdev.utils import logger
from cdev.resources.simple import xlambda as simple_lambda
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper


from ..aws import aws_client as raw_aws_client

from . import bucket_deployer, topic_deployer



from cdev.settings import SETTINGS


log = logger.get_cdev_logger(__name__)


##############################################
###### API GATEWAY ROUTE EVENTS
##############################################

def _handle_adding_api_event(event, cloud_function_id) -> Dict:
    log.debug(f"Attempting to create {event} for function {cloud_function_id}")
    api_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::api", event.original_resource_name)
    log.debug(f"Found Api info for {event} -> {api_resource}")
    api_id = api_resource.get("cloud_id")
    routes = api_resource.get("endpoints")

    route_id=""
    for route in routes:
        if routes.get(route).get("route") == event.config.get("path") and routes.get(route).get("verbs") == event.config.get("verb"):
            log.debug(f"Found route information -> {route}")
            route_id = routes.get(route).get("cloud_id")
            route_verb = event.config.get("verb")
            route_path = event.config.get("path")
            break

    if not route_id:
        log.error(f"could not find route info for event {event} in routes {routes} from api info {api_resource}")
        return False

    log.debug(f"Route ID -> {route_id}")
    log.debug(f"Route Integration Method: {route_verb}")
    args = {
        "IntegrationType": IntegrationType.AWS_PROXY,
        "IntegrationUri": cloud_function_id,
        "PayloadFormatVersion": "2.0",
        "IntegrationMethod": f"{route_verb}",
        "ApiId": api_id
    }

    integration_rv = raw_aws_client.run_client_function("apigatewayv2", "create_integration", args)

    # Now that the integration has been created we need to attach it to the apigateway route
    update_info = {
        "ApiId": api_id,
        "RouteId": route_id,
        "Target": f"integrations/{integration_rv.get('IntegrationId')}"
    }

    raw_aws_client.run_client_function("apigatewayv2", "update_route", update_info)


    # Add permission to lambda to allow apigateway to invoke this function
    stmt_id = f"stmt-{event.original_resource_name}-{route_id}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "apigateway.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": f"arn:aws:execute-api:{SETTINGS.get('AWS_REGION')}:{SETTINGS['AWS_ACCOUNT']}:{api_id}/*/{route_verb}{route_path}"
    }

    raw_aws_client.run_client_function("lambda", "add_permission", permission_model_args)

    return {"UUID": integration_rv.get("IntegrationId"), "event_type": "api::endpoint", "Stmt_id": stmt_id}



def _handle_deleting_api_event(event: simple_lambda.Event, resource_hash) -> bool:
    log.debug(f"Attempting to delete {event} from function {resource_hash}")
    
    # Go ahead and make sure we have info for this event in the function's output and cloud integration id of this event
    function_event_info = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "events")
    log.debug(f"Function event info {function_event_info}")

    if not event.get_hash() in function_event_info:
        log.error(f"Could not find info for {event} ({event.get_hash()}) in function ({resource_hash}) output")
        return False

    integration_id = function_event_info.get(event.get_hash()).get("UUID")
    stmt_id = function_event_info.get(event.get_hash()).get("Stmt_id")
    cloud_id = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "cloud_id")

    # Delete the permission on the lambda function
    raw_aws_client.run_client_function("lambda", "remove_permission", {
        "FunctionName": cloud_id,
        "StatementId": stmt_id
    })

    # To delete a route event from a simple api we need to delete the integration.
    # This requires first detaching the integration from the route then deleting the integration. 
    try:
        api_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::api", event.original_resource_name)
    except Exception as e:
        log.debug(e)
        log.error(f"Looking up 'cdev::simple::api' {event.original_resource_name} in cloud_output")

    log.debug(f"Found api info for event -> {api_resource}")
    api_id = api_resource.get("cloud_id")
    routes = api_resource.get("endpoints")

    route_id=""
    for route in routes:
        if routes.get(route).get("route") == event.config.get("path") and routes.get(route).get("verbs") == event.config.get("verb"):
            log.debug(f"Found route information -> {route}")
            route_id = routes.get(route).get("cloud_id")

    if not route_id:
        log.error(f"could not find route info for event {event} in routes {routes} from api info {api_resource}")
        return False
    
    update_info = {
        "ApiId": api_id,
        "RouteId": route_id,
        "Target": ""
    }

    raw_aws_client.run_client_function("apigatewayv2", "update_route", update_info)

    log.debug(f"Removed integration {integration_id} from route {route_id} in api {api_id}")
   
    raw_aws_client.run_client_function("apigatewayv2", "delete_integration", {
        "ApiId": api_id,
        "IntegrationId": integration_id
    })

    log.debug(f"Removed integration {integration_id} from api {api_id}")

    return True


##############################################
##### DYNAMODB TABLE STREAM EVENT
##############################################

def _handle_adding_stream_event(event: simple_lambda.Event, cloud_function_id) -> Dict:
    log.debug(f"Attempting to create {event} for function {cloud_function_id}")
    table_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::table", event.original_resource_name)
    log.debug(f"Found Table info for {event} -> {table_resource}")

    rv = raw_aws_client.run_client_function("dynamodb", "describe_table", {
        'TableName': table_resource.get("table_name")
    })

    if not rv.get("Table").get("StreamSpecification"):
        rv = raw_aws_client.run_client_function("dynamodb", "update_table", {
            "TableName": table_resource.get("table_name"),
            "StreamSpecification": {
                "StreamEnabled": True,
                "StreamViewType": event.config.get("ViewType")
            }
        })
        table_data = rv.get("TableDescription")

    else:
        if not rv.get("Table").get("StreamSpecification").get("StreamEnabled"):
            rv = raw_aws_client.run_client_function("dynamodb", "update_table", {
            "TableName": table_resource.get("table_name"),
            "StreamSpecification": {
                "StreamEnabled": True,
                "StreamViewType": event.config.get("ViewType")
            }
            })
            table_data = rv.get("TableDescription")

        else:
            table_data = rv.get("Table") 

    stream_arn = table_data.get("LatestStreamArn")
    log.debug(f"Created Stream with arn: {stream_arn}")

    rv = raw_aws_client.run_client_function("lambda", "create_event_source_mapping", {
        "EventSourceArn": stream_arn,
        "FunctionName": cloud_function_id,
        "Enabled": True,
        "BatchSize": event.config.get("BatchSize"),
        "StartingPosition": "LATEST"
    })

    uuid = rv.get("UUID")


    return {"stream_arn": stream_arn, "event_type": "table::stream", "UUID": uuid}



def _handle_deleting_stream_event(event: simple_lambda.Event, resource_hash) -> bool:
    log.debug(f"Attempting to delete {event} from function {resource_hash}")
    # Go ahead and make sure we have info for this event in the function's output and cloud integration id of this event
    function_event_info = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "events")
    log.debug(f"Function event info {function_event_info}")
    log.debug(event)
    if not event.get_hash() in function_event_info:
        log.error(f"Could not find info for {event} ({event.get_hash()}) in function ({resource_hash}) output")
        return False

    uuid = function_event_info.get(event.get_hash()).get("UUID")

    raw_aws_client.run_client_function("lambda", "delete_event_source_mapping", {
        "UUID": uuid
    })
    log.debug(f"Removed Event {uuid} from {resource_hash}")

    return True


##############################################
##### BUCKET EVENT TRIGGER
##############################################

def _handle_adding_bucket_event(event: simple_lambda.Event, cloud_function_id) -> Dict:
    log.debug(f"Attempting to create {event} for function {cloud_function_id}")
    bucket_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::bucket", event.original_resource_name)
    log.debug(f"Found Bucket info for {event} -> {bucket_resource}")
    bucket_arn = bucket_resource.get("arn")
    bucket_name = bucket_resource.get("bucket_name")


    # Add permission to lambda to allow s3 to invoke this function
    stmt_id = f"stmt-{event.original_resource_name}-{bucket_name}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "s3.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": bucket_arn
    }

    raw_aws_client.run_client_function("lambda", "add_permission", permission_model_args)


    # Add trigger to the bucket... use helper function in the bucket deployer because bucket can send events to sqs and sns also 
    bucket_event_id = bucket_deployer.add_eventsource(bucket_name, bucket_deployer.event_hander_types.LAMBDA, cloud_function_id, event.config.get("EventTypes"))

    return {"UUID": bucket_event_id, "event_type": "bucket::event", "Stmt_id": stmt_id, "bucket_name": bucket_name}


def _handle_deleting_bucket_event(event: simple_lambda.Event, resource_hash) -> bool:
    log.debug(f"Attempting to delete {event} from function {resource_hash}")
    
    # Go ahead and make sure we have info for this event in the function's output and cloud integration id of this event
    function_event_info = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "events")
    log.debug(f"Function event info {function_event_info}")

    if not event.get_hash() in function_event_info:
        log.error(f"Could not find info for {event} ({event.get_hash()}) in function ({resource_hash}) output")
        return False

    bucket_event_id = function_event_info.get(event.get_hash()).get("UUID")
    bucket_name = function_event_info.get(event.get_hash()).get("bucket_name")
    stmt_id = function_event_info.get(event.get_hash()).get("Stmt_id")
    cloud_id = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "cloud_id")

    # Delete the permission on the lambda function
    raw_aws_client.run_client_function("lambda", "remove_permission", {
        "FunctionName": cloud_id,
        "StatementId": stmt_id
    })


    bucket_deployer.remove_eventsource(bucket_name, bucket_event_id)

    log.debug(f"Removed Event {event} from {resource_hash}")

    return True


##############################################
##### QUEUE EVENT TRIGGER
##############################################


def _handle_adding_queue_event(event: simple_lambda.Event, cloud_function_id) -> Dict:
    log.debug(f"Attempting to create {event} for function {cloud_function_id}")
    queue_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::queue", event.original_resource_name)
    log.debug(f"Found Table info for {event} -> {queue_resource}")

    

    

    rv = raw_aws_client.run_client_function("lambda", "create_event_source_mapping", {
        "EventSourceArn": queue_resource.get("arn"),
        "FunctionName": cloud_function_id,
        "Enabled": True,
        "BatchSize": event.config.get("batch_size"),
    })

    uuid = rv.get("UUID")


    return {"event_type": "queue::trigger", "UUID": uuid}



def _handle_deleting_queue_event(event: simple_lambda.Event, resource_hash) -> bool:
    log.debug(f"Attempting to delete {event} from function {resource_hash}")
    # Go ahead and make sure we have info for this event in the function's output and cloud integration id of this event
    function_event_info = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "events")
    log.debug(f"Function event info {function_event_info}")
    log.debug(event)
    if not event.get_hash() in function_event_info:
        log.error(f"Could not find info for {event} ({event.get_hash()}) in function ({resource_hash}) output")
        return False

    uuid = function_event_info.get(event.get_hash()).get("UUID")

    raw_aws_client.run_client_function("lambda", "delete_event_source_mapping", {
        "UUID": uuid
    })
    log.debug(f"Removed Event {uuid} from {resource_hash}")

    return True


##############################################
##### TOPIC EVENT TRIGGER
##############################################

def _handle_adding_topic_subscription(event: simple_lambda.Event, cloud_function_id) -> Dict:
    log.debug(f"Attempting to create {event} for function {cloud_function_id}")
    topic_resource = cdev_cloud_mapper.get_output_by_name("cdev::simple::topic", event.original_resource_name)
    log.debug(f"Found Table info for {event} -> {topic_resource}")

    # Add permission to lambda to allow apigateway to invoke this function
    stmt_id = f"stmt-{event.original_resource_name}-{event.get_hash()}"
    permission_model_args = {
        "FunctionName": cloud_function_id,
        "Action": "lambda:InvokeFunction",
        "Principal": "sns.amazonaws.com",
        "StatementId": stmt_id,
        "SourceArn": topic_resource.get("arn")
    }

    raw_aws_client.run_client_function("lambda", "add_permission", permission_model_args)

    subscribe_arn = topic_deployer.add_subscriber(topic_resource.get("arn"), "lambda", cloud_function_id)

    return {"UUID": subscribe_arn, "event_type": "topic::trigger", "Stmt_id": stmt_id}

def _handle_deleting_topic_subscription(event: simple_lambda.Event, resource_hash) -> bool:
    log.debug(f"Attempting to delete {event} from function {resource_hash}")
    # Go ahead and make sure we have info for this event in the function's output and cloud integration id of this event
    function_event_info = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "events")
    log.debug(f"Function event info {function_event_info}")
    log.debug(event)
    if not event.get_hash() in function_event_info:
        log.error(f"Could not find info for {event} ({event.get_hash()}) in function ({resource_hash}) output")
        return False



    subscription_arn = function_event_info.get(event.get_hash()).get("UUID")
    stmt_id = function_event_info.get(event.get_hash()).get("Stmt_id")
    cloud_id = cdev_cloud_mapper.get_output_value_by_hash(resource_hash, "cloud_id")

    # Delete the permission on the lambda function
    raw_aws_client.run_client_function("lambda", "remove_permission", {
        "FunctionName": cloud_id,
        "StatementId": stmt_id
    })

    # Remove subscription
    topic_deployer.remove_subscriber(subscription_arn)

    return True



EVENT_TO_HANDLERS = {
    simple_lambda.EventTypes.HTTP_API_ENDPOINT : {
        "CREATE": _handle_adding_api_event,
        "REMOVE": _handle_deleting_api_event
    },
    simple_lambda.EventTypes.TABLE_STREAM : {
        "CREATE": _handle_adding_stream_event,
        "REMOVE": _handle_deleting_stream_event
    },
    simple_lambda.EventTypes.BUCKET_TRIGGER: {
        "CREATE": _handle_adding_bucket_event,
        "REMOVE": _handle_deleting_bucket_event
    },
    simple_lambda.EventTypes.QUEUE_TRIGGER : {
        "CREATE": _handle_adding_queue_event,
        "REMOVE": _handle_deleting_queue_event
    },
    simple_lambda.EventTypes.TOPIC_TRIGGER: {
        "CREATE": _handle_adding_topic_subscription,
        "REMOVE": _handle_deleting_topic_subscription
    }
}
