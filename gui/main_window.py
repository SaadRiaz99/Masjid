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
from gui.change_password_dialog import ChangePasswordDialog
from gui.quick_registration_form import QuickRegistrationForm
from utils.localization import Localization
from utils.config import ConfigManager
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
        self.root.title(Localization.t("title"))
        self.root.geometry("1000x700")

        # Main Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text=Localization.t("title"), style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text=Localization.t("backup_db"), command=self.backup_db).pack(side=tk.RIGHT)

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 1. Dashboard Tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text=Localization.t("dashboard"))
        self.setup_dashboard(self.dashboard_tab)

        # 2. Participants Tab
        self.participants_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.participants_tab, text=Localization.t("participants"))
        self.setup_participants_tab(self.participants_tab)

        # 3. Animals Tab
        self.animals_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.animals_tab, text=Localization.t("animals"))
        self.setup_animals_tab(self.animals_tab)

        # 4. Allocation & Payments Tab
        self.allocation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.allocation_tab, text=Localization.t("allocation"))
        self.setup_allocation_tab(self.allocation_tab)

        # 5. Receipt Verification Tab
        self.verification_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.verification_tab, text=Localization.t("verify"))
        self.setup_verification_tab(self.verification_tab)

        # 6. Meat Distribution Tab
        self.distribution_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.distribution_tab, text=Localization.t("distribution"))
        self.setup_distribution_tab(self.distribution_tab)

        # 7. Reports Tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text=Localization.t("reports"))
        self.setup_reports_tab(self.reports_tab)

        # 8. Settings Tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text=Localization.t("settings"))
        self.setup_settings_tab(self.settings_tab)

        # Refresh data on tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # We can't rely on tab name if it's localized, so we check index or just reload based on visible content?
        # Better: just use index or check which tab object is selected.
        selected_tab = self.notebook.select()
        
        if selected_tab == str(self.dashboard_tab):
            self.load_dashboard_stats()
        elif selected_tab == str(self.participants_tab):
            self.load_participants()
        elif selected_tab == str(self.animals_tab):
            self.load_animals()
        elif selected_tab == str(self.distribution_tab):
            self.load_distribution()

    # --- Dashboard ---
    def setup_dashboard(self, parent):
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Stats Cards
        self.create_stat_card(stats_frame, Localization.t("total_participants"), "0", 0)
        self.create_stat_card(stats_frame, Localization.t("total_animals"), "0", 1)
        self.create_stat_card(stats_frame, Localization.t("shares_sold"), "0", 2)
        self.create_stat_card(stats_frame, Localization.t("money_collected"), "Rs. 0", 3)
        self.create_stat_card(stats_frame, Localization.t("pending_shares"), "0", 4)

        # Refresh Button
        ttk.Button(parent, text=Localization.t("refresh_dashboard"), command=self.load_dashboard_stats).pack(pady=20)

    def create_stat_card(self, parent, title, value, col):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        ttk.Label(card, text=title, font=("Segoe UI", 10)).pack()
        # Mapping title to attribute name is tricky with localization.
        # We will map by column index logic or just use specific attribute names if needed.
        # Let's verify load_dashboard_stats updates correct labels.
        # Since I create them dynamically here, I need a way to reference them.
        # Simple fix: Store them in a dict or list by index.
        label = ttk.Label(card, text=value, font=("Segoe UI", 14, "bold"), foreground="#4CAF50")
        label.pack()
        
        if col == 0: self.stat_participants = label
        elif col == 1: self.stat_animals = label
        elif col == 2: self.stat_shares = label
        elif col == 3: self.stat_money = label
        elif col == 4: self.stat_pending = label

    def load_dashboard_stats(self):
        stats = self.db.get_dashboard_stats()
        self.stat_participants.config(text=str(stats['participants']))
        self.stat_animals.config(text=str(stats['animals']))
        self.stat_shares.config(text=str(stats['shares_sold']))
        self.stat_money.config(text=f"Rs. {stats['collected']:,.0f}")
        self.stat_pending.config(text=str(stats['pending_shares']))

    # --- Participants ---
    def setup_participants_tab(self, parent):
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text=Localization.t("add_participant"), command=self.add_participant).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("edit_selected"), command=self.edit_participant).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("delete_selected"), command=self.delete_participant, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("generate_receipt"), command=self.generate_receipt).pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(toolbar, text=Localization.t("search")).pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.load_participants())
        ttk.Entry(toolbar, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Treeview
        cols = ("ID", Localization.t("name"), Localization.t("phone"), Localization.t("cnic"), Localization.t("shares"), Localization.t("cost"), Localization.t("paid"), Localization.t("balance"))
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
            balance = p[6] - p[7]
            self.part_tree.insert("", tk.END, values=(p[0], p[1], p[2], p[4], p[5], f"{p[6]:,.0f}", f"{p[7]:,.0f}", f"{balance:,.0f}"))

    def add_participant(self):
        ParticipantForm(self.root, self.db, self.load_participants)

    def edit_participant(self):
        sel = self.part_tree.selection()
        if sel:
            pid = self.part_tree.item(sel[0])['values'][0]
            ParticipantForm(self.root, self.db, self.load_participants, pid)
        else:
            messagebox.showwarning(Localization.t("warning"), "Select a participant")

    def delete_participant(self):
        sel = self.part_tree.selection()
        if sel:
            pid = self.part_tree.item(sel[0])['values'][0]
            if messagebox.askyesno(Localization.t("warning"), Localization.t("confirm_delete")):
                self.db.delete_participant(pid)
                self.load_participants()
        else:
            messagebox.showwarning(Localization.t("warning"), "Select a participant")

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
                messagebox.showwarning(Localization.t("warning"), "Cannot generate receipt for 0 payment.")
                return

            receipt_no = self.db.create_receipt(pid, paid)
            
            receipt_data = {
                'mosque_name': ConfigManager.get("mosque_name", "Ijtimai Qurbani Center"),
                'receipt_number': receipt_no,
                'participant_name': name,
                'phone': str(phone),
                'cnic': str(cnic),
                'animal_type': 'Qurbani Share',
                'shares': str(shares),
                'amount_paid': str(paid),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            if not os.path.exists("receipts"):
                os.makedirs("receipts")
                
            output_path = f"receipts/Receipt_{receipt_no}.pdf"
            self.pdf_gen.generate_receipt(receipt_data, output_path)
            
            if messagebox.askyesno(Localization.t("success"), f"Receipt generated: {output_path}\nDo you want to print it now?"):
                self.pdf_gen.print_receipt(output_path)
        else:
            messagebox.showwarning(Localization.t("warning"), "Select a participant")

    # --- Animals ---
    def setup_animals_tab(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text=Localization.t("add_animal"), command=self.add_animal).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("edit_selected"), command=self.edit_animal).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("delete_animal"), command=self.delete_animal, style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        cols = ("ID", Localization.t("type"), Localization.t("price"), "Buy Price", Localization.t("seller"), Localization.t("total"), Localization.t("remaining"))
        self.animal_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.animal_tree.heading(col, text=col)
        self.animal_tree.pack(fill=tk.BOTH, expand=True)
        self.load_animals()

    def load_animals(self):
        for row in self.animal_tree.get_children():
            self.animal_tree.delete(row)
        for a in self.db.get_animals():
            # a = (id, type, price, actual_buy_price, seller, total, rem, date)
            # Display prices formatted
            price = f"{a[2]:,.0f}"
            actual = f"{a[3]:,.0f}" if a[3] else "-"
            self.animal_tree.insert("", tk.END, values=(a[0], a[1], price, actual, a[4], a[5], a[6]))

    def add_animal(self):
        AnimalForm(self.root, self.db, self.load_animals)

    def edit_animal(self):
        sel = self.animal_tree.selection()
        if sel:
            aid = self.animal_tree.item(sel[0])['values'][0]
            AnimalForm(self.root, self.db, self.load_animals, aid)
        else:
            messagebox.showwarning(Localization.t("warning"), "Select an animal")

    def delete_animal(self):
        sel = self.animal_tree.selection()
        if sel:
            aid = self.animal_tree.item(sel[0])['values'][0]
            if messagebox.askyesno(Localization.t("warning"), Localization.t("confirm_delete")):
                success = self.db.delete_animal(aid)
                if success:
                    self.load_animals()
                else:
                    messagebox.showerror(Localization.t("error"), "Cannot delete animal with allocated shares.")
        else:
            messagebox.showwarning(Localization.t("warning"), "Select an animal")

    # --- Allocation & Payments ---
    def setup_allocation_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(frame, text=Localization.t("allocate_share"), padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        right_frame = ttk.LabelFrame(frame, text=Localization.t("record_payment"), padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        ttk.Button(left_frame, text=Localization.t("allocate_share"), command=self.open_allocate_form).pack(pady=20)
        ttk.Button(right_frame, text=Localization.t("record_payment"), command=self.open_payment_form).pack(pady=20)

    def open_allocate_form(self):
        AllocateForm(self.root, self.db, self.load_dashboard_stats)

    def open_payment_form(self):
        PaymentForm(self.root, self.db, self.load_dashboard_stats)

    # --- Verification ---
    def setup_verification_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=Localization.t("receipt_no"), style="SubHeader.TLabel").pack(pady=10)
        self.verify_entry = ttk.Entry(frame, font=("Arial", 14))
        self.verify_entry.pack(pady=5, ipadx=50)
        
        ttk.Button(frame, text=Localization.t("verify_receipt"), command=self.verify_receipt).pack(pady=10)

        self.verify_result_frame = ttk.Frame(frame, style="Card.TFrame", padding=20)
        self.verify_result_frame.pack(pady=20, fill=tk.X)
        self.verify_result_label = ttk.Label(self.verify_result_frame, text="...", font=("Arial", 12))
        self.verify_result_label.pack()

    def verify_receipt(self):
        receipt_no = self.verify_entry.get().strip()
        if not receipt_no: return
        result = self.db.verify_receipt(receipt_no)
        for widget in self.verify_result_frame.winfo_children(): widget.destroy()

        if result:
            self.verify_result_frame.configure(style="Card.TFrame")
            tk.Label(self.verify_result_frame, text=Localization.t("valid_receipt"), fg="green", font=("Arial", 18, "bold"), bg="white").pack()
            ttk.Label(self.verify_result_frame, text=f"Receipt No: {result[0]}").pack()
            ttk.Label(self.verify_result_frame, text=f"{Localization.t('name')}: {result[1]}").pack()
            ttk.Label(self.verify_result_frame, text=f"Amount: Rs. {result[2]:,.0f}").pack()
            ttk.Label(self.verify_result_frame, text=f"Date: {result[3]}").pack()
        else:
            tk.Label(self.verify_result_frame, text=Localization.t("invalid_receipt"), fg="red", font=("Arial", 18, "bold"), bg="white").pack()

    # --- Distribution ---
    def setup_distribution_tab(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text=Localization.t("mark_delivered"), command=self.toggle_delivery).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text=Localization.t("refresh_list"), command=self.load_distribution).pack(side=tk.LEFT, padx=5)

        cols = ("ID", Localization.t("name"), Localization.t("phone"), Localization.t("status"), Localization.t("time"))
        self.dist_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.dist_tree.heading(col, text=col)
        self.dist_tree.pack(fill=tk.BOTH, expand=True)

    def load_distribution(self):
        for row in self.dist_tree.get_children():
            self.dist_tree.delete(row)
        for d in self.db.get_distributions():
            status = Localization.t("delivered") if d[3] else Localization.t("pending")
            time = d[4] if d[4] else "-"
            self.dist_tree.insert("", tk.END, values=(d[0], d[1], d[2], status, time))

    def toggle_delivery(self):
        sel = self.dist_tree.selection()
        if sel:
            pid = self.dist_tree.item(sel[0])['values'][0]
            self.db.toggle_delivery(pid)
            self.load_distribution()
        else:
            messagebox.showwarning(Localization.t("warning"), "Select a participant")

    # --- Reports ---
    def setup_reports_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Button(frame, text=Localization.t("export_participants"), command=lambda: self.export_report("participants")).pack(pady=5, fill=tk.X)
        ttk.Button(frame, text=Localization.t("export_finance"), command=lambda: self.export_report("finance")).pack(pady=5, fill=tk.X)

    def export_report(self, report_type):
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if not save_path: return

            if report_type == "participants":
                ws.append(["ID", "Name", "Phone", "CNIC", "Shares", "Total Cost", "Paid", "Balance"])
                for p in self.db.get_participants():
                     ws.append([p[0], p[1], p[2], p[4], p[5], p[6], p[7], p[6]-p[7]])
            elif report_type == "finance":
                ws.append(["Receipt No", "Participant", "Amount", "Date"])
                conn = self.db.get_connection()
                rows = conn.execute("SELECT r.receipt_no, p.name, r.amount, r.date FROM receipts r JOIN participants p ON r.participant_id = p.id").fetchall()
                conn.close()
                for r in rows: ws.append(list(r))
            
            wb.save(save_path)
            messagebox.showinfo(Localization.t("success"), f"Report saved to {save_path}")
        except Exception as e:
            messagebox.showerror(Localization.t("error"), str(e))

    # --- Settings ---
    def setup_settings_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Language
        ttk.Label(frame, text=Localization.t("language"), style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.lang_var = tk.StringVar(value=Localization.get_language())
        lang_frame = ttk.Frame(frame)
        lang_frame.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Radiobutton(lang_frame, text=Localization.t("english"), variable=self.lang_var, value="en", command=self.save_language).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(lang_frame, text=Localization.t("urdu"), variable=self.lang_var, value="ur", command=self.save_language).pack(side=tk.LEFT, padx=10)

        # Receipt Background
        ttk.Label(frame, text=Localization.t("receipt_bg"), style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        bg_frame = ttk.Frame(frame)
        bg_frame.pack(anchor=tk.W, pady=(0, 10))
        
        self.bg_label = ttk.Label(bg_frame, text=ConfigManager.get("receipt_bg_path") or "No Image Selected")
        self.bg_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(bg_frame, text=Localization.t("set_bg"), command=self.set_receipt_bg).pack(side=tk.LEFT, padx=5)
        ttk.Button(bg_frame, text=Localization.t("remove_bg"), command=self.remove_receipt_bg).pack(side=tk.LEFT, padx=5)

        # Password
        ttk.Label(frame, text=Localization.t("change_password"), style="SubHeader.TLabel").pack(anchor=tk.W, pady=(20, 5))
        ttk.Button(frame, text=Localization.t("change_password"), command=self.open_change_password).pack(anchor=tk.W)

    def open_change_password(self):
        ChangePasswordDialog(self.root, self.db)

    def save_language(self):
        new_lang = self.lang_var.get()
        if new_lang != Localization.get_language():
            Localization.set_language(new_lang)
            messagebox.showinfo(Localization.t("language"), Localization.t("restart_required"))

    def set_receipt_bg(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            ConfigManager.set("receipt_bg_path", path)
            self.bg_label.config(text=path)
            messagebox.showinfo(Localization.t("success"), "Background image saved.")

    def remove_receipt_bg(self):
        ConfigManager.set("receipt_bg_path", None)
        self.bg_label.config(text="No Image Selected")
        messagebox.showinfo(Localization.t("success"), "Background image removed.")

    def backup_db(self):
        backup_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.backup_database(backup_path)
            messagebox.showinfo(Localization.t("success"), "Database backed up")

    def restore_db(self):
        backup_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if backup_path:
            self.db.restore_database(backup_path)
            self.load_dashboard_stats()
            messagebox.showinfo(Localization.t("success"), "Database restored")

    # --- Settings ---
    def setup_settings_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Language Selection
        ttk.Label(frame, text=Localization.t("language")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lang_var = tk.StringVar(value=ConfigManager.get("language", "en"))
        lang_combo = ttk.Combobox(frame, textvariable=self.lang_var, values=["en", "ur"], state="readonly")
        lang_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)

        # Mosque Name
        ttk.Label(frame, text=Localization.t("mosque_name")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.mosque_entry = ttk.Entry(frame)
        self.mosque_entry.insert(0, ConfigManager.get("mosque_name", "Ijtimai Qurbani Center"))
        self.mosque_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Receipt Background
        ttk.Label(frame, text=Localization.t("receipt_bg")).grid(row=2, column=0, sticky=tk.W, pady=5)
        bg_frame = ttk.Frame(frame)
        bg_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.bg_path_var = tk.StringVar(value=ConfigManager.get("receipt_bg_path", ""))
        ttk.Entry(bg_frame, textvariable=self.bg_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(bg_frame, text=Localization.t("set_bg"), command=self.set_receipt_bg).pack(side=tk.LEFT, padx=5)
        ttk.Button(bg_frame, text=Localization.t("remove_bg"), command=self.remove_receipt_bg).pack(side=tk.LEFT)

        # Password Change
        ttk.Button(frame, text=Localization.t("change_password"), command=self.change_password).grid(row=3, column=0, columnspan=2, pady=20)

        # Save Button
        ttk.Button(frame, text=Localization.t("save"), command=self.save_settings).grid(row=4, column=0, columnspan=2)

    def change_language(self, event):
        lang = self.lang_var.get()
        ConfigManager.set("language", lang)
        messagebox.showinfo(Localization.t("restart_required"), Localization.t("restart_required"))

    def set_receipt_bg(self):
        bg_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if bg_path:
            self.bg_path_var.set(bg_path)
            ConfigManager.set("receipt_bg_path", bg_path)
            messagebox.showinfo(Localization.t("success"), "Background image set.")

    def remove_receipt_bg(self):
        self.bg_path_var.set("")
        ConfigManager.set("receipt_bg_path", "")
        messagebox.showinfo(Localization.t("success"), "Background image removed.")

    def change_password(self):
        ChangePasswordDialog(self.root, self.db)

    def save_settings(self):
        mosque_name = self.mosque_entry.get()
        ConfigManager.set("mosque_name", mosque_name)
        messagebox.showinfo(Localization.t("success"), "Settings saved.")