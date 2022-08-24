"""Definition of the functionality of a Backend within the framework

A Backend is designed to be the single central place for persistent storage within the framework. It is responsible
for managing all changes within the state of a project. The backend touches almost all other primitives within
the framework. To gain a better understanding of its larger role with the framework, refer to the documentation
about the design of the framework (link).

This file provides the definition of the functionality a backend should implement, but it does not provide
a concrete implementation.

This file also contains the definition of how to configure and dynamically load a backend class. To denote a
concrete implementation, a python `module` and `class` must be provide. These should both be strings. They are
used to load a class that inherits from the base `Backend` class. It also takes in a generic dictionary to be
passed as configuration into the dynamically loaded class.

"""
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any, List
from pydantic import BaseModel

from core.constructs.components import Component_Difference, ComponentModel
from core.constructs.resource import (
    Resource_Reference_Difference,
    ResourceModel,
    Resource_Difference,
)
from core.constructs.resource_state import Resource_State

from core.utils.module_loader import import_class, ImportClassError, ImportModuleError
from core.utils.exceptions import cdev_core_error


###############################
##### Exceptions
###############################


@dataclass
class BackendError(cdev_core_error):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class BackendInitializationError(BackendError):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### API
###############################


class Backend_Configuration(BaseModel):
    python_module: str
    python_class: str
    config: Dict

    def __init__(
        __pydantic_self__, python_module: str, python_class: str, config: Dict
    ) -> None:
        """
        Represents the data needed to create a new cdev backend:

        Parameters:
            python_module: The name of the python module to load as the backend
            config: configuration option for the backend

        """

        super().__init__(
            **{
                "python_module": python_module,
                "python_class": python_class,
                "config": config,
            }
        )


