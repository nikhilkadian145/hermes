---
name: report-outstanding
description: Generate an outstanding payments report showing all unpaid and partially paid invoices. Use when the user asks "outstanding report", "kitna baaki hai", "kaunse clients ne nahi diya", "accounts receivable", "pending payments report", "overdue list dikhao", or wants to know total money owed to the business.
---

# Report — Outstanding Payments

Show all money owed to the business — unpaid and partial invoices grouped by client.

## Tool Call Sequence

```
1. DbGetOutstandingTool()            → all UNPAID + PARTIAL invoices
2. db.groupByClient(invoices)             → aggregate per client
3. [optional] PdfGenerateOutstandingReportTool(data)
```

## Quick Summary (Default — In Chat)

```
📋 Outstanding Payments Report
As of: 15 Jan 2025

🔴 OVERDUE:
  Meena Stores       ₹8,500   (5 din late)  INV-0038
  Kumar & Sons       ₹45,000  (2 din late)  INV-0035

⏳ DUE SOON (next 7 days):
  Raj Traders        ₹6,240   due 20 Jan    INV-0042
  Rohit Agencies     ₹12,000  due 18 Jan    INV-0044

📅 DUE LATER:
  Sharma Tech        ₹25,000  due 15 Feb    INV-0046
  Patel & Co         ₹18,500  due 28 Feb    INV-0047

─────────────────────────────────────
Total Outstanding:  ₹1,15,240
  Overdue:           ₹53,500
  Due soon:          ₹18,240
  Future:            ₹43,500
```

## Client-Wise Detail

If user asks for specific client: show all their outstanding invoices plus payment history.

## Aging Analysis

Group by age buckets (show if requested or in PDF):
- 0–30 days
- 31–60 days
- 61–90 days
- 90+ days (critical — flag these)

```
Aging Summary:
0–30 days:   ₹61,740  (53%)
31–60 days:  ₹38,000  (33%)
61–90 days:   ₹9,000   (8%)
90+ days:     ₹6,500   (6%) ⚠️ ACTION NEEDED
```

## PDF Report

Full PDF includes:
- Client-wise outstanding table
- Aging analysis
- Top 5 debtors by amount
- Month-wise trend of outstanding growth

```
PdfGenerateOutstandingReportTool(data) → data/reports/Outstanding_15Jan2025.pdf
```

## Actions to Offer

After showing report:
- "Sab overdue clients ko reminder bhejein? (bulk)"
- "Specific client ka status dekhna hai?"
- "PDF download karein?"
- "CA ko export karein?"

## Bulk Reminder Option

If user selects "sab ko reminder bhejo":
- Generate reminder drafts for all overdue clients
- Show all drafts for review
- Confirm before user manually sends each
