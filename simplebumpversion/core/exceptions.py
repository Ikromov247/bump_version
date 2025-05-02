class ArgumentsNotFound(Exception):
    """No argument provided in cli"""

    def __init__(self, message):
        super().__init__(message)


class NoValidVersionStr(Exception):
    """No valid version file is found"""

    def __init__(self, message):
        super().__init__(message)
