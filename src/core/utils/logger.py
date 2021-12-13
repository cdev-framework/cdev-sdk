import logging.config
import logging
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
        log_info = cdev_settings.get("LOGGING_INFO")

        fp = log_info.get("handlers").get("fileHandler").get("filename")
        
        if not os.path.isfile(fp):
            
            os.mkdir(os.path.dirname(os.path.dirname(fp)))
            os.mkdir(os.path.dirname(fp))
            with open(fp, 'a'):
                os.utime(fp,None)
        #
        logging.config.dictConfig(log_info)
        self._json_logger = logging.getLogger(module_name)
        self._simple_logger = logging.getLogger(f"{module_name}_simple")
        self._rich_logger = logging.getLogger(f"{module_name}_rich")

    
    def _write_log(self, func_name, original_msg, formatted_msg):
        # Always write a log to the json file
        getattr(self._json_logger, func_name)(original_msg)

        if cdev_settings.get("SHOW_LOGS"):
            # We need to write logs to console
            # Either write a plain log or rich formatted log to the console
            if cdev_settings.get("OUTPUT_PLAIN"):
                getattr(self._simple_logger, func_name)(original_msg)
            else:
                getattr(self._rich_logger, func_name)(formatted_msg)
        

    def debug(self, msg):
        #self._logger.info(msg)
        self._write_log("debug", msg, f"[bold blue]{msg}")


    def info(self, msg):
        #if isinstance(msg, str):
        #    msg = f"[bold blue blink]{msg}"
        self._write_log("info", msg, f"[bold blue]{msg}")
    

    def warning(self, msg):
        #if isinstance(msg, str):
        #    msg = f"[bold yellow blink]{msg}[/bold yellow blink]"
        self._write_log("warning", msg, f"[bold yellow blink]{msg}")


    def error(self, msg):
        #if isinstance(msg, str):
        #    msg = f"[bold red blink]:cross_mark: :cross_mark: :cross_mark: {msg} :cross_mark: :cross_mark: :cross_mark:"
        self._write_log("error", msg, f"[bold red blink]:cross_mark: :cross_mark: :cross_mark: {msg} :cross_mark: :cross_mark: :cross_mark:")

    
    def critical(self, msg):
        self._write_log("critical", msg, f"[bold red blink]:skull: :skull: :skull: {msg} :skull: :skull: :skull:")


    def exception(self, msg):
        self._write_log("exception", msg, msg)


    


def get_cdev_logger(name: str):
    top_level_module_name = name.split(".")[1] if len(name.split(".")) > 1 else name


    return cdev_logger(top_level_module_name)
