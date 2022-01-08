from ..utils.exceptions import Cdev_Error


class BackendError(Cdev_Error):
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


class ResourceDoesNotExist(BackendError):
    pass


class CloudOutputDoesNotExist(BackendError):
    pass


class KeyNotInCloudOutput(BackendError):
    pass


class ResourceReferenceError(BackendError):
    pass
