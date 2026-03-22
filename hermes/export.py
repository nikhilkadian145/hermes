import os
import sqlite3
import csv
import zipfile
import tempfile
from pathlib import Path
from hermes.db import get_pl_summary, get_gst_report, get_outstanding_report, get_business, list_invoices, list_expenses
from hermes.pdf import generate_pl_report_pdf, generate_gst_report_pdf, generate_outstanding_report_pdf

def export_table_to_csv(db_path: str, table: str, from_date: str, to_date: str, output_csv_path: str):
    """Exports a specified table to a CSV file for a given date range."""
    # Mapping table names to their respective date columns for filtering
    date_columns = {
        "invoices": "issue_date",
        "payments": "payment_date",
        "expenses": "date",
        "quotations": "issue_date"
    }
    
    date_col = date_columns.get(table)
    if not date_col:
        # Fallback to exporting everything if not a dated table
        query = f"SELECT * FROM {table}"
        params = []
    else:
        query = f"SELECT * FROM {table} WHERE {date_col} >= ? AND {date_col} <= ?"
        params = [from_date, to_date]
        
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            if rows:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(rows[0].keys())
                # Write rows
                for row in rows:
                    writer.writerow(tuple(row))

def create_ca_bundle(db_path: str, customer_data_dir: str, from_date: str, to_date: str, output_path: str) -> dict:
    """
    Generates a quarterly financial ZIP bundle for a CA.
    Returns: {"success": True/False, "output_path": path_to_zip, "error": msg}
    """
    if not os.path.exists(db_path):
        return {"success": False, "error": f"Database not found: {db_path}", "output_path": None}
        
    customer_dir = Path(customer_data_dir)
    invoices_dir = customer_dir / "invoices"
    receipts_dir = customer_dir / "expenses" / "receipts"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        
        # 1. Fetch Business Data & Generate Summaries
        business = get_business(db_path)
        
        pl_data = get_pl_summary(db_path, from_date, to_date)
        gst_data = get_gst_report(db_path, from_date, to_date)
        outstanding_data = get_outstanding_report(db_path)
        
        pl_path = str(tmp / "pl_report.pdf")
        gst_path = str(tmp / "gst_report.pdf")
        out_path = str(tmp / "outstanding_report.pdf")
        
        generate_pl_report_pdf(pl_data, business, from_date, to_date, pl_path)
        generate_gst_report_pdf(gst_data, business, from_date, to_date, gst_path)
        generate_outstanding_report_pdf(outstanding_data, business, out_path)
        
        # 2. Export CSV Data
        inv_csv = str(tmp / "invoices.csv")
        pay_csv = str(tmp / "payments.csv")
        exp_csv = str(tmp / "expenses.csv")
        
        export_table_to_csv(db_path, "invoices", from_date, to_date, inv_csv)
        export_table_to_csv(db_path, "payments", from_date, to_date, pay_csv)
        export_table_to_csv(db_path, "expenses", from_date, to_date, exp_csv)
        
        # 3. Create README.txt
        readme_text = f"""HERMES CA EXPORT BUNDLE
========================
Client: {business.get('name', 'Unknown Business')}
Period: {from_date} to {to_date}

Folder Structure:
- summary/: Contains auto-generated P&L, GST, and Outstanding PDF reports.
- data/: Contains raw CSV exports of the ledgers for Excel processing.
- invoices/: Contains copies of the actual PDF invoices generated during the period.
- expenses/: Contains the receipt photos attached to logged expenses.

End of Report.
"""
        readme_path = tmp / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_text)
            
        # 4. Filter Invoices & Expenses for this period
        period_invoices = list_invoices(db_path) # Assume list_invoices returns all; we'll filter below
        period_invoices = [i for i in period_invoices if from_date <= i["issue_date"] <= to_date]
        
        period_expenses = list_expenses(db_path, from_date, to_date)
        
        # 5. Build ZIP
        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add Summaries
                zf.write(pl_path, "summary/pl_report.pdf")
                zf.write(gst_path, "summary/gst_report.pdf")
                zf.write(out_path, "summary/outstanding.pdf")
                
                # Add Data
                if os.path.exists(inv_csv): zf.write(inv_csv, "data/invoices.csv")
                if os.path.exists(pay_csv): zf.write(pay_csv, "data/payments.csv")
                if os.path.exists(exp_csv): zf.write(exp_csv, "data/expenses.csv")
                
                # Add README
                zf.write(readme_path, "README.txt")
                
                # Add Invoice PDFs 
                for inv in period_invoices:
                    inv_num = inv["invoice_number"]
                    # Assuming invoice PDFs are named exactly like INV-001.pdf
                    possible_pdf = invoices_dir / f"{inv_num}.pdf"
                    if possible_pdf.exists():
                        zf.write(str(possible_pdf), f"invoices/{inv_num}.pdf")
                        
                # Add Expense Receipts
                for exp in period_expenses:
                    receipt_path = exp.get("receipt_path")
                    if receipt_path and os.path.exists(receipt_path):
                        fname = os.path.basename(receipt_path)
                        zf.write(receipt_path, f"expenses/receipts/{fname}")
                        
            return {"success": True, "output_path": output_path, "error": None}
            
        except Exception as e:
            return {"success": False, "output_path": None, "error": f"Failed to compress ZIP: {str(e)}"}
