import tkinter as tk
from tkinter import messagebox
from database import Database

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = Database()
        self.create_widgets()

    def create_widgets(self):
        self.root.title("Admin Login")
        self.root.geometry("300x200")

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.db.authenticate_admin(username, password):
            # Don't destroy the root, just signal success
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid credentials")