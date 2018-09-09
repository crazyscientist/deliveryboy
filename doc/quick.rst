Quickstart
==========

Installation
------------
Installation is quick and requires no dependencies that are unhandled by
``pip``. Follow instructions in :ref:`installation`.

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

ssh
^^^

.. code-block:: python

    >>> import os
    >>> import getpass
    >>> import socket
    >>> from deliveryboy.core import DeliveryBoyDecorator
    >>> @DeliveryBoyDecorator(transport="ssh", transport_params=['testserver'], executable="/opt/deliveryboy/bin/python")
    >>> def ssh_test(value):
    >>>     print("=== HELLO WORLD ===")
    >>>     return "This is PID {} run by {} on {} with value: {}".format(
    >>>     os.getpid(), getpass.getuser(), socket.gethostname(), value
    >>> )
    >>> print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    This id PID 8877 run by andi
    >>> print(ssh_test("date"))
    === HELLO WORLD ===

    This is PID 2581 run by andi on testserver with value: date

Importing modules that are not provided by the Python environment need to be
transferred to the remote host. This has not been solved to a satisfactory
extent.

.. important::
    When importing submodules or importing as a different name, it will not work
    out of the box. In that case re-import inside the decorated callable, e.g.:

    .. code-block:: python

        import getpass
        import os
        import socket
        from deliveryboy.core import DeliveryBoyDecorator
        import mymodule.sudo

        @DeliveryBoyDecorator(transport="ssh", transport_params=['testserver'], executable='/opt/deliveryboy/bin/python')
        def sudo_test(value):
            print("=== HELLO WORLD ===")
            import mymodule.sudo
            return "This is PID {} run by {} on {} with value: {}".format(
                os.getpid(), getpass.getuser(), socket.gethostname(), mymodule.sudo.foo(value)
            )

        ##################
        # mymodule/sudo.py
        def foo(value):
            """Foo Bar function"""
            print("<= FOO BAR =>")
            return "My foo value: {}".format(value*5)
        ##################