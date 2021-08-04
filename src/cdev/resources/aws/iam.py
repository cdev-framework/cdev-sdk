from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .iam_models import *


class Policy(Cdev_Resource):
    """
    Creates a new version of the specified managed policy. To update a managed policy, you create a new policy version. A managed policy can have up to five versions. If the policy has five versions, you must delete an existing version using DeletePolicyVersion before you create a new version.

 Optionally, you can set the new version as the policy's default version. The default version is the version that is in effect for the IAM users, groups, and roles to which the policy is attached.

 For more information about managed policy versions, see [Versioning for managed policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/policies-managed-versions.html) in the *IAM User Guide*.


    """

    def __init__(self,name: str, PolicyName: str, PolicyDocument: str, Path: str=None, Description: str=None, Tags: List[Tag]=None):
        ""
        super().__init__(name)

        self.PolicyName = PolicyName
        """
        The friendly name of the policy.

 IAM user, group, role, and policy names must be unique within the account. Names are not distinguished by case. For example, you cannot create resources named both "MyResource" and "myresource".


        """

        self.Path = Path
        """
        The path for the policy.

 For more information about paths, see [IAM identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.

 This parameter is optional. If it is not included, it defaults to a slash (/).

 This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of either a forward slash (/) by itself or a string that must begin and end with forward slashes. In addition, it can contain any ASCII character from the ! (`\u0021`) through the DEL character (`\u007F`), including most punctuation characters, digits, and upper and lowercased letters.


        """

        self.PolicyDocument = PolicyDocument
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

        self.Description = Description
        """
        A friendly description of the policy.

 Typically used to store information about the permissions defined in the policy. For example, "Grants access to production DynamoDB tables."

 The policy description is immutable. After a value is assigned, it cannot be changed.


        """

        self.Tags = Tags
        """
        A structure that represents user-provided metadata that can be associated with an IAM resource. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.


        """

        self.hash = hasher.hash_list([self.PolicyName, self.PolicyDocument, self.Path, self.Description, self.Tags])

    def render(self) -> policy_model:
        data = {
            "ruuid": "cdev::aws::iam::policy",
            "name": self.name,
            "hash": self.hash,
            "PolicyName": self.PolicyName,
            "Path": self.Path,
            "PolicyDocument": self.PolicyDocument,
            "Description": self.Description,
            "Tags": self.Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return policy_model(**filtered_data)

    def from_output(self, key: policy_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::iam::policy::{self.hash}", "key": key, "type": "cdev_output"})


class Role(Cdev_Resource):
    """
    Updates the description or maximum session duration setting of a role.


    """

    def __init__(self,name: str, RoleName: str, AssumeRolePolicyDocument: str, Path: str=None, Description: str=None, MaxSessionDuration: int=None, PermissionsBoundary: str=None, Tags: List[Tag]=None):
        ""
        super().__init__(name)

        self.Path = Path
        """
         The path to the role. For more information about paths, see [IAM Identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.

 This parameter is optional. If it is not included, it defaults to a slash (/).

 This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of either a forward slash (/) by itself or a string that must begin and end with forward slashes. In addition, it can contain any ASCII character from the ! (`\u0021`) through the DEL character (`\u007F`), including most punctuation characters, digits, and upper and lowercased letters.


        """

        self.RoleName = RoleName
        """
        The name of the role to create.

 IAM user, group, role, and policy names must be unique within the account. Names are not distinguished by case. For example, you cannot create resources named both "MyResource" and "myresource".


        """

        self.AssumeRolePolicyDocument = AssumeRolePolicyDocument
        """
        The trust relationship policy document that grants an entity permission to assume the role.

 In IAM, you must provide a JSON policy that has been converted to a string. However, for CloudFormation templates formatted in YAML, you can provide the policy in JSON or YAML format. CloudFormation always converts a YAML policy to JSON format before submitting it to IAM.

 The [regex pattern](http://wikipedia.org/wiki/regex) used to validate this parameter is a string of characters consisting of the following:

 * Any printable ASCII character ranging from the space character (`\u0020`) through the end of the ASCII character range


* The printable characters in the Basic Latin and Latin-1 Supplement character set (through `\u00FF`)


* The special characters tab (`\u0009`), line feed (`\u000A`), and carriage return (`\u000D`)



  Upon success, the response includes the same trust policy in JSON format.


        """

        self.Description = Description
        """
        A description of the role.


        """

        self.MaxSessionDuration = MaxSessionDuration
        """
        The maximum session duration (in seconds) that you want to set for the specified role. If you do not specify a value for this setting, the default maximum of one hour is applied. This setting can have a value from 1 hour to 12 hours.

 Anyone who assumes the role from the or API can use the `DurationSeconds` API parameter or the `duration-seconds` CLI parameter to request a longer session. The `MaxSessionDuration` setting determines the maximum duration that can be requested using the `DurationSeconds` parameter. If users don't specify a value for the `DurationSeconds` parameter, their security credentials are valid for one hour by default. This applies when you use the `AssumeRole*` API operations or the `assume-role*` CLI operations but does not apply when you use those operations to create a console URL. For more information, see [Using IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html) in the *IAM User Guide*.


        """

        self.PermissionsBoundary = PermissionsBoundary
        """
        The ARN of the policy that is used to set the permissions boundary for the role.


        """

        self.Tags = Tags
        """
        A structure that represents user-provided metadata that can be associated with an IAM resource. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.


        """

        self.hash = hasher.hash_list([self.RoleName, self.AssumeRolePolicyDocument, self.Path, self.Description, self.MaxSessionDuration, self.PermissionsBoundary, self.Tags])

    def render(self) -> role_model:
        data = {
            "ruuid": "cdev::aws::iam::role",
            "name": self.name,
            "hash": self.hash,
            "Path": self.Path,
            "RoleName": self.RoleName,
            "AssumeRolePolicyDocument": self.AssumeRolePolicyDocument,
            "Description": self.Description,
            "MaxSessionDuration": self.MaxSessionDuration,
            "PermissionsBoundary": self.PermissionsBoundary,
            "Tags": self.Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return role_model(**filtered_data)

    def from_output(self, key: role_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::iam::role::{self.hash}", "key": key, "type": "cdev_output"})


