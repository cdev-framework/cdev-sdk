from argparse import ArgumentParser
import json
import os

from core.constructs.commands import BaseCommand

from core.default.resources.simple.table import simple_table_model
from core.default.mappers import aws_client
from core.default.commands import utils as command_utils

from . import utils as table_utils


RUUID = "cdev::simple::table"


class put_object(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "resource_name", type=str, help="The resource you want to sync data to"
        )
        parser.add_argument(
            "--file", type=str, help="The location of the json file containing data"
        )
        parser.add_argument(
            "--data", type=str, help="The json data you want to put in the db"
        )

    def command(self, *args, **kwargs) -> None:

        (
            component_name,
            table_resource_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(
            kwargs.get("resource_name")
        )

        cloud_output = command_utils.get_cloud_output_from_cdev_name(
            component_name, RUUID, table_resource_name
        )
        resource: simple_table_model = command_utils.get_resource_from_cdev_name(
            component_name, RUUID, table_resource_name
        )

        table_cloud_name = cloud_output.get("table_name")

        data_string = kwargs.get("data")
        data_file = kwargs.get("file")

        if data_string and data_file:
            raise Exception(f"Can not provide both --data and --file arguments")

        if not (data_string or data_file):
            raise Exception(f"Must provide either --data or --file arguments")

        if data_string:
            try:
                data = json.loads(data_string)

            except Exception as e:
                self.output.print("Data provided was not a valid json string")
                return

        if data_file:
            if not os.path.isfile(data_file):
                raise Exception(f"{data_file} is not a valid data file")

            try:
                with open(data_file) as fp:
                    data = json.load(fp)

            except Exception as e:
                print(e)
                raise e

            if "items" not in data:
                raise Exception(
                    f"Loaded data from {data_file} does not contain the 'items' key"
                )

        attributes_dict = {
            x.get("attribute_name"): x.get("attribute_type")
            for x in resource.attributes
        }

        for datum in data.get("items"):
            is_data_valid, msg = table_utils.validate_data(
                datum, attributes_dict, resource.keys
            )

            if not is_data_valid:
                self.output.print(msg)
                return

        try:

            translated_data = [
                table_utils.recursive_translate_data(x) for x in data.get("items")
            ]
        except:
            self.output.print("Could not translate data to dynamodb put item form")

        try:
            for datum in translated_data:
                aws_client.run_client_function(
                    "dynamodb",
                    "put_item",
                    {"TableName": table_cloud_name, "Item": datum},
                )

                self.output.print(f"Wrote {datum} to {table_resource_name}")
        except Exception as e:
            self.output.print(f"Could not write data to table {table_resource_name}")
            return
