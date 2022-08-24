import copy
import json
import os

from pydantic.main import BaseModel
from pydantic.types import DirectoryPath, FilePath

from typing import Dict, List, Any, Tuple
import uuid


from core.constructs.backend import Backend_Configuration, Backend
from core.constructs.backend_exceptions import *

from core.constructs.components import (
    Component_Change_Type,
    ComponentModel,
    Component_Difference,
)
from core.constructs.resource import (
    Resource_Change_Type,
    Resource_Difference,
    Resource_Reference_Change_Type,
    ResourceModel,
    Resource_Reference_Difference,
    ResourceReferenceModel,
)
from core.constructs.resource_state import Resource_State
from ..utils import file_manager, hasher as cdev_hasher


class LocalBackendError(BackendError):
    pass


class CanNotFindResourceStateFile(LocalBackendError):
    pass


class InvalidResourceStateData(LocalBackendError):
    pass


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Local_Backend_Configuration(Backend_Configuration):
    def __init__(self, config: Dict) -> None:
        """Represents the data needed to create a new cdev workspace:

        Args:
            python_module: The name of the python module to load as the backend
            config: configuration option for the backend

        """

        super().__init__(
            **{
                "python_module": "core.default.backend",
                "python_class": "LocalBackend",
                "config": config,
            }
        )


class CentralState(BaseModel):
    resource_state_locations: Dict[str, str]  # uuid -> file location
    top_level_states: List[str]  # uuid
    resource_state_names: List[str]

    def __init__(
        __pydantic_self__,
        resource_state_locations: Dict[str, str],
        top_level_states: List[str],
        resource_state_names: List[str],
    ) -> None:
        super().__init__(
            **{
                "resource_state_locations": resource_state_locations,
                "top_level_states": top_level_states,
                "resource_state_names": resource_state_names,
            }
        )


