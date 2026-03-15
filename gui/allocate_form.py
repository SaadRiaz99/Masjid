import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AllocateForm:
    def __init__(self, parent, db, refresh_callback):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.top = tk.Toplevel(parent)
        self.top.title("Allocate Share")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.top, text="Participant:").grid(row=0, column=0, padx=10, pady=5)
        self.participant_var = tk.StringVar()
        self.participant_combo = ttk.Combobox(self.top, textvariable=self.participant_var)
        self.participant_combo['values'] = [f"{p[0]} - {p[1]}" for p in self.db.get_participants()]
        self.participant_combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Animal:").grid(row=1, column=0, padx=10, pady=5)
        self.animal_var = tk.StringVar()
        self.animal_combo = ttk.Combobox(self.top, textvariable=self.animal_var)
        self.animal_combo['values'] = [f"{a[0]} - {a[1]} ({a[5]} remaining)" for a in self.db.get_animals()]
        self.animal_combo.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.top, text="Allocate", command=self.allocate).grid(row=2, column=0, pady=20)
        tk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=2, column=1, pady=20)

    def allocate(self):
        participant_str = self.participant_var.get()
        animal_str = self.animal_var.get()
        if not participant_str or not animal_str:
            messagebox.showerror("Error", "All fields required")
            return
        
        participant_id = int(participant_str.split(' - ')[0])
        animal_id = int(animal_str.split(' - ')[0])
        
        success, message = self.db.allocate_share(participant_id, animal_id)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_callback()
            self.top.destroy()
        else:
            messagebox.showerror("Error", message)