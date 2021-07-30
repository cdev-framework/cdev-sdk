from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Rendered_Resource


class QueueAttributeName(str, Enum): 

    All = 'All'

    Policy = 'Policy'

    VisibilityTimeout = 'VisibilityTimeout'

    MaximumMessageSize = 'MaximumMessageSize'

    MessageRetentionPeriod = 'MessageRetentionPeriod'

    ApproximateNumberOfMessages = 'ApproximateNumberOfMessages'

    ApproximateNumberOfMessagesNotVisible = 'ApproximateNumberOfMessagesNotVisible'

    CreatedTimestamp = 'CreatedTimestamp'

    LastModifiedTimestamp = 'LastModifiedTimestamp'

    QueueArn = 'QueueArn'

    ApproximateNumberOfMessagesDelayed = 'ApproximateNumberOfMessagesDelayed'

    DelaySeconds = 'DelaySeconds'

    ReceiveMessageWaitTimeSeconds = 'ReceiveMessageWaitTimeSeconds'

    RedrivePolicy = 'RedrivePolicy'

    FifoQueue = 'FifoQueue'

    ContentBasedDeduplication = 'ContentBasedDeduplication'

    KmsMasterKeyId = 'KmsMasterKeyId'

    KmsDataKeyReusePeriodSeconds = 'KmsDataKeyReusePeriodSeconds'

    DeduplicationScope = 'DeduplicationScope'

    FifoThroughputLimit = 'FifoThroughputLimit'





class queue_output(str, Enum):
    QueueUrl = "QueueUrl"


class queue_model(Rendered_Resource):
    QueueName: str

    Attributes: Optional[Dict[str,str]]

    tags: Optional[Dict[str,str]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, QueueName: str, Attributes: Dict[str, str]=None, tags: Dict[str, str]=None ) -> None:
        data = {
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "QueueName": QueueName,
            "Attributes": Attributes,
            "tags": tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        super().__init__(**filtered_data)

    class Config:
        extra='ignore'

