import tkinter as tk
from tkinter import messagebox
from database import Database

class ParticipantForm:
    def __init__(self, parent, db, refresh_callback, participant_id=None):
        self.parent = parent
        self.db = db
        self.refresh_callback = refresh_callback
        self.participant_id = participant_id
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Participant" if participant_id else "Add Participant")
        self.top.geometry("400x450")
        self.create_widgets()
        if participant_id:
            self.load_participant()

    def create_widgets(self):
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Name:").pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Phone:").pack(anchor=tk.W, pady=(0, 5))
        self.phone_entry = ttk.Entry(main_frame)
        self.phone_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="Address:").pack(anchor=tk.W, pady=(0, 5))
        self.address_entry = ttk.Entry(main_frame)
        self.address_entry.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(main_frame, text="CNIC:").pack(anchor=tk.W, pady=(0, 5))
        self.cnic_entry = ttk.Entry(main_frame)
        self.cnic_entry.pack(fill=tk.X, pady=(0, 15))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save, style="TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def load_participant(self):
        p = self.db.get_participant(self.participant_id)
        if p:
            self.name_entry.insert(0, p[1])
            self.phone_entry.insert(0, p[2])
            self.address_entry.insert(0, p[3])
            self.cnic_entry.insert(0, p[4])

    def save(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()
        cnic = self.cnic_entry.get()
        if not name or not cnic:
            messagebox.showerror("Error", "Name and CNIC are required")
            return
        if self.participant_id:
            self.db.update_participant(self.participant_id, name, phone, address, cnic)
        else:
            self.db.add_participant(name, phone, address, cnic)
        self.refresh_callback()
        self.top.destroy()