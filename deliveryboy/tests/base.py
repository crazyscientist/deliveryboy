import random
import string


class UtilsMixin(object):
    """
    Mixin for testcase classes providing utils
    """
    def get_random_string(self, length=8):
        return "".join([random.choice(string.printable) for x in range(length)])

    def get_random_bytes(self, *args, **kwargs):
        return self.get_random_string(*args, **kwargs).encode("utf8")