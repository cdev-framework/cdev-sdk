from argparse import ArgumentParser
import json
from typing import Dict, List

import boto3


from cdev.management.base import BaseCommand
from cdev.backend.utils import get_resource
from cdev.backend.cloud_mapper_manager import get_output_value_by_hash
from cdev.mapper.backend.aws import aws_client as raw_aws_client

RUUID = "cdev::simple::table"


class clear_table(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource-name", type=str, help="The resource you want to sync data to"
        )

    def command(self, *args, **kwargs):
        """
        Clear all items for the table
        """
        # https://stackoverflow.com/questions/55169952/delete-all-items-dynamodb-using-python

        resource_name = kwargs.get("resource-name")
        dynamo = boto3.resource("dynamodb")

        try:
            resource = get_resource(resource_name, RUUID)
            dynamodb_table_name = get_output_value_by_hash(resource.hash, "table_name")
        except Exception as e:
            self.stderr.write(f"Could not find simple table {resource_name}")
            return

        table = dynamo.Table(dynamodb_table_name)

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
                    self.stdout.write(f"Removing item {itemKeys}")
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

        self.stdout.write(f"Deleted {counter}")
