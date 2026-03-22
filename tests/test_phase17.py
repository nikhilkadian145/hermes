"""
Phase 17 -- All Report Tools End-to-End Integration Test
Tests: P&L, Outstanding, Expense, GST reports + CA Export Bundle.
"""
import os
import zipfile
import tempfile
from datetime import date, timedelta
from pathlib import Path

import hermes.db as db
from hermes.pdf import (
    generate_pl_report_pdf,
    generate_outstanding_report_pdf,
    generate_expense_report_pdf,
    generate_gst_report_pdf,
)
from hermes.export import create_ca_bundle


def _seed_db(db_path: str):
    """Seed a database with realistic data for report testing."""
    db.init_db(db_path)
    db.update_business(db_path, name="Hermes Agency", gstin="22AAAAA0000A1Z5", owner_name="Nikhil")

    today = date.today()

    raj_id = db.create_client(db_path, "Raj Traders", phone="9876543210")
    meena_id = db.create_client(db_path, "Meena Stores", phone="9988776655")

    # Paid invoice (Raj) with GST
    inv1 = db.create_invoice(db_path, raj_id,
        items=[{"description": "Web Dev", "unit_price": 25000.0, "quantity": 1}],
        due_date=(today - timedelta(days=10)).isoformat(), tax_rate=18.0)
    db.update_invoice_status(db_path, inv1, "sent")
    db.record_payment(db_path, inv1, 29500.0, mode="upi",
        payment_date=(today - timedelta(days=5)).isoformat())

    # Unpaid overdue invoice (Meena) with GST
    inv2 = db.create_invoice(db_path, meena_id,
        items=[{"description": "Goods Supply", "unit_price": 8500.0, "quantity": 1}],
        due_date=(today - timedelta(days=3)).isoformat(), tax_rate=18.0)
    db.update_invoice_status(db_path, inv2, "sent")

    # Expenses
    db.log_expense(db_path, (today - timedelta(days=2)).isoformat(),
        "Office rent", "rent", 15000.0, vendor="Landlord")
    db.log_expense(db_path, (today - timedelta(days=1)).isoformat(),
        "Stationery", "supplies", 450.0, vendor="Sharma Stationery")

    return raj_id, meena_id, inv1, inv2


# ---------------------------------------------------------------------------
# Task 17.1 -- P&L Report
# ---------------------------------------------------------------------------

def test_phase17_pl_report():
    """Generate P&L report PDF from real DB data."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    _seed_db(db_path)

    today = date.today()
    from_date = today.replace(day=1).isoformat()
    to_date = today.isoformat()

    pl = db.get_pl_summary(db_path, from_date, to_date)
    assert "total_collected" in pl
    assert "total_expenses" in pl
    assert "net_profit" in pl
    assert pl["total_collected"] > 0
    assert pl["total_expenses"] > 0

    business = db.get_business(db_path)
    pdf_path = str(tmp / "pl_report.pdf")
    generate_pl_report_pdf(pl, business, from_date, to_date, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print("  [OK] Task 17.1 - P&L report PDF generated")


# ---------------------------------------------------------------------------
# Task 17.2 -- Outstanding Report
# ---------------------------------------------------------------------------

def test_phase17_outstanding_report():
    """Generate Outstanding dues PDF."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    _seed_db(db_path)

    report = db.get_outstanding_report(db_path)
    assert len(report) >= 1  # At least Meena's unpaid invoice
    # Each entry has client_name + invoices list
    assert "client_name" in report[0]
    assert "invoices" in report[0]
    assert "total_outstanding" in report[0]

    business = db.get_business(db_path)
    pdf_path = str(tmp / "outstanding_report.pdf")
    generate_outstanding_report_pdf(report, business, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print("  [OK] Task 17.2 - Outstanding report PDF generated")


# ---------------------------------------------------------------------------
# Task 17.3 -- Expense Report
# ---------------------------------------------------------------------------

def test_phase17_expense_report():
    """Generate Expense report PDF for date range."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    _seed_db(db_path)

    today = date.today()
    from_date = (today - timedelta(days=30)).isoformat()
    to_date = today.isoformat()

    expenses = db.list_expenses(db_path, from_date=from_date, to_date=to_date)
    assert len(expenses) >= 2

    categories = db.get_expense_total_by_category(db_path, from_date, to_date)
    assert "rent" in categories
    assert "supplies" in categories

    business = db.get_business(db_path)
    pdf_path = str(tmp / "expense_report.pdf")
    generate_expense_report_pdf(expenses, categories, business, from_date, to_date, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print("  [OK] Task 17.3 - Expense report PDF generated")


# ---------------------------------------------------------------------------
# Task 17.4 -- GST Report
# ---------------------------------------------------------------------------

def test_phase17_gst_report():
    """Generate GST report with CGST + SGST calculations."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    _seed_db(db_path)

    today = date.today()
    from_date = (today - timedelta(days=90)).isoformat()
    to_date = today.isoformat()

    gst = db.get_gst_report(db_path, from_date, to_date)
    assert "total_gst" in gst
    assert "cgst" in gst
    assert "sgst" in gst
    assert "invoice_details" in gst
    assert gst["total_gst"] > 0
    assert gst["cgst"] == gst["sgst"]  # CGST = SGST for intra-state

    business = db.get_business(db_path)
    pdf_path = str(tmp / "gst_report.pdf")
    generate_gst_report_pdf(gst, business, from_date, to_date, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print("  [OK] Task 17.4 - GST report PDF with CGST/SGST verified")


# ---------------------------------------------------------------------------
# Task 17.5 -- CA Export Bundle
# ---------------------------------------------------------------------------

def test_phase17_ca_export():
    """Generate ZIP with all PDFs + CSVs."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    _seed_db(db_path)

    data_dir = str(tmp / "customer_data")
    os.makedirs(data_dir, exist_ok=True)

    today = date.today()
    from_date = (today - timedelta(days=90)).isoformat()
    to_date = today.isoformat()

    zip_path = str(tmp / "ca_export.zip")
    result = create_ca_bundle(db_path, data_dir, from_date, to_date, zip_path)
    assert os.path.exists(zip_path)
    assert os.path.getsize(zip_path) > 0

    # Verify ZIP contents
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        csv_files = [n for n in names if n.endswith('.csv')]
        assert len(csv_files) >= 1, f"Expected CSV files in ZIP, got: {names}"

    print("  [OK] Task 17.5 - CA Export ZIP bundle generated and verified")


if __name__ == "__main__":
    test_phase17_pl_report()
    test_phase17_outstanding_report()
    test_phase17_expense_report()
    test_phase17_gst_report()
    test_phase17_ca_export()
    print("\n[PASS] Phase 17 - All 5 Report Tools E2E tests passed!")
