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


# ===========================================================================
# GST & TAX TOOLS
# ===========================================================================

class GstLookupTool(Tool):
    """Look up the correct GST rate and HSN/SAC code for any product or service."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "gst_lookup"

    @property
    def description(self) -> str:
        return (
            "Look up the correct GST rate and HSN/SAC code for any product or service. "
            "ALWAYS call this for every line item before creating an invoice or recording an expense. "
            "Never guess or assume a GST rate. This tool checks the business's item cache first "
            "(instant for known items), then searches the official HSN/SAC master table."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "item_description": {
                    "type": "string",
                    "description": "The product or service description as stated by the user."
                }
            },
            "required": ["item_description"]
        }

    async def execute(self, item_description: str = "", **kwargs: Any) -> Any:
        try:
            # Layer 1: business cache
            cached = db.get_cached_item_gst(self.db_path, item_description)
            if cached:
                return json.dumps({
                    "hsn_code": cached["hsn_code"],
                    "gst_rate": cached["gst_rate"],
                    "source": "cache",
                    "confidence": "high",
                    "message": f"HSN {cached['hsn_code']}, GST {cached['gst_rate']}% (previously confirmed)"
                })

            # Layer 2: FTS search
            results = db.search_hsn(self.db_path, item_description, limit=5)

            if not results:
                business = db.get_business(self.db_path)
                default = business.get("default_gst_rate", 18.0) if business else 18.0
                return json.dumps({
                    "hsn_code": None,
                    "gst_rate": default,
                    "source": "default",
                    "confidence": "low",
                    "message": (
                        f"No HSN match found for '{item_description}'. "
                        f"Using business default {default}%. "
                        f"Please ask the user to confirm the correct rate."
                    )
                })

            top = results[0]
            if len(results) == 1:
                db.save_item_gst_cache(
                    self.db_path, item_description,
                    top['code'], top['gst_rate'], 'agent'
                )
                return json.dumps({
                    "hsn_code": top['code'],
                    "gst_rate": top['gst_rate'],
                    "source": "hsn_lookup",
                    "confidence": "medium",
                    "matched_description": top['description'],
                    "message": f"HSN {top['code']} — {top['description']} — {top['gst_rate']}% GST"
                })

            # Multiple candidates
            return json.dumps({
                "hsn_code": None,
                "gst_rate": None,
                "source": "hsn_lookup",
                "confidence": "low",
                "candidates": [
                    {"code": r['code'], "description": r['description'], "gst_rate": r['gst_rate']}
                    for r in results[:3]
                ],
                "message": (
                    f"Multiple HSN matches for '{item_description}'. "
                    f"Present these options to the user and ask them to pick one."
                )
            })
        except Exception as e:
            return f"Error: {e}"


class ConfirmItemGstTool(Tool):
    """Save a confirmed HSN code and GST rate for an item."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "confirm_item_gst"

    @property
    def description(self) -> str:
        return (
            "Save a confirmed HSN code and GST rate for an item. "
            "Call this after the user picks the correct rate from candidates returned by gst_lookup. "
            "This saves the mapping permanently so the user is never asked again for this item."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "item_description": {"type": "string"},
                "hsn_code": {"type": "string"},
                "gst_rate": {"type": "number"}
            },
            "required": ["item_description", "hsn_code", "gst_rate"]
        }

    async def execute(self, item_description: str = "", hsn_code: str = "",
                      gst_rate: float = 0, **kwargs: Any) -> Any:
        try:
            db.save_item_gst_cache(self.db_path, item_description, hsn_code, gst_rate, 'user')
            return json.dumps({"success": True, "message": f"Saved: {item_description} → HSN {hsn_code}, {gst_rate}% GST"})
        except Exception as e:
            return f"Error: {e}"


