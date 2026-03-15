import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='qurbani.db'):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                cnic TEXT UNIQUE,
                shares_purchased INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                paid_amount REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Animals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_type TEXT NOT NULL,  -- cow, goat, camel
                purchase_price REAL NOT NULL,
                seller_details TEXT,
                total_shares INTEGER NOT NULL,
                remaining_shares INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Shares allocation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                animal_id INTEGER,
                share_number INTEGER,
                allocated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES participants (id),
                FOREIGN KEY (animal_id) REFERENCES animals (id)
            )
        ''')

        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
        ''')

        # Receipts table (New)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_no TEXT UNIQUE NOT NULL,
                participant_id INTEGER,
                amount REAL NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
        ''')

        # Meat distribution
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                delivered BOOLEAN DEFAULT FALSE,
                delivered_at TEXT,
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
        ''')

        # Admin users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT
            )
        ''')

        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            import hashlib
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ('admin', password_hash))

        # Migration: Add paid_amount to participants if missing
        try:
            cursor.execute("SELECT paid_amount FROM participants LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE participants ADD COLUMN paid_amount REAL DEFAULT 0.0")

        conn.commit()
        conn.close()

    # Participant methods
    def add_participant(self, name, phone, address, cnic):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO participants (name, phone, address, cnic)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, address, cnic))
            participant_id = cursor.lastrowid
            # Init distribution record
            cursor.execute("INSERT INTO distributions (participant_id, delivered) VALUES (?, FALSE)", (participant_id,))
            conn.commit()
            return participant_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_participants(self, search_query=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if search_query:
            query = f"%{search_query}%"
            cursor.execute("SELECT * FROM participants WHERE name LIKE ? OR phone LIKE ? OR cnic LIKE ?", (query, query, query))
        else:
            cursor.execute("SELECT * FROM participants")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_participant(self, participant_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_participant(self, participant_id, name, phone, address, cnic):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE participants
            SET name = ?, phone = ?, address = ?, cnic = ?
            WHERE id = ?
        ''', (name, phone, address, cnic, participant_id))
        conn.commit()
        conn.close()

    def delete_participant(self, participant_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM participants WHERE id = ?", (participant_id,))
        cursor.execute("DELETE FROM distributions WHERE participant_id = ?", (participant_id,))
        conn.commit()
        conn.close()

    # Animal methods
    def add_animal(self, animal_type, purchase_price, seller_details, total_shares):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO animals (animal_type, purchase_price, seller_details, total_shares, remaining_shares)
            VALUES (?, ?, ?, ?, ?)
        ''', (animal_type, purchase_price, seller_details, total_shares, total_shares))
        animal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return animal_id

    def get_animals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animals")
        rows = cursor.fetchall()
        conn.close()
        return rows
        
    def get_animal(self, animal_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animals WHERE id = ?", (animal_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_animal(self, animal_id, animal_type, price, seller, total_shares):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Note: updating total shares might be tricky if some are allocated.
        # For simplicity, we update basic info.
        cursor.execute('''
            UPDATE animals
            SET animal_type = ?, purchase_price = ?, seller_details = ?, total_shares = ?
            WHERE id = ?
        ''', (animal_type, price, seller, total_shares, animal_id))
        conn.commit()
        conn.close()
        
    def delete_animal(self, animal_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Check if shares are allocated
        cursor.execute("SELECT COUNT(*) FROM shares WHERE animal_id = ?", (animal_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False # Cannot delete
        cursor.execute("DELETE FROM animals WHERE id = ?", (animal_id,))
        conn.commit()
        conn.close()
        return True

    # Share allocation
    def allocate_share(self, participant_id, animal_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get animal details
        cursor.execute("SELECT remaining_shares, purchase_price, total_shares FROM animals WHERE id = ?", (animal_id,))
        animal_data = cursor.fetchone()
        if not animal_data or animal_data[0] <= 0:
            conn.close()
            return False, "No shares available"
            
        remaining, price, total_shares = animal_data
        share_cost = price / total_shares

        try:
            # Allocate
            cursor.execute('''
                INSERT INTO shares (participant_id, animal_id, share_number)
                VALUES (?, ?, ?)
            ''', (participant_id, animal_id, total_shares - remaining + 1))
            
            # Update animal
            cursor.execute("UPDATE animals SET remaining_shares = remaining_shares - 1 WHERE id = ?", (animal_id,))
            
            # Update participant
            cursor.execute("UPDATE participants SET shares_purchased = shares_purchased + 1, total_cost = total_cost + ? WHERE id = ?", (share_cost, participant_id))
            
            conn.commit()
            return True, "Share allocated successfully"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    # Payment methods
    def add_payment(self, participant_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (participant_id, amount)
            VALUES (?, ?)
        ''', (participant_id, amount))
        
        # Update participant paid amount
        cursor.execute("UPDATE participants SET paid_amount = paid_amount + ? WHERE id = ?", (amount, participant_id))
        
        conn.commit()
        conn.close()
        return True

    # Receipt methods
    def create_receipt(self, participant_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Generate receipt number: R-{YYYY}-{ID}-{Random/Count}
        # Simple auto-increment logic via count for now, or just use DB ID after insert
        count = cursor.execute("SELECT COUNT(*) FROM receipts").fetchone()[0] + 1
        receipt_no = f"R-{datetime.now().year}-{count:04d}"
        
        cursor.execute('''
            INSERT INTO receipts (receipt_no, participant_id, amount)
            VALUES (?, ?, ?)
        ''', (receipt_no, participant_id, amount))
        
        conn.commit()
        conn.close()
        return receipt_no

    def verify_receipt(self, receipt_no):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.receipt_no, p.name, r.amount, r.date 
            FROM receipts r
            JOIN participants p ON r.participant_id = p.id
            WHERE r.receipt_no = ?
        ''', (receipt_no,))
        row = cursor.fetchone()
        conn.close()
        return row

    # Distribution
    def get_distributions(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.phone, d.delivered, d.delivered_at
            FROM participants p
            LEFT JOIN distributions d ON p.id = d.participant_id
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def toggle_delivery(self, participant_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT delivered FROM distributions WHERE participant_id = ?", (participant_id,))
        result = cursor.fetchone()
        
        if result and result[0]: # If delivered, mark undelivered
            cursor.execute("UPDATE distributions SET delivered = FALSE, delivered_at = NULL WHERE participant_id = ?", (participant_id,))
        else: # Mark delivered
             cursor.execute('''
                INSERT OR REPLACE INTO distributions (id, participant_id, delivered, delivered_at)
                VALUES ((SELECT id FROM distributions WHERE participant_id = ?), ?, TRUE, ?)
            ''', (participant_id, participant_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

    # Reports / Stats
    def get_dashboard_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        stats['participants'] = cursor.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        stats['animals'] = cursor.execute("SELECT COUNT(*) FROM animals").fetchone()[0]
        stats['shares_sold'] = cursor.execute("SELECT SUM(shares_purchased) FROM participants").fetchone()[0] or 0
        stats['collected'] = cursor.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0
        stats['pending_shares'] = cursor.execute("SELECT SUM(remaining_shares) FROM animals").fetchone()[0] or 0
        
        conn.close()
        return stats

    # Backup
    def backup_database(self, backup_path):
        import shutil
        shutil.copy(self.db_path, backup_path)

    def restore_database(self, backup_path):
        import shutil
        shutil.copy(backup_path, self.db_path)

    # Auth
    def authenticate_admin(self, username, password):
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def update_admin_password(self, username, new_password):
        import hashlib
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET password_hash = ? WHERE username = ?", (password_hash, username))
        conn.commit()
        conn.close()
        return True