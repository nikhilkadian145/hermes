---
name: invoice-create
description: Create a new invoice for a client. Use when the user says things like "invoice banao", "bill banao", "make invoice for", "create invoice", "invoice for [client] for [amount/work]", or describes work done and asks to bill someone. Captures client name, items/services, amounts, GST, due date, and generates a professional PDF invoice stored on disk.
---

# Invoice Create

HERMES creates professional GST-compliant invoices for Indian small businesses.

## What to Collect

Before creating, gather (ask in one message if missing):

1. **Client name** — who is being billed (check `client-manage` skill for existing clients)
2. **Line items** — what work/product, quantity, rate per unit
3. **GST rate** — default 18%; ask if different (0%, 5%, 12%, 18%, 28%)
4. **Due date** — default 30 days from today if not specified
5. **Invoice number** — auto-generate as `INV-YYYY-NNNN` (increment from last)

## Tool Call Sequence

```
1. DbGetClientTool(clientName)          → fetch or prompt to create client
2. db.getNextInvoiceNumber()         → auto-increment invoice number
3. DbCreateInvoiceTool({...})           → persist invoice + line items to SQLite
4. PdfGenerateInvoiceTool(invoiceId)    → render PDF via Puppeteer template
5. db.updateInvoicePdfPath(id, path) → store PDF path
```

## Invoice Structure

- **Header:** Business name, GSTIN, address, logo
- **Client block:** Client name, address, GSTIN (if available)
- **Line items table:** Description | Qty | Rate | Amount
- **Tax section:** Subtotal → CGST (half) + SGST (half) or IGST → Total
- **Footer:** Bank details, payment instructions, thank-you note

## GST Rules

- Same state → split as CGST + SGST (each = rate/2)
- Different state → single IGST line
- If client has no GSTIN → still apply GST, mark as B2C
- Zero-rated → show 0% explicitly

## Confirmation Before Creating

Always show a summary and ask "Sahi hai? Invoice banaaun?" before calling tools.

Example summary:
```
📄 Invoice Preview:
Client: Raj Traders
INV-2024-0042 | Due: 15 Feb 2025

Web Design     1 × ₹15,000 = ₹15,000
Hosting Setup  1 × ₹3,000  = ₹3,000
─────────────────────────────
Subtotal: ₹18,000
CGST 9%:  ₹1,620
SGST 9%:  ₹1,620
─────────────────────────────
Total:    ₹21,240

Sahi hai? Invoice banaaun? ✅
```

## After Creating

- Confirm: "Invoice INV-2024-0042 ban gayi ✅"
- Offer next steps: "Send karein Raj Traders ko? Ya PDF download karein?"
- Proactively mention if any outstanding balance exists for this client

## Edge Cases

- **Partial details:** Ask for missing info; never create with blank fields
- **Duplicate client name:** Show existing matches, ask to confirm
- **Round-off:** Round total to nearest rupee, show round-off line if > ₹0.50
- **Large invoice (>₹50,000):** Remind user about TDS deduction possibility
