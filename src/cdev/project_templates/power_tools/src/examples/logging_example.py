from aws_lambda_powertools import Logger

from cdev.aws.lambda_function import ServerlessFunction

from src.examples.config import powertool_vars

logger = Logger(service="payment")


@ServerlessFunction(
    "logger_example",
    environment=powertool_vars,
    tags={"environment": "dev", "sample_tag": "power"},
)
@logger.inject_lambda_context
def handler(event, context):
    logger.info("Collecting payment")

    logger.info({"operation": "collect_payment", "charge_id": event["charge_id"]})