class LocalBackend(Backend):
    # This implementation uses local json files to store the different states. Each Resource State will be store in a different json files to help with diffing them using git.
    # note the __init__ function allows any kwargs to preserve backwards compatibility with previous implementations.
    def __init__(self, base_folder: DirectoryPath, *args, **kwargs) -> None:
        """This implementation uses local json files to store the different states. Each Resource State will be store in a different json files to help with diffing them using git.

        Args:
            base_folder (DirectoryPath): Path to a folder to use for storing local json files. Defaults to cdev setting if not provided.
        """

        self.base_folder = base_folder
        self._resource_state_prefix = "resource_state_"

        if not os.path.isdir(self.base_folder):
            raise FileNotFoundError(f"Can not find directory -> {self.base_folder}")

        self._central_state = self._compute_central_state()

    def _compute_resource_state_file_location(
        self, resource_state_uuid: str
    ) -> FilePath:
        """Helper function to uniformly compute the resource state file name

        Args:
            resource_state_uuid (str)

        Returns:
            FilePath
        """

        return os.path.join(
            self.base_folder, f"{self._resource_state_prefix}{resource_state_uuid}.json"
        )

    def _compute_central_state(self) -> CentralState:
        resource_state_locations = {}
        top_level_states = []
        resource_state_names = []

        for child in os.listdir(self.base_folder):
            full_path = os.path.join(self.base_folder, child)
            if not (
                child.startswith(self._resource_state_prefix)
                and os.path.isfile(full_path)
            ):
                continue

            try:
                rs = Resource_State(**json.load(open(full_path)))
            except Exception:
                continue

            resource_state_locations[rs.uuid] = full_path
            top_level_states.append(rs.uuid)
            resource_state_names.append(rs.name)

        return CentralState(
            resource_state_locations=resource_state_locations,
            top_level_states=top_level_states,
            resource_state_names=resource_state_names,
        )

    def _write_resource_state_file(self, resource_state: Resource_State, fp: FilePath):
        """Save the resource state to disk

        Args:
            resource_state (Resource_State)
            fp (FilePath)
        """
        file_manager.safe_json_write(resource_state.dict(), fp)

    # Api for working with Resource States
    def create_resource_state(
        self, name: str, parent_resource_state_uuid: str = None
    ) -> str:
        # Create the new resource state
        if name in set(self._central_state.resource_state_names):
            raise ResourceStateAlreadyExists("Creating resource state with taken name")

        resource_state_uuid = str(uuid.uuid4())
        if not parent_resource_state_uuid:
            # Create this as a top level resource state
            new_resource_state = Resource_State(name, resource_state_uuid)
            self._central_state.top_level_states.append(new_resource_state.uuid)

        else:
            new_resource_state = Resource_State(
                name=name,
                uuid=resource_state_uuid,
                components=[],
                parent_uuid=parent_resource_state_uuid,
            )

        filename = self._compute_resource_state_file_location(new_resource_state.uuid)

        self._central_state.resource_state_locations[new_resource_state.uuid] = filename
        self._central_state.resource_state_names.append(new_resource_state.name)

        self._write_resource_state_file(new_resource_state, filename)

        return new_resource_state.uuid

    def delete_resource_state(self, resource_state_uuid: str) -> None:
        if resource_state_uuid not in self._central_state.resource_state_locations:
            raise ResourceStateDoesNotExist(
                f"Resource state: {resource_state_uuid} does not exist"
            )

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
        file_location = self._central_state.resource_state_locations.pop(
            resource_state_to_delete.uuid
        )

        os.remove(file_location)

    def get_resource_state(self, resource_state_uuid: str) -> Resource_State:
        if resource_state_uuid not in self._central_state.resource_state_locations:
            raise ResourceStateDoesNotExist(
                f"Resource State: {resource_state_uuid} does not exists"
            )

        file_location = self._central_state.resource_state_locations.get(
            resource_state_uuid
        )

        if not os.path.isfile(file_location):
            raise CanNotFindResourceStateFile(
                f"Can not find resource state file for {resource_state_uuid}"
            )

        try:
            return file_manager.load_resource_state(file_location)

        except Exception as e:
            raise InvalidResourceStateData(
                f"Invalid data for Resource State from file {file_location} for resource state {resource_state_uuid}; {e}"
            )

    def get_top_level_resource_states(self) -> List[Resource_State]:
        # Let any exception from loading a state pass up to caller
        rv = [
            self.get_resource_state(resource_id)
            for resource_id in self._central_state.top_level_states
        ]
        return rv

    # Components
    def _create_component(self, resource_state_uuid: str, component_name: str) -> None:
        """Create a component with the provide name in provided the resource state

        Args:
            resource_state_uuid (str)
            component_name (str)

        Raises:
            ComponentAlreadyExists
        """
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if component_name in set(x.name for x in resource_state.components):
            # Can't have two components of the same name in the same resource state
            raise ComponentAlreadyExists(
                f"Component already exists with name {component_name} in Resource State {resource_state_uuid}"
            )

        # Create the new component
        new_component = ComponentModel(component_name)
        resource_state.components.append(new_component)

        # Create a uuid for the component
        component_uuid = str(uuid.uuid4())
        resource_state.component_name_to_uuid[component_name] = component_uuid

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def _delete_component(self, resource_state_uuid: str, component_name: str) -> None:
        """Delete the component by name in a provided resource state

        Args:
            resource_state_uuid (str)
            component_name (str)

        Raises:
            ComponentDoesNotExist
            ComponentNotEmpty
        """
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        deleting_component = None
        for component in resource_state.components:
            if component.name == component_name:
                deleting_component = component
                break

        if not deleting_component:
            # Component of that name does not exist
            raise ComponentDoesNotExist(
                f"Could not find component {component_name} in Resource State {resource_state_uuid}"
            )

        if len(deleting_component.resources) != 0:
            raise ComponentNotEmpty(
                f"Can not delete Component {component_name} in Resource State {resource_state_uuid} because the component is not empty"
            )

        resource_state.components.remove(deleting_component)
        resource_state.component_name_to_uuid.pop(component_name)

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def _update_component_name(
        self,
        resource_state_uuid: str,
        previous_component_name: str,
        new_component_name: str,
    ) -> None:
        """Update the component by name

        Args:
            resource_state_uuid (str)
            previous_component_name (str)
            new_component_name (str)

        Raises:
            ComponentDoesNotExist
            ComponentAlreadyExists
        """
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if (
            previous_component_name
            not in set(x.name for x in resource_state.components)
            or previous_component_name not in resource_state.component_name_to_uuid
        ):
            # Component of that name does not exists
            raise ComponentDoesNotExist(
                f"Could not find component {previous_component_name} in Resource State {resource_state_uuid}"
            )

        if (
            new_component_name in set(x.name for x in resource_state.components)
            or new_component_name in resource_state.component_name_to_uuid
        ):
            # Cant not have two components of the same name in the same resource state
            raise ComponentAlreadyExists(
                f"Component already exists with name {new_component_name} in Resource State {resource_state_uuid}"
            )

        # get the component to rename
        rename_component = next(
            x for x in resource_state.components if x.name == previous_component_name
        )

        # remove the component from the list of components
        resource_state.components.remove(rename_component)

        # Since ComponentModels are frozen, we can just change the name
        # So we make a dict of the current ComponentModel then change the name and use the dict as input
        # for a new ComponentModel Obj. Then add the new Obj to the resource state
        component_as_dict = rename_component.dict()
        component_as_dict["name"] = new_component_name
        new_component = ComponentModel(**component_as_dict)

        resource_state.components.append(new_component)

        # Update the name to uuid dict
        resource_state.component_name_to_uuid.pop(previous_component_name)
        # ANIBAL IS THIS RIGHT, it is expecting str and we are setting it to ComponentModel
        resource_state.component_name_to_uuid[new_component_name] = new_component

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def get_component(
        self, resource_state_uuid: str, component_name: str
    ) -> ComponentModel:
        resource_state = self.get_resource_state(resource_state_uuid)

        for component in resource_state.components:
            if component.name == component_name:
                return component

        # Component of that name does not exists
        raise ComponentDoesNotExist(
            f"Can not find Component {component_name} in Resource State {resource_state_uuid}"
        )

    def get_component_uuid(self, resource_state_uuid: str, component_name: str) -> str:
        resource_state = self.get_resource_state(resource_state_uuid)

        if component_name not in resource_state.component_name_to_uuid:
            raise ComponentDoesNotExist(
                f"Can not find Component {component_name} in Resource State {resource_state_uuid}"
            )

        component_uuid = resource_state.component_name_to_uuid.get(component_name)

        return cdev_hasher.hash_list([resource_state_uuid, component_uuid])

    def update_component(
        self, resource_state_uuid: str, component_difference: Component_Difference
    ) -> None:
        if component_difference.action_type == Component_Change_Type.CREATE:
            self._create_component(resource_state_uuid, component_difference.new_name)
            return

        elif component_difference.action_type == Component_Change_Type.DELETE:
            self._delete_component(
                resource_state_uuid, component_difference.previous_name
            )
            return

        elif component_difference.action_type == Component_Change_Type.UPDATE_IDENTITY:
            return

        elif component_difference.action_type == Component_Change_Type.UPDATE_NAME:
            self._update_component_name(
                resource_state_uuid,
                component_difference.previous_name,
                component_difference.new_name,
            )

        else:
            raise Exception(
                f"Component Action type not supported {component_difference.action_type}"
            )

    def create_resource_change_transaction(
        self, resource_state_uuid: str, component_name: str, diff: Resource_Difference
    ) -> Tuple[str, str]:
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        ruuid = (
            diff.new_resource.ruuid
            if diff.new_resource
            else diff.previous_resource.ruuid
        )

        namespace_token = cdev_hasher.hash_list(
            [
                resource_state_uuid,
                self.get_component_uuid(resource_state_uuid, component_name),
                ruuid,
            ]
        )

        transaction_token = str(uuid.uuid4())
        resource_state.resource_changes[transaction_token] = (component_name, diff)

        self._write_resource_state_file(resource_state, resource_state_file_location)

        return transaction_token, namespace_token

    def complete_resource_change(
        self,
        resource_state_uuid: str,
        component_name: str,
        diff: Resource_Difference,
        transaction_token: str,
        cloud_output: Dict = None,
        resolved_cloud_information: Dict = {},
    ) -> None:

        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if transaction_token not in resource_state.resource_changes:
            raise ResourceChangeTransactionDoesNotExist(
                f"Transaction {transaction_token} does not exist in Resource State {resource_state_uuid}"
            )

        component = self.get_component(resource_state_uuid, component_name)

        new_component = self._update_component(
            component, diff, cloud_output, resolved_cloud_information
        )

        resource_state.components = [
            x for x in resource_state.components if x.name != component.name
        ] + [new_component]

        resource_state.resource_changes.pop(transaction_token)

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def fail_resource_change(
        self,
        resource_state_uuid: str,
        component_name: str,
        diff: Resource_Difference,
        transaction_token: str,
        failed_state: Dict,
    ) -> None:

        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if transaction_token not in resource_state.resource_changes:
            raise ResourceChangeTransactionDoesNotExist(
                f"Transaction {transaction_token} does not exist in Resource State {resource_state_uuid}"
            )

        resource_state.resource_changes.pop(transaction_token)
        resource_state.failed_changes[transaction_token] = (
            component_name,
            diff,
            failed_state,
        )

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def change_failed_state_of_resource_change(
        self, resource_state_uuid: str, transaction_token: str, new_failed_state: Dict
    ) -> None:

        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if transaction_token not in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist(
                f"Transaction {transaction_token} does not exist in Resource State {resource_state_uuid}"
            )

        previous_component_name, previous_diff, _ = resource_state.failed_changes.get(
            transaction_token
        )

        resource_state.failed_changes[transaction_token] = (
            previous_component_name,
            previous_diff,
            new_failed_state,
        )

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def recover_failed_resource_change(
        self,
        resource_state_uuid: str,
        transaction_token: str,
        to_previous_state: bool = True,
        cloud_output: Dict = None,
    ) -> None:

        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if transaction_token not in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist(
                f"Transaction {transaction_token} does not exist in Resource State {resource_state_uuid}"
            )

        component_name, diff, _ = resource_state.failed_changes.pop(transaction_token)

        if not to_previous_state:
            # ANIBAL THIS METHOD IS WRONG
            component = self.get_component(component_name)

            new_component = self._update_component(component, diff, cloud_output)

            resource_state.components = [
                x for x in resource_state.components if x.name != component_name
            ] + [new_component]

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def remove_failed_resource_change(
        self, resource_state_uuid: str, transaction_token: str
    ) -> None:

        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        if transaction_token not in resource_state.failed_changes:
            raise ResourceChangeTransactionDoesNotExist(
                f"Transaction {transaction_token} does not exist in Resource State {resource_state_uuid}"
            )

        resource_state.failed_changes.pop(transaction_token)

        self._write_resource_state_file(resource_state, resource_state_file_location)

    def resolve_reference_change(
        self,
        resource_state_uuid: str,
        diff: Resource_Reference_Difference,
    ) -> None:
        resource_state = self.get_resource_state(resource_state_uuid)
        resource_state_file_location = self._get_resource_state_file_location(
            resource_state_uuid
        )

        component = self.get_component(
            resource_state_uuid, diff.originating_component_name
        )

        _reference_resource_state = resource_state
        if diff.resource_reference.is_in_parent_resource_state:
            if not resource_state.parent_uuid:
                raise ResourceReferenceError(
                    f"Current Resource State {resource_state_uuid} does not have a Parent Resource State to resolve {diff} to"
                )

            _reference_resource_state = self.get_resource_state(
                resource_state.parent_uuid
            )

        try:
            _referenced_component = self.get_component(
                _reference_resource_state.uuid, diff.resource_reference.component_name
            )
        except ComponentDoesNotExist:
            raise ResourceReferenceError(
                f"Resource State {_reference_resource_state.uuid} does not contain component {diff.resource_reference.component_name} for {diff}"
            )

        all_parent_resources = set(
            [f"{x.ruuid}{x.name}" for x in _referenced_component.resources]
        )

        if (
            f"{diff.resource_reference.ruuid}{diff.resource_reference.name}"
            not in all_parent_resources
        ):
            raise ResourceReferenceError(
                f"Could not find resource {diff.resource_reference.ruuid};{diff.resource_reference.name} in parent component"
            )

        if diff.action_type == Resource_Reference_Change_Type.CREATE:

            reference_id = (
                f"{diff.resource_reference.ruuid}{diff.resource_reference.name}"
            )

            # resolve the reference by adding a count to the reference counter in the referenced component
            if reference_id not in _referenced_component.external_references:
                _referenced_component.external_references[reference_id] = {"cnt": 1}

            else:
                previous_cnt = _referenced_component.external_references[
                    reference_id
                ].get("cnt")
                _referenced_component.external_references[reference_id] = {
                    "cnt": previous_cnt + 1
                }

            # Add this to the references for this component
            component.references.append(diff.resource_reference)

        elif diff.action_type == Resource_Reference_Change_Type.DELETE:

            reference_id = (
                f"{diff.resource_reference.ruuid}{diff.resource_reference.name}"
            )

            # resolve the dereference by subtracting a count to the reference counter in the referenced component
            if reference_id not in _referenced_component.external_references:
                raise ResourceReferenceError(
                    f"Trying to deference resource that does not have reference info"
                )

            else:
                previous_cnt = _referenced_component.external_references[
                    reference_id
                ].get("cnt")
                _referenced_component.external_references[reference_id] = {
                    "cnt": previous_cnt - 1
                }

            if _referenced_component.external_references[reference_id] == 0:
                _referenced_component.external_references.pop(reference_id)

            # Pop this references for this component
            component.references.remove(diff.resource_reference)

        _reference_resource_state.components = [
            x for x in resource_state.components if x.name != _referenced_component.name
        ] + [_referenced_component]
        resource_state.components = [
            x for x in resource_state.components if x.name != component.name
        ] + [component]

        if diff.resource_reference.is_in_parent_resource_state:
            # if the reference is from the parent resource state then we need to update it so that it knows that the reference was resolved
            _reference_resource_state_fp = self._get_resource_state_file_location(
                _reference_resource_state.uuid
            )

            self._write_resource_state_file(
                _reference_resource_state, _reference_resource_state_fp
            )

        self._write_resource_state_file(resource_state, resource_state_file_location)

    # Get resources and cloud output
    def get_resource_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
    ) -> ResourceModel:
        resource = self._get_resource_by_property(
            resource_state_uuid, component_name, resource_type, "name", resource_name
        )
        return resource

    def get_resource_by_hash(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_hash: str,
    ) -> ResourceModel:
        resource = self._get_resource_by_property(
            resource_state_uuid, component_name, resource_type, "hash", resource_hash
        )
        return resource

    def _get_resource_by_property(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        property_name: str,
        property_value: str,
    ) -> ResourceModel:

        component = self.get_component(resource_state_uuid, component_name)

        for resource in component.resources:
            if (
                resource.ruuid == resource_type
                and getattr(resource, property_name) == property_value
            ):
                return resource

        raise ResourceDoesNotExist(
            f"Resource {resource_type}::{property_value} does not exist in Component {component_name} in Resource State {resource_state_uuid}"
        )

    def get_cloud_output_value_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
        key: str,
    ) -> Any:

        cloud_output_value = self._get_cloud_output_value_by_property(
            resource_state_uuid,
            component_name,
            resource_type,
            "name",
            resource_name,
            key,
        )
        return cloud_output_value

    def get_cloud_output_value_by_hash(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_hash: str,
        key: str,
    ) -> Any:

        cloud_output_value = self._get_cloud_output_value_by_property(
            resource_state_uuid,
            component_name,
            resource_type,
            "hash",
            resource_hash,
            key,
        )
        return cloud_output_value

    def _get_cloud_output_value_by_property(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        property_name: str,
        property_value: str,
        key: str,
    ) -> Any:

        component = self.get_component(resource_state_uuid, component_name)
        resource = self._get_resource_by_property(
            resource_state_uuid,
            component_name,
            resource_type,
            property_name,
            property_value,
        )

        cloud_output_id = self._get_cloud_output_id(resource)

        if cloud_output_id not in component.cloud_output:
            raise CloudOutputDoesNotExist(
                f"Can not find Cloud Output for {resource_type}::{property_value} in Component {component_name} in Resource State {resource_state_uuid}"
            )

        cloud_output = component.cloud_output[cloud_output_id]

        if not cloud_output:
            raise CloudOutputDoesNotExist(
                f"None value for Cloud Output for {resource_type}::{property_value} in Component {component_name} in Resource State {resource_state_uuid}"
            )

        if key not in cloud_output:
            raise KeyNotInCloudOutput(
                f"Can not find Key {key} in Cloud Output for {resource_type}::{property_value} in Component {component_name} in Resource State {resource_state_uuid}"
            )

        return cloud_output.get(key)

    def get_cloud_output_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
    ) -> Any:

        component = self.get_component(resource_state_uuid, component_name)
        resource = self.get_resource_by_name(
            resource_state_uuid, component.name, resource_type, resource_name
        )

        cloud_output_id = self._get_cloud_output_id(resource)

        if cloud_output_id not in component.cloud_output:

            raise CloudOutputDoesNotExist(
                f"Can not find Cloud Output for {resource_type}::{resource_name} in Component {component_name} in Resource State {resource_state_uuid}"
            )

        cloud_output = component.cloud_output.get(cloud_output_id)

        return cloud_output

    def create_differences(
        self,
        resource_state_uuid: str,
        new_components: List[ComponentModel],
        old_components: List[str],
    ) -> Tuple[
        List[Component_Difference],
        List[Resource_Difference],
        List[Resource_Reference_Difference],
    ]:
        try:
            # Load the previous components
            previous_components: List[ComponentModel] = [
                self.get_component(resource_state_uuid, x) for x in old_components
            ]

        except Exception as e:
            raise e

        return _create_differences(new_components, previous_components)

    def _update_component(
        self,
        component: ComponentModel,
        diff: Resource_Difference,
        new_cloud_output: Dict = {},
        resolved_cloud_information: Dict = {},
    ) -> ComponentModel:
        """Apply a resource difference over a component model and return the updated component model

        Args:
            component(ComponentModel): The component to update
            diff (Resource_Difference): The difference to apply
            new_cloud_output (Dict): The updated output if needed
            resolved_cloud_information (Dict): cloud output information used to deploy resource

        Returns:
            new_component(ComponentModel)
        """
        if diff.action_type == Resource_Change_Type.DELETE:

            component.resources = [
                x
                for x in component.resources
                if not (
                    x.ruuid == diff.previous_resource.ruuid
                    and x.name == diff.previous_resource.name
                )
            ]

            # remove the previous resource's cloud output
            previous_resource_cloud_output_id = self._get_cloud_output_id(
                diff.previous_resource
            )

            if previous_resource_cloud_output_id in component.cloud_output:
                component.cloud_output.pop(previous_resource_cloud_output_id)

            if (
                previous_resource_cloud_output_id
                in component.previous_resolved_cloud_values
            ):
                component.previous_resolved_cloud_values.pop(
                    previous_resource_cloud_output_id
                )

        elif (
            diff.action_type == Resource_Change_Type.UPDATE_IDENTITY
            or diff.action_type == Resource_Change_Type.UPDATE_NAME
        ):

            component.resources = [
                x
                for x in component.resources
                if not (
                    x.ruuid == diff.previous_resource.ruuid
                    and x.name == diff.previous_resource.name
                )
            ] + [diff.new_resource]

            # remove the previous resource's cloud output
            previous_resource_cloud_output_id = self._get_cloud_output_id(
                diff.previous_resource
            )

            if previous_resource_cloud_output_id in component.cloud_output:
                component.cloud_output.pop(previous_resource_cloud_output_id)

            if (
                previous_resource_cloud_output_id
                in component.previous_resolved_cloud_values
            ):
                component.previous_resolved_cloud_values.pop(
                    previous_resource_cloud_output_id
                )

            cloud_output_id = self._get_cloud_output_id(diff.new_resource)
            component.cloud_output[cloud_output_id] = new_cloud_output

            component.previous_resolved_cloud_values[
                cloud_output_id
            ] = resolved_cloud_information

        elif diff.action_type == Resource_Change_Type.CREATE:
            component.resources.append(diff.new_resource)

            cloud_output_id = self._get_cloud_output_id(diff.new_resource)

            component.cloud_output[cloud_output_id] = new_cloud_output
            component.previous_resolved_cloud_values[
                cloud_output_id
            ] = resolved_cloud_information

        # recompute hash
        component.hash = _compute_component_hash(component)

        return component

    def _get_cloud_output_id(self, resource: ResourceModel) -> str:
        """Uniform way of generating cloud mapping id's

        Args:
            resource (ResourceModel): resource to get id of

        Returns:
            cloud_output_id (str): id for the resource
        """
        return f"{resource.ruuid};{resource.name}"

    def _get_resource_state_file_location(self, resource_state_uuid: str) -> FilePath:
        return self._central_state.resource_state_locations.get(resource_state_uuid)


