
from argparse import ArgumentParser
import cmd
from typing import List

import aurora_data_api
from boto3 import client
from rich.console import Console
from rich.table import Table

from core.constructs.commands import BaseCommand
from core.default.commands.relationaldb.utils import get_db_info_from_cdev_name


class shell(BaseCommand):

    help = """
        Open an interactive shell to a relational db.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource", type=str, help="The database to execute on. Name must include component name. ex: comp1.myDb"
        )
      

    def command(self, *args, **kwargs):

        full_database_name: str = kwargs.get("resource")
        component_name = full_database_name.split('.')[0]
        database_name = full_database_name.split('.')[1]

        cluster_arn, secret_arn, db_name = get_db_info_from_cdev_name(component_name, database_name)

        interactive_shell(fmt(Console()), cluster_arn, secret_arn, db_name).cmdloop()



class db_connection():
    def __init__(self, cluster_arn: str, secret_arn: str, database_name: str):
        self.conn = aurora_data_api.connect(aurora_cluster_arn=cluster_arn, secret_arn=secret_arn, database=database_name)
        self._db_name = database_name
        self._cluster_arn = cluster_arn
        self._secret_arn = secret_arn

    def execute(self, line: str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(line)
                
                return (cursor.description, cursor.fetchall(), cursor._current_response.get('numberOfRecordsUpdated'))

        except Exception as e:
            raise e


    def begin(self):
        try:
            res = self.conn._client.begin_transaction(
                database=self._db_name,
                resourceArn=self._cluster_arn,
                secretArn=self._secret_arn
            )
            
            self.conn._transaction_id = res["transactionId"]
            
        except Exception as e:
            raise e


    def commit(self):
        try:
            
            self.conn.commit()

        except Exception as e:
            raise e


    def rollback(self):
        try:
            self.conn.rollback()

        except Exception as e:
            raise e


class fmt():
    def __init__(self, console: Console) -> None:
        self._console = console


    def print_results(self, column_descriptions: List, rows: List, updated_rows: int):
        if rows:
            display =  Table()

            headers = [f"{x[0]} ({x[1].__name__})"  for x in column_descriptions]
            
            data = [[str(y) for y in x] for x in rows]

            [display.add_column(header=x) for x in headers]
            [display.add_row(*x) for x in data]

            self._console.print(display)


        if updated_rows:
            self._console.print(f"UPDATED {updated_rows} ROWS")


class interactive_shell(cmd.Cmd):

    def __init__(self, fmt: fmt, cluster_arn: str, secret_arn: str, database_name: str):
        super().__init__()
        self.prompt = f"{database_name}=> "
        self._db_connection = db_connection(cluster_arn, secret_arn, database_name)
        self.formater = fmt


    def default(self, line):
        try:
            col_descriptions, rows, updated_row_cnt = self._db_connection.execute(line)
            self.formater.print_results(col_descriptions, rows, updated_row_cnt)
        except Exception as e:
            self.formater._console.print(e)

    def do_quit(self, arg):
        return True
    
    def do_BEGIN(self, args):
        self._db_connection.begin()
        self.formater._console.print("BEGIN TRANSACTION")

    def do_COMMIT(self, args):
        self._db_connection.commit()
        self.formater._console.print("COMMIT")

    def do_ROLLBACK(self, args):
        self._db_connection.rollback()
        self.formater._console.print("ROLLBACK")



