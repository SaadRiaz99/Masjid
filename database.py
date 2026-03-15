import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='qurbani.db'):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

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
                status TEXT DEFAULT 'completed',  -- completed, pending
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

        conn.commit()
        conn.close()

    # Participant methods
    def add_participant(self, name, phone, address, cnic):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO participants (name, phone, address, cnic)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, address, cnic))
        participant_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return participant_id

    def get_participants(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM participants")
        rows = cursor.fetchall()
        conn.close()
        return rows

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

    # Share allocation
    def allocate_share(self, participant_id, animal_id, share_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Check if share is available
        cursor.execute("SELECT remaining_shares FROM animals WHERE id = ?", (animal_id,))
        remaining = cursor.fetchone()[0]
        if remaining > 0:
            cursor.execute('''
                INSERT INTO shares (participant_id, animal_id, share_number)
                VALUES (?, ?, ?)
            ''', (participant_id, animal_id, share_number))
            cursor.execute("UPDATE animals SET remaining_shares = remaining_shares - 1 WHERE id = ?", (animal_id,))
            # Update participant shares
            cursor.execute("UPDATE participants SET shares_purchased = shares_purchased + 1 WHERE id = ?", (participant_id,))
            cursor.execute("UPDATE participants SET total_cost = shares_purchased * 2500 WHERE id = ?", (participant_id,))
            conn.commit()
            success = True
        else:
            success = False
        conn.close()
        return success

    # Payment methods
    def add_payment(self, participant_id, amount, status='completed'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (participant_id, amount, status)
            VALUES (?, ?, ?)
        ''', (participant_id, amount, status))
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id

    def get_payments(self, participant_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if participant_id:
            cursor.execute("SELECT * FROM payments WHERE participant_id = ?", (participant_id,))
        else:
            cursor.execute("SELECT * FROM payments")
        rows = cursor.fetchall()
        conn.close()
        return rows

    # Distribution
    def mark_delivered(self, participant_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE distributions
            SET delivered = TRUE, delivered_at = ?
            WHERE participant_id = ?
        ''', (datetime.now().isoformat(), participant_id))
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO distributions (participant_id, delivered, delivered_at)
                VALUES (?, TRUE, ?)
            ''', (participant_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    # Reports
    def get_total_participants(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM participants")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_total_animals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM animals")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_total_shares_sold(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(shares_purchased) FROM participants")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total

    def get_total_money_collected(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'completed'")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total

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