import tkinter as tk
from tkinter import messagebox
from utils.localization import Localization

class ChangePasswordDialog:
    def __init__(self, parent, db, username="admin"):
        self.parent = parent
        self.db = db
        self.username = username
        self.top = tk.Toplevel(parent)
        self.top.title(Localization.t("settings"))
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.top, text="Current Password:").grid(row=0, column=0, padx=10, pady=5)
        self.current_pwd = tk.Entry(self.top, show="*")
        self.current_pwd.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.top, text="New Password:").grid(row=1, column=0, padx=10, pady=5)
        self.new_pwd = tk.Entry(self.top, show="*")
        self.new_pwd.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.top, text="Confirm New Password:").grid(row=2, column=0, padx=10, pady=5)
        self.confirm_pwd = tk.Entry(self.top, show="*")
        self.confirm_pwd.grid(row=2, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self.top)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text=Localization.t("save"), command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=Localization.t("cancel"), command=self.top.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        curr = self.current_pwd.get()
        new_p = self.new_pwd.get()
        conf = self.confirm_pwd.get()

        if not curr or not new_p or not conf:
            messagebox.showerror(Localization.t("error"), "All fields are required")
            return

        if new_p != conf:
            messagebox.showerror(Localization.t("error"), "New passwords do not match")
            return

        if not self.db.authenticate_admin(self.username, curr):
            messagebox.showerror(Localization.t("error"), "Incorrect current password")
            return

        self.db.update_admin_password(self.username, new_p)
        messagebox.showinfo(Localization.t("success"), "Password updated successfully")
        self.top.destroy()