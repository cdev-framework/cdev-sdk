from cdev.management.base import BaseCommand
from argparse import ArgumentParser

from boto3 import client

class put_object(BaseCommand):

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("function_name", type=str, help= "The function that you want to watch")

    def command(self, *args, **kwargs):
        function_name = args[0]

