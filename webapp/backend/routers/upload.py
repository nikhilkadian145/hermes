import os
import json
import shutil
import uuid
import csv
import io
import sqlite3
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

import hermes.db as db
from ..database import get_db_path

# Get CUSTOMER_DATA_DIR from env or default
CUSTOMER_DATA_DIR = os.environ.get("CUSTOMER_DATA_DIR", os.path.join(os.getcwd(), "data"))
UPLOADS_DIR = os.path.join(CUSTOMER_DATA_DIR, "uploads")

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/tiff": "tiff",
}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

@router.post("/upload/bills")
async def upload_bills(files: List[UploadFile] = File(...), db_path: str = Depends(get_db_path)):
    """
    Accept one or more vendor bill files.
    Save each to disk, enqueue for OCR processing.
    Returns list of queue items created.
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    results = []

    for file in files:
        # Validate content type
        file_type = ALLOWED_TYPES.get(file.content_type)
        if not file_type:
            # Fallback based on filename extension
            ext = os.path.splitext(file.filename)[1].lower()
            ext_map = {'.pdf': 'pdf', '.jpg': 'jpg', '.jpeg': 'jpeg', '.png': 'png', '.tiff': 'tiff'}
            file_type = ext_map.get(ext)
            
        if not file_type:
            results.append({
                "filename": file.filename,
                "error": f"Unsupported file type: {file.content_type}"
            })
            continue

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            results.append({
                "filename": file.filename,
                "error": "File exceeds 25MB limit"
            })
            continue

        # Save with a unique name to prevent collisions
        unique_name = f"{uuid.uuid4()}_{file.filename.replace(' ', '_')}"
        save_path = os.path.join(UPLOADS_DIR, unique_name)
        with open(save_path, "wb") as f:
            f.write(content)

        # Enqueue
        queue_id = db.enqueue_upload(
            db_path, save_path, file.filename, file_type, source="webapp"
        )
        results.append({
            "queue_id": queue_id,
            "filename": file.filename,
            "status": "queued"
        })

    return {"uploaded": results}


@router.get("/upload/queue")
async def get_queue(db_path: str = Depends(get_db_path)):
    """Returns current queue status for all recent uploads."""
    items = db.get_queue_listing(db_path, limit=50)
    return {"items": items}


@router.get("/upload/queue/{queue_id}")
async def get_queue_item(queue_id: int, db_path: str = Depends(get_db_path)):
    """Returns a single queue item with its OCR result."""
    item = db.get_queue_item(db_path, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    # Parse OCR result if present
    if item.get("ocr_result"):
        try:
            item["ocr_result"] = json.loads(item["ocr_result"])
        except json.JSONDecodeError:
            pass
    return item


@router.post("/upload/queue/{queue_id}/requeue")
async def requeue_item(queue_id: int, db_path: str = Depends(get_db_path)):
    """Reset a failed item back to queued for retry."""
    item = db.get_queue_item(db_path, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.update_upload_status(db_path, queue_id, "queued", error_message=None)
    return {"status": "queued"}


@router.post("/upload/queue/{queue_id}/finalize")
async def finalize_bill(queue_id: int, data: dict, db_path: str = Depends(get_db_path)):
    """
    Called when user confirms the extracted data on the Bill Review page.
    Writes the confirmed data to the expenses table.
    Marks queue item as finalized.
    """
    item = db.get_queue_item(db_path, queue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    if item["status"] not in ("review", "error"):
        raise HTTPException(status_code=400, detail=f"Cannot finalize item with status: {item['status']}")

    # Write to expenses table
    expense_id = db.log_expense(
        db_path=db_path,
        date=data.get("bill_date"),
        description=data.get("vendor", "Vendor Bill"),
        category=data.get("category", "supplies"),
        amount=data.get("amount", 0),
        vendor=data.get("vendor"),
        receipt_path=item["original_path"],
        ocr_raw=item.get("ocr_result"),
        notes=data.get("notes"),
        # New GST fields:
        vendor_gstin=data.get("vendor_gstin"),
        bill_number=data.get("bill_number"),
        bill_date=data.get("bill_date"),
        gst_rate=data.get("gst_rate", 0),
        cgst_amount=data.get("cgst", 0),
        sgst_amount=data.get("sgst", 0),
        igst_amount=data.get("igst", 0),
        itc_eligible=data.get("itc_eligible", True)
    )

    # Mark queue item finalized
    db.update_upload_status(db_path, queue_id, "finalized", linked_bill_id=expense_id)

    return {"status": "finalized", "expense_id": expense_id}


@router.get("/invoices/purchases/review/{queue_id}/original")
async def serve_original_document(queue_id: int, db_path: str = Depends(get_db_path)):
    """
    Serves the original uploaded file for the Bill Review page document viewer.
    Validates the path is within CUSTOMER_DATA_DIR before serving.
    """
    item = db.get_queue_item(db_path, queue_id)
    if not item:
        raise HTTPException(status_code=404)

    path = item["original_path"]

    # Security: ensure path is within allowed directory
    if not os.path.abspath(path).startswith(os.path.abspath(CUSTOMER_DATA_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path,
        media_type="application/octet-stream" if not item["filename"].endswith(".pdf") else "application/pdf",
        filename=item["filename"]
    )

@router.post("/upload/bank-statement")
async def upload_bank_statement(file: UploadFile = File(...), db_path: str = Depends(get_db_path)):
    """Reads a CSV bank statement and imports rows into bank_statement_entries."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.reader(io.StringIO(text))
    
    header = next(reader, None)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    imported = 0
    for row in reader:
        if len(row) < 5: 
            continue
            
        try:
            date = row[0][:10]
            desc = row[1]
            ref = row[2]
            debit = float(row[3].replace(',', '')) if row[3] else 0.0
            credit = float(row[4].replace(',', '')) if len(row) > 4 and row[4] else 0.0
            
            amount = debit if debit > 0 else credit
            typ = "debit" if debit > 0 else "credit"
            if amount == 0:
                continue
                
            cur.execute(
                "INSERT INTO bank_statement_entries (date, description, reference, amount, type) VALUES (?, ?, ?, ?, ?)",
                (date, desc, ref, amount, typ)
            )
            imported += 1
        except Exception:
            continue
            
    conn.commit()
    conn.close()
    
    return {"status": "success", "imported": imported}
