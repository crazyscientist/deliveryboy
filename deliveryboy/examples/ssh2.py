#!/usr/bin/eny python3

import getpass
import os
import socket
from deliveryboy.core import DeliveryBoyDecorator
import mymodule.sudo


@DeliveryBoyDecorator(transport="ssh", transport_params=['testserver'],
                      executable='/opt/deliveryboy/bin/python')
def sudo_test(value):
    # TODO: Having to import inside the decorated function is not desirable :-(
    import mymodule.sudo
    print("=== HELLO WORLD ===")
    return "This is PID {} run by {} on {} with value: {}".format(
        os.getpid(), getpass.getuser(), socket.gethostname(),
        mymodule.sudo.foo(value)
    )


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    # Example: Simple usage
    try:
        print(sudo_test(5))
    except:
        print(sudo_test.outbox)
        raise