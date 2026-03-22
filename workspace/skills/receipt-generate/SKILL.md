---
name: receipt-generate
description: Generate and send a payment receipt to confirm money received from a client. Use when the user says "receipt banao", "receipt bhejo", "payment confirm karo Raj ko", "receipt chahiye", "payment receipt generate karo", or after recording a payment when the client needs written confirmation of their payment.
---

# Receipt Generate

Create and deliver professional payment receipts to confirm payments received.

## When to Generate a Receipt

- Immediately after recording a payment (offer proactively)
- Client asks for confirmation of their payment
- Cash payment was made — receipt is extra important
- Advance payment received

## Tool Call Sequence

```
1. db.getPayment(paymentId)              → fetch payment + linked invoice
2. PdfGenerateReceiptTool(paymentId)        → render receipt PDF
3. db.saveReceiptPath(paymentId, path)   → store path
4. MessageTool(chatId, pdfPath, caption)
```

## Resolving Which Payment

- If triggered right after `payment-record` → use that payment automatically
- If triggered standalone: "Kaunse payment ki receipt chahiye?"
  - Show recent payments (last 5) for quick selection
  - Or accept invoice number / client name

## Receipt Structure

```
════════════════════════════════════
        PAYMENT RECEIPT
════════════════════════════════════
Receipt No: REC-2024-0089
Date: 15 Jan 2025

FROM:
[Business Name]
[Address]
GSTIN: XXXXXXXXXXXX

TO:
Raj Traders
[Client Address]

PAYMENT DETAILS:
─────────────────────────────────
Invoice No:     INV-2024-0042
Invoice Date:   01 Jan 2025
Invoice Amount: ₹21,240

Amount Received: ₹21,240
Payment Mode:    UPI
Transaction ID:  TXN123456789
Payment Date:    15 Jan 2025

Balance Due:     ₹0.00
─────────────────────────────────
Status: PAID IN FULL ✅
════════════════════════════════════
This is a computer-generated receipt.
```

## Partial Payment Receipt

If payment was partial:
```
Amount Received:  ₹10,000
Invoice Amount:   ₹21,240
Balance Due:      ₹11,240 ⏳
Status: PARTIALLY PAID
```

## Telegram Caption

```
🧾 Payment Receipt — INV-2024-0042
Raj Traders | ₹21,240 | PAID ✅
15 Jan 2025

Raj ko forward kar dein.
```

## After Sending

```
✅ Receipt Telegram pe bhej di!
Raj ko forward karein as payment confirmation.

Kuch aur karna hai?
```

## Quick Receipt (No PDF)

For small cash payments where user just wants text confirmation:

```
"PDF nahi chahiye, sirf text message do" →
Generate a text-format receipt for WhatsApp forwarding:

🧾 Payment Receipt
─────────────────
Business: [Name]
Date: 15 Jan 2025
Received from: Raj Traders
Amount: ₹5,000
Mode: Cash
For: INV-2024-0042
Balance: ₹16,240 pending

[Business Name] | [Phone]
```

## Receipt Numbering

Auto-increment: `REC-YYYY-NNNN`
Separate series from invoices to avoid confusion.
