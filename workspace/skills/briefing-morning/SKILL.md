---
name: briefing-morning
description: Send the daily morning business briefing to the owner. Use when triggered by the scheduled wakeup (every morning at configured time), or when the user says "aaj ka briefing do", "morning report", "aaj kya hai", "daily summary dikhao", "subah ki report". This is the flagship proactive skill — sends a consolidated financial snapshot every morning.
---

# Briefing — Morning

Deliver the daily morning business briefing — a complete at-a-glance snapshot sent proactively every morning.

## Wakeup Schedule

This skill is configured to run automatically every morning at the owner's preferred time (set in `settings-manage`). Default: 8:00 AM.

When triggered by wakeup:
- Do NOT wait for user input
- Fetch all data immediately
- Compose and send briefing to Telegram
- No confirmation needed

## Tool Call Sequence

```
1. db.getTodayStats()                → income today, pending today
2. db.getOverdueInvoices()           → overdue list
3. db.getDueTodayInvoices()          → due exactly today
4. db.getMonthStats()                → MTD income, expenses, profit
5. DbGetDueSoonTool({days:3}) → next 3 days reminders
6. db.getRecentPayments({days:1})    → yesterday's payments
7. compose briefing message
8. telegram.sendText(chatId, briefing)
```

## Briefing Format

```
🌅 Good Morning! — 15 Jan 2025 (Wednesday)

━━━━━━━━━━━━━━━━━━━━━
💼 JANUARY 2025 — MTD
━━━━━━━━━━━━━━━━━━━━━
💰 Income received:  ₹98,760
💸 Expenses:         ₹67,100
📊 Net Profit:       ₹31,660

━━━━━━━━━━━━━━━━━━━━━
🔴 ACTION NEEDED
━━━━━━━━━━━━━━━━━━━━━
Overdue (2):
  • Meena Stores — ₹8,500 (5 din late)
  • Kumar & Sons — ₹45,000 (2 din late)

Due TODAY (1):
  • Rohit Agencies — ₹12,000

━━━━━━━━━━━━━━━━━━━━━
📅 NEXT 3 DAYS
━━━━━━━━━━━━━━━━━━━━━
16 Jan: Raj Traders installment — ₹7,080
17 Jan: GST payment deadline
18 Jan: Sharma Tech invoice due — ₹25,000

━━━━━━━━━━━━━━━━━━━━━
✅ YESTERDAY
━━━━━━━━━━━━━━━━━━━━━
Payments received: ₹21,240
  • Raj Traders paid INV-0042 in full

━━━━━━━━━━━━━━━━━━━━━

Have a productive day! 💪
```

## Adaptive Content

- **No overdue items:** Skip "ACTION NEEDED" section; replace with "✅ Sab clear hai!"
- **No upcoming dues:** Skip "NEXT 3 DAYS" or show "Koi due date nahi agle 3 din mein"
- **Month-end (last 3 days):** Add "📅 Mahine ke 3 din baaki — GST filing ready hai?"
- **First of month:** Add last month's final summary as bonus section
- **Low income month:** Add gentle motivational nudge ("Pichle mahine se slow hai — naye clients reach out karein?")

## On-Demand Briefing

When user manually requests it (not wakeup):
- Same content but respond inline in chat
- Add: "Kisi cheez pe detail chahiye? Pooch lo."

## Tone

- Warm, professional, Hinglish
- Bullet-heavy for scannability (this is meant to be read in 30 seconds)
- Numbers always formatted: ₹1,23,456 (Indian comma system)
- Emojis used sparingly for section headers only — not excessive
