#!/usr/bin/env python3
# -*- coding: utf8 -*-

from marshal import dumps, loads
import base64
import subprocess
import sys


class DeliveryBoy(object):
    def __init__(self, func, **params):
        self.func = func
        self.params = params
        self.transport = self.params.pop("transport", "sudo")

    def __call__(self, *args, **kwargs):
        pickled = dumps(
            [self.func.__code__, args, kwargs]
        )
        encoded = base64.b64encode(pickled)
        print("=DEBUG= PICKLED:", pickled)
        print("=DEBUG= ENCODED:", encoded)

        child_process = subprocess.Popen(
            [
                #self.transport,
                sys.executable,
                "-m", "deliveryboy",
                encoded
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        response = child_process.communicate()
        print("=DEBUG=", response[0])
        print("=DEBUG=", response[1])

        return loads(response[0])


class DeliveryBoyDecorator(object):
    def __init__(self, **params):
        self.params = params

    def __call__(self, func):
        return DeliveryBoy(func, **self.params)
