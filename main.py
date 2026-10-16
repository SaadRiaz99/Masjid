from src.models.resource import Resource


def main():
    medicine = Resource("Medicine", 100)
    medicine.display()


if __name__ == "__main__":
    main()