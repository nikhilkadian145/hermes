"""Generated HERMES tools for nanobot agent."""
import json
from pathlib import Path
from typing import Any
import hermes.db as db
from nanobot.agent.tools.base import Tool

class DbGetBusinessInfoTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetBusinessInfoTool"

    @property
    def description(self) -> str:
        return "Get business details (GSTIN, Address, Bank, etc)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_business(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbUpdateBusinessInfoTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbUpdateBusinessInfoTool"

    @property
    def description(self) -> str:
        return "Update business settings. Pass fields as kwargs."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "kwargs": {
                                    "type": "string"
                        }
            },
            "required": [
                        "kwargs"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.update_business(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbCreateClientTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbCreateClientTool"

    @property
    def description(self) -> str:
        return "Create a new client. Returns client_id."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "name": {
                                    "type": "string"
                        },
                        "phone": {
                                    "type": "string"
                        },
                        "email": {
                                    "type": "string"
                        },
                        "address": {
                                    "type": "string"
                        },
                        "gstin": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "name"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.create_client(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetClientTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetClientTool"

    @property
    def description(self) -> str:
        return "Get a specific client by ID."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "client_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "client_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_client(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbFindClientTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbFindClientTool"

    @property
    def description(self) -> str:
        return "Fuzzy search clients by name or phone."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "query": {
                                    "type": "string"
                        }
            },
            "required": [
                        "query"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.find_client(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbListClientsTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbListClientsTool"

    @property
    def description(self) -> str:
        return "List all clients."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.list_clients(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbUpdateClientTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbUpdateClientTool"

    @property
    def description(self) -> str:
        return "Update a specific client's details."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "client_id": {
                                    "type": "string"
                        },
                        "kwargs": {
                                    "type": "string"
                        }
            },
            "required": [
                        "client_id",
                        "kwargs"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.update_client(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbCreateInvoiceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbCreateInvoiceTool"

    @property
    def description(self) -> str:
        return "Create an invoice with line items. Returns invoice_id."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "client_id": {
                                    "type": "string"
                        },
                        "items": {
                                    "type": "array"
                        },
                        "due_date": {
                                    "type": "string"
                        },
                        "tax_rate": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "client_id",
                        "items",
                        "due_date"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.create_invoice(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetInvoiceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetInvoiceTool"

    @property
    def description(self) -> str:
        return "Get invoice details by invoice_id."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_invoice(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetInvoiceByNumberTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetInvoiceByNumberTool"

    @property
    def description(self) -> str:
        return "Get invoice details by invoice number (e.g., INV-0001)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_number": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_number"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_invoice_by_number(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbListInvoicesTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbListInvoicesTool"

    @property
    def description(self) -> str:
        return "List invoices, optionally filtered by status or client_id."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "status": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        },
                        "client_id": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        },
                        "limit": {
                                    "type": "string"
                        }
            }
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.list_invoices(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbUpdateInvoiceStatusTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbUpdateInvoiceStatusTool"

    @property
    def description(self) -> str:
        return "Update invoice status (draft, sent, paid, cancelled)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        },
                        "status": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id",
                        "status"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.update_invoice_status(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetOutstandingTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetOutstandingTool"

    @property
    def description(self) -> str:
        return "Get total outstanding balance for a specific client (or all clients)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "client_id": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        }
            }
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_outstanding_balance(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetOverdueTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetOverdueTool"

    @property
    def description(self) -> str:
        return "Get a list of all overdue invoices."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_overdue_invoices(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetDueSoonTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetDueSoonTool"

    @property
    def description(self) -> str:
        return "Get a list of invoices due within the next N days."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "days": {
                                    "type": "string"
                        }
            }
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_due_soon_invoices(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbRecordPaymentTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbRecordPaymentTool"

    @property
    def description(self) -> str:
        return "Record a payment against an invoice and auto-update its status."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        },
                        "amount": {
                                    "type": "string"
                        },
                        "payment_date": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        },
                        "mode": {
                                    "type": "string"
                        },
                        "reference": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id",
                        "amount"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.record_payment(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetPaymentsForInvoiceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetPaymentsForInvoiceTool"

    @property
    def description(self) -> str:
        return "Get all recorded payments for an invoice."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_payments_for_invoice(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbLogExpenseTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbLogExpenseTool"

    @property
    def description(self) -> str:
        return "Log a new business expense."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "date_str": {
                                    "type": "string"
                        },
                        "description": {
                                    "type": "string"
                        },
                        "category": {
                                    "type": "string"
                        },
                        "amount": {
                                    "type": "string"
                        },
                        "vendor": {
                                    "type": "string"
                        },
                        "receipt_path": {
                                    "type": "string"
                        },
                        "ocr_raw": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "date_str",
                        "description",
                        "category",
                        "amount"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.log_expense(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetExpenseTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetExpenseTool"

    @property
    def description(self) -> str:
        return "Get expense details by ID."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "expense_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "expense_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_expense(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbListExpensesTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbListExpensesTool"

    @property
    def description(self) -> str:
        return "List expenses, optionally filtered by category and date range."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "category": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        },
                        "from_date": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        },
                        "to_date": {
                                    "type": [
                                                "string",
                                                "null"
                                    ]
                        }
            }
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.list_expenses(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbCreateQuotationTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbCreateQuotationTool"

    @property
    def description(self) -> str:
        return "Create a quotation/estimate with line items."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "client_id": {
                                    "type": "string"
                        },
                        "items": {
                                    "type": "array"
                        },
                        "valid_until": {
                                    "type": "string"
                        },
                        "tax_rate": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "client_id",
                        "items",
                        "valid_until"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.create_quotation(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetQuotationTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetQuotationTool"

    @property
    def description(self) -> str:
        return "Get quotation details by ID."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "quotation_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "quotation_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_quotation(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbConvertQuotationTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbConvertQuotationTool"

    @property
    def description(self) -> str:
        return "Convert an accepted quotation into an invoice."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "quotation_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "quotation_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.convert_quotation_to_invoice(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbUpdateQuotationStatusTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbUpdateQuotationStatusTool"

    @property
    def description(self) -> str:
        return "Update quotation status (draft, sent, accepted, rejected)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "quotation_id": {
                                    "type": "string"
                        },
                        "status": {
                                    "type": "string"
                        }
            },
            "required": [
                        "quotation_id",
                        "status"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.update_quotation_status(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbAddUdhaarTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbAddUdhaarTool"

    @property
    def description(self) -> str:
        return "Add an informal credit/udhaar record (given or received)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "person_name": {
                                    "type": "string"
                        },
                        "phone": {
                                    "type": "string"
                        },
                        "amount": {
                                    "type": "string"
                        },
                        "direction": {
                                    "type": "string"
                        },
                        "notes": {
                                    "type": "string"
                        }
            },
            "required": [
                        "person_name"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.add_udhaar(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbSettleUdhaarTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbSettleUdhaarTool"

    @property
    def description(self) -> str:
        return "Mark an udhaar record as settled."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "udhaar_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "udhaar_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.settle_udhaar(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbListUdhaarTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbListUdhaarTool"

    @property
    def description(self) -> str:
        return "List udhaar records (optionally filter by settled status)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "settled": {
                                    "type": "string"
                        }
            }
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.list_udhaar(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetUdhaarBalanceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetUdhaarBalanceTool"

    @property
    def description(self) -> str:
        return "Get net udhaar balance for a person (positive=they owe you, negative=you owe them)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "person_name": {
                                    "type": "string"
                        }
            },
            "required": [
                        "person_name"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_udhaar_balance(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetPlSummaryTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetPlSummaryTool"

    @property
    def description(self) -> str:
        return "Get Profit & Loss summary for a specific date range."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "from_date": {
                                    "type": "string"
                        },
                        "to_date": {
                                    "type": "string"
                        }
            },
            "required": [
                        "from_date",
                        "to_date"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_pl_summary(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetRevenueByMonthTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetRevenueByMonthTool"

    @property
    def description(self) -> str:
        return "Get monthly revenue aggregation for a specific year."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "year": {
                                    "type": "string"
                        }
            },
            "required": [
                        "year"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_revenue_by_month(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetOutstandingReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetOutstandingReportTool"

    @property
    def description(self) -> str:
        return "Get detailed outstanding invoice report per client."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_outstanding_report(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetGstReportTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetGstReportTool"

    @property
    def description(self) -> str:
        return "Get GST report details within a date range."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "from_date": {
                                    "type": "string"
                        },
                        "to_date": {
                                    "type": "string"
                        }
            },
            "required": [
                        "from_date",
                        "to_date"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_gst_report(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetMtdSummaryTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetMtdSummaryTool"

    @property
    def description(self) -> str:
        return "Get Month-To-Date (MTD) financial summary for the morning briefing."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_mtd_summary(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbLogReminderTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbLogReminderTool"

    @property
    def description(self) -> str:
        return "Log that a payment reminder was sent."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        },
                        "client_id": {
                                    "type": "string"
                        },
                        "message_text": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id",
                        "client_id",
                        "message_text"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.log_reminder(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"


class DbGetRemindersForInvoiceTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "DbGetRemindersForInvoiceTool"

    @property
    def description(self) -> str:
        return "Get history of reminders sent for a specific invoice."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                        "invoice_id": {
                                    "type": "string"
                        }
            },
            "required": [
                        "invoice_id"
            ]
}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            res = db.get_reminders_for_invoice(self.db_path, **kwargs)
            return json.dumps(res, default=str)
        except Exception as e:
            return f"Error: {e}"

