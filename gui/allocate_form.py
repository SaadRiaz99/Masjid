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
        self.top.geometry("400x350")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Participant:").pack(anchor=tk.W, pady=(0, 5))
        self.participant_var = tk.StringVar()
        self.participant_combo = ttk.Combobox(main_frame, textvariable=self.participant_var, state="readonly")
        self.participant_combo['values'] = [f"{p[0]} - {p[1]}" for p in self.db.get_participants()]
        self.participant_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Animal:").pack(anchor=tk.W, pady=(0, 5))
        self.animal_var = tk.StringVar()
        self.animal_combo = ttk.Combobox(main_frame, textvariable=self.animal_var, state="readonly")
        self.animal_combo['values'] = [f"{a[0]} - {a[1]} ({a[6]} remaining)" for a in self.db.get_animals()]
        self.animal_combo.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Number of Shares:").pack(anchor=tk.W, pady=(0, 5))
        self.shares_entry = ttk.Entry(main_frame)
        self.shares_entry.insert(0, "1")
        self.shares_entry.pack(fill=tk.X, pady=(0, 15))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Allocate", command=self.allocate, style="TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def allocate(self):
        participant_str = self.participant_var.get()
        animal_str = self.animal_var.get()
        try:
            num_shares = int(self.shares_entry.get() or 1)
        except ValueError:
            messagebox.showerror("Error", "Invalid number of shares")
            return

        if not participant_str or not animal_str:
            messagebox.showerror("Error", "All fields required")
            return
        
        participant_id = int(participant_str.split(' - ')[0])
        animal_id = int(animal_str.split(' - ')[0])
        
        success, message = self.db.allocate_shares(participant_id, animal_id, num_shares)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_callback()
            self.top.destroy()
        else:
            messagebox.showerror("Error", message)