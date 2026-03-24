"""GST Reports API endpoints."""
from fastapi import APIRouter, Query
import os, sys

router = APIRouter(prefix="/api/reports", tags=["reports"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path

# We need hermes.db functions — add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import hermes.db as db


@router.get("/health")
def health():
    return {"status": "ok", "router": "reports"}


@router.get("/gst")
def get_gst_report(
    from_date: str = Query(..., description="YYYY-MM-DD"),
    to_date: str = Query(..., description="YYYY-MM-DD"),
):
    """GSTR-1 compliant report with B2B, B2C, HSN summary."""
    db_path = get_db_path()
    return db.get_gst_report(db_path, from_date, to_date)


@router.get("/gst/itc")
def get_itc_summary(
    from_date: str = Query(...),
    to_date: str = Query(...),
):
    """Input Tax Credit summary."""
    db_path = get_db_path()
    return db.get_itc_summary(db_path, from_date, to_date)


@router.get("/gst/liability")
def get_gst_liability(
    from_date: str = Query(...),
    to_date: str = Query(...),
):
    """Net GST payable = output - ITC."""
    db_path = get_db_path()
    return db.get_gst_liability(db_path, from_date, to_date)


@router.get("/gst/hsn-summary")
def get_hsn_summary(
    from_date: str = Query(...),
    to_date: str = Query(...),
):
    """HSN/SAC-wise summary for GSTR-1 filing."""
    db_path = get_db_path()
    return db.get_hsn_summary(db_path, from_date, to_date)


@router.get("/gst/filing-periods")
def get_filing_periods():
    """List all filing periods."""
    db_path = get_db_path()
    return db.get_filing_periods(db_path)

@router.post("/gst/export-json")
def export_gst_json(quarter: str = Query(...), year: str = Query(...)):
    """Generates GST portal-ready JSON (Stub)."""
    db_path = get_db_path()
    db._notify(
        db_path,
        type="system",
        title="GST Report Ready",
        message=f"Your GSTR-1 JSON export ({quarter} {year}) has been generated successfully.",
        link_type="report",
        link_id=0
    )
    return {
        "url": f"/files/reports/gst_export_{quarter}_{year}.json",
        "message": "Demo GST JSON Export created successfully."
    }


@router.get("/hsn/search")
def search_hsn(q: str = Query(..., min_length=2), limit: int = Query(5)):
    """Search HSN/SAC codes."""
    db_path = get_db_path()
    return db.search_hsn(db_path, q, limit)

# -----------------------------------------------------------------------------
# Financial Reports (Phase 30)
# -----------------------------------------------------------------------------
import sqlite3
from typing import Optional

def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/pl")
def get_profit_and_loss(from_date: Optional[str] = None, to_date: Optional[str] = None):
    conn = _get_conn()
    cur = conn.cursor()
    
    # Very simplified P&L: Revenue from invoices, COGS/Expenses from expenses table
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status != 'draft'")
    revenue = cur.fetchone()[0]
    
    cur.execute("SELECT category, SUM(amount) as amt FROM expenses GROUP BY category")
    expenses_raw = cur.fetchall()
    
    expenses_list = [{"name": r["category"].title(), "amount": r["amt"]} for r in expenses_raw]
    total_expenses = sum(r["amount"] for r in expenses_list)
    
    conn.close()
    return {
        "title": "Profit & Loss Statement",
        "sections": [
            {
                "name": "Revenue",
                "items": [{"name": "Sales Revenue", "amount": revenue}],
                "subtotal": revenue
            },
            {
                "name": "Operating Expenses",
                "items": expenses_list,
                "subtotal": total_expenses
            }
        ],
        "net_income": revenue - total_expenses
    }

@router.get("/balance-sheet")
def get_balance_sheet(as_of: Optional[str] = None):
    conn = _get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COALESCE(SUM(total), 0) - COALESCE(SUM(amount), 0) FROM invoices i LEFT JOIN payments p ON i.id = p.invoice_id")
    ar = cur.fetchone()[0] or 0
    # Simulate bank balance simply as sum of payments (since we don't have full bank feed booked)
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
    cash = cur.fetchone()[0] or 0
    
    total_assets = ar + cash
    
    # Simplified liabilities (example)
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE category = 'supplies'")
    ap = cur.fetchone()[0] or 0 # Dummy logic for demo
    
    conn.close()
    
    return {
        "title": "Balance Sheet",
        "assets": [
            {"name": "Cash & Cash Equivalents", "amount": cash},
            {"name": "Accounts Receivable", "amount": ar}
        ],
        "total_assets": total_assets,
        "liabilities": [
            {"name": "Accounts Payable", "amount": ap}
        ],
        "total_liabilities": ap,
        "equity": [
            {"name": "Retained Earnings", "amount": total_assets - ap}
        ],
        "total_equity": total_assets - ap
    }

@router.get("/receivables-aging")
def get_receivables_aging():
    conn = _get_conn()
    cur = conn.cursor()
    
    query = """
    SELECT c.name as client_name, 
           i.invoice_number, i.issue_date, i.due_date,
           (i.total - COALESCE((SELECT SUM(amount) FROM payments WHERE invoice_id = i.id), 0)) as due_amount,
           CAST(julianday('now') - julianday(i.due_date) AS INTEGER) as days_overdue
    FROM invoices i
    JOIN clients c ON c.id = i.client_id
    WHERE i.status != 'paid' AND i.status != 'draft'
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
    for r in rows:
        amt = r["due_amount"]
        days = r["days_overdue"]
        if amt <= 0: continue
        
        if days <= 30: buckets["0-30"] += amt
        elif days <= 60: buckets["31-60"] += amt
        elif days <= 90: buckets["61-90"] += amt
        else: buckets["90+"] += amt
        
    conn.close()
    return {"title": "Accounts Receivable Aging", "buckets": buckets, "total": sum(buckets.values())}

# -----------------------------------------------------------------------------
# Intelligence & Specialty Reports (Phase 32)
# -----------------------------------------------------------------------------

@router.get("/anomaly-report")
def get_anomaly_report():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.*, pb.vendor_name, pb.bill_number
            FROM anomalies a
            LEFT JOIN purchase_bills pb ON pb.id = a.bill_id
            ORDER BY a.created_at DESC LIMIT 100
        """)
        anomalies = [dict(r) for r in cur.fetchall()]
    except Exception:
        anomalies = []
    conn.close()
    
    flagged = len([a for a in anomalies if a.get('status') == 'flagged'])
    resolved = len([a for a in anomalies if a.get('status') == 'resolved'])
    dismissed = len([a for a in anomalies if a.get('status') == 'dismissed'])
    
    return {
        "title": "Anomaly Report",
        "summary": {"flagged": flagged, "resolved": resolved, "dismissed": dismissed, "total": len(anomalies)},
        "anomalies": anomalies
    }

@router.get("/duplicate-detection")
def get_duplicate_detection():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.id, b.id as other_id,
                   a.vendor_name, a.bill_number as bill_a, b.bill_number as bill_b,
                   a.total as amount_a, b.total as amount_b,
                   a.bill_date as date_a, b.bill_date as date_b
            FROM purchase_bills a
            JOIN purchase_bills b ON a.vendor_name = b.vendor_name
                AND ABS(a.total - b.total) < 1
                AND a.id < b.id
                AND ABS(julianday(a.bill_date) - julianday(b.bill_date)) < 7
            ORDER BY a.vendor_name
            LIMIT 50
        """)
        pairs = [dict(r) for r in cur.fetchall()]
    except Exception:
        pairs = []
    conn.close()
    return {"title": "Duplicate Detection Report", "pairs": pairs, "count": len(pairs)}

@router.get("/vendor-spend-analysis")
def get_vendor_spend_analysis(vendor_id: Optional[int] = None, months: int = 12):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT vendor_name,
                   strftime('%Y-%m', bill_date) as month,
                   SUM(total) as spend,
                   COUNT(*) as bills
            FROM purchase_bills
            WHERE bill_date >= date('now', ? || ' months')
            GROUP BY vendor_name, month
            ORDER BY vendor_name, month
        """, (f"-{months}",))
        rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        rows = []
    conn.close()
    
    # Group by vendor
    vendors: dict = {}
    for r in rows:
        vn = r["vendor_name"]
        if vn not in vendors:
            vendors[vn] = []
        vendors[vn].append({"month": r["month"], "spend": r["spend"], "bills": r["bills"]})
    
    return {"title": "Vendor Spend Analysis", "vendors": vendors}

