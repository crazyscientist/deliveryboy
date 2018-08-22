import unittest
import pickle
import base64
import tempfile


def test_func(value):
    return value * 4


class DeliveryTest(unittest.TestCase):

    def test_pickle(self):
        pickled = pickle.dumps(test_func)
        encoded = base64.b64encode(pickled)
        tmp = tempfile.mkstemp()

        with open(tmp[1], "wb") as fh:
            fh.write(encoded)

        with open(tmp[1], "rb") as fh:
            read = fh.read()

        self.assertEqual(encoded, read)
        decoded = base64.b64decode(read)
        self.assertEqual(decoded, pickled)
        fun = pickle.loads(decoded)
        self.assertEqual(test_func, fun)