# Helper functions
def _compute_component_hash(component: ComponentModel) -> str:
    """Uniform way of computing a component's identity hash

    Args:
        component (ComponentModel): The component to compute the hash of

    Returns:
        hash (str): identity hash for the component
    """
    if component.resources:

        resources = copy.copy(component.resources)
        resources.sort(key=lambda x: x.hash)
        resource_hashes = [x.hash for x in resources]
    else:
        resource_hashes = []

    if component.references:
        # TODO create hash of all the things
        references = copy.copy(component.references)
        references.sort(key=lambda x: x.name)
        references_hashes = [x.name for x in references]
    else:
        references_hashes = []

    all_hashes = references_hashes + resource_hashes
    return cdev_hasher.hash_list(all_hashes)


def _create_resource_diffs(
    component_name: str,
    new_resources: List[ResourceModel],
    old_resource: List[ResourceModel],
) -> List[Resource_Difference]:
    """Create the differences between differences in the resources

    Args:
        component_name (str)
        new_resources (List[ResourceModel]
        old_resource (List[ResourceModel])

    Returns:
        List[Resource_Difference]
    """
    if old_resource:
        # build map<hash,resource>
        old_hash_to_resource: Dict[str, ResourceModel] = {
            x.hash: x for x in old_resource
        }
        # build map<name,resource>
        old_name_to_resource: Dict[str, ResourceModel] = {
            x.name: x for x in old_resource
        }
    else:
        old_hash_to_resource = {}
        old_name_to_resource = {}

    rv = []
    for resource in new_resources:
        if (
            resource.hash in old_hash_to_resource
            and resource.name in old_name_to_resource
        ):

            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))
            continue

        elif (
            resource.hash in old_hash_to_resource
            and resource.name not in old_name_to_resource
        ):

            rv.append(
                Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.UPDATE_NAME,
                        "component_name": component_name,
                        "previous_resource": old_hash_to_resource.get(resource.hash),
                        "new_resource": resource,
                    }
                )
            )
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_hash_to_resource.get(resource.hash))

        elif (
            not resource.hash in old_hash_to_resource
            and resource.name in old_name_to_resource
        ):

            rv.append(
                Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.UPDATE_IDENTITY,
                        "component_name": component_name,
                        "previous_resource": old_name_to_resource.get(resource.name),
                        "new_resource": resource,
                    }
                )
            )
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_resource.remove(old_name_to_resource.get(resource.name))

        elif (
            not resource.hash in old_hash_to_resource
            and resource.name not in old_name_to_resource
        ):

            rv.append(
                Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.CREATE,
                        "component_name": component_name,
                        "previous_resource": None,
                        "new_resource": resource,
                    }
                )
            )

    if old_resource:
        for resource in old_resource:

            rv.append(
                Resource_Difference(
                    **{
                        "action_type": Resource_Change_Type.DELETE,
                        "component_name": component_name,
                        "previous_resource": resource,
                        "new_resource": None,
                    }
                )
            )

    return rv


