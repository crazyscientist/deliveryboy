import os
import getpass
import socket
from deliveryboy.core import DeliveryBoyDecorator


@DeliveryBoyDecorator(transport="ssh", transport_params=['-v', 'localhost'], discard_excess=False)
def ssh_test(value):
    print("=== HELLO WORLD ===")
    return "This is PID {} run by {} on {} with value: {}".format(
        os.getpid(), getpass.getuser(), socket.gethostname(), value
    )


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    # Example: Simple usage
    print(ssh_test("date"))