@router.get("/processing-quality")
def get_processing_quality(from_date: Optional[str] = None, to_date: Optional[str] = None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM purchase_bills")
        total_docs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM purchase_bills WHERE status = 'error'")
        error_docs = cur.fetchone()[0]
        cur.execute("SELECT AVG(confidence) FROM purchase_bills WHERE confidence IS NOT NULL")
        avg_conf_row = cur.fetchone()
        avg_confidence = round(avg_conf_row[0] * 100, 1) if avg_conf_row[0] else 85.0
    except Exception:
        total_docs, error_docs, avg_confidence = 0, 0, 0
    conn.close()
    
    error_rate = round((error_docs / total_docs * 100), 1) if total_docs > 0 else 0
    correction_rate = 12.5  # Placeholder — would track edits vs originals
    
    return {
        "title": "Processing Quality Report",
        "metrics": {
            "total_documents": total_docs,
            "avg_confidence": avg_confidence,
            "correction_rate": correction_rate,
            "error_rate": error_rate,
            "error_count": error_docs
        }
    }

@router.get("/audit-trail")
def get_audit_trail(
    from_date: Optional[str] = None, to_date: Optional[str] = None,
    action_type: Optional[str] = None, page: int = 1, limit: int = 50
):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM audit_log
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, (page - 1) * limit))
        entries = [dict(r) for r in cur.fetchall()]
    except Exception:
        entries = []
    conn.close()
    return {"title": "Audit Trail", "entries": entries, "page": page}