class Backend:
    def __init__(self, **kwargs) -> None:
        raise NotImplementedError

    # Api for working with Resource States
    def create_resource_state(
        self, name: str, parent_resource_state_uuid: str = None
    ) -> str:
        """
        Create a new resource state within this stored state.

        Args:
            parent_resource_state_uuid (str): The uuid of the parent resource state.
            name (str): the name of this resource state.

        Returns:
            uuid (str): The uuid of the newly created resource state.

        Raises:
            ResourceStateAlreadyExists

        """
        raise NotImplementedError

    def delete_resource_state(self, resource_state_uuid: str) -> None:
        """
        Delete a resource state within this store state.

        Args:
            resource_state_uuid (str): The uuid of the resource state to delete

        Raises:
            ResourceStateDoesNotExist
            ResourceStateNotEmpty
        """
        raise NotImplementedError

    def get_resource_state(self, resource_state_uuid: str) -> Resource_State:
        """
        Load a resource state from the stored state.

        Args:
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

    def get_component(
        self, resource_state_uuid: str, component_name: str
    ) -> ComponentModel:
        """
        Get a component from the resource state.

        Args:
            resource_state_uuid (str): The resource state that this component will be in.
            component_name (str): Name of the component

        Returns:
            component (ComponentModel): The data for the requested component

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
        """
        raise NotImplementedError

    def update_component(
        self, resource_state_uuid: str, component_difference: Component_Difference
    ) -> None:
        """Make an update to the component.

        Args:
            resource_state_uuid (str): The resource state that the change is in.
            component_difference (Component_Difference): The difference in the component to be made.

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
        """
        pass

    def get_component_uuid(self, resource_state_uuid: str, component_name: str) -> str:
        """
        Get the unique namespace for this resource state and component.

        Args:
            resource_state_uuid (str): The resource state that this component will be in.
            component_name (str): Name of the component

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist

        Returns:
            identifier (str): A unique identifier for this namespace
        """

    # Api for changing individual Resources
    # The resource state needs to know when a mapper will be attempting to update a cdev resource. It is in charge of
    # determing if the current resource state is capable of handling a change in the resource.
    def create_resource_change_transaction(
        self, resource_state_uuid: str, component_name: str, diff: Resource_Difference
    ) -> Tuple[str, str]:
        """
        Create in the Resource State the desire to change a particular resource. If the resource state can currently handle creating
        this change, it will return a base idempotency token that can be used to construct idempotency tokens for deploying the underlying
        cloud resources. If the resource state can not handle the change, it will throw an error.

        Args:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource.

        Returns:
            transaction_token (str): The transaction token to be used by the mapper when deploying the resource. This token can be used to give to a cloud
            provider as a idempotency token.
            namespace_token (str): A suffix that can be added to deployed cloud resources that acts as a namespace for the resource within the cloud.

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
        """
        raise NotImplementedError

    def complete_resource_change(
        self,
        resource_state_uuid: str,
        component_name: str,
        diff: Resource_Difference,
        transaction_token: str,
        cloud_output: Dict,
        resolved_cloud_information: Dict = {},
    ) -> None:
        """
        Notify the resource state that all changes to a resource have completed successfully. This will cause the resource to
        update the state of the resource to the new state.

        Args:
            resource_state_uuid (str): The resource state for this resource change.
            component_name (str): The component this resource change is occuring in.
            diff (Resource_Difference): The desired change in the resource
            transaction_token (str): Identifying token representing what transaction is being completed
            cloud_output (Dict): Output information from the cloud provider
            resolved_cloud_information (Dict): Information that was resolved from the cloud output of the component to deploy this change.


        Raises:
            ResourceChangeTransactionDoesNotExist
            ComponentDoesNotExist

        """
        raise NotImplementedError

    def fail_resource_change(
        self,
        resource_state_uuid: str,
        component_name: str,
        diff: Resource_Difference,
        transaction_token: str,
        failed_state: Dict,
    ) -> None:
        """
        Notify the resource state that an attempted change to a resource has failed. The provided failed state should encapsulate any needed information
        for a future mapper to recover the state of the resource back into a proper state.

        Args:
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
    def resolve_reference_change(
        self,
        resource_state_uuid: str,
        diff: Resource_Reference_Difference,
    ) -> None:
        """
        Either reference or dereference a resource from a different component.

        Args:
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
    def change_failed_state_of_resource_change(
        self, resource_state_uuid: str, transaction_token: str, new_failed_state: Dict
    ) -> None:
        """
        Update the failed state of a 'resource change'.

        Args:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.
            new_failed_state (Dict): The new failed state of the transaction.

        Raises:
            ResourceStateDoesNotExist
            ResourceChangeTransactionDoesNotExist

        """
        raise NotImplementedError

    def recover_failed_resource_change(
        self,
        resource_state_uuid: str,
        transaction_token: str,
        to_previous_state: bool = True,
    ) -> None:
        """
        Recover the state of the change back to the previous state or forward to the new state. Note this will result in the failed resource change being removed from the stored state.

        Args:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.
            to_previous_state (bool): Bool to decide if the resource should be transitioned to the previous state or new state.

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
            ResourceChangeTransactionDoesNotExist
        """
        raise NotImplementedError

    def remove_failed_resource_change(
        self, resource_state_uuid: str, transaction_token: str
    ) -> None:
        """
        Completely remove the failed resource change from the stored state. Note that this should be used with caution as it can lead to hanging cloud resources.

        Args:
            resource_state_uuid (str): The resource state that this transaction is in.
            transaction_token (str): Identifying token for the failed transaction.

        Raises:
            ResourceStateDoesNotExist
            ResourceChangeTransactionDoesNotExist
        """
        raise NotImplementedError

    # Api for getting information about a resource from the backend
    def get_resource_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
    ) -> ResourceModel:
        """
        Get the state of a resource from a component based on the name of the resource

        Args:
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

    def get_resource_by_hash(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_hash: str,
    ) -> ResourceModel:
        """
        Get the state of a resource from a component based on the hash of the resource

        Args:
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

    # Api for getting a set of resources that match the given tag from the backend
    def get_resources_by_tag(
            self,
            resource_state_uuid: str,
            component_name: str,
            resource_type: str,
            resource_tag: str,
    ) -> List[ResourceModel]:
        """
        Get the state of a resource from a component based on the name of the resource

        Args:
            resource_state_uuid (str): The resource state for this resource.
            component_name (str): The component this resource is in.
            resource_type: The RUUID of the resource desired
            resource_tag: The tag of the resources desired

        Raises:
            ResourceStateDoesNotExist
            ComponentDoesNotExist
            ResourceDoesNotExist
        """
        raise NotImplementedError

    def get_cloud_output_value_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
        key: str,
    ) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information.

        Args:
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

    def get_cloud_output_by_name(
        self,
        resource_state_uuid: str,
        component_name: str,
        resource_type: str,
        resource_name: str,
    ) -> Dict:
        """
        Get full output from the cloud provider for a resource by the name of the resource.

        Args:
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

    def get_cloud_output_value_by_hash(
        self,
        resource_state_uuid: str,
        component_uuid: str,
        resource_type: str,
        resource_hash: str,
        key: str,
    ) -> Any:
        """
        Get an output value from the cloud provider for a resource by the name of the resource. This function also takes an optional function as a parameter
        that will be executed on the output and should return a transformed version of the information.

        Args:
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
        """
        Create the set of differences from a proposed set of components to a provided set of current components identified by their name. This allows the flexibility for working on a particular
        set of components within a resource state.
        """
        raise NotImplementedError


def load_backend(config: Backend_Configuration) -> Backend:
    """Dynamically load a backend

    Load a backend by initializing the provided module and looking for the class within the loaded module.

    Args:
        config (Backend_Configuration): configuration of what backend to load.

    Raises:
        Exception: [description]

    Returns:
        Backend: [description]
    """
    try:
        backend_class = import_class(config.python_module, config.python_class)
    except ImportClassError as e:
        raise BackendInitializationError(
            error_message=f"""When loading '{config.python_class}' from '{config.python_module}' as the settings base class the following exception occurred:
            {e.error_message}
            """
        )
    except ImportModuleError as e:
        raise BackendInitializationError(
            error_message=f"""When loading '{config.python_module}' to load the base settings class ('{config.python_class}') the following exception occurred:
            {e.error_message}
            """
        )

    try:
        # initialize the backend obj with the provided configuration values
        initialized_obj = backend_class(**config.config)
    except Exception as e:
        raise BackendInitializationError(
            error_message=f"""When Initializing Backend ('{config.python_module}.{config.python_class}') with Configuration {config.config}, an error occurred:
            {e}
            """
        )

    return initialized_obj
