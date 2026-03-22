"""
HERMES — Database Operations
All SQLite operations for invoices, payments, expenses, clients, etc.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Convert a sqlite3.Row to a plain dict, or None if row is None."""
    if row is None:
        return None
    return dict(row)


def _rows_to_list(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Setup & Init
# ---------------------------------------------------------------------------

def get_conn(db_path: str) -> sqlite3.Connection:
    """Return a connection with row_factory = sqlite3.Row and WAL mode."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> sqlite3.Connection:
    """Create DB file, run schema.sql, return connection."""
    conn = get_conn(db_path)
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()
    return conn


def get_business(db_path: str) -> dict[str, Any]:
    """Return the single business settings row."""
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM business WHERE id = 1").fetchone()
    conn.close()
    return _row_to_dict(row) or {}


def update_business(db_path: str, **kwargs: Any) -> dict[str, Any]:
    """Update business settings. Only updates fields that are passed."""
    if not kwargs:
        return get_business(db_path)
    allowed = {
        "name", "owner_name", "address", "city", "state", "pin", "gstin",
        "phone", "email", "bank_name", "account_number", "ifsc", "upi_id",
        "web_password_hash", "currency",
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_business(db_path)
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn = get_conn(db_path)
    conn.execute(f"UPDATE business SET {set_clause} WHERE id = 1", list(fields.values()))
    conn.commit()
    row = conn.execute("SELECT * FROM business WHERE id = 1").fetchone()
    conn.close()
    return _row_to_dict(row) or {}


# ---------------------------------------------------------------------------
# Client Operations
# ---------------------------------------------------------------------------

def create_client(
    db_path: str, name: str,
    phone: str = "", email: str = "", address: str = "",
    gstin: str = "", notes: str = "",
) -> int:
    """Create a new client. Returns client_id."""
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO clients (name, phone, email, address, gstin, notes) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, phone, email, address, gstin, notes),
    )
    conn.commit()
    client_id = cur.lastrowid
    conn.close()
    return client_id


def get_client(db_path: str, client_id: int) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def find_client(db_path: str, query: str) -> list[dict[str, Any]]:
    """Fuzzy search clients by name or phone."""
    conn = get_conn(db_path)
    pattern = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM clients WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
        (pattern, pattern),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def list_clients(db_path: str) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return _rows_to_list(rows)


def update_client(db_path: str, client_id: int, **kwargs: Any) -> dict[str, Any] | None:
    allowed = {"name", "phone", "email", "address", "gstin", "notes"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_client(db_path, client_id)
    fields["updated_at"] = datetime.now().isoformat(timespec="seconds")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn = get_conn(db_path)
    conn.execute(
        f"UPDATE clients SET {set_clause} WHERE id = ?",
        [*fields.values(), client_id],
    )
    conn.commit()
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


# ---------------------------------------------------------------------------
# Invoice Operations
# ---------------------------------------------------------------------------

def next_invoice_number(db_path: str) -> str:
    """Return next invoice number like INV-0042."""
    conn = get_conn(db_path)
    row = conn.execute("SELECT MAX(id) AS max_id FROM invoices").fetchone()
    conn.close()
    next_id = (row["max_id"] or 0) + 1
    return f"INV-{next_id:04d}"


def create_invoice(
    db_path: str, client_id: int, items: list[dict[str, Any]],
    due_date: str, tax_rate: float = 0.0, notes: str = "",
) -> int:
    """
    Create an invoice with line items.
    items: list of {"description": str, "quantity": float, "unit_price": float}
    Returns invoice_id.
    """
    inv_number = next_invoice_number(db_path)
    subtotal = sum(it.get("quantity", 1) * it.get("unit_price", 0) for it in items)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    total = round(subtotal + tax_amount, 2)

    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO invoices "
        "(invoice_number, client_id, due_date, subtotal, tax_rate, tax_amount, total, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (inv_number, client_id, due_date, subtotal, tax_rate, tax_amount, total, notes),
    )
    invoice_id = cur.lastrowid
    for it in items:
        qty = it.get("quantity", 1)
        price = it.get("unit_price", 0)
        amount = round(qty * price, 2)
        conn.execute(
            "INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount) "
            "VALUES (?, ?, ?, ?, ?)",
            (invoice_id, it["description"], qty, price, amount),
        )
    conn.commit()
    conn.close()
    return invoice_id


def get_invoice(db_path: str, invoice_id: int) -> dict[str, Any] | None:
    """Get invoice with items and client info."""
    conn = get_conn(db_path)
    inv = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv is None:
        conn.close()
        return None
    result = dict(inv)
    result["items"] = _rows_to_list(
        conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    )
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (result["client_id"],)).fetchone()
    result["client"] = _row_to_dict(client)
    conn.close()
    return result


def get_invoice_by_number(db_path: str, invoice_number: str) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    inv = conn.execute(
        "SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,)
    ).fetchone()
    conn.close()
    if inv is None:
        return None
    return get_invoice(db_path, inv["id"])


def list_invoices(
    db_path: str, status: str | None = None,
    client_id: int | None = None, limit: int = 20,
) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    sql = "SELECT * FROM invoices WHERE 1=1"
    params: list[Any] = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if client_id:
        sql += " AND client_id = ?"
        params.append(client_id)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _rows_to_list(rows)


def update_invoice_status(db_path: str, invoice_id: int, status: str) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE invoices SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, invoice_id),
    )
    conn.commit()
    conn.close()
    return get_invoice(db_path, invoice_id)


def set_invoice_pdf_path(db_path: str, invoice_id: int, pdf_path: str) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE invoices SET pdf_path = ?, updated_at = datetime('now') WHERE id = ?",
        (pdf_path, invoice_id),
    )
    conn.commit()
    conn.close()


def get_overdue_invoices(db_path: str) -> list[dict[str, Any]]:
    """Invoices past due_date that are not paid/cancelled."""
    today = date.today().isoformat()
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT i.*, c.name AS client_name, c.phone AS client_phone "
        "FROM invoices i JOIN clients c ON i.client_id = c.id "
        "WHERE i.due_date < ? AND i.status NOT IN ('paid','cancelled') "
        "ORDER BY i.due_date",
        (today,),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_due_soon_invoices(db_path: str, days: int = 3) -> list[dict[str, Any]]:
    """Invoices due within the next N days that are not paid/cancelled."""
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT i.*, c.name AS client_name, c.phone AS client_phone "
        "FROM invoices i JOIN clients c ON i.client_id = c.id "
        "WHERE i.due_date >= ? AND i.due_date <= ? "
        "AND i.status NOT IN ('paid','cancelled') ORDER BY i.due_date",
        (today.isoformat(), cutoff),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_outstanding_balance(db_path: str, client_id: int | None = None) -> float:
    """Total outstanding (invoiced - paid) for a client or all clients."""
    conn = get_conn(db_path)
    if client_id:
        row = conn.execute(
            "SELECT COALESCE(SUM(i.total), 0) - COALESCE("
            "  (SELECT SUM(p.amount) FROM payments p "
            "   JOIN invoices i2 ON p.invoice_id = i2.id "
            "   WHERE i2.client_id = ?), 0"
            ") AS balance "
            "FROM invoices i WHERE i.client_id = ? AND i.status != 'cancelled'",
            (client_id, client_id),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT COALESCE(SUM(total), 0) - "
            "  COALESCE((SELECT SUM(amount) FROM payments), 0) "
            "AS balance FROM invoices WHERE status != 'cancelled'"
        ).fetchone()
    conn.close()
    return round(row["balance"], 2) if row else 0.0


# ---------------------------------------------------------------------------
# Payment Operations
# ---------------------------------------------------------------------------

def record_payment(
    db_path: str, invoice_id: int, amount: float,
    payment_date: str | None = None, mode: str = "other",
    reference: str = "", notes: str = "",
) -> int:
    """Record a payment against an invoice. Returns payment_id."""
    if payment_date is None:
        payment_date = date.today().isoformat()
    conn = get_conn(db_path)
    # Get client_id from invoice
    inv = conn.execute("SELECT client_id FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv is None:
        conn.close()
        raise ValueError(f"Invoice {invoice_id} not found")
    client_id = inv["client_id"]
    cur = conn.execute(
        "INSERT INTO payments (invoice_id, client_id, amount, payment_date, mode, reference, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (invoice_id, client_id, amount, payment_date, mode, reference, notes),
    )
    payment_id = cur.lastrowid
    conn.commit()
    conn.close()
    # Auto-update invoice status
    auto_update_invoice_status_after_payment(db_path, invoice_id)
    return payment_id


def get_payments_for_invoice(db_path: str, invoice_id: int) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date", (invoice_id,)
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_invoice_paid_total(db_path: str, invoice_id: int) -> float:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS paid FROM payments WHERE invoice_id = ?",
        (invoice_id,),
    ).fetchone()
    conn.close()
    return round(row["paid"], 2)


def auto_update_invoice_status_after_payment(db_path: str, invoice_id: int) -> None:
    """Mark invoice 'paid' if fully paid, otherwise set to 'sent' (partial)."""
    conn = get_conn(db_path)
    inv = conn.execute("SELECT total, status FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv is None or inv["status"] == "cancelled":
        conn.close()
        return
    paid = get_invoice_paid_total(db_path, invoice_id)
    new_status = "paid" if paid >= inv["total"] else "sent"
    if inv["status"] != new_status:
        conn.execute(
            "UPDATE invoices SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (new_status, invoice_id),
        )
        conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Expense Operations
# ---------------------------------------------------------------------------

def log_expense(
    db_path: str, date_str: str, description: str, category: str, amount: float,
    vendor: str = "", receipt_path: str = "", ocr_raw: str = "", notes: str = "",
) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO expenses (date, description, category, amount, vendor, "
        "receipt_path, ocr_raw, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (date_str, description, category, amount, vendor, receipt_path, ocr_raw, notes),
    )
    conn.commit()
    expense_id = cur.lastrowid
    conn.close()
    return expense_id


def get_expense(db_path: str, expense_id: int) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_expenses(
    db_path: str, category: str | None = None,
    from_date: str | None = None, to_date: str | None = None,
) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    sql = "SELECT * FROM expenses WHERE 1=1"
    params: list[Any] = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if from_date:
        sql += " AND date >= ?"
        params.append(from_date)
    if to_date:
        sql += " AND date <= ?"
        params.append(to_date)
    sql += " ORDER BY date DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_expense_total_by_category(
    db_path: str, from_date: str, to_date: str,
) -> dict[str, float]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE date >= ? AND date <= ? GROUP BY category ORDER BY total DESC",
        (from_date, to_date),
    ).fetchall()
    conn.close()
    return {r["category"]: round(r["total"], 2) for r in rows}


# ---------------------------------------------------------------------------
# Quotation Operations
# ---------------------------------------------------------------------------

def next_quotation_number(db_path: str) -> str:
    conn = get_conn(db_path)
    row = conn.execute("SELECT MAX(id) AS max_id FROM quotations").fetchone()
    conn.close()
    next_id = (row["max_id"] or 0) + 1
    return f"QT-{next_id:04d}"


def create_quotation(
    db_path: str, client_id: int, items: list[dict[str, Any]],
    valid_until: str, tax_rate: float = 0.0, notes: str = "",
) -> int:
    qt_number = next_quotation_number(db_path)
    subtotal = sum(it.get("quantity", 1) * it.get("unit_price", 0) for it in items)
    tax_amount = round(subtotal * tax_rate / 100, 2)
    total = round(subtotal + tax_amount, 2)

    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO quotations "
        "(quotation_number, client_id, valid_until, subtotal, tax_rate, tax_amount, total, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (qt_number, client_id, valid_until, subtotal, tax_rate, tax_amount, total, notes),
    )
    qt_id = cur.lastrowid
    for it in items:
        qty = it.get("quantity", 1)
        price = it.get("unit_price", 0)
        amount = round(qty * price, 2)
        conn.execute(
            "INSERT INTO quotation_items (quotation_id, description, quantity, unit_price, amount) "
            "VALUES (?, ?, ?, ?, ?)",
            (qt_id, it["description"], qty, price, amount),
        )
    conn.commit()
    conn.close()
    return qt_id


def get_quotation(db_path: str, quotation_id: int) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    qt = conn.execute("SELECT * FROM quotations WHERE id = ?", (quotation_id,)).fetchone()
    if qt is None:
        conn.close()
        return None
    result = dict(qt)
    result["items"] = _rows_to_list(
        conn.execute(
            "SELECT * FROM quotation_items WHERE quotation_id = ?", (quotation_id,)
        ).fetchall()
    )
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (result["client_id"],)).fetchone()
    result["client"] = _row_to_dict(client)
    conn.close()
    return result


def convert_quotation_to_invoice(db_path: str, quotation_id: int) -> int:
    """Copy a quotation's items into a new invoice. Returns invoice_id."""
    qt = get_quotation(db_path, quotation_id)
    if qt is None:
        raise ValueError(f"Quotation {quotation_id} not found")
    items = [
        {"description": it["description"], "quantity": it["quantity"], "unit_price": it["unit_price"]}
        for it in qt["items"]
    ]
    due_date = (date.today() + timedelta(days=30)).isoformat()
    invoice_id = create_invoice(
        db_path, qt["client_id"], items, due_date, qt["tax_rate"], qt.get("notes", ""),
    )
    update_quotation_status(db_path, quotation_id, "accepted")
    return invoice_id


def update_quotation_status(db_path: str, quotation_id: int, status: str) -> None:
    conn = get_conn(db_path)
    conn.execute("UPDATE quotations SET status = ? WHERE id = ?", (status, quotation_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Udhaar Operations
# ---------------------------------------------------------------------------

def add_udhaar(
    db_path: str, person_name: str, phone: str = "",
    amount: float = 0.0, direction: str = "given", notes: str = "",
) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO udhaar (person_name, phone, amount, direction, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (person_name, phone, amount, direction, notes),
    )
    conn.commit()
    udhaar_id = cur.lastrowid
    conn.close()
    return udhaar_id


def settle_udhaar(db_path: str, udhaar_id: int) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE udhaar SET settled = 1, settled_at = datetime('now') WHERE id = ?",
        (udhaar_id,),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM udhaar WHERE id = ?", (udhaar_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def list_udhaar(db_path: str, settled: bool = False) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM udhaar WHERE settled = ? ORDER BY created_at DESC",
        (1 if settled else 0,),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_udhaar_balance(db_path: str, person_name: str) -> float:
    """Net balance: positive = they owe you, negative = you owe them."""
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT "
        "  COALESCE(SUM(CASE WHEN direction='given' THEN amount ELSE 0 END), 0) - "
        "  COALESCE(SUM(CASE WHEN direction='received' THEN amount ELSE 0 END), 0) "
        "AS balance FROM udhaar WHERE person_name = ? AND settled = 0",
        (person_name,),
    ).fetchone()
    conn.close()
    return round(row["balance"], 2) if row else 0.0


# ---------------------------------------------------------------------------
# Report Queries
# ---------------------------------------------------------------------------

def get_pl_summary(db_path: str, from_date: str, to_date: str) -> dict[str, Any]:
    """Profit & Loss summary for a date range."""
    conn = get_conn(db_path)
    rev = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM payments "
        "WHERE payment_date >= ? AND payment_date <= ?",
        (from_date, to_date),
    ).fetchone()
    exp = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
        "WHERE date >= ? AND date <= ?",
        (from_date, to_date),
    ).fetchone()
    invoiced = conn.execute(
        "SELECT COALESCE(SUM(total), 0) AS total FROM invoices "
        "WHERE issue_date >= ? AND issue_date <= ? AND status != 'cancelled'",
        (from_date, to_date),
    ).fetchone()
    conn.close()
    revenue = round(rev["total"], 2)
    expenses = round(exp["total"], 2)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_invoiced": round(invoiced["total"], 2),
        "total_collected": revenue,
        "total_expenses": expenses,
        "net_profit": round(revenue - expenses, 2),
    }


