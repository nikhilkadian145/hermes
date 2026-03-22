---
name: report-expenses
description: Generate an expense summary or detailed expense report. Use when the user asks "expense report banao", "kitna kharcha hua", "expenses dikhao", "category wise kharcha", "is mahine ke expenses", or wants to analyze where money was spent. Different from P&L — this focuses only on expense breakdown and trends.
---

# Report — Expenses

Analyze and report on business expenses with category breakdowns and trends.

## Tool Call Sequence

```
1. db.getExpensesByPeriod({from, to})          → all expenses in range
2. db.groupExpensesByCategory(expenses)         → category totals
3. [optional] pdf.generateExpenseReport(data)   → full PDF
```

## Quick Chat Summary (Default)

```
💸 Expense Report — January 2025

Category Breakdown:
─────────────────────────────────
Salaries:              ₹35,000  (52%)
Rent:                  ₹15,000  (22%)
Travel:                 ₹5,200   (8%)
Software/SaaS:          ₹4,500   (7%)
Office Supplies:        ₹3,400   (5%)
Utilities:              ₹2,800   (4%)
Miscellaneous:          ₹1,200   (2%)
─────────────────────────────────
Total:                 ₹67,100

vs Last Month: ₹61,200 (+₹5,900 ↑ 9.6%)
```

## Detailed View (Per Category)

If user drills into a category ("travel expenses dikhao"):
```
✈️ Travel Expenses — January 2025

14 Jan: Petrol Delhi–Noida    ₹2,500  UPI
16 Jan: Cab to airport         ₹850   UPI
18 Jan: Train ticket           ₹1,850  Card

Total: ₹5,200
```

## Trend Analysis

If user asks for trend ("3 mahine ke expenses"):
```
📈 Expense Trend (Oct–Dec 2024)

           Oct      Nov      Dec
Salaries:  ₹35k     ₹35k     ₹35k
Rent:      ₹15k     ₹15k     ₹15k
Travel:    ₹3.2k    ₹4.8k    ₹5.2k ↑
Total:     ₹58k     ₹61k     ₹67k ↑
```

Flag rising categories: "Travel 3 mahine mein 62% badha hai."

## PDF Report

Full PDF includes:
- Period header
- Pie chart (category-wise share)
- Month-wise expense trend (bar chart)
- Itemized list per category
- GST Input Credit eligible expenses highlighted

```
pdf.generateExpenseReport(data) → data/reports/Expenses_Jan2025.pdf
```

## GST Input Credit Summary

Separate section for ITC-eligible expenses:
```
🧾 GST Input Credit Eligible: ₹12,400
  Office supplies (GST bill): ₹3,400
  Software subscription:       ₹4,500
  Professional services:       ₹4,500

CA ko export karein for GST return? 📤
```

## Flags and Alerts

- **Expense spike:** If any category > 150% of previous month average → flag it
- **Missing category data:** "Koi aur expenses nahi hain? Report accurate rahegi tabhi."
- **Cash expenses > 50%:** Remind user to prefer digital for audit trail
