from fastapi import APIRouter, Query
from typing import List, Optional
import random
from ..database import (
    get_dashboard_kpis, 
    get_revenue_expenses, 
    get_expense_breakdown, 
    get_invoice_status, 
    get_recent_activity
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/kpis")
def kpis():
    return get_dashboard_kpis()

@router.get("/charts/revenue-expenses")
def revenue_expenses(months: int = Query(12)):
    return get_revenue_expenses(months)

@router.get("/charts/expense-breakdown")
def expense_breakdown(month: str = Query("current")):
    return get_expense_breakdown(month)

@router.get("/charts/invoice-status")
def invoice_status(months: int = Query(6)):
    return get_invoice_status(months)

@router.get("/activity")
def activity(limit: int = Query(20)):
    return get_recent_activity(limit)

@router.get("/sparkline/{metric}")
def sparkline(metric: str):
    return [random.randint(10, 100) for _ in range(7)]

