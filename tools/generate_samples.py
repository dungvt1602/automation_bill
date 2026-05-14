"""
Generate sample PDF (Moved to tools/)
"""
import sys
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import SAMPLE_INPUT_DIR

def create_invoice(filename):
    SAMPLE_INPUT_DIR.mkdir(exist_ok=True)
    path = SAMPLE_INPUT_DIR / filename
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "AGO FRUIT EXPORT - COMMERCIAL INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, "Invoice No: INV-2026-001")
    c.drawString(50, 760, "Date: 14-May-2026")
    c.drawString(50, 740, "Seller: AGO FRUIT EXPORT CO., LTD")
    c.drawString(50, 720, "Buyer: GLOBAL FRESH MART")
    c.drawString(50, 680, "Item 1: Fresh Dragon Fruit - 2000 kg - 2.5 USD/kg - Amount: 5000 USD")
    c.drawString(50, 660, "Item 2: Premium Mango (Cat Chu) - 1000 kg - 3.0 USD/kg - Amount: 3000 USD")
    c.drawString(50, 640, "Item 3: Seedless Lime - 500 kg - 1.8 USD/kg - Amount: 900 USD")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, "TOTAL AMOUNT: 8900 USD")
    c.save()
    print(f"Generated: {path}")

def create_packing_list(filename):
    SAMPLE_INPUT_DIR.mkdir(exist_ok=True)
    path = SAMPLE_INPUT_DIR / filename
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "AGO FRUIT EXPORT - PACKING LIST")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, "Packing List No: PL-2026-001")
    c.drawString(50, 760, "Reference Invoice: INV-2026-001")
    c.drawString(50, 720, "Item 1: Fresh Dragon Fruit - Qty: 100 boxes - Net: 2000kg - Gross: 2100kg")
    c.drawString(50, 700, "Item 2: Premium Mango - Qty: 50 boxes - Net: 1000kg - Gross: 1050kg")
    c.drawString(50, 680, "Item 3: Seedless Lime - Qty: 25 boxes - Net: 500kg - Gross: 525kg")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 640, "TOTAL NET WEIGHT: 3500 kg")
    c.drawString(50, 620, "TOTAL GROSS WEIGHT: 3675 kg")
    c.save()
    print(f"Generated: {path}")

if __name__ == "__main__":
    create_invoice("commercial_invoice_sample.pdf")
    create_packing_list("packing_list_sample.pdf")
