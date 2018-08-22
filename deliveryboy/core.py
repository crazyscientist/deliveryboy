#!/usr/bin/env python3
# -*- coding: utf8 -*-

from dill import dumps, loads
import base64
import os
import subprocess
import sys
import types


class ExceptionWrapper(object):
    """
    Wrapper to allow pickling of exceptions

    :param exc: exception
    """
    def __init__(self, exc):
        self.exc = exc


class DeliveryBox(object):
    """
    Container for data exchange
    """
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
    def __init__(self, **params):
        self.params = params

    def __call__(self, func):
        return DeliveryBoy(func, **self.params)
