# Generated as part of Quick Start project template
from twilio.twiml.messaging_response import MessagingResponse

from cdev.resources.simple.xlambda import simple_function_annotation

from .api import twilio_webhook_route


@simple_function_annotation(
    "twilio_handler", events=[twilio_webhook_route.event("application/xml")]
)
def twilio_handler(event, context):
    print(f"full event -> {event}")
    print(f"event body -> {event.get('body')}")

    response = MessagingResponse()
    response.message("Hi from your backend!")

    return response.to_xml()
