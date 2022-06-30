import json
from typing import FrozenSet, List, Tuple, Union, Dict, Optional
from uuid import uuid4

from botocore.exceptions import ClientError

from core.default.resources.simple.iam import permission_model, permission_arn_model

from .. import aws_client


def create_role_with_permissions(
    role_name: str,
    permissions: FrozenSet[Union[permission_model, permission_arn_model]],
    assume_role_policy: str,
) -> Tuple[Optional[str], Optional[List[Dict]]]:
    """
    This function creates a new IAM role and policies such that the function will have correct access to resources.

    Arguments:
        role_name: Name of the role
        permissions [List[Union[permission_model, permission_arn_model]]]: The permission to assign to the role

    Returns:
        str: The arn of the role created
        List[Tuple[str,bool]]: List of Tuple of permission arn and bool to denote if the permission should be destroyed on delete

    """

    role_arn = _create_role(role_name, assume_role_policy)
    if role_arn is None:
        return None, None

    permission_info: List[Dict] = []

    for permission in permissions:
        permission_info.append(add_policy(role_name, permission))

    basic_execution_permission_arn = permission_arn_model(
        arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        hash="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )

    permission_info.append(add_policy(role_name, basic_execution_permission_arn))

    return role_arn, permission_info


def delete_role_and_permissions(role_name: str, permission_arns: List[Dict]) -> None:
    """
    Delete all permissions and the associated role
    """
    for info in permission_arns:
        delete_policy(role_name, info)

    aws_client.run_client_function("iam", "delete_role", {"RoleName": role_name})


def delete_policy(role_name: str, permission_info: Dict) -> None:
    """
    Delete a policy
    """
    detach_policy(role_name, permission_info.get("arn"))

    if permission_info.get("was_created"):
        aws_client.run_client_function(
            "iam", "delete_policy", {"PolicyArn": permission_info.get("arn")}
        )


def add_policy(
    role_name: str, permission: Union[permission_model, permission_arn_model]
) -> Dict:
    """
    Creates a policy if needed and then adds the policy to the given role
    """
    if isinstance(permission, permission_arn_model):
        # Already deployed policy so just append arn
        returned_permission_arn = permission.arn
        was_created = False

    else:
        returned_permission_arn = create_policy(permission)
        was_created = True

    _attach_policy_to_arn(role_name, returned_permission_arn)

    return {
        "hash": permission.hash,
        "arn": returned_permission_arn,
        "was_created": was_created,
    }


def create_policy(permission: permission_model) -> str:
    """
    Creates the policy and returns the arn
    """

    policy = {
        "Version": "2012-10-17",
    }

    statement = {"Effect": permission.effect, "Action": list(permission.actions)}

    statement["Resource"] = permission.cloud_id
    policy["Statement"] = [statement]

    permission_name = str(uuid4())

    rv = aws_client.run_client_function(
        "iam",
        "create_policy",
        {"PolicyName": permission_name, "PolicyDocument": json.dumps(policy)},
    )

    return rv.get("Policy").get("Arn")


def detach_policy(role_name: str, permission_arn: str) -> None:
    aws_client.run_client_function(
        "iam",
        "detach_role_policy",
        {"RoleName": role_name, "PolicyArn": permission_arn},
    )


def _create_role(name: str, assume_role_policy: str) -> Optional[str]:
    """
    Creates the role and returns the arn
    """
    try:
        rv = aws_client.run_client_function(
            "iam",
            "create_role",
            {
                "RoleName": name,
                "AssumeRolePolicyDocument": assume_role_policy,
            },
        )
        return rv.get("Role").get("Arn")
    except ClientError as e:
        print(f"Unable to create role {name}. {e}")

    return None


def _attach_policy_to_arn(role_arn: str, policy_arn: str) -> None:
    aws_client.run_client_function(
        "iam", "attach_role_policy", {"RoleName": role_arn, "PolicyArn": policy_arn}
    )
