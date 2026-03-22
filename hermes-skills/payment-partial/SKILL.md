---
name: payment-partial
description: Handle partial payment queries, payment schedules, and balance tracking. Use when the user asks "kitna bacha hai", "partial payment track karo", "balance due kya hai", "installment set karo", "Raj ne abhi tak kitna diya", or manages payment plans and remaining balances on invoices.
---

# Payment Partial

Track partial payments, balances due, and payment schedules for invoices.

## Use Cases

1. **Check balance remaining** on a specific invoice or client
2. **Record installment** as part of a planned payment schedule
3. **Set up payment plan** — split invoice into installments
4. **View payment history** — all payments received against an invoice

## Balance Query

When user asks how much is still pending:

```
Tool: db.getInvoicePaymentHistory(invoiceId or clientName)
```

Display:
```
📊 Raj Traders — Payment Status

Invoice: INV-2024-0042 (₹21,240)
─────────────────────────────────
✅ 05 Jan: ₹10,000 (UPI)
✅ 12 Jan: ₹5,000 (Cash)
─────────────────────────────────
Total received: ₹15,000
Balance due:    ₹6,240 ⏳

Due date: 31 Jan 2025 (19 din baaki)
```

## Payment Schedule Setup

If user wants to set installments:

```
Collect:
- Total amount
- Number of installments
- Frequency (weekly / monthly / custom dates)
- First installment date

Tool: db.createPaymentSchedule({invoiceId, installments: [...]})
Tool: reminder.schedulePaymentReminders(installments)
```

Display the plan before confirming:
```
📅 Payment Plan — Raj Traders

INV-2024-0042: ₹21,240
─────────────────────
15 Jan: ₹7,080
01 Feb: ₹7,080
15 Feb: ₹7,080

Reminders set karoon automatically? ⏰
```

## Recording Installment Payment

Same as `payment-record` but explicitly linked to a schedule entry.

After each installment:
- Update schedule entry as received
- Show next installment date
- Calculate and show remaining balance

## Overdue Partial Payments

If a scheduled installment is missed:
```
⚠️ Missed Installment

Raj Traders ka ₹7,080 aana tha 01 Feb ko.
Aaj 05 Feb hai.

Reminder bhejein? Ya payment aa gaya tha?
```

## Summary View

`db.getAllPartialInvoices()` → invoices with PARTIAL status

```
🔶 Partial Payments Pending

1. Raj Traders    INV-0042  Balance: ₹6,240   Due: 31 Jan
2. Meena Stores   INV-0038  Balance: ₹3,500   Due: 25 Jan ⚠️

Total outstanding: ₹9,740
```
