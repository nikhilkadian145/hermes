---
name: expense-log
description: Log a business expense manually (without a photo/receipt). Use when the user types "expense add karo", "₹500 petrol ka", "aaj ₹2000 kharcha hua", "office supplies kharche", "rent pay kiya ₹15,000", or describes any money spent on business without sending an image. For photo-based expense logging, the expense-ocr skill handles that.
---

# Expense Log

Record business expenses manually for bookkeeping and GST input credit tracking.

## Information to Collect

Ask in one message if missing:

1. **Amount** — how much was spent (₹)
2. **Category** — what kind of expense (see categories below)
3. **Vendor/description** — who was paid / what was bought
4. **Date** — today by default
5. **Payment mode** — Cash / UPI / Card / Bank Transfer
6. **GST paid?** — did you get a GST invoice? (important for input credit)
7. **Bill number** — optional, for reference

## Expense Categories

| Category | Examples |
|---|---|
| Office Supplies | Stationery, printer ink, USB drives |
| Travel | Petrol, auto, cab, flight, train |
| Rent | Office rent, workspace fees |
| Utilities | Electricity, internet, phone |
| Salaries | Staff payments, contractor fees |
| Food & Entertainment | Client lunches, team meals |
| Equipment | Laptop, phone, tools |
| Software & Subscriptions | SaaS tools, domains, hosting |
| Advertising | Google Ads, social media, printing |
| Professional Services | CA fees, lawyer, consultant |
| Miscellaneous | Anything else |

## Tool Call Sequence

```
1. DbLogExpenseTool({amount, category, vendor, date, mode, gstPaid, billNo})
2. db.updateLedger({type: 'debit', category, amount, date})
```

## Confirmation Before Logging

```
💸 Expense Log:

Amount: ₹2,500
Category: Travel
Description: Petrol — Delhi to Noida
Mode: UPI
Date: 15 Jan 2025
GST input credit: No

Log karoon? ✅
```

## After Logging

```
✅ Expense recorded!

₹2,500 — Travel (Petrol)
15 Jan 2025 | UPI

Is month total expenses: ₹18,450
```

Show running monthly expense total after each log to build awareness.

## GST Input Credit Tracking

If `gstPaid = yes`:
- Ask for vendor GSTIN and bill number
- Flag this expense for GST return (ITC eligible)
- Store separately for CA export

```
📝 GST Note: Ye expense ITC eligible hai.
Vendor GSTIN aur invoice number save kar lo — 
CA ko export karte waqt kaam aayega.
```

## Recurring Expenses

If user says "rent har mahine ₹15,000":
- Ask: "Recurring expense set karoon? Automatically log hoga har mahine."
- `db.createRecurringExpense({...})` with monthly schedule
