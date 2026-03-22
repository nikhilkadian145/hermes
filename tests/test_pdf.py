import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from hermes import pdf

# Dummy Data
BUSINESS = {
    "name": "Acme Corp", "address": "123 Startup Lane", "city": "Bengaluru", 
    "pin": "560001", "phone": "+91 9876543210", "email": "hello@acme.in",
    "gstin": "29ABCDE1234F1Z5", "bank_name": "HDFC Bank", 
    "account_number": "1234567890", "ifsc": "HDFC0001234", "upi_id": "acme@hdfc"
}

CLIENT = {
    "name": "Global Tech", "address": "456 Corporate Road", 
    "phone": "+91 9998887770", "gstin": "27XYZZZ9876A1Z9"
}

INVOICE = {
    "invoice_number": "INV-0001", "issue_date": "2023-10-01", "due_date": "2023-10-15",
    "client": CLIENT,
    "items": [
        {"description": "Web Development", "quantity": 1, "unit_price": 50000.0, "amount": 50000.0},
        {"description": "Server Hosting", "quantity": 12, "unit_price": 1000.0, "amount": 12000.0}
    ],
    "subtotal": 62000.0, "tax_rate": 18.0, "tax_amount": 11160.0, "total": 73160.0,
    "notes": "100% advance payment required for hosting.", "status": "paid"
}

QUOTATION = dict(INVOICE, quotation_number="QT-0001", valid_until="2023-11-01", status="accepted")

PAYMENT = {
    "id": 10, "payment_date": "2023-10-05", "amount": 73160.0,
    "mode": "UPI", "reference": "UPI/327712345678", "notes": "Paid in full"
}

PL_DATA = {
    "total_invoiced": 150000.0, "total_collected": 120000.0, 
    "total_expenses": 30000.0, "net_profit": 90000.0
}

OUTSTANDING_DATA = [
    {
        "client_name": "Global Tech", "client_phone": "9998887770", 
        "total_outstanding": 45000.0,
        "invoices": [
            {"invoice_number": "INV-0002", "due_date": "2023-09-01", "days_overdue": 30, "total": 45000.0, "paid": 0.0, "outstanding": 45000.0}
        ]
    }
]

EXPENSES_DATA = [
    {"date": "2023-10-02", "description": "Office Rent", "category": "Rent", "vendor": "Landlord", "amount": 25000.0},
    {"date": "2023-10-05", "description": "Internet", "category": "Utilities", "vendor": "Airtel", "amount": 5000.0}
]
EXPENSES_TOTALS = {"Rent": 25000.0, "Utilities": 5000.0}

GST_DATA = {
    "taxable_turnover": 100000.0, "total_gst": 18000.0, "cgst": 9000.0, "sgst": 9000.0,
    "invoice_details": [
        {"invoice_number": "INV-0001", "issue_date": "2023-10-01", "subtotal": 100000.0, "tax_rate": 18.0, "tax_amount": 18000.0, "total": 118000.0}
    ]
}

def test_generate_invoice():
    with TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "inv.pdf"
        assert pdf.generate_invoice_pdf(INVOICE, BUSINESS, str(out)) == str(out)
        assert out.exists() and out.stat().st_size > 1000

def test_generate_receipt():
    with TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "rcpt.pdf"
        assert pdf.generate_receipt_pdf(PAYMENT, INVOICE, BUSINESS, str(out)) == str(out)
        assert out.exists()

def test_generate_quotation():
    with TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "qt.pdf"
        assert pdf.generate_quotation_pdf(QUOTATION, BUSINESS, str(out)) == str(out)
        assert out.exists()

def test_generate_reports():
    with TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        pdf.generate_pl_report_pdf(PL_DATA, BUSINESS, "2023-10-01", "2023-10-31", str(p / "pl.pdf"))
        pdf.generate_outstanding_report_pdf(OUTSTANDING_DATA, BUSINESS, str(p / "out.pdf"))
        pdf.generate_expense_report_pdf(EXPENSES_DATA, EXPENSES_TOTALS, BUSINESS, "2023-10-01", "2023-10-31", str(p / "exp.pdf"))
        pdf.generate_gst_report_pdf(GST_DATA, BUSINESS, "2023-10-01", "2023-10-31", str(p / "gst.pdf"))
        
        assert (p / "pl.pdf").exists()
        assert (p / "out.pdf").exists()
        assert (p / "exp.pdf").exists()
        assert (p / "gst.pdf").exists()
