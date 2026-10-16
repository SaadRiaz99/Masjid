from src.models.resource import Resource


def main():
    medicine = Resource("Medicine", 100)
    medicine.add_stock(20)
    print("After adding stock:")
    medicine.display()
    
    camping_tent = Resource("Camping Tent", 19)
    # camping_tent.add_stock(20)
    camping_tent.use_stock(40)
    camping_tent.display()


if __name__ == "__main__":
    main()