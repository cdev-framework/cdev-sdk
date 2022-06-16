from dataclasses import dataclass, field
from typing import List

from ..utils.exceptions import cdev_core_error


class BackendError(cdev_core_error):
    pass


class ResourceStateAlreadyExists(BackendError):
    pass


class ResourceStateDoesNotExist(BackendError):
    pass


class ResourceStateNotEmpty(BackendError):
    pass


class ComponentAlreadyExists(BackendError):
    pass


class ComponentDoesNotExist(BackendError):
    pass


class ComponentNotEmpty(BackendError):
    pass


class ResourceChangeTransactionDoesNotExist(BackendError):
    pass


@dataclass
class ResourceDoesNotExist(BackendError):
    help_message: str = "Make sure you typed the resource name, component name, and resource type correctly."
    help_resources: List[str] = field(
        default_factory=lambda: ["https://cdevframework.io"]
    )


class CloudOutputDoesNotExist(BackendError):
    pass


class KeyNotInCloudOutput(BackendError):
    pass


class ResourceReferenceError(BackendError):
    pass
