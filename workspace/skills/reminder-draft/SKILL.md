---
name: reminder-draft
description: Draft and send a polite payment reminder message to a client. Use when the user says "Raj ko reminder bhejo", "payment reminder draft karo", "follow up message banao", "reminder message chahiye", or wants to nudge a client about a pending or overdue payment. Generates professional yet friendly Hinglish reminder messages.
---

# Reminder Draft

Craft and send polite payment reminder messages for overdue or upcoming invoices.

## When to Use

- Client payment is due soon (proactive reminder)
- Invoice is overdue (follow-up reminder)
- User wants to nudge a client without being rude
- Sending a second/third reminder for stubborn outstanding

## Information to Gather

1. **Client name** — who to remind
2. **Invoice reference** — auto-fetch if client specified
3. **Tone** — Friendly / Firm / Very Formal (default: Friendly)
4. **Days overdue** — auto-calculate from due date

## Tool Call Sequence

```
1. db.getClientOutstanding(clientName)    → fetch invoice + amount + due date
2. llm.draftReminder({client, invoice, tone, daysOverdue})
3. [show draft to user]
4. [on confirm] telegram.sendText(chatId, reminderText) OR just show for forwarding
```

## Reminder Templates by Tone

**Friendly (default — 0–7 days overdue):**
```
Namaste [Client Name] ji! 🙏

Humara invoice INV-2024-0042 ke baare mein yaad dilana tha.

📋 Invoice: INV-2024-0042
💰 Amount: ₹21,240
📅 Due Date: 31 Jan 2025

Agar payment ho gayi ho to please confirm kar dein. 
Koi problem ho to batayein, hum help karenge.

Dhanyawad! 😊
— [Business Name]
```

**Firm (8–20 days overdue):**
```
Dear [Client Name],

Aapka payment ₹21,240 abhi tak nahi mila hai.
Invoice INV-2024-0042 ki due date 31 Jan thi.

Please aaj payment process kar dein ya hume batayein.

Regards,
[Business Name]
```

**Formal/Legal (21+ days overdue):**
```
Dear [Client Name],

This is a formal notice regarding your outstanding payment of ₹21,240 
against Invoice No. INV-2024-0042 dated 01 Jan 2025.

Despite our previous reminders, the amount remains unpaid.
We request immediate settlement to avoid further action.

[Business Name] | [Phone] | [GSTIN]
```

## Draft Customization

After showing draft, ask:
"Kuch change karna hai? Ya seedha copy karein forward karne ke liye?"

Options:
- Edit before sending
- Copy text for WhatsApp forwarding
- Send to owner's Telegram (they forward manually)

## Reminder Log

After user confirms sending:
```
db.logReminderSent(invoiceId, {sentAt, tone, channel: 'whatsapp'})
```

This tracks reminder history so next reminder can escalate tone automatically.

## Escalation Logic

- 1st reminder → Friendly
- 2nd reminder (after 7 days, no response) → Firm
- 3rd reminder (after 15 days, no response) → Formal
- After 3 reminders → suggest: "CA/legal notice bhejne ka waqt ho sakta hai"