def get_revenue_by_month(db_path: str, year: int) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT strftime('%m', payment_date) AS month, "
        "SUM(amount) AS revenue FROM payments "
        "WHERE strftime('%Y', payment_date) = ? "
        "GROUP BY month ORDER BY month",
        (str(year),),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def get_outstanding_report(db_path: str) -> list[dict[str, Any]]:
    """Per-client outstanding invoices."""
    conn = get_conn(db_path)
    clients_rows = conn.execute(
        "SELECT DISTINCT c.id, c.name, c.phone FROM clients c "
        "JOIN invoices i ON c.id = i.client_id "
        "WHERE i.status NOT IN ('paid','cancelled') ORDER BY c.name"
    ).fetchall()
    result = []
    for c in clients_rows:
        invoices = conn.execute(
            "SELECT i.*, "
            "  COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) "
            "  AS paid_amount "
            "FROM invoices i WHERE i.client_id = ? AND i.status NOT IN ('paid','cancelled') "
            "ORDER BY i.due_date",
            (c["id"],),
        ).fetchall()
        inv_list = []
        total_outstanding = 0.0
        today = date.today()
        for inv in invoices:
            outstanding = round(inv["total"] - inv["paid_amount"], 2)
            due = date.fromisoformat(inv["due_date"])
            days_overdue = (today - due).days if today > due else 0
            inv_list.append({
                "invoice_number": inv["invoice_number"],
                "total": inv["total"],
                "paid": inv["paid_amount"],
                "outstanding": outstanding,
                "due_date": inv["due_date"],
                "days_overdue": days_overdue,
            })
            total_outstanding += outstanding
        result.append({
            "client_id": c["id"],
            "client_name": c["name"],
            "client_phone": c["phone"],
            "invoices": inv_list,
            "total_outstanding": round(total_outstanding, 2),
        })
    conn.close()
    return result