class CalculateInvoiceTaxTool(Tool):
    """Calculate CGST, SGST, IGST, and totals for an invoice."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "calculate_invoice_tax"

    @property
    def description(self) -> str:
        return (
            "Calculate CGST, SGST, IGST, and totals for an invoice based on line items, "
            "supply type (intrastate/interstate), and per-item GST rates. "
            "Call this after all line items have confirmed HSN codes, before creating the invoice."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Line items with description, quantity, unit_price, hsn_code, gst_rate",
                    "items": {"type": "object"}
                },
                "client_id": {"type": "integer"},
            },
            "required": ["items", "client_id"]
        }

    async def execute(self, items: list | None = None, client_id: int = 0,
                      **kwargs: Any) -> Any:
        try:
            from hermes.gst import determine_supply_type, calculate_item_tax, calculate_invoice_totals
            items = items or []
            business = db.get_business(self.db_path)
            client = db.get_client(self.db_path, client_id)

            supply_type = determine_supply_type(
                (business or {}).get('state_code', ''),
                (client or {}).get('state_code', ''),
                (client or {}).get('gstin')
            )

            enriched_items = []
            for item in items:
                tax = calculate_item_tax(
                    item['unit_price'], item['quantity'],
                    item['gst_rate'], supply_type
                )
                enriched_items.append({**item, **tax})

            totals = calculate_invoice_totals(enriched_items)
            return json.dumps({
                "supply_type": supply_type,
                "items": enriched_items,
                "totals": totals,
                "summary": (
                    f"Taxable: ₹{totals['subtotal']:,.0f} | "
                    f"{'CGST+SGST' if supply_type == 'intrastate' else 'IGST'}: "
                    f"₹{totals['total_tax']:,.0f} | "
                    f"Total: ₹{totals['grand_total']:,.0f}"
                )
            })
        except Exception as e:
            return f"Error: {e}"


class GetGstLiabilityTool(Tool):
    """Get the net GST payable for a period — output tax minus ITC."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "get_gst_liability"

    @property
    def description(self) -> str:
        return "Get the net GST payable for a period — output tax minus input tax credit (ITC). Use for GST-3B filing queries."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "from_date": {"type": "string", "description": "YYYY-MM-DD"},
                "to_date":   {"type": "string", "description": "YYYY-MM-DD"}
            },
            "required": ["from_date", "to_date"]
        }

    async def execute(self, from_date: str = "", to_date: str = "", **kwargs: Any) -> Any:
        try:
            liability = db.get_gst_liability(self.db_path, from_date, to_date)
            return json.dumps(liability)
        except Exception as e:
            return f"Error: {e}"


class GetHsnSummaryTool(Tool):
    """Get HSN/SAC-wise summary of supplies for a period."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "get_hsn_summary"

    @property
    def description(self) -> str:
        return "Get HSN/SAC-wise summary of supplies for a period. Required for GSTR-1 filing."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "from_date": {"type": "string"},
                "to_date":   {"type": "string"}
            },
            "required": ["from_date", "to_date"]
        }

    async def execute(self, from_date: str = "", to_date: str = "", **kwargs: Any) -> Any:
        try:
            result = db.get_hsn_summary(self.db_path, from_date, to_date)
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error: {e}"


class RunAnomalyDetectionTool(Tool):
    """Scan all transactions for anomalies."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "run_anomaly_detection"

    @property
    def description(self) -> str:
        return (
            "Scan all transactions for anomalies: duplicate bills, price drift, "
            "round-number billing. Writes results to the anomalies table. "
            "Called by the nightly cron job automatically."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            count = db.run_anomaly_detection(self.db_path)
            return json.dumps({"new_anomalies": count, "message": f"Detection complete. {count} new anomalies found."})
        except Exception as e:
            return f"Error: {e}"





class WebChatPollTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "web_chat_poll"

    @property
    def description(self) -> str:
        return (
            "Check if a user has sent a message via the HERMES web dashboard chat. "
            "This tool is called automatically by the system — not by the user. "
            "Returns the pending message if one exists."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    async def execute(self, **kwargs) -> Any:
        try:
            msg = db.get_pending_web_chat_message(self.db_path)
            if not msg:
                return json.dumps({"has_message": False})
            db.mark_web_chat_message_processing(self.db_path, msg["id"])
            return json.dumps({
                "has_message": True,
                "message_id": msg["id"],
                "conversation_id": msg["conversation_id"],
                "content": msg["content"],
                "metadata": msg["metadata"]
            })
        except Exception as e:
            return f"Error: {e}"


class WebChatRespondTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "web_chat_respond"

    @property
    def description(self) -> str:
        return (
            "Send your response to the user on the web dashboard chat. "
            "Call this after processing a web chat message — "
            "pass the message_id from web_chat_poll and your response content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message_id":      {"type": "integer", "description": "The id returned by web_chat_poll"},
                "conversation_id": {"type": "string"},
                "content":         {"type": "string", "description": "Your response text"},
                "metadata":        {"type": "string", "description": "Optional JSON: linked invoice_id, bill_id, etc."}
            },
            "required": ["message_id", "conversation_id", "content"]
        }

    async def execute(self, message_id: int, conversation_id: str,
                content: str, metadata: str = None, **kwargs) -> Any:
        try:
            db.mark_web_chat_message_done(self.db_path, message_id)
            db.write_web_chat_assistant_message(self.db_path, conversation_id, content, metadata)
            return json.dumps({"success": True})
        except Exception as e:
            return f"Error: {e}"



class NotifyOverdueInvoicesTool(Tool):
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.db_path = str(workspace / "hermes.db")

    @property
    def name(self) -> str:
        return "notify_overdue_invoices"

    @property
    def description(self) -> str:
        return (
            "Scan for invoices that became overdue today. "
            "Write a notification for each one. Update their status to overdue. "
            "Called by the nightly 7:30 AM cron — not by users directly."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **kwargs: Any) -> Any:
        try:
            count = db.notify_overdue_invoices(self.db_path)
            return json.dumps({
                "newly_overdue": count,
                "message": f"{count} invoices marked overdue and notifications sent."
            })
        except Exception as e:
            return f"Error: {e}"
