"""Qpm exception classes."""

class qpmError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg

class qpmConfigError(qpmError):
    """Config related errors."""
    pass

class qpmRuntimeError(qpmError):
    """Generic runtime errors."""
    pass

class qpmArgumentError(qpmError):
    """Argument related errors."""
    pass
