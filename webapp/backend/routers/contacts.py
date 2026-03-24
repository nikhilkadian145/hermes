"""
Phase 27 — Contacts API
Customer and vendor management with full ledger visibility.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Optional
import os
import sys
import math

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def _get_conn():
    import sqlite3
    from ..database import get_db_path
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


# ────────────────────────────────────────────────────────────────
# GET /api/contacts — paginated listing with type/search filter
# ────────────────────────────────────────────────────────────────
@router.get("")
def list_contacts(
    type: Optional[str] = Query(None, description="customer|vendor|all"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    conn = _get_conn()
    cur = conn.cursor()

    where_clauses = []
    params: list = []

    if type and type != "all":
        where_clauses.append("c.client_type = ?")
        params.append(type)

    if search:
        where_clauses.append("(c.name LIKE ? OR c.gstin LIKE ? OR c.phone LIKE ?)")
        q = f"%{search}%"
        params.extend([q, q, q])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Count
    cur.execute(f"SELECT COUNT(*) FROM clients c {where_sql}", params)
    total = cur.fetchone()[0]
    total_pages = max(1, math.ceil(total / per_page))
    offset = (page - 1) * per_page

    # Fetch contacts with aggregated financial data
    cur.execute(f"""
        SELECT c.*,
            COALESCE((SELECT SUM(i.total) FROM invoices i WHERE i.client_id = c.id), 0) as total_billed,
            COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.client_id = c.id), 0) as total_paid,
            COALESCE((SELECT COUNT(*) FROM invoices i WHERE i.client_id = c.id), 0) as total_transactions,
            COALESCE((SELECT COUNT(*) FROM invoices i WHERE i.client_id = c.id AND i.status = 'overdue'), 0) as overdue_count
        FROM clients c
        {where_sql}
        ORDER BY c.name ASC
        LIMIT ? OFFSET ?
    """, params + [per_page, offset])

    contacts = []
    for row in cur.fetchall():
        outstanding = (row["total_billed"] or 0) - (row["total_paid"] or 0)
        contacts.append({
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"],
            "email": row["email"],
            "address": row["address"],
            "gstin": row["gstin"],
            "client_type": row["client_type"] if "client_type" in row.keys() else "customer",
            "total_billed": row["total_billed"],
            "total_paid": row["total_paid"],
            "outstanding": outstanding,
            "total_transactions": row["total_transactions"],
            "overdue_count": row["overdue_count"],
            "created_at": row["created_at"],
        })

    conn.close()
    return {
        "contacts": contacts,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


# ────────────────────────────────────────────────────────────────
# GET /api/contacts/:id — full detail with history
# ────────────────────────────────────────────────────────────────
@router.get("/{contact_id}")
def get_contact_detail(contact_id: int):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients WHERE id = ?", (contact_id,))
    contact = cur.fetchone()
    if not contact:
        conn.close()
        raise HTTPException(status_code=404, detail="Contact not found")

    # Financial totals
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE client_id = ?", (contact_id,))
    total_billed = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE client_id = ?", (contact_id,))
    total_paid = cur.fetchone()[0]

    cur.execute("SELECT MAX(payment_date) FROM payments WHERE client_id = ?", (contact_id,))
    last_payment = cur.fetchone()[0]

    # Recent invoices
    cur.execute("""
        SELECT id, invoice_number, issue_date, due_date, total, status
        FROM invoices WHERE client_id = ?
        ORDER BY issue_date DESC LIMIT 50
    """, (contact_id,))
    invoices = [dict(r) for r in cur.fetchall()]

    # Recent payments
    cur.execute("""
        SELECT p.id, p.amount, p.payment_date, p.mode, p.reference,
               i.invoice_number
        FROM payments p
        LEFT JOIN invoices i ON i.id = p.invoice_id
        WHERE p.client_id = ?
        ORDER BY p.payment_date DESC LIMIT 50
    """, (contact_id,))
    payments = [dict(r) for r in cur.fetchall()]

    conn.close()

    return {
        "id": contact["id"],
        "name": contact["name"],
        "phone": contact["phone"],
        "email": contact["email"],
        "address": contact["address"],
        "gstin": contact["gstin"],
        "notes": contact["notes"],
        "client_type": contact["client_type"] if "client_type" in contact.keys() else "customer",
        "created_at": contact["created_at"],
        "total_billed": total_billed,
        "total_paid": total_paid,
        "outstanding": total_billed - total_paid,
        "last_payment_date": last_payment,
        "invoices": invoices,
        "payments": payments,
    }


# ────────────────────────────────────────────────────────────────
# GET /api/contacts/:id/ledger — running balance
# ────────────────────────────────────────────────────────────────
@router.get("/{contact_id}/ledger")
def get_contact_ledger(
    contact_id: int,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
):
    conn = _get_conn()
    cur = conn.cursor()

    # Combine invoices (debits) and payments (credits) into one ledger
    entries = []

    # Invoices = money owed to us (debit)
    date_filter_inv = ""
    date_params_inv: list = [contact_id]
    if from_date:
        date_filter_inv += " AND i.issue_date >= ?"
        date_params_inv.append(from_date)
    if to_date:
        date_filter_inv += " AND i.issue_date <= ?"
        date_params_inv.append(to_date)

    cur.execute(f"""
        SELECT i.issue_date as date, 'Invoice ' || i.invoice_number as description,
               i.total as debit, 0 as credit
        FROM invoices i WHERE i.client_id = ? {date_filter_inv}
    """, date_params_inv)
    entries.extend([dict(r) for r in cur.fetchall()])

    # Payments = money received (credit)
    date_filter_pay = ""
    date_params_pay: list = [contact_id]
    if from_date:
        date_filter_pay += " AND p.payment_date >= ?"
        date_params_pay.append(from_date)
    if to_date:
        date_filter_pay += " AND p.payment_date <= ?"
        date_params_pay.append(to_date)

    cur.execute(f"""
        SELECT p.payment_date as date,
               'Payment — ' || p.mode || CASE WHEN p.reference != '' THEN ' (' || p.reference || ')' ELSE '' END as description,
               0 as debit, p.amount as credit
        FROM payments p WHERE p.client_id = ? {date_filter_pay}
    """, date_params_pay)
    entries.extend([dict(r) for r in cur.fetchall()])

    conn.close()

    # Sort by date
    entries.sort(key=lambda e: e["date"] or "")

    # Calculate running balance
    balance = 0
    for entry in entries:
        balance += entry["debit"] - entry["credit"]
        entry["balance"] = balance

    return {"entries": entries, "closing_balance": balance}


# ────────────────────────────────────────────────────────────────
# PATCH /api/contacts/:id/notes — auto-save notes
# ────────────────────────────────────────────────────────────────
@router.patch("/{contact_id}/notes")
def update_contact_notes(contact_id: int, notes: str = Body(..., embed=True)):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE clients SET notes = ?, updated_at = datetime('now') WHERE id = ?", (notes, contact_id))
    conn.commit()
    conn.close()
    return {"ok": True}


# ────────────────────────────────────────────────────────────────
# GET /api/contacts/:id/statement/pdf — placeholder for statement
# ────────────────────────────────────────────────────────────────
@router.get("/{contact_id}/statement/pdf")
def download_statement(contact_id: int):
    """Placeholder — would generate a PDF statement via hermes.pdf"""
    return JSONResponse(
        status_code=501,
        content={"detail": "Statement PDF generation not yet implemented."},
    )
