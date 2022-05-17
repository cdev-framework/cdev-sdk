from cdev.resources.simple.iam import PermissionArn, Permission

powertool_vars = {
    "LOG_LEVEL": "INFO",
    "POWERTOOLS_SERVICE_NAME": "example",
    "POWERTOOLS_METRICS_NAMESPACE": "PowertoolsDemo",
}

# https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html#services-xray-permissions
tracer_permissions = PermissionArn("arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess")
