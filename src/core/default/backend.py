import json
import os
from pydantic.main import BaseModel
from pydantic.types import DirectoryPath, FilePath
from typing import Dict, List, Any, Tuple
import uuid



from ..constructs.backend import Backend_Configuration, Backend
from ..constructs.backend_exceptions import *

from ..constructs.components import Component_Change_Type, ComponentModel, Component_Difference
from ..constructs.resource import Resource_Change_Type, Resource_Difference, Resource_Reference_Change_Type, ResourceModel, Resource_Reference_Difference, ResourceReferenceModel
from ..constructs.resource_state import Resource_State
from ..settings import SETTINGS as cdev_settings
from ..utils import hasher as cdev_hasher, logger


class LocalBackendError(BackendError):
    pass


class CanNotFindResourceStateFile(LocalBackendError):
    pass


class InvalidResourceStateData(LocalBackendError):
    pass

DEFAULT_BASE = os.path.join(cdev_settings.get('ROOT_FOLDER_NAME'), "state")
DEFAULT_CENTRAL_STATE_FILE = os.path.join(DEFAULT_BASE, "local_state.json")

log = logger.get_cdev_logger(__name__)

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
    # Structurally, this implementation will have a central json that can be used as an index into more precise json files. For example, each resource state will be its own json file, but 
    # the central file will keep track of each one. 
    def __init__(self, base_folder: DirectoryPath= None, central_state_file: FilePath= None) -> None:
        """
        Implementation of a Backend using locally stored json files as the peristent storage medium. This backend should only be used for small project as it does not provide any mechanisms 
        to work well when multiple people edit the state. Also this is a single threaded implementation.

        *** For now, we will not use any kind of WAL for make changes to underlying state files, so it can be bad if you kill the process unexpectedly. In the future, it will use some mechanism
        to prevent this. ***

        Arguments:
            base_folder (DirectoryPath): Path to a folder to use for storing local json files. Defaults to cdev setting if not provided.
            central_state_file (FilePath): Path to the central state file. Defaults to cdev setting if not provided.
        """
    

        self.base_folder = base_folder if base_folder else DEFAULT_BASE
        self.central_state_file = central_state_file if central_state_file else DEFAULT_CENTRAL_STATE_FILE

        if not os.path.isdir(self.base_folder):
            print(f"ERROR HERE")
            raise Exception

        if not os.path.isfile(self.central_state_file):
            self._central_state = LocalCentralFile({}, [], [])

        else:
            with open(self.central_state_file, 'r') as fh:
                self._central_state = LocalCentralFile(**json.load(fh))

        
    def _write_central_file(self):
        with open(self.central_state_file, 'w') as fh:
            json.dump(self._central_state.dict(), fh, indent=4)


    def _write_resource_state_file(self, resource_state: Resource_State, fp: FilePath):
        with open(fp, "w") as fh:
            json.dump(resource_state.dict(), fh, indent=4)
        

    # Api for working with Resource States
    def create_resource_state(self, name: str, parent_resource_state_uuid: str=None)  -> str:
        # Create the new resource state 
        if name in set(self._central_state.resource_state_names):
            raise ResourceStateAlreadyExists("Creating resource state with taken name")

        resource_state_uuid = str(uuid.uuid4())
        if not parent_resource_state_uuid:
            # Create this as a top level resource state
            new_resource_state = Resource_State(name, resource_state_uuid)
            self._central_state.top_level_states.append(new_resource_state.uuid)

        else:
            new_resource_state = Resource_State(name=name, uuid=resource_state_uuid, components=[], parent_uuid=parent_resource_state_uuid)

        filename = os.path.join(self.base_folder, f"resource_state_{new_resource_state.uuid}.json")

        self._central_state.resource_state_locations[new_resource_state.uuid] = filename
        self._central_state.resource_state_names.append(new_resource_state.name)


        self._write_central_file()
        self._write_resource_state_file(new_resource_state, filename)

        return new_resource_state.uuid


    def delete_resource_state(self, resource_state_uuid: str):
        if not resource_state_uuid in self._central_state.resource_state_locations:
            raise ResourceStateDoesNotExist

        resource_state_to_delete = self.get_resource_state(resource_state_uuid)

        if resource_state_to_delete.children:
            # Can not delete resource state with children
            raise ResourceStateNotEmpty("Resource state has child resource states")

        
        if not len(resource_state_to_delete.components) == 0:
            # Can not delete a non empty resource state
            raise ResourceStateNotEmpty("Resource state has components")

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


    def get_resource_state(self, resource_state_uuid: str) -> Resource_State:
        if not resource_state_uuid in self._central_state.resource_state_locations:
            raise ResourceStateDoesNotExist

        file_location = self._central_state.resource_state_locations.get(resource_state_uuid)

        if not os.path.isfile(file_location):
            raise CanNotFindResourceStateFile

        try:
            with open(file_location, 'r') as fh:
                return Resource_State(**json.load(fh))

        except Exception as e:
            raise InvalidResourceStateData

    
    def get_top_level_resource_states(self) -> List[Resource_State]:
        rv = []
        
        for resource_id in self._central_state.top_level_states:
            # Let any exception from loading a state pass up to caller
            rv.append(self.get_resource_state(resource_id))

        return rv

    # Components
    def create_component(self, resource_state_uuid: str, component_name: str):
        
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)
        


        if component_name in set(x.name for x in resource_state.components):
            # Cant not have two components of the same name in the same resource state
            raise ComponentAlreadyExists

    
        new_component = ComponentModel(
            component_name
        )

        resource_state.components.append(new_component)

        self._write_resource_state_file(resource_state, resource_state_file_location)


    def delete_component(self, resource_state_uuid: str, component_name: str):
        
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)
        
        if not component_name in set(x.name for x in resource_state.components):
            # Component of that name does not exists
            raise ComponentDoesNotExist(component_name)

        deleteing_component = next(x for x in resource_state.components if x.name == component_name)

        if not len(deleteing_component.resources) == 0:
            raise ComponentNotEmpty

        resource_state.components = [x for x in resource_state.components if not x.name == component_name]

        self._write_resource_state_file(resource_state, resource_state_file_location)


    def get_component(self, resource_state_uuid: str, component_name: str) -> ComponentModel:

        resource_state = self.get_resource_state(resource_state_uuid)

        if not component_name in set(x.name for x in resource_state.components):
            # Component of that name does not exists
            raise ComponentDoesNotExist(component_name)

    
        return next(x for x in resource_state.components if x.name == component_name)


    # Resource Changes
    def create_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference) -> str:
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)
        
        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise ComponentDoesNotExist


        transaction_token = str(uuid.uuid4())

        resource_state.resource_changes[transaction_token] = (component_name, diff)

        self._write_resource_state_file(resource_state, resource_state_file_location)

        return transaction_token


    def complete_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, cloud_output: Dict=None):
    
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)

        if not transaction_token in resource_state.resource_changes:
            raise ResourceChangeTransactionDoesNotExist

        component = next((x for x in resource_state.components if x.name == component_name), None)

        if not component:
            raise ComponentDoesNotExist

       
        new_component = self._update_component(component, diff, cloud_output)

        resource_state.components = [x for x in resource_state.components if not x.name == component.name] + [new_component]

        resource_state.resource_changes.pop(transaction_token)
        
        self._write_resource_state_file(resource_state, resource_state_file_location)


    def fail_resource_change(self, resource_state_uuid: str, component_name: str, diff: Resource_Difference, transaction_token: str, failed_state: Dict):
        
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)


        if not transaction_token in resource_state.resource_changes:
            raise ResourceChangeTransactionDoesNotExist

        resource_state.resource_changes.pop(transaction_token)
        resource_state.failed_changes[transaction_token] = (component_name, diff, failed_state)

        self._write_resource_state_file(resource_state, resource_state_file_location)


    def change_failed_state_of_resource_change(self, resource_state_uuid: str, transaction_token: str, new_failed_state: Dict):
    
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)

        if not transaction_token in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist

        previous_component_name, previous_diff, _ = resource_state.failed_changes.get(transaction_token)

        resource_state.failed_changes[transaction_token] = (previous_component_name, previous_diff, new_failed_state)

        self._write_resource_state_file(resource_state, resource_state_file_location)

    
    def recover_failed_resource_change(self, resource_state_uuid: str, transaction_token: str, to_previous_state: bool=True, cloud_output: Dict=None):
    
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)

        if not transaction_token in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist


        component_name, diff, _ = resource_state.failed_changes.pop(transaction_token)

        if not to_previous_state:
            component = self.get_component(component_name)

            new_component = self._update_component(component, diff, cloud_output)

            resource_state.components = [x for x in resource_state.components if not x.name == component_name] + [new_component]
        
        
        self._write_resource_state_file(resource_state, resource_state_file_location)


    def remove_failed_resource_change(self, resource_state_uuid: str, transaction_token: str): 
        
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(resource_state_uuid)        

        if not transaction_token in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist


        resource_state.failed_changes.pop(transaction_token)

        self._write_resource_state_file(resource_state, resource_state_file_location)


    # Get resources and cloud output
    def get_resource_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str) -> ResourceModel:

        component = self.get_component(resource_state_uuid, component_name)

        resource =  next((x for x in component.resources if x.ruuid == resource_type and x.name == resource_name), None)

        if not resource:
            raise ResourceDoesNotExist

        return resource


    def get_resource_by_hash(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_hash: str) -> ResourceModel:
        
        component = self.get_component(resource_state_uuid, component_name)

        resource =  next((x for x in component.resources if x.ruuid == resource_type and x.hash == resource_hash), None)

        if not resource:
            raise ResourceDoesNotExist


        return resource

    
    def get_cloud_output_value_by_name(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_name: str, key: str) -> Any:
        
        component = self.get_component(resource_state_uuid, component_name)
        resource = self.get_resource_by_name(resource_state_uuid, component_name, resource_type, resource_name)

        cloud_output_id = self._get_cloud_output_id(resource)

        if not cloud_output_id in component.cloud_output:
            raise CloudOutputDoesNotExist

        cloud_output = component.cloud_output.get(cloud_output_id)

        if not key in cloud_output:
            raise KeyNotInCloudOutput

        return cloud_output.get(key)

    
    def get_cloud_output_value_by_hash(self, resource_state_uuid: str, component_name: str, resource_type: str, resource_hash: str, key: str) -> Any:    
    
        component = self.get_component(resource_state_uuid, component_name)
        resource = self.get_resource_by_hash(resource_state_uuid, component_name, resource_type, resource_hash)

        cloud_output_id = self._get_cloud_output_id(resource)

        if not cloud_output_id in component.cloud_output:
            raise CloudOutputDoesNotExist
    
        cloud_output = component.cloud_output.get(cloud_output_id)

        if not key in cloud_output:
            raise KeyNotInCloudOutput

        return cloud_output.get(key)


    def create_differences(self, resource_state_uuid: str, new_components: List[ComponentModel], old_components: List[str]) -> Tuple[Component_Difference, Resource_Reference_Difference, Resource_Difference]:
        previous_state = self.get_resource_state(resource_state_uuid)
        log.info(f"previous local state -> {previous_state}")

        if not previous_state:
            #raise Cdev_Error(f"no previous local state. Run `cdev init` to solve issue.")
            raise Exception


        try:
            # Load the previous components
            previous_components: List[ComponentModel] = [self.get_component(x) for x in old_components]
        except Exception as e:
            raise e

        return _create_differences(new_components, previous_components)
        

    def _update_component(self, component: ComponentModel, diff: Resource_Difference, cloud_output: Dict=None) -> ComponentModel:
        """
        Apply a resource difference over a component model and return the updated component model

        Arguments:
            component(ComponentModel): The component to update
            diff (Resource_Difference): The difference to apply
            cloud_output (Dict): The updated output if needed

        Returns:
            new_component(ComponentModel): The update component model

        """
        if diff.action_type == Resource_Change_Type.DELETE:
            component.resources = [x for x in component.resources if x.ruuid == diff.previous_resource.ruuid and x.name == diff.previous_resource.name]

            # remove the previous resource's cloud output
            previous_resource_cloud_output_id = self._get_cloud_output_id(diff.previous_resource)

            if previous_resource_cloud_output_id in component.cloud_output:
                cloud_output.pop(previous_resource_cloud_output_id)

        elif diff.action_type == Resource_Change_Type.UPDATE_IDENTITY or diff.action_type == Resource_Change_Type.UPDATE_NAME:
            
            component.resources = [x for x in component.resources if x.ruuid == diff.previous_resource.ruuid and x.name == diff.previous_resource.name].append(diff.new_resource)
            
            # remove the previous resource's cloud output
            previous_resource_cloud_output_id = self._get_cloud_output_id(diff.previous_resource)

            if previous_resource_cloud_output_id in component.cloud_output:
                cloud_output.pop(previous_resource_cloud_output_id)

            # Add the new resources cloud output
            if cloud_output:
                cloud_output_id = self._get_cloud_output_id(diff.new_resource)
                component.cloud_output[cloud_output_id] = cloud_output

        elif diff.action_type == Resource_Change_Type.CREATE:
            component.resources.append(diff.new_resource)
        
            if cloud_output:
                cloud_output_id = self._get_cloud_output_id(diff.new_resource)
                component.cloud_output[cloud_output_id] = cloud_output

        # recompute hash
        component.hash = _compute_component_hash(component)

        return component


    def _get_cloud_output_id(self, resource: ResourceModel) -> str:
        """
        Uniform way of generating cloud mapping id's

        Arguments:
            resource (ResourceModel): resource to get id of

        Returns:
            cloud_output_id (str): id for the resource
        """
        return f"{resource.ruuid};{resource.name}"

    
    def _get_resource_state_file_location(self, resource_state_uuid: str) -> FilePath:
        return self._central_state.resource_state_locations.get(resource_state_uuid)


