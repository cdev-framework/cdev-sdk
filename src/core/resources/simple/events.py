from typing import Optional, Union

from core.constructs.models import frozendict, ImmutableModel
from core.resources.simple.iam import permission_arn_model, permission_model

################
##### Events
################
class event_model(ImmutableModel):
    """
    Arguments:
        original_resource_name (str): [description]
        original_resource_type (str): [description]
        granting_permission (Optional[Union[permission_model, permission_arn_model]]): [description]
    """
    originating_resource_name: str

    originating_resource_type: str

    granting_permission: Optional[Union[permission_model, permission_arn_model]]


class Event():
    
    def hash(self) -> str:
        raise NotImplementedError

    def render(self,) -> event_model:
        raise NotImplementedError
