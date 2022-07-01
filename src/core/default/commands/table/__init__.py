from core.constructs.commands import BaseCommandContainer


class SimpleCommandContainer(BaseCommandContainer):
    help = """
These are the commands that are available for use on the simple table.

put_items: Load data into the table
clear_table: Clear all data from the table
delete_item: Delete item from the table
get_item: Get item from the table
put_item_from_json: Insert data into the table from a json file
delete_item_from_json: Delete data from the table from a json file
"""
