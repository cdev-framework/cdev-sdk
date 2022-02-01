
from argparse import ArgumentParser

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
            "function_name", type=str, help="The function that you want to watch. Name must include component name. ex: comp1.demo_function"
        )
        parser.add_argument(
            "--event",
            action="store_true",
            help="watch the logs. If this flag is passed, only --start_time flag is read",
        )
        parser.add_argument(
            "--context", action="store_true", help="show the tail of the logs"
        )
       

    def command(self, *args, **kwargs):

        full_function_name: str = kwargs.get("function_name")
        component_name = full_function_name.split('.')[0]
        function_name = full_function_name.split('.')[1]

        cloud_name = get_cloud_id_from_cdev_name(component_name, function_name)

        lambda_client = client('lambda')    

        self.stdout.write(f'executing {full_function_name}')
        response = lambda_client.invoke(
            FunctionName=cloud_name,
            InvocationType='RequestResponse',
        )


        print(response)