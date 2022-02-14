
from argparse import ArgumentParser
import json
import os
from typing import List, Dict

from boto3 import client

from core.constructs.commands import BaseCommand, OutputWrapper
from core.constructs.workspace import Workspace
from core.utils import hasher



from core.default.commands.function.utils import get_cloud_id_from_cdev_name

RUUID = "cdev::simple::function"


class execute(BaseCommand):

    help = """
        Execute a function in the cloud.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "function_id", 
            type=str, 
            help="The id of the function to execute."
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
        
       

    def command(self, *args, **kwargs):

        full_function_name: str = kwargs.get("function_id")

        event_file_location: str = kwargs.get("event")
        event_raw_data: str = kwargs.get("event_data")

        if event_file_location and event_raw_data:
            raise Exception("Can not provide both '--event-data' and '--event'")

        event_data = {}

        if event_file_location:
            if not os.path.isfile(event_file_location):
                raise Exception(f"{event_file_location} is not a valid file location")

            with open(event_file_location) as fh:
                try:
                    event_data = json.load(fh)
                except Exception as e:
                    print(e)
                    raise Exception(f'Could not load {event_file_location} as json')

                
        if event_raw_data:
            try:
                event_data = json.loads(event_raw_data)
            except Exception as e:
                print(e)
                raise Exception(f'Could not load {event_raw_data} as json')


        component_name = full_function_name.split('.')[0]
        function_name = full_function_name.split('.')[1]

        cloud_name = get_cloud_id_from_cdev_name(component_name, function_name)

        lambda_client = client('lambda')    

        self.stdout.write(f'executing {full_function_name}')
        response = lambda_client.invoke(
            FunctionName=cloud_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(event_data)
        )


        print(response)