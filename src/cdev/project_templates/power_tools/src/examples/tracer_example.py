from aws_lambda_powertools import Tracer

from cdev.resources.simple.xlambda import simple_function_annotation

from src.examples.config import powertool_vars, tracer_permissions


tracer = Tracer()  # Sets service via env var


def collect_payment(charge_id: str):
    print(f"Collected charge: {charge_id}")


@simple_function_annotation(
    "tracer_example", environment=powertool_vars, permissions=[tracer_permissions]
)
@tracer.capture_lambda_handler
def handler(event, context):
    charge_id = event.get("charge_id")
    payment = collect_payment(charge_id)
