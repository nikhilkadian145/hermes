---
name: report-ca-export
description: Export all financial data in a CA-ready package for the accountant. Use when the user says "CA ko data do", "accountant ke liye export karo", "CA export banao", "year end data chahiye CA ko", "accounts export", or needs to share business data with their chartered accountant or bookkeeper.
---

# Report — CA Export

Package all financial data into a clean, CA-ready export bundle.

## What Gets Exported

A single zip file containing:

| File | Contents |
|---|---|
| `invoices.xlsx` | All invoices with client, amount, GST, status, date |
| `payments.xlsx` | All payments received with invoice linkage |
| `expenses.xlsx` | All expenses with category, vendor, GST details |
| `outstanding.xlsx` | Unpaid/partial invoices as of export date |
| `gst_summary.xlsx` | Output tax + ITC summary by month |
| `ledger.xlsx` | Complete debit/credit ledger |
| `receipts/` | Folder with all scanned receipt images |
| `invoices_pdf/` | Folder with all generated invoice PDFs |
| `README.txt` | Explains each file for the CA |

## Tool Call Sequence

```
1. Determine period (FY by default, or user-specified)
2. ExportCaBundleTool({from, to})           → structured data objects
3. excel.generateWorkbooks(data)          → create all .xlsx files
4. files.copyReceipts(period)             → gather receipt images
5. files.copyInvoicePDFs(period)          → gather invoice PDFs
6. files.createZip(exportDir)             → bundle everything
7. MessageTool(chatId, zipPath, caption)
```

## Period Selection

```
"CA export banao" → ask:
  Which period?
  1. Current Financial Year (Apr 2024 – Mar 2025)
  2. Last Financial Year (Apr 2023 – Mar 2024)
  3. Current Quarter
  4. Custom range
```

## Excel File Structure

**invoices.xlsx columns:**
Invoice No | Date | Due Date | Client Name | Client GSTIN | HSN/SAC | Taxable Amount | CGST | SGST | IGST | Total | Status | Payment Date

**expenses.xlsx columns:**
Date | Vendor | Category | Description | Amount | GST Paid | GST Amount | Vendor GSTIN | Bill No | Payment Mode | ITC Eligible

**ledger.xlsx columns:**
Date | Type (Dr/Cr) | Account Head | Description | Amount | Balance | Reference

## Confirmation Before Export

```
📤 CA Export Ready

Period: FY 2024-25 (Apr 2024 – 15 Jan 2025)

Included:
✅ 127 invoices (₹18,40,000 total)
✅ 89 payments recorded
✅ 234 expenses (₹6,82,400 total)
✅ 43 receipt images
✅ All invoice PDFs

Zip file size: ~24 MB

Export karoon? CA ko bhejein?
```

## README.txt Template

```
HERMES Financial Export
Business: [Name] | GSTIN: [GSTIN]
Period: FY 2024-25 | Exported: 15 Jan 2025

FILES:
- invoices.xlsx: All sales invoices
- payments.xlsx: Payments received
- expenses.xlsx: Business expenses (ITC column marks GST-eligible)
- outstanding.xlsx: Unpaid invoices as of export date
- gst_summary.xlsx: Month-wise GST output + input credit
- ledger.xlsx: Full double-entry ledger
- receipts/: Scanned expense bills
- invoices_pdf/: Generated invoice PDFs

Notes:
- All amounts in INR
- GST figures for reference only — verify with portal data
- ITC column = 'Yes' means bill received with GSTIN
```

## After Export

"✅ CA export ready! Zip file aapke Telegram pe bhej di.
CA ko WhatsApp karo ya email pe forward karo."

Also offer: "Next export ke liye reminder set karein? (quarterly / yearly)"
