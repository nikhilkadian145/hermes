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

def _notify(db_path: str, type: str, title: str, message: str,
             link_type: str = None, link_id: int = None) -> None:
    """Safe notification writer. Logs errors but never raises."""
    try:
        create_notification(db_path, type, title, message, link_type, link_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Notification write failed: {e}")

def get_conn(db_path: str) -> sqlite3.Connection:
    """Return a connection with row_factory = sqlite3.Row and WAL mode."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> sqlite3.Connection:
    """Create DB file, run schema.sql idempotently, load HSN data, return connection."""
    conn = get_conn(db_path)
    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    
    try:
        conn.executescript(schema_sql)
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            pass
        else:
            raise
    conn.commit()

    # Automatically load HSN master data
    try:
        import sys
        scripts_dir = str(Path(__file__).parent.parent / "scripts")
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        import load_hsn_data
        load_hsn_data.load(db_path)
    except Exception as e:
        print(f"Warning: Failed to auto-load HSN data: {e}")

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
    
    conn = get_conn(db_path)
    client_name = conn.execute("SELECT name FROM clients WHERE id = ?", (client_id,)).fetchone()["name"]
    conn.close()

    _notify(
        db_path,
        type="invoice_created",
        title=f"Invoice {inv_number} Created",
        message=f"{inv_number} for {client_name} — ₹{total:,.0f}",
        link_type="invoice",
        link_id=invoice_id
    )

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


def get_sales_invoices_paginated(
    db_path: str,
    status: str | None = None,
    client_id: int | None = None,
    search: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    """Returns paginated invoice list plus summary stats for the Sales Invoices page."""
    conn = get_conn(db_path)
    
    # Base query for filtering
    base_sql = "FROM invoices i JOIN clients c ON i.client_id = c.id WHERE 1=1"
    params: list[Any] = []
    
    if status and status.lower() != "all":
        base_sql += " AND i.status = ?"
        params.append(status.lower())
    if client_id:
        base_sql += " AND i.client_id = ?"
        params.append(client_id)
    if search:
        search_term = f"%{search}%"
        base_sql += " AND (i.invoice_number LIKE ? OR c.name LIKE ?)"
        params.extend([search_term, search_term])
    if from_date:
        base_sql += " AND i.issue_date >= ?"
        params.append(from_date)
    if to_date:
        base_sql += " AND i.issue_date <= ?"
        params.append(to_date)
        
    # Get total count
    count_sql = f"SELECT count(*) as total {base_sql}"
    total = conn.execute(count_sql, params).fetchone()["total"]
    
    # Get items for current page
    offset = (page - 1) * per_page
    items_sql = f"""
        SELECT i.*, c.name as client_name 
        {base_sql} 
        ORDER BY i.created_at DESC 
        LIMIT ? OFFSET ?
    """
    items_params = params + [per_page, offset]
    items = _rows_to_list(conn.execute(items_sql, items_params).fetchall())
    
    # Create a nice sub-summary of this exact filtered dataset
    summary_sql = f"""
        SELECT 
            COALESCE(SUM(i.total), 0) as total_amount,
            SUM(CASE WHEN i.status = 'paid' THEN i.total ELSE 0 END) as paid_amount,
            SUM(CASE WHEN i.status NOT IN ('paid', 'cancelled') THEN i.total ELSE 0 END) as outstanding_amount
        {base_sql}
    """
    summary_row = conn.execute(summary_sql, params).fetchone()
    
    # Get status counts
    status_counts_sql = f"""
        SELECT i.status, COUNT(*) as count 
        {base_sql} 
        GROUP BY i.status
    """
    status_counts = {r['status']: r['count'] for r in conn.execute(status_counts_sql, params)}
    
    conn.close()
    
    return {
        "items": items,
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "summary": {
            "total_amount": round(summary_row["total_amount"], 2),
            "paid_amount": round(summary_row["paid_amount"], 2),
            "outstanding_amount": round(summary_row["outstanding_amount"], 2),
            "count_by_status": status_counts
        }
    }


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

    conn = get_conn(db_path)
    client_name_row = conn.execute("SELECT name FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    client_name = client_name_row["name"] if client_name_row else "Unknown"

    _notify(
        db_path,
        type="payment_received",
        title="Payment Received",
        message=f"₹{amount:,.0f} received from {client_name} — {mode}",
        link_type="invoice",
        link_id=invoice_id
    )

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

    if new_status == "paid" and inv["status"] != "paid":
        conn = get_conn(db_path)
        inv_data = conn.execute("SELECT i.invoice_number, c.name FROM invoices i JOIN clients c ON i.client_id = c.id WHERE i.id = ?", (invoice_id,)).fetchone()
        conn.close()
        if inv_data:
            _notify(
                db_path,
                type="invoice_paid",
                title=f"Invoice {inv_data['invoice_number']} Fully Paid",
                message=f"{inv_data['invoice_number']} for {inv_data['name']} is now fully settled.",
                link_type="invoice",
                link_id=invoice_id
            )


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

    _notify(
        db_path,
        type="expense_logged",
        title="Expense Recorded",
        message=f"₹{amount:,.0f} — {description[:60]} ({category})",
        link_type="expense",
        link_id=expense_id
    )

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
        (invoice_id,)
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)

# ---------------------------------------------------------------------------
# Web Chat Operations
# ---------------------------------------------------------------------------

def get_pending_web_chat_message(db_path: str) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM chat_messages WHERE role = 'user' AND status = 'pending' ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    conn.close()
    return _row_to_dict(row)

def mark_web_chat_message_processing(db_path: str, message_id: int) -> None:
    conn = get_conn(db_path)
    conn.execute("UPDATE chat_messages SET status = 'processing' WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def mark_web_chat_message_done(db_path: str, message_id: int) -> None:
    conn = get_conn(db_path)
    conn.execute("UPDATE chat_messages SET status = 'done' WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def write_web_chat_response(db_path: str, conversation_id: str, content: str, metadata: str = None) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "INSERT INTO chat_messages (conversation_id, role, content, status, metadata) VALUES (?, 'assistant', ?, 'done', ?)",
        (conversation_id, content, metadata)
    )
    conn.commit()
    conn.close()

def get_web_chat_history(db_path: str, conversation_id: str, limit: int = 50) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ?",
        (conversation_id, limit)
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)

# ===========================================================================
# HSN / GST Lookup Operations
# ===========================================================================

def search_hsn(db_path: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
    """FTS5 search on HSN/SAC descriptions. Falls back to LIKE."""
    conn = get_conn(db_path)
    try:
        rows = conn.execute("""
            SELECT m.code, m.type, m.description,
                   m.gst_rate, m.chapter, m.cess_rate, rank
            FROM hsn_fts
            JOIN hsn_master m ON hsn_fts.rowid = m.id
            WHERE hsn_fts MATCH ? AND m.is_active = 1
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        rows = conn.execute("""
            SELECT code, type, description, gst_rate, chapter, cess_rate
            FROM hsn_master
            WHERE description LIKE ? AND is_active = 1
            LIMIT ?
        """, (f'%{query}%', limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_hsn_by_code(db_path: str, code: str) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM hsn_master WHERE code = ?", (code,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_cached_item_gst(db_path: str, description: str) -> dict[str, Any] | None:
    normalized = description.lower().strip()
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM item_gst_cache WHERE item_normalized = ?",
        (normalized,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE item_gst_cache SET use_count = use_count + 1, "
            "updated_at = CURRENT_TIMESTAMP WHERE item_normalized = ?",
            (normalized,)
        )
        conn.commit()
    conn.close()
    return dict(row) if row else None


def save_item_gst_cache(db_path: str, description: str, hsn_code: str,
                         gst_rate: float, confirmed_by: str = 'agent') -> None:
    normalized = description.lower().strip()
    conn = get_conn(db_path)
    conn.execute("""
        INSERT INTO item_gst_cache
          (item_description, item_normalized, hsn_code, gst_rate, confirmed_by)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_normalized) DO UPDATE SET
          hsn_code     = excluded.hsn_code,
          gst_rate     = excluded.gst_rate,
          confirmed_by = excluded.confirmed_by,
          use_count    = item_gst_cache.use_count + 1,
          updated_at   = CURRENT_TIMESTAMP
    """, (description, normalized, hsn_code, gst_rate, confirmed_by))
    conn.commit()
    conn.close()


def get_hsn_summary(db_path: str, from_date: str, to_date: str) -> list[dict[str, Any]]:
    """HSN/SAC-wise summary of all supplies for a period."""
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT ii.hsn_code, ii.gst_rate,
               COUNT(*) as num_items,
               SUM(ii.quantity) as total_qty,
               ROUND(SUM(ii.taxable_amount), 2) as taxable_value,
               ROUND(SUM(ii.cgst_amount), 2) as cgst,
               ROUND(SUM(ii.sgst_amount), 2) as sgst,
               ROUND(SUM(ii.igst_amount), 2) as igst,
               ROUND(SUM(ii.cess_amount), 2) as cess
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        WHERE i.issue_date BETWEEN ? AND ?
          AND ii.hsn_code IS NOT NULL
        GROUP BY ii.hsn_code, ii.gst_rate
        ORDER BY taxable_value DESC
    """, (from_date, to_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ===========================================================================
# GST-Aware Invoice Creation
# ===========================================================================

def create_invoice(
    db_path: str,
    client_id: int,
    items: list[dict[str, Any]],
    due_date: str,
    supply_type: str,
    place_of_supply: str,
    notes: str | None = None,
    reverse_charge: bool = False,
    is_export: bool = False,
    lut_number: str | None = None,
) -> int:
    """Create invoice with full per-item GST breakdown."""
    from hermes.gst import calculate_invoice_totals
    conn = get_conn(db_path)

    # Generate invoice number
    row = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()
    count = (row[0] if row else 0) + 1
    invoice_number = f"INV-{count:04d}"

    totals = calculate_invoice_totals(items)

    cur = conn.execute("""
        INSERT INTO invoices (
            invoice_number, client_id, due_date, subtotal,
            tax_rate, tax_amount, total, notes,
            supply_type, place_of_supply, reverse_charge,
            total_taxable_amount, total_cgst, total_sgst, total_igst, total_cess,
            is_export, lut_number, total_in_words
        ) VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number, client_id, due_date, totals['subtotal'],
        totals['total_tax'], totals['grand_total'],
        notes or '',
        supply_type, place_of_supply, 1 if reverse_charge else 0,
        totals['subtotal'], totals['total_cgst'], totals['total_sgst'],
        totals['total_igst'], totals['total_cess'],
        1 if is_export else 0, lut_number,
        totals['total_in_words'],
    ))
    invoice_id = cur.lastrowid

    for item in items:
        conn.execute("""
            INSERT INTO invoice_items (
                invoice_id, description, quantity, unit_price, amount,
                hsn_code, gst_rate, cgst_amount, sgst_amount, igst_amount,
                cess_amount, taxable_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id, item['description'], item['quantity'],
            item['unit_price'], item.get('line_total', item.get('amount', 0)),
            item.get('hsn_code'), item.get('gst_rate'),
            item.get('cgst_amount', 0), item.get('sgst_amount', 0),
            item.get('igst_amount', 0), item.get('cess_amount', 0),
            item.get('taxable_amount', 0),
        ))

    conn.commit()
    conn.close()

    # Create notification
    try:
        client = get_client(db_path, client_id)
        client_name = client.get('name', 'Unknown') if client else 'Unknown'
        create_notification(
            db_path, 'invoice', f'Invoice {invoice_number} created',
            f'Invoice {invoice_number} created for {client_name} — ₹{totals["grand_total"]:,.0f}',
            'invoice', invoice_id
        )
    except Exception:
        pass

    return invoice_id


# ===========================================================================
# GSTR-1 Compliant GST Reporting
# ===========================================================================

def get_gst_report(db_path: str, from_date: str, to_date: str) -> dict[str, Any]:
    """
    Returns structured GSTR-1 data:
    b2b, b2c_large, b2c_small, hsn_summary, summary.
    Handles both old-style (tax_rate/tax_amount) and new-style invoices.
    """
    conn = get_conn(db_path)

    # All invoices in period
    invoices = conn.execute("""
        SELECT i.*, c.name as client_name, c.gstin as client_gstin,
               c.state_code as client_state_code
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.issue_date BETWEEN ? AND ?
          AND i.status != 'cancelled'
        ORDER BY i.issue_date
    """, (from_date, to_date)).fetchall()

    b2b = []
    b2c_large = []
    b2c_small_by_rate: dict[float, dict[str, float]] = {}
    rate_summary: dict[float, dict[str, float]] = {}

    for inv in invoices:
        inv = dict(inv)

        # Normalize: use new columns if available, else derive from old
        taxable = inv.get('total_taxable_amount') or inv.get('subtotal', 0)
        cgst = inv.get('total_cgst') or 0
        sgst = inv.get('total_sgst') or 0
        igst = inv.get('total_igst') or 0

        if not cgst and not igst and inv.get('tax_amount'):
            # Old invoice — approximate split
            cgst = round(float(inv['tax_amount']) / 2, 2)
            sgst = round(float(inv['tax_amount']) - cgst, 2)

        total_tax = round(cgst + sgst + igst, 2)
        rate = inv.get('tax_rate', 0) or 0

        record = {
            'invoice_number': inv['invoice_number'],
            'date': inv['issue_date'],
            'client_name': inv.get('client_name', ''),
            'client_gstin': inv.get('client_gstin', ''),
            'taxable_value': float(taxable),
            'cgst': float(cgst),
            'sgst': float(sgst),
            'igst': float(igst),
            'cess': float(inv.get('total_cess', 0) or 0),
            'total': float(inv.get('total', 0)),
            'supply_type': inv.get('supply_type', 'intrastate'),
        }

        # Classify
        has_gstin = bool(inv.get('client_gstin'))
        if has_gstin:
            b2b.append(record)
        elif float(inv.get('total', 0)) > 250000:
            b2c_large.append(record)
        else:
            # B2C small — aggregate by rate
            r = float(rate)
            if r not in b2c_small_by_rate:
                b2c_small_by_rate[r] = {'taxable': 0, 'cgst': 0, 'sgst': 0, 'igst': 0, 'cess': 0}
            b2c_small_by_rate[r]['taxable'] += float(taxable)
            b2c_small_by_rate[r]['cgst'] += float(cgst)
            b2c_small_by_rate[r]['sgst'] += float(sgst)
            b2c_small_by_rate[r]['igst'] += float(igst)

        # Rate summary
        r = float(rate)
        if r not in rate_summary:
            rate_summary[r] = {'taxable': 0, 'cgst': 0, 'sgst': 0, 'igst': 0, 'cess': 0, 'total': 0}
        rate_summary[r]['taxable'] += float(taxable)
        rate_summary[r]['cgst'] += float(cgst)
        rate_summary[r]['sgst'] += float(sgst)
        rate_summary[r]['igst'] += float(igst)
        rate_summary[r]['total'] += float(inv.get('total', 0))

    conn.close()

    # Build b2c_small list
    b2c_small = [
        {'rate': k, **{kk: round(vv, 2) for kk, vv in v.items()}}
        for k, v in sorted(b2c_small_by_rate.items())
    ]

    summary = [
        {'rate': k, **{kk: round(vv, 2) for kk, vv in v.items()}}
        for k, v in sorted(rate_summary.items())
    ]

    return {
        'period': {'from': from_date, 'to': to_date},
        'b2b': b2b,
        'b2c_large': b2c_large,
        'b2c_small': b2c_small,
        'hsn_summary': get_hsn_summary(db_path, from_date, to_date),
        'summary': summary,
        'totals': {
            'total_invoices': len(invoices),
            'total_taxable': round(sum(r['taxable'] for r in rate_summary.values()), 2),
            'total_cgst': round(sum(r['cgst'] for r in rate_summary.values()), 2),
            'total_sgst': round(sum(r['sgst'] for r in rate_summary.values()), 2),
            'total_igst': round(sum(r['igst'] for r in rate_summary.values()), 2),
            'total_tax': round(sum(r['cgst'] + r['sgst'] + r['igst'] for r in rate_summary.values()), 2),
        },
    }


def get_itc_summary(db_path: str, from_date: str, to_date: str) -> dict[str, Any]:
    """Input Tax Credit from eligible vendor bills (expenses)."""
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT gst_rate,
               ROUND(SUM(cgst_amount), 2) as cgst,
               ROUND(SUM(sgst_amount), 2) as sgst,
               ROUND(SUM(igst_amount), 2) as igst,
               ROUND(SUM(cgst_amount + sgst_amount + igst_amount), 2) as total,
               COUNT(*) as bill_count
        FROM expenses
        WHERE date BETWEEN ? AND ?
          AND itc_eligible = 1
          AND vendor_gstin IS NOT NULL
          AND vendor_gstin != ''
        GROUP BY gst_rate
        ORDER BY gst_rate
    """, (from_date, to_date)).fetchall()
    conn.close()

    by_rate = [dict(r) for r in rows]
    total_itc = round(sum(r.get('total', 0) for r in by_rate), 2)
    return {
        'total_itc': total_itc,
        'by_rate': by_rate,
        'period': {'from': from_date, 'to': to_date},
    }


def get_gst_liability(db_path: str, from_date: str, to_date: str) -> dict[str, Any]:
    """Net GST payable = output tax - ITC."""
    gst_report = get_gst_report(db_path, from_date, to_date)
    itc = get_itc_summary(db_path, from_date, to_date)

    output_cgst = gst_report['totals']['total_cgst']
    output_sgst = gst_report['totals']['total_sgst']
    output_igst = gst_report['totals']['total_igst']
    output_total = gst_report['totals']['total_tax']

    itc_total = itc['total_itc']
    itc_cgst = round(sum(r.get('cgst', 0) for r in itc['by_rate']), 2)
    itc_sgst = round(sum(r.get('sgst', 0) for r in itc['by_rate']), 2)
    itc_igst = round(sum(r.get('igst', 0) for r in itc['by_rate']), 2)

    return {
        'period': {'from': from_date, 'to': to_date},
        'output_tax': {
            'cgst': output_cgst, 'sgst': output_sgst,
            'igst': output_igst, 'total': output_total,
        },
        'input_tax_credit': {
            'cgst': itc_cgst, 'sgst': itc_sgst,
            'igst': itc_igst, 'total': itc_total,
        },
        'net_payable': {
            'cgst': round(output_cgst - itc_cgst, 2),
            'sgst': round(output_sgst - itc_sgst, 2),
            'igst': round(output_igst - itc_igst, 2),
            'total': round(output_total - itc_total, 2),
        },
    }


# ===========================================================================
# Notifications
# ===========================================================================

def create_notification(db_path: str, type: str, title: str,
                         message: str, link_type: str | None = None,
                         link_id: int | None = None) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO notifications (type, title, message, link_type, link_id) "
        "VALUES (?, ?, ?, ?, ?)",
        (type, title, message, link_type, link_id)
    )
    conn.commit()
    nid = cur.lastrowid or 0
    conn.close()
    return nid


