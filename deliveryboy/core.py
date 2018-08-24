#!/usr/bin/env python3
# -*- coding: utf8 -*-

import base64
from io import StringIO
import subprocess
import sys
import types

from dill import dumps, loads


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


class DeliveryBoy(object):
    """Operator for call the new process and handle input/output

    When called the decorated function and almost all modules stored in its
    `__globals__` attribute are pickled and passed via the transport command
    to the newly started python process.

    If an exception is raised during execution of the decorated function, this
    exception is pickled and reraised.

    If `async` is `False`, STDOUT, STDERR and the return value of the decorated
    function are returned upon calling the decorated function. Otherwise only
    the STDOUT and STDERR of the transport command are returned.

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
        self.transport = self.params.pop("transport", "sudo")

    def __call__(self, *args, **kwargs):
        box = DeliveryBox()
        box.args = args
        box.kwargs = kwargs
        box.func = self.func.__code__
        box.modules = [k for (k, v) in self.func.__globals__.items()
                       if isinstance(v, types.ModuleType)
                       and not k.startswith("__")]

        pickled = dumps(box)
        encoded = base64.b64encode(pickled)

        child_process = subprocess.Popen(
            [
                self.transport,
                sys.executable,
                "-m", "deliveryboy",
                encoded
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        response = child_process.communicate()

        if response[0].endswith(b"\n"):
            box = loads(base64.b64decode(response[0][:-1]))
        else:
            box = loads(base64.b64decode(response[0]))

        return box.return_value


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


def main():
    """Entry function for new process

    This method unpickles data from the command line, redirects STDOUT + STDERR
    and pickles the return value and exception

    Input and output of this function are base64 encoded strings representing
    pickled :py:obj:`deliveryboy.core.DeliveryBox` objects.
    """
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    decoded = base64.b64decode(bytes(sys.argv[1], "utf8"))
    box = DeliveryBox()

    try:
        inbox = loads(decoded)

        globals().update({x: __import__(x) for x in inbox.modules})

        func = types.FunctionType(inbox.func, globals())
        box.return_value = func(*inbox.args, **inbox.kwargs)
    except Exception as error:
        box.exception = error

    box.stdout = sys.stdout.getvalue()
    box.stderr = sys.stderr.getvalue()

    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    print(base64.b64encode(dumps(box)).decode("utf8"))