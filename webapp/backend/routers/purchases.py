import os
from typing import Optional, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..database import get_db_path
import hermes.db as db

router = APIRouter(prefix="/api/invoices/purchases", tags=["purchases"])

@router.get("/")
def get_purchase_bills(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db_path: str = Depends(get_db_path)
):
    """Get paginated list of purchase bills (expenses + upload queue view)."""
    return db.get_purchase_bills_paginated(
        db_path,
        status=status,
        search=search,
        page=page,
        per_page=per_page
    )

@router.get("/{expense_id}")
def get_purchase_bill_detail(expense_id: int, db_path: str = Depends(get_db_path)):
    """Get full bill detail with items and metadata."""
    bill = db.get_purchase_bill_detail(db_path, expense_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/{expense_id}/original")
def get_bill_original_file(expense_id: int, db_path: str = Depends(get_db_path)):
    """Serve the original uploaded file for the viewer."""
    bill = db.get_purchase_bill_detail(db_path, expense_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    receipt_path = bill.get('receipt_path')
    # If the upload queue has the filename (in our DB `filename` is the partial or full path we stored)
    if not receipt_path and bill.get('upload') and bill['upload'].get('filename'):
        # Fallback to upload queue's filename if expense header isn't fully updated yet
        receipt_path = bill['upload']['filename']
        
    if not receipt_path:
        raise HTTPException(status_code=404, detail="Original file path not found for this bill")
        
    # We resolve it relative to the process working directory
    full_path = os.path.abspath(receipt_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Original file not found on server")
        
    return FileResponse(full_path)

class BillFinalizeRequest(BaseModel):
    expense_data: dict
    items: List[dict]

@router.post("/{expense_id}/finalize")
def finalize_purchase_bill(expense_id: int, req: BillFinalizeRequest, db_path: str = Depends(get_db_path)):
    """Mark a REVIEW-status bill as finalized with corrected extracted data."""
    # Ensure expense exists
    bill = db.get_purchase_bill_detail(db_path, expense_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    db.finalize_purchase_bill(
        db_path,
        expense_id,
        expense_data=req.expense_data,
        items=req.items
    )
    return {"status": "success", "expense_id": expense_id}
