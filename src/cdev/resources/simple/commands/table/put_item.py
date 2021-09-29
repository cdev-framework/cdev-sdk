from argparse import ArgumentParser
import json
from typing import Dict, List


from cdev.management.base import BaseCommand
from cdev.backend.utils import get_resource
from cdev.backend.cloud_mapper_manager import get_output_value_by_hash
from cdev.mapper.backend.aws import aws_client as raw_aws_client

from cdev.resources.simple.commands.table.utils import _validate_data, recursive_translate_data

RUUID = "cdev::simple::table"

class put_object(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("resource-name", type=str, help="The resource you want to sync data to")
        parser.add_argument("data", type=str, help="The json data you want to put in the db")
        

    def command(self, *args, **kwargs):
        resource_name = kwargs.get("resource-name")
        data_string = kwargs.get("data")

        try:
            data = json.loads(data_string)
        except Exception as e:
            self.stderr.write("Data provided was not a valid json string")
            return

        try:
            resource = get_resource(resource_name, RUUID)
            dynamodb_table_name = get_output_value_by_hash(resource.hash, "table_name")
        except Exception as e:
            self.stderr.write(f"Could not find simple table {resource_name}")        
            return

        attributes_dict = {x.get("AttributeName"): x.get("AttributeType") for x in resource.attributes}

        is_data_valid, msg = _validate_data(data, attributes_dict, resource.keys)

        if not is_data_valid:
            self.stderr.write(msg)
            return

        try:
            translated_data = recursive_translate_data(data)
        except:
            self.stderr.write("Could not translate data to dynamodb put item form")

        try:
            raw_aws_client.run_client_function("dynamodb", "put_item", {
                "TableName": dynamodb_table_name,
                "Item": translated_data
            })
        except Exception as e:
            self.stderr.write(f"Could not write data to table {resource_name}")
            return

        self.stdout.write(f"Wrote {data} to {resource_name}")
        






