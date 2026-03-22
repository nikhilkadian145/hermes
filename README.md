# HERMES

**AI Financial Assistant for Indian Small Businesses**

HERMES is a Telegram-first AI assistant that handles invoicing, payments, expenses, bookkeeping, and reporting for small businesses in India. It speaks Hinglish — a natural mix of Hindi and English — and feels like a trusted munshi (accountant) in your pocket.

---

## What HERMES Does

- **Invoices** — Create, send, track invoices with GST support
- **Payments** — Record full and partial payments, auto-update invoice status
- **Expenses** — Log expenses manually or via receipt photo OCR
- **Quotations** — Create quotes, convert accepted quotes to invoices
- **Reminders** — Draft and send payment reminders via Telegram
- **Reports** — P&L, Outstanding Balances, Expense Reports, GST Reports
- **CA Export** — Quarterly ZIP bundle for your Chartered Accountant
- **Udhaar** — Track informal credit (given/received)
- **Voice** — Dictate expenses and invoices via Telegram voice messages
- **Web Dashboard** — Browser-based view of all data with JWT auth

## Architecture

```
Customer's Telegram
       │
       ▼
┌──────────────────────────────────────────┐
│  nanobot gateway (frozen fork)           │
│  SOUL.md → LLM → hermes_tools.py        │
│  Native Python tools, no MCP, no subprocess │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  hermes/db.py · pdf.py · ocr.py         │
│  whisper_tool.py · export.py            │
│  SQLite · PDF files · receipt images    │
└──────────────────────────────────────────┘

Separate process:
┌──────────────────────────────────────────┐
│  FastAPI web dashboard (webapp/)         │
└──────────────────────────────────────────┘
```

## Deployment Model

- **One VM = One Business** — each customer runs HERMES on their own Google Cloud VM
- Customer pays OpenRouter directly for LLM usage
- No SaaS lock-in — one-time setup fee, then it's theirs
- You never touch their data after handover

## Setup (for development)

```bash
git clone https://github.com/nikhilkadian145/hermes.git
cd hermes
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -e .
```

## Tech Stack

- **Agent Framework**: nanobot (frozen fork)
- **Language**: Python 3.11+
- **Database**: SQLite (one file per business)
- **PDF**: WeasyPrint + Jinja2 templates
- **OCR**: OpenRouter Vision LLM
- **Voice**: OpenAI Whisper
- **Web Dashboard**: FastAPI + Jinja2 + vanilla JS
- **Messaging**: Telegram (via python-telegram-bot)

## License

MIT

---

> Forked from [HKUDS/nanobot](https://github.com/HKUDS/nanobot). See `FORKED_FROM` for details.