def _create_reference_diffs(
    new_references: List[ResourceReferenceModel],
    old_references: List[ResourceReferenceModel],
    originating_component_name: str,
) -> List[Resource_Reference_Difference]:
    """Create the differences between components

    Args:
        new_references (List[ResourceReferenceModel])
        old_references (List[ResourceReferenceModel])
        originating_component_name (str)

    Returns:
        List[Resource_Reference_Difference]
    """
    if old_references:
        # build map<name,resource>
        old_name_to_references: Dict[str, ResourceReferenceModel] = {
            f"{x.ruuid};;{x.name}": x for x in old_references
        }
    else:
        old_name_to_references = {}

    rv = []
    for reference in new_references:
        _id = f"{reference.ruuid};;{reference.name}"
        if _id in old_name_to_references:
            # POP the seen previous resources as we go so only remaining resources will be deletes
            old_references.remove(old_name_to_references.get(_id))

        else:
            rv.append(
                Resource_Reference_Difference(
                    Resource_Reference_Change_Type.CREATE,
                    originating_component_name,
                    reference,
                )
            )

    for old_reference in old_references:

        rv.append(
            Resource_Reference_Difference(
                Resource_Reference_Change_Type.DELETE,
                originating_component_name,
                old_reference,
            )
        )

    return rv


