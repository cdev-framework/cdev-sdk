from typing import Dict
from pydantic import BaseModel

from cdev.core.models import Component, Rendered_State, Resource_State, Resource 


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


    def create_resource(self, parent_state_uuid: str, parent_component_uuid: str, resource: Resource):
        pass


    # Deletes
    def delete_resource_state(self, state_uuid: str):
        pass


    def delete_component(self, state_uuid: str, component_uuid: str):
        pass
    

    def delete_resource(self, state_uuid: str, component_uuid: str, resource_hash: str):
        pass


    # Updates
    def update_resource(self, old_resource_hash: str, new_resource: Resource):
        pass


    def load_resource_state(self) -> Rendered_State:
        pass




    def get_resource(self, original_resource_name: str, original_resource_type: str):
        pass