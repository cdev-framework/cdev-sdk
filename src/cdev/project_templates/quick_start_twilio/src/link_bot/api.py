from cdev.resources.simple.api import Api
from cdev import Project as cdev_project


myProject = cdev_project.instance()

webhooks_api = Api("demoapi")
twilio_webhook_route = webhooks_api.route("/twilio_handler", "POST")

myProject.display_output("Base API URL", webhooks_api.output.endpoint)
