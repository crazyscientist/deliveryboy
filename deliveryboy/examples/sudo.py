import os
import getpass
from deliveryboy.core import DeliveryBoyDecorator


@DeliveryBoyDecorator()
def sudo_test(value):
    print("=== HELLO WORLD ===")
    return "This is PID {} run by {} with value: {}".format(
        os.getpid(), getpass.getuser(), value
    )


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    print(sudo_test("date"))
    print(sudo_test("time"))