# Helper functions
def _compute_component_hash(component: ComponentModel) -> str:
        """
        Uniform way of computing a component's identity hash

        Argument:
            component (ComponentModel): The component to compute the hash of

        Returns:
            hash (str): identity hash for the component
        """
        resources = [x for x in component.resources]
        resources.sort(key=lambda x: x.name)

        resource_hashes = [x.hash for x in resources]


        references = [x for x in component.references]
        references.sort(key=lambda x: x.hash)

        references_hashes = [x.hash for x in references]

        all_hashes = references_hashes + resource_hashes

        return cdev_hasher.hash_list(all_hashes)


def _create_resource_diffs(new_resources: List[ResourceModel], old_resource: List[ResourceModel]) -> List[Resource_Difference]:
    
    if old_resource:
        # build map<hash,resource>
        old_hash_to_resource: Dict[str, ResourceModel] = {x.hash: x for x in old_resource}
        # build map<name,resource>
        old_name_to_resource: Dict[str, ResourceModel] = {x.name: x for x in old_resource}
    else:
        old_hash_to_resource = {}
        old_name_to_resource = {}

    log.debug(f"old_hash_to_resource -> {old_hash_to_resource}")
    log.debug(f"old_name_to_resource -> {old_name_to_resource}")

    rv = []
    for resource in new_resources:
        if resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            
            log.info(f"same resource diff {old_hash_to_resource.get(resource.hash).name}")
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))
            continue

        elif resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            print(f"update resource diff {old_hash_to_resource.get(resource.hash)} name {old_hash_to_resource.get(resource.hash).name} -> {resource.name}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.UPDATE_NAME,
                    "previous_resource": old_hash_to_resource.get(resource.hash),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))

        elif not resource.hash in old_hash_to_resource and resource.name in old_name_to_resource:
            log.info(f"update resource diff {old_name_to_resource.get(resource.name)} hash {old_name_to_resource.get(resource.name).hash} -> {resource.hash}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.UPDATE_IDENTITY,
                    "previous_resource": old_name_to_resource.get(resource.name),
                    "new_resource": resource
                }
            ))
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_name_to_resource.get(resource.name))

        elif not resource.hash in old_hash_to_resource and not resource.name in old_name_to_resource:
            log.info(f"create resource diff {resource}")
            rv.append(Resource_Difference(
                **{
                    "action_type": Resource_Change_Type.CREATE,
                    "previous_resource": None,
                    "new_resource": resource
                }
            ))

    if old_resource:
        for resource in old_resource:
            log.info(f"delete resource diff {resource}")
            rv.append(Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.DELETE,
                        "previous_resource": resource,
                        "new_resource": None
                    }
                )
            )

    return rv


