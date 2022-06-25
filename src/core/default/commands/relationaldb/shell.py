import cmd
import readline
import os

from argparse import ArgumentParser
from core.constructs.workspace import Workspace
from typing import List, Tuple

import aurora_data_api
from rich.console import Console
from rich.table import Table

from core.constructs.commands import BaseCommand
from core.default.commands.relationaldb.utils import get_db_info_from_cdev_name
from core.default.commands import utils as command_utils


class shell(BaseCommand):
    help = """
        Open an interactive shell to a relational db.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "resource",
            type=str,
            help="The database to execute on. Name must include component name. ex: comp1.myDb",
        )
        parser.add_argument(
            "-c", "--command", nargs="+", type=str, help="sql command to execute"
        )
        parser.add_argument(
            "-f", "--file", nargs="+", help="execute sql commands from a file"
        )

    def command(self, *args, **kwargs) -> None:
        (
            component_name,
            database_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(
            kwargs.get("resource")
        )

        c_command = kwargs.get("command")
        f_command = kwargs.get("file")
        cluster_arn, secret_arn, db_name = get_db_info_from_cdev_name(
            component_name, database_name
        )
        if c_command is not None:
            self.run_sql_command(c_command[0], cluster_arn, secret_arn, db_name)
        elif f_command is not None:
            try:
                fd = open(f_command[0], "r")
            except Exception as e:
                raise e
            sql_file = fd.read()
            fd.close()
            sql_commands = sql_file.split(";")
            self.run_multiple_sql_commands(
                sql_commands, cluster_arn, secret_arn, db_name
            )
        else:
            history_location = os.path.join(
                Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION, "dbshell"
            )
            if not os.path.isfile(history_location):
                # touch the file
                with open(history_location, "a"):
                    pass
            interactive_shell(
                fmt(Console()), cluster_arn, secret_arn, db_name, history_location
            ).cmdloop()

    def run_sql_command(
        self, query_string: str, cluster_arn: str, secret_arn: str, db_name: str
    ):
        connection = db_connection(cluster_arn, secret_arn, db_name)
        col_descriptions, rows, updated_row_cnt = connection.execute(query_string)
        fmt(Console()).print_results(col_descriptions, rows, updated_row_cnt)

    def run_multiple_sql_commands(
        self, query_list: List, cluster_arn: str, secret_arn: str, db_name: str
    ):
        connection = db_connection(cluster_arn, secret_arn, db_name)
        connection.begin()
        for query in query_list:
            if query != "":
                self.output.print(query)
                try:
                    col_descriptions, rows, updated_row_cnt = connection.execute(query)
                except Exception as e:
                    self.output.print("FAIL")
                    connection.rollback()
                    raise e
                fmt(Console()).print_results(col_descriptions, rows, updated_row_cnt)
        connection.commit()


class db_connection:
    def __init__(self, cluster_arn: str, secret_arn: str, database_name: str) -> None:
        self.conn = aurora_data_api.connect(
            aurora_cluster_arn=cluster_arn,
            secret_arn=secret_arn,
            database=database_name,
        )
        self._db_name = database_name
        self._cluster_arn = cluster_arn
        self._secret_arn = secret_arn

    def execute(self, line: str) -> Tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(line)

            return (
                cursor.description,
                cursor.fetchall(),
                cursor._current_response.get("numberOfRecordsUpdated"),
            )

    def begin(self) -> None:
        res = self.conn._client.begin_transaction(
            database=self._db_name,
            resourceArn=self._cluster_arn,
            secretArn=self._secret_arn,
        )

        self.conn._transaction_id = res["transactionId"]

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()


class fmt:
    def __init__(self, console: Console) -> None:
        self._console = console

    def print_results(
        self, column_descriptions: List, rows: List, updated_rows: int
    ) -> None:
        if rows:
            display = Table()

            headers = [f"{x[0]} ({x[1].__name__})" for x in column_descriptions]

            data = [[str(y) for y in x] for x in rows]

            [display.add_column(header=x) for x in headers]
            [display.add_row(*x) for x in data]

            self._console.print(display)

        if updated_rows:
            self._console.print(f"UPDATED {updated_rows} ROWS")


class interactive_shell(cmd.Cmd):
    def __init__(
        self,
        fmt: fmt,
        cluster_arn: str,
        secret_arn: str,
        database_name: str,
        history_location: str,
    ) -> None:
        super().__init__()
        self.histfile = history_location
        readline.read_history_file(self.histfile)
        self.prompt = f"{database_name}=> "
        self._db_connection = db_connection(cluster_arn, secret_arn, database_name)
        self.formater = fmt

    def default(self, line) -> None:
        try:
            readline.add_history(line)
            readline.insert_text(readline.get_line_buffer())
            readline.write_history_file(self.histfile)
            col_descriptions, rows, updated_row_cnt = self._db_connection.execute(line)
            self.formater.print_results(col_descriptions, rows, updated_row_cnt)
        except Exception as e:
            self.formater._console.print(e)

    def do_quit(self, arg) -> bool:
        return True

    def do_BEGIN(self, args) -> None:
        self._db_connection.begin()
        self.formater._console.print("BEGIN TRANSACTION")

    def do_COMMIT(self, args) -> None:
        self._db_connection.commit()
        self.formater._console.print("COMMIT")

    def do_ROLLBACK(self, args) -> None:
        self._db_connection.rollback()
        self.formater._console.print("ROLLBACK")
