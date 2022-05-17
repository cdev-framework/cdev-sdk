class CdevError(Exception):
    pass


class CouldNotParseFileError(CdevError):
    def __init__(self, error):
        self.error = error


class CdevFileNotFoundError(FileNotFoundError):
    def __init__(self, message):
        self.message = message


class InvalidParamError(CdevError):
    # This error should be thrown when anything is passed a wrong param
    def __init__(self, message):
        self.message = message


class InvalidDataError(CdevError):
    # This error should be thrown when there is a problem with the integrity of data passed into a system
    def __init__(self, message):
        self.message = message
