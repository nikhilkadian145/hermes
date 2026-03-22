"""
HERMES — tests/test_db.py
Comprehensive tests for hermes/db.py using temporary in-memory SQLite.
"""
import os
import tempfile

import pytest

from hermes import db


@pytest.fixture
def tmp_db():
    """Create a temporary DB file, initialize schema, yield path, cleanup."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        path = os.path.join(tmpdir, "test_hermes.db")
        db.init_db(path)
        yield path


# ---------------------------------------------------------------------------
# Setup & Business
# ---------------------------------------------------------------------------

class TestBusiness:
    def test_default_business_exists(self, tmp_db):
        biz = db.get_business(tmp_db)
        assert biz is not None
        assert biz["id"] == 1
        assert biz["currency"] == "INR"

    def test_update_business(self, tmp_db):
        updated = db.update_business(tmp_db, name="Raj Traders", gstin="29ABCDE1234F1Z5")
        assert updated["name"] == "Raj Traders"
        assert updated["gstin"] == "29ABCDE1234F1Z5"
        # Re-read
        biz = db.get_business(tmp_db)
        assert biz["name"] == "Raj Traders"

    def test_update_business_ignores_unknown_fields(self, tmp_db):
        updated = db.update_business(tmp_db, foo="bar")
        assert "foo" not in updated


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

class TestClients:
    def test_create_and_get(self, tmp_db):
        cid = db.create_client(tmp_db, "Raj Kumar", phone="9876543210")
        assert cid == 1
        client = db.get_client(tmp_db, cid)
        assert client["name"] == "Raj Kumar"
        assert client["phone"] == "9876543210"

    def test_find_client_by_name(self, tmp_db):
        db.create_client(tmp_db, "Amit Shah", phone="1111111111")
        db.create_client(tmp_db, "Raj Kumar", phone="2222222222")
        results = db.find_client(tmp_db, "Raj")
        assert len(results) == 1
        assert results[0]["name"] == "Raj Kumar"

    def test_find_client_by_phone(self, tmp_db):
        db.create_client(tmp_db, "Amit Shah", phone="9876543210")
        results = db.find_client(tmp_db, "9876")
        assert len(results) == 1

    def test_list_clients(self, tmp_db):
        db.create_client(tmp_db, "A Client")
        db.create_client(tmp_db, "B Client")
        clients = db.list_clients(tmp_db)
        assert len(clients) == 2

    def test_update_client(self, tmp_db):
        cid = db.create_client(tmp_db, "Old Name")
        updated = db.update_client(tmp_db, cid, name="New Name", phone="999")
        assert updated["name"] == "New Name"
        assert updated["phone"] == "999"


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

class TestInvoices:
    def _make_client(self, tmp_db):
        return db.create_client(tmp_db, "Test Client", phone="1234567890")

    def test_next_invoice_number(self, tmp_db):
        assert db.next_invoice_number(tmp_db) == "INV-0001"

    def test_create_and_get_invoice(self, tmp_db):
        cid = self._make_client(tmp_db)
        items = [
            {"description": "Web Dev", "quantity": 1, "unit_price": 5000},
            {"description": "Hosting", "quantity": 12, "unit_price": 500},
        ]
        inv_id = db.create_invoice(tmp_db, cid, items, "2026-04-15", tax_rate=18)
        assert inv_id == 1

        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["invoice_number"] == "INV-0001"
        assert inv["subtotal"] == 11000.0  # 5000 + 6000
        assert inv["tax_amount"] == 1980.0  # 18% of 11000
        assert inv["total"] == 12980.0
        assert inv["status"] == "draft"
        assert len(inv["items"]) == 2
        assert inv["client"]["name"] == "Test Client"

    def test_get_invoice_by_number(self, tmp_db):
        cid = self._make_client(tmp_db)
        db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 100}], "2026-05-01")
        inv = db.get_invoice_by_number(tmp_db, "INV-0001")
        assert inv is not None
        assert inv["total"] == 100.0

    def test_list_invoices_filter(self, tmp_db):
        cid = self._make_client(tmp_db)
        db.create_invoice(tmp_db, cid, [{"description": "A", "quantity": 1, "unit_price": 100}], "2026-05-01")
        inv_id2 = db.create_invoice(tmp_db, cid, [{"description": "B", "quantity": 1, "unit_price": 200}], "2026-05-01")
        db.update_invoice_status(tmp_db, inv_id2, "sent")

        all_inv = db.list_invoices(tmp_db)
        assert len(all_inv) == 2
        sent = db.list_invoices(tmp_db, status="sent")
        assert len(sent) == 1
        assert sent[0]["invoice_number"] == "INV-0002"

    def test_update_invoice_status(self, tmp_db):
        cid = self._make_client(tmp_db)
        inv_id = db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 100}], "2026-05-01")
        result = db.update_invoice_status(tmp_db, inv_id, "sent")
        assert result["status"] == "sent"

    def test_set_pdf_path(self, tmp_db):
        cid = self._make_client(tmp_db)
        inv_id = db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 100}], "2026-05-01")
        db.set_invoice_pdf_path(tmp_db, inv_id, "/path/to/inv.pdf")
        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["pdf_path"] == "/path/to/inv.pdf"

    def test_overdue_invoices(self, tmp_db):
        cid = self._make_client(tmp_db)
        # Past due date, status draft
        db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 100}], "2020-01-01")
        overdue = db.get_overdue_invoices(tmp_db)
        assert len(overdue) == 1
        assert overdue[0]["client_name"] == "Test Client"

    def test_due_soon_invoices(self, tmp_db):
        from datetime import date, timedelta
        cid = self._make_client(tmp_db)
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 100}], tomorrow)
        due_soon = db.get_due_soon_invoices(tmp_db, days=3)
        assert len(due_soon) == 1

    def test_outstanding_balance(self, tmp_db):
        cid = self._make_client(tmp_db)
        db.create_invoice(tmp_db, cid, [{"description": "X", "quantity": 1, "unit_price": 1000}], "2026-05-01")
        balance = db.get_outstanding_balance(tmp_db, client_id=cid)
        assert balance == 1000.0


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class TestPayments:
    def _setup_invoice(self, tmp_db):
        cid = db.create_client(tmp_db, "Pay Client")
        inv_id = db.create_invoice(
            tmp_db, cid,
            [{"description": "Service", "quantity": 1, "unit_price": 10000}],
            "2026-05-01",
        )
        return cid, inv_id

    def test_record_payment(self, tmp_db):
        cid, inv_id = self._setup_invoice(tmp_db)
        pid = db.record_payment(tmp_db, inv_id, 5000, mode="upi", reference="UTR123")
        assert pid == 1
        payments = db.get_payments_for_invoice(tmp_db, inv_id)
        assert len(payments) == 1
        assert payments[0]["amount"] == 5000.0
        assert payments[0]["mode"] == "upi"

    def test_partial_payment_status(self, tmp_db):
        _, inv_id = self._setup_invoice(tmp_db)
        db.record_payment(tmp_db, inv_id, 5000)
        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["status"] == "sent"  # Partial → sent

    def test_full_payment_marks_paid(self, tmp_db):
        _, inv_id = self._setup_invoice(tmp_db)
        db.record_payment(tmp_db, inv_id, 10000)
        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["status"] == "paid"

    def test_multiple_partial_payments(self, tmp_db):
        _, inv_id = self._setup_invoice(tmp_db)
        db.record_payment(tmp_db, inv_id, 3000)
        db.record_payment(tmp_db, inv_id, 3000)
        assert db.get_invoice_paid_total(tmp_db, inv_id) == 6000.0
        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["status"] == "sent"
        db.record_payment(tmp_db, inv_id, 4000)
        inv = db.get_invoice(tmp_db, inv_id)
        assert inv["status"] == "paid"

    def test_payment_updates_outstanding(self, tmp_db):
        cid, inv_id = self._setup_invoice(tmp_db)
        db.record_payment(tmp_db, inv_id, 7000)
        balance = db.get_outstanding_balance(tmp_db, client_id=cid)
        assert balance == 3000.0


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------

class TestExpenses:
    def test_log_and_get(self, tmp_db):
        eid = db.log_expense(tmp_db, "2026-03-01", "Office rent", "rent", 15000, vendor="Landlord")
        assert eid == 1
        exp = db.get_expense(tmp_db, eid)
        assert exp["amount"] == 15000.0
        assert exp["category"] == "rent"

    def test_list_expenses_filter(self, tmp_db):
        db.log_expense(tmp_db, "2026-03-01", "Rent", "rent", 15000)
        db.log_expense(tmp_db, "2026-03-05", "Lunch", "food", 500)
        db.log_expense(tmp_db, "2026-03-10", "Cab", "travel", 300)

        all_exp = db.list_expenses(tmp_db)
        assert len(all_exp) == 3
        food = db.list_expenses(tmp_db, category="food")
        assert len(food) == 1
        march = db.list_expenses(tmp_db, from_date="2026-03-01", to_date="2026-03-05")
        assert len(march) == 2

    def test_expense_by_category(self, tmp_db):
        db.log_expense(tmp_db, "2026-03-01", "Rent", "rent", 15000)
        db.log_expense(tmp_db, "2026-03-05", "Lunch", "food", 500)
        db.log_expense(tmp_db, "2026-03-06", "Dinner", "food", 700)
        totals = db.get_expense_total_by_category(tmp_db, "2026-03-01", "2026-03-31")
        assert totals["rent"] == 15000.0
        assert totals["food"] == 1200.0


# ---------------------------------------------------------------------------
# Quotations
# ---------------------------------------------------------------------------

class TestQuotations:
    def test_create_and_get(self, tmp_db):
        cid = db.create_client(tmp_db, "Quote Client")
        items = [{"description": "Design", "quantity": 1, "unit_price": 3000}]
        qt_id = db.create_quotation(tmp_db, cid, items, "2026-04-30", tax_rate=18)
        assert qt_id == 1
        qt = db.get_quotation(tmp_db, qt_id)
        assert qt["quotation_number"] == "QT-0001"
        assert qt["subtotal"] == 3000.0
        assert qt["tax_amount"] == 540.0
        assert qt["total"] == 3540.0
        assert len(qt["items"]) == 1

    def test_convert_to_invoice(self, tmp_db):
        cid = db.create_client(tmp_db, "Convert Client")
        items = [
            {"description": "Design", "quantity": 1, "unit_price": 3000},
            {"description": "Dev", "quantity": 2, "unit_price": 5000},
        ]
        qt_id = db.create_quotation(tmp_db, cid, items, "2026-04-30", tax_rate=18)
        inv_id = db.convert_quotation_to_invoice(tmp_db, qt_id)
        assert inv_id == 1

        inv = db.get_invoice(tmp_db, inv_id)
        assert len(inv["items"]) == 2
        assert inv["subtotal"] == 13000.0  # 3000 + 10000
        assert inv["tax_rate"] == 18.0

        qt = db.get_quotation(tmp_db, qt_id)
        assert qt["status"] == "accepted"


# ---------------------------------------------------------------------------
# Udhaar
# ---------------------------------------------------------------------------

class TestUdhaar:
    def test_add_and_list(self, tmp_db):
        uid = db.add_udhaar(tmp_db, "Ramesh", phone="9999", amount=5000, direction="given")
        assert uid == 1
        unsettled = db.list_udhaar(tmp_db, settled=False)
        assert len(unsettled) == 1
        assert unsettled[0]["person_name"] == "Ramesh"

    def test_settle(self, tmp_db):
        uid = db.add_udhaar(tmp_db, "Ramesh", amount=5000, direction="given")
        result = db.settle_udhaar(tmp_db, uid)
        assert result["settled"] == 1
        assert result["settled_at"] is not None
        unsettled = db.list_udhaar(tmp_db, settled=False)
        assert len(unsettled) == 0
        settled = db.list_udhaar(tmp_db, settled=True)
        assert len(settled) == 1

    def test_balance(self, tmp_db):
        db.add_udhaar(tmp_db, "Suresh", amount=5000, direction="given")
        db.add_udhaar(tmp_db, "Suresh", amount=2000, direction="received")
        balance = db.get_udhaar_balance(tmp_db, "Suresh")
        assert balance == 3000.0  # Net: they owe 3000

    def test_balance_after_settle(self, tmp_db):
        uid = db.add_udhaar(tmp_db, "Suresh", amount=5000, direction="given")
        db.settle_udhaar(tmp_db, uid)
        db.add_udhaar(tmp_db, "Suresh", amount=2000, direction="given")
        balance = db.get_udhaar_balance(tmp_db, "Suresh")
        assert balance == 2000.0  # Settled one doesn't count


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

class TestReports:
    def _seed_data(self, tmp_db):
        """Seed invoices, payments, expenses for report testing."""
        cid = db.create_client(tmp_db, "Report Client")
        # Invoice 1: paid
        inv1 = db.create_invoice(
            tmp_db, cid,
            [{"description": "Service A", "quantity": 1, "unit_price": 10000}],
            "2026-03-31", tax_rate=18,
        )
        db.record_payment(tmp_db, inv1, 11800, payment_date="2026-03-15", mode="bank")
        # Invoice 2: outstanding
        db.create_invoice(
            tmp_db, cid,
            [{"description": "Service B", "quantity": 1, "unit_price": 5000}],
            "2026-04-15", tax_rate=18,
        )
        # Expenses
        db.log_expense(tmp_db, "2026-03-10", "Rent", "rent", 15000)
        db.log_expense(tmp_db, "2026-03-12", "Lunch", "food", 500)
        return cid

    def test_pl_summary(self, tmp_db):
        self._seed_data(tmp_db)
        pl = db.get_pl_summary(tmp_db, "2026-03-01", "2026-03-31")
        assert pl["total_collected"] == 11800.0
        assert pl["total_expenses"] == 15500.0
        assert pl["net_profit"] == -3700.0

    def test_outstanding_report(self, tmp_db):
        self._seed_data(tmp_db)
        report = db.get_outstanding_report(tmp_db)
        assert len(report) == 1  # One client
        assert report[0]["client_name"] == "Report Client"
        # Only Invoice 2 should be outstanding (Invoice 1 is paid)
        assert len(report[0]["invoices"]) == 1
        assert report[0]["total_outstanding"] == 5900.0  # 5000 + 18% GST

    def test_gst_report(self, tmp_db):
        self._seed_data(tmp_db)
        gst = db.get_gst_report(tmp_db, "2026-03-01", "2026-03-31")
        # Both invoices have issue_date = today (March), so both are included
        assert gst["taxable_turnover"] == 15000.0  # 10000 + 5000
        assert gst["total_gst"] == 2700.0  # 18% of 15000
        assert gst["cgst"] == 1350.0
        assert gst["sgst"] == 1350.0

    def test_mtd_summary(self, tmp_db):
        self._seed_data(tmp_db)
        # MTD depends on current date, but we can check structure
        mtd = db.get_mtd_summary(tmp_db)
        assert "mtd_revenue" in mtd
        assert "mtd_expenses" in mtd
        assert "overdue_count" in mtd
        assert "due_today_count" in mtd
        assert "due_soon_3d_count" in mtd

    def test_revenue_by_month(self, tmp_db):
        self._seed_data(tmp_db)
        months = db.get_revenue_by_month(tmp_db, 2026)
        assert len(months) >= 1
        march = [m for m in months if m["month"] == "03"]
        assert len(march) == 1
        assert march[0]["revenue"] == 11800.0


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

class TestReminders:
    def test_log_and_get(self, tmp_db):
        cid = db.create_client(tmp_db, "Reminder Client")
        inv_id = db.create_invoice(
            tmp_db, cid,
            [{"description": "X", "quantity": 1, "unit_price": 100}],
            "2026-05-01",
        )
        rid = db.log_reminder(tmp_db, inv_id, cid, "Bhai payment kar do!")
        assert rid == 1
        reminders = db.get_reminders_for_invoice(tmp_db, inv_id)
        assert len(reminders) == 1
        assert "payment" in reminders[0]["message_text"]
