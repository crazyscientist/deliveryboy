#!/usr/bin/env python3
# -*- coding: utf8 -*-

import base64
from io import StringIO
import subprocess
import sys
import types

from dill import dumps, loads

from .exceptions import (DeliveryTransportError, DeliveryPickleError,
                         DeliveryPackingError)


class DeliveryBox(object):
    """Container for data exchange"""
    # OUTPUT VALUES
    stdout = None
    stderr = None
    return_value = None
    exception = None

    # INPUT VALUES
    func = None
    args = None
    kwargs = None
    modules = []

    def __str__(self):
        return "\n".join(["{:15s}: {}".format(key, value)
                          for (key, value) in self.__dict__.items()])


class DeliveryBoy(object):
    """Operator for call the new process and handle input/output

    When called the decorated callable and non-standard modules stored in its
    `__globals__` attribute are pickled and passed via the transport command
    to the newly started python process.

    If an exception is raised during execution of the decorated callable, this
    exception is pickled and reraised.

    If `async` is `False`, STDOUT, STDERR and the return value of the decorated
    callable are returned upon calling the decorated callable. Otherwise only
    the process ID is returned; if a transport is defined, it is the process ID
    of the transport, otherwise the process ID of the interpreter.

    After execution STDOUT and STDERR writing during execution of the callable
    are written to STDOUT and STDERR of the main process. This applies only to
    synchronous execution!

    :param func: Callable objecte that is called in the new process
    :type func: callable
    :param transport: Transport command
    :type transport: str
    :param executable: The python executable to be called.
                       Default: `sys.executable`.
    :type executable: Absolute path of python interpreter
    :param async: If set to `True`, this process will not wait for the process
                  called via the transport command to finish. Default: `False`
    :type async: bool

    TODO: Think about more parameters
    TODO: Define arguments
    TODO: Raise exception, if one is returned
    TODO: Implement async feature
    """
    def __init__(self, func, **params):
        self.func = func
        self.params = params
        self.async = self.params.pop("async", False)
        self.executable = self.params.pop("executable", sys.executable)
        self.transport = self.params.pop("transport", None)
        self.transport_params = self.params.pop("transport_params", [])
        self.inbox = DeliveryBox()
        self.outbox = None

    def __call__(self, *args, **kwargs):
        self._pack_box(args, kwargs)

        response = self._run_delivery()

        if self.transport:
            self._unpickle(response[0])
            self._pipe_stdout_err()
            self._reraise()

        return self.outbox.return_value

    def _pack_box(self, args, kwargs):
        """Pack callable, arguments and modules

        :param args: Arguments to be passed to the callable
        :type args: list
        :param kwargs: Arguments to be passed to the callable
        :type kwargs: dict
        """
        self.inbox.args = args
        self.inbox.kwargs = kwargs
        if isinstance(self.func, types.FunctionType):
            self.inbox.func = self.func.__code__
            myglobals = self.func.__globals__
        else:
            raise DeliveryPackingError(
                "This type of callable is not supported"
            )
        self.inbox.modules = [k for (k, v) in myglobals.items()
                              if isinstance(v, types.ModuleType)
                              and not k.startswith("__")]

    def _run_delivery(self):
        """Executes the actual transport/executable

        If `transport` is `None`, it and `transport_params` will be omitted
        from the command line. In this case the callable is run directly.
        Also, in this case the `async` option is ignored.
        """
        if self.transport:
            cmd = [self.transport, ] + self.transport_params + [
                self.executable, "-m", "deliveryboy", self._pickle()
            ]

            try:
                child_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as error:
                raise DeliveryTransportError(real_exception=error)

            if not self.async:
                return child_process.communicate()
            else:
                return child_process.pid
        else:
            self.outbox = DeliveryBox()
            self.outbox.return_value = execute(self.inbox)

    def _pipe_stdout_err(self):
        """Redirect STDOUT and STDERR from delivered callable"""
        for stream in ["stdout", "stderr"]:
            if isinstance(self.outbox, DeliveryBox) \
                    and getattr(self.outbox, stream, None):
                print(
                    getattr(self.outbox, stream),
                    file=getattr(sys, stream)
                )

    def _pickle(self):
        """Return pickled and encoded :py:obj:`deliveryboy.core.DeliveryBox`

        :returns: pickled/encoded delivery box
        :type: bytes
        """
        try:
            return base64.b64encode(dumps(self.inbox))
        except Exception as error:
            raise DeliveryPickleError(real_exception=error)

    def _unpickle(self, data):
        """Return unpickled :py:obj:`deliveryboy.core.DeliveryBox`

        :param data: pickled/encoded delivery box
        :type data: bytes
        :return: :py:obj:`deliveryboy.core.DeliveryBox`
        """
        if data.endswith(b"\n"):
            data = data[:-1]
        try:
            self.outbox = loads(base64.b64decode(data))
        except Exception as error:
            raise DeliveryPickleError(real_exception=error)
        else:
            return self.outbox

    def _reraise(self):
        """Re-raises an exception originating from the callable"""
        if self.outbox and isinstance(self.outbox.exception, Exception):
            raise self.outbox.exception


class DeliveryBoyDecorator(object):
    """Decorator for functions

    Decorated functions are pickled and passed to a newly started python process
    that is called via a transport command (e.g. sudo)

    :param transport: Transport command
    :type transport: str
    :param executable: The python executable to be called.
                       Default: `sys.executable`.
    :type executable: Absolute path of python interpreter
    :param async: If set to `True`, this process will not wait for the process
                  called via the transport command to finish. Default: `False`
    :type async: bool
    """
    def __init__(self, **params):
        self.params = params

    def __call__(self, func):
        return DeliveryBoy(func, **self.params)


def execute(inbox):
    globals().update({x: __import__(x) for x in inbox.modules})

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    if inbox.func is not None and isinstance(inbox.func, types.CodeType):
        func = types.FunctionType(inbox.func, globals())
    else:
        raise DeliveryPackingError("No callable to run in delivery box")

    box = DeliveryBox()
    try:
        box.return_value = func(*inbox.args, **inbox.kwargs)
    except Exception as error:
        box.exception = error
    box.stdout = sys.stdout.getvalue()
    box.stderr = sys.stderr.getvalue()

    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    return box


def main():
    """Entry function for new process

    This method unpickles data from the command line, redirects STDOUT + STDERR
    and pickles the return value and exception

    Input and output of this function are base64 encoded strings representing
    pickled :py:obj:`deliveryboy.core.DeliveryBox` objects.
    """
    try:
        decoded = base64.b64decode(bytes(sys.argv[1], "utf8"))
        inbox = loads(decoded)
    except Exception as error:
        box = DeliveryBox()
        box.exception = error
    else:
        box = execute(inbox)

    print(base64.b64encode(dumps(box)).decode("utf8"))