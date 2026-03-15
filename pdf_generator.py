from fpdf import FPDF
import os
from utils.config import ConfigManager

class ReceiptGenerator:
    def __init__(self):
        pass

    def generate_receipt(self, data, output_path):
        """
        data = {
            'mosque_name': str,
            'receipt_number': str,
            'participant_name': str,
            'phone': str,
            'shares': int,
            'amount_paid': float,
            'date': str
        }
        """
        pdf = FPDF(format='A5') # A5 is better for receipts
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Background Image (Watermark)
        bg_path = ConfigManager.get("receipt_bg_path")
        if bg_path and os.path.exists(bg_path):
            # Add image to cover the page (A5 size: 148 x 210 mm)
            # Use as watermark with low opacity is not directly supported in standard FPDF 1.7.2
            # So we just place it. Ideally, user provides a light image.
            try:
                pdf.image(bg_path, x=0, y=0, w=148, h=210)
            except Exception:
                pass # Ignore if image format is not supported

        # Border
        pdf.set_line_width(1)
        pdf.rect(5, 5, 138, 200)

        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt=data['mosque_name'], ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 5, txt="Ijtimai Qurbani Management System", ln=True, align='C')
        pdf.ln(5)
        
        # Title
        pdf.set_font("Arial", 'B', 14)
        # Check if we should use fill (might cover bg) - let's keep it transparent or minimal
        pdf.set_fill_color(220, 220, 220) 
        pdf.cell(0, 10, txt="OFFICIAL RECEIPT", ln=True, align='C', fill=True)
        pdf.ln(5)

        # Info Grid
        pdf.set_font("Arial", size=11)
        
        # Row 1: Receipt No & Date
        pdf.cell(65, 8, txt=f"Receipt No: {data['receipt_number']}", border=0)
        pdf.cell(65, 8, txt=f"Date: {data['date']}", border=0, align='R', ln=True)
        pdf.ln(2)
        
        pdf.line(10, pdf.get_y(), 138, pdf.get_y())
        pdf.ln(5)

        # Participant Info
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Received From:", border=0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=data['participant_name'], ln=True)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Phone:", border=0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=data['phone'], ln=True)
        
        pdf.ln(5)
        
        # Payment Table
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(80, 8, txt="Description", border=1, fill=True)
        pdf.cell(50, 8, txt="Amount (PKR)", border=1, fill=True, align='R', ln=True)
        
        pdf.set_font("Arial", size=11)
        pdf.cell(80, 8, txt=f"Qurbani Shares ({data['shares']})", border=1)
        pdf.cell(50, 8, txt=f"{data['amount_paid']:,.2f}", border=1, align='R', ln=True)
        
        # Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(80, 10, txt="Total Received", border=1, align='R')
        pdf.cell(50, 10, txt=f"{data['amount_paid']:,.2f}", border=1, align='R', ln=True)
        
        pdf.ln(15)

        # QR Code (Optional)
        try:
            import qrcode
            qr = qrcode.make(f"{data['receipt_number']}|{data['amount_paid']}")
            qr_path = "temp_qr.png"
            qr.save(qr_path)
            pdf.image(qr_path, x=105, y=pdf.get_y(), w=25)
            os.remove(qr_path)
        except ImportError:
            pass # Skip if qrcode lib not installed

        # Footer
        pdf.set_y(-40)
        pdf.set_font("Arial", size=10)
        pdf.cell(60, 5, "_______________________", ln=0, align='C')
        pdf.cell(10, 5, "", ln=0)
        pdf.cell(60, 5, "_______________________", ln=1, align='C')
        pdf.cell(60, 5, "Authorized Signature", ln=0, align='C')
        pdf.cell(10, 5, "", ln=0)
        pdf.cell(60, 5, "Stamp", ln=1, align='C')
        
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, "Note: This receipt is computer generated and valid for claim.", ln=True, align='C')

        pdf.output(output_path)

    def print_receipt(self, output_path):
        if os.name == 'nt':
            os.startfile(output_path, "print")
        else:
            # Linux/Mac placeholder
            pass