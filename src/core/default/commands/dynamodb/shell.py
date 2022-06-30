import cmd
import json
import csv
from io import StringIO
from argparse import ArgumentParser
from typing import List, Tuple

import aurora_data_api
from rich.console import Console
from rich.table import Table

from core.constructs.commands import BaseCommand
from core.default.commands.dynamodb.utils import get_dynamodb_info_from_cdev_name

import core.default.mappers.aws_client as aws_client
import boto3
import json


class shell(BaseCommand):
    help = """
        Open an interactive shell to a non-relational db.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "resource",
            type=str,
            help="The database to execute on. Name must include component name. ex: comp1.myDb",
        )
        parser.add_argument(
            "--put_item",
            help="put item command, format: field:field_name , field_type: string or int , value: "
            "value_field; field:field2_name, field_type: string, value:value_field2 (...)",
        )
        parser.add_argument(
            "--delete_item",
            type=str,
            help="delete item command, format: field:field_name , field_type: string or int , value: "
            "value_field; field:field2_name, field_type: string, value:value_field2 (...)",
        )
        parser.add_argument(
            "--get_item",
            type=str,
            help="get item command, format: field:field_name , field_type: "
            "string or int , value: "
            "value_field; field:field2_name, field_type: string, value:value_field2 (...)",
        )
        parser.add_argument(
            "--put_item_from_json",
            type=str,
            help="put item command from a json file in single quotes",
        )
        parser.add_argument(
            "--delete_item_from_json",
            type=str,
            help="delete item command from a json file in single quotes",
        )

    def command(self, *args, **kwargs) -> None:
        (
            component_name,
            database_name,
        ) = self.get_component_and_resource_from_qualified_name(kwargs.get("resource"))
        put_item = kwargs.get("put_item")
        delete_item = kwargs.get("delete_item")
        get_item = kwargs.get("get_item")
        put_item_from_json = kwargs.get("put_item_from_json")
        delete_item_from_json = kwargs.get("delete_item_from_json")
        if put_item:
            action_type = "put_item"
            dict_fields = create_dict_from_string(put_item)
        elif delete_item:
            action_type = "delete_item"
            dict_fields = create_dict_from_string(delete_item)
        elif get_item:
            action_type = "get_item"
            dict_fields = create_dict_from_string(get_item)
        elif put_item_from_json:
            action_type = "put_item"
            dict_fields = import_json(put_item_from_json)
        elif delete_item_from_json:
            action_type = "delete_item"
            dict_fields = import_json(delete_item_from_json)
        else:
            print("A action type needs to be specified")
            return
        cloud_arn, db_name = get_dynamodb_info_from_cdev_name(
            component_name, database_name
        )
        put_dynamodb_item(action_type, db_name, dict_fields)


def import_json(file_path: str) -> dict:
    with open(file_path) as file:
        dict_fields = json.load(file)
    return dict_fields


def create_dict_from_string(str_text: str) -> dict:
    str_text = str_text.split(";")
    dict_fields = {}
    for item in str_text:
        str_text2 = item.split(",")
        cont_itens = 0
        for item2 in str_text2:
            if "field:" in item2:
                field = item2[item2.find("field:") + len("field:") : len(item2)]
                cont_itens += 1
            if "field_type:" in item2:
                type_field = item2[
                    item2.find("field_type:") + len("field_type:") : len(item2)
                ]
                if type_field.replace(" ", "") == "string":
                    type_field = "S"
                elif type_field.replace(" ", "") == "int":
                    type_field = "I"
                cont_itens += 1
            if "value:" in item2:
                value_add = item2[item2.find("value:") + len("value:") : len(item2)]
                cont_itens += 1
        if cont_itens != 3:
            print(
                "An undefined parameter was found inside the "
                + str(item2)
                + " elements"
            )
        dict_fields[field.replace(" ", "")] = {type_field: value_add}
    return dict_fields


def put_dynamodb_item(operation_type: str, table_name: str, item: dict) -> None:
    rendered_client = boto3.client("dynamodb")
    try:
        if operation_type == "put_item":
            rendered_client.put_item(TableName=table_name, Item=item)
        elif operation_type == "delete_item":
            rendered_client.delete_item(TableName=table_name, Key=item)
        elif operation_type == "get_item":
            res = rendered_client.get_item(TableName=table_name, Key=item)
            print(res)
        else:
            res = "Invalid operation type"
            print(res)
    except Exception as e:
        raise e
