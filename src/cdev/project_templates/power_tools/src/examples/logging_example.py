from aws_lambda_powertools import Logger

from cdev.resources.simple.xlambda import simple_function_annotation

from src.examples.config import powertool_vars

logger = Logger(service="payment")


@simple_function_annotation("logger_example", environment=powertool_vars, tags={"environment": "dev", "sample_tag": "power"})
@logger.inject_lambda_context
def handler(event, context):
    logger.info("Collecting payment")

    logger.info({"operation": "collect_payment", "charge_id": event["charge_id"]})
