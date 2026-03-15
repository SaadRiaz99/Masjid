import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from pdf_generator import ReceiptGenerator
from gui.participant_form import ParticipantForm
from gui.animal_form import AnimalForm
from gui.payment_form import PaymentForm
from gui.allocate_form import AllocateForm
from datetime import datetime
import os

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.pdf_gen = ReceiptGenerator()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.root.title("Ijtimai Qurbani Management System")
        self.root.geometry("800x600")

        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_db)
        file_menu.add_command(label="Restore Database", command=self.restore_db)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        manage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=manage_menu)
        manage_menu.add_command(label="Add Participant", command=self.add_participant)
        manage_menu.add_command(label="Add Animal", command=self.add_animal)
        manage_menu.add_command(label="Allocate Share", command=self.allocate_share)
        manage_menu.add_command(label="Record Payment", command=self.record_payment)

        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=report_menu)
        report_menu.add_command(label="View Reports", command=self.view_reports)

        # Dashboard
        self.dashboard_frame = tk.Frame(self.root)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Stats
        stats_frame = tk.Frame(self.dashboard_frame)
        stats_frame.pack(pady=10)

        self.participants_label = tk.Label(stats_frame, text="Total Participants: 0", font=("Arial", 12))
        self.participants_label.grid(row=0, column=0, padx=10)

        self.animals_label = tk.Label(stats_frame, text="Total Animals: 0", font=("Arial", 12))
        self.animals_label.grid(row=0, column=1, padx=10)

        self.shares_label = tk.Label(stats_frame, text="Shares Sold: 0", font=("Arial", 12))
        self.shares_label.grid(row=0, column=2, padx=10)

        self.money_label = tk.Label(stats_frame, text="Money Collected: Rs. 0", font=("Arial", 12))
        self.money_label.grid(row=0, column=3, padx=10)

        # Tabs
        self.tab_control = ttk.Notebook(self.dashboard_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        # Participants Tab
        self.participants_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.participants_tab, text="Participants")

        self.participants_tree = ttk.Treeview(self.participants_tab, columns=("ID", "Name", "Phone", "Shares", "Cost"), show="headings")
        self.participants_tree.heading("ID", text="ID")
        self.participants_tree.heading("Name", text="Name")
        self.participants_tree.heading("Phone", text="Phone")
        self.participants_tree.heading("Shares", text="Shares")
        self.participants_tree.heading("Cost", text="Total Cost")
        self.participants_tree.pack(fill=tk.BOTH, expand=True)

        participants_buttons = tk.Frame(self.participants_tab)
        participants_buttons.pack(fill=tk.X)
        tk.Button(participants_buttons, text="Edit", command=self.edit_participant).pack(side=tk.LEFT, padx=5)
        tk.Button(participants_buttons, text="Delete", command=self.delete_participant).pack(side=tk.LEFT, padx=5)
        tk.Button(participants_buttons, text="Generate Receipt", command=self.generate_receipt).pack(side=tk.LEFT, padx=5)
        tk.Button(participants_buttons, text="Mark Delivered", command=self.mark_delivered).pack(side=tk.LEFT, padx=5)

        # Animals Tab
        self.animals_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.animals_tab, text="Animals")

        self.animals_tree = ttk.Treeview(self.animals_tab, columns=("ID", "Type", "Price", "Total Shares", "Remaining"), show="headings")
        self.animals_tree.heading("ID", text="ID")
        self.animals_tree.heading("Type", text="Type")
        self.animals_tree.heading("Price", text="Purchase Price")
        self.animals_tree.heading("Total Shares", text="Total Shares")
        self.animals_tree.heading("Remaining", text="Remaining Shares")
        self.animals_tree.pack(fill=tk.BOTH, expand=True)

        # Search
        search_frame = tk.Frame(self.dashboard_frame)
        search_frame.pack(fill=tk.X, pady=5)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Search", command=self.search_participants).pack(side=tk.LEFT)

    def load_data(self):
        # Load stats
        self.participants_label.config(text=f"Total Participants: {self.db.get_total_participants()}")
        self.animals_label.config(text=f"Total Animals: {self.db.get_total_animals()}")
        self.shares_label.config(text=f"Shares Sold: {self.db.get_total_shares_sold()}")
        self.money_label.config(text=f"Money Collected: Rs. {self.db.get_total_money_collected()}")

        # Load participants
        for row in self.participants_tree.get_children():
            self.participants_tree.delete(row)
        for participant in self.db.get_participants():
            self.participants_tree.insert("", tk.END, values=participant)

        # Load animals
        for row in self.animals_tree.get_children():
            self.animals_tree.delete(row)
        for animal in self.db.get_animals():
            self.animals_tree.insert("", tk.END, values=animal)

    def add_participant(self):
        ParticipantForm(self.root, self.db, self.load_data)

    def add_animal(self):
        AnimalForm(self.root, self.db, self.load_data)

    def allocate_share(self):
        AllocateForm(self.root, self.db, self.load_data)

    def record_payment(self):
        PaymentForm(self.root, self.db, self.load_data)

    def view_reports(self):
        ReportWindow(self.root, self.db)

    def edit_participant(self):
        selected = self.participants_tree.selection()
        if selected:
            item = self.participants_tree.item(selected[0])
            participant_id = item['values'][0]
            ParticipantForm(self.root, self.db, self.load_data, participant_id)
        else:
            messagebox.showwarning("Warning", "Select a participant to edit")

    def delete_participant(self):
        selected = self.participants_tree.selection()
        if selected:
            item = self.participants_tree.item(selected[0])
            participant_id = item['values'][0]
            if messagebox.askyesno("Confirm", "Delete this participant?"):
                self.db.delete_participant(participant_id)
                self.load_data()
        else:
            messagebox.showwarning("Warning", "Select a participant to delete")

    def generate_receipt(self):
        selected = self.participants_tree.selection()
        if selected:
            item = self.participants_tree.item(selected[0])
            participant_id = item['values'][0]
            name = item['values'][1]
            phone = item['values'][2]
            shares = item['values'][3]
            cost = item['values'][4]
            # Assume share price is fixed, say 2500 per share
            share_price = 2500
            receipt_data = {
                'mosque_name': 'Masjid-e-Example',
                'receipt_number': f"R{participant_id:03d}",
                'participant_name': name,
                'phone': phone,
                'shares': shares,
                'amount_paid': cost,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            output_path = f"receipt_{participant_id}.pdf"
            self.pdf_gen.generate_receipt(receipt_data, output_path)
            messagebox.showinfo("Success", f"Receipt saved as {output_path}")
            # Print
            self.pdf_gen.print_receipt(output_path)
        else:
            messagebox.showwarning("Warning", "Select a participant")

    def mark_delivered(self):
        selected = self.participants_tree.selection()
        if selected:
            item = self.participants_tree.item(selected[0])
            participant_id = item['values'][0]
            self.db.mark_delivered(participant_id)
            messagebox.showinfo("Success", "Marked as delivered")
        else:
            messagebox.showwarning("Warning", "Select a participant")

    def search_participants(self):
        query = self.search_entry.get()
        # Simple search by name
        for row in self.participants_tree.get_children():
            self.participants_tree.delete(row)
        for participant in self.db.get_participants():
            if query.lower() in participant[1].lower():
                self.participants_tree.insert("", tk.END, values=participant)

    def backup_db(self):
        backup_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.backup_database(backup_path)
            messagebox.showinfo("Success", "Database backed up")

    def restore_db(self):
        backup_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.restore_database(backup_path)
            self.load_data()
            messagebox.showinfo("Success", "Database restored")