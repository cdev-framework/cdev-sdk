from core.utils import logger


def set_global_logger_from_cli(log_level: int) -> None:

    new_log = logger.cdev_logger(show_logs=True, logging_level=log_level)

    logger.set_global_logger(new_log)
