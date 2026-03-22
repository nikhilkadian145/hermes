---
name: report-pl
description: Generate a Profit & Loss (P&L) report for the business. Use when the user asks "P&L report banao", "profit loss dikhao", "is mahine kitna kamaya", "net profit kya hai", "income expense report chahiye", "monthly P&L", or asks about business profitability for any time period.
---

# Report — Profit & Loss

Generate a clear P&L statement from invoiced income and logged expenses.

## Time Period Options

Interpret naturally:
- "Is mahine" → current calendar month
- "Pichla mahine" → previous calendar month
- "Q1 / Q2 / Q3 / Q4" → financial year quarters (Apr-Jun, Jul-Sep, Oct-Dec, Jan-Mar)
- "Is saal" → current financial year (Apr 1 to today)
- "FY 2024-25" → full financial year
- Specific date range → use as given

Default if not specified: current month.

## Tool Call Sequence

```
1. DbGetPlSummaryTool({from, to})        → paid invoices (income)
2. DbListExpensesTool({from, to})       → logged expenses by category
3. PdfGeneratePlReportTool({income, expenses, period})  → PDF
```

## P&L Structure

```
════════════════════════════════════
  PROFIT & LOSS STATEMENT
  [Business Name]
  Period: January 2025
════════════════════════════════════

INCOME
─────────────────────────────────────
Invoiced Revenue:          ₹1,20,000
  Less: Unpaid Invoices:   (₹21,240)
─────────────────────────────────────
Net Revenue Received:      ₹98,760

EXPENSES
─────────────────────────────────────
Office Supplies:            ₹3,400
Travel:                     ₹5,200
Rent:                      ₹15,000
Utilities:                  ₹2,800
Software & Subscriptions:   ₹4,500
Salaries:                  ₹35,000
Miscellaneous:              ₹1,200
─────────────────────────────────────
Total Expenses:            ₹67,100

════════════════════════════════════
NET PROFIT:                ₹31,660
Profit Margin:              32.1%
════════════════════════════════════
```

## Inline Summary (Quick Reply)

Before generating full PDF, show quick summary in chat:
```
📊 P&L — January 2025

Income received:  ₹98,760
Total expenses:   ₹67,100
─────────────────
Net Profit: ₹31,660 (32.1%) ✅

PDF report chahiye? 📄
```

## PDF Report

Full PDF includes:
- Cover: Business name, period, generated date
- Income breakdown (client-wise invoices)
- Expense breakdown (category-wise)
- Month-over-month comparison if previous period data exists
- Simple bar chart (income vs expense)

```
PdfGeneratePlReportTool(data) → data/reports/PL_Jan2025.pdf
MessageTool(chatId, pdfPath)
```

## Notes and Flags

- Unpaid invoices shown separately — not counted in "received"
- If expenses > income: "⚠️ Is mahine loss hua: ₹X,XXX. Expenses check karein."
- If data is sparse (< 5 expense entries): "Kuch expenses add nahi hue? Aur expenses hain to log karo accurate report ke liye."
