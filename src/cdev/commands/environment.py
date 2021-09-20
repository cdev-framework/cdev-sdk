from ..utils.logger import get_cdev_logger
from ..utils import environment as cdev_environment
from .. import output as cdev_output



log = get_cdev_logger(__name__)


def environment(command, args):
    parsed_args = vars(args)
    
    if command == '':
        cdev_output.print("You must provide a sub-command. run `cdev environment --help` for more information on available subcommands")
    elif command == 'ls':
        current_env = cdev_environment.get_current_environment()

        for env in cdev_environment.get_environment_info_object().environments:
            if env.name == current_env:
                cdev_output.print(f"> {env.name}")
            else:
                cdev_output.print(env.name)
    elif command == 'get':
        cdev_output.print(cdev_environment.get_environment_info(parsed_args.get("env")))
    elif command == 'set':
        cdev_environment.set_current_environment(parsed_args.get("env"))
    elif command == 'create':
        cdev_environment.create_environment(parsed_args.get("env"))
