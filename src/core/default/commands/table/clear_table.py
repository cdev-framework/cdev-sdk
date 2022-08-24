import boto3

from argparse import ArgumentParser

from core.constructs.commands import BaseCommand
from core.default.commands import utils as command_utils


RUUID = "cdev::simple::table"


class clear_table(BaseCommand):

    help = """
Clear the current data from a given Table. This should only be used on development tables.
"""

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "resource_name", type=str, help="The resource you want to sync data to"
        )

    def command(self, *args, **kwargs) -> None:
        """
        Clear all items for the table
        """
        # https://stackoverflow.com/questions/55169952/delete-all-items-dynamodb-using-python

        (
            component_name,
            table_resource_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(
            kwargs.get("resource_name")
        )

        cloud_output = command_utils.get_cloud_output_from_cdev_name(
            component_name, RUUID, table_resource_name
        )
        table_cloud_name = cloud_output.get("table_name")

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
                    self.output.print(f"Removing item {itemKeys}")
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

        self.output.print(f"Deleted {counter}")
