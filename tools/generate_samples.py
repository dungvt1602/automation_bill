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
    c.drawString(50, 800, "AGO FRUIT EXPORT - SAMPLE INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, "Invoice No: INV-TEST-001")
    c.drawString(50, 760, "Item: Fresh Dragon Fruit - 1000kg - 2.5 USD/kg")
    c.save()
    print(f"Generated: {path}")

if __name__ == "__main__":
    create_invoice("commercial_invoice_sample.pdf")
