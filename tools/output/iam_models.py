from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager







class Tag(BaseModel):
    """
    A structure that represents user-provided metadata that can be associated with an IAM resource. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.


    """


    Key: Union[str, Cloud_Output]
    """
    The key name that can be used to look up or retrieve the associated value. For example, `Department` or `Cost Center` are common choices.


    """

    Value: Union[str, Cloud_Output]
    """
    The value associated with this tag. For example, tags with a key name of `Department` could have values such as `Human Resources`, `Accounting`, and `Support`. Tags with a key name of `Cost Center` might have values that consist of the number associated with the different cost centers in your company. Typically, many resources have tags with the same key name but with different values.

  Amazon Web Services always interprets the tag `Value` as a single string. If you need to store an array, you can store comma-separated values in the string. However, you must interpret the value in your code.

 
    """


    def __init__(self, Key: str, Value: str ):
        "My doc string"
        super().__init__(**{
            "Key": Key,
            "Value": Value,
        })        








class policy_output(str, Enum):
    """
    Creates a new managed policy for your account.

 This operation creates a policy version with a version identifier of `v1` and sets v1 as the policy's default version. For more information about policy versions, see [Versioning for managed policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-versions.html) in the *IAM User Guide*.

 As a best practice, you can validate your IAM policies. To learn more, see [Validating IAM policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_policy-validator.html) in the *IAM User Guide*.

 For more information about managed policies in general, see [Managed policies and inline policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-vs-inline.html) in the *IAM User Guide*.


    """

    PolicyName = "PolicyName"
    """
    The friendly name (not ARN) identifying the policy.


    """

    PolicyId = "PolicyId"
    """
    The stable and unique string identifying the policy.

 For more information about IDs, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.


    """

    Arn = "Arn"

    Path = "Path"
    """
    The path to the policy.

 For more information about paths, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.


    """

    DefaultVersionId = "DefaultVersionId"
    """
    The identifier for the version of the policy that is set as the default version.


    """

    AttachmentCount = "AttachmentCount"
    """
    The number of entities (users, groups, and roles) that the policy is attached to.


    """

    PermissionsBoundaryUsageCount = "PermissionsBoundaryUsageCount"
    """
    The number of entities (users and roles) for which the policy is used to set the permissions boundary. 

 For more information about permissions boundaries, see [Permissions boundaries for IAM identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)  in the *IAM User Guide*.


    """

    IsAttachable = "IsAttachable"
    """
    Specifies whether the policy can be attached to an IAM user, group, or role.


    """

    Description = "Description"
    """
    A friendly description of the policy.

 This element is included in the response to the GetPolicy operation. It is not included in the response to the ListPolicies operation. 


    """

    CreateDate = "CreateDate"
    """
    The date and time, in [ISO 8601 date-time format](http://www.iso.org/iso/iso8601), when the policy was created.


    """

    UpdateDate = "UpdateDate"
    """
    The date and time, in [ISO 8601 date-time format](http://www.iso.org/iso/iso8601), when the policy was last updated.

 When a policy has only one version, this field contains the date and time when the policy was created. When a policy has more than one version, this field contains the date and time when the most recent policy version was created.


    """

    Tags = "Tags"
    """
    A list of tags that are attached to the instance profile. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.


    """



class role_output(str, Enum):
    """
    Creates a new role for your account. For more information about roles, see [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/WorkingWithRoles.html). For information about quotas for role names and the number of roles you can create, see [IAM and STS quotas](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html) in the *IAM User Guide*.


    """

    Path = "Path"
    """
     The path to the role. For more information about paths, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*. 


    """

    RoleName = "RoleName"
    """
    The friendly name that identifies the role.


    """

    RoleId = "RoleId"
    """
     The stable and unique string identifying the role. For more information about IDs, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*. 


    """

    Arn = "Arn"
    """
     The Amazon Resource Name (ARN) specifying the role. For more information about ARNs and how to use them in policies, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide* guide. 


    """

    CreateDate = "CreateDate"
    """
    The date and time, in [ISO 8601 date-time format](http://www.iso.org/iso/iso8601), when the role was created.


    """

    AssumeRolePolicyDocument = "AssumeRolePolicyDocument"
    """
    The policy that grants an entity permission to assume the role.


    """

    Description = "Description"
    """
    A description of the role that you provide.


    """

    MaxSessionDuration = "MaxSessionDuration"
    """
    The maximum session duration (in seconds) for the specified role. Anyone who uses the CLI, or API to assume the role can specify the duration using the optional `DurationSeconds` API parameter or `duration-seconds` CLI parameter.


    """

    PermissionsBoundary = "PermissionsBoundary"
    """
    The ARN of the policy used to set the permissions boundary for the role.

 For more information about permissions boundaries, see [Permissions boundaries for IAM identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)  in the *IAM User Guide*.


    """

    Tags = "Tags"
    """
    A list of tags that are attached to the role. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.


    """

    RoleLastUsed = "RoleLastUsed"
    """
    Contains information about the last time that an IAM role was used. This includes the date and time and the Region in which the role was last used. Activity is only reported for the trailing 400 days. This period can be shorter if your Region began supporting these features within the last year. The role might have been used more than 400 days ago. For more information, see [Regions where data is tracked](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_access-advisor.html#access-advisor_tracking-period) in the *IAM User Guide*.


    """



