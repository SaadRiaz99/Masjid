import sqlite3
import os
import sys
import shutil
from datetime import datetime
from utils.config import DATA_DIR

class Database:
    def __init__(self, db_path='qurbani.db'):
        self.db_path = os.path.join(DATA_DIR, db_path)
        if getattr(sys, 'frozen', False) and not os.path.exists(self.db_path):
            bundle_db = os.path.join(sys._MEIPASS, db_path)
            if os.path.exists(bundle_db):
                shutil.copy(bundle_db, self.db_path)
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
                participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                animal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_type TEXT NOT NULL,  -- cow, goat, camel
                purchase_price REAL NOT NULL,
                actual_buy_price REAL DEFAULT 0.0,
                seller_details TEXT,
                total_shares INTEGER NOT NULL,
                remaining_shares INTEGER NOT NULL,
                category TEXT DEFAULT 'Qurbani', -- Qurbani, Waqf
                status TEXT DEFAULT 'Available', -- Available, Completed
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Shares allocation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                share_id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                animal_id INTEGER,
                share_number INTEGER,
                allocated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES participants (participant_id),
                FOREIGN KEY (animal_id) REFERENCES animals (animal_id)
            )
        ''')

        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                amount REAL NOT NULL,
                payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
            )
        ''')

        # Receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_no TEXT UNIQUE NOT NULL,
                participant_id INTEGER,
                amount REAL NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
            )
        ''')

        # Meat distribution
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS distributions (
                dist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                delivered BOOLEAN DEFAULT FALSE,
                delivered_at TEXT,
                FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
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

        # Migration: Add category to animals if missing
        try:
            cursor.execute("SELECT category FROM animals LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE animals ADD COLUMN category TEXT DEFAULT 'Qurbani'")

        # Migration: Add status to animals if missing
        try:
            cursor.execute("SELECT status FROM animals LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE animals ADD COLUMN status TEXT DEFAULT 'Available'")

        # Migration: Add paid_amount to participants if missing
        try:
            cursor.execute("SELECT paid_amount FROM participants LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE participants ADD COLUMN paid_amount REAL DEFAULT 0.0")

        # Migration: Add actual_buy_price to animals if missing
        try:
            cursor.execute("SELECT actual_buy_price FROM animals LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE animals ADD COLUMN actual_buy_price REAL DEFAULT 0.0")

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_name ON participants(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_animals_category ON animals(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_animals_status ON animals(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shares_animal ON shares(animal_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shares_participant ON shares(participant_id)")

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
        cursor.execute("SELECT * FROM participants WHERE participant_id = ?", (participant_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_participant(self, participant_id, name, phone, address, cnic):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE participants
            SET name = ?, phone = ?, address = ?, cnic = ?
            WHERE participant_id = ?
        ''', (name, phone, address, cnic, participant_id))
        conn.commit()
        conn.close()

    def delete_participant(self, participant_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Check if they have payments or shares
        cursor.execute("SELECT COUNT(*) FROM shares WHERE participant_id = ?", (participant_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Cannot delete participant with allocated shares."
            
        cursor.execute("DELETE FROM participants WHERE participant_id = ?", (participant_id,))
        cursor.execute("DELETE FROM distributions WHERE participant_id = ?", (participant_id,))
        cursor.execute("DELETE FROM payments WHERE participant_id = ?", (participant_id,))
        conn.commit()
        conn.close()
        return True, "Deleted successfully"

    # Animal methods
    def add_animal(self, animal_type, purchase_price, seller_details, total_shares, actual_buy_price=0.0, category='Qurbani'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO animals (animal_type, purchase_price, seller_details, total_shares, remaining_shares, actual_buy_price, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (animal_type, purchase_price, seller_details, total_shares, total_shares, actual_buy_price, category))
        animal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return animal_id

    def get_animals(self, animal_type=None, category=None, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM animals WHERE 1=1"
        params = []
        if animal_type and animal_type != "All":
            query += " AND animal_type = ?"
            params.append(animal_type)
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if status and status != "All":
            query += " AND status = ?"
            params.append(status)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_animal(self, animal_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM animals WHERE animal_id = ?", (animal_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_animal(self, animal_id, animal_type, price, seller, total_shares, actual_buy_price=0.0, category='Qurbani', status='Available'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE animals
            SET animal_type = ?, purchase_price = ?, seller_details = ?, total_shares = ?, actual_buy_price = ?, category = ?, status = ?
            WHERE animal_id = ?
        ''', (animal_type, price, seller, total_shares, actual_buy_price, category, status, animal_id))
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
        cursor.execute("DELETE FROM animals WHERE animal_id = ?", (animal_id,))
        conn.commit()
        conn.close()
        return True

    # Share allocation
    def allocate_shares(self, participant_id, animal_id, num_shares=1):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get animal details
        cursor.execute("SELECT remaining_shares, purchase_price, total_shares, actual_buy_price FROM animals WHERE animal_id = ?", (animal_id,))
        animal_data = cursor.fetchone()
        if not animal_data or animal_data[0] < num_shares:
            conn.close()
            return False, f"Not enough shares available (Available: {animal_data[0] if animal_data else 0})"

        remaining, price, total_shares, actual_price = animal_data

        # Use actual price if set, otherwise estimated price
        cost_basis = actual_price if actual_price > 0 else price
        share_cost = (cost_basis / total_shares) * num_shares

        try:
            # Allocate
            for i in range(num_shares):
                cursor.execute('''
                    INSERT INTO shares (participant_id, animal_id, share_number)
                    VALUES (?, ?, ?)
                ''', (participant_id, animal_id, total_shares - remaining + 1 + i))

            # Update animal
            new_remaining = remaining - num_shares
            new_status = 'Completed' if new_remaining == 0 else 'Available'
            cursor.execute("UPDATE animals SET remaining_shares = ?, status = ? WHERE animal_id = ?", (new_remaining, new_status, animal_id))

            # Update participant
            cursor.execute("UPDATE participants SET shares_purchased = shares_purchased + ?, total_cost = total_cost + ? WHERE participant_id = ?", (num_shares, share_cost, participant_id))

            conn.commit()
            return True, f"{num_shares} shares allocated successfully"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def allocate_share(self, participant_id, animal_id):
        return self.allocate_shares(participant_id, animal_id, 1)

    # Payment methods
    def add_payment(self, participant_id, amount):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (participant_id, amount)
            VALUES (?, ?)
        ''', (participant_id, amount))

        # Update participant paid amount
        cursor.execute("UPDATE participants SET paid_amount = paid_amount + ? WHERE participant_id = ?", (amount, participant_id))

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
            JOIN participants p ON r.participant_id = p.participant_id
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
            SELECT p.participant_id, p.name, p.phone, d.delivered, d.delivered_at
            FROM participants p
            LEFT JOIN distributions d ON p.participant_id = d.participant_id
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
                INSERT OR REPLACE INTO distributions (dist_id, participant_id, delivered, delivered_at)
                VALUES ((SELECT dist_id FROM distributions WHERE participant_id = ?), ?, TRUE, ?)
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

        # Advanced Stats
        stats['waqf_animals'] = cursor.execute("SELECT COUNT(*) FROM animals WHERE category = 'Waqf'").fetchone()[0]
        stats['qurbani_animals'] = cursor.execute("SELECT COUNT(*) FROM animals WHERE category = 'Qurbani'").fetchone()[0]

        cursor.execute("SELECT animal_type, COUNT(*) FROM animals GROUP BY animal_type")
        stats['type_breakdown'] = dict(cursor.fetchall())

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