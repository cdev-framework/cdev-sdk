from typing import  TypeVar

from core.constructs.output import Cloud_Output_Bool, Cloud_Output_Int, Cloud_Output_Str, cloud_output_dynamic_model


cdev_str = TypeVar('cdev_str', str, Cloud_Output_Str)
cdev_str_model = TypeVar('cdev_str_model', str, cloud_output_dynamic_model)
