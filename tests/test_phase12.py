import os
import tempfile
from pathlib import Path

import hermes.db as db
from hermes.pdf import generate_invoice_pdf

def test_phase12_e2e_invoice_flow():
    tmpdir = tempfile.mkdtemp()
    tmp = Path(tmpdir)
    db_path = str(tmp / "hermes.db")
    
    # Initialize DB structures
    db.init_db(db_path)
    
    # Task 12.1 & 12.4: Edge Cases (New client, multiple items, GST)
    
    # 1. Create a Client
    client_id = db.create_client(db_path, "Raj", phone="9876543210")
    assert client_id is not None
    
    # 2. Setup Business
    db.update_business(db_path, name="Test Agency", gstin="22AAAAA0000A1Z5")
    business = db.get_business(db_path)
    
    # 3. Create Invoice
    items = [
        {"description": "Design", "unit_price": 2000.0, "quantity": 1},
        {"description": "Dev", "unit_price": 5000.0, "quantity": 1},
        {"description": "Hosting", "unit_price": 500.0, "quantity": 1}
    ]
    
    inv_id = db.create_invoice(
        db_path=db_path,
        client_id=client_id,
        items=items,
        due_date="2024-01-15",
        tax_rate=18.0  # GST edge case
    )
    assert inv_id is not None
    
    # 4. Generate PDF
    inv_data = db.get_invoice(db_path, inv_id)
    assert inv_data is not None
    
    pdf_path = str(tmp / f"{inv_data['invoice_number']}.pdf")
    
    # Check that arithmetic is correct
    subtotal = 2000 + 5000 + 500
    tax = subtotal * 0.18
    expected_total = subtotal + tax
    
    assert inv_data["subtotal"] == float(subtotal)
    assert inv_data["tax_amount"] == float(tax)
    assert inv_data["total"] == float(expected_total)
    
    output = generate_invoice_pdf(inv_data, business, pdf_path)
    assert os.path.exists(pdf_path)
    
    # Task 12.2: Retrieve Invoice
    retrieved_status = db.get_invoice_by_number(db_path, inv_data["invoice_number"])
    assert retrieved_status["status"] == "draft"
    
    # Task 12.3: Send Invoice Reminder
    # Need to find unpaid invoices
    unpaid_invoices = db.list_invoices(db_path, status="draft", client_id=client_id)
    assert len(unpaid_invoices) == 1
    
    # Log reminder
    reminder_id = db.log_reminder(db_path, inv_id, client_id, "Sent reminder via Telegram")
    assert reminder_id is not None
    
    # Verify reminder history
    reminders = db.get_reminders_for_invoice(db_path, inv_id)
    assert len(reminders) == 1
    assert reminders[0]["message_text"] == "Sent reminder via Telegram"

    print("Phase 12 E2E Invoice Flow fully verified.")

if __name__ == "__main__":
    test_phase12_e2e_invoice_flow()