def get_gst_report(db_path: str, from_date: str, to_date: str) -> dict[str, Any]:
    """GST report for a period."""
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT invoice_number, issue_date, subtotal, tax_rate, tax_amount, total "
        "FROM invoices WHERE issue_date >= ? AND issue_date <= ? "
        "AND status != 'cancelled' ORDER BY issue_date",
        (from_date, to_date),
    ).fetchall()
    totals = conn.execute(
        "SELECT COALESCE(SUM(subtotal), 0) AS taxable, "
        "COALESCE(SUM(tax_amount), 0) AS gst_collected "
        "FROM invoices WHERE issue_date >= ? AND issue_date <= ? "
        "AND status != 'cancelled'",
        (from_date, to_date),
    ).fetchone()
    conn.close()
    gst_total = round(totals["gst_collected"], 2)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "taxable_turnover": round(totals["taxable"], 2),
        "total_gst": gst_total,
        "cgst": round(gst_total / 2, 2),
        "sgst": round(gst_total / 2, 2),
        "invoice_details": _rows_to_list(rows),
    }


def get_mtd_summary(db_path: str) -> dict[str, Any]:
    """Month-to-date summary for morning briefing."""
    today = date.today()
    mtd_start = today.replace(day=1).isoformat()
    today_str = today.isoformat()
    yesterday = (today - timedelta(days=1)).isoformat()

    conn = get_conn(db_path)

    # MTD revenue (payments collected)
    rev = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM payments "
        "WHERE payment_date >= ? AND payment_date <= ?",
        (mtd_start, today_str),
    ).fetchone()

    # MTD expenses
    exp = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
        "WHERE date >= ? AND date <= ?",
        (mtd_start, today_str),
    ).fetchone()

    # Yesterday's payments
    yest_pay = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE payment_date = ?",
        (yesterday,),
    ).fetchone()

    # Overdue count
    overdue = conn.execute(
        "SELECT COUNT(*) AS cnt FROM invoices "
        "WHERE due_date < ? AND status NOT IN ('paid','cancelled')",
        (today_str,),
    ).fetchone()

    # Due today
    due_today = conn.execute(
        "SELECT COUNT(*) AS cnt FROM invoices "
        "WHERE due_date = ? AND status NOT IN ('paid','cancelled')",
        (today_str,),
    ).fetchone()

    # Due in 3 days
    cutoff_3d = (today + timedelta(days=3)).isoformat()
    due_soon = conn.execute(
        "SELECT COUNT(*) AS cnt FROM invoices "
        "WHERE due_date > ? AND due_date <= ? AND status NOT IN ('paid','cancelled')",
        (today_str, cutoff_3d),
    ).fetchone()

    conn.close()

    return {
        "date": today_str,
        "mtd_revenue": round(rev["total"], 2),
        "mtd_expenses": round(exp["total"], 2),
        "mtd_net": round(rev["total"] - exp["total"], 2),
        "yesterday_payments": round(yest_pay["total"], 2),
        "overdue_count": overdue["cnt"],
        "due_today_count": due_today["cnt"],
        "due_soon_3d_count": due_soon["cnt"],
    }


# ---------------------------------------------------------------------------
# Reminder Operations
# ---------------------------------------------------------------------------

def log_reminder(
    db_path: str, invoice_id: int, client_id: int, message_text: str,
) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO reminders (invoice_id, client_id, message_text) VALUES (?, ?, ?)",
        (invoice_id, client_id, message_text),
    )
    conn.commit()
    reminder_id = cur.lastrowid
    conn.close()
    return reminder_id


def get_reminders_for_invoice(db_path: str, invoice_id: int) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM reminders WHERE invoice_id = ? ORDER BY sent_at DESC",
        (invoice_id,),
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)