def get_unread_notification_count(db_path: str) -> int:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE is_read = 0"
    ).fetchone()
    conn.close()
    return row[0] if row else 0


def get_notifications(db_path: str, limit: int = 50,
                       unread_only: bool = False) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    sql = "SELECT * FROM notifications"
    if unread_only:
        sql += " WHERE is_read = 0"
    sql += " ORDER BY created_at DESC LIMIT ?"
    rows = conn.execute(sql, (limit,)).fetchall()
    conn.close()
    return _rows_to_list(rows)


def mark_notifications_read(db_path: str, ids: list[int]) -> None:
    conn = get_conn(db_path)
    placeholders = ','.join('?' * len(ids))
    conn.execute(
        f"UPDATE notifications SET is_read = 1 WHERE id IN ({placeholders})", ids
    )
    conn.commit()
    conn.close()


# ===========================================================================
# Anomaly Detection
# ===========================================================================

def detect_duplicate_bills(db_path: str) -> list[dict[str, Any]]:
    """Find likely duplicate expenses (same vendor + amount, within 30 days)."""
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT e1.id as id1, e2.id as id2,
               e1.vendor, e1.amount, e1.date as date1, e2.date as date2
        FROM expenses e1
        JOIN expenses e2 ON e1.id < e2.id
          AND e1.vendor = e2.vendor AND e1.vendor != ''
          AND e1.amount = e2.amount AND e1.amount > 0
          AND ABS(julianday(e1.date) - julianday(e2.date)) <= 30
    """).fetchall()
    conn.close()
    return [
        {
            'type': 'duplicate_bill',
            'id1': r['id1'], 'id2': r['id2'],
            'vendor': r['vendor'], 'amount': r['amount'],
            'date1': r['date1'], 'date2': r['date2'],
            'confidence': 0.85,
        }
        for r in [dict(row) for row in rows]
    ]


def detect_price_drift(db_path: str, threshold_pct: float = 20.0) -> list[dict[str, Any]]:
    """Find items where unit price drifted > threshold from recent average."""
    conn = get_conn(db_path)
    # Compare latest invoice_items to their own average
    rows = conn.execute("""
        WITH item_stats AS (
            SELECT ii.description, ii.unit_price,
                   AVG(ii.unit_price) OVER (
                       PARTITION BY LOWER(ii.description)
                       ORDER BY i.issue_date
                       ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
                   ) as avg_price,
                   ROW_NUMBER() OVER (
                       PARTITION BY LOWER(ii.description)
                       ORDER BY i.issue_date DESC
                   ) as rn
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
        )
        SELECT description, unit_price as current_price, avg_price,
               ROUND(ABS(unit_price - avg_price) * 100.0 / avg_price, 1) as drift_pct
        FROM item_stats
        WHERE rn = 1 AND avg_price IS NOT NULL AND avg_price > 0
          AND ABS(unit_price - avg_price) * 100.0 / avg_price > ?
    """, (threshold_pct,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def detect_round_number_billing(db_path: str) -> list[dict[str, Any]]:
    """Flag invoices/expenses with suspiciously round totals (>₹10k, divisible by 1000)."""
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT 'invoice' as source, id, total as amount, invoice_number as ref
        FROM invoices
        WHERE total > 10000 AND CAST(total AS INTEGER) % 1000 = 0
        UNION ALL
        SELECT 'expense' as source, id, amount, description as ref
        FROM expenses
        WHERE amount > 10000 AND CAST(amount AS INTEGER) % 1000 = 0
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def run_anomaly_detection(db_path: str) -> int:
    """Run all detection functions and write new anomalies to DB."""
    conn = get_conn(db_path)
    new_count = 0

    # Duplicate bills
    for d in detect_duplicate_bills(db_path):
        existing = conn.execute(
            "SELECT id FROM anomalies WHERE type = 'duplicate_bill' "
            "AND affected_id_1 = ? AND affected_id_2 = ?",
            (d['id1'], d['id2'])
        ).fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO anomalies (type, confidence, title, description,
                    affected_id_1, affected_type_1, affected_id_2, affected_type_2)
                VALUES (?, ?, ?, ?, ?, 'expense', ?, 'expense')
            """, (
                'duplicate_bill', d['confidence'],
                f"Possible duplicate: {d['vendor']} ₹{d['amount']:,.0f}",
                f"Bills #{d['id1']} and #{d['id2']} from {d['vendor']} — "
                f"same amount ₹{d['amount']:,.0f}, dates {d['date1']} and {d['date2']}",
                d['id1'], d['id2'],
            ))
            new_count += 1

    # Price drift
    for d in detect_price_drift(db_path):
        existing = conn.execute(
            "SELECT id FROM anomalies WHERE type = 'price_drift' "
            "AND title LIKE ?",
            (f"%{d['description']}%",)
        ).fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO anomalies (type, confidence, title, description)
                VALUES (?, 0.75, ?, ?)
            """, (
                'price_drift',
                f"Price change: {d['description']}",
                f"Current ₹{d['current_price']:,.0f} vs avg ₹{d['avg_price']:,.0f} "
                f"({d['drift_pct']}% drift)",
            ))
            new_count += 1

    # Round numbers
    for d in detect_round_number_billing(db_path):
        existing = conn.execute(
            "SELECT id FROM anomalies WHERE type = 'round_number' "
            "AND affected_id_1 = ? AND affected_type_1 = ?",
            (d['id'], d['source'])
        ).fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO anomalies (type, confidence, title, description,
                    affected_id_1, affected_type_1)
                VALUES (?, 0.6, ?, ?, ?, ?)
            """, (
                'round_number',
                f"Round amount: {d['ref']} ₹{d['amount']:,.0f}",
                f"Suspiciously round total ₹{d['amount']:,.0f} on {d['source']} #{d['id']}",
                d['id'], d['source'],
            ))
            new_count += 1

    conn.commit()
    conn.close()

    # Notify if new anomalies
    if new_count > 0:
        try:
            create_notification(
                db_path, 'anomaly', f'{new_count} new anomalies detected',
                f'Anomaly scan found {new_count} potential issues. Review them in the Anomalies page.',
            )
        except Exception:
            pass

    return new_count


