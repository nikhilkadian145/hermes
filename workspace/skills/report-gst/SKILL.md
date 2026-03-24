---
name: report-gst
description: Generate a GST summary report for a filing period. Use when the user asks "GST report banao", "GSTR-1 data chahiye", "GST kitna bharna hai", "output tax kya hai", "GST filing ke liye report", "is quarter ka GST", or needs GST data for returns filing.
---

# Report — GST

Generate GSTR-1 compliant GST reports with B2B/B2C classification, HSN summary, ITC tracker, and net liability.

## Time Periods

- Monthly: "January ka GST" → 1–31 Jan
- Quarterly: "Q3 GST" → Oct–Dec
- Full year: "FY 2024-25 GST"
- Default: current month if not specified.

## Tool Call Sequence

```
1. get_gst_liability(from, to)      → output tax, ITC, net payable
2. get_hsn_summary(from, to)        → HSN-wise breakdown for GSTR-1
3. PdfGenerateGstReportTool(data)   → exportable PDF with all sections
```

## GSTR-1 Report Sections

### B2B (Registered Buyers)
- Invoices where client has GSTIN
- Shows: Invoice#, GSTIN, Taxable Value, CGST, SGST, IGST

### B2C Large (Unregistered, invoice > ₹2.5L)
- Individual invoice detail required

### B2C Small (Unregistered, invoice ≤ ₹2.5L)
- Aggregated by GST rate slab

### HSN Summary
- HSN code + description, total quantity, taxable value, tax
- Get via `get_hsn_summary(from, to)`

### ITC (Input Tax Credit)
- From expenses with `vendor_gstin` and `itc_eligible = 1`
- Shows: GST rate-wise CGST+SGST+IGST breakdown

## In-Chat Quick Summary

```
🧾 GST Summary — Jan 2025

 Output Tax:
   B2B:  ₹16,200 (5 invoices)
   B2C:  ₹2,160  (3 invoices)
   Total: ₹18,360

 Input Credit:  (₹2,148)
 ─────────────────────────
 Net Payable:   ₹16,212

 Filing: GSTR-3B due 20 Feb (5 din baaki)
```

## Flags

- HSN codes missing → "X invoices pe HSN code nahi hai"
- IGST vs CGST+SGST mismatch → check client state  
- Large ITC claims → "CA se confirm karo"
- Anomalies found → "Y anomalies detected — review in Anomalies page"
