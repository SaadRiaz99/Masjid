import unittest
import os
import shutil
from database import Database
from pdf_generator import ReceiptGenerator
from utils.config import DATA_DIR

class TestQurbaniSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a test database
        cls.db_path = "test_qurbani.db"
        if os.path.exists(os.path.join(DATA_DIR, cls.db_path)):
            os.remove(os.path.join(DATA_DIR, cls.db_path))
        cls.db = Database(cls.db_path)
        cls.pdf_gen = ReceiptGenerator()

    def test_1_participant_crud(self):
        # Add
        pid = self.db.add_participant("Test User", "1234567890", "Test Address", "12345-6789012-3")
        self.assertIsNotNone(pid)
        
        # Get
        p = self.db.get_participant(pid)
        self.assertEqual(p[1], "Test User")
        
        # Update
        self.db.update_participant(pid, "Updated User", "0987654321", "New Address", "12345-6789012-3")
        p = self.db.get_participant(pid)
        self.assertEqual(p[1], "Updated User")

    def test_2_animal_crud(self):
        # Add
        aid = self.db.add_animal("cow", 150000, "Test Seller", 7, 0.0, "Waqf")
        self.assertIsNotNone(aid)
        
        # Get
        a = self.db.get_animal(aid)
        self.assertEqual(a[1], "cow")
        self.assertEqual(a[5], 7) # total_shares
        self.assertEqual(a[6], 7) # remaining_shares
        self.assertEqual(a[7], "Waqf") # category

    def test_7_dashboard_stats_advanced(self):
        self.db.add_animal("goat", 50000, "Seller", 1, 0.0, "Qurbani")
        stats = self.db.get_dashboard_stats()
        self.assertIn('waqf_animals', stats)
        self.assertIn('qurbani_animals', stats)
        self.assertTrue(stats['waqf_animals'] >= 1)
        self.assertTrue(stats['qurbani_animals'] >= 1)

    def test_3_allocation(self):
        pid = self.db.add_participant("Alloc User", "111", "Addr", "11111-1111111-1")
        aid = self.db.add_animal("goat", 50000, "Seller", 1)
        
        success, msg = self.db.allocate_shares(pid, aid, 1)
        self.assertTrue(success)
        
        a = self.db.get_animal(aid)
        self.assertEqual(a[6], 0) # remaining_shares should be 0
        
        p = self.db.get_participant(pid)
        self.assertEqual(p[5], 1) # shares_purchased should be 1
        self.assertEqual(p[6], 50000) # total_cost should be 50000

    def test_4_payment_and_receipt(self):
        pid = self.db.add_participant("Pay User", "222", "Addr", "22222-2222222-2")
        self.db.add_payment(pid, 10000)
        
        p = self.db.get_participant(pid)
        self.assertEqual(p[7], 10000) # paid_amount
        
        receipt_no = self.db.create_receipt(pid, 10000)
        self.assertIsNotNone(receipt_no)
        
        # Verify receipt
        r = self.db.verify_receipt(receipt_no)
        self.assertIsNotNone(r)
        self.assertEqual(r[1], "Pay User")
        self.assertEqual(r[2], 10000)

    def test_5_multiple_shares_allocation(self):
        pid = self.db.add_participant("Multi User", "333", "Addr", "33333-3333333-3")
        aid = self.db.add_animal("cow", 210000, "Seller", 7)
        
        success, msg = self.db.allocate_shares(pid, aid, 3)
        self.assertTrue(success)
        
        a = self.db.get_animal(aid)
        self.assertEqual(a[6], 4) # 7 - 3 = 4 remaining
        
        p = self.db.get_participant(pid)
        self.assertEqual(p[5], 3)
        self.assertEqual(p[6], 90000) # (210000/7)*3 = 30000*3 = 90000

    def test_6_pdf_generation(self):
        receipt_data = {
            'mosque_name': "Test Mosque",
            'receipt_number': "TEST-001",
            'participant_name': "PDF Tester",
            'phone': "123",
            'cnic': "123",
            'animal_type': "cow",
            'shares': "1",
            'amount_paid': "30000",
            'date': "2026-03-16"
        }
        output_path = "test_receipt.pdf"
        self.pdf_gen.generate_receipt(receipt_data, output_path)
        self.assertTrue(os.path.exists(output_path))
        # Optional: cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

    @classmethod
    def tearDownClass(cls):
        # Cleanup test database
        if os.path.exists(os.path.join(DATA_DIR, cls.db_path)):
            # Close connection if any? Database class doesn't keep persistent connection
            pass
        # os.remove(os.path.join(DATA_DIR, cls.db_path))

if __name__ == '__main__':
    unittest.main()