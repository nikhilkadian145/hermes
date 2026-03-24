"""Audit Trail API endpoints."""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import os, sys, sqlite3, csv, io

router = APIRouter(prefix="/api/audit", tags=["audit"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path


def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/health")
def health():
    return {"status": "ok", "router": "audit"}


@router.get("")
def list_audit_entries(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    user: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    record_type: Optional[str] = Query(None),
    page: int = Query(1),
    limit: int = Query(50),
):
    conn = _get_conn()
    cur = conn.cursor()
    clauses = []
    params = []

    if from_date:
        clauses.append("created_at >= ?")
        params.append(from_date)
    if to_date:
        clauses.append("created_at <= ?")
        params.append(to_date + " 23:59:59")
    if user:
        clauses.append("source = ?")
        params.append(user)
    if action_type:
        # Support comma-separated multi-select
        types = [t.strip() for t in action_type.split(",")]
        placeholders = ",".join(["?"] * len(types))
        clauses.append(f"action_type IN ({placeholders})")
        params.extend(types)
    if record_type:
        clauses.append("record_type = ?")
        params.append(record_type)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    offset = (page - 1) * limit

    try:
        cur.execute(f"SELECT COUNT(*) FROM audit_log {where}", params)
        total = cur.fetchone()[0]

        cur.execute(f"""
            SELECT * FROM audit_log
            {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        entries = [dict(r) for r in cur.fetchall()]
    except Exception:
        total = 0
        entries = []

    conn.close()
    return {"entries": entries, "total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)}


@router.get("/action-types")
def get_action_types():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT action_type FROM audit_log WHERE action_type IS NOT NULL ORDER BY action_type")
        types = [r[0] for r in cur.fetchall()]
    except Exception:
        types = ["CREATE", "EDIT", "DELETE", "DOWNLOAD", "PROCESS", "EXPORT", "SETTING_CHANGE", "NOTE_ADDED"]
    conn.close()
    return {"types": types}


@router.get("/record-types")
def get_record_types():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT record_type FROM audit_log WHERE record_type IS NOT NULL ORDER BY record_type")
        types = [r[0] for r in cur.fetchall()]
    except Exception:
        types = []
    conn.close()
    return {"types": types}


@router.get("/export")
def export_audit_csv(
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
):
    conn = _get_conn()
    cur = conn.cursor()
    clauses = []
    params = []
    if from_date:
        clauses.append("created_at >= ?")
        params.append(from_date)
    if to_date:
        clauses.append("created_at <= ?")
        params.append(to_date + " 23:59:59")

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    try:
        cur.execute(f"SELECT * FROM audit_log {where} ORDER BY created_at DESC", params)
        rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        rows = []
    conn.close()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("No audit entries found for the selected period.\n")

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_trail.csv"}
    )