def _create_reference_diffs(new_references: List[ResourceReferenceModel], old_references: List[ResourceReferenceModel]) -> List[Resource_Reference_Difference]:
    
    if old_references:
        # build map<name,resource>
        old_name_to_references: Dict[str, ResourceReferenceModel] = {x.hash: x for x in old_references}
    else:
        old_name_to_references = {}

    log.debug(f"old_name_to_resource -> {old_name_to_references}")

    rv = []
    for reference in new_references:
       
        if reference.hash in old_name_to_references:
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_references.remove(old_name_to_references.get(reference.hash))
            
        else:
            rv.append(
                Resource_Reference_Difference(
                    Resource_Reference_Change_Type.CREATE,
                    reference
                )
            )

    for old_reference in old_references:
        log.info(f"delete resource diff {old_reference}")
        rv.append(
            Resource_Reference_Difference(
                Resource_Reference_Change_Type.DELETE,
                old_reference
            )
        )

    return rv


def _create_differences(new_components: List[ComponentModel], previous_components: List[ComponentModel]) -> Tuple[Component_Difference, Resource_Reference_Difference, Resource_Difference]:
    
    component_diffs = []
    resource_diffs = []
    reference_diffs = []

    if previous_components:
        # build map<hash,resource>
        previous_hash_to_component = {x.hash: x for x in previous_components}
        # build map<name,resource>
        previous_name_to_component = {x.name: x for x in previous_components}
        previous_components_to_remove = [x for x in previous_components]
    else:
        previous_hash_to_component = {}
        previous_name_to_component = {}
        previous_components_to_remove = []

    log.debug(f"previous_hash_to_component -> {previous_hash_to_component}")
    log.debug(f"previous_name_to_component -> {previous_name_to_component}")


    if new_components:
        for component in new_components:

            if not component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
                # Create component and all resources and all references 
                log.info(f"CREATE COMPONENT -> {component.name}")
                component_diffs.append( 
                    Component_Difference(
                        Component_Change_Type.CREATE,
                        new_name=component.name
                    )
                )

                tmp_resource_diff = _create_resource_diffs(component.resources,[])
                resource_diffs.extend( tmp_resource_diff )

                tmp_reference_diff = _create_reference_diffs(component.references, [])
                reference_diffs.extend(tmp_reference_diff)
                        

            elif component.hash in previous_hash_to_component and component.name in previous_name_to_component:
                # Since the hash is the same we can infer all the resource hashes and reference hashes are the same
                # Even though the hash has remained the same we need to check for name changes in the resources

                previous_component = previous_name_to_component.get(component.name)

                # Should only output resource name changes
                tmp_resource_diff = _create_resource_diffs(component.resources, previous_component.resources)

                if any([not x.action_type == Resource_Change_Type.UPDATE_NAME for x in tmp_resource_diff]):
                    # if there is a resource change that is not an update name raise an exception
                    raise Exception

                resource_diffs.extend(tmp_resource_diff)

                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)

            elif component.hash in previous_hash_to_component and not component.name in previous_name_to_component:
                # hash of the component has stayed the same but the user has renamed the component name
                # Even though the hash has remained the same we need to check for name changes in the resources
                previous_component = previous_hash_to_component.get(component.hash)

                component_diffs.append(
                    Component_Difference(
                        Component_Change_Type.UPDATE_NAME,
                        previous_name=previous_component.name,
                        new_name=component.name
                    )
                )

                # Should only output resource name changes
                tmp_resource_diff = _create_resource_diffs(component.resources, previous_component.resources)

                if any([not x.action_type == Resource_Change_Type.UPDATE_NAME for x in tmp_resource_diff]):
                    # if there is a resource change that is not an update name raise an exception
                    raise Exception

                resource_diffs.extend(tmp_resource_diff)


                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)

            elif not component.hash in previous_hash_to_component and component.name in previous_name_to_component:
                # hash of the component has changed but not the name
                # This means a resource or reference has updated its identity hash
                previous_component = previous_name_to_component.get(component.name)

                tmp_resource_diff = _create_resource_diffs(component.resources, previous_component.resources)
                resource_diffs.extend(tmp_resource_diff)

                tmp_reference_diff = _create_reference_diffs(component.references, previous_component.references)
                reference_diffs.extend(tmp_reference_diff)

            
                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)


    
    for removed_component in previous_components_to_remove:

        component_diffs.append(
            Component_Difference(
                Component_Change_Type.DELETE,
                previous_name=removed_component.name,
            )
        )

        tmp_resource_diff = _create_resource_diffs([], removed_component.resources)
        resource_diffs.extend(tmp_resource_diff)


        tmp_reference_diff = _create_reference_diffs([], removed_component.references)
        reference_diffs.extend(tmp_reference_diff)


    return component_diffs, reference_diffs, resource_diffs
