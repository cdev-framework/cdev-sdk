from typing import Dict, Optional
from pydantic import BaseModel

from cdev.core.models import Component, Resource_State, Resource, Resource_Difference


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


class StoredState():

    def create_resource_state(self, state: Resource_State):
        pass


    def create_component(self, parent_state_uuid: str, component: Component):
        pass


    # Deletes
    def delete_resource_state(self, state_uuid: str):
        pass


    def delete_component(self, state_uuid: str, component_uuid: str):
        pass


    def load_resource_state(self) -> Resource_State:
        pass


    def get_resource_by_name(self, original_resource_type: str, original_resource_name: str) -> Resource:
        pass

    def get_resource_by_hash(self, original_resource_type: str, original_resource_hash: str) -> Resource:
        pass


    # Api for changing individual Resources
    # The resource state needs to know when a mapper will be attempting to update a cdev resource. It is in charge of
    # determing if the current resource state is capable of handling a change in the resource. 
    def create_resource_change(self, diff: Resource_Difference) -> str:
        """
        Create in the Resource State the desire to change a particular resource. If the resource state can currently handle creating
        this change, it will return a base idempotency token that can be used to construct idempotency tokens for deploying the underlying
        cloud resources. If the resource state can not handle the change, it will throw an error. 
        """
        pass


    def complete_resource_change(self, diff: Resource_Difference, transaction_token: str ):
        """
        Notify the resource state that all changes to a resource have completed successfully. This will cause the resource to
        update the state of the resource to the new state. 
        """
        pass


    def fail_resource_change(self, diff: Resource_Difference, transaction_token: str, failed_state: Dict):
        """
        Notify the resource state that an attempted change to a resource has failed. The provided failed state should encapsulate any needed information
        for a future mapper to recover the state of the resource back into a proper state.
        """
        pass


    # Api for working with a resource states failed resource updates 
    # We can either update the failed state by the mapper attempting to fix the underlying issue, or
    # We can recover the resource to either the new state or previous state by the mapper fixing the issues, or
    # We can just delete the failure from our failed state (not recommended unless you know what you are doing because it can leave resources in the cloud)

    def change_failed_state_of_resource_change(transaction_token: str, new_failed_state: Dict):
        """
        Update the failed state of a 'resource change'. 
        """
        pass

    
    def recover_failed_resource_change(transaction_token: str, to_previous_state: bool=True):
        """
        Recover the state of the change back to the previous state or forward to the new state. Note this will result in the failed resource change being removed from the stored state.
        """
        pass


    def remove_failed_resource_change(transaction_token: str): 
        """
        Completely remove the failed resource change from the stored state. Note that this should be used with caution as it can lead to hanging cloud resources. 
        """
        pass

