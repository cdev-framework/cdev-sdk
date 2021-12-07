from typing import Dict, Optional, Callable, Any
from pydantic import BaseModel

from cdev.core.models import ComponentModel, Resource_State, Resource, Resource_Difference


class Backend_Configuration(BaseModel):
    python_module: str
    config: Dict

    def __init__(__pydantic_self__, python_module: str, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": python_module, 
            "config": config
        })
    

class Local_Backend_Configuration(Backend_Configuration):
    def __init__(self, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": "cdev.core.constructs.backend.Local_Backend_Configuration", 
            "config": config
        })


class Backend():

    # Api for working with Resource States
    def create_resource_state(self, parent_resource_state_uuid: str, name: str) -> str:
        pass


    def delete_resource_state(self, state_uuid: str):
        pass


    def load_resource_state(self, state_uuid) -> Resource_State:
        pass


    # Api for working with components within a resource state
    def create_component(self, resource_state_uuid: str, component_name: str) -> ComponentModel:
        pass


    def delete_component(self, resource_state_uuid: str, component_uuid: str):
        
        pass


    # Api for changing individual Resources
    # The resource state needs to know when a mapper will be attempting to update a cdev resource. It is in charge of
    # determing if the current resource state is capable of handling a change in the resource. 
    def create_resource_change(self, diff: Resource_Difference) -> str:
        """
        Create in the Resource State the desire to change a particular resource. If the resource state can currently handle creating
        this change, it will return a base idempotency token that can be used to construct idempotency tokens for deploying the underlying
        cloud resources. If the resource state can not handle the change, it will throw an error. 

        Arguments:
            diff (Resource_Difference): The desired change in the resource

        Returns:
            transaction_token (str): The transaction token to be used by the mapper when deploying the resource. This token can be used to give to a cloud 
            provider as a idempotency token.
        """
        pass


    def complete_resource_change(self, diff: Resource_Difference, transaction_token: str, cloud_output: Dict):
        """
        Notify the resource state that all changes to a resource have completed successfully. This will cause the resource to
        update the state of the resource to the new state.

        Arguments:
            diff (Resource_Difference): The desired change in the resource
            transaction_token (str): Identifying token representing what transaction is being completed
            cloud_output (Dict): Output information from the cloud provider 
        """
        pass


    def fail_resource_change(self, diff: Resource_Difference, transaction_token: str, failed_state: Dict):
        """
        Notify the resource state that an attempted change to a resource has failed. The provided failed state should encapsulate any needed information
        for a future mapper to recover the state of the resource back into a proper state.

        Arguments:
            diff (Resource_Difference): The desired change in the resource
            transaction_token (str): Identifying token representing what transaction is being completed
            failed_state (Dict): A dictionary containing information a mapper could use to resolve the failed state
        """
        pass


    # Api for getting information about a resource from the backend
    def get_resource_by_name(self, component_uuid: str, resource_type: str, resource_name: str) -> Resource:
        """
        Get the state of a resource from a component based on the name of the resource

        Arguments:
            component_uuid: The component that this resource is apart of
            resource_type: The RUUID of the resource desired
            resource_name: The name of the resource desired
        """
        pass


    def get_resource_by_hash(self, component_uuid: str, resource_type: str, resource_hash: str) -> Resource:
        """
        Get the state of a resource from a component based on the hash of the resource

        Arguments:
            component_uuid (str): The component that this resource is apart of
            resource_type (str): The RUUID of the resource desired
            resource_hash (str): The hash of the resource desired
        """
        pass

    
    def get_cloud_output_value_by_name(self, component_uuid: str, resource_type: str, resource_name: str, key: str) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information. 

        Arguments:
            component_uuid (str): The component that this resource is apart of
            resource_type (str): The RUUID of the resource desired
            resource_name (str): The hash of the resource desired
            key (str): The key for the desired value
        """
        pass

    
    def get_cloud_output_value_by_hash(self, component_uuid: str, resource_type: str, resource_hash: str, key: str) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information. 

        Arguments:
            component_uuid (str): The component that this resource is apart of
            resource_type (str): The RUUID of the resource desired
            resource_hash (str): The hash of the resource desired
            key (str): The key for the desired value
        """
        pass




    # Api for working with a resource states failed resource updates 
    # We can either update the failed state by the mapper attempting to fix the underlying issue, or
    # We can recover the resource to either the new state or previous state by the mapper fixing the issues, or
    # We can just delete the failure from our failed state (not recommended unless you know what you are doing because it can leave resources in the cloud)
    def change_failed_state_of_resource_change(transaction_token: str, new_failed_state: Dict):
        """
        Update the failed state of a 'resource change'.

        Arguments:
            transaction_token (str): Identifying token for the failed transaction
            new_failed_state (Dict): The new failed state of the transaction
        """
        pass

    
    def recover_failed_resource_change(transaction_token: str, to_previous_state: bool=True):
        """
        Recover the state of the change back to the previous state or forward to the new state. Note this will result in the failed resource change being removed from the stored state.
        
        Arguments:
            transaction_token (str): Identifying token for the failed transaction
            to_previous_state (bool): Bool to decide if the resource should be transitioned to the previous state or new state.
        """
        pass


    def remove_failed_resource_change(transaction_token: str): 
        """
        Completely remove the failed resource change from the stored state. Note that this should be used with caution as it can lead to hanging cloud resources. 
        
        Arguments:
            transaction_token (str): Identifying token for the failed transaction
        """
        pass

