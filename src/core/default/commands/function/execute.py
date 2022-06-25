import json
import os

from argparse import ArgumentParser
from typing import Dict
from boto3 import client

from core.constructs.commands import BaseCommand
from core.default.commands import utils as command_utils

RUUID = "cdev::simple::function"


class execute(BaseCommand):

    help = """
        Execute a function in the cloud.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "function_id", type=str, help="The id of the function to execute."
        )
        parser.add_argument(
            "--event",
            type=str,
            help="File (json) location of event object to provide as input to the function. Can not be used with '--event-data` flag.",
        )
        parser.add_argument(
            "--event-data",
            type=str,
            help="Raw string form of event object to provide as input to the function. Can not be used with '--event' flag.",
        )

    def command(self, *args, **kwargs) -> None:

        event_data = self._get_event_data(*args, **kwargs)

        full_function_name = kwargs.get("function_id")
        (
            component_name,
            function_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(
            full_function_name
        )

        cloud_name = command_utils.get_cloud_output_from_cdev_name(
            component_name, RUUID, function_name
        ).get("cloud_id")

        lambda_client = client("lambda")

        self.output.print(f"executing {full_function_name}")
        response = lambda_client.invoke(
            FunctionName=cloud_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(event_data),
        )

        self.output.print(str(response))

    def _get_event_data(self, *args, **kwargs) -> Dict:
        event_file_location: str = kwargs.get("event")
        event_raw_data: str = kwargs.get("event_data")

        if event_file_location and event_raw_data:
            raise Exception("Can not provide both '--event-data' and '--event'")

        if event_file_location:
            if not os.path.isfile(event_file_location):
                raise Exception(f"{event_file_location} is not a valid file location")

            with open(event_file_location) as fh:
                try:
                    event_data = json.load(fh)
                    return event_data
                except Exception as e:
                    print(e)
                    raise Exception(f"Could not load {event_file_location} as json")

        if event_raw_data:
            try:
                event_data = json.loads(event_raw_data)
                return event_data
            except Exception as e:
                print(e)
                raise Exception(f"Could not load {event_raw_data} as json")
        return {}
