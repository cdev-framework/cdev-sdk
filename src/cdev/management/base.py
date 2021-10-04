
import os
from argparse import ArgumentParser, HelpFormatter
import sys
from io import TextIOBase

class CdevCommandError(BaseException):
    """
    This is directly from Django, but I have to rename it for consistency sake since end users will have to raise it. Thank you Django. 

    Exception class indicating a problem while executing a management
    command.
    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.
    """
    def __init__(self, *args, returncode=1, **kwargs):
        self.returncode = returncode
        super().__init__(*args, **kwargs)


class DjangoHelpFormatter(HelpFormatter):
    """
    This is just a nice feature of the formatter. Thank you Django.

    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all commands.
    """
    show_last = {
        '--version', '--verbosity', '--traceback', '--settings', '--pythonpath',
        '--no-color', '--force-color', '--skip-checks',
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions,
            key=lambda a: set(a.option_strings) & self.show_last != set()
        )

    def add_usage(self, usage, actions, *args, **kwargs):
        super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

    def add_arguments(self, actions):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    """
    Wrapper around stdout/stderr
    """
    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, ending='\n'):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def flush(self):
        if hasattr(self._out, 'flush'):
            self._out.flush()

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg='', style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class BaseCommand():
    """
    This command system is heavily influenced/inspired by the Django command system (https://github.com/django/django/blob/b0ed619303d2fb723330ca9efa3acf23d49f1d19/django/core/management/base.py).

    Steps:
    - A command is called with `cdev run <subcommand args>
    - Manage searches the project for the command.. TODO add more detail
    - When the command is found, we build it's arg parser
    - Then the command is run via the `run_command` 

    Note that `run_command` and `command` can both throw `CdevCommandError` and that should be caught in `run_from_command_line` and delegate the output through cdev_output.

    """

    # Help message for this command
    help = ""

    # If this command requires the project to have been initialized
    requires_initialized_project = True

    # If the command should look to substitute args with cloud output values
    substitute_from_output = True

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)


    def create_arg_parser(self, prog_name, subcommand, **kwargs) -> ArgumentParser:
        parser = ArgumentParser(
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
            formatter_class=DjangoHelpFormatter,
            **kwargs
        )

        self.add_arguments(parser)

        return parser


    def add_arguments(self, parser: ArgumentParser):
        """
        Must be overridden by the subclasses
        """
        pass


    def run_from_command_line(self, argv):
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
        args = cmd_options.pop('args', ())

        try:
            self.run_command(*args, **cmd_options)
        except CdevCommandError as e:
            self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(e.returncode)


    def run_command(self, *args, **kwargs):
        """
        Actually runs the command and sets up correct output and scaffolding. Also does any project checks. This should be the entry point to all commands not the actual `command` function.
        
        **This method should not be overridden**
        """
        #TODO init project

        output = self.command(*args, **kwargs)

        if output:
            self.stdout.write(output)

        return output
    

    def command(self, *args, **kwargs):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError('subclasses of BaseCommand must provide a command() method')



class BaseCommandContainer():
    """
    This is used to designate that the directory is a CommandContainer and should be searched for when looking for commands.

    This class should be initialized in the __init__.py file for the folder.

    The directory should contain valid Commands or other CommandContainers
    """

    # Help message for this container
    help = ""

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)


    def display_help_message(self) -> str:
        self.stdout.write(self.help)
