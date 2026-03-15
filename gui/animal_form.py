import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AnimalForm:
    def __init__(self, parent, db, refresh_callback):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.top = tk.Toplevel(parent)
        self.top.title("Add Animal")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.top, text="Animal Type:").grid(row=0, column=0, padx=10, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self.top, textvariable=self.type_var, values=["cow", "goat", "camel"])
        self.type_combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Purchase Price:").grid(row=1, column=0, padx=10, pady=5)
        self.price_entry = tk.Entry(self.top)
        self.price_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Seller Details:").grid(row=2, column=0, padx=10, pady=5)
        self.seller_entry = tk.Entry(self.top)
        self.seller_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Total Shares:").grid(row=3, column=0, padx=10, pady=5)
        self.shares_entry = tk.Entry(self.top)
        self.shares_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self.top, text="Save", command=self.save).grid(row=4, column=0, pady=10)
        tk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=4, column=1, pady=10)

    def save(self):
        animal_type = self.type_var.get()
        price = float(self.price_entry.get() or 0)
        seller = self.seller_entry.get()
        shares = int(self.shares_entry.get() or 0)
        if not animal_type or price <= 0 or shares <= 0:
            messagebox.showerror("Error", "All fields are required and valid")
            return
        self.db.add_animal(animal_type, price, seller, shares)
        self.refresh_callback()
        self.top.destroy()