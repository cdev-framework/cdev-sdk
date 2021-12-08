import json
import os
from typing import Dict, List, Any
import uuid

from cdev.core.constructs.backend import Backend_Configuration, Backend
from cdev.core.constructs.components import ComponentModel
from cdev.core.constructs.resource import Resource_Change_Type, Resource_Difference, ResourceModel
from cdev.core.constructs.resource_state import Resource_State
from cdev.core.settings import SETTINGS as cdev_settings
from pydantic.main import BaseModel
from pydantic.types import FilePath


DEFAULT_CENTRAL_STATE_FOLDER = os.path.join(cdev_settings.get('ROOT_FOLDER_NAME'), "state")
DEFAULT_CENTRAL_STATE_FILE = os.path.join(DEFAULT_CENTRAL_STATE_FOLDER, "local_state.json")

class Local_Backend_Configuration(Backend_Configuration):
    def __init__(self, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": "cdev.default.backend",
            "python_class": "Local_Backend",
            "config": config
        })


class LocalCentralFile(BaseModel):
    resource_state_locations: Dict[str, FilePath] # uuid -> file location
    top_level_states: List[str] # uuid
    resource_state_names: List[str]

    def __init__(__pydantic_self__, resource_state_locations: Dict[str, FilePath], top_level_states: List[str], resource_state_names: List[str] ) -> None:
        super().__init__(**{
            "resource_state_locations": resource_state_locations,
            "top_level_states": top_level_states,
            "resource_state_names": resource_state_names,
        })


