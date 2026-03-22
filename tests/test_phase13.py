"""
Phase 13 — Payment & Bookkeeping End-to-End Integration Test
Tests: full payment, partial payment, bookkeeping queries, receipt PDF generation.
"""
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path

import hermes.db as db
from hermes.pdf import generate_receipt_pdf


def test_phase13_full_payment():
    """Task 13.1: Record a full UPI payment and verify status auto-updates to 'paid'."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    # Setup business + client + invoice
    db.update_business(db_path, name="Raj Agency", gstin="22AAAAA0000A1Z5")
    client_id = db.create_client(db_path, "Raj", phone="9876543210")
    inv_id = db.create_invoice(
        db_path, client_id,
        items=[{"description": "Web Development", "unit_price": 5000.0, "quantity": 1}],
        due_date=(date.today() + timedelta(days=15)).isoformat(),
    )
    inv = db.get_invoice(db_path, inv_id)
    assert inv["status"] == "draft"
    assert inv["total"] == 5000.0

    # Record full payment via UPI
    payment_id = db.record_payment(db_path, inv_id, 5000.0, mode="upi", reference="UPI-REF-12345")
    assert payment_id is not None

    # Status should have auto-updated to "paid"
    inv_after = db.get_invoice(db_path, inv_id)
    assert inv_after["status"] == "paid", f"Expected 'paid', got '{inv_after['status']}'"

    # Verify payment record
    payments = db.get_payments_for_invoice(db_path, inv_id)
    assert len(payments) == 1
    assert payments[0]["amount"] == 5000.0
    assert payments[0]["mode"] == "upi"
    assert payments[0]["reference"] == "UPI-REF-12345"

    print("  [OK] Task 13.1 - Full payment recorded, invoice marked paid")


def test_phase13_partial_payment():
    """Task 13.2: Partial payment — invoice should stay 'sent', balance tracked."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="Test Agency")
    client_id = db.create_client(db_path, "Amit", phone="9988776655")
    inv_id = db.create_invoice(
        db_path, client_id,
        items=[{"description": "Consulting", "unit_price": 10000.0, "quantity": 1}],
        due_date=(date.today() + timedelta(days=30)).isoformat(),
    )

    # Record partial payment of ₹6000 out of ₹10000
    db.record_payment(db_path, inv_id, 6000.0, mode="bank", reference="NEFT-001")

    inv = db.get_invoice(db_path, inv_id)
    assert inv["status"] == "sent", f"Expected 'sent' for partial, got '{inv['status']}'"

    # Verify outstanding balance
    paid_total = db.get_invoice_paid_total(db_path, inv_id)
    remaining = inv["total"] - paid_total
    assert paid_total == 6000.0
    assert remaining == 4000.0

    # Record rest of the payment
    db.record_payment(db_path, inv_id, 4000.0, mode="upi")
    inv_final = db.get_invoice(db_path, inv_id)
    assert inv_final["status"] == "paid", f"After full payment, expected 'paid', got '{inv_final['status']}'"

    print("  [OK] Task 13.2 - Partial payment tracked, final payment completes invoice")


def test_phase13_bookkeeping_queries():
    """Task 13.3: Outstanding balance, MTD summary, overdue detection."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="Test Business")
    raj_id = db.create_client(db_path, "Raj")
    amit_id = db.create_client(db_path, "Amit")

    # Create invoices — one due yesterday (overdue), one due today, one future
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    future = (date.today() + timedelta(days=10)).isoformat()

    inv1 = db.create_invoice(db_path, raj_id,
        items=[{"description": "Design", "unit_price": 3000.0, "quantity": 1}],
        due_date=yesterday)
    # Mark as sent so it shows as overdue
    db.update_invoice_status(db_path, inv1, "sent")

    inv2 = db.create_invoice(db_path, raj_id,
        items=[{"description": "Dev", "unit_price": 7000.0, "quantity": 1}],
        due_date=future)

    inv3 = db.create_invoice(db_path, amit_id,
        items=[{"description": "Marketing", "unit_price": 5000.0, "quantity": 1}],
        due_date=future)

    # Test outstanding balance for Raj
    raj_balance = db.get_outstanding_balance(db_path, client_id=raj_id)
    assert raj_balance == 10000.0, f"Expected 10000, got {raj_balance}"

    # Test overdue invoices
    overdue = db.get_overdue_invoices(db_path)
    assert len(overdue) >= 1
    overdue_numbers = [o["invoice_number"] for o in overdue]
    inv1_data = db.get_invoice(db_path, inv1)
    assert inv1_data["invoice_number"] in overdue_numbers

    # Test MTD summary
    mtd = db.get_mtd_summary(db_path)
    assert "mtd_revenue" in mtd
    assert "overdue_count" in mtd
    assert mtd["overdue_count"] >= 1

    print("  [OK] Task 13.3 - Outstanding, overdue, and MTD bookkeeping queries verified")


def test_phase13_receipt_pdf():
    """Task 13.4: Generate a receipt PDF after recording payment."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="Receipt Test Agency", gstin="22BBBBB0000B1Z5")
    business = db.get_business(db_path)
    client_id = db.create_client(db_path, "Suresh", phone="9123456789")

    inv_id = db.create_invoice(
        db_path, client_id,
        items=[{"description": "Annual Maintenance", "unit_price": 12000.0, "quantity": 1}],
        due_date=(date.today() + timedelta(days=7)).isoformat(),
        tax_rate=18.0,
    )

    # Record payment
    payment_id = db.record_payment(db_path, inv_id, 14160.0, mode="upi", reference="UPI-9876")

    # Fetch objects for PDF generation
    inv_data = db.get_invoice(db_path, inv_id)
    payments = db.get_payments_for_invoice(db_path, inv_id)
    assert len(payments) == 1

    pdf_path = str(tmp / f"receipt_{payment_id}.pdf")
    output = generate_receipt_pdf(payments[0], inv_data, business, pdf_path)
    assert os.path.exists(pdf_path), f"Receipt PDF not found at {pdf_path}"
    assert os.path.getsize(pdf_path) > 0, "Receipt PDF is empty"

    print("  [OK] Task 13.4 - Receipt PDF generated and verified")


if __name__ == "__main__":
    test_phase13_full_payment()
    test_phase13_partial_payment()
    test_phase13_bookkeeping_queries()
    test_phase13_receipt_pdf()
    print("\n[PASS] Phase 13 - All Payment & Bookkeeping E2E tests passed!")
