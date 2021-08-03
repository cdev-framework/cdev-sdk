from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager


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
    """
    Creates a new standard or FIFO queue. You can pass one or more attributes in the request. Keep the following in mind:

 * If you don't specify the `FifoQueue` attribute, Amazon SQS creates a standard queue.

  You can't change the queue type after you create it and you can't convert an existing standard queue into a FIFO queue. You must either create a new FIFO queue for your application or delete your existing standard queue and recreate it as a FIFO queue. For more information, see [Moving From a Standard Queue to a FIFO Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html#FIFO-queues-moving) in the *Amazon SQS Developer Guide*. 

 
* If you don't provide a value for an attribute, the queue is created with the default value for the attribute.


* If you delete a queue, you must wait at least 60 seconds before creating a queue with the same name.



 To successfully create a new queue, you must provide a queue name that adheres to the [limits related to queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/limits-queues.html) and is unique within the scope of your queues.

  After you create a queue, you must wait at least one second after the queue is created to be able to use the queue.

  To get the queue URL, use the  `GetQueueUrl`  action.  `GetQueueUrl`  requires only the `QueueName` parameter. be aware of existing queue names:

 * If you provide the name of an existing queue along with the exact names and values of all the queue's attributes, `CreateQueue` returns the queue URL for the existing queue.


* If the queue name, attribute names, or attribute values don't match an existing queue, `CreateQueue` returns an error.



 Some actions take lists of parameters. These lists are specified using the `param.n` notation. Values of `n` are integers starting from 1. For example, a parameter list with two elements looks like this:

  `&AttributeName.1=first` 

  `&AttributeName.2=second` 

  Cross-account permissions don't apply to this action. For more information, see [Grant cross-account permissions to a role and a user name](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-customer-managed-policy-examples.html#grant-cross-account-permissions-to-role-and-user-name) in the *Amazon SQS Developer Guide*.

 
    """

    QueueUrl = "QueueUrl"
    """
    The name of the new queue. The following limits apply to this name:

 * A queue name can have up to 80 characters.


* Valid values: alphanumeric characters, hyphens (`-`), and underscores (`_`).


* A FIFO queue name must end with the `.fifo` suffix.



 Queue URLs and names are case-sensitive.


    """



