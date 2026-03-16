import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = Database()
        self.create_widgets()

    def create_widgets(self):
        self.root.title("Admin Login - Qurbani Management")
        self.root.geometry("400x350")
        
        # Main Frame
        main_frame = ttk.Frame(self.root, padding=40)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Login Required", style="Header.TLabel").pack(pady=(0, 20))

        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=2)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        self.username_entry.insert(0, "admin")

        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W, pady=2)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))

        # Login Button
        self.login_btn = ttk.Button(main_frame, text="Login", command=self.login, style="TButton")
        self.login_btn.pack(fill=tk.X, pady=20, ipady=5)

        # Software Footer
        ttk.Label(main_frame, text="Software By Saad Bin Riaz 0314 1088892", style="Footer.TLabel").pack(side=tk.BOTTOM)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.db.authenticate_admin(username, password):
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid credentials")