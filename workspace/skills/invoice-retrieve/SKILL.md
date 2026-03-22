---
name: invoice-retrieve
description: Look up, search, or find existing invoices. Use when the user asks "invoice dikhao", "kaunsi invoice pending hai", "last invoice kya tha", "invoice number INV-xxx", "Raj ki invoices", "is month ki invoices", or any query about finding/viewing/listing invoices already created.
---

# Invoice Retrieve

Search, filter, and display invoice records from the database.

## Query Patterns to Handle

| User says | What to fetch |
|---|---|
| "Last invoice dikhao" | Most recent invoice (any client) |
| "Raj ki invoices" | All invoices for client matching "Raj" |
| "Pending invoices" | All invoices with status = UNPAID or PARTIAL |
| "INV-2024-0042" | Exact invoice by number |
| "Is mahine ki invoices" | Invoices created this calendar month |
| "Overdue invoices" | Invoices past due date, status ≠ PAID |
| "Last 5 invoices" | 5 most recent across all clients |

## Tool Call Sequence

```
db.queryInvoices({ filters })   → returns array of invoice records
db.getInvoiceLineItems(id)      → fetch line items for a specific invoice
```

## Display Format

**Single invoice:**
```
📄 INV-2024-0042
Client: Raj Traders
Date: 01 Jan 2025 | Due: 31 Jan 2025
Amount: ₹21,240 | Status: ⏳ UNPAID
─────────────────
Web Design:    ₹15,000
Hosting Setup: ₹3,000
GST (18%):     ₹3,240
─────────────────
[Send] [Mark Paid] [Download PDF]
```

**Invoice list:**
```
📋 Pending Invoices (3)

1. INV-2024-0042 | Raj Traders | ₹21,240 | Due 31 Jan
2. INV-2024-0038 | Meena Stores | ₹8,500 | Due 25 Jan ⚠️ OVERDUE
3. INV-2024-0035 | Kumar & Sons | ₹45,000 | Due 28 Jan

Total pending: ₹74,740
```

## Status Indicators

- ✅ PAID — received full payment
- ⏳ UNPAID — no payment received
- 🔶 PARTIAL — some payment received
- 🔴 OVERDUE — past due date, not fully paid

## Offer Actions After Showing

After displaying results, always offer relevant next steps:
- For unpaid: "Send reminder? Ya payment record karein?"
- For single invoice: "PDF chahiye? Ya send karein?"
- For list: "Kisi specific invoice pe kaam karna hai?"

## Filters

- **Date range:** "pichle 3 mahine", "January 2025", "FY 2024-25"
- **Client:** fuzzy match on client name
- **Status:** paid / unpaid / partial / overdue
- **Amount:** "10,000 se zyada", "> ₹50,000"
- **Sort:** newest first by default; can sort by amount or due date
