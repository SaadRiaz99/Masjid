class Resource:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def display(self):
        print(f"Resource: {self.name}")
        print(f"Quantity: {self.quantity}")