import json
from typing import List, Tuple, Union, Dict


from cdev.backend import cloud_mapper_manager
from cdev.utils import hasher, logger, environment as cdev_environment
from cdev.resources.simple import xlambda as simple_lambda



from ..aws import aws_client as raw_aws_client


log = logger.get_cdev_logger(__name__)

AssumeRolePolicyDocumentJSON = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'''


def create_role_with_permissions(role_name: str, permissions: List[Union[simple_lambda.Permission,simple_lambda.PermissionArn]]) -> Tuple[str, Dict[str, Tuple[str,bool]]]:
    """
    This function creates a new IAM role and policies such that the function will have correct access to resources. 

    It returns a tuple (RoleArn, Dict(permission_hash -> PolicyArn) ) that should be stored in the functions cloud output so that they can be cleaned up. 
    """
    
    role_arn = _create_role(role_name)
    log.debug(f"Create Role {role_arn}")

    permission_info = dict()

    # Add the basic lambda permission to all lambda roles
    # interestingly, adding this permission in the resource caused a weird issue with the live deployment module
    permissions.append(simple_lambda.PermissionArn(**{
        "arn": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    }))


    for permission in permissions:
        rv= add_policy(role_name, permission)
        permission_info[permission.get_hash()] = rv

    return (role_arn, permission_info)


def delete_role_and_permissions(role_name: str, permission_arns: List[Tuple[str, bool]]) -> bool:
    """
    Delete all permissions and the associated role
    """
    for permission_arn in permission_arns:
        delete_policy(role_name, permission_arn)
    
    raw_aws_client.run_client_function("iam", "delete_role", {
        "RoleName": role_name
    })
        
    return True


def delete_policy(role_name: str, permission_arn: Tuple[str, bool]) -> bool:
    """
    Detaches the policy from the role then deletes the policy if it was created by us
    """
    raw_aws_client.run_client_function("iam", "detach_role_policy", {
            "RoleName": role_name,
            "PolicyArn": permission_arn[0]
        })

    if permission_arn[1]:
        raw_aws_client.run_client_function("iam", "delete_policy", {
            "PolicyArn": permission_arn[0]
        })


def add_policy(role_name: str, permission: Union[simple_lambda.Permission,simple_lambda.PermissionArn] ):
    """
    Creates a policy if need and then adds the policy to the given role
    """
    if isinstance(permission, simple_lambda.PermissionArn):
        # Already deployed policy so just append arn
        returned_permission_arn = permission.arn
        is_created = False
        log.debug(f"Added Already Deployed Permission {permission.arn}")

    else:
        returned_permission_arn = _create_policy(permission)
        is_created = True
        log.debug(f"Created Permission {returned_permission_arn} from {permission.get_hash()}")

    _attach_policy_to_arn(role_name, returned_permission_arn)
    log.debug(f"Attached Permission {returned_permission_arn} to Role {role_name}")
    return (returned_permission_arn, is_created)


def _create_policy(permission: simple_lambda.Permission) -> str:
    """
    Creates the policy and returns the arn
    """
    log.debug(f"Attempting to create {permission}")

    policy = {
        "Version": "2012-10-17",
    }

    statement = {
        "Effect": permission.effect,
        "Action": permission.actions
    }

    cdev_resource_name = permission.resource.split("::")[-1]
    cdev_resource_type = "::".join(permission.resource.split("::")[:-1])
    
    resource_info = cloud_mapper_manager.get_output_by_name(cdev_resource_type, cdev_resource_name)
    
    if not resource_info:
        raise Exception
    
    statement["Resource"] = resource_info.get("arn")

    policy['Statement'] = [statement]

    permission_name = f"{cdev_resource_name}_{hasher.hash_list(permission.actions)}_{cdev_environment.get_current_environment_hash()}"

    rv = raw_aws_client.run_client_function("iam", "create_policy", {
        "PolicyName": permission_name,
        "PolicyDocument": json.dumps(policy)
    })

    return rv.get("Policy").get('Arn')


def _create_role(name: str) -> str:
    """
    Creates the role and returns the arn
    """
    log.debug(f"Attemping to create Role {name}")
    rv = raw_aws_client.run_client_function("iam", "create_role", {
        "RoleName": name,
        "AssumeRolePolicyDocument": AssumeRolePolicyDocumentJSON,
    })

    return rv.get("Role").get("Arn")


def _attach_policy_to_arn(role_arn: str, policy_arn: str) -> bool:
    log.debug(f"Attempting to attach {policy_arn} to role {role_arn}")
    raw_aws_client.run_client_function("iam", "attach_role_policy", {
        "RoleName":role_arn,
        "PolicyArn": policy_arn
    })

    return True
