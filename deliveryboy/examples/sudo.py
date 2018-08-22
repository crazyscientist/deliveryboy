import os
from deliveryboy.core import DeliveryBoyDecorator


@DeliveryBoyDecorator()
def sudo_test(value):
    print("=== HELLO WORLD ===")
    return "This is PID {} with value: {}".format(
        os.getpid(), value
    )


if __name__ == '__main__':
    print("This id PID {}".format(os.getpid()))
    print(sudo_test("date"))
    print(sudo_test("time"))