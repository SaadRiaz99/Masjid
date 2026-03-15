from database import Database

def populate_sample_data():
    db = Database()

    # Add sample participants
    db.add_participant("Ahmed Khan", "03001234567", "Lahore", "12345-6789012-3")
    db.add_participant("Fatima Ali", "03009876543", "Karachi", "98765-4321098-7")
    db.add_participant("Muhammad Usman", "03211234567", "Islamabad", "11223-3344556-7")

    # Add sample animals
    db.add_animal("cow", 50000, "Farmer Ahmed", 7)
    db.add_animal("goat", 15000, "Butcher Ali", 1)
    db.add_animal("camel", 100000, "Desert Trader", 10)

    # Allocate some shares
    db.allocate_share(1, 1)  # Ahmed to cow share 1
    db.allocate_share(1, 1)  # Ahmed to cow share 2
    db.allocate_share(2, 2)  # Fatima to goat share 1
    db.allocate_share(3, 3)  # Usman to camel share 1

    # Record payments
    db.add_payment(1, 5000)
    db.add_payment(2, 1500)
    db.add_payment(3, 2500)

    print("Sample data populated successfully!")

if __name__ == "__main__":
    populate_sample_data()