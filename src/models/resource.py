class Resource:
    def __init__(self, name, quantity):
        if not name.strip():
            raise ValueError("Resource name cannot be empty.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        self.name = name
        self.quantity = quantity

    def display(self):
        print(f"Resource: {self.name}")
        print(f"Quantity: {self.quantity}")


    
    def add_stock(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        self.quantity += amount

    def use_stock(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        if amount > self.quantity:
            raise ValueError("Insufficient stock.")

        self.quantity -= amount
