import json
import inspect
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.resolve()))
import hermes.db as db

tools_info = [
    # Setup
    ("DbGetBusinessInfoTool", "get_business", "Get business details (GSTIN, Address, Bank, etc)."),
    ("DbUpdateBusinessInfoTool", "update_business", "Update business settings. Pass fields as kwargs."),
    # Clients
    ("DbCreateClientTool", "create_client", "Create a new client. Returns client_id."),
    ("DbGetClientTool", "get_client", "Get a specific client by ID."),
    ("DbFindClientTool", "find_client", "Fuzzy search clients by name or phone."),
    ("DbListClientsTool", "list_clients", "List all clients."),
    ("DbUpdateClientTool", "update_client", "Update a specific client's details."),
    # Invoices
    ("DbCreateInvoiceTool", "create_invoice", "Create an invoice with line items. Returns invoice_id."),
    ("DbGetInvoiceTool", "get_invoice", "Get invoice details by invoice_id."),
    ("DbGetInvoiceByNumberTool", "get_invoice_by_number", "Get invoice details by invoice number (e.g., INV-0001)."),
    ("DbListInvoicesTool", "list_invoices", "List invoices, optionally filtered by status or client_id."),
    ("DbUpdateInvoiceStatusTool", "update_invoice_status", "Update invoice status (draft, sent, paid, cancelled)."),
    ("DbGetOutstandingTool", "get_outstanding_balance", "Get total outstanding balance for a specific client (or all clients)."),
    ("DbGetOverdueTool", "get_overdue_invoices", "Get a list of all overdue invoices."),
    ("DbGetDueSoonTool", "get_due_soon_invoices", "Get a list of invoices due within the next N days."),
    # Payments
    ("DbRecordPaymentTool", "record_payment", "Record a payment against an invoice and auto-update its status."),
    ("DbGetPaymentsForInvoiceTool", "get_payments_for_invoice", "Get all recorded payments for an invoice."),
    # Expenses
    ("DbLogExpenseTool", "log_expense", "Log a new business expense."),
    ("DbGetExpenseTool", "get_expense", "Get expense details by ID."),
    ("DbListExpensesTool", "list_expenses", "List expenses, optionally filtered by category and date range."),
    # Quotations
    ("DbCreateQuotationTool", "create_quotation", "Create a quotation/estimate with line items."),
    ("DbGetQuotationTool", "get_quotation", "Get quotation details by ID."),
    ("DbConvertQuotationTool", "convert_quotation_to_invoice", "Convert an accepted quotation into an invoice."),
    ("DbUpdateQuotationStatusTool", "update_quotation_status", "Update quotation status (draft, sent, accepted, rejected)."),
    # Udhaar
    ("DbAddUdhaarTool", "add_udhaar", "Add an informal credit/udhaar record (given or received)."),
    ("DbSettleUdhaarTool", "settle_udhaar", "Mark an udhaar record as settled."),
    ("DbListUdhaarTool", "list_udhaar", "List udhaar records (optionally filter by settled status)."),
    ("DbGetUdhaarBalanceTool", "get_udhaar_balance", "Get net udhaar balance for a person (positive=they owe you, negative=you owe them)."),
    # Reports
    ("DbGetPlSummaryTool", "get_pl_summary", "Get Profit & Loss summary for a specific date range."),
    ("DbGetRevenueByMonthTool", "get_revenue_by_month", "Get monthly revenue aggregation for a specific year."),
    ("DbGetOutstandingReportTool", "get_outstanding_report", "Get detailed outstanding invoice report per client."),
    ("DbGetGstReportTool", "get_gst_report", "Get GST report details within a date range."),
    ("DbGetMtdSummaryTool", "get_mtd_summary", "Get Month-To-Date (MTD) financial summary for the morning briefing."),
    # Reminders
    ("DbLogReminderTool", "log_reminder", "Log that a payment reminder was sent."),
    ("DbGetRemindersForInvoiceTool", "get_reminders_for_invoice", "Get history of reminders sent for a specific invoice."),
]

def py_type_to_json_schema(py_type, default=inspect.Parameter.empty):
    if py_type == int:
        return {"type": "integer"}
    elif py_type == float:
        return {"type": "number"}
    elif py_type == bool:
        return {"type": "boolean"}
    elif py_type == str:
        return {"type": "string"}
    elif py_type == list or str(py_type).startswith("list"):
        return {"type": "array"}
    elif py_type == dict or str(py_type).startswith("dict"):
        return {"type": "object"}
    elif py_type == Any:
        return {}
    # if optional:
    if "None" in str(py_type):
        base = py_type_to_json_schema(py_type.__args__[0] if hasattr(py_type, "__args__") else str)
        return {"type": [base.get("type", "string"), "null"]}
    return {"type": "string"}

out = []
out.append('"""Generated HERMES tools for nanobot agent."""')
out.append('import json')
out.append('from pathlib import Path')
out.append('from typing import Any')
out.append('import hermes.db as db')
out.append('from nanobot.agent.tools.base import Tool\n')

for cls_name, func_name, desc in tools_info:
    func = getattr(db, func_name)
    sig = inspect.signature(func)
    
    props = {}
    required = []
    
    for pname, param in list(sig.parameters.items())[1:]: # skip db_path
        props[pname] = py_type_to_json_schema(param.annotation, param.default)
        if param.default == inspect.Parameter.empty:
            required.append(pname)
            
    schema = {
        "type": "object",
        "properties": props,
    }
    if required:
        schema["required"] = required

    out.append(f'class {cls_name}(Tool):')
    out.append(f'    def __init__(self, workspace: Path):')
    out.append(f'        self.workspace = workspace')
    out.append(f'        self.db_path = str(workspace / "hermes.db")\n')
    
    out.append(f'    @property')
    out.append(f'    def name(self) -> str:')
    out.append(f'        return "{cls_name}"\n')
    
    out.append(f'    @property')
    out.append(f'    def description(self) -> str:')
    out.append(f'        return "{desc}"\n')
    
    out.append(f'    @property')
    out.append(f'    def parameters(self) -> dict[str, Any]:')
    out.append(f'        return {json.dumps(schema, indent=12).strip()}')
    out.append(f'\n    async def execute(self, **kwargs: Any) -> Any:')
    out.append(f'        try:')
    out.append(f'            res = db.{func_name}(self.db_path, **kwargs)')
    out.append(f'            return json.dumps(res, default=str)')
    out.append(f'        except Exception as e:')
    out.append(f'            return f"Error: {{e}}"')
    out.append('\n')

Path("nanobot/agent/tools/hermes_tools.py").write_text("\n".join(out), encoding="utf-8")
print("Successfully generated hermes_tools.py")
