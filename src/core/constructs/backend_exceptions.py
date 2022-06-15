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


class ResourceDoesNotExist(BackendError):
    pass


class CloudOutputDoesNotExist(BackendError):
    pass


class KeyNotInCloudOutput(BackendError):
    pass


class ResourceReferenceError(BackendError):
    pass
