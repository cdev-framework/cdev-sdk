"""Structures for user defined command system

One of the goals of the Core Framework is to provide flexibility such that end users can easily
create custom functionality for their projects. One way of providing this flexibility, is to provide
an easy interface for executing code from within the context of the framework from the CLI. This
process is heavily modeled and inspired by the `Django Command Framework`
(https://github.com/django/django/blob/b0ed619303d2fb723330ca9efa3acf23d49f1d19/django/core/management/base.py).

The main primitive is the `BaseCommand` class. By deriving from this class, developers can create code
that is easily accessible and discoverable from the command line. To see how these class are discovered
and execute see our more in depth documentation on the command system at <link>

"""
from argparse import ArgumentParser

from core.constructs.output_manager import OutputManager


class BaseCommand:
    """Base Class for a user defined command"""

    # Help message for this command
    help = ""

    def __init__(
        self,
        output: OutputManager,
    ) -> None:
        self.output = output

    def create_arg_parser(self, prog_name, subcommand, **kwargs) -> ArgumentParser:
        parser = ArgumentParser(
            prog=f"{prog_name} {subcommand}", description=self.help or None, **kwargs
        )

        self.add_arguments(parser)

        return parser

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add the cli arguments for the command"""
        pass

    def run_from_command_line(self, argv) -> None:
        """
        Handles input from command line and builds arg parser and uses it to validate input.

        argv -> [program_name, command, *args]

        program_name: represents where to find the command
        command: command to run
        *args: args for the command
        """
        parser = self.create_arg_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])

        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())

        self.command(*args, **cmd_options)

    def command(self, *args, **kwargs) -> None:
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError(
            "subclasses of BaseCommand must provide a command() method"
        )


class BaseCommandContainer:
    """
    This is used to designate that the directory is a CommandContainer and should be searched for when looking for commands.

    This class should be initialized in the __init__.py file for the folder.

    The directory should contain valid Commands or other CommandContainers
    """

    # Help message for this container
    help = ""

    def __init__(self, output: OutputManager) -> None:
        self.output = output

    def display_help_message(self) -> None:
        self.output.print(self.help)
