---
name: invoice-send
description: Send an invoice to a client via Telegram message (PDF attachment). Use when the user says "invoice bhejo", "send karo Raj ko", "invoice forward karo", "WhatsApp pe bhej do invoice", or asks to share/send/forward a specific invoice to a client. Also handles resending or sharing the PDF file.
---

# Invoice Send

Deliver invoice PDFs to the business owner's Telegram so they can forward to their client.

## How HERMES Sends Invoices

HERMES sends the PDF to the **business owner's Telegram chat**. The owner then manually forwards it to their client on WhatsApp/email/Telegram. This is intentional — HERMES does not have direct access to the client's contact.

## Tool Call Sequence

```
1. db.getInvoice(invoiceId or latest for client)   → fetch invoice record
2. pdf.ensureInvoicePdf(invoiceId)                  → generate PDF if not exists
3. telegram.sendDocument(chatId, pdfPath, caption)  → send to owner
4. db.logInvoiceSent(invoiceId, timestamp)          → mark as sent in DB
```

## Resolving Which Invoice to Send

- If user specifies invoice number → use that
- If user specifies client name only → find latest unpaid invoice for that client
- If multiple unpaid → show list and ask which one

## Telegram Caption Format

```
📄 Invoice INV-2024-0042
👤 Raj Traders
💰 ₹21,240 (Due: 31 Jan 2025)

_HERMES by [Business Name]_
```

## After Sending

Confirm to the user:
```
✅ Invoice INV-2024-0042 aapke Telegram pe bhej di!
Raj Traders ko forward kar dein. 

Due date: 31 Jan 2025 (15 din baaki)
Reminder set karoon? ⏰
```

Offer to set a payment reminder automatically.

## Resend Handling

If the invoice was already sent before:
- Show previous send time: "Ye invoice 5 Jan ko already bheji thi"
- Ask: "Phir se bhejna chahte hain? (Reshare / Cancel)"
- On confirm: resend and update `last_sent_at` timestamp

## Edge Cases

- **PDF missing:** Regenerate automatically before sending
- **Invoice already paid:** Warn "Ye invoice paid hai. Phir bhi bhejein?"
- **No invoice found for client:** Offer to create one
