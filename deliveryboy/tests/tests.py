import base64
import unittest

import tempfile

import dill

from .base import UtilsMixin
from .. import core, exceptions, pickle


def test_func(value):
    return value * 4


class Foo(object):
    def __init__(self, multiply):
        self.multiply = multiply

    def __call__(self, value):
        return self.multiply * value


class PickleTest(UtilsMixin, unittest.TestCase):

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

    def test_pickle_delivery_box(self):
        box = core.DeliveryBox()
        box.args = [self.get_random_string() for x in range(3)]
        box.kwargs = {
            self.get_random_string(): self.get_random_string()
            for x in range(3)}
        box.func = test_func

        pickled = core.pickle(box)
        unpickled, p, s = core.unpickle(pickled.encode("utf8"))
        self.assertEqual(box, unpickled)

    def test_pickle_markers(self):
        data = self.get_random_bytes()
        pickled = pickle.pickle(data).encode("utf8")

        with self.subTest("while pickling"):
            self.assertTrue(pickled.startswith(pickle.PICKLE_START_MARKER))
            self.assertTrue(pickled.endswith(pickle.PICKLE_END_MARKER))

        with self.subTest("while unpickling"):
            unpickled, prefix, suffix = core.unpickle(pickled)
            self.assertEqual(unpickled, data)

        with self.subTest("while unpickling with overhead"):
            pre = self.get_random_bytes()
            post = self.get_random_bytes()
            unpickled, prefix, suffix = core.unpickle(pre + pickled + post,
                                                      discard_excess=False)
            self.assertEqual(data, unpickled)
            self.assertEqual(prefix, pre)
            self.assertEqual(suffix, post)

    def test_unpickle_error(self):
        testdata = [
            b'simple plain invalid text',
            pickle.PICKLE_START_MARKER + b'missing end marker',
            b'missing start marker' + pickle.PICKLE_END_MARKER,
            pickle.PICKLE_START_MARKER + b'invalid' + pickle.PICKLE_END_MARKER
        ]

        for data in testdata:
            with self.subTest("Invalid data: {}".format(data)):
                self.assertRaises(
                    exceptions.DeliveryPickleError, pickle.unpickle, data
                )