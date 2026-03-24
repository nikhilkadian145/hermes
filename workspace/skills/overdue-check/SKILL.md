---
name: overdue-check
description: Nightly check for newly overdue invoices.
---
## overdue-check

Trigger: "Run overdue invoice check now" (from nightly cron)

Steps:
1. Call `notify_overdue_invoices` tool (new tool, see Part 4).
2. Log the count. No Telegram message needed — notifications go to webapp bell.
   The morning briefing (30 minutes later at 8 AM) will include the overdue list.