class LocalBackend(Backend):
    """
    Implementation of a Backend using locally stored json files as the peristent storage medium. This backend should only be used for small project as it does not provide any mechanisms 
    to work well when multiple people edit the state. Also this is a single threaded implementation.

    *** For now, we will not use any kind of WAL for make changes to underlying state files, so it can be bad if you kill the process unexpectedly. In the future, it will use some mechanism
    to prevent this. ***
    """
    
    # Structurally, this implementation will have a central json that can be used as an index into more precise json files. For example, each resource state will be its own json file, but 
    # the central file will keep track of each one. 
    def __init__(self, **kwargs) -> None:
        print("right here")
        if not os.path.isdir(DEFAULT_CENTRAL_STATE_FOLDER):
            os.mkdir(DEFAULT_CENTRAL_STATE_FOLDER)

        if not os.path.isfile(DEFAULT_CENTRAL_STATE_FILE):
            self._central_state = LocalCentralFile({}, [], [])

        else:
            with open(DEFAULT_CENTRAL_STATE_FILE, 'r') as fh:
                self._central_state = LocalCentralFile(**json.load(fh))

        
    def _write_central_file(self):
        with open(DEFAULT_CENTRAL_STATE_FILE, 'w') as fh:
            json.dump(self._central_state.dict(), fh, indent=4)


    def _write_resource_state_file(self, resource_state: Resource_State, fp: FilePath):
        with open(fp, "w") as fh:
            json.dump(resource_state.dict(), fh, indent=4)
        

    # Api for working with Resource States
    def create_resource_state(self, parent_resource_state_uuid: str, name: str) -> str:
        # Create the new resource state 
        if name in set(self._central_state.resource_state_names):
            raise Exception("Creating resource state with taken name")

        resource_state_uuid = str(uuid.uuid4())
        if not parent_resource_state_uuid:
            # Create this as a top level resource state
            new_resource_state = Resource_State(name, resource_state_uuid, [])
            self._central_state.top_level_states.append(new_resource_state.uuid)

        else:
            new_resource_state = Resource_State(name, resource_state_uuid, [], parent_resource_state_uuid)

        filename = os.path.join(DEFAULT_CENTRAL_STATE_FOLDER, f"resource_state_{new_resource_state.uuid}.json")

        self._central_state.resource_state_locations[new_resource_state.uuid] = filename
        self._central_state.resource_state_names.append(new_resource_state.name)


        self._write_central_file()
        self._write_resource_state_file(new_resource_state, filename)

        return new_resource_state.uuid


    def delete_resource_state(self, state_uuid: str):
        if not state_uuid in self._central_state.resource_state_locations:
            raise Exception

        resource_state_to_delete = self.load_resource_state(state_uuid)

        if resource_state_to_delete.children:
            print(f"Can not delete resource state with children")
            raise Exception

        if resource_state_to_delete.parent_uuid:
            # Need to remove this as child of parent
            pass

        else:
            # if the resource state had no parent, then it was a top level resource state
            self._central_state.top_level_states.remove(resource_state_to_delete.uuid)


        self._central_state.resource_state_names.remove(resource_state_to_delete.name)
        file_location = self._central_state.resource_state_locations.pop(resource_state_to_delete.uuid)

        self._write_central_file()
        os.remove(file_location)


    def load_resource_state(self, state_uuid: str) -> Resource_State:
        if not state_uuid in self._central_state.resource_state_locations:
            raise Exception

        file_location = self._central_state.resource_state_locations.get(state_uuid)

        if not os.path.isfile(file_location):
            raise Exception

        try:
            with open(file_location, 'r') as fh:
                return Resource_State(**json.load(fh))

        except Exception as e:
            print(f"Error loading data from {file_location} as a Resource State")
            raise e

    
    def list_top_level_resource_states(self) -> List[Resource_State]:
        rv = []
        
        for resource_id in self._central_state.top_level_states:
            # Let any exception from loading a state pass up to caller
            rv.append(self.load_resource_state(resource_id))

        return rv
            

    # Components
    def create_component(self, resource_state_uuid: str, component_name: str):
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)
        except Exception as e:
            # Wrap in more informative error
            raise e 


        if component_name in set(x.name for x in resource_state.components):
            # Cant not have two components of the same name in the same resource state
            raise Exception

    
        new_component = ComponentModel(
            component_name
        )

        resource_state.components.append(new_component)

        self._write_resource_state_file(resource_state, resource_state_file_location)



    def delete_component(self, resource_state_uuid: str, component_name: str):
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)
        except Exception as e:
            # Wrap in more informative error
            raise e 


        if not component_name in set(x.name for x in resource_state.components):
            # Component of that name does not exists
            raise Exception

    
        resource_state.components = [x for x in resource_state.components if not x.name == component_name]

        self._write_resource_state_file(resource_state, resource_state_file_location)
        

    def create_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference) -> str:
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)
        except Exception as e:
            # Wrap in more informative error
            raise e 

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception


        transaction_token = str(uuid.uuid4())

        resource_state.resource_changes[transaction_token] = (component_name, diff)

        self._write_resource_state_file(resource_state, resource_state_file_location)

        return transaction_token


    def complete_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, cloud_output: Dict=None):
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)

        except Exception as e:
            # Wrap in more informative error
            raise e 

        if not transaction_token in resource_state.resource_changes:
            raise Exception

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception

        if diff.action_type == Resource_Change_Type.DELETE:
            component.rendered_resources = [x for x in component.rendered_resources if x.ruuid == diff.previous_resource.ruuid and x.name == diff.previous_resource.name]

        elif diff.action_type == Resource_Change_Type.UPDATE_IDENTITY or diff.action_type == Resource_Change_Type.UPDATE_NAME:
            
            component.rendered_resources = [x for x in component.rendered_resources if x.ruuid == diff.previous_resource.ruuid and x.name == diff.previous_resource.name].append(diff.new_resource)
            
            if cloud_output:
                cloud_output_id = f"{diff.new_resource.ruuid};{diff.new_resource.name}"
                component.cloud_output[cloud_output_id] = cloud_output

        elif diff.action_type == Resource_Change_Type.CREATE:
            component.rendered_resources.append(diff.new_resource)
        
            if cloud_output:
                cloud_output_id = f"{diff.new_resource.ruuid};{diff.new_resource.name}"
                component.cloud_output[cloud_output_id] = cloud_output
        
       
        # recompute hash

        resource_state.components = [x for x in resource_state.components if not x.name == component.name].append(component)

        resource_state.resource_changes.pop(transaction_token)
        

        self._write_resource_state_file(resource_state, resource_state_file_location)


    def fail_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, failed_state: Dict):
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)

        except Exception as e:
            # Wrap in more informative error
            raise e 

        if not transaction_token in resource_state.resource_changes:
            raise Exception

        resource_state.resource_changes.pop(transaction_token)
        resource_state.failed_changes[transaction_token] = (component_name, diff, failed_state)

        self._write_resource_state_file(resource_state, resource_state_file_location)


    def get_resource_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str) -> ResourceModel:
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            
        except Exception as e:
            # Wrap in more informative error
            raise e 

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception

        resource =  next((x for x in component.rendered_resources if x.ruuid == resource_type and x.name == resource_name), None)

        if not resource:
            raise Exception

        return resource


    def get_resource_by_hash(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_hash: str) -> ResourceModel:
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
        except Exception as e:
            # Wrap in more informative error
            raise e 

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception

        resource =  next((x for x in component.rendered_resources if x.ruuid == resource_type and x.hash == resource_hash), None)

        if not resource:
            raise Exception


        return resource

    
    def get_cloud_output_value_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str, key: str) -> Any:
        try:
            resource_state = self.load_resource_state(resource_state_uuid)

        except Exception as e:
            # Wrap in more informative error
            raise e 

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception

        resource =  next((x for x in component.rendered_resources if x.ruuid == resource_type and x.name == resource_name), None)

        if not resource:
            raise Exception

        cloud_output_id = f"{resource.ruuid};{resource.name}"

        if not cloud_output_id in component.cloud_output:
            raise Exception

        cloud_output = component.cloud_output.get(cloud_output_id)

        if not key in cloud_output:
            raise Exception

        return cloud_output.get(key)

    
    def get_cloud_output_value_by_hash(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_hash: str, key: str) -> Any:
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
        except Exception as e:
            # Wrap in more informative error
            raise e 

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise Exception

        resource =  next((x for x in component.rendered_resources if x.ruuid == resource_type and x.hash == resource_hash), None)

        if not resource:
            raise Exception


        cloud_output_id = f"{resource.ruuid};{resource.name}"


        if not cloud_output_id in component.cloud_output:
            raise Exception

    
        cloud_output = component.cloud_output.get(cloud_output_id)

        if not key in cloud_output:
            raise Exception

        return cloud_output.get(key)


    def change_failed_state_of_resource_change(self, resource_state_uuid: str, transaction_token: str, new_failed_state: Dict):
        try:
            resource_state = self.load_resource_state(resource_state_uuid)
            resource_state_file_location = self._central_state.resource_state_locations.get(resource_state_uuid)

        except Exception as e:
            # Wrap in more informative error
            raise e 


        if not transaction_token in resource_state.failed_changes:
            raise Exception


        previous_component, previous_diff, _ = resource_state.failed_changes.get(transaction_token)

        resource_state.failed_changes[transaction_token] = (previous_component, previous_diff, new_failed_state)

        self._write_resource_state_file(resource_state, resource_state_file_location)

    
    def recover_failed_resource_change(self, resource_state_uuid: str, transaction_token: str, to_previous_state: bool=True):
        pass


    def remove_failed_resource_change(self, resource_state_uuid: str, transaction_token: str): 
        pass