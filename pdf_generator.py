from fpdf import FPDF
import os
from utils.config import ConfigManager
from utils.localization import Localization

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
            'cnic': str,
            'animal_type': str,
            'shares': str,
            'amount_paid': str,
            'date': str
        }
        """
        lang = ConfigManager.get("language", "en")
        
        # Define labels based on language
        if lang == "ur":
            labels = {
                "receipt": "رسید",
                "mosque": "مسجد",
                "receipt_no": "رسید نمبر",
                "date": "تاریخ",
                "received_from": "وصول کنندہ:",
                "phone": "فون:",
                "cnic": "شناختی کارڈ:",
                "description": "تفصیل",
                "amount_pkr": "رقم (روپے)",
                "total": "کل",
                "footer": "یہ رسید کمپیوٹر سے تیار کی گئی ہے اور دستی دستخط کی ضرورت نہیں۔"
            }
        else:
            labels = {
                "receipt": "RECEIPT",
                "mosque": "Mosque",
                "receipt_no": "Receipt No",
                "date": "Date",
                "received_from": "Received From:",
                "phone": "Phone:",
                "cnic": "CNIC:",
                "description": "Description",
                "amount_pkr": "Amount (PKR)",
                "total": "Total",
                "footer": "This receipt is computer generated and does not require manual signature."
            }
        
        pdf = FPDF(format='A5') # A5 is better for receipts
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Try to set font for Unicode
        try:
            if lang == "ur":
                pdf.set_font("Arial Unicode MS", size=12)
            else:
                pdf.set_font("Arial", size=12)
        except:
            pdf.set_font("Arial", size=12)  # Fallback
        
        # Background Image (Watermark)
        bg_path = ConfigManager.get("receipt_bg_path")
        if bg_path and os.path.exists(bg_path):
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
        pdf.cell(0, 10, txt=labels["receipt"], ln=True, align='C', fill=True)
        pdf.ln(5)

        # Info Grid
        pdf.set_font("Arial", size=11)
        
        # Row 1: Receipt No & Date
        pdf.cell(65, 8, txt=f"{labels['receipt_no']}: {data['receipt_number']}", border=0)
        pdf.cell(65, 8, txt=f"{labels['date']}: {data['date']}", border=0, align='R', ln=True)
        pdf.ln(2)
        
        pdf.line(10, pdf.get_y(), 138, pdf.get_y())
        pdf.ln(5)

        # Participant Info
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt=labels["received_from"], border=0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=data['participant_name'], ln=True)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt=labels["phone"], border=0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=data['phone'], ln=True)
        
        if 'cnic' in data:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(40, 8, txt=labels["cnic"], border=0)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, txt=data['cnic'], ln=True)
        
        pdf.ln(5)
        
        # Payment Table
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(80, 8, txt=labels["description"], border=1, fill=True)
        pdf.cell(50, 8, txt=labels["amount_pkr"], border=1, fill=True, align='R', ln=True)
        
        pdf.set_font("Arial", size=11)
        animal_desc = f"Qurbani Shares - {data.get('animal_type', 'Animal')} ({data['shares']})"
        pdf.cell(80, 8, txt=animal_desc, border=1)
        pdf.cell(50, 8, txt=f"{data['amount_paid']:,.2f}", border=1, align='R', ln=True)
        
        # Total
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(80, 10, txt=labels["total"], border=1, align='R')
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
        pdf.cell(0, 5, txt=labels["footer"], ln=True, align='C')

        pdf.output(output_path)

    def print_receipt(self, output_path):
        if os.name == 'nt':
            os.startfile(output_path, "print")
        else:
            # Linux/Mac placeholder
            pass