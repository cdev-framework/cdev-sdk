from typing import Dict, Union, List, Optional, Set, Callable, Any
from typing_extensions import Literal

from enum import Enum

from pydantic import BaseModel


class ResourceModel(BaseModel):
    """
    This is the most basic information needed to describe a resource. 

    --- Attributes ---

    - ruuid ->  a string that represents the resource identifier (provider::resource-type)

    - hash  ->  a string that is the hash of this object. This hash must be computed such that 
                it changes only if a change in the state is desired.
    """


    ruuid: str
    """
    Name space identifier that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace)::(resource-type-id)
    """


    hash: str
    """
    This is a hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """


    name: str
    """
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace and resource type
    (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    parent_resources: Optional[List[str]]
    """
    A set of all resource identifications (ruuid:hash) that are a parent resource to some other resource in the component. This set serves as 
    a fast way of checking if we need to update descendants when a resource is updated 
    """

    class Config:
        validate_assignment = True
        extra = 'allow'


    def get_parent_resources(self) -> List[str]:
        """
        This function returns any resources that this resources depends on via the Output mechanism
        """
        return None


class ResourceReferenceModel(BaseModel):
    """
    This is the information needed to reference a resource that is defined outside this component

    --- Attributes ---

    - ruuid ->  a string that represents the resource identifier (provider::resource-type)

    - hash  ->  a string that is the hash of this object. This hash must be computed such that 
                it changes only if a change in the state is desired.
    """

    component_name: str
    """
    Name of the component that this resources resides in
    """

    ruuid: str
    """
    Name space identifier that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace)::(resource-type-id)
    """

    name: str
    """
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace and resource type
    (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    hash: Optional[str]
    """
    This is a hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """




    is_in_parent_resource_state: Optional[bool]
    """
    Boolean to determine if the reference should be resolved in the same resource state or from the parent resource state.
    """


    class Config:
        validate_assignment = True
        extra = 'allow'



class Resource_Change_Type(str, Enum):
    CREATE='CREATE'
    UPDATE_IDENTITY='UPDATE_IDENTITY'
    UPDATE_NAME='UPDATE_NAME'
    DELETE='DELETE'


class Resource_Reference_Change_Type(str, Enum):
    CREATE='CREATE'
    DELETE='DELETE'


class Resource_Difference(BaseModel):
    action_type: Resource_Change_Type
    component_uuid: str
    previous_resource: Union[ResourceModel, None]
    new_resource: Union[ResourceModel, None]

    class Config:  
        use_enum_values = True


class Resource_Reference_Difference(BaseModel):
    action_type: Resource_Reference_Change_Type
    resource_reference: ResourceReferenceModel

    class Config:  
        use_enum_values = True




class Cloud_Output(BaseModel):
    """
    Often we want resources that depend on the value of output of other resources that is only known after a cloud resource is created. This servers
    as an placeholder for that desired value until it is available. 
    """

    resource: str
    """
    ruuid:hash
    """

    key: str
    """
    The key to lookup the output value by (ex: arn)
    """

    type: Literal["cdev_output"]

        
    def __str__(self) -> str:
        return f"{self.resource}$${self.key}"



class Resource():
    RUUID: str = None

    def __init__(self, name: str):
        self.name = name
    

    def render(self) -> ResourceModel:
        pass

    def from_output(key: str) -> Cloud_Output:
        pass



class Referenced_Resource():
    RUUID: str = None

    def __init__(self, component_name: str, name: str, hash: str=None, is_in_parent_resource_state: bool = False):
        raise NotImplementedError
    

    def render(self) -> ResourceReferenceModel:
        raise NotImplementedError


    def from_output(key: str) -> Cloud_Output:
        raise NotImplementedError