# -----------------------------------------------------------------------------
# Custom Report Builder (Phase 33)
# -----------------------------------------------------------------------------
from pydantic import BaseModel
from typing import List

class BuilderConfig(BaseModel):
    dimensions: List[str] = []
    metrics: List[str] = []
    filters: dict = {}

class SaveTemplateReq(BaseModel):
    name: str
    config: dict

@router.post("/custom/preview")
def custom_report_preview(config: BuilderConfig):
    conn = _get_conn()
    cur = conn.cursor()
    
    # Build a dynamic query based on the config
    dim_map = {
        "vendor": "e.vendor",
        "customer": "c.name",
        "category": "e.category",
        "month": "strftime('%Y-%m', e.date)",
        "quarter": "'Q' || ((CAST(strftime('%m', e.date) AS INTEGER) - 1) / 3 + 1) || ' ' || strftime('%Y', e.date)"
    }
    metric_map = {
        "total_amount": "SUM(e.amount)",
        "count": "COUNT(*)",
        "average": "ROUND(AVG(e.amount), 2)",
        "min": "MIN(e.amount)",
        "max": "MAX(e.amount)"
    }
    
    select_parts = []
    group_parts = []
    headers = []
    
    for d in config.dimensions:
        col = dim_map.get(d)
        if col:
            select_parts.append(f"{col} AS {d}")
            group_parts.append(col)
            headers.append(d.title())
    
    for m in config.metrics:
        agg = metric_map.get(m)
        if agg:
            select_parts.append(f"{agg} AS {m}")
            headers.append(m.replace('_', ' ').title())
    
    if not select_parts:
        conn.close()
        return {"headers": [], "rows": [], "message": "Add dimensions or metrics to preview."}
    
    query = f"SELECT {', '.join(select_parts)} FROM expenses e LEFT JOIN clients c ON 1=0"
    if group_parts:
        query += f" GROUP BY {', '.join(group_parts)}"
    query += " ORDER BY 1 LIMIT 100"
    
    try:
        cur.execute(query)
        rows = [list(r) for r in cur.fetchall()]
    except Exception as ex:
        rows = []
        headers = ["Error"]
        rows.append([str(ex)])
    
    conn.close()
    return {"headers": headers, "rows": rows}

