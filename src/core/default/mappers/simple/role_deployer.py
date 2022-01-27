import json
from typing import FrozenSet, List, Tuple, Union, Dict
from uuid import uuid4

from core.resources.simple.iam import permission_model, permission_arn_model

from .. import aws_client 


def create_role_with_permissions(
    role_name: str,
    permissions: FrozenSet[Union[permission_model, permission_arn_model]],
    assume_role_policy: str
) -> Tuple[str, List[Tuple[Union[permission_model, permission_arn_model], str]]]:
    """
    This function creates a new IAM role and policies such that the function will have correct access to resources.

    Arguments:
        role_name: Name of the role
        permissions [List[Union[permission_model, permission_arn_model]]]: The permission to assign to the role
    
    Returns:
        str: The arn of the role created
        Dict[Union[permission_model, permission_arn_model], str]]: Permission to the arn of the created permission
    
    """

    role_arn = _create_role(role_name, assume_role_policy)
    permission_info: List[Tuple[Union[permission_model, permission_arn_model], str]] = []


    for permission in permissions:
        rv = add_policy(role_name, permission)
        permission_info.append((permission, rv))


    basic_execution_permission_arn = permission_arn_model(
        arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )

    permission_info.append(
        (
            basic_execution_permission_arn, 
            add_policy(role_name, basic_execution_permission_arn)
        )
    )

    return (role_arn, permission_info)


def delete_role_and_permissions(
    role_name: str, permission_arns: List[Tuple[Union[permission_model, permission_arn_model], str]]
) -> bool:
    """
    Delete all permissions and the associated role
    """
    for permission_model, permission_arn in permission_arns:
        _detach_policy(role_name, permission_arn)

        #if isinstance(permission_model, simple_lambda.permission_model):
        #    delete_policy(permission_arn)

    aws_client.run_client_function("iam", "delete_role", {"RoleName": role_name})

    return True



def delete_policy(permission_arn: str):
    """
    Delete a policy
    """
    aws_client.run_client_function(
        "iam", "delete_policy", {"PolicyArn": permission_arn}
    )


def add_policy(
    role_name: str,
    permission: Union[permission_model, permission_arn_model]
):
    """
    Creates a policy if needed and then adds the policy to the given role
    """
    if isinstance(permission, permission_arn_model):
        # Already deployed policy so just append arn
        returned_permission_arn = permission.arn
        
    else:
        returned_permission_arn = _create_policy(permission)
        
    _attach_policy_to_arn(role_name, returned_permission_arn)

    return returned_permission_arn


def _create_policy(permission: permission_model) -> str:
    """
    Creates the policy and returns the arn
    """

    policy = {
        "Version": "2012-10-17",
    }

    statement = {"Effect": permission.effect, "Action": permission.actions}

    statement["Resource"] = permission_model.cloud_id
    policy["Statement"] = [statement]

    permission_name = str(uuid4())

    rv = aws_client.run_client_function(
        "iam",
        "create_policy",
        {
            "PolicyName": permission_name, 
            "PolicyDocument": json.dumps(policy)
        },
    )

    return rv.get("Policy").get("Arn")


def _create_role(name: str, assume_role_policy: str) -> str:
    """
    Creates the role and returns the arn
    """
    
    rv = aws_client.run_client_function(
        "iam",
        "create_role",
        {
            "RoleName": name,
            "AssumeRolePolicyDocument": assume_role_policy,
        },
    )

    return rv.get("Role").get("Arn")


def _attach_policy_to_arn(role_arn: str, policy_arn: str) -> bool:   
    aws_client.run_client_function(
        "iam", 
        "attach_role_policy", 
        {
            "RoleName": role_arn, 
            "PolicyArn": policy_arn
        }
    )



def _detach_policy(role_name: str, permission_arn: str):
    aws_client.run_client_function(
        "iam",
        "detach_role_policy",
        {
            "RoleName": role_name, 
            "PolicyArn": permission_arn
        },
    )