# ===========================================================================
# GST Filing Periods
# ===========================================================================

def get_filing_periods(db_path: str) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM gst_filing_periods ORDER BY from_date DESC"
    ).fetchall()
    conn.close()
    return _rows_to_list(rows)


def update_filing_period_status(db_path: str, period_id: int, status: str) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE gst_filing_periods SET status = ?, filed_at = CURRENT_TIMESTAMP "
        "WHERE id = ?", (status, period_id)
    )
    conn.commit()
    conn.close()


# ===========================================================================
# Anomaly CRUD for webapp
# ===========================================================================

def get_anomalies(db_path: str, status: str | None = None,
                   limit: int = 50) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    sql = "SELECT * FROM anomalies"
    params: list[Any] = []
    if status:
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _rows_to_list(rows)


def update_anomaly_status(db_path: str, anomaly_id: int, status: str,
                           reason: str | None = None) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE anomalies SET status = ?, dismiss_reason = ?, "
        "resolved_at = CASE WHEN ? IN ('dismissed','acknowledged') THEN CURRENT_TIMESTAMP ELSE resolved_at END "
        "WHERE id = ?",
        (status, reason, status, anomaly_id)
    )
    conn.commit()
    conn.close()


# ===========================================================================
# Phase 25: Upload Queue & Purchase Bills
# ===========================================================================

