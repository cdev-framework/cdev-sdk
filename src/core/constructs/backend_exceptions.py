from dataclasses import dataclass, field
from typing import List

from core.utils.exceptions import cdev_core_error


@dataclass
class BackendError(cdev_core_error):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceStateAlreadyExists(BackendError):
    help_message: str = "   Try creating the resource state with a different name"
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceStateDoesNotExist(BackendError):
    help_message: str = "   Make sure the Resource State Exists."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceStateNotEmpty(BackendError):
    help_message: str = "   You must delete all Resources, References, and Components in the Resource State before completing this action."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ComponentAlreadyExists(BackendError):
    help_message: str = "   Try creating the resource state with a different name"
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ComponentDoesNotExist(BackendError):
    help_message: str = "   Make sure the Component Exists."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ComponentNotEmpty(BackendError):
    help_message: str = "   You must delete all Resources and References in the Resource State before completing this action."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceChangeTransactionDoesNotExist(BackendError):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceDoesNotExist(BackendError):
    help_message: str = "   Make sure you typed the resource name, component name, and resource type correctly."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class CloudOutputDoesNotExist(BackendError):
    help_message: str = "   Make sure you typed the resource name, component name, and resource type correctly."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class KeyNotInCloudOutput(BackendError):
    help_message: str = "   Make sure you typed the key correctly."
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ResourceReferenceError(BackendError):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])
