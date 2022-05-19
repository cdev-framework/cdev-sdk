# Generated as part of the Slack Events project template
import json
import os

from slack_sdk import signature
from slack_sdk import WebClient

from cdev.resources.simple.api import Api, route_verb
from cdev.resources.simple.xlambda import simple_function_annotation

from cdev import Project as cdev_project

from ..project_settings import SlackBotSettings

myProject = cdev_project.instance()

mySettings: SlackBotSettings = myProject.settings

DemoApi = Api("demoapi")

webhook_route = DemoApi.route("/webhook", route_verb.POST)


env_vars = {
    "SLACK_SECRET": mySettings.SLACK_SECRET,
    "SLACK_BOT_OAUTH_TOKEN": mySettings.SLACK_BOT_OAUTH_TOKEN,
}


signature_verifier = signature.SignatureVerifier(
    signing_secret=os.environ.get("SLACK_SECRET")
)
client = WebClient(token=os.environ.get("SLACK_BOT_OAUTH_TOKEN"))


@simple_function_annotation(
    "webhook", events=[webhook_route.event()], environment=env_vars
)
def webhook(event, context):
    # Load the info to validate the request
    body = event.get("body")
    timestamp = event.get("headers").get("x-slack-request-timestamp")
    slack_signature = event.get("headers").get("x-slack-signature")

    is_valid = signature_verifier.is_valid(body, timestamp, slack_signature)

    if not is_valid:
        # Not a valid request from our Slack App so return 401
        return {
            "status_code": 401,
        }

    data = json.loads(event.get("body"))
    print(data)

    if data.get("type") == "url_verification":
        return {"status_code": 200, "message": {"challenge": data.get("challenge")}}

    response_channel = data.get("event").get("channel")

    client.chat_meMessage(
        channel=response_channel,
        text="Hello from your app! :tada:",
    )

    return {
        "status_code": 200,
    }


myProject.display_output("Base API URL", DemoApi.output.endpoint)
myProject.display_output("Routes", DemoApi.output.endpoints)
