---
name: invoice-create
description: Create a new invoice for a client. Use when the user says things like "invoice banao", "bill banao", "make invoice for", "create invoice", "invoice for [client] for [amount/work]", or describes work done and asks to bill someone. Captures client name, items/services, amounts, GST with per-item HSN lookup, due date, and generates a professional PDF invoice stored on disk.
---

# Invoice Create

HERMES creates professional GST-compliant invoices for Indian small businesses with proper HSN codes and tax breakdowns.

## What to Collect

Before creating, gather (ask in one message if missing):

1. **Client name** — who is being billed (check `client-manage` skill for existing clients)
2. **Line items** — what work/product, quantity, rate per unit
3. **Due date** — default 30 days from today if not specified

> **GST rate is NEVER guessed.** Always use the `gst_lookup` tool for every line item.

## GST Lookup Workflow (Mandatory for EVERY Item)

```
For each line item:
1. gst_lookup(item_description)
   → If source = "cache" → use the cached HSN + rate (instant, no ask)
   → If source = "hsn_lookup" + confidence = "medium" → use it, no ask
   → If source = "hsn_lookup" + candidates → show options to user, ask to pick
   → If source = "default" → ask user to confirm the rate

2. If user picked or confirmed:
   confirm_item_gst(item_description, hsn_code, gst_rate)
   → Permanently saves mapping to cache

3. After ALL items have confirmed HSN:
   calculate_invoice_tax(items, client_id)
   → Returns supply_type, per-item CGST/SGST/IGST, totals, amount_in_words
```

## Confirmation Before Creating

Always show a summary and ask "Sahi hai? Invoice banaaun?" before calling tools.

Example summary:
```
📄 Invoice Preview:
Client: Raj Traders (GSTIN: 27AABCT1234H1ZS)
Supply Type: Intrastate (Maharashtra → Maharashtra)
Due: 15 Feb 2025

 Item              HSN   Qty   Rate    Taxable  CGST 9%  SGST 9%  Total
 Web Design        9983   1   ₹15,000  ₹15,000  ₹1,350   ₹1,350  ₹17,700
 Hosting Setup     9984   1   ₹3,000   ₹3,000    ₹270     ₹270   ₹3,540
 ─────────────────────────────────────────────────────────────────
 Subtotal: ₹18,000 | CGST: ₹1,620 | SGST: ₹1,620
 Total:    ₹21,240
 (Rupees Twenty One Thousand Two Hundred Forty Only)

Sahi hai? Invoice banaaun? ✅
```

## Tool Call Sequence

```
1. DbFindClientTool / DbGetClientTool    → fetch or prompt to create client
2. gst_lookup(item1), gst_lookup(item2)  → HSN + rate for each item
3. [optional] confirm_item_gst(...)      → if user picked from candidates
4. calculate_invoice_tax(items, client)  → full tax calculation
5. DbCreateInvoiceTool({...})            → persist invoice + items to DB
6. PdfGenerateInvoiceTool(invoiceId)     → render PDF
```

## After Creating

- Confirm: "Invoice INV-0042 ban gayi ✅"
- Offer next steps: "Send karein client ko? Ya PDF download karein?"
- Proactively mention if outstanding balance exists for this client

## Edge Cases

- **Partial details:** Ask for missing info; never create with blank fields
- **Duplicate client name:** Show existing matches, ask to confirm
- **No GSTIN on client:** Still apply GST, mark as B2C unregistered
- **Interstate supply:** Use IGST instead of CGST+SGST split
- **Round-off:** Round total to nearest rupee, show round-off line if > ₹0.50
- **Large invoice (>₹50,000):** Remind user about TDS deduction possibility
