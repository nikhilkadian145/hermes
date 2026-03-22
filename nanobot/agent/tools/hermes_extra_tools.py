import os
import json
from pathlib import Path
from typing import Any
from nanobot.agent.tools.base import Tool

import hermes.db as db
from hermes.pdf import (
    generate_invoice_pdf,
    generate_receipt_pdf,
    generate_quotation_pdf,
    generate_pl_report_pdf,
    generate_outstanding_report_pdf,
    generate_expense_report_pdf,
    generate_gst_report_pdf
)
from hermes.ocr import extract_receipt
from hermes.whisper_tool import transcribe
from hermes.export import create_ca_bundle

def _get_outpath(workspace: Path, subfolder: str, filename: str) -> str:
    path = workspace / subfolder
    path.mkdir(parents=True, exist_ok=True)
    return str(path / filename)

class PdfGenerateInvoiceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateInvoiceTool"
    @property
    def description(self) -> str: return "Generates a PDF for a given invoice_num (e.g., INV-0001). Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"invoice_num": {"type": "string"}}, "required": ["invoice_num"]}
    async def execute(self, invoice_num: str) -> Any:
        try:
            invoice = db.get_invoice_by_number(self.db_path, invoice_num)
            if not invoice: return f"Error: Invoice {invoice_num} not found."
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "invoices", f"{invoice_num}.pdf")
            generate_invoice_pdf(invoice, business, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGenerateReceiptTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateReceiptTool"
    @property
    def description(self) -> str: return "Generates a payment receipt PDF for a given payment_id. Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"payment_id": {"type": "string"}}, "required": ["payment_id"]}
    async def execute(self, payment_id: str) -> Any:
        try:
            # We need the payment and its associated invoice.
            # get_payments_for_invoice requires an invoice_id. But what if we just query the payment?
            # Custom query to get payment details
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM payments WHERE id=?", (payment_id,))
                payment = cur.fetchone()
                if not payment: return f"Error: Payment {payment_id} not found."
                payment = dict(payment)
                
            invoice = db.get_invoice(self.db_path, payment["invoice_id"])
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "receipts", f"RCPT-{payment_id}.pdf")
            generate_receipt_pdf(payment, invoice, business, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGenerateQuotationTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateQuotationTool"
    @property
    def description(self) -> str: return "Generates a Quotation PDF for a quotation_id. Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"quotation_id": {"type": "string"}}, "required": ["quotation_id"]}
    async def execute(self, quotation_id: str) -> Any:
        try:
            qt = db.get_quotation(self.db_path, quotation_id)
            if not qt: return f"Error: Quotation not found."
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "quotations", f"{qt['quotation_number']}.pdf")
            generate_quotation_pdf(qt, business, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGeneratePlReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGeneratePlReportTool"
    @property
    def description(self) -> str: return "Generates Profit & Loss PDF for date range YYYY-MM-DD. Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"from_date": {"type": "string"}, "to_date": {"type": "string"}}, "required": ["from_date", "to_date"]}
    async def execute(self, from_date: str, to_date: str) -> Any:
        try:
            data = db.get_pl_summary(self.db_path, from_date, to_date)
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "reports", f"PL_{from_date}_{to_date}.pdf")
            generate_pl_report_pdf(data, business, from_date, to_date, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGenerateOutstandingReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateOutstandingReportTool"
    @property
    def description(self) -> str: return "Generates Outstanding Balances PDF. Returns path."
    @property
    def parameters(self) -> dict[str, Any]: return {"type": "object", "properties": {}}
    async def execute(self) -> Any:
        try:
            data = db.get_outstanding_report(self.db_path)
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "reports", "Outstanding_Report.pdf")
            generate_outstanding_report_pdf(data, business, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGenerateExpenseReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateExpenseReportTool"
    @property
    def description(self) -> str: return "Generates Expense Report PDF for date range YYYY-MM-DD. Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"from_date": {"type": "string"}, "to_date": {"type": "string"}}, "required": ["from_date", "to_date"]}
    async def execute(self, from_date: str, to_date: str) -> Any:
        try:
            expenses = db.list_expenses(self.db_path, from_date=from_date, to_date=to_date)
            totals = {}
            for e in expenses:
                totals[e["category"]] = totals.get(e["category"], 0.0) + e["amount"]
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "reports", f"Expenses_{from_date}_{to_date}.pdf")
            generate_expense_report_pdf(expenses, totals, business, from_date, to_date, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class PdfGenerateGstReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "PdfGenerateGstReportTool"
    @property
    def description(self) -> str: return "Generates GST Report PDF for date range YYYY-MM-DD. Returns path."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"from_date": {"type": "string"}, "to_date": {"type": "string"}}, "required": ["from_date", "to_date"]}
    async def execute(self, from_date: str, to_date: str) -> Any:
        try:
            data = db.get_gst_report(self.db_path, from_date, to_date)
            business = db.get_business(self.db_path)
            out = _get_outpath(self.workspace, "reports", f"GST_{from_date}_{to_date}.pdf")
            generate_gst_report_pdf(data, business, from_date, to_date, out)
            return out
        except Exception as e:
            return f"Error: {e}"

class OcrExtractReceiptTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
    @property
    def name(self) -> str: return "OcrExtractReceiptTool"
    @property
    def description(self) -> str: return "Extract structured data from a receipt image. Returns JSON string."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"image_path": {"type": "string"}}, "required": ["image_path"]}
    async def execute(self, image_path: str) -> Any:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key: return "Error: OPENROUTER_API_KEY environment variable not set."
        res = extract_receipt(image_path, api_key)
        return json.dumps(res, default=str)

class TranscribeAudioTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
    @property
    def name(self) -> str: return "TranscribeAudioTool"
    @property
    def description(self) -> str: return "Transcribes voice messages to text. Returns transcription."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"audio_path": {"type": "string"}}, "required": ["audio_path"]}
    async def execute(self, audio_path: str) -> Any:
        res = transcribe(audio_path)
        return json.dumps(res, default=str)

class ExportCaBundleTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")
    @property
    def name(self) -> str: return "ExportCaBundleTool"
    @property
    def description(self) -> str: return "Generates a CA bundle ZIP with reports and data. Returns path to ZIP."
    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {"from_date": {"type": "string"}, "to_date": {"type": "string"}}, "required": ["from_date", "to_date"]}
    async def execute(self, from_date: str, to_date: str) -> Any:
        out = _get_outpath(self.workspace, "exports", f"CA_Bundle_{from_date}_{to_date}.zip")
        res = create_ca_bundle(self.db_path, str(self.workspace), from_date, to_date, out)
        if res["success"]:
            return res["output_path"]
        return f"Error: {res['error']}"