def _create_differences(
    new_components: List[ComponentModel], previous_components: List[ComponentModel]
) -> Tuple[
    List[Component_Difference],
    List[Resource_Difference],
    List[Resource_Reference_Difference],
]:
    """Create the differences between components

    Args:
        new_components (List[ComponentModel])
        previous_components (List[ComponentModel])

    Raises:
        Exception

    Returns:
        Tuple[ List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference], ]
    """
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

    if new_components:
        for component in new_components:

            if (
                not component.hash in previous_hash_to_component
                and component.name not in previous_name_to_component
            ):
                # Create component and all resources and all references

                component_diffs.append(
                    Component_Difference(
                        Component_Change_Type.CREATE, new_name=component.name
                    )
                )

                tmp_resource_diff = _create_resource_diffs(
                    component.name, component.resources, []
                )
                resource_diffs.extend(tmp_resource_diff)

                tmp_reference_diff = _create_reference_diffs(
                    component.references, [], component.name
                )
                reference_diffs.extend(tmp_reference_diff)

            elif (
                component.hash in previous_hash_to_component
                and component.name in previous_name_to_component
            ):
                # Since the hash is the same we can infer all the resource hashes and reference hashes are the same
                # Even though the hash has remained the same we need to check for name changes in the resources
                previous_component = previous_name_to_component.get(component.name)

                # Should only output resource name changes
                tmp_resource_diff = _create_resource_diffs(
                    component.name, component.resources, previous_component.resources
                )

                if any(
                    [
                        x.action_type != Resource_Change_Type.UPDATE_NAME
                        for x in tmp_resource_diff
                    ]
                ):
                    # if there is a resource change that is not an update name raise an exception
                    raise Exception

                resource_diffs.extend(tmp_resource_diff)

                component_diffs.append(
                    Component_Difference(
                        Component_Change_Type.UPDATE_IDENTITY,
                        previous_name=previous_component.name,
                        new_name=component.name,
                    )
                )

                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)

            elif (
                component.hash in previous_hash_to_component
                and component.name not in previous_name_to_component
            ):
                # hash of the component has stayed the same but the user has renamed the component name
                # Even though the hash has remained the same we need to check for name changes in the resources
                previous_component = previous_hash_to_component.get(component.hash)

                component_diffs.append(
                    Component_Difference(
                        Component_Change_Type.UPDATE_NAME,
                        previous_name=previous_component.name,
                        new_name=component.name,
                    )
                )

                # Should only output resource name changes
                tmp_resource_diff = _create_resource_diffs(
                    component.name, component.resources, previous_component.resources
                )

                if any(
                    [
                        not x.action_type == Resource_Change_Type.UPDATE_NAME
                        for x in tmp_resource_diff
                    ]
                ):
                    # if there is a resource change that is not an update name raise an exception
                    raise Exception

                resource_diffs.extend(tmp_resource_diff)

                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)

            elif (
                not component.hash in previous_hash_to_component
                and component.name in previous_name_to_component
            ):
                # hash of the component has changed but not the name
                # This means a resource or reference has updated its identity hash
                previous_component = previous_name_to_component.get(component.name)

                tmp_resource_diff = _create_resource_diffs(
                    component.name, component.resources, previous_component.resources
                )
                resource_diffs.extend(tmp_resource_diff)

                tmp_reference_diff = _create_reference_diffs(
                    component.references, previous_component.references, component.name
                )
                reference_diffs.extend(tmp_reference_diff)

                component_diffs.append(
                    Component_Difference(
                        Component_Change_Type.UPDATE_IDENTITY,
                        previous_name=previous_component.name,
                        new_name=component.name,
                    )
                )

                # POP the seen previous component as we go so only remaining resources will be deletes
                previous_components_to_remove.remove(previous_component)

    for removed_component in previous_components_to_remove:

        component_diffs.append(
            Component_Difference(
                Component_Change_Type.DELETE,
                previous_name=removed_component.name,
            )
        )

        tmp_resource_diff = _create_resource_diffs(
            removed_component.name, [], removed_component.resources
        )
        resource_diffs.extend(tmp_resource_diff)

        tmp_reference_diff = _create_reference_diffs(
            [], removed_component.references, removed_component.name
        )
        reference_diffs.extend(tmp_reference_diff)

    return component_diffs, resource_diffs, reference_diffs
