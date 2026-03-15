from fpdf import FPDF
import os

class ReceiptGenerator:
    def __init__(self):
        self.pdf = None

    def generate_receipt(self, receipt_data, output_path):
        """
        receipt_data = {
            'mosque_name': 'Mosque Name',
            'receipt_number': '001',
            'participant_name': 'John Doe',
            'phone': '123456789',
            'shares': 2,
            'amount_paid': 5000.0,
            'date': '2023-10-01'
        }
        """
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

        # Header
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(200, 10, txt=receipt_data['mosque_name'], ln=True, align='C')
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt="Qurbani Receipt", ln=True, align='C')
        self.pdf.ln(10)

        # Receipt Number
        self.pdf.cell(200, 10, txt=f"Receipt Number: {receipt_data['receipt_number']}", ln=True)
        self.pdf.ln(5)

        # Participant Details
        self.pdf.cell(200, 10, txt=f"Participant Name: {receipt_data['participant_name']}", ln=True)
        self.pdf.cell(200, 10, txt=f"Phone: {receipt_data['phone']}", ln=True)
        self.pdf.cell(200, 10, txt=f"Shares Purchased: {receipt_data['shares']}", ln=True)
        self.pdf.cell(200, 10, txt=f"Amount Paid: Rs. {receipt_data['amount_paid']:.2f}", ln=True)
        self.pdf.cell(200, 10, txt=f"Date: {receipt_data['date']}", ln=True)
        self.pdf.ln(10)

        # Footer
        self.pdf.set_font("Arial", 'I', 10)
        self.pdf.cell(200, 10, txt="Thank you for your contribution to Qurbani.", ln=True, align='C')

        self.pdf.output(output_path)

    def print_receipt(self, output_path):
        # For Windows, use os.startfile to print
        os.startfile(output_path, "print")