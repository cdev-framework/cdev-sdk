from enum import Enum
from core.utils.types import frozendict, ImmutableModel
################
##### Events
################

class EventTypes(str, Enum):
    HTTP_API_ENDPOINT = "api::endpoint"
    TABLE_STREAM = "table::stream"
    BUCKET_TRIGGER = "bucket:trigger"
    QUEUE_TRIGGER = "queue::trigger"
    TOPIC_TRIGGER = "topic::trigger"


class event_model(ImmutableModel):
    original_resource_name: str

    original_resource_type: str

    event_type: EventTypes

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True



class Event():
    
    def get_hash(self) -> str:
        raise NotImplementedError

    def render(self,) -> event_model:
        raise NotImplementedError
