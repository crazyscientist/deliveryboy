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


# TODO: Decorator for classes
@DeliveryBoyDecorator(transport=None, transport_params=["-u", "nobody"])
class SudoDemo(object):
    def __init__(self, multiplier):
        self.multiplier = multiplier

    def __call__(self, value):
        return "This is PID {} run by {} with value: {}".format(
            os.getpid(), getpass.getuser(), value * self.multiplier
        )


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    print(sudo_test("date"))

    sudo_test.transport_params = ['-u', 'nobody']
    print(sudo_test("time"))

    print(sudo_div("2"))

    sinst = SudoDemo(3)
    # This raises a DeliveryPackingError!
    print(sinst(2))
