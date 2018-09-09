#!/usr/bin/env python3
# -*- coding: utf8 -*-


from io import StringIO
import os

import subprocess
import sys
import types

from .exceptions import (DeliveryTransportError, DeliveryPackingError)
from .pickle import pickle, unpickle, ModulePickle


class DeliveryBox(object):
    """Container for data exchange"""
    # OUTPUT VALUES
    stdout = None
    stderr = None
    return_value = None
    exception = None

    # INPUT VALUES
    instance = None
    func = None
    args = None
    kwargs = None
    modules = set()
    pickled_modules = set()

    def __str__(self):
        return "\n".join(["{:15s}: {}".format(key, value)
                          for (key, value) in self.__dict__.items()])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class DeliveryBoy(object):
    """Operator for call the new process and handle input/output

    When called the decorated function and non-standard modules stored in its
    `__globals__` attribute are pickled and passed via the transport command
    to the newly started python process.

    If an exception is raised during execution of the decorated function, this
    exception is pickled and reraised.

    If `async` is `False`, STDOUT, STDERR and the return value of the decorated
    function are returned upon calling the decorated function. Otherwise only
    the process ID is returned; if a transport is defined, it is the process ID
    of the transport, otherwise the process ID of the interpreter.

    After execution STDOUT and STDERR writing during execution of the callable
    are written to STDOUT and STDERR of the main process. This applies only to
    synchronous execution!

    :param func: Function object that is called in the new process
    :type func: callable
    :param transport: Transport command
    :type transport: str
    :param transport_params: Additional arguments for the transport command.
    :type transport_params: list
    :param executable: The python executable to be called.
                       Default: `sys.executable`.
    :type executable: Absolute path of python interpreter
    :param async: If set to `True`, this process will not wait for the process
                  called via the transport command to finish. Default: `False`
    :type async: bool
    :param discard_excess: If set to `False`, all output written to STDOUT by
                           the new process that is not redirected gets pre- or
                           appended accordingly to the delivery box.
                           Default: `True`
    :type discard_excess: bool

    :return: Return value of the decorated callable

    :raises deliveryboy.exceptions.DeliveryPackingError: if decorated callable
        is not supported, if a module cannot be added to the delivery box
    :raises deliveryboy.exceptions.DeliveryTransportError: if calling the
        transport or executable fail (e.g. command not found, exit code not
        equal zero.
    """

    def __init__(self, func, transport=None, transport_params=[],
                 executable=sys.executable, async=False, discard_excess=True,
                 **params):
        self.func = func
        self.params = params
        self.async = async
        self.discard_excess= discard_excess
        self.executable = executable
        self.transport = transport
        self.transport_params = transport_params
        self.inbox = DeliveryBox()
        self.outbox = None

    def __call__(self, *args, **kwargs):
        self._pack_box(args, kwargs)

        response = self._run_delivery()

        if self.transport:
            self.outbox, prefix, suffix = unpickle(response[0],
                                                   self.discard_excess)
            if prefix or suffix:
                self.outbox.stdout = prefix + self.outbox.stdout + suffix

        self._pipe_stdout_err()
        self._reraise()
        return self.outbox.return_value

    def __get__(self, obj, classobj=None):
        if obj is not None:
            self.inbox.instance = obj
        return self

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
            self._pack_box_modules()
            # myglobals = self.func.__globals__
        else:
            raise DeliveryPackingError(
                "This type of callable is not supported"
            )

    def _pack_box_modules(self):
        """Add modules to box for pickling"""
        allmodules = [(k, v) for (k, v) in self.func.__globals__.items()
                      if isinstance(v, types.ModuleType)
                      and not k.startswith("__")]

        venv = os.environ.get("VIRTUAL_ENV", None)
        path = sys.path[1:]
        if venv:
            path = [p for p in path if p and not p.startswith(venv)]
            path.append(venv)

        try:
            # Handle builtins and modules from virtual env
            # Start with those that have no __file__ attribute
            self.inbox.modules |= set([k for (k, v) in allmodules
                                       if getattr(v, '__file__', None) is None])

            # Then add those from the system paths
            for sitepath in path:
                self.inbox.modules |= {
                        k for (k, v) in allmodules
                        if getattr(v, '__file__', '').startswith(sitepath)
                }
        except Exception as error:
            raise DeliveryPackingError(
                "Cannot pack built-in/venv modules",
                real_exception=error
            )

        # TODO: This breaks availability of imported submodules
        mod_pickle = ModulePickle(modules=[v for (k, v) in allmodules
                                           if k not in self.inbox.modules])
        self.inbox.pickled_modules = mod_pickle.pickle()
        self.inbox.modules |= set([k for (k, v) in allmodules
                                   if k not in self.inbox.modules])

    def _run_delivery(self):
        """Executes the actual transport/executable

        If `transport` is `None`, it and `transport_params` will be omitted
        from the command line. In this case the callable is run directly.
        Also, in this case the `async` option is ignored.
        """
        if self.transport:
            cmd = [self.transport, ] + self.transport_params + [
                self.executable, "-m", "deliveryboy", pickle(self.inbox)
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
                response = child_process.communicate()
                self._handle_call_error(response, child_process.returncode)
                return response
            else:
                return child_process.pid
        else:
            self.outbox = execute(self.inbox)

    def _handle_call_error(self, response, returncode):
        if returncode:
            raise DeliveryTransportError(
                "Child process exited with {}: {}".format(
                    returncode, response[1].decode("utf8")
            ))

    def _pipe_stdout_err(self):
        """Redirect STDOUT and STDERR from delivered callable"""
        for stream in ["stdout", "stderr"]:
            if isinstance(self.outbox, DeliveryBox) \
                    and getattr(self.outbox, stream, None):
                print(
                    getattr(self.outbox, stream),
                    file=getattr(sys, stream)
                )

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

    def __call__(self, func, *args, **kwargs):
        return DeliveryBoy(func, **self.params)


def execute(inbox):
    """Setup the environment and execute the decorated callable

    :param inbox: Pickled :py:obj:`DeliveryBox` instance
    :return: :py:obj:`DeliveryBox`
    :raises deliveryboy.exception.DeliveryPackingError: If callable is missing
    """
    # Load pickled modules
    mod_pickle = ModulePickle(pickled=inbox.pickled_modules)
    mod_pickle.unpickle()

    # Import modules
    globals().update({x: __import__(x) for x in inbox.modules})

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    if inbox.func is not None and isinstance(inbox.func, types.CodeType):
        func = types.FunctionType(inbox.func, globals())
    else:
        del mod_pickle
        raise DeliveryPackingError("No callable to run in delivery box")

    box = DeliveryBox()
    try:
        if inbox.instance is not None:
            box.return_value = func(inbox.instance, *inbox.args, **inbox.kwargs)
        else:
            box.return_value = func(*inbox.args, **inbox.kwargs)
    except Exception as error:
        box.exception = error
    box.stdout = sys.stdout.getvalue()
    box.stderr = sys.stderr.getvalue()

    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    del mod_pickle
    return box


def main():
    """Entry function for new process

    This method unpickles data from the command line, redirects STDOUT + STDERR
    and pickles the return value and exception

    Input and output of this function are base64 encoded strings representing
    pickled :py:obj:`deliveryboy.core.DeliveryBox` objects.
    """
    try:
        inbox = unpickle(bytes(sys.argv[1], "utf8"))[0]
    except Exception as error:
        box = DeliveryBox()
        box.exception = error
    else:
        box = execute(inbox)

    print(pickle(box))
