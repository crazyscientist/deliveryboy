class DeliveryError(Exception):
    """Base class for all exceptions raised by DeliveryBoy

    In general derived exceptions are convenience wrappers around other
    exceptions.

    The real exception that was raised will be delivered in the attribute
    `real_exception`.
    """
    real_exception = None

    def __init__(self, *args, **kwargs):
        self.real_exception = kwargs.pop("real_exception", None)
        super().__init__(*args, **kwargs)


class DeliveryTransportError(DeliveryError):
    """Failure during call of the transport command

    This exception is raised, if the transport command or the executable ran
    into an error like the command not being found or missing permission.
    """


class DeliveryPickleError(DeliveryError):
    """Failure during (un-) pickling

    This exception is raised, if picklung or unpickling fails.
    """


class DeliveryPackingError(DeliveryError):
    """Failure during packing of the callable

    This exception is raised, if the decorated callable is not supported.
    """