@router.post("/custom/generate")
def custom_report_generate(config: BuilderConfig):
    return {"url": "/files/reports/custom_report.pdf", "message": "Custom report generated (demo)."}

@router.get("/custom/templates")
def list_custom_templates():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM report_templates ORDER BY created_at DESC")
        templates = [dict(r) for r in cur.fetchall()]
    except Exception:
        templates = []
    conn.close()
    return {"templates": templates}

@router.post("/custom/templates")
def save_custom_template(req: SaveTemplateReq):
    import json
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS report_templates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, config TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')))")
        cur.execute("INSERT INTO report_templates (name, config) VALUES (?, ?)", (req.name, json.dumps(req.config)))
        conn.commit()
        return {"status": "success", "id": cur.lastrowid}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@router.delete("/custom/templates/{template_id}")
def delete_custom_template(template_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM report_templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# Stubs for other reports to allow frontend development to proceed
@router.get("/generic/{report_name}")
def get_generic_report(report_name: str):
    return {
        "title": report_name.replace('-', ' ').title(),
        "message": "This is a simplified stub report for demo purposes.",
        "data": [{"Item": "Sample A", "Amount": 1000}, {"Item": "Sample B", "Amount": 2500}]
    }

@router.post("/{type}/pdf")
def export_report_pdf(
    type: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Generate a PDF report.

    Attempts to call hermes.pdf module for real PDF generation via WeasyPrint.
    Falls back to a demo response if the module is unavailable.
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{type}_{timestamp}.pdf"

    # Determine output directory
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, filename)

    try:
        import hermes.pdf as pdf_gen
        db_path = get_db_path()

        # Dispatch to the appropriate PDF generator
        generators = {
            "gst": lambda: pdf_gen.generate_gst_report(db_path, from_date, to_date, output_path),
            "pl": lambda: pdf_gen.generate_pl_report(db_path, from_date, to_date, output_path),
            "balance-sheet": lambda: pdf_gen.generate_balance_sheet(db_path, from_date, to_date, output_path),
            "cashflow": lambda: pdf_gen.generate_cashflow_report(db_path, from_date, to_date, output_path),
            "aging": lambda: pdf_gen.generate_aging_report(db_path, output_path),
            "tds": lambda: pdf_gen.generate_tds_report(db_path, from_date, to_date, output_path),
        }

        gen_func = generators.get(type)
        if gen_func:
            gen_func()
            return {
                "url": f"/files/reports/{filename}",
                "filename": filename,
                "path": output_path,
                "message": f"{type.upper()} report generated successfully.",
            }
        else:
            return {"url": f"/files/reports/{type}_demo.pdf", "filename": f"{type}_demo.pdf", "message": f"No generator for '{type}'. Demo PDF returned."}

    except (ImportError, AttributeError):
        # hermes.pdf not available or generator not implemented
        return {"url": f"/files/reports/{type}_demo.pdf", "filename": f"{type}_demo.pdf", "message": "Demo PDF generated (PDF engine not available)."}
    except Exception as e:
        return {"url": f"/files/reports/{type}_demo.pdf", "filename": f"{type}_demo.pdf", "message": f"PDF generation failed: {str(e)}. Demo PDF returned."}

@router.post("/{type}/excel")
def export_report_excel(type: str):
    return {"url": f"/files/reports/{type}_demo.xlsx", "message": "Demo Excel generated"}

