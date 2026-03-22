---
name: bookkeeping-query
description: Answer any natural language question about the business finances from the ledger and database. Use when the user asks "kitna aaya is mahine", "net cash kya hai", "sabse zyada kisne diya", "kaunsa expense sabse zyada hai", "last week ka summary", "business kaisa chal raha hai", or any open-ended financial question that needs data lookup and interpretation.
---

# Bookkeeping Query

Answer any financial question about the business by querying the database and explaining in plain Hinglish.

## Types of Questions to Handle

| Question type | Example |
|---|---|
| Cash received | "Is mahine kitna aaya?" |
| Cash spent | "Kitna kharcha hua pichle hafte?" |
| Net position | "Ab mera balance kya hai?" |
| Client ranking | "Sabse zyada kaun pay karta hai?" |
| Expense insight | "Kaunsa expense sabse zyada hai?" |
| Comparison | "Pichle mahine se better hai kya?" |
| Trend | "Last 6 mahine ka income trend" |
| Specific lookup | "March mein travel pe kitna kharcha tha?" |
| Health check | "Business kaisa chal raha hai?" |

## Tool Call Sequence

```
1. Parse question → identify metric + time period + filters
2. db.query(relevantTables, {filters})      → raw data
3. calculate(metrics)                        → computed answer
4. format and explain in Hinglish
```

## Response Style

Always answer in plain conversational Hinglish. No jargon. Numbers always in ₹ with comma formatting. Add context and one actionable insight.

**Example — "Is mahine kitna aaya?"**
```
📊 January 2025 mein:

Payments received: ₹98,760
  (8 clients ne pay kiya)

Sabse bada payment:
  Kumar & Sons — ₹45,000 (18 Jan)

Still pending: ₹27,740 (2 invoices)

Pichle mahine (Dec) se 12% zyada aaya ✅
```

**Example — "Business kaisa chal raha hai?"**
```
📈 Business Health — January 2025

💰 Revenue:    ₹98,760
💸 Expenses:   ₹67,100
📊 Net Profit: ₹31,660 (32% margin)

🟢 Income: UP ↑ 12% vs last month
🟡 Expenses: UP ↑ 9.6% vs last month
🟢 Profit: UP ↑ 15% vs last month

⚠️ Watch out: ₹53,500 overdue from 2 clients

Overall: Acha chal raha hai! Overdue collections
pe focus karo — woh aate hi margin 54% ho jayega.
```

**Example — "Sabse zyada kaun pay karta hai?"**
```
🏆 Top Paying Clients (This FY)

1. Kumar & Sons      ₹3,45,000  ⭐ Most reliable
2. Raj Traders       ₹2,12,760
3. Sharma Tech       ₹1,89,000
4. Patel & Co        ₹98,400
5. Meena Stores      ₹67,200
```

## Calculations Available

- Total revenue (by period, by client, by service type)
- Total expenses (by period, by category, by vendor)
- Net profit and profit margin
- Cash inflow vs outflow
- Outstanding total and aging
- Average invoice value
- Average payment time (days to pay)
- Month-over-month / year-over-year comparison
- Top clients by revenue
- Top expense categories

## Handling Ambiguity

If question is vague, answer the most likely interpretation and offer alternatives:
"Yeh lo is mahine ki income. Ya aur kuch specific dekhna hai — expenses, profit, ya outstanding?"

## Limitations

Be honest when data is insufficient:
"Sirf 3 expense entries hain is mahine mein — accurately nahi bata sakta. Expenses log karo to better picture milegi."
