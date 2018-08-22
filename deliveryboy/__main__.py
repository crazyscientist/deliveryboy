#!/usr/bin/env python3
# -*- coding: utf8 -*-

from dill import loads, dump, dumps
import base64
from io import StringIO
import sys
from types import FunctionType

from .core import DeliveryBox


def main():
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    decoded = base64.b64decode(bytes(sys.argv[1], "utf8"))
    box = DeliveryBox()

    try:
        inbox = loads(decoded)

        globals().update({x: __import__(x) for x in inbox.modules})

        func = FunctionType(inbox.func, globals())
        box.return_value = func(*inbox.args, **inbox.kwargs)
    except Exception as error:
        box.exception = error

    box.stdout = sys.stdout.getvalue()
    box.stderr = sys.stderr.getvalue()

    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    print(base64.b64encode(dumps(box)).decode("utf8"))


main()
