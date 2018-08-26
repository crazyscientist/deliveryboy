import os
import getpass
from deliveryboy.core import DeliveryBoyDecorator


@DeliveryBoyDecorator(transport="sudo")
def sudo_test(value):
    print("=== HELLO WORLD ===")
    return "This is PID {} run by {} with value: {}".format(
        os.getpid(), getpass.getuser(), value
    )


@DeliveryBoyDecorator(transport="sudo")
def sudo_div(value):
    print("=== HELLO WORLD ===")
    return "This is PID {} run by {} with value: {}".format(
        os.getpid(), getpass.getuser(), 4./float(value)
    )


class SudoDemo(object):
    def __init__(self, multiplier):
        self.multiplier = multiplier

    @DeliveryBoyDecorator(transport="sudo", transport_params = ["-u", "nobody"])
    def __call__(self, value):
        return "This is PID {} run by {} with value: {}".format(
            os.getpid(), getpass.getuser(), value * self.multiplier
        )


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    # Example: Simple usage
    print(sudo_test("date"))

    # Example: Messing with the decorator parameters
    sudo_test.transport_params = ['-u', 'nobody']
    print(sudo_test("time"))

    try:
        print(sudo_div("0"))
    except ZeroDivisionError:
        print("Yes, we got the expected exception")

    # Example: Using the decorator on a class method
    sinst = SudoDemo(3)
    print(sinst(2))
