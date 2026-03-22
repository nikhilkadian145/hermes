import os
import re
from pathlib import Path

SKILLS_DIR = Path(r"d:\HERMES\nanobot\skills")

REPLACEMENTS = {
    # DB Invoices
    r"db\.createInvoice": "DbCreateInvoiceTool",
    r"db\.getInvoiceByNumber": "DbGetInvoiceByNumberTool",
    r"db\.getInvoice\(": "DbGetInvoiceTool(",
    r"db\.listInvoices|db\.findUnpaidInvoice": "DbListInvoicesTool",
    r"db\.updateInvoiceStatus": "DbUpdateInvoiceStatusTool",
    r"db\.getOutstandingInvoices": "DbGetOutstandingTool",
    r"db\.getOverdueItems": "DbGetOverdueTool",
    r"db\.getUpcomingReminders": "DbGetDueSoonTool",
    
    # DB Clients
    r"db\.createClient": "DbCreateClientTool",
    r"db\.findClient": "DbFindClientTool",
    r"db\.updateClient": "DbUpdateClientTool",
    r"db\.getClient\(": "DbGetClientTool(",
    
    # DB Payments
    r"db\.recordPayment": "DbRecordPaymentTool",
    r"db\.getInvoicePaymentHistory": "DbGetPaymentsForInvoiceTool",
    
    # DB Expenses
    r"db\.logExpense": "DbLogExpenseTool",
    r"db\.getExpensesByPeriod": "DbListExpensesTool",
    
    # DB Reports
    r"db\.getRevenueByPeriod": "DbGetPlSummaryTool",
    r"db\.getInvoicesByPeriod": "DbGetGstReportTool",
    
    # PDF
    r"pdf\.generateInvoice": "PdfGenerateInvoiceTool",
    r"pdf\.generateReceipt": "PdfGenerateReceiptTool",
    r"pdf\.generateQuotation": "PdfGenerateQuotationTool",
    r"pdf\.generatePLReport": "PdfGeneratePlReportTool",
    r"pdf\.generateOutstandingReport": "PdfGenerateOutstandingReportTool",
    r"pdf\.generateExpenseReport": "PdfGenerateExpenseReportTool",
    r"pdf\.generateGSTReport": "PdfGenerateGstReportTool",
    
    # OCR / Whisper / Export
    r"ocr\.extractReceipt|ocr\.parseReceipt": "OcrExtractReceiptTool",
    r"whisper\.transcribe": "TranscribeAudioTool",
    r"db\.exportAllData": "ExportCaBundleTool",
    
    # Message Tool for telegram stuff
    r"telegram\.sendDocument|telegram\.sendMessage": "MessageTool",
}

def process_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    original = content
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        print(f"Updated {filepath.parent.name}/{filepath.name}")

if __name__ == "__main__":
    count = 0
    for root, _, files in os.walk(SKILLS_DIR):
        for file in files:
            if file == "SKILL.md":
                process_file(Path(root) / file)
                count += 1
    print(f"Processed {count} SKILL.md files.")