def queue_upload(db_path: str, filename: str, file_size: int) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO upload_queue (filename, file_size, status) VALUES (?, ?, 'queued')",
        (filename, file_size)
    )
    upload_id = cur.lastrowid
    conn.commit()
    conn.close()
    if upload_id is None:
        raise ValueError("Failed to queue upload")
    return upload_id


def get_upload_queue(db_path: str) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute("""
        SELECT * FROM upload_queue 
        WHERE status != 'finalized' 
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return _rows_to_list(rows)


def reprocess_upload(db_path: str, upload_id: int) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE upload_queue SET status = 'queued', error_message = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (upload_id,)
    )
    conn.commit()
    conn.close()


def get_purchase_bills_paginated(
    db_path: str,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    conn = get_conn(db_path)
    
    # Unified view of bills + uploads
    base_sql = """
        SELECT 
            e.id as expense_id, u.id as upload_id,
            COALESCE(e.vendor, 'Unknown Vendor') as vendor,
            COALESCE(e.bill_number, 'N/A') as bill_number,
            COALESCE(e.date, DATE(u.created_at)) as date,
            COALESCE(e.amount, 0) as total,
            COALESCE(u.status, 'finalized') as status,
            u.filename, u.error_message,
            COALESCE(e.created_at, u.created_at) as created_at
        FROM upload_queue u
        LEFT JOIN expenses e ON u.expense_id = e.id
        UNION
        SELECT 
            e.id as expense_id, NULL as upload_id,
            e.vendor, e.bill_number, e.date, e.amount,
            'finalized' as status,
            NULL as filename, NULL as error_message,
            e.created_at
        FROM expenses e
        WHERE e.id NOT IN (SELECT expense_id FROM upload_queue WHERE expense_id IS NOT NULL)
    """
    
    # Wrap in a CTE to filter
    filter_sql = f"WITH bills AS ({base_sql}) SELECT * FROM bills WHERE 1=1"
    params: list[Any] = []
    
    if status and status.lower() != "all":
        if status.lower() == "needs review":
            filter_sql += " AND status = 'review_needed'"
        else:
            filter_sql += " AND status = ?"
            params.append(status.lower())
    if search:
        search_term = f"%{search}%"
        filter_sql += " AND (vendor LIKE ? OR bill_number LIKE ?)"
        params.extend([search_term, search_term])
        
    count_sql = f"SELECT count(*) as total FROM ({filter_sql})"
    total = conn.execute(count_sql, params).fetchone()["total"]
    
    offset = (page - 1) * per_page
    items_sql = f"{filter_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    items_params = params + [per_page, offset]
    items = _rows_to_list(conn.execute(items_sql, items_params).fetchall())
    
    summary_sql = f"""
        SELECT 
            SUM(total) as total_amount,
            SUM(CASE WHEN status = 'finalized' THEN total ELSE 0 END) as finalized_amount,
            SUM(CASE WHEN status != 'finalized' THEN total ELSE 0 END) as pending_amount
        FROM ({filter_sql})
    """
    summary_row = conn.execute(summary_sql, params).fetchone()
    
    status_counts_sql = f"SELECT status, COUNT(*) as count FROM ({filter_sql}) GROUP BY status"
    status_counts = {r['status']: r['count'] for r in conn.execute(status_counts_sql, params)}
    
    conn.close()
    
    return {
        "items": items,
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "summary": {
            "total_amount": round(summary_row["total_amount"] or 0, 2),
            "finalized_amount": round(summary_row["finalized_amount"] or 0, 2),
            "pending_amount": round(summary_row["pending_amount"] or 0, 2),
            "count_by_status": status_counts
        }
    }


def get_purchase_bill_detail(db_path: str, expense_id: int) -> dict[str, Any] | None:
    conn = get_conn(db_path)
    
    # Get the header
    expense_row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not expense_row:
        conn.close()
        return None
        
    expense = dict(expense_row)
    
    # Get upload queue info
    upload_row = conn.execute("SELECT * FROM upload_queue WHERE expense_id = ?", (expense_id,)).fetchone()
    expense["upload"] = dict(upload_row) if upload_row else None
    
    # Get items
    items_rows = conn.execute("SELECT * FROM expense_items WHERE expense_id = ?", (expense_id,)).fetchall()
    expense["items"] = _rows_to_list(items_rows)
    
    conn.close()
    return expense


def finalize_purchase_bill(db_path: str, expense_id: int, expense_data: dict[str, Any], items: list[dict[str, Any]]) -> None:
    conn = get_conn(db_path)
    
    # Update expense header
    conn.execute("""
        UPDATE expenses SET
            vendor = ?, bill_number = ?, date = ?, category = ?, amount = ?,
            cgst_amount = ?, sgst_amount = ?, igst_amount = ?, vendor_gstin = ?
        WHERE id = ?
    """, (
        expense_data.get('vendor', ''),
        expense_data.get('bill_number', ''),
        expense_data.get('date', ''),
        expense_data.get('category', 'other'),
        expense_data.get('amount', 0),
        expense_data.get('cgst_amount', 0),
        expense_data.get('sgst_amount', 0),
        expense_data.get('igst_amount', 0),
        expense_data.get('vendor_gstin', ''),
        expense_id
    ))
    
    # Delete old items
    conn.execute("DELETE FROM expense_items WHERE expense_id = ?", (expense_id,))
    
    # Insert new items
    for item in items:
        conn.execute("""
            INSERT INTO expense_items (
                expense_id, description, quantity, unit_price, amount,
                hsn_code, gst_rate, cgst_amount, sgst_amount, igst_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            expense_id,
            item.get('description', ''),
            item.get('quantity', 1),
            item.get('unit_price', 0),
            item.get('amount', 0),
            item.get('hsn_code', ''),
            item.get('gst_rate', 0),
            item.get('cgst_amount', 0),
            item.get('sgst_amount', 0),
            item.get('igst_amount', 0)
        ))
        
    # Mark upload as finalized if applicable
    conn.execute("UPDATE upload_queue SET status = 'finalized', updated_at = CURRENT_TIMESTAMP WHERE expense_id = ?", (expense_id,))
    
    conn.commit()
    conn.close()




