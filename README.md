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

## 🚀 HERMES — Start Everything From Scratch

You need **3 terminals**. Here's the exact sequence:

---

### Terminal 1: Backend (FastAPI)

```powershell
cd d:\HERMES

# Set the database path to your customer folder
$env:DB_PATH = "d:\HERMES\test_customer\hermes.db"

# Start the backend
uvicorn webapp.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

This auto-creates `hermes.db` if it doesn't exist, runs all schema migrations, and starts the API.

✅ Verify: Open `http://localhost:8000/api/health` → `{"status":"ok"}`

---

### Terminal 2: Frontend (React/Vite)

```powershell
cd d:\HERMES\webapp\frontend
npm install          # only needed first time
npm run dev
```

✅ Verify: Open `http://localhost:5173` → Dashboard loads

---

### Terminal 3: Agent (nanobot)

```powershell
cd d:\HERMES\test_customer
nanobot
```

This starts the AI agent in interactive CLI mode. It reads [config.json](cci:7://file:///d:/HERMES/test_customer/config.json:0:0-0:0) from the current directory.

---

### First-time setup (do this once)

1. Open `http://localhost:5173/settings` in your browser
2. Go to the **🤖 AI Configuration** tab
3. Select your **LLM Provider** (e.g. OpenRouter, Anthropic)
4. Paste your **API Key**
5. Set your **Model** (e.g. `anthropic/claude-sonnet-4-20250514`)
6. Click **Save Changes**
7. **Restart Terminal 3** (the nanobot agent) for the new config to take effect

---

### Quick verification checklist

| Step | What to do                                                          | Expected result                        |
| ---- | ------------------------------------------------------------------- | -------------------------------------- |
| 1    | Open `http://localhost:5173`                                        | Dashboard with KPI cards               |
| 2    | Click 🔔 bell icon                                                  | Notification panel slides open         |
| 3    | Go to Settings → 🤖 AI Configuration                                | See your provider/model fields         |
| 4    | In Terminal 3, type: `"Create a test invoice for ABC Corp, ₹10000"` | Agent creates invoice                  |
| 5    | Refresh `/invoices/sales`                                           | Invoice appears in the list            |
| 6    | Check 🔔 bell                                                       | "Invoice Created" notification appears |

---

### If something goes wrong

| Problem                       | Fix                                                                    |
| ----------------------------- | ---------------------------------------------------------------------- |
| Backend won't start           | Make sure `pip install -e .` completed from `d:\HERMES`                |
| `ModuleNotFoundError: hermes` | Run `pip install -e .` again from `d:\HERMES`                          |
| Frontend blank screen         | Check browser console (F12), make sure backend is running on port 8000 |
| Agent says "No API key"       | Go to Settings → AI Config → set key → restart agent                   |
| Database errors               | Delete `test_customer/hermes.db` and restart backend (it recreates)    |
