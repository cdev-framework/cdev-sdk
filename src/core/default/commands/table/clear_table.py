from argparse import ArgumentParser
from typing import Dict, List

import boto3


from core.constructs.commands import BaseCommand, OutputWrapper
from core.default.resources.simple.table import Table
from core.utils.paths import get_full_path_from_workspace_base


from . import utils

RUUID = "cdev::simple::table"


class clear_table(BaseCommand):

    help = """
Clear the current data from a given Table. This should only be used on development tables.   
"""

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource_name", type=str, help="The resource you want to sync data to"
        )

    def command(self, *args, **kwargs):
        """
        Clear all items for the table
        """
        # https://stackoverflow.com/questions/55169952/delete-all-items-dynamodb-using-python

        full_resource_name = kwargs.get("resource_name")
        component_name = full_resource_name.split('.')[0]
        table_resource_name = full_resource_name.split('.')[1]

        cloud_output = utils.get_cloud_output_from_cdev_name(component_name, table_resource_name)
        table_cloud_name = cloud_output.get('table_name')

        dynamo = boto3.resource("dynamodb")
        table = dynamo.Table(table_cloud_name)

        # get the table keys
        tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

        # Only retrieve the keys for each item in the table (minimize data transfer)
        projectionExpression = ", ".join("#" + key for key in tableKeyNames)
        expressionAttrNames = {"#" + key: key for key in tableKeyNames}

        counter = 0
        page = table.scan(
            ProjectionExpression=projectionExpression,
            ExpressionAttributeNames=expressionAttrNames,
        )
        with table.batch_writer() as batch:
            while page["Count"] > 0:
                counter += page["Count"]
                # Delete items in batches
                for itemKeys in page["Items"]:
                    self.stderr.write(f"Removing item {itemKeys}")
                    batch.delete_item(Key=itemKeys)
                # Fetch the next page
                if "LastEvaluatedKey" in page:
                    page = table.scan(
                        ProjectionExpression=projectionExpression,
                        ExpressionAttributeNames=expressionAttrNames,
                        ExclusiveStartKey=page["LastEvaluatedKey"],
                    )
                else:
                    break

        self.stderr.write(f"Deleted {counter}")
