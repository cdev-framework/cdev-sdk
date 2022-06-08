"""Extra types to be used within the type hints of the framework
"""
from typing import TypeVar, Callable, Any

from core.constructs.cloud_output import (
    Cloud_Output_Bool,
    Cloud_Output_Int,
    Cloud_Output_Str,
    cloud_output_dynamic_model,
)


cdev_str = TypeVar("cdev_str", str, Cloud_Output_Str)
cdev_int = TypeVar("cdev_int", int, Cloud_Output_Int)
cdev_str_model = TypeVar("cdev_str_model", str, cloud_output_dynamic_model)

F = TypeVar("F", bound=Callable[..., Any])
