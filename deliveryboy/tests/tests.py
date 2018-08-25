import base64
import unittest
import tempfile

import dill


def test_func(value):
    return value * 4


class Foo(object):
    def __init__(self, multiply):
        self.multiply = multiply

    def __call__(self, value):
        return self.multiply * value


class DeliveryTest(unittest.TestCase):

    def test_pickle(self):
        pickled = dill.dumps(test_func)
        encoded = base64.b64encode(pickled)
        tmp = tempfile.mkstemp()

        with open(tmp[1], "wb") as fh:
            fh.write(encoded)

        with open(tmp[1], "rb") as fh:
            read = fh.read()

        self.assertEqual(encoded, read)
        decoded = base64.b64decode(read)
        self.assertEqual(decoded, pickled)
        fun = dill.loads(decoded)
        self.assertEqual(test_func, fun)

    def test_pickle_exception(self):
        try:
            1/0
        except Exception as error:
            pickled = dill.dumps(error)

        unpickled = dill.loads(pickled)
        self.assertTrue(isinstance(unpickled, ZeroDivisionError))

    def test_pickle_instance(self):
        pickled = dill.dumps(Foo(3))
        instance = dill.loads(pickled)

        self.assertEqual(instance(2), 6)
