import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class PaymentForm:
    def __init__(self, parent, db, refresh_callback):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.top = tk.Toplevel(parent)
        self.top.title("Record Payment")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.top, text="Participant:").grid(row=0, column=0, padx=10, pady=5)
        self.participant_var = tk.StringVar()
        self.participant_combo = ttk.Combobox(self.top, textvariable=self.participant_var)
        self.participant_combo['values'] = [f"{p[0]} - {p[1]}" for p in self.db.get_participants()]
        self.participant_combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Amount:").grid(row=1, column=0, padx=10, pady=5)
        self.amount_entry = tk.Entry(self.top)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Status:").grid(row=2, column=0, padx=10, pady=5)
        self.status_var = tk.StringVar(value="completed")
        self.status_combo = ttk.Combobox(self.top, textvariable=self.status_var, values=["completed", "pending"])
        self.status_combo.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self.top, text="Save", command=self.save).grid(row=3, column=0, pady=10)
        tk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=3, column=1, pady=10)

    def save(self):
        participant_str = self.participant_var.get()
        if not participant_str:
            messagebox.showerror("Error", "Select a participant")
            return
        participant_id = int(participant_str.split(' - ')[0])
        amount = float(self.amount_entry.get() or 0)
        status = self.status_var.get()
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive")
            return
        self.db.add_payment(participant_id, amount, status)
        self.refresh_callback()
        self.top.destroy()