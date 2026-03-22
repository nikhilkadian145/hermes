"""
Phase 15 -- Quotation, Receipt, Udhaar End-to-End Integration Test
Tests: quotation flow + convert-to-invoice, receipt PDF, udhaar tracking.
"""
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path

import hermes.db as db
from hermes.pdf import generate_quotation_pdf, generate_receipt_pdf


# ---------------------------------------------------------------------------
# Task 15.1 -- Quotation flow
# ---------------------------------------------------------------------------

def test_phase15_quotation_flow():
    """Create quotation, generate PDF, convert to invoice."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="Raj Agency", gstin="22AAAAA0000A1Z5")
    business = db.get_business(db_path)
    client_id = db.create_client(db_path, "Raj", phone="9876543210")

    valid_until = (date.today() + timedelta(days=7)).isoformat()

    # Create quotation with line items
    qt_id = db.create_quotation(
        db_path, client_id,
        items=[
            {"description": "Website Design", "unit_price": 10000.0, "quantity": 1},
            {"description": "Hosting Setup", "unit_price": 5000.0, "quantity": 1},
        ],
        valid_until=valid_until,
        tax_rate=18.0,
    )
    assert qt_id is not None

    qt = db.get_quotation(db_path, qt_id)
    assert qt is not None
    assert qt["subtotal"] == 15000.0
    assert qt["tax_amount"] == 2700.0
    assert qt["total"] == 17700.0
    assert qt["status"] == "draft"
    assert len(qt["items"]) == 2

    # Generate quotation PDF
    pdf_path = str(tmp / f"{qt['quotation_number']}.pdf")
    generate_quotation_pdf(qt, business, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    # Convert quotation to invoice (client accepted it)
    inv_id = db.convert_quotation_to_invoice(db_path, qt_id)
    assert inv_id is not None

    # Verify the new invoice has the same items and totals
    inv = db.get_invoice(db_path, inv_id)
    assert inv is not None
    assert inv["subtotal"] == 15000.0
    assert inv["total"] == 17700.0
    assert len(inv["items"]) == 2
    assert inv["items"][0]["description"] == "Website Design"

    # Verify quotation status updated to accepted
    qt_after = db.get_quotation(db_path, qt_id)
    assert qt_after["status"] == "accepted"

    print("  [OK] Task 15.1 - Quotation flow + convert-to-invoice verified")


# ---------------------------------------------------------------------------
# Task 15.2 -- Receipt generation
# ---------------------------------------------------------------------------

def test_phase15_receipt_generation():
    """After payment, generate a receipt with unique number."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="Receipt Agency", gstin="22CCCCC0000C1Z5")
    business = db.get_business(db_path)
    client_id = db.create_client(db_path, "Suresh", phone="9111222333")

    inv_id = db.create_invoice(
        db_path, client_id,
        items=[{"description": "Consulting", "unit_price": 8000.0, "quantity": 1}],
        due_date=(date.today() + timedelta(days=10)).isoformat(),
    )

    # Record payment
    payment_id = db.record_payment(db_path, inv_id, 8000.0, mode="upi", reference="UPI-ABCD")
    inv_data = db.get_invoice(db_path, inv_id)
    payments = db.get_payments_for_invoice(db_path, inv_id)
    assert len(payments) == 1

    payment = payments[0]
    assert payment["mode"] == "upi"
    assert payment["reference"] == "UPI-ABCD"

    # Generate receipt PDF
    pdf_path = str(tmp / f"receipt_{payment_id}.pdf")
    generate_receipt_pdf(payment, inv_data, business, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print("  [OK] Task 15.2 - Receipt PDF generated with payment details")


# ---------------------------------------------------------------------------
# Task 15.3 -- Udhaar tracking
# ---------------------------------------------------------------------------

def test_phase15_udhaar_tracking():
    """Add udhaar, list it, settle it."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    # "Ramesh ko 2000 udhaar diya hai"
    udhaar_id = db.add_udhaar(
        db_path,
        person_name="Ramesh",
        phone="9999888877",
        amount=2000.0,
        direction="given",
        notes="Personal loan",
    )
    assert udhaar_id is not None

    # Add another udhaar (received)
    udhaar_id2 = db.add_udhaar(
        db_path,
        person_name="Sunil",
        amount=3000.0,
        direction="received",
        notes="Borrowed for supplies",
    )

    # List all unsettled udhaar
    unsettled = db.list_udhaar(db_path, settled=False)
    assert len(unsettled) == 2

    # Check the amounts
    given = [u for u in unsettled if u["direction"] == "given"]
    received = [u for u in unsettled if u["direction"] == "received"]
    assert len(given) == 1
    assert given[0]["amount"] == 2000.0
    assert given[0]["person_name"] == "Ramesh"
    assert len(received) == 1
    assert received[0]["amount"] == 3000.0

    # "Ramesh ne 2000 wapas kar diya" -- settle it
    settled_record = db.settle_udhaar(db_path, udhaar_id)
    assert settled_record is not None
    assert settled_record["settled"] == 1

    # Now unsettled list should have only 1
    unsettled_after = db.list_udhaar(db_path, settled=False)
    assert len(unsettled_after) == 1
    assert unsettled_after[0]["person_name"] == "Sunil"

    # Settled list should have 1
    settled_list = db.list_udhaar(db_path, settled=True)
    assert len(settled_list) == 1
    assert settled_list[0]["person_name"] == "Ramesh"

    print("  [OK] Task 15.3 - Udhaar tracking (add, list, settle) verified")


if __name__ == "__main__":
    test_phase15_quotation_flow()
    test_phase15_receipt_generation()
    test_phase15_udhaar_tracking()
    print("\n[PASS] Phase 15 - All Quotation, Receipt, Udhaar E2E tests passed!")
