from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

from enum import Enum

from pydantic import BaseModel

from ..models import Rendered_Component, Rendered_Resource



class Action_Type(str, Enum):
    CREATE='CREATE'
    UPDATE_IDENTITY='UPDATE_IDENTITY'
    UPDATE_NAME='UPDATE_NAME'
    DELETE='DELETE'



class Resource_State_Difference(BaseModel):
    action_type: Action_Type
    previous_resource: Union[Rendered_Resource, None]
    new_resource: Union[Rendered_Resource, None]

    class Config:  
        use_enum_values = True


class Component_State_Difference(BaseModel):
    action_type: Action_Type
    previous_component: Union[Rendered_Component, None]
    new_component: Union[Rendered_Component, None]

    resource_diff: Union[List[Resource_State_Difference], None]

    class Config:  
        use_enum_values = True

