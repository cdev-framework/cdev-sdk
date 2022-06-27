import cmd
import json

from argparse import ArgumentParser
from typing import List, Tuple

import aurora_data_api
from rich.console import Console
from rich.table import Table

from core.constructs.commands import BaseCommand
from core.default.commands.dynamodb.utils import get_dynamodb_info_from_cdev_name

import core.default.mappers.aws_client as aws_client


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
            "--put_item", help="put item command from a json in single quotes"
        )
        parser.add_argument(
            "--delete_item",
            type=str,
            help="delete item command from a json in single quotes",
        )
        parser.add_argument(
            "--get_item", type=str, help="get item command from a json in single quotes"
        )

    def command(self, *args, **kwargs) -> None:

        (
            component_name,
            database_name,
        ) = self.get_component_and_resource_from_qualified_name(kwargs.get("resource"))
        put_item = kwargs.get("put_item")
        delete_item = kwargs.get("delete_item")
        get_item = kwargs.get("get_item")

        cloud_arn, db_name = get_dynamodb_info_from_cdev_name(
            component_name, database_name
        )
        if put_item:
            action_type = "put_item"
            item = json.loads(put_item)
        elif delete_item:
            action_type = "delete_item"
            item = json.loads(delete_item)
        elif get_item:
            action_type = "get_item"
            item = json.loads(get_item)
        else:
            print("A action type needs to be specified")
            return
        put_dynamodb_item(action_type, db_name, item)


def put_dynamodb_item(action_type: str, table_name: str, item: dict):
    aws_client.dynamodb_item_operation(action_type, table_name, item)
