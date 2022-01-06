import importlib
import inspect
import sys
from typing import Dict, Tuple, Any, List
from pydantic import BaseModel

from .components import Component_Difference, ComponentModel

from .resource import Resource_Reference_Difference, ResourceModel, Resource_Difference
from .resource_state import Resource_State

from ..utils.module_loader import import_module


class Backend_Configuration(BaseModel):
    python_module: str
    python_class: str
    config: Dict

    def __init__(__pydantic_self__, python_module: str, python_class: str, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": python_module,
            "python_class": python_class,
            "config": config
        })
    

class Backend():
    def __init__(self, **kwargs) -> None:
        raise NotImplementedError

    # Api for working with Resource States
    def create_resource_state(self, name: str, parent_resource_state_uuid: str=None) -> str:
        """
        Create a new resource state within this stored state. 

        Arguments:
            parent_resource_state_uuid (str): The uuid of the parent resource state.
            name (str): the name of this resource state.

        Returns:
            uuid (str): The uuid of the newly created resource state.

        Raises:
            ResourceStateAlreadyExists

        """
        raise NotImplementedError


    def delete_resource_state(self, resource_state_uuid: str):
        """
        Delete a resource state within this store state.

        Arguments:
            resource_state_uuid (str): The uuid of the resource state to delete

        Raises:
            ResourceStateDoesNotExist
            ResourceStateNotEmpty
        """
        raise NotImplementedError


    def get_resource_state(self, resource_state_uuid: str) -> Resource_State:
        """
        Load a resource state from the stored state.

        Arguments:
            resource_state_uuid (str): The uuid of the desired resource state
        
        Raises:
            ResourceStateDoesNotExist
        """
        raise NotImplementedError


    def get_top_level_resource_states(self) -> List[Resource_State]:
        """
        List all the top level resource states for this stored state

        Returns:
            resource_states (List[Resource_States]): Top level resource states.
        
        Raises:
            ResourceStateDoesNotExist
        
        """
        raise NotImplementedError


    # Api for working with components within a resource state
    def create_component(self, resource_state_uuid: str, component_name: str):
        """
        Create a component within a resource state.

        Arguments:
            resource_state_uuid (str): The resource state that this component will be in.
            component_name (str): Name of the component

        Returns:
            uuid (str): The uuid for the new component

        Raises:
            ComponentAlreadyExists

        """
        raise NotImplementedError


    def delete_component(self, resource_state_uuid: str, component_name: str):
        """
        Delete a component within a resource state. 

        Arguments:
            resource_state_uuid (str): The resource state that this component will be in.
            component_name (str): uuid of the component.
        
        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
            ComponentNotEmpty
        """
        raise NotImplementedError


    def get_component(self, resource_state_uuid: str, component_name: str) -> ComponentModel:
        """
        Get a component from the resource state

        Arguments:
            resource_state_uuid (str): The resource state that this component will be in.
            component_name (str): Name of the component
        
        Returns: 
            component (ComponentModel): The data for the requested component

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
        """
        raise NotImplementedError 


    # Api for changing individual Resources
    # The resource state needs to know when a mapper will be attempting to update a cdev resource. It is in charge of
    # determing if the current resource state is capable of handling a change in the resource. 
    def create_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference) -> str:
        """
        Create in the Resource State the desire to change a particular resource. If the resource state can currently handle creating
        this change, it will return a base idempotency token that can be used to construct idempotency tokens for deploying the underlying
        cloud resources. If the resource state can not handle the change, it will throw an error. 

        Arguments:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource.

        Returns:
            transaction_token (str): The transaction token to be used by the mapper when deploying the resource. This token can be used to give to a cloud 
            provider as a idempotency token.
        
        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
        """
        raise NotImplementedError


    def complete_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, cloud_output: Dict):
        """
        Notify the resource state that all changes to a resource have completed successfully. This will cause the resource to
        update the state of the resource to the new state.

        Arguments:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource
            transaction_token (str): Identifying token representing what transaction is being completed
            cloud_output (Dict): Output information from the cloud provider 
        
        
        Raises:
            ResourceChangeTransactionDoesNotExist
            ComponentDoesNotExist

        """
        raise NotImplementedError


    def fail_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, failed_state: Dict):
        """
        Notify the resource state that an attempted change to a resource has failed. The provided failed state should encapsulate any needed information
        for a future mapper to recover the state of the resource back into a proper state.

        Arguments:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource
            transaction_token (str): Identifying token representing what transaction is being completed
            failed_state (Dict): A dictionary containing information a mapper could use to resolve the failed state
        
        Raises:
            ResourceStateDoesNotExist
            ResourceChangeTransactionDoesNotExist
        """
        raise NotImplementedError


    # Api for getting references from other components
    # Components can have references to resources that are managed in other components and it is the responsibility of the backend to resolve those references
    # The backend should be in charge of handling IAM to determine if resolving the reference is possible
    def resolve_reference_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Reference_Difference):
        """
        Either reference or dereference a resource from a different component. 

        Arguments:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource

        Raises:
            ResourceReferenceError
        """
        raise NotImplementedError


    # Api for working with a resource states failed resource updates 
    # We can either update the failed state by the mapper attempting to fix the underlying issue, or
    # We can recover the resource to either the new state or previous state by the mapper fixing the issues, or
    # We can just delete the failure from our failed state (not recommended unless you know what you are doing because it can leave resources in the cloud)
    def change_failed_state_of_resource_change(self, resource_state_uuid: str, transaction_token: str, new_failed_state: Dict):
        """
        Update the failed state of a 'resource change'.

        Arguments:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.
            new_failed_state (Dict): The new failed state of the transaction.
        
        Raises:
            ResourceStateDoesNotExist
            ResourceChangeTransactionDoesNotExist
        
        """
        raise NotImplementedError

    
    def recover_failed_resource_change(self, resource_state_uuid: str, transaction_token: str, to_previous_state: bool=True):
        """
        Recover the state of the change back to the previous state or forward to the new state. Note this will result in the failed resource change being removed from the stored state.
        
        Arguments:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.
            to_previous_state (bool): Bool to decide if the resource should be transitioned to the previous state or new state.
        
        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
            ResourceChangeTransactionDoesNotExist
        """
        raise NotImplementedError


    def remove_failed_resource_change(self, resource_state_uuid: str, transaction_token: str): 
        """
        Completely remove the failed resource change from the stored state. Note that this should be used with caution as it can lead to hanging cloud resources. 
        
        Arguments:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.
        
        Raises:
            ResourceStateDoesNotExist
            ResourceChangeTransactionDoesNotExist
        """
        raise NotImplementedError


    # Api for getting information about a resource from the backend
    def get_resource_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str) -> ResourceModel:
        """
        Get the state of a resource from a component based on the name of the resource

        Arguments:
            resource_state_uuid (str): The resource state for this resource.
            component_name (str): The component this resource is in.
            resource_type: The RUUID of the resource desired
            resource_name: The name of the resource desired
        
        Raises:
            ResourceStateDoesNotExist 
            ComponentDoesNotExist
            ResourceDoesNotExist
        """
        raise NotImplementedError


    def get_resource_by_hash(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_hash: str) -> ResourceModel:
        """
        Get the state of a resource from a component based on the hash of the resource

        Arguments:
            resource_state_uuid (str): The resource state for this resource.
            component_name (str): The component this resource is in.
            resource_type (str): The RUUID of the resource desired.
            resource_hash (str): The hash of the resource desired.
        
        Raises:
            ResourceStateDoesNotExist 
            ComponentDoesNotExist
            ResourceDoesNotExist
        """
        raise NotImplementedError

    
    def get_cloud_output_value_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str, key: str) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information. 

        Arguments:
            resource_state_uuid (str): The resource state for this resource.
            component_name (str): The component this resource is in.
            resource_type (str): The RUUID of the resource desired
            resource_name (str): The hash of the resource desired
            key (str): The key for the desired value
        
        Raises:
            ResourceStateDoesNotExist 
            ComponentDoesNotExist
            CloudOutputDoesNotExist
            KeyNotInCloudOutput
        
        """
        raise NotImplementedError

    
    def get_cloud_output_value_by_hash(self, resource_state_uuid: str, component_uuid: str, resource_type: str, resource_hash: str, key: str) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information. 

        Arguments:
            resource_state_uuid (str): The resource state for this resource.
            component_name (str): The component this resource is in.
            resource_type (str): The RUUID of the resource desired.
            resource_hash (str): The hash of the resource desired.
            key (str): The key for the desired value.
        
        Raises:
            ResourceStateDoesNotExist 
            ComponentDoesNotExist
            KeyNotInCloudOutput
            CloudOutputDoesNotExist
        
        """
        raise NotImplementedError



    # Api for creating differences between workspace and the backend
    # The backend must be responsible for determining the differences to get to a new potential state because the backend
    # is the one that has to implement the changes.
    # In the future, this will also allow for the backend to manage IAM permissions for creating, updating, referencing, etc
    # the actual cdev resources.
    def create_differences(self, resource_state_uuid: str, new_components: List[ComponentModel], old_components: List[str]) -> Tuple[Component_Difference, Resource_Reference_Difference, Resource_Difference]:
        """
        Create the set of differences from a proposed set of components to a provided set of current components identified by their name. This allows the flexibility for working on a particular 
        set of components within a resource state. 
        """
        raise NotImplementedError


def load_backend(config: Backend_Configuration) -> Backend:
    # sometime the module is already loaded so just reload it to capture any changes
    try:
        backend_module = import_module(config.python_module)
    except Exception as e:
        print("Error loading backend module")
        print(f'Error > {e}')
        
        raise e


    backend_class = None
    for item in dir(backend_module):  
        potential_obj = getattr(backend_module,item)  
        if inspect.isclass(potential_obj) and issubclass(potential_obj, Backend) and item == config.python_class:
            backend_class = potential_obj
            break
    
    
    if not backend_class:
        print(f"Could not find {config.python_class} in {config.python_module}")
        raise Exception
    
    try:
        # initialize the backend obj with the provided configuration values
        initialized_obj = potential_obj(**config.config)
    except Exception as e:
        print(f"Could not initialize {potential_obj} Class from config {config.config}")
        raise e

    return initialized_obj
