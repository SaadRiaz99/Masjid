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
        self.top.title("Add/Edit Participant")
        self.create_widgets()
        if participant_id:
            self.load_participant()

    def create_widgets(self):
        tk.Label(self.top, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = tk.Entry(self.top)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Phone:").grid(row=1, column=0, padx=10, pady=5)
        self.phone_entry = tk.Entry(self.top)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Address:").grid(row=2, column=0, padx=10, pady=5)
        self.address_entry = tk.Entry(self.top)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.top, text="CNIC:").grid(row=3, column=0, padx=10, pady=5)
        self.cnic_entry = tk.Entry(self.top)
        self.cnic_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self.top, text="Save", command=self.save).grid(row=4, column=0, pady=10)
        tk.Button(self.top, text="Cancel", command=self.top.destroy).grid(row=4, column=1, pady=10)

    def load_participant(self):
        # Load data if editing
        participants = self.db.get_participants()
        for p in participants:
            if p[0] == self.participant_id:
                self.name_entry.insert(0, p[1])
                self.phone_entry.insert(0, p[2])
                self.address_entry.insert(0, p[3])
                self.cnic_entry.insert(0, p[4])
                break

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