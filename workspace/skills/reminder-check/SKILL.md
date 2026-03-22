---
name: reminder-check
description: Check, list, or manage scheduled reminders and upcoming due dates. Use when the user asks "kya reminders hain", "aaj kya karna hai", "upcoming dues", "kaunse reminders set hain", "reminder cancel karo", or wants to see what's scheduled. Also triggers for proactive wakeup checks if configured as a scheduled task.
---

# Reminder Check

View, manage, and act on scheduled reminders and due dates.

## Types of Reminders HERMES Tracks

| Type | Example |
|---|---|
| Payment due | Invoice INV-0042 due in 3 days |
| Payment overdue | INV-0038 is 5 days overdue |
| Follow-up | "Call Raj about project status" |
| Installment due | Raj ki next installment 01 Feb |
| Tax deadline | GST filing due 20th of month |
| Custom | User-set reminders |

## Tool Call Sequence

```
DbGetDueSoonTool({days: 7})      → next 7 days
DbGetOverdueTool()                    → overdue invoices + missed installments
db.getPendingFollowUps()                → manual follow-ups set by user
```

## Display Format

**Daily check view:**
```
📅 Aaj ke reminders — 15 Jan 2025

🔴 OVERDUE (2):
  • Meena Stores INV-0038 — ₹8,500 (5 din late)
  • Kumar & Sons INV-0035 — ₹45,000 (2 din late)

⏰ UPCOMING (3):
  • Raj Traders INV-0042 — ₹6,240 due 20 Jan (5 din baaki)
  • Rohit advance — ₹5,000 installment due 18 Jan
  • GST filing — 20 Jan deadline

📝 FOLLOW-UPS (1):
  • Priya ke saath meeting confirm karo (set: 12 Jan)
```

## Actions After Showing

For each reminder, offer:
- **Overdue invoice:** "Reminder bhejein? Ya payment aa gaya?"
- **Upcoming invoice:** "Pehle se reminder bhej dein?"
- **Custom follow-up:** "Done? (Dismiss karo)"

## Managing Reminders

**Delete a reminder:**
```
db.deleteReminder(reminderId)
```
Confirm before deleting.

**Snooze a reminder:**
```
db.snoozeReminder(reminderId, snoozeUntil)
```
"Kal yaad dilao" → snooze 24 hours
"Agli week" → snooze 7 days

**Add a custom reminder:**
Collect: what, when → `db.createReminder({text, dueAt, type: 'custom'})`

## Proactive Wakeup Mode

When triggered by nanobot's scheduled cron (morning briefing time):
- Fetch all due today + overdue
- Send consolidated message to owner
- Do not ask for confirmation — just send the briefing

This is separate from `briefing-morning` which includes financial stats.
See `briefing-morning` skill for full morning report.
