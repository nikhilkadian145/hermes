"""Global Search API endpoint."""
from fastapi import APIRouter, Query
from typing import Optional
import os, sys, sqlite3

router = APIRouter(prefix="/api/search", tags=["search"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path


def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/health")
def health():
    return {"status": "ok", "router": "search"}


@router.get("")
def global_search(
    q: str = Query("", min_length=0),
    types: Optional[str] = Query(None),
):
    if not q or len(q.strip()) < 1:
        return {"invoices": [], "contacts": [], "documents": [], "reports": []}

    conn = _get_conn()
    cur = conn.cursor()
    pattern = f"%{q.strip()}%"
    allowed_types = set(types.split(",")) if types else {"invoices", "contacts", "documents", "reports"}
    results = {}

    # Search invoices (sales + purchases)
    if "invoices" in allowed_types:
        try:
            invoices = []
            # Sales invoices
            cur.execute("""
                SELECT id, invoice_number AS number, client_name, total_amount AS amount, status, 'sales' AS source
                FROM invoices
                WHERE invoice_number LIKE ? OR client_name LIKE ?
                ORDER BY created_at DESC LIMIT 5
            """, (pattern, pattern))
            invoices.extend([dict(r) for r in cur.fetchall()])

            # Purchase bills
            cur.execute("""
                SELECT id, bill_number AS number, vendor_name AS client_name, total AS amount, status, 'purchases' AS source
                FROM purchase_bills
                WHERE bill_number LIKE ? OR vendor_name LIKE ?
                ORDER BY created_at DESC LIMIT 5
            """, (pattern, pattern))
            invoices.extend([dict(r) for r in cur.fetchall()])
            results["invoices"] = invoices[:5]
        except Exception:
            results["invoices"] = []

    # Search contacts
    if "contacts" in allowed_types:
        try:
            cur.execute("""
                SELECT id, name, type, gstin
                FROM contacts
                WHERE name LIKE ? OR gstin LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name LIMIT 5
            """, (pattern, pattern, pattern, pattern))
            results["contacts"] = [dict(r) for r in cur.fetchall()]
        except Exception:
            results["contacts"] = []

    # Search documents
    if "documents" in allowed_types:
        try:
            cur.execute("""
                SELECT id, filename, file_type AS type, linked_entity AS linked_to
                FROM documents
                WHERE filename LIKE ? OR file_type LIKE ?
                ORDER BY created_at DESC LIMIT 5
            """, (pattern, pattern))
            results["documents"] = [dict(r) for r in cur.fetchall()]
        except Exception:
            results["documents"] = []

    # Search reports (use report_templates as a source)
    if "reports" in allowed_types:
        try:
            cur.execute("""
                SELECT id, name, 'custom' AS type, created_at
                FROM report_templates
                WHERE name LIKE ?
                ORDER BY created_at DESC LIMIT 5
            """, (pattern,))
            results["reports"] = [dict(r) for r in cur.fetchall()]
        except Exception:
            results["reports"] = []

    conn.close()
    return results
