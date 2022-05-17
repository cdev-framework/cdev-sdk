"""Set of constructs for creating triggerable events

"""

from typing import Optional, Union

from core.constructs.models import frozendict, ImmutableModel
from core.default.resources.simple.iam import permission_arn_model, permission_model

################
##### Events
################
class event_model(ImmutableModel):
    originating_resource_name: str

    originating_resource_type: str

    hash: str

    granting_permission: Optional[Union[permission_model, permission_arn_model]]


class Event:
    def hash(self) -> str:
        raise NotImplementedError

    def render(
        self,
    ) -> event_model:
        raise NotImplementedError
