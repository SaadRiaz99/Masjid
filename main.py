from src.models.resource import Resource


def main():
    medicine = Resource("Medicine", 100)
    camping_tent = Resource("Camping Tent", 19)
    medicine.display()


if __name__ == "__main__":
    main()