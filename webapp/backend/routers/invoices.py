from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional, Any
from datetime import date
from pydantic import BaseModel
import os

from ..database import get_db_path
import hermes.db as db

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

@router.get("/health")
def health():
    return {"status": "ok", "router": "invoices"}

@router.get("/sales")
def get_sales_invoices(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    search: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db_path: str = Depends(get_db_path)
):
    """Get paginated list of sales invoices with summary stats."""
    return db.get_sales_invoices_paginated(
        db_path=db_path,
        status=status,
        client_id=client_id,
        search=search,
        from_date=from_date,
        to_date=to_date,
        page=page,
        per_page=per_page
    )

@router.get("/sales/{invoice_id}")
def get_sales_invoice_detail(invoice_id: int, db_path: str = Depends(get_db_path)):
    """Get full details of a specific invoice."""
    inv = db.get_invoice(db_path, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv

class PaymentReq(BaseModel):
    amount: float
    payment_date: Optional[str] = None
    mode: str = "other"
    reference: str = ""
    notes: str = ""

@router.post("/sales/{invoice_id}/mark-paid")
def mark_invoice_paid(invoice_id: int, req: Optional[PaymentReq] = None, db_path: str = Depends(get_db_path)):
    """Record payment and mark invoice as paid."""
    inv = db.get_invoice(db_path, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    amount = req.amount if req else inv["total"]
    payment_date = req.payment_date if req and req.payment_date else date.today().isoformat()
    mode = req.mode if req else "other"
    reference = req.reference if req else ""
    notes = req.notes if req else ""

    db.record_payment(
        db_path, invoice_id, amount,
        payment_date=payment_date, mode=mode,
        reference=reference, notes=notes
    )
    return {"status": "success", "invoice_id": invoice_id}

@router.post("/sales/{invoice_id}/void")
def void_invoice(invoice_id: int, db_path: str = Depends(get_db_path)):
    """Mark an invoice as void (cancelled)."""
    inv = db.get_invoice(db_path, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if inv["status"] == "paid":
        raise HTTPException(status_code=400, detail="Cannot void a paid invoice")
        
    db.update_invoice_status(db_path, invoice_id, "cancelled")
    return {"status": "success", "invoice_id": invoice_id}

@router.get("/sales/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db_path: str = Depends(get_db_path)):
    """Stream the invoice PDF file."""
    inv = db.get_invoice(db_path, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    pdf_path = inv.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found or not generated yet")
        
    filename = os.path.basename(pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)

@router.get("/sales/{invoice_id}/payment-history")
def get_invoice_payment_history(invoice_id: int, db_path: str = Depends(get_db_path)):
    """List all payments recorded for an invoice."""
    return db.get_payments_for_invoice(db_path, invoice_id)

class NotesReq(BaseModel):
    notes: str

@router.patch("/sales/{invoice_id}/notes")
def update_invoice_notes(invoice_id: int, req: NotesReq, db_path: str = Depends(get_db_path)):
    """Update notes on an invoice."""
    conn = db.get_conn(db_path)
    conn.execute(
        "UPDATE invoices SET notes = ?, updated_at = datetime('now') WHERE id = ?",
        (req.notes, invoice_id)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}
