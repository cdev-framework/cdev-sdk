from argparse import ArgumentParser
import json
import os
from tempfile import TemporaryFile
from typing import Dict, List

from core.constructs.commands import BaseCommand, OutputWrapper
from core.default.resources.simple.table import Table, simple_table_model
from core.utils.paths import get_full_path_from_workspace_base

from core.default.mappers import aws_client


from . import utils 


RUUID = "cdev::simple::table"


class put_object(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource_name", type=str, help="The resource you want to sync data to"
        )
        parser.add_argument(
            "--file", type=str, help="The location of the json file containing data"
        )
        parser.add_argument(
            "--data", type=str, help="The json data you want to put in the db"
        )

    def command(self, *args, **kwargs):
        full_resource_name = kwargs.get("resource_name")
        component_name = full_resource_name.split('.')[0]
        table_resource_name = full_resource_name.split('.')[1]

        cloud_output = utils.get_cloud_output_from_cdev_name(component_name, table_resource_name)
        resource: simple_table_model = utils.get_resource_from_cdev_name(component_name, table_resource_name)

        table_cloud_name = cloud_output.get('table_name')

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
                self.stderr.write("Data provided was not a valid json string")
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


            if not 'items' in data:
                raise Exception(f"Loaded data from {data_file} does not contain the 'items' key")


        attributes_dict = {
            x.get("attribute_name"): x.get("attribute_type") for x in resource.attributes
        }


        for datum in data.get('items'):
            is_data_valid, msg = utils.validate_data(datum, attributes_dict, resource.keys)

            if not is_data_valid:
                self.stderr.write(msg)
                return

        try:
            
            translated_data = [utils.recursive_translate_data(x) for x in data.get('items')]
        except:
            self.stderr.write("Could not translate data to dynamodb put item form")

        try:
            for datum in translated_data:
                aws_client.run_client_function(
                    "dynamodb",
                    "put_item",
                    {
                        "TableName": table_cloud_name, 
                        "Item": datum
                    },
                )

                self.stdout.write(f"Wrote {datum} to {table_resource_name}")
        except Exception as e:
            self.stderr.write(f"Could not write data to table {table_resource_name}")
            return

        
