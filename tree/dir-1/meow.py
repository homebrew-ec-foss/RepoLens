def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


class Calculator:
    def __init__(self):
        self.result = 0

    def compute(self, x, y, operation):
        if operation == "add":
            self.result = add(x, y)
        elif operation == "subtract":
            self.result = subtract(x, y)
        return self.result


if __name__ == "__main__":
    calc = Calculator()
    print(calc.compute(5, 3, "add"))
    print(calc.compute(5, 3, "subtract"))