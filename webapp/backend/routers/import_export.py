"""Import / Export API endpoints."""
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import os, sys, sqlite3, csv, io, json, uuid, time

router = APIRouter(tags=["import_export"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path


def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Sample Templates
# ---------------------------------------------------------------------------
@router.get("/api/import/{import_type}/sample.csv")
def download_sample_template(import_type: str):
    templates = {
        "contacts": "name,type,gstin,email,phone,address\nAcme Corp,vendor,27AABCT1332L1ZD,acme@example.com,9876543210,Mumbai MH\n",
        "opening-balances": "account_code,account_name,debit,credit\n1000,Cash,50000,0\n2000,Accounts Payable,0,25000\n",
        "bank-statement": "date,description,reference,debit,credit,balance\n2025-01-15,Payment received,TXN001,0,15000,65000\n2025-01-16,Vendor payment,TXN002,8000,0,57000\n",
    }
    content = templates.get(import_type, "column1,column2\nvalue1,value2\n")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={import_type}_sample.csv"}
    )


# ---------------------------------------------------------------------------
# Import: Contacts
# ---------------------------------------------------------------------------
@router.post("/api/import/contacts")
async def import_contacts(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    errors = []
    valid_count = 0

    for i, row in enumerate(reader):
        r = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        err = []
        if not r.get("name"):
            err.append("Name is required")
        if r.get("type") and r["type"] not in ("vendor", "customer", "both"):
            err.append("Type must be vendor, customer, or both")
        rows.append({**r, "row": i + 2, "errors": err, "valid": len(err) == 0})
        if not err:
            valid_count += 1

    # If confirm import (second call with ?confirm=true)
    return {
        "total": len(rows),
        "valid": valid_count,
        "error_count": len(rows) - valid_count,
        "preview": rows[:20],
        "all_rows": rows,
    }


@router.post("/api/import/contacts/confirm")
async def confirm_import_contacts(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    conn = _get_conn()
    cur = conn.cursor()
    imported = 0
    errors = []

    for i, row in enumerate(reader):
        r = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        if not r.get("name"):
            errors.append({"row": i + 2, "reason": "Name is required"})
            continue
        try:
            cur.execute("""
                INSERT INTO contacts (name, type, gstin, email, phone, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (r.get("name"), r.get("type", "vendor"), r.get("gstin"), r.get("email"), r.get("phone"), r.get("address")))
            imported += 1
        except Exception as e:
            errors.append({"row": i + 2, "reason": str(e)})

    conn.commit()
    conn.close()
    return {"imported": imported, "errors": errors, "error_count": len(errors)}


# ---------------------------------------------------------------------------
# Import: Opening Balances
# ---------------------------------------------------------------------------
@router.post("/api/import/opening-balances")
async def import_opening_balances(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    valid_count = 0

    for i, row in enumerate(reader):
        r = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        err = []
        if not r.get("account_code"):
            err.append("Account code is required")
        if not r.get("account_name"):
            err.append("Account name is required")
        rows.append({**r, "row": i + 2, "errors": err, "valid": len(err) == 0})
        if not err:
            valid_count += 1

    return {"total": len(rows), "valid": valid_count, "error_count": len(rows) - valid_count, "preview": rows[:20]}


# ---------------------------------------------------------------------------
# Import: Bank Statement
# ---------------------------------------------------------------------------
@router.post("/api/import/bank-statement")
async def import_bank_statement(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    valid_count = 0

    for i, row in enumerate(reader):
        r = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        err = []
        if not r.get("date"):
            err.append("Date is required")
        if not r.get("description"):
            err.append("Description is required")
        rows.append({**r, "row": i + 2, "errors": err, "valid": len(err) == 0})
        if not err:
            valid_count += 1

    return {"total": len(rows), "valid": valid_count, "error_count": len(rows) - valid_count, "preview": rows[:20]}


# ---------------------------------------------------------------------------
# Export: Full Data Backup
# ---------------------------------------------------------------------------
_export_jobs = {}

@router.post("/api/export/data")
def start_export():
    job_id = str(uuid.uuid4())[:8]
    _export_jobs[job_id] = {"status": "ready", "started": time.time()}
    return {"job_id": job_id, "status": "ready"}


@router.get("/api/export/data/{job_id}/status")
def export_status(job_id: str):
    job = _export_jobs.get(job_id, {"status": "not_found"})
    return {"job_id": job_id, "status": job.get("status", "ready")}


@router.get("/api/export/data/{job_id}/download")
def export_download(job_id: str):
    conn = _get_conn()
    cur = conn.cursor()
    data = {}

    for table in ["contacts", "invoices", "purchase_bills", "expenses", "payments"]:
        try:
            cur.execute(f"SELECT * FROM {table}")
            data[table] = [dict(r) for r in cur.fetchall()]
        except Exception:
            data[table] = []

    conn.close()
    content = json.dumps(data, indent=2, default=str)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=hermes_export_{job_id}.json"}
    )


# ---------------------------------------------------------------------------
# Bulk Document Download
# ---------------------------------------------------------------------------
@router.get("/api/files/bulk-download")
def bulk_download(ids: str = Query("")):
    # For demo purposes return a JSON manifest of requested files
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    return {
        "message": f"Bulk download of {len(id_list)} files prepared (demo).",
        "file_count": len(id_list),
        "ids": id_list,
    }
