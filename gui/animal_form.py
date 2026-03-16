import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AnimalForm:
    def __init__(self, parent, db, refresh_callback, animal_id=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.animal_id = animal_id
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Animal" if animal_id else "Add Animal")
        self.top.geometry("400x450")
        self.create_widgets()
        if animal_id:
            self.load_animal()

    def create_widgets(self):
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Animal Type:").pack(anchor=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, values=["cow", "goat", "camel"], state="readonly")
        self.type_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Total/Est. Price:").pack(anchor=tk.W, pady=(0, 5))
        self.price_entry = ttk.Entry(main_frame)
        self.price_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Actual Buy Price:").pack(anchor=tk.W, pady=(0, 5))
        self.actual_price_entry = ttk.Entry(main_frame)
        self.actual_price_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Seller Details:").pack(anchor=tk.W, pady=(0, 5))
        self.seller_entry = ttk.Entry(main_frame)
        self.seller_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Total Shares:").pack(anchor=tk.W, pady=(0, 5))
        self.shares_entry = ttk.Entry(main_frame)
        self.shares_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Category:").pack(anchor=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar(value="Qurbani")
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, values=["Qurbani", "Waqf"], state="readonly")
        self.category_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Status:").pack(anchor=tk.W, pady=(0, 5))
        self.status_var = tk.StringVar(value="Available")
        self.status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, values=["Available", "Completed"], state="readonly")
        self.status_combo.pack(fill=tk.X, pady=(0, 15))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save, style="TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def load_animal(self):
        a = self.db.get_animal(self.animal_id)
        if a:
            # a = (id, type, price, actual_price, seller, total, remaining, category, status, date)
            self.type_var.set(a[1])
            self.price_entry.insert(0, str(a[2]))
            self.actual_price_entry.insert(0, str(a[3]))
            self.seller_entry.insert(0, str(a[4]))
            self.shares_entry.insert(0, str(a[5]))
            self.category_var.set(a[7])
            self.status_var.set(a[8])

    def save(self):
        animal_type = self.type_var.get()
        category = self.category_var.get()
        status = self.status_var.get()
        try:
            price = float(self.price_entry.get() or 0)
            actual_price = float(self.actual_price_entry.get() or 0)
            shares = int(self.shares_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or shares")
            return

        seller = self.seller_entry.get()

        if not animal_type or price <= 0 or shares <= 0:
            messagebox.showerror("Error", "All fields are required and valid")
            return

        if self.animal_id:
            self.db.update_animal(self.animal_id, animal_type, price, seller, shares, actual_price, category, status)
            messagebox.showinfo("Success", "Animal updated")
        else:
            self.db.add_animal(animal_type, price, seller, shares, actual_price, category)
            messagebox.showinfo("Success", "Animal added")

        self.refresh_callback()
        self.top.destroy()