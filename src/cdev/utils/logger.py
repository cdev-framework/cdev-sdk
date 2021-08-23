import logging.config
import os

from ..settings import SETTINGS as cdev_settings


#logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "..","logging.ini"), disable_existing_loggers=False)
#logger = logging.getLogger("frontend")


class cdev_logger:
    """
    This is a wrapper around pythons basic logger object to provide a layer of indirection for logging. Specifically, this will add some formatting with `rich`. It should make it easy to toggle
    between `rich` fromatted and plain logs

    It will implement the functions of a Logger obj 
    https://docs.python.org/3/library/logging.html#logging.Logger.propagate
    """

    def __init__(self, module_name: str = 'root') -> None:
        logging.config.dictConfig(cdev_settings.get("LOGGING_INFO"))
        self._logger = logging.getLogger(module_name)


    def debug(self, msg):
        self._logger.info(msg)


    def info(self, msg):
        self._logger.info(msg)


    def warning(self, msg):
        if isinstance(msg, str):
            msg = f"[bold red blink]{msg}"

        self._logger.warning(msg)


    def error(self, msg):
        self._logger.error(msg)

    
    def critical(self, msg):
        self._logger.critical(msg)


    def log(self, level: int, msg):
        self._logger.log(level, msg)

    
    def exception(self, msg):
        self._logger.exception(msg)


    


def get_cdev_logger(name: str):
    print(name)

    top_level_module_name = name.split(".")[1] if len(name.split(".")) > 1 else None

    print(top_level_module_name) 

    return cdev_logger(top_level_module_name)