# ---------------------------------------------------------------------------
# Web Chat Operations
# ---------------------------------------------------------------------------

def write_web_chat_user_message(db_path: str, conversation_id: str,
                                 content: str, metadata: str = None) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO chat_messages (conversation_id, role, content, status, metadata) "
        "VALUES (?, 'user', ?, 'pending', ?)",
        (conversation_id, content, metadata)
    )
    conn.commit()
    return cur.lastrowid


def get_pending_web_chat_message(db_path: str) -> dict | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM chat_messages "
        "WHERE role = 'user' AND status = 'pending' "
        "ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def mark_web_chat_message_processing(db_path: str, message_id: int) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE chat_messages SET status = 'processing' WHERE id = ?",
        (message_id,)
    )
    conn.commit()


def mark_web_chat_message_done(db_path: str, message_id: int) -> None:
    conn = get_conn(db_path)
    conn.execute(
        "UPDATE chat_messages SET status = 'done' WHERE id = ?",
        (message_id,)
    )
    conn.commit()


def write_web_chat_assistant_message(db_path: str, conversation_id: str,
                                      content: str, metadata: str = None) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO chat_messages (conversation_id, role, content, status, metadata) "
        "VALUES (?, 'assistant', ?, 'done', ?)",
        (conversation_id, content, metadata)
    )
    conn.commit()
    return cur.lastrowid


