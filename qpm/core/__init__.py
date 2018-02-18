"""qpm core exceptions module."""

class qpmError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class qpmConfigError(qpmError):
    pass

class qpmRuntimeError(qpmError):
    pass

class qpmArgumentError(qpmError):
    pass

class qpmInterfaceError(qpmError):
    pass
