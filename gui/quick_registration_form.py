import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
from utils.localization import Localization
from utils.config import ConfigManager, DATA_DIR

class QuickRegistrationForm:
    def __init__(self, parent, db, pdf_gen, refresh_callback):
        self.parent = parent
        self.db = db
        self.pdf_gen = pdf_gen
        self.refresh_callback = refresh_callback
        
        self.frame = ttk.Frame(parent, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        # Header
        ttk.Label(self.frame, text=Localization.t("quick_register_header"), style="Header.TLabel").pack(pady=(0, 20))

        # Main Layout - 2 Columns
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_col = ttk.LabelFrame(content_frame, text=Localization.t("participant_info"), padding=15)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_col = ttk.LabelFrame(content_frame, text=Localization.t("allocation_payment"), padding=15)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- Left Column: Participant ---
        # Name
        ttk.Label(left_col, text=Localization.t("name")).pack(anchor=tk.W)
        self.name_entry = ttk.Entry(left_col)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        # Phone
        ttk.Label(left_col, text=Localization.t("phone")).pack(anchor=tk.W)
        self.phone_entry = ttk.Entry(left_col)
        self.phone_entry.pack(fill=tk.X, pady=(0, 10))

        # CNIC
        ttk.Label(left_col, text=Localization.t("cnic")).pack(anchor=tk.W)
        self.cnic_entry = ttk.Entry(left_col)
        self.cnic_entry.pack(fill=tk.X, pady=(0, 10))

        # Address
        ttk.Label(left_col, text="Address").pack(anchor=tk.W)
        self.address_entry = ttk.Entry(left_col)
        self.address_entry.pack(fill=tk.X, pady=(0, 10))

        # --- Right Column: Allocation & Payment ---
        # Shares
        ttk.Label(right_col, text="Number of Shares (Hisse)").pack(anchor=tk.W)
        self.shares_var = tk.StringVar(value="1")
        self.shares_entry = ttk.Entry(right_col, textvariable=self.shares_var)
        self.shares_entry.pack(fill=tk.X, pady=(0, 10))
        self.shares_var.trace("w", self.on_shares_change)

        # Animal Selection
        self.animal_label = ttk.Label(right_col, text=Localization.t("select_animal"))
        self.animal_label.pack(anchor=tk.W)
        self.animal_var = tk.StringVar()
        self.animal_combo = ttk.Combobox(right_col, textvariable=self.animal_var, state="readonly")
        self.animal_combo.pack(fill=tk.X, pady=(0, 10))
        self.update_animal_list()
        
        # Category (Waqf/Qurbani)
        ttk.Label(right_col, text="Category (Qurbani/Waqf)").pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="Qurbani")
        self.category_combo = ttk.Combobox(right_col, textvariable=self.category_var, values=["Qurbani", "Waqf"], state="readonly")
        self.category_combo.pack(fill=tk.X, pady=(0, 10))

        # Payment
        ttk.Label(right_col, text=Localization.t("amount_paid")).pack(anchor=tk.W)
        self.amount_entry = ttk.Entry(right_col)
        self.amount_entry.pack(fill=tk.X, pady=(0, 10))

        # Action Button
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        self.register_btn = ttk.Button(btn_frame, text=Localization.t("register_print"), command=self.process_registration, style="Success.TButton")
        self.register_btn.pack(fill=tk.X, ipady=10)

    def on_shares_change(self, *args):
        try:
            shares = int(self.shares_var.get() or 0)
            if shares == 7:
                self.animal_label.config(text="Select Animal (Or New Cow will be created)")
            else:
                self.animal_label.config(text=Localization.t("select_animal"))
        except ValueError:
            pass

    def update_animal_list(self):
        animals = self.db.get_animals()
        # Filter only animals with remaining shares
        # a = (id, type, price, actual_price, seller, total, rem, category, status, date)
        available = [f"{a[0]} - {a[1]} (Rem: {a[6]} | Cost: {int(a[2]/a[5])})" for a in animals if a[6] > 0]
        self.animal_combo['values'] = available

    def process_registration(self):
        # 1. Validation
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        cnic = self.cnic_entry.get().strip()
        address = self.address_entry.get().strip()
        animal_sel = self.animal_var.get()
        amount_str = self.amount_entry.get().strip()
        try:
            num_shares = int(self.shares_var.get() or 1)
        except ValueError:
            messagebox.showerror("Error", "Invalid number of shares")
            return

        if not name or not amount_str:
            messagebox.showerror(Localization.t("error"), "Name and Amount are required.")
            return

        # Special logic for 7 shares
        animal_id = None
        if num_shares == 7 and not animal_sel:
            if messagebox.askyesno("Animal Distribution", "7 shares completed. Would you like to automatically create a new Cow for this user?"):
                # Automatically create a cow
                # Default values for automatic cow creation
                animal_id = self.db.add_animal("cow", 210000, "Auto-Created", 7)
            else:
                if not animal_sel:
                    messagebox.showerror(Localization.t("error"), "Please select an animal or confirm auto-creation.")
                    return

        if not animal_id:
            try:
                animal_id = int(animal_sel.split(' - ')[0])
            except (ValueError, IndexError):
                messagebox.showerror(Localization.t("error"), "Invalid Animal selection.")
                return

        try:
            amount_paid = float(amount_str)
        except ValueError:
            messagebox.showerror(Localization.t("error"), "Invalid Amount.")
            return

        # 2. Add Participant
        participant_id = self.db.add_participant(name, phone, address, cnic)
        if not participant_id:
            messagebox.showerror(Localization.t("error"), "Failed to add participant (CNIC might be duplicate).")
            return

        # 3. Allocate Shares
        success, msg = self.db.allocate_shares(participant_id, animal_id, num_shares)
        if not success:
            messagebox.showerror(Localization.t("error"), f"Allocation failed: {msg}")
            return

        # 4. Add Payment
        self.db.add_payment(participant_id, amount_paid)

        # 5. Generate Receipt
        receipt_no = self.db.create_receipt(participant_id, amount_paid)
        
        # Get latest participant data for receipt
        p = self.db.get_participant(participant_id)
        
        # Get animal type for receipt
        animal = self.db.get_animal(animal_id)
        animal_type = animal[1] if animal else "Unknown"
        
        receipt_data = {
            'mosque_name': ConfigManager.get("mosque_name", "Ijtimai Qurbani Center"),
            'receipt_number': receipt_no,
            'participant_name': name,
            'phone': str(phone),
            'cnic': cnic,
            'animal_type': animal_type,
            'category': self.category_var.get(),
            'shares': str(num_shares),
            'amount_paid': str(amount_paid),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        if not os.path.exists(os.path.join(DATA_DIR, "receipts")):
            os.makedirs(os.path.join(DATA_DIR, "receipts"))
            
        output_path = os.path.join(DATA_DIR, "receipts", f"Receipt_{receipt_no}.pdf")
        self.pdf_gen.generate_receipt(receipt_data, output_path)
        
        # 6. Print & Cleanup
        try:
            self.pdf_gen.print_receipt(output_path)
        except Exception:
            pass # Printing might fail if no default printer
            
        messagebox.showinfo(Localization.t("success"), f"Registration Complete!\nReceipt: {receipt_no}")
        
        # Clear form
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.cnic_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.shares_var.set("1")
        self.animal_var.set("")
        
        # Refresh Data
        self.update_animal_list()
        self.refresh_callback()