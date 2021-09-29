


from argparse import ArgumentParser
import json
from typing import Dict, List


from cdev.management.base import BaseCommand
from cdev.backend.utils import get_resource
from cdev.backend.cloud_mapper_manager import get_output_value_by_hash
from cdev.mapper.backend.aws import aws_client as raw_aws_client

RUUID = "cdev::simple::table"

class put_object(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("resource-name", type=str, help="The resource you want to sync data to")
        parser.add_argument("data", type=str, help="The json data you want to put in the db")
        

    def command(self, *args, **kwargs):
        pass