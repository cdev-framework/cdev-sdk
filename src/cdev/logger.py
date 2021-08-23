import logging.config
import os

from .settings import SETTINGS as cdev_settings


#logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "..","logging.ini"), disable_existing_loggers=False)
#logger = logging.getLogger("frontend")


def get_cdev_logger(name: str):
    print(name)

    top_level_module_name = name.split(".")[1] if len(name.split(".")) > 1 else None

    print(top_level_module_name) 

    logging.config.dictConfig(cdev_settings.get("LOGGING_INFO"))
    logger = logging.getLogger(top_level_module_name)

    return logger