class policy_model(Rendered_Resource):
    """

    Creates a new version of the specified managed policy. To update a managed policy, you create a new policy version. A managed policy can have up to five versions. If the policy has five versions, you must delete an existing version using DeletePolicyVersion before you create a new version.

 Optionally, you can set the new version as the policy's default version. The default version is the version that is in effect for the IAM users, groups, and roles to which the policy is attached.

 For more information about managed policy versions, see [Versioning for managed policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-versions.html) in the *IAM User Guide*.
    
    """


    PolicyName: Union[str, Cloud_Output]
    """
    The friendly name of the policy.

 IAM user, group, role, and policy names must be unique within the account. Names are not distinguished by case. For example, you cannot create resources named both "MyResource" and "myresource".
    """

    Path: Optional[Union[str, Cloud_Output]]
    """
    The path for the policy.

 For more information about paths, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.

 This parameter is optional. If it is not included, it defaults to a slash (/).

 This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of either a forward slash (/) by itself or a string that must begin and end with forward slashes. In addition, it can contain any ASCII character from the ! (`\u0021`) through the DEL character (`\u007F`), including most punctuation characters, digits, and upper and lowercased letters.
    """

    PolicyDocument: Union[str, Cloud_Output]
    """
    The JSON policy document that you want to use as the content for the new policy.

 You must provide policies in JSON format in IAM. However, for CloudFormation templates formatted in YAML, you can provide the policy in JSON or YAML format. CloudFormation always converts a YAML policy to JSON format before submitting it to IAM.

 The maximum length of the policy document that you can pass in this operation, including whitespace, is listed below. To view the maximum character counts of a managed policy with no whitespaces, see [IAM and STS character quotas](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entity-length).

 To learn more about JSON policy grammar, see [Grammar of the IAM JSON policy language](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_grammar.html) in the *IAM User Guide*. 

 The [regex pattern](http://wikipedia.org/wiki/regex) used to validate this parameter is a string of characters consisting of the following:

 * Any printable ASCII character ranging from the space character (`\u0020`) through the end of the ASCII character range


* The printable characters in the Basic Latin and Latin-1 Supplement character set (through `\u00FF`)


* The special characters tab (`\u0009`), line feed (`\u000A`), and carriage return (`\u000D`)
    """

    Description: Optional[Union[str, Cloud_Output]]
    """
    A friendly description of the policy.

 Typically used to store information about the permissions defined in the policy. For example, "Grants access to production DynamoDB tables."

 The policy description is immutable. After a value is assigned, it cannot be changed.
    """

    Tags: Optional[Union[List[Tag], Cloud_Output]]
    """
    A structure that represents user-provided metadata that can be associated with an IAM resource. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.
    """


    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['PolicyName', 'PolicyDocument', 'Path', 'Description', 'Tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set([('PolicyArn', 'Arn')])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


class role_model(Rendered_Resource):
    """

    Updates the description or maximum session duration setting of a role.
    
    """


    Path: Optional[Union[str, Cloud_Output]]
    """
    The path to the role. For more information about paths, see [IAM Identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.

 This parameter is optional. If it is not included, it defaults to a slash (/).

 This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of either a forward slash (/) by itself or a string that must begin and end with forward slashes. In addition, it can contain any ASCII character from the ! (`\u0021`) through the DEL character (`\u007F`), including most punctuation characters, digits, and upper and lowercased letters.
    """

    RoleName: Union[str, Cloud_Output]
    """
    The name of the role to create.

 IAM user, group, role, and policy names must be unique within the account. Names are not distinguished by case. For example, you cannot create resources named both "MyResource" and "myresource".
    """

    AssumeRolePolicyDocument: Union[str, Cloud_Output]
    """
    The trust relationship policy document that grants an entity permission to assume the role.

 In IAM, you must provide a JSON policy that has been converted to a string. However, for CloudFormation templates formatted in YAML, you can provide the policy in JSON or YAML format. CloudFormation always converts a YAML policy to JSON format before submitting it to IAM.

 The [regex pattern](http://wikipedia.org/wiki/regex) used to validate this parameter is a string of characters consisting of the following:

 * Any printable ASCII character ranging from the space character (`\u0020`) through the end of the ASCII character range


* The printable characters in the Basic Latin and Latin-1 Supplement character set (through `\u00FF`)


* The special characters tab (`\u0009`), line feed (`\u000A`), and carriage return (`\u000D`)



  Upon success, the response includes the same trust policy in JSON format.
    """

    Description: Optional[Union[str, Cloud_Output]]
    """
    A description of the role.
    """

    MaxSessionDuration: Optional[Union[int, Cloud_Output]]
    """
    The maximum session duration (in seconds) that you want to set for the specified role. If you do not specify a value for this setting, the default maximum of one hour is applied. This setting can have a value from 1 hour to 12 hours.

 Anyone who assumes the role from the or API can use the `DurationSeconds` API parameter or the `duration-seconds` CLI parameter to request a longer session. The `MaxSessionDuration` setting determines the maximum duration that can be requested using the `DurationSeconds` parameter. If users don't specify a value for the `DurationSeconds` parameter, their security credentials are valid for one hour by default. This applies when you use the `AssumeRole*` API operations or the `assume-role*` CLI operations but does not apply when you use those operations to create a console URL. For more information, see [Using IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html) in the *IAM User Guide*.
    """

    PermissionsBoundary: Optional[Union[str, Cloud_Output]]
    """
    The ARN of the policy that is used to set the permissions boundary for the role.
    """

    Tags: Optional[Union[List[Tag], Cloud_Output]]
    """
    A structure that represents user-provided metadata that can be associated with an IAM resource. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.
    """


    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['RoleName', 'AssumeRolePolicyDocument', 'Path', 'Description', 'MaxSessionDuration', 'PermissionsBoundary', 'Tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['RoleName'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


