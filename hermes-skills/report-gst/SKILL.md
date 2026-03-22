---
name: report-gst
description: Generate a GST summary report for a filing period. Use when the user asks "GST report banao", "GSTR-1 data chahiye", "GST kitna bharna hai", "output tax kya hai", "GST filing ke liye report", "is quarter ka GST", or needs GST data for returns filing. Summarizes output tax collected on invoices and input tax paid on expenses.
---

# Report — GST

Generate GST summary data for GSTR-1 / GSTR-3B filing preparation.

## Time Periods

- Monthly: "January ka GST" → 1–31 Jan
- Quarterly: "Q3 GST" → Oct–Dec
- Full year: "FY 2024-25 GST"

Default: current month if not specified.

## Tool Call Sequence

```
1. db.getInvoicesByPeriod({from, to, paid: true})   → output tax (B2B + B2C)
2. db.getITCExpenses({from, to})                     → input tax credit
3. db.groupByGSTRate(invoices)                       → split by 5/12/18/28%
4. pdf.generateGSTReport(data)                       → exportable PDF
```

## GST Report Structure

```
════════════════════════════════════════
  GST SUMMARY REPORT
  [Business Name] | GSTIN: XX-XXXXX
  Period: January 2025
════════════════════════════════════════

OUTPUT TAX (Tax Collected on Sales)
────────────────────────────────────
B2B Invoices (Registered clients):
  Taxable Value:    ₹90,000
  CGST (9%):         ₹8,100
  SGST (9%):         ₹8,100
  Total GST:        ₹16,200

B2C Invoices (Unregistered clients):
  Taxable Value:    ₹12,000
  CGST (9%):         ₹1,080
  SGST (9%):         ₹1,080
  Total GST:         ₹2,160

Total Output Tax:   ₹18,360
────────────────────────────────────

INPUT TAX CREDIT (Tax Paid on Purchases)
────────────────────────────────────
Office Supplies:    ₹3,400 → GST: ₹520
Software/SaaS:      ₹4,500 → GST: ₹814
Professional:       ₹4,500 → GST: ₹814
Total ITC:          ₹2,148
────────────────────────────────────

NET GST PAYABLE:   ₹16,212
  (Output ₹18,360 - ITC ₹2,148)
════════════════════════════════════════
```

## In-Chat Quick Summary

```
🧾 GST Summary — Jan 2025

Output tax collected: ₹18,360
Input credit (ITC):  (₹2,148)
─────────────────────────────
Net GST payable:     ₹16,212

Filing deadline: 20 Feb 2025 (36 din baaki)

Detailed PDF chahiye? CA ko bhejein?
```

## GSTR-1 Data Export

Separate HSN-wise summary (required for GSTR-1):
- Group invoices by HSN/SAC code
- Show taxable value + GST per code

Remind user: "Ye data aapke CA ko de do ya GST portal pe manually enter karo."

## Filing Reminders

Auto-remind when:
- GSTR-1 due: 11th of following month
- GSTR-3B due: 20th of following month

"⚠️ GSTR-3B deadline 20 Feb hai — 5 din baaki. CA ko data bhej dein."

## Flags

- HSN codes missing on invoices → "Kuch invoices pe HSN code nahi hai. CA se puch ke add karo."
- IGST vs CGST+SGST mismatch → highlight client state vs business state
- Large ITC claims → "ITC ₹X hai — CA se confirm karo claim eligibility"
