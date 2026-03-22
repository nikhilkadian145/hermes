---
name: quotation-create
description: Create a price quotation or estimate for a potential client. Use when the user says "quotation banao", "estimate do", "quote bhejo", "price quote chahiye", "Raj ko quotation dena hai", or needs to share a formal price proposal before starting work. Quotations do not get recorded as income until converted to invoices.
---

# Quotation Create

Generate professional price quotations (estimates) for prospective clients.

## Difference from Invoice

| Quotation | Invoice |
|---|---|
| Before work starts | After work done / payment due |
| No income recorded | Income tracked in ledger |
| Has expiry date | Has due date (payment deadline) |
| Client can accept/reject | Payment expected |
| Marked QUOTE-XXXX | Marked INV-XXXX |

## Information to Collect

Ask in one message:

1. **Client name** — new or existing
2. **Line items** — what services/products being quoted
3. **Quantities and rates** — per unit pricing
4. **GST rate** — default 18%
5. **Valid until date** — default 30 days from today
6. **Special notes** — payment terms, exclusions, assumptions

```
Tool: db.getNextQuotationNumber()     → QUOTE-2024-0018
Tool: db.createQuotation({...})       → save to DB
Tool: PdfGenerateQuotationTool(quoteId)  → render PDF
```

## Quotation PDF Structure

- **Header:** Business name, GSTIN, logo
- **Client block:** To whom the quote is addressed
- **Quote number and date**
- **Valid until date** (prominent)
- **Line items table:** Description | Qty | Rate | Amount
- **Tax section:** Subtotal → GST → Total
- **Terms section:** Payment terms, validity note, inclusions/exclusions
- **Acceptance line:** "Please sign and return to confirm" (optional)

## Confirmation Preview

```
📋 Quotation Preview:

QUOTE-2024-0018 | Valid till: 14 Feb 2025
For: Raj Traders

Website Redesign        1 × ₹25,000 = ₹25,000
Mobile App (Android)    1 × ₹40,000 = ₹40,000
─────────────────────────────────────────
Subtotal:  ₹65,000
GST 18%:   ₹11,700
─────────────────────────────────────────
Total:     ₹76,700

Banaaun? Ya kuch change karni hai?
```

## After Creating

```
✅ Quotation ready!

QUOTE-2024-0018 — Raj Traders
₹76,700 (Valid: 14 Feb 2025)

PDF Telegram pe bhejein?
Raj ne accept kar liya to invoice banao → "invoice banao Raj ke liye"
```

## Converting to Invoice

When client accepts:
- "Raj ne quote accept kar liya" → trigger `invoice-create` with pre-filled data from quote
- Mark quotation as ACCEPTED in DB
- `db.updateQuotationStatus(quoteId, 'accepted')`
- `db.convertQuotationToInvoice(quoteId)` → creates draft invoice

## Quotation Status Tracking

| Status | Meaning |
|---|---|
| SENT | Delivered to client |
| ACCEPTED | Client agreed |
| REJECTED | Client declined |
| EXPIRED | Past valid date |
| CONVERTED | Became an invoice |

"Kaunse quotes pending hain?" → `db.getPendingQuotations()`

## Expiry Reminders

2 days before expiry: "QUOTE-0018 Raj Traders ka 2 din mein expire hoga — follow up karein?"
