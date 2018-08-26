Quickstart
==========

Installation
------------
This needs to be defined, later

Examples
--------

sudo
^^^^
.. code-block:: python

    >>> import os
    >>> import getpass
    >>> from deliveryboy.core import DeliveryBoyDecorator
    >>>
    >>> @DeliveryBoyDecorator()
    >>> def sudo_test(value):
    >>>    return "This is PID {} run by {} with value: {}".format(
    >>>        os.getpid(), getpass.getuser(), value
    >>>    )
    >>> print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    This id PID 12111 run by andi
    >>> print(sudo_test("date"))
    This is PID 12113 run by root with value: date
    >>> print(sudo_test("time"))
    This is PID 12115 run by root with value: time

.. important:: Always use the decorator with parenthesis!