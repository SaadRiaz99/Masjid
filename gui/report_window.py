import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from database import Database
import openpyxl

class ReportWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.top = tk.Toplevel(parent)
        self.top.title("Reports and Analytics")
        self.top.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        # Stats
        stats_frame = tk.Frame(self.top)
        stats_frame.pack(pady=10)

        tk.Label(stats_frame, text=f"Total Participants: {self.db.get_total_participants()}", font=("Arial", 12)).grid(row=0, column=0, padx=10)
        tk.Label(stats_frame, text=f"Total Animals: {self.db.get_total_animals()}", font=("Arial", 12)).grid(row=0, column=1, padx=10)
        tk.Label(stats_frame, text=f"Shares Sold: {self.db.get_total_shares_sold()}", font=("Arial", 12)).grid(row=1, column=0, padx=10)
        tk.Label(stats_frame, text=f"Money Collected: Rs. {self.db.get_total_money_collected()}", font=("Arial", 12)).grid(row=1, column=1, padx=10)

        # Export buttons
        export_frame = tk.Frame(self.top)
        export_frame.pack(pady=10)
        tk.Button(export_frame, text="Export Participants to Excel", command=self.export_participants).pack(side=tk.LEFT, padx=5)
        tk.Button(export_frame, text="Export Payments to Excel", command=self.export_payments).pack(side=tk.LEFT, padx=5)

    def export_participants(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Participants"
            ws.append(["ID", "Name", "Phone", "Address", "CNIC", "Shares Purchased", "Total Cost"])
            for p in self.db.get_participants():
                ws.append(p)
            wb.save(file_path)
            messagebox.showinfo("Success", "Exported to Excel")

    def export_payments(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Payments"
            ws.append(["ID", "Participant ID", "Amount", "Date", "Status"])
            for p in self.db.get_payments():
                ws.append(p)
            wb.save(file_path)
            messagebox.showinfo("Success", "Exported to Excel")