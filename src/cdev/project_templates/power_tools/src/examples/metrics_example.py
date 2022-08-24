from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

from cdev.resources.simple.xlambda import simple_function_annotation

from src.examples.config import powertool_vars

metrics = Metrics(namespace="ExampleApplication", service="booking")


@simple_function_annotation("metrics_example", environment=powertool_vars, tags={"environment": "dev", "sample_tag": "metrics"})
@metrics.log_metrics
def lambda_handler(evt, ctx):
    metrics.add_metric(name="SuccessfulBooking", unit=MetricUnit.Count, value=123)
