#!/usb/bin/env python3
# -*- coding: utf8 -*-

import base64
import io
import os
import re
import shutil
import sys
import tarfile
import tempfile

from dill import dumps, loads

from .exceptions import DeliveryPickleError

PICKLE_START_MARKER = b"=====BEGINPICKLE====="
PICKLE_END_MARKER = b"=====ENDPICKLE====="


def pickle(data):
    """Return pickled and encoded :py:obj:`deliveryboy.core.DeliveryBox`

    :param data: delivery box to be pickled
    :type data: :py:obj:`deliveryboy.core.DeliveryBox`
    :returns: pickled/encoded delivery box
    :rtype: bytes
    :raises DeliveryPickleError: if data cannot be pickled
    """
    try:
        return PICKLE_START_MARKER.decode("utf8") + \
               base64.b64encode(dumps(data)).decode("utf8") + \
               PICKLE_END_MARKER.decode("utf8")
    except Exception as error:
        raise DeliveryPickleError(real_exception = error)


def unpickle(data, discard_excess=True):
    """Return unpickled :py:obj:`deliveryboy.core.DeliveryBox`

    :param data: pickled/encoded delivery box
    :type data: bytes
    :param discard_excess: If ``True``, additional text around the pickled data
                           will be discarded. Default: ``True``
    :type discard_excess: bool
    :return: :py:obj:`deliveryboy.core.DeliveryBox`, prefix, suffix
    :rtype: :py:obj:`deliveryboy.core.DeliveryBox`, str, str
    :raises DeliveryPickleError: if data cannot be unpickled
    """
    match = re.match(
        "(?P<prefix>.*?){}(?P<data>.*?){}(?P<suffix>.*)".format(
            PICKLE_START_MARKER.decode("utf8"),
            PICKLE_END_MARKER.decode("utf8")
        ).encode("utf8"),
        data
    )

    if match is None:
        raise DeliveryPickleError("Cannot unpickle data: {}".format(data))

    try:
        return_data = loads(base64.b64decode(match.group("data")))
    except Exception as error:
        raise DeliveryPickleError(real_exception = error)

    if discard_excess:
        return return_data, "", ""
    return return_data, match.group("prefix"), match.group("suffix")


class ModulePickle(object):
    """Serializer for modules

    This serializer accepts a list of modules and adds all source files of these
    modules in a TAR archive. :py:meth:`pickle` returns the byte stream of this
    archive that will be transfered in the pickled data. :py:meth:`unpickle`
    takes this bytes stream and extracts the module sources in a temporary
    directory which is added to :py:obj:`sys.path` in order to allow importing
    these modules.

    :param modules: list of module names
    :param pickled: Byte data
    """
    name = "modulecontainer"

    def __init__(self, modules=[], pickled=None):
        self.modules = modules
        self.buffer = io.BytesIO()
        self.tmpdir = None

        if pickled is not None:
            self.buffer.write(pickled)
            self.buffer.seek(0)

    def __del__(self):
        if self.tmpdir and os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def pickle(self):
        """Add modules to TAR archive and return byte data of TAR archive"""
        tarball = tarfile.open(
            self.name,
            mode="w:gz",
            fileobj=self.buffer
        )

        for mod in self.modules:
            path = os.path.dirname(mod.__file__)
            tarball.add(path, os.path.basename(path))

        tarball.close()
        self.buffer.seek(0)
        return self.buffer.read()

    def unpickle(self):
        """Restore modules

        Creates a temporary directory, add it to :py:obj:`sys.path`, opens TAR
        archive from byte data and extracts it into the temporary directory.
        """
        self.tmpdir = tempfile.mkdtemp()
        sys.path.append(self.tmpdir)

        tarball = tarfile.open(
            self.name,
            mode="r:gz",
            fileobj=self.buffer
        )
        tarball.extractall(self.tmpdir)