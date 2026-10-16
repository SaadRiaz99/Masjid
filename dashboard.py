
import tkinter as tk
from tkinter import ttk


class DraieDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("DRAIE - Disaster Resource Management")
        self.root.geometry("850x550")
        self.root.minsize(700, 450)

        self.create_widgets()

    def create_widgets(self):
        title = ttk.Label(
            self.root,
            text="DRAIE Operations Dashboard",
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(pady=(25, 5))

        subtitle = ttk.Label(
            self.root,
            text="Disaster Resource Allocator & Inventory Engine",
            font=("Segoe UI", 10),
        )
        subtitle.pack(pady=(0, 25))

        modules = ttk.Frame(self.root, padding=20)
        modules.pack(fill="both", expand=True)

        buttons = [
            ("Inventory Management", self.show_inventory),
            ("Regional Management", self.show_regions),
            ("Resource Allocation", self.show_allocation),
            ("Users & Roles", self.show_users),
        ]

        for index, (label, command) in enumerate(buttons):
            button = ttk.Button(
                modules,
                text=label,
                command=command,
            )
            button.grid(
                row=index // 2,
                column=index % 2,
                padx=15,
                pady=15,
                ipadx=20,
                ipady=25,
                sticky="nsew",
            )

        modules.columnconfigure(0, weight=1)
        modules.columnconfigure(1, weight=1)
        modules.rowconfigure(0, weight=1)
        modules.rowconfigure(1, weight=1)

        self.status = ttk.Label(
            self.root,
            text="System ready | Backend not connected",
            anchor="w",
            padding=10,
        )
        self.status.pack(fill="x", side="bottom")

    def show_inventory(self):
        self.status.config(text="Inventory Management selected")

    def show_regions(self):
        self.status.config(text="Regional Management selected")

    def show_allocation(self):
        self.status.config(text="Resource Allocation selected")

    def show_users(self):
        self.status.config(text="Users & Roles selected")


def main():
    root = tk.Tk()
    DraieDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
