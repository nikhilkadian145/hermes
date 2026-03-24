"""
Phase 28 — Payments API
Record payments against invoices and manual reconciliation.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, List
import sqlite3
import math

router = APIRouter(prefix="/api/payments", tags=["payments"])

def _get_conn():
    from ..database import get_db_path
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

@router.get("")
def list_payments(
    contact_id: Optional[int] = Query(None),
    mode: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100)
):
    conn = _get_conn()
    cur = conn.cursor()

    where_clauses = []
    params: list = []

    if contact_id:
        where_clauses.append("p.client_id = ?")
        params.append(contact_id)
    if mode:
        where_clauses.append("p.mode = ?")
        params.append(mode)
    if from_date:
        where_clauses.append("p.payment_date >= ?")
        params.append(from_date)
    if to_date:
        where_clauses.append("p.payment_date <= ?")
        params.append(to_date)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    cur.execute(f"SELECT COUNT(*) FROM payments p {where_sql}", params)
    total = cur.fetchone()[0]
    total_pages = max(1, math.ceil(total / per_page))
    offset = (page - 1) * per_page

    cur.execute(f"""
        SELECT p.*, c.name as client_name, i.invoice_number
        FROM payments p
        LEFT JOIN clients c ON c.id = p.client_id
        LEFT JOIN invoices i ON i.id = p.invoice_id
        {where_sql}
        ORDER BY p.payment_date DESC, p.id DESC
        LIMIT ? OFFSET ?
    """, params + [per_page, offset])

    payments = [dict(r) for r in cur.fetchall()]
    conn.close()

    return {
        "payments": payments,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }

@router.post("")
def record_payment(
    invoice_ids: List[int] = Body(...),
    amount: float = Body(...),
    date: str = Body(...),
    mode: str = Body(...),
    reference: str = Body(""),
    notes: str = Body("")
):
    """
    Record payment against one or multiple invoices.
    Simple distribution: pays off first fully, then applies remainder to next.
    """
    if not invoice_ids or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid payment payload.")

    conn = _get_conn()
    cur = conn.cursor()

    # Load invoices to verify and apply amounts
    placeholders = ",".join(["?"] * len(invoice_ids))
    cur.execute(f"""
        SELECT id, client_id, total, 
               COALESCE((SELECT SUM(amount) FROM payments WHERE invoice_id = invoices.id), 0) as paid
        FROM invoices WHERE id IN ({placeholders})
        ORDER BY issue_date ASC
    """, invoice_ids)
    
    invoices = cur.fetchall()
    if not invoices:
        conn.close()
        raise HTTPException(status_code=404, detail="No valid invoices found.")
        
    client_id = invoices[0]["client_id"] # Assume all invoices are for same client

    remaining = amount
    created_payments = []

    try:
        for inv in invoices:
            if remaining <= 0: break
            
            due = inv["total"] - inv["paid"]
            if due <= 0: continue
            
            pay_amt = min(due, remaining)
            
            cur.execute("""
                INSERT INTO payments (invoice_id, client_id, amount, payment_date, mode, reference, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (inv["id"], client_id, pay_amt, date, mode, reference, notes))
            
            created_payments.append(cur.lastrowid)
            
            # Check if invoice is fully paid now
            if pay_amt >= due:
                cur.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (inv["id"],))
                
            remaining -= pay_amt
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
        
    return {"status": "success", "payment_ids": created_payments, "amount_applied": amount - remaining, "unapplied": remaining}


@router.get("/reconciliation")
def get_reconciliation_data():
    """Returns HERMES payments + imported bank entries."""
    conn = _get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT id, amount, payment_date as date, mode, reference FROM payments WHERE id NOT IN (SELECT matched_to_payment_id FROM bank_statement_entries WHERE matched_to_payment_id IS NOT NULL)")
    hermes_unmatched = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT * FROM bank_statement_entries WHERE status = 'unmatched'")
    bank_unmatched = [dict(r) for r in cur.fetchall()]
    
    cur.execute("""
        SELECT b.*, p.amount as hermes_amount, p.payment_date as hermes_date, p.reference as hermes_ref
        FROM bank_statement_entries b
        JOIN payments p ON p.id = b.matched_to_payment_id
        WHERE b.status = 'matched'
    """)
    matched = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    # Very basic matching heuristic
    suggestions = []
    for h in hermes_unmatched:
        for b in bank_unmatched:
            if abs(h["amount"] - b["amount"]) < 1.0: # Match amount
                # Add a dummy suggestion payload
                suggestions.append({
                    "payment_id": h["id"],
                    "bank_entry_id": b["id"],
                    "confidence": 92 if h["date"] == b["date"] else 75,
                    "bank_entry_summary": f"{b['description']} (₹{b['amount']}, {b['date']})"
                })
                break
                
    return {
        "unmatched_hermes": hermes_unmatched,
        "unmatched_bank": bank_unmatched,
        "matched": matched,
        "suggestions": suggestions
    }

@router.post("/reconciliation/confirm-match")
def confirm_match(payload: dict = Body(...)):
    """Confirms match between HERMES payment and bank entry."""
    payment_id = payload.get("payment_id")
    bank_entry_id = payload.get("bank_entry_id")
    
    if not payment_id or not bank_entry_id:
        raise HTTPException(status_code=400, detail="Missing IDs")
        
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE bank_statement_entries SET status = 'matched', matched_to_payment_id = ? WHERE id = ?", (payment_id, bank_entry_id))
    conn.commit()
    conn.close()
    
    return {"status": "success"}

@router.post("/reconciliation/ignore")
def ignore_bank_entry(payload: dict = Body(...)):
    bank_entry_id = payload.get("bank_entry_id")
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE bank_statement_entries SET status = 'ignored' WHERE id = ?", (bank_entry_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
