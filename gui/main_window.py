import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
from pdf_generator import ReceiptGenerator
from gui.participant_form import ParticipantForm
from gui.animal_form import AnimalForm
from gui.payment_form import PaymentForm
from gui.allocate_form import AllocateForm
from gui.report_window import ReportWindow
from gui.styles import apply_styles
from datetime import datetime
import os

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.pdf_gen = ReceiptGenerator()
        
        # Apply Styles
        self.style = apply_styles(self.root)
        
        self.create_widgets()
        self.load_dashboard_stats()

    def create_widgets(self):
        self.root.title("Ijtimai Qurbani Management System - Professional Edition")
        self.root.geometry("1000x700")

        # Main Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Ijtimai Qurbani Management System", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Backup Database", command=self.backup_db).pack(side=tk.RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 1. Dashboard Tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.setup_dashboard(self.dashboard_tab)

        # 2. Participants Tab
        self.participants_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.participants_tab, text="Participants")
        self.setup_participants_tab(self.participants_tab)

        # 3. Animals Tab
        self.animals_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.animals_tab, text="Animals")
        self.setup_animals_tab(self.animals_tab)

        # 4. Allocation & Payments Tab (Combined for workflow)
        self.allocation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.allocation_tab, text="Allocation & Payments")
        self.setup_allocation_tab(self.allocation_tab)

        # 5. Receipt Verification Tab
        self.verification_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.verification_tab, text="Verify Receipt")
        self.setup_verification_tab(self.verification_tab)

        # 6. Meat Distribution Tab
        self.distribution_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.distribution_tab, text="Distribution")
        self.setup_distribution_tab(self.distribution_tab)

        # 7. Reports Tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        self.setup_reports_tab(self.reports_tab)

        # Refresh data on tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        if tab_name == "Dashboard":
            self.load_dashboard_stats()
        elif tab_name == "Participants":
            self.load_participants()
        elif tab_name == "Animals":
            self.load_animals()
        elif tab_name == "Distribution":
            self.load_distribution()

    # --- Dashboard ---
    def setup_dashboard(self, parent):
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Stats Cards
        self.create_stat_card(stats_frame, "Total Participants", "0", 0)
        self.create_stat_card(stats_frame, "Total Animals", "0", 1)
        self.create_stat_card(stats_frame, "Shares Sold", "0", 2)
        self.create_stat_card(stats_frame, "Money Collected", "Rs. 0", 3)
        self.create_stat_card(stats_frame, "Pending Shares", "0", 4)

        # Refresh Button
        ttk.Button(parent, text="Refresh Dashboard", command=self.load_dashboard_stats).pack(pady=20)

    def create_stat_card(self, parent, title, value, col):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        ttk.Label(card, text=title, font=("Segoe UI", 10)).pack()
        label = ttk.Label(card, text=value, font=("Segoe UI", 14, "bold"), foreground="#4CAF50")
        label.pack()
        # Store reference to update later
        setattr(self, f"stat_{title.lower().replace(' ', '_')}", label)

    def load_dashboard_stats(self):
        stats = self.db.get_dashboard_stats()
        self.stat_total_participants.config(text=str(stats['participants']))
        self.stat_total_animals.config(text=str(stats['animals']))
        self.stat_shares_sold.config(text=str(stats['shares_sold']))
        self.stat_money_collected.config(text=f"Rs. {stats['collected']:,.0f}")
        self.stat_pending_shares.config(text=str(stats['pending_shares']))

    # --- Participants ---
    def setup_participants_tab(self, parent):
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="Add Participant", command=self.add_participant).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Edit Selected", command=self.edit_participant).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_participant, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Generate Receipt", command=self.generate_receipt).pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.load_participants())
        ttk.Entry(toolbar, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Treeview
        cols = ("ID", "Name", "Phone", "CNIC", "Shares", "Total Cost", "Paid", "Balance")
        self.part_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.part_tree.heading(col, text=col)
            self.part_tree.column(col, width=100)
        self.part_tree.pack(fill=tk.BOTH, expand=True)

    def load_participants(self):
        query = self.search_var.get()
        for row in self.part_tree.get_children():
            self.part_tree.delete(row)
        for p in self.db.get_participants(query):
            # p = (id, name, phone, address, cnic, shares, total, paid, created)
            # Calculate balance
            balance = p[6] - p[7]  # total - paid
            self.part_tree.insert("", tk.END, values=(p[0], p[1], p[2], p[4], p[5], f"{p[6]:,.0f}", f"{p[7]:,.0f}", f"{balance:,.0f}"))

    def add_participant(self):
        ParticipantForm(self.root, self.db, self.load_participants)

    def edit_participant(self):
        sel = self.part_tree.selection()
        if sel:
            pid = self.part_tree.item(sel[0])['values'][0]
            ParticipantForm(self.root, self.db, self.load_participants, pid)
        else:
            messagebox.showwarning("Warning", "Select a participant")

    def delete_participant(self):
        sel = self.part_tree.selection()
        if sel:
            pid = self.part_tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Confirm", "Delete this participant? This action cannot be undone."):
                self.db.delete_participant(pid)
                self.load_participants()
        else:
            messagebox.showwarning("Warning", "Select a participant")

    def generate_receipt(self):
        sel = self.part_tree.selection()
        if sel:
            item = self.part_tree.item(sel[0])['values']
            pid = item[0]
            name = item[1]
            phone = item[2]
            shares = item[4]
            paid = float(str(item[6]).replace(',', ''))
            
            if paid <= 0:
                messagebox.showwarning("Warning", "Cannot generate receipt for 0 payment.")
                return

            # Generate Receipt Number and Record in DB
            receipt_no = self.db.create_receipt(pid, paid)
            
            receipt_data = {
                'mosque_name': 'Jamia Masjid Qurbani Center',
                'receipt_number': receipt_no,
                'participant_name': name,
                'phone': phone,
                'shares': shares,
                'amount_paid': paid,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            # Create receipts folder
            if not os.path.exists("receipts"):
                os.makedirs("receipts")
                
            output_path = f"receipts/Receipt_{receipt_no}.pdf"
            self.pdf_gen.generate_receipt(receipt_data, output_path)
            
            if messagebox.askyesno("Success", f"Receipt generated: {output_path}\nDo you want to print it now?"):
                self.pdf_gen.print_receipt(output_path)
        else:
            messagebox.showwarning("Warning", "Select a participant")

    # --- Animals ---
    def setup_animals_tab(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="Add New Animal", command=self.add_animal).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Edit Selected", command=self.edit_animal).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Delete Animal", command=self.delete_animal, style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        cols = ("ID", "Type", "Price", "Seller", "Total Shares", "Remaining")
        self.animal_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.animal_tree.heading(col, text=col)
        self.animal_tree.pack(fill=tk.BOTH, expand=True)
        self.load_animals()

    def load_animals(self):
        for row in self.animal_tree.get_children():
            self.animal_tree.delete(row)
        for a in self.db.get_animals():
            self.animal_tree.insert("", tk.END, values=(a[0], a[1], f"{a[2]:,.0f}", a[3], a[4], a[5]))

    def add_animal(self):
        AnimalForm(self.root, self.db, self.load_animals)

    def edit_animal(self):
        sel = self.animal_tree.selection()
        if sel:
            aid = self.animal_tree.item(sel[0])['values'][0]
            AnimalForm(self.root, self.db, self.load_animals, aid)
        else:
            messagebox.showwarning("Warning", "Select an animal to edit")

    def delete_animal(self):
        sel = self.animal_tree.selection()
        if sel:
            aid = self.animal_tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Confirm", "Delete this animal?"):
                success = self.db.delete_animal(aid)
                if success:
                    self.load_animals()
                else:
                    messagebox.showerror("Error", "Cannot delete animal with allocated shares.")
        else:
            messagebox.showwarning("Warning", "Select an animal")

    # --- Allocation & Payments ---
    def setup_allocation_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Split into two columns
        left_frame = ttk.LabelFrame(frame, text="Allocate Share", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        right_frame = ttk.LabelFrame(frame, text="Record Payment", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Allocation
        ttk.Label(left_frame, text="Use the dedicated form to allocate shares.").pack(pady=10)
        ttk.Button(left_frame, text="Open Allocation Form", command=self.open_allocate_form).pack(pady=10)

        # Payment
        ttk.Label(right_frame, text="Record payments for participants.").pack(pady=10)
        ttk.Button(right_frame, text="Open Payment Form", command=self.open_payment_form).pack(pady=10)

    def open_allocate_form(self):
        AllocateForm(self.root, self.db, self.load_dashboard_stats)

    def open_payment_form(self):
        PaymentForm(self.root, self.db, self.load_dashboard_stats)

    # --- Verification ---
    def setup_verification_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Enter Receipt Number:", style="SubHeader.TLabel").pack(pady=10)
        self.verify_entry = ttk.Entry(frame, font=("Arial", 14))
        self.verify_entry.pack(pady=5, ipadx=50)
        
        ttk.Button(frame, text="Verify Receipt", command=self.verify_receipt).pack(pady=10)

        self.verify_result_frame = ttk.Frame(frame, style="Card.TFrame", padding=20)
        self.verify_result_frame.pack(pady=20, fill=tk.X)
        self.verify_result_label = ttk.Label(self.verify_result_frame, text="Enter a number to verify.", font=("Arial", 12))
        self.verify_result_label.pack()

    def verify_receipt(self):
        receipt_no = self.verify_entry.get().strip()
        if not receipt_no:
            return
        
        result = self.db.verify_receipt(receipt_no)
        
        for widget in self.verify_result_frame.winfo_children():
            widget.destroy()

        if result:
            # Valid
            self.verify_result_frame.configure(style="Card.TFrame") # Reset or set green border style if possible
            tk.Label(self.verify_result_frame, text="✔ VALID RECEIPT", fg="green", font=("Arial", 18, "bold"), bg="white").pack()
            ttk.Label(self.verify_result_frame, text=f"Receipt No: {result[0]}").pack()
            ttk.Label(self.verify_result_frame, text=f"Participant: {result[1]}").pack()
            ttk.Label(self.verify_result_frame, text=f"Amount: Rs. {result[2]:,.0f}").pack()
            ttk.Label(self.verify_result_frame, text=f"Date: {result[3]}").pack()
        else:
            # Invalid
            tk.Label(self.verify_result_frame, text="✘ INVALID / FAKE RECEIPT", fg="red", font=("Arial", 18, "bold"), bg="white").pack()
            ttk.Label(self.verify_result_frame, text=f"No record found for: {receipt_no}").pack()

    # --- Distribution ---
    def setup_distribution_tab(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="Mark Delivered / Undelivered", command=self.toggle_delivery).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh List", command=self.load_distribution).pack(side=tk.LEFT, padx=5)

        cols = ("ID", "Name", "Phone", "Status", "Time")
        self.dist_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.dist_tree.heading(col, text=col)
        self.dist_tree.pack(fill=tk.BOTH, expand=True)

    def load_distribution(self):
        for row in self.dist_tree.get_children():
            self.dist_tree.delete(row)
        for d in self.db.get_distributions():
            # d = (id, name, phone, delivered, delivered_at)
            status = "DELIVERED" if d[3] else "Pending"
            time = d[4] if d[4] else "-"
            # Color code? Treeview tags needed for color
            self.dist_tree.insert("", tk.END, values=(d[0], d[1], d[2], status, time))

    def toggle_delivery(self):
        sel = self.dist_tree.selection()
        if sel:
            pid = self.dist_tree.item(sel[0])['values'][0]
            self.db.toggle_delivery(pid)
            self.load_distribution()
        else:
            messagebox.showwarning("Warning", "Select a participant")

    # --- Reports ---
    def setup_reports_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Generate Reports", style="SubHeader.TLabel").pack(pady=10)
        
        ttk.Button(frame, text="Export Participants List (Excel)", command=lambda: self.export_report("participants")).pack(pady=5, fill=tk.X)
        ttk.Button(frame, text="Export Financial Report (Excel)", command=lambda: self.export_report("finance")).pack(pady=5, fill=tk.X)
        
    def export_report(self, report_type):
        # Placeholder for export logic. Can use openpyxl or pandas.
        # Since requirements.txt has openpyxl
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if not save_path:
                return

            if report_type == "participants":
                ws.append(["ID", "Name", "Phone", "CNIC", "Shares", "Total Cost", "Paid", "Balance"])
                for p in self.db.get_participants():
                     ws.append([p[0], p[1], p[2], p[4], p[5], p[6], p[7], p[6]-p[7]])
            
            elif report_type == "finance":
                ws.append(["Receipt No", "Participant", "Amount", "Date"])
                # Ideally fetch receipts join participants
                conn = self.db.get_connection()
                rows = conn.execute("SELECT r.receipt_no, p.name, r.amount, r.date FROM receipts r JOIN participants p ON r.participant_id = p.id").fetchall()
                conn.close()
                for r in rows:
                    ws.append(list(r))
            
            wb.save(save_path)
            messagebox.showinfo("Success", f"Report saved to {save_path}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def backup_db(self):
        backup_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.backup_database(backup_path)
            messagebox.showinfo("Success", "Database backed up")

    def restore_db(self):
        backup_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.restore_database(backup_path)
            self.load_dashboard_stats()
            messagebox.showinfo("Success", "Database restored")