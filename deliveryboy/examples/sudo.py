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


if __name__ == '__main__':
    print("This id PID {} run by {}".format(os.getpid(), getpass.getuser()))
    print(sudo_test("date"))

    sudo_test.transport_params = ['-u', 'nobody']
    print(sudo_test("time"))

    print(sudo_div("2"))
    print(sudo_div(0))