class queue_model(Rendered_Resource):
    """

    Deletes the queue specified by the `QueueUrl`, regardless of the queue's contents.

  Be careful with the `DeleteQueue` action: When you delete a queue, any messages in the queue are no longer available. 

  When you delete a queue, the deletion process takes up to 60 seconds. Requests you send involving that queue during the 60 seconds might succeed. For example, a  `SendMessage`  request might succeed, but after 60 seconds the queue and the message you sent no longer exist.

 When you delete a queue, you must wait at least 60 seconds before creating a queue with the same name.

  Cross-account permissions don't apply to this action. For more information, see [Grant cross-account permissions to a role and a user name](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-customer-managed-policy-examples.html#grant-cross-account-permissions-to-role-and-user-name) in the *Amazon SQS Developer Guide*.
    
    """


    QueueName: str
    """
    The name of the new queue. The following limits apply to this name:

 * A queue name can have up to 80 characters.


* Valid values: alphanumeric characters, hyphens (`-`), and underscores (`_`).


* A FIFO queue name must end with the `.fifo` suffix.



 Queue URLs and names are case-sensitive.
    """

    Attributes: Optional[Dict[QueueAttributeName,str]]
    """
    A map of attributes with their corresponding values.

 The following lists the names, descriptions, and values of the special request parameters that the `CreateQueue` action uses:

 *  `DelaySeconds` – The length of time, in seconds, for which the delivery of all messages in the queue is delayed. Valid values: An integer from 0 to 900 seconds (15 minutes). Default: 0. 


*  `MaximumMessageSize` – The limit of how many bytes a message can contain before Amazon SQS rejects it. Valid values: An integer from 1,024 bytes (1 KiB) to 262,144 bytes (256 KiB). Default: 262,144 (256 KiB). 


*  `MessageRetentionPeriod` – The length of time, in seconds, for which Amazon SQS retains a message. Valid values: An integer from 60 seconds (1 minute) to 1,209,600 seconds (14 days). Default: 345,600 (4 days). 


*  `Policy` – The queue's policy. A valid Amazon Web Services policy. For more information about policy structure, see [Overview of Amazon Web Services IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/PoliciesOverview.html) in the *Amazon IAM User Guide*. 


*  `ReceiveMessageWaitTimeSeconds` – The length of time, in seconds, for which a  `ReceiveMessage`  action waits for a message to arrive. Valid values: An integer from 0 to 20 (seconds). Default: 0. 


*  `RedrivePolicy` – The string that includes the parameters for the dead-letter queue functionality of the source queue as a JSON object. For more information about the redrive policy and dead-letter queues, see [Using Amazon SQS Dead-Letter Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) in the *Amazon SQS Developer Guide*.


	+  `deadLetterTargetArn` – The Amazon Resource Name (ARN) of the dead-letter queue to which Amazon SQS moves messages after the value of `maxReceiveCount` is exceeded.
	
	
	+  `maxReceiveCount` – The number of times a message is delivered to the source queue before being moved to the dead-letter queue. When the `ReceiveCount` for a message exceeds the `maxReceiveCount` for a queue, Amazon SQS moves the message to the dead-letter-queue. The dead-letter queue of a FIFO queue must also be a FIFO queue. Similarly, the dead-letter queue of a standard queue must also be a standard queue.

 
*  `VisibilityTimeout` – The visibility timeout for the queue, in seconds. Valid values: An integer from 0 to 43,200 (12 hours). Default: 30. For more information about the visibility timeout, see [Visibility Timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) in the *Amazon SQS Developer Guide*.



 The following attributes apply only to [server-side-encryption](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html):

 *  `KmsMasterKeyId` – The ID of an Amazon Web Services managed customer master key (CMK) for Amazon SQS or a custom CMK. For more information, see [Key Terms](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html#sqs-sse-key-terms). While the alias of the Amazon Web Services managed CMK for Amazon SQS is always `alias/aws/sqs`, the alias of a custom CMK can, for example, be `alias/*MyAlias*` . For more examples, see [KeyId](https://docs.aws.amazon.com/kms/latest/APIReference/API_DescribeKey.html#API_DescribeKey_RequestParameters) in the *Key Management Service API Reference*. 


*  `KmsDataKeyReusePeriodSeconds` – The length of time, in seconds, for which Amazon SQS can reuse a [data key](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#data-keys) to encrypt or decrypt messages before calling KMS again. An integer representing seconds, between 60 seconds (1 minute) and 86,400 seconds (24 hours). Default: 300 (5 minutes). A shorter time period provides better security but results in more calls to KMS which might incur charges after Free Tier. For more information, see [How Does the Data Key Reuse Period Work?](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html#sqs-how-does-the-data-key-reuse-period-work). 



 The following attributes apply only to [FIFO (first-in-first-out) queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html):

 *  `FifoQueue` – Designates a queue as FIFO. Valid values are `true` and `false`. If you don't specify the `FifoQueue` attribute, Amazon SQS creates a standard queue. You can provide this attribute only during queue creation. You can't change it for an existing queue. When you set this attribute, you must also provide the `MessageGroupId` for your messages explicitly.

 For more information, see [FIFO queue logic](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html) in the *Amazon SQS Developer Guide*.


*  `ContentBasedDeduplication` – Enables content-based deduplication. Valid values are `true` and `false`. For more information, see [Exactly-once processing](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html) in the *Amazon SQS Developer Guide*. Note the following: 


	+ Every message must have a unique `MessageDeduplicationId`.
	
	
		- You may provide a `MessageDeduplicationId` explicitly.
		
		
		- If you aren't able to provide a `MessageDeduplicationId` and you enable `ContentBasedDeduplication` for your queue, Amazon SQS uses a SHA-256 hash to generate the `MessageDeduplicationId` using the body of the message (but not the attributes of the message). 
		
		
		- If you don't provide a `MessageDeduplicationId` and the queue doesn't have `ContentBasedDeduplication` set, the action fails with an error.
		
		
		- If the queue has `ContentBasedDeduplication` set, your `MessageDeduplicationId` overrides the generated one.
	+ When `ContentBasedDeduplication` is in effect, messages with identical content sent within the deduplication interval are treated as duplicates and only one copy of the message is delivered.
	
	
	+ If you send one message with `ContentBasedDeduplication` enabled and then another message with a `MessageDeduplicationId` that is the same as the one generated for the first `MessageDeduplicationId`, the two messages are treated as duplicates and only one copy of the message is delivered.

 The following attributes apply only to [high throughput for FIFO queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/high-throughput-fifo.html):

 *  `DeduplicationScope` – Specifies whether message deduplication occurs at the message group or queue level. Valid values are `messageGroup` and `queue`.


*  `FifoThroughputLimit` – Specifies whether the FIFO queue throughput quota applies to the entire queue or per message group. Valid values are `perQueue` and `perMessageGroupId`. The `perMessageGroupId` value is allowed only when the value for `DeduplicationScope` is `messageGroup`.



 To enable high throughput for FIFO queues, do the following:

 * Set `DeduplicationScope` to `messageGroup`.


* Set `FifoThroughputLimit` to `perMessageGroupId`.



 If you set these attributes to anything other than the values shown for enabling high throughput, normal throughput is in effect and deduplication occurs as specified.

 For information on throughput quotas, see [Quotas related to messages](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html) in the *Amazon SQS Developer Guide*.
    """

    tags: Optional[Dict[str,str]]
    """
    Add cost allocation tags to the specified Amazon SQS queue. For an overview, see [Tagging Your Amazon SQS Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-tags.html) in the *Amazon SQS Developer Guide*.

 When you use queue tags, keep the following guidelines in mind:

 * Adding more than 50 tags to a queue isn't recommended.


* Tags don't have any semantic meaning. Amazon SQS interprets tags as character strings.


* Tags are case-sensitive.


* A new tag with a key identical to that of an existing tag overwrites the existing tag.



 For a full list of tag restrictions, see [Quotas related to queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-limits.html#limits-queues) in the *Amazon SQS Developer Guide*.

  To be able to tag a queue on creation, you must have the `sqs:CreateQueue` and `sqs:TagQueue` permissions.

 Cross-account permissions don't apply to this action. For more information, see [Grant cross-account permissions to a role and a user name](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-customer-managed-policy-examples.html#grant-cross-account-permissions-to-role-and-user-name) in the *Amazon SQS Developer Guide*.
    """


    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['QueueName', 'Attributes', 'tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['QueueUrl'])
        return {k:cloud_mapper_manager.get_output_value(identifier, k) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


