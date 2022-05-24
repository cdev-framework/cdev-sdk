"""Utilities for generating logs of framework executions

Note that logging should work in a duality within the framework. Meaning, that all functions within the framework
should use the same logging utilities, but how they are provided will differ. All files will have a module
level definition of a default logger, this will allow the utilities to log when called as simple functions
through normal python execution. Within the framework, all executions will be wrapped in a global namespace
that has a logger, therefor when the functions are called as part of the framework, it will be this logger
that is used.

This is important in mainting that utility functions for the framework are not bound to used within the framework,
but it also allows there to be dynamic functionality of how logs will be proccessed and displayed to the user.

"""
import logging.config
import logging
import os
from typing import Dict, Union


def _create_logging_settings(log_level: str) -> Dict:
    return {
        "version": 1,
        "filename": ".cdev/logs/userlogs",
        "formatters": {
            "jsonFormatter": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
            "simpleFormatter": {
                "format": "%(asctime)s %(name)s - %(levelname)s: %(message)s"
            },
            "richFormatter": {"format": "%(name)s - %(levelname)s: %(message)s"},
        },
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "jsonFormatter",
                "filename": ".cdev/logs/userlogs",
            },
            "simpleHandler": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simpleFormatter",
            },
            "richHandler": {
                "class": "rich.logging.RichHandler",
                "level": log_level,
                "formatter": "richFormatter",
                "markup": True,
                "show_path": False,
                "show_time": False,
                "rich_tracebacks": True,
            },
        },
        "loggers": {
            "core_file": {
                "level": log_level,
                "handlers": ["fileHandler"],
                "propagate": False,
            },
            "core_rich": {
                "level": log_level,
                "handlers": ["richHandler"],
                "propagate": False,
            },
            "core_simple": {
                "level": log_level,
                "handlers": ["simpleHandler"],
                "propagate": False,
            },
        },
        "root": {"level": "ERROR", "handlers": ["simpleHandler"]},
        "disable_existing_loggers": False,
    }


class cdev_logger:
    """Wrapper around pythons basic logger object to provide a layer of flexibility for logging.

    Specifically, this will add the ability to always process logs into a JSON file for debugging errors, while
    also allowing the user to provide a flag to set a logging level to display to the user.

    It will implement the functions of a Logger obj
    https://docs.python.org/3/library/logging.html#logging.Logger.propagate


    Note that when formating data into a log message, it must use '%' formatted strings instead of f
    strings. This is allows am optimization used by the logging library to not allocate strings unless the
    log needs to be evaluated. Within the context of a framework, these allocations can add up. This should
    be enforced with code styling at the PR level.

    Also note the optimization around formmatted logs.

    For more info read https://docs.python.org/3/howto/logging.html#optimization
    """

    def __init__(
        self,
        is_rich_formatted=True,
        show_logs: bool = False,
        logging_level: Union[str, int] = "ERROR",
    ) -> None:

        self.is_rich_formatted = is_rich_formatted
        self.show_logs = show_logs

        log_info = _create_logging_settings(logging_level)

        fp = os.path.join(os.getcwd(), log_info.get("filename"))

        if not os.path.isfile(fp):
            if not os.path.isdir(os.path.dirname(os.path.dirname(fp))):
                os.mkdir(os.path.dirname(os.path.dirname(fp)))

            if not os.path.isdir(os.path.dirname(fp)):
                os.mkdir(os.path.dirname(fp))

            with open(fp, "a"):
                os.utime(fp, None)

        logging.config.dictConfig(log_info)
        self._json_logger = logging.getLogger("core_file")
        self._simple_logger = logging.getLogger("core_simple")
        self._rich_logger = logging.getLogger("core_rich")

    def _write_log(
        self,
        *args,
        func_name: str,
        original_msg: str,
        formatted_msg: str = "",
        **kw_args,
    ) -> None:
        # Always write a log to the json file
        getattr(self._json_logger, func_name)(original_msg, *args, **kw_args)
        if self.show_logs:
            # We need to write logs to console
            # Either write a plain log or rich formatted log to the console
            if not self.is_rich_formatted:
                getattr(self._simple_logger, func_name)(original_msg, *args, **kw_args)
            else:
                getattr(self._rich_logger, func_name)(formatted_msg, *args, **kw_args)

    def debug(self, msg, *args, **kw_args) -> None:
        if self.is_rich_formatted:
            self._write_log(
                *args,
                func_name="debug",
                original_msg=msg,
                formatted_msg=f"[bold blue]{msg}",
                **kw_args,
            )

        else:
            self._write_log(*args, func_name="debug", original_msg=msg, **kw_args)

    def info(self, msg, *args, **kw_args):
        if self.is_rich_formatted:
            self._write_log(
                *args,
                func_name="info",
                original_msg=msg,
                formatted_msg=f"[bold blue]{msg}",
                **kw_args,
            )

        else:
            self._write_log(*args, func_name="info", original_msg=msg, **kw_args)

    def warning(self, msg, *args, **kw_args) -> None:
        if self.is_rich_formatted:
            self._write_log(
                *args,
                func_name="warning",
                original_msg=msg,
                formatted_msg=f"[bold yellow blink]{msg}",
                **kw_args,
            )

        else:
            self._write_log(*args, func_name="warning", original_msg=msg, **kw_args)

    def error(self, msg, *args, **kw_args) -> None:
        if self.is_rich_formatted:
            self._write_log(
                *args,
                func_name="error",
                original_msg=msg,
                formatted_msg=f"[bold red blink]:cross_mark: :cross_mark: :cross_mark: {msg} :cross_mark: :cross_mark: :cross_mark:",
                **kw_args,
            )

        else:
            self._write_log(*args, func_name="error", original_msg=msg, **kw_args)

    def exception(self, msg) -> None:
        self._write_log("exception", msg, msg)


class global_log_container:
    def __init__(self, logger: cdev_logger) -> None:
        self._logger = logger

    @property
    def is_rich_formatted(self) -> bool:
        return self._logger.is_rich_formatted

    @property
    def show_logs(self) -> bool:
        return self._logger.show_logs

    def debug(self, msg, *args, **kw_args) -> None:
        self._logger.debug(msg, *args, **kw_args)

    def info(self, msg, *args, **kw_args) -> None:
        self._logger.info(msg, *args, **kw_args)

    def warning(self, msg, *args, **kw_args) -> None:
        self._logger.warning(msg, *args, **kw_args)

    def error(self, msg, *args, **kw_args) -> None:
        self._logger.error(msg, *args, **kw_args)

    def exception(self, msg) -> None:
        self._logger.exception(msg)


log = global_log_container(cdev_logger())


def set_global_logger(new_logger: cdev_logger) -> None:
    global log

    log._logger = new_logger
