#!/usr/bin/env python3
# -*- coding: utf8 -*-

from marshal import loads, dump
import base64
from types import FunctionType
import sys

decoded = base64.b64decode(bytes(sys.argv[1], "utf8"))
print("=DEBUG= ORIGINAL", sys.argv[1])
print("=DEBUG= DECODED", decoded)
try:
    func, args, kwargs = loads(decoded)
    func = FunctionType(func, globals())
    print("=== Executing", func, args, kwargs)
except Exception as error:
    dump(sys.stdout, error)
else:
    dump(sys.stdout, func(*args, **kwargs))
