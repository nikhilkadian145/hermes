---
name: udhaar-track
description: Track informal credit (udhaar) given to clients or taken from vendors — money lent or borrowed without a formal invoice. Use when the user says "udhaar diya", "Raj ko udhaar hai", "udhaar wapas aaya", "kisko kitna diya", "udhaar list dikhao", "udhaar record karo", or manages informal credit that doesn't go through the invoice system.
---

# Udhaar Track

Manage informal credit (udhaar) — money given or taken without formal invoices.

## Two Types of Udhaar

| Type | Description | Example |
|---|---|---|
| **Given (Receivable)** | You gave udhaar to client/person | "Raj ko ₹5,000 diye the" |
| **Taken (Payable)** | You took udhaar from vendor/person | "Supplier se ₹8,000 ka maal udhar liya" |

## Recording Udhaar

**Collect:**
1. Person/party name
2. Amount
3. Direction — given or taken
4. Date
5. Reason/description (optional)
6. Expected return date (optional)

```
Tool: db.recordUdhaar({party, amount, type: 'given'|'taken', date, reason, dueDate})
```

**Confirmation:**
```
📝 Udhaar Record:

Raj ko diya: ₹5,000
Date: 15 Jan 2025
Reason: Emergency cash
Wapas kab: 31 Jan 2025

Record karoon? ✅
```

## Udhaar List

**"Udhaar list dikhao" or "kitna baaki hai":**

```
💳 Udhaar Summary — 15 Jan 2025

📤 DIYA HUA (Log aapko denge):
  Raj Traders        ₹5,000    Due: 31 Jan
  Meena (personal)   ₹2,000    No date set
  Rohit              ₹8,500    ⚠️ Overdue (10 din)
  ─────────────────────────────
  Total due to you:  ₹15,500

📥 LIYA HUA (Aap denge):
  ABC Suppliers      ₹12,000   Due: 20 Jan
  Ravi Transport     ₹3,500    Due: 25 Jan
  ─────────────────────────────
  Total you owe:     ₹15,500

Net Udhaar Position: ₹0 (balanced)
```

## Settling Udhaar

When payment returns:

**"Raj ne udhaar wapas kar diya":**
```
1. db.getUdhaar(partyName, type: 'given')
2. Show: "Raj ka ₹5,000 wapas aaya?"
3. On confirm: db.settleUdhaar(udhaariId, {settledAt, mode})
4. db.updateLedger({type: 'credit', ...})
```

After settling:
```
✅ Udhaar settled!
Raj Traders — ₹5,000 wapas aaya.
Koi udhaar baaki nahi Raj se.
```

Partial settlement also supported — same as payment-partial logic.

## Reminders

For udhaar with a due date:
- Auto-remind 2 days before due date
- Flag overdue udhaar in morning briefing
- "Rohit ka ₹8,500 ka udhaar 10 din se overdue hai — remind karein?"

## Relationship to Invoices

Udhaar is separate from formal invoices — it's for:
- Personal loans to clients
- Informal vendor credit
- Cash advances
- Family/friend business money

If user later wants to formalize an udhaar into an invoice:
"Raj ke ₹5,000 udhaar ko formal invoice mein convert karoon?"
→ `invoice-create` with pre-filled amount
