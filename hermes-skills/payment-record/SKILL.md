---
name: payment-record
description: Record a payment received from a client against an invoice. Use when the user says "payment aa gaya", "Raj ne pay kar diya", "₹10,000 mila", "payment record karo", "mark as paid", "paise aa gaye", or mentions receiving money from a client. Handles full payments, partial payments, and advance payments.
---

# Payment Record

Record incoming payments against invoices and update ledger.

## Information to Collect

1. **Client name** — who paid (or which invoice)
2. **Amount received** — exact rupee amount
3. **Payment mode** — UPI / Cash / Bank Transfer / Cheque
4. **Date** — today by default; ask if different
5. **Invoice reference** — which invoice this is for (auto-match if possible)
6. **UTR/reference number** — optional, but important for bank transfers

## Tool Call Sequence

```
1. db.findUnpaidInvoice(clientName, amount)    → match invoice
2. db.recordPayment({invoiceId, amount, mode, date, utr})
3. db.updateInvoiceStatus(invoiceId)           → PAID if full, PARTIAL if not
4. db.updateLedger({type: 'credit', ...})      → update bookkeeping ledger
```

## Matching Logic

- If amount = invoice total → mark PAID ✅
- If amount < invoice total → mark PARTIAL 🔶, record balance due
- If amount > invoice total → ask: "Advance tha? Ya koi aur invoice ke liye?"
- If no invoice found → record as unlinked advance payment

## Confirmation Display

```
💰 Payment Record Karna Hai:

Client: Raj Traders
Invoice: INV-2024-0042 (₹21,240)
Amount received: ₹21,240 ✅ FULL PAYMENT
Mode: UPI
Date: 15 Jan 2025

Record karoon? ✅
```

## After Recording

```
✅ Payment recorded!

INV-2024-0042 → PAID 🎉
Raj Traders ka koi balance nahi bacha.

Receipt generate karoon? 📄
```

- Offer to generate receipt
- Offer to check other pending invoices for same client
- Auto-update outstanding report

## Payment Modes

| Mode | Fields to log |
|---|---|
| UPI | UPI ID / transaction ID |
| Cash | Just amount + date |
| Bank Transfer | UTR number |
| Cheque | Cheque number, bank, clearance date |

## Partial Payment Handling

```
🔶 Partial Payment:

Received: ₹10,000
Invoice total: ₹21,240
Balance due: ₹11,240

Reminder set karoon payment balance ke liye? ⏰
```

Always set a reminder if partial payment received.