def get_web_chat_history(db_path: str, conversation_id: str,
                          limit: int = 50, after_id: int = 0) -> list[dict]:
    conn = get_conn(db_path)
    if after_id > 0:
        rows = conn.execute(
            "SELECT * FROM chat_messages "
            "WHERE conversation_id = ? AND id > ? "
            "ORDER BY created_at ASC",
            (conversation_id, after_id)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM chat_messages "
            "WHERE conversation_id = ? "
            "ORDER BY created_at ASC LIMIT ?",
            (conversation_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def get_web_chat_conversations(db_path: str, limit: int = 20) -> list[dict]:
    conn = get_conn(db_path)
    rows = conn.execute('''
        SELECT
            conversation_id,
            MIN(CASE WHEN role = 'user' THEN content END) AS first_message,
            MAX(created_at) AS last_activity,
            COUNT(*) AS message_count
        FROM chat_messages
        GROUP BY conversation_id
        ORDER BY last_activity DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    return [dict(r) for r in rows]




def enqueue_upload(db_path: str, original_path: str, filename: str,
                   file_type: str, source: str = 'webapp') -> int:
    """Add a file to the processing queue. Returns queue item id."""
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO upload_queue (original_path, filename, file_type, source) "
        "VALUES (?, ?, ?, ?)",
        (original_path, filename, file_type, source)
    )
    conn.commit()
    return cur.lastrowid

def get_queued_upload(db_path: str) -> dict | None:
    """Returns the oldest queued item, or None. Called by background thread."""
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM upload_queue WHERE status = 'queued' "
        "ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None

def update_upload_status(db_path: str, queue_id: int, status: str,
                          ocr_result: str = None, ocr_confidence: float = None,
                          error_message: str = None, linked_bill_id: int = None) -> None:
    conn = get_conn(db_path)
    conn.execute("""
        UPDATE upload_queue SET
          status         = ?,
          ocr_result     = COALESCE(?, ocr_result),
          ocr_confidence = COALESCE(?, ocr_confidence),
          error_message  = COALESCE(?, error_message),
          linked_bill_id = COALESCE(?, linked_bill_id),
          updated_at     = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, ocr_result, ocr_confidence, error_message, linked_bill_id, queue_id))
    conn.commit()

def increment_retry_count(db_path: str, queue_id: int) -> int:
    """Increments retry count. Returns new count."""
    conn = get_conn(db_path)
    cur = conn.execute(
        "UPDATE upload_queue SET retry_count = retry_count + 1 WHERE id = ? "
        "RETURNING retry_count", (queue_id,)
    )
    conn.commit()
    row = cur.fetchone()
    return row[0] if row else 0

def get_queue_listing(db_path: str, limit: int = 50) -> list[dict]:
    """Returns recent queue items for the webapp queue status display."""
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM upload_queue ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    return [dict(r) for r in rows]

def get_queue_item(db_path: str, queue_id: int) -> dict | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM upload_queue WHERE id = ?", (queue_id,)
    ).fetchone()
    return dict(row) if row else None
