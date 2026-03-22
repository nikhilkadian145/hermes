# HERMES — Implementation Plan v5
### Nanobot Fork · Native Tools · FastAPI Dashboard · Python Only
### Version 5.0 | Source of Truth — Supersedes All Previous Versions

---

> **What changed from v4:**
> v4 still used MCP stdio — an external subprocess bridge between nanobot and HERMES tools.
> Correct architecture, but adds an unnecessary layer for a product you own outright.
>
> **v5 forks nanobot entirely.**
>
> You clone nanobot, freeze it, and build HERMES *inside* it. Tools are native Python
> subclasses of nanobot's own `Tool` base class, registered directly in the tool registry.
> No MCP. No subprocess. No external protocol. One Python process per customer.
>
> This is correct because:
> - You charge a one-time fee. No SaaS lock-in. Ship once, done.
> - Customer runs HERMES on their own GVM (their Google account, their billing). You touch nothing after handover.
> - Customer pays OpenRouter directly for API usage. Zero ongoing cost for you.
> - You never need nanobot upstream changes — your fork is frozen at the version you ship.
> - Native tools are faster, simpler to debug, and have zero serialization overhead.
> - You own the full stack: agent loop, tools, Telegram, web dashboard, all in one repo.

---

## WHAT THE FORK CHANGES INSIDE NANOBOT

| File / Location | What HERMES does to it |
|---|---|
| `nanobot/templates/SOUL.md` | Replaced with HERMES personality template |
| `nanobot/agent/tools/registry.py` | Modified to auto-load `hermes_tools.py` |
| `nanobot/agent/tools/hermes_tools.py` | NEW — all Tool subclasses for HERMES |
| `nanobot/skills/` | Not used — HERMES skills live in `workspace/skills/` |
| `pyproject.toml` | Renamed project to `hermes`, updated deps |
| `README.md` | Replaced with HERMES README |

**Everything else in nanobot is untouched.** Telegram handler, session manager, agent loop,
cron service, memory consolidation — all frozen and working exactly as nanobot shipped them.

---

## ARCHITECTURE DIAGRAM

```
CUSTOMER'S TELEGRAM
       │
       ▼
┌──────────────────────────────────────────────────────┐
│           nanobot gateway (frozen fork)              │
│                                                      │
│  1. Telegram message received                        │
│  2. SOUL.md → injected as system prompt              │
│  3. workspace/skills/ → skill descriptions loaded    │
│  4. LLM picks skill, decides to call tool            │
│  5. Tool call → hermes_tools.py (native Python)      │
│  6. hermes_tools.py → hermes/db.py / pdf.py / etc.  │
│  7. Result returned to agent loop                    │
│  8. LLM formats Hinglish reply                       │
│  9. nanobot sends via Telegram                       │
└──────────────────────────────────────────────────────┘
       │ direct Python call (no subprocess, no MCP)
       ▼
┌──────────────────────────────────────────────────────┐
│  hermes/db.py  hermes/pdf.py  hermes/ocr.py          │
│  hermes/whisper_tool.py  hermes/export.py            │
│  SQLite DB · PDF files · receipt images              │
└──────────────────────────────────────────────────────┘

SEPARATE PM2 PROCESS:
┌──────────────────────────────────────────────────────┐
│  FastAPI web dashboard (webapp/)                     │
│  Direct SQLite read · JWT auth · file browser        │
└──────────────────────────────────────────────────────┘
```

---

## FULL DIRECTORY STRUCTURE

```
hermes/                                  ← your repo (forked from nanobot)
├── nanobot/                             ← original nanobot package, modified minimally
│   ├── agent/
│   │   ├── tools/
│   │   │   ├── hermes_tools.py          ← NEW: all HERMES Tool subclasses (native)
│   │   │   ├── registry.py              ← MODIFIED: loads hermes_tools automatically
│   │   │   ├── base.py                  ← untouched
│   │   │   ├── mcp.py                   ← kept but not used
│   │   │   ├── filesystem.py            ← untouched
│   │   │   ├── shell.py                 ← untouched
│   │   │   └── web.py                   ← untouched
│   │   ├── context.py                   ← untouched
│   │   ├── loop.py                      ← untouched
│   │   ├── memory.py                    ← untouched
│   │   ├── skills.py                    ← untouched
│   │   └── subagent.py                  ← untouched
│   ├── channels/                        ← untouched (Telegram, Discord, etc.)
│   ├── cron/                            ← untouched
│   ├── session/                         ← untouched
│   ├── templates/
│   │   ├── SOUL.md                      ← REPLACED with HERMES personality template
│   │   └── memory/MEMORY.md             ← untouched
│   └── __main__.py                      ← untouched
│
├── hermes/                              ← all HERMES business logic
│   ├── __init__.py
│   ├── db.py                            ← all SQLite operations
│   ├── pdf.py                           ← WeasyPrint invoice/receipt/report PDFs
│   ├── ocr.py                           ← vision LLM receipt extraction
│   ├── whisper_tool.py                  ← voice transcription
│   └── export.py                        ← CA export bundle (zip)
│
├── workspace/                           ← template workspace (copied per customer)
│   ├── SOUL.md                          ← HERMES personality ({{VARS}} placeholders)
│   └── skills/
│       ├── invoice-create/SKILL.md
│       ├── invoice-retrieve/SKILL.md
│       ├── invoice-send/SKILL.md
│       ├── payment-record/SKILL.md
│       ├── payment-partial/SKILL.md
│       ├── expense-log/SKILL.md
│       ├── expense-ocr/SKILL.md
│       ├── reminder-check/SKILL.md
│       ├── reminder-draft/SKILL.md
│       ├── report-pl/SKILL.md
│       ├── report-outstanding/SKILL.md
│       ├── report-expenses/SKILL.md
│       ├── report-gst/SKILL.md
│       ├── report-ca-export/SKILL.md
│       ├── client-manage/SKILL.md
│       ├── bookkeeping-query/SKILL.md
│       ├── briefing-morning/SKILL.md
│       ├── udhaar-track/SKILL.md
│       ├── quotation-create/SKILL.md
│       ├── receipt-generate/SKILL.md
│       ├── message-draft/SKILL.md
│       └── settings-manage/SKILL.md
│
├── templates/                           ← Jinja2 HTML → PDF templates
│   ├── invoice.html
│   ├── receipt.html
│   ├── quotation.html
│   ├── report_pl.html
│   ├── report_outstanding.html
│   ├── report_expenses.html
│   └── report_gst.html
│
├── webapp/                              ← FastAPI web dashboard (separate PM2 process)
│   ├── main.py
│   ├── auth.py                          ← JWT + bcrypt
│   ├── database.py                      ← read-only SQLite access layer
│   ├── routers/
│   │   ├── dashboard.py
│   │   ├── invoices.py
│   │   ├── clients.py
│   │   ├── expenses.py
│   │   ├── reports.py
│   │   ├── files.py
│   │   └── settings.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── invoices.html
│       ├── invoice_detail.html
│       ├── clients.html
│       ├── client_detail.html
│       ├── expenses.html
│       ├── reports.html
│       ├── files.html
│       └── settings.html
│
├── scripts/
│   ├── install.sh                       ← one-line server setup
│   ├── provision.sh                     ← new customer provisioning
│   └── onboard-tui.js                   ← interactive CLI onboarding
│
├── requirements.txt
├── pyproject.toml                       ← renamed from nanobot, hermes entry point
└── .gitignore
```

---

Data directory on customer's GVM:
```
/home/hermes/data/                       ← this customer's data (one VM = one business)
├── config.json                          ← nanobot gateway config
├── workspace/
│   ├── SOUL.md                          ← filled from template at install time
│   ├── skills/ → symlink to /home/hermes/app/workspace/skills/
│   └── memory/
│       └── HISTORY.md                   ← auto-maintained by nanobot memory system
├── db/
│   └── hermes.db                        ← the business's SQLite DB
├── invoices/                            ← generated invoice PDFs
├── expenses/
│   ├── originals/                       ← raw receipt images from Telegram
│   └── processed/                       ← resized before OCR
├── reports/                             ← generated report PDFs
├── exports/                             ← CA export ZIP bundles
├── uploads/
├── logs/
└── webapp/
    └── .env                             ← DB_PATH, JWT_SECRET, PORT
```

> **One VM = One Business.** Each customer runs HERMES on their own Google VM, in their own
> Google account. There is no multi-tenant directory structure. `/home/hermes/data/` is always
> this one business. No `c001/c002` naming needed.

---

## PHASES AT A GLANCE

| Phase | Name | Deliverable |
|---|---|---|
| 1 | Fork & Repo Setup | nanobot forked, renamed hermes, venv working |
| 2 | Codebase Cleanup | Unused nanobot skills removed, structure added |
| 3 | pyproject.toml & Requirements | hermes is the installable package |
| 4 | Database Layer | schema.sql + hermes/db.py fully tested |
| 5 | SOUL.md & Config Template | HERMES personality done, config.json format confirmed |
| 6 | Native Tool Registration | hermes_tools.py wired into registry.py |
| 7 | PDF Generator | hermes/pdf.py + all Jinja2 templates |
| 8 | OCR Tool | hermes/ocr.py vision LLM pipeline tested |
| 9 | Voice Tool | hermes/whisper_tool.py tested |
| 10 | Export Tool | hermes/export.py CA bundle tested |
| 11 | 22 SKILL.md Files | All skills in workspace/skills/, routing confirmed |
| 12 | Invoice Tools E2E | Create → PDF → Send via Telegram working |
| 13 | Payment & Bookkeeping | Record, partial, ledger working |
| 14 | Expense & OCR Pipeline | Photo → vision LLM → confirm → DB |
| 15 | Quotation, Receipt, Udhaar | All 3 skill groups E2E |
| 16 | Reminder + Cron Wakeup | Morning briefing auto-firing |
| 17 | All Report Tools | 5 report types generating correct PDFs |
| 18 | Webapp — Foundation | FastAPI up, auth working, DB layer |
| 19 | Webapp — Dashboard & Invoices | KPI cards, invoice list, invoice detail |
| 20 | Webapp — Clients & Expenses | Client detail, expense gallery |
| 21 | Webapp — Reports & Files | Report generation UI, file browser |
| 22 | Webapp — Settings | Business info, password change |
| 23 | Full E2E Test on YOUR GVM | 40+ scenarios pass on your own test VM — this is your QA gate |
| 24 | Deploy to Customer's GVM | SSH into customer's VM, run install + onboard, hand over — you're done |

---

## PHASE 1 — Fork & Repo Setup

**Goal:** Clone nanobot into your own repo. Freeze it. Rename the project.

### Task 1.1 — Fork nanobot
- Go to nanobot's GitHub page
- Fork it to your own GitHub account under the name `hermes`
- Clone it locally: `git clone https://github.com/YOURNAME/hermes`
- Create a `main` branch as your working branch
- Add a `FORKED_FROM` file at root noting nanobot version + commit hash (for your own reference)
- From this point: never pull upstream again

### Task 1.2 — Create Python venv
- Inside the cloned repo: `python3 -m venv .venv`
- `source .venv/bin/activate`
- Install nanobot in editable mode: `pip install -e .`
- Confirm `nanobot status` runs without error

### Task 1.3 — Confirm nanobot internals work
- Run the existing nanobot test suite: `pytest tests/ -x -q`
- All tests should pass — this is your baseline confirmation that the fork is intact
- Note any that fail before you've touched anything (pre-existing issues)

---

## PHASE 2 — Codebase Cleanup

**Goal:** Remove nanobot's built-in skills that HERMES does not use. Add HERMES directories.

### Task 2.1 — Remove nanobot built-in skills
- Delete `nanobot/skills/clawhub/`
- Delete `nanobot/skills/github/`
- Delete `nanobot/skills/tmux/`
- Delete `nanobot/skills/weather/`
- Delete `nanobot/skills/skill-creator/`
- Keep: `nanobot/skills/memory/SKILL.md`, `nanobot/skills/cron/SKILL.md`, `nanobot/skills/summarize/SKILL.md`
- These 3 are useful to HERMES (memory management, cron briefing, summarize)

### Task 2.2 — Create HERMES directory scaffold
```
mkdir -p hermes/
mkdir -p workspace/skills/
mkdir -p templates/
mkdir -p webapp/routers/
mkdir -p webapp/static/css/
mkdir -p webapp/static/js/
mkdir -p webapp/templates/
mkdir -p scripts/
```
- Create empty `hermes/__init__.py`
- Create empty `webapp/__init__.py`

### Task 2.3 — Replace nanobot SOUL.md template
- Location: `nanobot/templates/SOUL.md`
- This is the default personality injected if no workspace SOUL.md exists
- Replace its content with a generic HERMES fallback (before the real per-customer SOUL.md is installed)
- Content should say: "You are HERMES, an AI financial assistant for small businesses in India. You help with invoices, expenses, payments, and bookkeeping. You respond in Hinglish — a natural mix of Hindi and English."

### Task 2.4 — Update README
- Replace nanobot's README.md with a HERMES README describing the product, setup, and architecture
- Not critical path but keeps the repo clean

---

## PHASE 3 — pyproject.toml & Requirements

**Goal:** Make `hermes` the installable Python package. Declare all dependencies.

### Task 3.1 — Edit pyproject.toml
- Change `name` from `nanobot-ai` to `hermes`
- Change `description` to HERMES product description
- Keep all nanobot dependencies as-is (they are required)
- Add HERMES-specific dependencies:
  - `weasyprint` — HTML to PDF
  - `jinja2` — PDF templates (likely already present)
  - `Pillow` — image resize before OCR
  - `openai-whisper` — voice transcription
  - `httpx` — HTTP client for vision LLM OCR calls
  - `fastapi` — web dashboard
  - `uvicorn[standard]` — ASGI server
  - `python-jose[cryptography]` — JWT tokens
  - `passlib[bcrypt]` — password hashing
  - `python-multipart` — file uploads in FastAPI
  - `python-dotenv` — .env loading
  - `python-dateutil` — date parsing
  - `babel` — Indian number formatting (₹)
  - `aiofiles` — async file serving in FastAPI

### Task 3.2 — Create requirements.txt
- Generate from pyproject.toml for deployment use: `pip freeze > requirements.txt`
- Add a comment section at top noting system binaries required:
  - `ffmpeg` — for Whisper audio conversion
  - `libpango*`, `libharfbuzz*`, `libffi-dev` — for WeasyPrint rendering
  - `wkhtmltopdf` is NOT needed (WeasyPrint is self-contained)

### Task 3.3 — Reinstall in editable mode
- `pip install -e ".[all]"` or `pip install -e .`
- Confirm `hermes` is importable: `python -c "import hermes"`
- Confirm nanobot CLI still works: `nanobot status`

---

## PHASE 4 — Database Layer

**Goal:** Define the full schema and write all SQLite operations HERMES needs.

### Task 4.1 — Write schema.sql
Create `hermes/schema.sql` with the following tables:

**business** — single row, the owner's business settings
- id, name, owner_name, address, city, state, pin, gstin, phone, email, bank_name, account_number, ifsc, upi_id, web_password_hash, currency (default INR), created_at

**clients** — customers of the business
- id, name, phone, email, address, gstin, notes, created_at, updated_at

**invoices** — invoice header
- id, invoice_number (unique), client_id FK, issue_date, due_date, subtotal, tax_rate, tax_amount, total, status (draft/sent/paid/overdue/cancelled), notes, pdf_path, created_at, updated_at

**invoice_items** — line items
- id, invoice_id FK, description, quantity, unit_price, amount

**payments** — payments received against invoices
- id, invoice_id FK, client_id FK, amount, payment_date, mode (cash/upi/bank/cheque/other), reference, notes, created_at

**expenses** — business expenses
- id, date, description, category (rent/utilities/supplies/travel/food/salary/other), amount, vendor, receipt_path, ocr_raw (JSON string), notes, created_at

**quotations** — quotes before invoice
- id, quotation_number (unique), client_id FK, issue_date, valid_until, subtotal, tax_rate, tax_amount, total, status (draft/sent/accepted/rejected), notes, pdf_path, created_at

**quotation_items**
- id, quotation_id FK, description, quantity, unit_price, amount

**reminders** — payment reminders sent
- id, invoice_id FK, client_id FK, sent_at, channel (telegram/whatsapp/sms), message_text

**udhaar** — informal credit tracking (separate from invoices)
- id, person_name, phone, amount, direction (given/received), date, notes, settled (bool), settled_at, created_at

### Task 4.2 — Write hermes/db.py
Write all database operation functions. Group by domain:

**Setup & Init**
- `init_db(db_path)` — creates DB file, runs schema.sql, returns connection
- `get_conn(db_path)` — returns a connection with row_factory = sqlite3.Row
- `update_business(**kwargs)` — upsert business settings row
- `get_business(db_path)` — returns business settings dict

**Client Operations**
- `create_client(db_path, name, phone, email, address, gstin, notes)` → client_id
- `get_client(db_path, client_id)` → dict
- `find_client(db_path, query)` → list (fuzzy search by name/phone)
- `list_clients(db_path)` → list
- `update_client(db_path, client_id, **kwargs)` → updated dict

**Invoice Operations**
- `next_invoice_number(db_path)` → string e.g. "INV-0042"
- `create_invoice(db_path, client_id, items, due_date, tax_rate, notes)` → invoice_id
- `get_invoice(db_path, invoice_id)` → dict with items and client
- `get_invoice_by_number(db_path, invoice_number)` → dict
- `list_invoices(db_path, status=None, client_id=None, limit=20)` → list
- `update_invoice_status(db_path, invoice_id, status)` → updated dict
- `set_invoice_pdf_path(db_path, invoice_id, pdf_path)`
- `get_overdue_invoices(db_path)` → list
- `get_due_soon_invoices(db_path, days=3)` → list
- `get_outstanding_balance(db_path, client_id=None)` → amount float

**Payment Operations**
- `record_payment(db_path, invoice_id, amount, payment_date, mode, reference, notes)` → payment_id
- `get_payments_for_invoice(db_path, invoice_id)` → list
- `get_invoice_paid_total(db_path, invoice_id)` → float
- `auto_update_invoice_status_after_payment(db_path, invoice_id)` — marks paid if fully paid, else keeps sent

**Expense Operations**
- `log_expense(db_path, date, description, category, amount, vendor, receipt_path, ocr_raw, notes)` → expense_id
- `get_expense(db_path, expense_id)` → dict
- `list_expenses(db_path, category=None, from_date=None, to_date=None)` → list
- `get_expense_total_by_category(db_path, from_date, to_date)` → dict {category: total}

**Quotation Operations**
- `next_quotation_number(db_path)` → string e.g. "QT-0012"
- `create_quotation(db_path, client_id, items, valid_until, tax_rate, notes)` → quotation_id
- `get_quotation(db_path, quotation_id)` → dict with items and client
- `convert_quotation_to_invoice(db_path, quotation_id)` → invoice_id (copies items)
- `update_quotation_status(db_path, quotation_id, status)`

**Udhaar Operations**
- `add_udhaar(db_path, person_name, phone, amount, direction, notes)` → udhaar_id
- `settle_udhaar(db_path, udhaar_id)` → updated dict
- `list_udhaar(db_path, settled=False)` → list
- `get_udhaar_balance(db_path, person_name)` → net balance float

**Report Queries**
- `get_pl_summary(db_path, from_date, to_date)` → dict with revenue, expenses, net
- `get_revenue_by_month(db_path, year)` → list of {month, revenue}
- `get_outstanding_report(db_path)` → list of {client, invoices, total_outstanding}
- `get_gst_report(db_path, from_date, to_date)` → dict with taxable amounts, GST collected
- `get_mtd_summary(db_path)` → quick dict for morning briefing

**Reminder Operations**
- `log_reminder(db_path, invoice_id, client_id, message_text)` → reminder_id
- `get_reminders_for_invoice(db_path, invoice_id)` → list

### Task 4.3 — Test db.py independently
- Write a `tests/test_db.py` file
- Use a temporary in-memory SQLite DB for each test
- Test: create client, create invoice with items, record payment, auto-status update, overdue queries, MTD summary, udhaar settle flow

---

## PHASE 5 — SOUL.md & Config Template

**Goal:** Write HERMES personality. Write config.json template format.

### Task 5.1 — Write workspace/SOUL.md
This file is the agent's system prompt personality. It has `{{VARS}}` that provision.sh fills at onboarding.

Content must cover:
- Identity: "You are HERMES, the financial assistant for {{BUSINESS_NAME}}, owned by {{OWNER_NAME}}."
- Language rule: Always respond in Hinglish. Short, warm, confident. Never robotic.
- Context: You help with invoices, payments, expenses, quotations, reports, reminders, bookkeeping.
- Tone examples: "Invoice ban gayi bhai, yeh lo PDF", "Raj ka ₹5000 receive ho gaya, entry ho gayi."
- Business details section: GSTIN: {{GSTIN}}, Address: {{ADDRESS}}, Phone: {{PHONE}}
- Tool use rule: Always use tools to read/write data. Never guess numbers from memory.
- Privacy rule: Only discuss this business's data. Do not help with other topics.
- Error handling: If a tool fails, say so clearly in Hinglish and ask user to retry.
- Morning briefing format: When running briefing, always cover: overdue invoices, today due, due in 3 days, yesterday's payments, MTD revenue vs expenses.

### Task 5.2 — Document config.json format
Write a `docs/config-format.md` showing the exact config.json structure for a HERMES customer:
- providers block: openrouter API key, model selection (claude-3-haiku default)
- agents block: workspace path, maxToolIterations: 20
- channels block: telegram token, allowFrom user IDs
- No MCP block needed (tools are native)

### Task 5.3 — Confirm nanobot loads workspace correctly
- Create a test customer directory locally with a config.json
- Point workspace to your workspace/ template
- Run `nanobot gateway --config test_customer/config.json`
- Confirm SOUL.md is loaded into the system prompt (check logs)
- Confirm skills/ directory is scanned and SKILL.md files are found

---

## PHASE 6 — Native Tool Registration

**Goal:** Wire HERMES Python functions into nanobot's agent loop as first-class tools.

### Task 6.1 — Understand nanobot's Tool base class
Read `nanobot/agent/tools/base.py` carefully. Note:
- `Tool` is an abstract base class
- Subclasses must implement: `name` (property), `description` (property), `parameters` (property, JSON Schema), `execute(**kwargs)` (async method)
- `parameters` must be a valid JSON Schema object describing the tool's inputs
- `execute` must return a string (the tool result the LLM sees)

### Task 6.2 — Understand registry.py
Read `nanobot/agent/tools/registry.py`. Note:
- How tools are instantiated and registered
- Where to add HERMES tools so they are always loaded
- The registry is initialized during `nanobot gateway` startup

### Task 6.3 — Create nanobot/agent/tools/hermes_tools.py
Create this file. It imports from `hermes/` and defines one `Tool` subclass per HERMES function.

Tools to define (one class each):
- `DbCreateInvoiceTool` — wraps `hermes.db.create_invoice`
- `DbGetInvoiceTool` — wraps `hermes.db.get_invoice_by_number`
- `DbListInvoicesTool` — wraps `hermes.db.list_invoices`
- `DbUpdateInvoiceStatusTool` — wraps `hermes.db.update_invoice_status`
- `DbRecordPaymentTool` — wraps `hermes.db.record_payment`
- `DbGetOutstandingTool` — wraps `hermes.db.get_outstanding_balance`
- `DbGetOverdueTool` — wraps `hermes.db.get_overdue_invoices`
- `DbGetDueSoonTool` — wraps `hermes.db.get_due_soon_invoices`
- `DbLogExpenseTool` — wraps `hermes.db.log_expense`
- `DbListExpensesTool` — wraps `hermes.db.list_expenses`
- `DbCreateClientTool` — wraps `hermes.db.create_client`
- `DbFindClientTool` — wraps `hermes.db.find_client`
- `DbUpdateClientTool` — wraps `hermes.db.update_client`
- `DbCreateQuotationTool` — wraps `hermes.db.create_quotation`
- `DbConvertQuotationTool` — wraps `hermes.db.convert_quotation_to_invoice`
- `DbAddUdhaarTool` — wraps `hermes.db.add_udhaar`
- `DbSettleUdhaarTool` — wraps `hermes.db.settle_udhaar`
- `DbListUdhaarTool` — wraps `hermes.db.list_udhaar`
- `DbGetMtdSummaryTool` — wraps `hermes.db.get_mtd_summary`
- `DbGetPlSummaryTool` — wraps `hermes.db.get_pl_summary`
- `DbGetOutstandingReportTool` — wraps `hermes.db.get_outstanding_report`
- `DbGetGstReportTool` — wraps `hermes.db.get_gst_report`
- `DbLogReminderTool` — wraps `hermes.db.log_reminder`
- `PdfGenerateInvoiceTool` — wraps `hermes.pdf.generate_invoice_pdf`
- `PdfGenerateReceiptTool` — wraps `hermes.pdf.generate_receipt_pdf`
- `PdfGenerateQuotationTool` — wraps `hermes.pdf.generate_quotation_pdf`
- `PdfGeneratePlReportTool` — wraps `hermes.pdf.generate_pl_report_pdf`
- `PdfGenerateOutstandingReportTool` — wraps `hermes.pdf.generate_outstanding_report_pdf`
- `PdfGenerateExpenseReportTool` — wraps `hermes.pdf.generate_expense_report_pdf`
- `PdfGenerateGstReportTool` — wraps `hermes.pdf.generate_gst_report_pdf`
- `OcrExtractReceiptTool` — wraps `hermes.ocr.extract_receipt`
- `TranscribeAudioTool` — wraps `hermes.whisper_tool.transcribe`
- `ExportCaBundleTool` — wraps `hermes.export.create_ca_bundle`
- `DbGetBusinessInfoTool` — wraps `hermes.db.get_business`
- `DbUpdateBusinessInfoTool` — wraps `hermes.db.update_business`

Each tool's `execute` method reads `DB_PATH` and `CUSTOMER_DATA_DIR` from environment variables (set in config.json per-customer via `env` block or from the gateway's environment).

### Task 6.4 — Modify registry.py to load hermes_tools.py
- Import all HERMES tool classes from `hermes_tools.py`
- Register them in the tool list during registry initialization
- They should appear in the agent's available tools list

### Task 6.5 — Verify tools are visible to the agent
- Start a test gateway
- Send a test message
- Check logs: LLM should see HERMES tool names in its context
- Call one tool manually via a test message: "What's the MTD summary?" — should call DbGetMtdSummaryTool

---

## PHASE 7 — PDF Generator

**Goal:** Generate professional PDFs for invoices, receipts, quotations, and all reports.

### Task 7.1 — Write hermes/pdf.py
Functions:

**`generate_invoice_pdf(invoice_dict, business_dict, output_path)`**
- Loads `templates/invoice.html` with Jinja2
- Renders with invoice data + business data
- Runs WeasyPrint to output PDF at `output_path`
- Returns output_path on success

**`generate_receipt_pdf(payment_dict, invoice_dict, business_dict, output_path)`**
- Same pattern using `templates/receipt.html`

**`generate_quotation_pdf(quotation_dict, business_dict, output_path)`**
- Uses `templates/quotation.html`

**`generate_pl_report_pdf(pl_data, business_dict, from_date, to_date, output_path)`**
- Uses `templates/report_pl.html`

**`generate_outstanding_report_pdf(outstanding_data, business_dict, output_path)`**
- Uses `templates/report_outstanding.html`

**`generate_expense_report_pdf(expense_data, business_dict, from_date, to_date, output_path)`**
- Uses `templates/report_expenses.html`

**`generate_gst_report_pdf(gst_data, business_dict, from_date, to_date, output_path)`**
- Uses `templates/report_gst.html`

### Task 7.2 — Write Jinja2 HTML templates
For each template, design a clean, professional Indian business document:

**templates/invoice.html** must include:
- Business name, logo placeholder, address, GSTIN, phone, email, UPI ID
- Invoice number, date, due date
- Client name, address, GSTIN
- Line items table: description, qty, rate, amount
- Subtotal, GST percentage, GST amount, Grand Total
- Payment terms / notes section
- Bank details for payment (account number, IFSC, UPI)
- "Thank you for your business" footer
- Watermark: PAID (in green, rotated 45°) if status is paid

**templates/receipt.html** must include:
- Business details
- Receipt number, date
- Client name
- Against Invoice # X
- Amount received: ₹XXXX
- Payment mode (Cash/UPI/Bank)
- Reference/UTR number
- Authorized signature placeholder

**templates/quotation.html** — similar to invoice, header says "QUOTATION", shows valid-until date, no payment terms

**templates/report_pl.html** must include:
- Period header
- Revenue section: total invoiced, total collected, outstanding
- Expense section: by category, total expenses
- Net Profit/Loss (large, highlighted)
- Month-by-month breakdown table if available

**templates/report_outstanding.html** must include:
- Per-client section: client name, list of outstanding invoices with days overdue, total outstanding
- Grand total outstanding

**templates/report_expenses.html** must include:
- Date range header
- Expense list table: date, description, vendor, category, amount
- Category summary: pie-style text breakdown
- Total expenses

**templates/report_gst.html** must include:
- Period header
- GSTIN of business
- Taxable turnover, GST rate, CGST collected, SGST collected, total GST liability
- Invoice-wise detail table (for GST-3B filing reference)

### Task 7.3 — Test PDF generation
- Call each function with mock data
- Open the generated PDFs and visually verify: layout, fonts, Indian rupee symbol (₹), correct data placement
- Test WeasyPrint has all system fonts and pango libraries installed

---

## PHASE 8 — OCR Tool

**Goal:** Extract expense data from receipt photos using a vision LLM.

### Task 8.1 — Write hermes/ocr.py
Function: **`extract_receipt(image_path, openrouter_api_key, ocr_model)`**

Steps inside the function:
1. Open image with Pillow, resize to max 1024px on longest side (reduce API cost)
2. Save resized to a temp file
3. Encode to base64
4. Call OpenRouter vision LLM (e.g. `google/gemini-flash-1.5`) with the image
5. Prompt: "Extract from this receipt: vendor name, date, total amount, line items if visible, and expense category (rent/utilities/supplies/travel/food/salary/other). Return ONLY valid JSON with keys: vendor, date, amount, items, category, confidence (0-1)."
6. Parse JSON response
7. Return dict: `{vendor, date, amount, items, category, confidence, raw_response}`

Error handling:
- If image not found: return error dict
- If vision LLM call fails: return error dict with `success: False`
- If JSON parsing fails: return raw text in `raw_response`, `success: False`
- Always return a dict, never raise exceptions to the tool caller

### Task 8.2 — Test OCR pipeline
- Use a sample receipt image (any grocery receipt photo)
- Call extract_receipt directly in a test script
- Verify returned dict has all expected keys
- Verify amounts are reasonable (sanity check, not exact)

---

## PHASE 9 — Voice Transcription Tool

**Goal:** Transcribe Telegram voice messages to text for expense/invoice dictation.

### Task 9.1 — Write hermes/whisper_tool.py
Function: **`transcribe(audio_path, model_size="small", language="hi")`**

Steps:
1. Confirm ffmpeg is installed (subprocess check)
2. Convert audio to WAV if not already (ffmpeg subprocess call)
3. Load Whisper model (cache after first load — use module-level dict `_model_cache`)
4. Run `model.transcribe(wav_path, language=language)`
5. Return dict: `{text, language, duration_seconds, success}`

Model caching: load once per process, reuse. Model size `small` is ~460MB, handles Hindi+English well.

Language detection: pass `language=None` to let Whisper auto-detect, then return detected language. This handles Hinglish naturally.

### Task 9.2 — Test voice transcription
- Record a 5-second voice note on your phone (say an expense in Hinglish)
- Run transcribe on the .ogg or .m4a file Telegram would send
- Verify transcription is legible (not perfect, good enough)

---

## PHASE 10 — Export Tool

**Goal:** Generate a CA export bundle (quarterly financial ZIP) for the customer's chartered accountant.

### Task 10.1 — Write hermes/export.py
Function: **`create_ca_bundle(db_path, customer_data_dir, from_date, to_date, output_path)`**

Steps:
1. Query: all invoices in period (with items, client info)
2. Query: all payments in period
3. Query: all expenses in period (with receipt paths)
4. Generate: P&L report PDF for the period
5. Generate: GST report PDF for the period
6. Generate: Outstanding balance report PDF (as of to_date)
7. Collect: all invoice PDFs whose issue_date is in period
8. Collect: all expense receipt images in period
9. Create a ZIP file at output_path containing:
   - `summary/pl_report.pdf`
   - `summary/gst_report.pdf`
   - `summary/outstanding.pdf`
   - `invoices/INV-001.pdf`, `invoices/INV-002.pdf` ...
   - `expenses/receipts/expense_001.jpg` ...
   - `data/invoices.csv` (CSV export of invoice table)
   - `data/payments.csv`
   - `data/expenses.csv`
   - `README.txt` explaining folder structure
10. Return output_path on success

Helper: **`export_table_to_csv(db_path, table, from_date, to_date)`** — simple CSV export

---

## PHASE 11 — 22 SKILL.md Files

**Goal:** Extract your existing SKILL.md files from the zip and verify they work with native tools.

### Task 11.1 — Extract skills from zip
- Unzip your skills archive into `workspace/skills/`
- Confirm 22 skill folders each with SKILL.md:
  invoice-create, invoice-retrieve, invoice-send, payment-record, payment-partial,
  expense-log, expense-ocr, reminder-check, reminder-draft, report-pl,
  report-outstanding, report-expenses, report-gst, report-ca-export,
  client-manage, bookkeeping-query, briefing-morning, udhaar-track,
  quotation-create, receipt-generate, message-draft, settings-manage

### Task 11.2 — Audit each SKILL.md for MCP references
- Search all SKILL.md files for references to `hermes-mcp` or MCP tool names
- Update any tool call examples to use the native tool names defined in `hermes_tools.py`
- This is a find-and-replace pass, no content rewriting needed

### Task 11.3 — Verify skill routing
- Start a test gateway with the full workspace/skills/ directory
- Send routing test messages — one per skill:
  - "Ek invoice banao" → should route to invoice-create
  - "Aaj ke expenses kya hain" → should route to expense-log or bookkeeping-query
  - "P&L report chahiye is mahine ka" → should route to report-pl
- Check logs to confirm the correct SKILL.md was loaded into context
- Adjust SKILL.md trigger phrases if routing is wrong

### Task 11.4 — Symlink setup for per-customer deployment
- Document that per-customer, `skills/` directory will be symlinked to `workspace/skills/`
- This means all customers always get the latest skills automatically after a git pull + pm2 restart
- Confirm symlink works: `ls -la /home/hermes/customers/c001/workspace/skills/`

---

## PHASE 12 — Invoice Tools End-to-End

**Goal:** Full invoice flow working via Telegram.

### Task 12.1 — Subtask: Create invoice
- Send: "Raj ke liye invoice banao ₹5000 web development ke liye, due date 15 din baad"
- Agent should: call DbFindClientTool (or DbCreateClientTool if not found), call DbCreateInvoiceTool, call PdfGenerateInvoiceTool, call nanobot's file-send tool to send PDF in Telegram
- Verify: invoice created in DB, PDF generated at correct path, PDF received in Telegram

### Task 12.2 — Subtask: Retrieve invoice
- Send: "INV-0001 ka status kya hai?"
- Agent should: call DbGetInvoiceTool, return status, amount, due date in Hinglish

### Task 12.3 — Subtask: Send invoice reminder
- Send: "Raj ko invoice reminder bhejo"
- Agent should: call DbFindClientTool, call DbListInvoicesTool (unpaid for client), call DbLogReminderTool, draft reminder message in Hinglish, confirm with user before sending

### Task 12.4 — Subtask: Edge cases
- Create invoice for a new client (not in DB) — should auto-create client
- Create invoice with GST — verify GST calculated correctly
- Create invoice with multiple line items: "3 cheezein hain: Design ₹2000, Dev ₹5000, Hosting ₹500"

---

## PHASE 13 — Payment & Bookkeeping

**Goal:** Record payments, partial payments, query ledger.

### Task 13.1 — Record full payment
- Send: "Raj ne ₹5000 UPI se bheja INV-0001 ke liye"
- Agent should: call DbFindClientTool, call DbGetInvoiceTool, call DbRecordPaymentTool, call auto_update_invoice_status, confirm in Hinglish: "Entry ho gayi! Invoice paid mark ho gaya."

### Task 13.2 — Record partial payment
- Invoice of ₹10000, payment of ₹6000 received
- Agent should: record payment, note that ₹4000 still outstanding, keep invoice status as "sent" (not paid)

### Task 13.3 — Bookkeeping queries
- "Raj ka total outstanding kya hai?" → DbGetOutstandingTool filtered by client
- "Is mahine kitna aaya?" → DbGetMtdSummaryTool
- "Kon se invoices overdue hain?" → DbGetOverdueTool

### Task 13.4 — Payment receipt generation
- After recording payment, agent should offer/auto-generate receipt PDF
- Send receipt PDF in Telegram as confirmation

---

## PHASE 14 — Expense & OCR Pipeline

**Goal:** Log expenses by text and by photo receipt.

### Task 14.1 — Text expense logging
- Send: "Aaj office supplies pe ₹450 kharch kiye Sharma Stationery se"
- Agent should: call DbLogExpenseTool with parsed data, confirm in Hinglish

### Task 14.2 — Photo receipt OCR pipeline
- Send a receipt photo via Telegram
- nanobot receives it as base64 in context (already handled by `context.py`)
- Agent saves image to `expenses/originals/`
- Agent calls OcrExtractReceiptTool with image path
- Agent shows extracted data to user: "Kya yeh sahi hai? Vendor: ABC Mart, Amount: ₹234, Category: Food"
- User confirms ("haan sahi hai" or "nahi, amount ₹243 hai")
- Agent calls DbLogExpenseTool with confirmed data

### Task 14.3 — Voice expense logging
- Send a voice note: "Aaj petrol bhara ₹500, travel expense hai"
- nanobot's context.py gives audio file path
- Agent calls TranscribeAudioTool
- Agent parses transcription for expense details
- Agent calls DbLogExpenseTool
- Agent confirms in Hinglish

---

## PHASE 15 — Quotation, Receipt, Udhaar

**Goal:** Three remaining skill groups working E2E.

### Task 15.1 — Quotation flow
- "Raj ke liye quotation banao website ke liye ₹15000, valid 7 din"
- Agent creates quotation, generates PDF, sends via Telegram
- "Raj ne quotation accept kar liya, invoice banao"
- Agent calls DbConvertQuotationTool — converts quotation to invoice automatically (items copied)

### Task 15.2 — Receipt generation
- After any payment, "receipt chahiye"
- Agent calls PdfGenerateReceiptTool, sends PDF
- Receipt has unique receipt number, payment mode, reference

### Task 15.3 — Udhaar tracking
- "Ramesh ko ₹2000 udhaar diya hai"
- Agent calls DbAddUdhaarTool with direction=given
- "Ramesh ne ₹2000 wapas kar diya"
- Agent calls DbSettleUdhaarTool
- "Mera total udhaar kya hai?"
- Agent calls DbListUdhaarTool, summarizes in Hinglish

---

## PHASE 16 — Reminder + Cron Wakeup

**Goal:** Automated morning briefing and manual reminder drafting.

### Task 16.1 — Morning briefing cron
- Configure via nanobot cron: `nanobot cron add --name "morning-briefing" --cron "0 8 * * *" --message "Run morning briefing now"`
- briefing-morning SKILL.md tells agent what to do: call DbGetMtdSummaryTool, DbGetOverdueTool, DbGetDueSoonTool, then compose and send a structured Hinglish briefing
- Verify briefing fires at 8 AM and is sent to the customer's Telegram

### Task 16.2 — Briefing format
The morning briefing must follow this structure (as defined in briefing-morning/SKILL.md):
```
🌅 Good Morning, [Name]!

📋 OVERDUE (X invoices)
→ [Client], INV-XXX — ₹XXXX — X days overdue

📅 DUE TODAY (X invoices)
→ [Client], INV-XXX — ₹XXXX

⏰ DUE IN 3 DAYS
→ ...

💰 YESTERDAY'S COLLECTIONS
→ ₹XXXX received from [clients]

📊 THIS MONTH SO FAR
→ Invoiced: ₹XXXX | Collected: ₹XXXX | Expenses: ₹XXXX
```

### Task 16.3 — Manual reminder drafting
- "Raj ko payment reminder bhejo"
- reminder-draft SKILL.md: agent fetches outstanding invoices for Raj, drafts a polite Hinglish WhatsApp-style reminder message, shows it to user for approval before logging
- message-draft SKILL.md: generic message drafting for any client communication

---

## PHASE 17 — All Report Tools

**Goal:** All 5 report types generating accurate PDFs.

### Task 17.1 — P&L Report
- "Is mahine ka P&L report chahiye"
- Agent calls DbGetPlSummaryTool (current month), calls PdfGeneratePlReportTool, sends PDF
- Test with actual DB data (created in earlier phases)

### Task 17.2 — Outstanding Report
- "Outstanding dues ki list chahiye"
- Agent calls DbGetOutstandingReportTool, calls PdfGenerateOutstandingReportTool
- PDF should list clients with outstanding amounts and days overdue

### Task 17.3 — Expense Report
- "Pichhle 30 din ke expenses ka report"
- Agent calls DbListExpensesTool, calls PdfGenerateExpenseReportTool

### Task 17.4 — GST Report
- "GST report banao Q4 ka"
- Agent parses quarter dates, calls DbGetGstReportTool, calls PdfGenerateGstReportTool
- Verify: CGST + SGST calculated correctly per invoice

### Task 17.5 — CA Export Bundle
- "CA ke liye export banao last quarter ka"
- Agent calls ExportCaBundleTool with quarter date range
- ZIP file generated with all PDFs + CSVs
- ZIP sent or download link provided in Telegram

---

## PHASE 18 — Webapp Foundation

**Goal:** FastAPI application running, auth working, database access layer ready.

### Task 18.1 — webapp/database.py
Write the read layer for the webapp. This is separate from `hermes/db.py` (which is for the agent). The webapp reads the same SQLite DB but has its own connection management.

Functions:
- `get_db(db_path)` — returns a read-only connection (using `uri=True` with `?mode=ro`)
- `get_business(db_path)` → dict
- `get_dashboard_kpis(db_path)` → dict with: revenue_mtd, collected_mtd, outstanding_total, expenses_mtd, active_clients_count, overdue_count
- `get_recent_activity(db_path, limit=10)` → list of recent transactions (invoices + payments mixed, sorted by date)
- `get_invoices(db_path, status=None, client_id=None, search=None, page=1, per_page=20)` → {items, total, pages}
- `get_invoice_detail(db_path, invoice_id)` → full invoice dict with items + payments + client
- `get_clients(db_path, search=None)` → list
- `get_client_detail(db_path, client_id)` → client dict with invoice history + payment history + totals
- `get_expenses(db_path, category=None, from_date=None, to_date=None, page=1, per_page=20)` → {items, total, pages}
- `get_expense_category_summary(db_path, from_date, to_date)` → list of {category, total, count}
- `get_files_listing(customer_data_dir)` → dict of {invoices: [], reports: [], exports: []} with file names + sizes + dates
- `get_settings(db_path)` → business settings dict

### Task 18.2 — webapp/auth.py
- `hash_password(plain)` → bcrypt hash string
- `verify_password(plain, hashed)` → bool
- `create_access_token(data, expires_delta)` → JWT string (HS256)
- `decode_access_token(token)` → payload dict or None
- FastAPI dependency: `get_current_user(request)` — reads JWT from cookie, raises 401 if invalid

### Task 18.3 — webapp/main.py
- FastAPI app initialization
- Mount `/static` to `webapp/static/`
- Mount Jinja2 templates from `webapp/templates/`
- Include all routers
- Login POST endpoint: verifies password against `business.web_password_hash`, sets JWT cookie, redirects to dashboard
- Logout GET endpoint: clears cookie, redirects to login

### Task 18.4 — Environment configuration
The webapp reads from a `.env` file per customer at `customers/c001/webapp/.env`:
- `DB_PATH` — absolute path to `hermes.db`
- `CUSTOMER_DATA_DIR` — absolute path to customer directory
- `JWT_SECRET` — random 64-char hex string (generated at provision time)
- `PORT` — port this uvicorn instance listens on (e.g. 5001 for c001, 5002 for c002)
- `BUSINESS_NAME` — for display in the webapp

### Task 18.5 — Verify auth works
- Start webapp: `uvicorn webapp.main:app --port 5001`
- Hit `http://localhost:5001/` — should redirect to `/login`
- POST login with correct password — should redirect to `/dashboard`
- POST login with wrong password — should show error
- Hit `/dashboard` with no cookie — should redirect to `/login`

---

## PHASE 19 — Webapp: Dashboard & Invoices

**Goal:** The two most important screens are fully functional.

### DASHBOARD PAGE (`/dashboard`)

**Layout:** Full-width, single-column on mobile, 2-column on tablet+

**Section 1 — KPI Cards (top row, 4 cards)**
Each card has: icon, label, large number, small subtitle

- Card 1: 💰 Revenue MTD — ₹XX,XXX — "Total invoiced this month"
- Card 2: ✅ Collected MTD — ₹XX,XXX — "Payments received this month"
- Card 3: 🕐 Outstanding — ₹XX,XXX — "Unpaid across all clients"
- Card 4: 📉 Expenses MTD — ₹XX,XXX — "Logged this month"

Card colors: Revenue=green, Collected=blue, Outstanding=orange, Expenses=red

**Section 2 — Alert Banner (conditional)**
- Shown only if there are overdue invoices
- Red/orange banner: "⚠️ X invoices are overdue — total ₹XX,XXX" with a "View →" link to invoices filtered by overdue

**Section 3 — Quick Actions (icon buttons)**
- "New Invoice" — links to invoices page (note: invoice creation happens via Telegram/agent, this just links to the list)
- "View Reports" — links to reports page
- "Download CA Export" — triggers report generation or links to files page
- "View Outstanding" — links to invoices filtered by outstanding

**Section 4 — Recent Activity Feed**
- Timeline-style list of last 10 events
- Each item: icon + description + amount + time ago
- Invoice created: "📄 INV-0012 created for Raj Enterprises — ₹8,500 · 2 hours ago"
- Payment received: "💵 Payment of ₹5,000 from Raj Enterprises · Yesterday"
- Expense logged: "🧾 Office Supplies — ₹450 · 3 days ago"
- Items are clickable, link to the relevant detail page

**Section 5 — This Month Summary (bottom)**
- Simple text stats: "X invoices raised · X paid · X pending · X overdue"
- "Net this month: ₹XX,XXX collected - ₹XX,XXX expenses = ₹XX,XXX profit"

### INVOICES PAGE (`/invoices`)

**Layout:** Filter bar on top, table below

**Filter Bar:**
- Status dropdown: All / Draft / Sent / Paid / Overdue / Cancelled
- Client search: text input (filters by client name)
- Date range: From date + To date (date pickers)
- "Apply Filters" button | "Clear" link

**Invoices Table columns:**
- Invoice # (bold, clickable → invoice detail)
- Client Name
- Issue Date
- Due Date (red if overdue)
- Amount (₹XX,XXX)
- Status (colored pill badge: green=paid, orange=sent, red=overdue, gray=draft)
- Actions: [Download PDF] [Mark Paid] (for sent/overdue) [Send Reminder] (for overdue)

**Table footer:**
- Showing X–Y of Z invoices
- Pagination: Prev · 1 · 2 · 3 · Next

**Summary bar above table:**
- "Showing X invoices · Total: ₹XX,XXX · Paid: ₹XX,XXX · Outstanding: ₹XX,XXX"

### INVOICE DETAIL PAGE (`/invoices/{id}`)

**Header:**
- Invoice number (large), Status badge, Client name
- "Download PDF" button | "Back to Invoices" link

**Invoice Info block:**
- Issue date, Due date, Client address/GSTIN

**Line Items table:**
- Description | Qty | Rate | Amount
- Subtotal, GST %, GST Amount, Grand Total rows

**Payment History block:**
- Table: Date | Amount | Mode | Reference
- "Amount Paid: ₹X,XXX | Balance: ₹X,XXX"

**Notes section:**
- Invoice notes if any

---

## PHASE 20 — Webapp: Clients & Expenses

### CLIENTS PAGE (`/clients`)

**Layout:** Search bar + client cards grid

**Search bar:** Live search by name or phone

**Client cards (grid, 2-3 per row):**
Each card shows:
- Client name (bold)
- Phone number
- Outstanding balance (red if > 0, green if zero)
- "X invoices · Last invoice: DD Mon YYYY"
- Click → client detail page

### CLIENT DETAIL PAGE (`/clients/{id}`)

**Header:** Client name, phone, email, address, GSTIN, notes

**Stats row:**
- Total Billed | Total Paid | Outstanding | Last Payment Date

**Invoice History tab:**
- Table of all invoices for this client (same columns as invoices page)

**Payment History tab:**
- Table: Date | Invoice | Amount | Mode | Reference

### EXPENSES PAGE (`/expenses`)

**Layout:** Filter bar + summary + table

**Filter bar:**
- Category dropdown: All / Rent / Utilities / Supplies / Travel / Food / Salary / Other
- Date range pickers
- "Apply" button

**Category Summary (colored stat row):**
- One pill per category showing total: "Rent ₹12,000 · Supplies ₹3,450 · Travel ₹1,200"

**Expenses Table:**
- Date | Description | Vendor | Category (colored pill) | Amount | Receipt
- Receipt column: thumbnail image (clickable → opens full image in lightbox) or "No Receipt" text
- Actions: [View Receipt] if receipt exists

**Lightbox for receipts:**
- Clicking a receipt thumbnail opens a modal with the full-size image
- X button to close
- "Download" link below image

**Pagination:**
- Same as invoices page

---

## PHASE 21 — Webapp: Reports & Files

### REPORTS PAGE (`/reports`)

**Layout:** Six report cards in a grid

**Report Card structure (for each report):**
- Icon + Title
- Short description of what the report contains
- Date range selector (month picker or from/to date pickers)
- "Generate PDF" button
- "Download Last Generated" link (if a recent one exists) — shows "Generated: DD Mon YYYY HH:MM"

**Six report cards:**

1. **P&L Report** 📊
   - Description: "Revenue, expenses, and net profit for a period"
   - Date picker: month/year selector (defaults to current month)
   - On generate: calls backend endpoint which calls `hermes.pdf.generate_pl_report_pdf` and returns the PDF

2. **Outstanding Invoices** 🕐
   - Description: "All unpaid invoices grouped by client"
   - No date range needed (always current outstanding)
   - One button: "Generate PDF"

3. **Expense Report** 🧾
   - Description: "All expenses with category breakdown"
   - Date range picker

4. **GST Report** 📋
   - Description: "Taxable turnover and GST collected — for GST-3B filing"
   - Quarter selector: Q1/Q2/Q3/Q4 + year

5. **CA Export Bundle** 📦
   - Description: "Complete quarterly ZIP for your chartered accountant — invoices, receipts, reports, and CSVs"
   - Quarter selector
   - "Generate Bundle" button (shows progress spinner — takes a few seconds)
   - When done: "Download ZIP" button appears

6. **Monthly Summary** 📅
   - Description: "Quick revenue vs expense summary per month"
   - Year selector
   - Generates a simple table-format PDF

**Backend for report generation:**
- Each "Generate" button POSTs to a FastAPI endpoint
- Endpoint calls the relevant `hermes.pdf` function (using the customer's DB and data dir from env)
- Saves PDF to `customers/c001/reports/`
- Returns a download URL
- Frontend JS redirects to the download URL

### FILES PAGE (`/files`)

**Layout:** Three folder sections

**Section 1 — Invoices/**
- List of PDF files with name, size, date created
- Each row has a "Download" link
- Sorted by date desc, most recent first
- Shows last 50 files

**Section 2 — Reports/**
- Same as above for generated reports

**Section 3 — CA Exports/**
- ZIP files for CA export bundles
- Shows date range in filename and file size

**Implementation:**
- Reads file listing from filesystem (not DB)
- Files are served via nginx directly (secure, no Python overhead)
- FastAPI just renders the listing page
- Download links point to nginx `/files/` route (proxied securely)

---

## PHASE 22 — Webapp: Settings

### SETTINGS PAGE (`/settings`)

**Layout:** Tabbed sections or accordion sections

**Section 1 — Business Information**
Form fields (pre-filled from DB):
- Business Name
- Owner Name
- Address (multiline)
- City, State, PIN (three fields in a row)
- GSTIN
- Phone
- Email

"Save Changes" button — POSTs to `/settings/business`, updates DB via `hermes.db.update_business`

**Section 2 — Bank & Payment Details**
Form fields:
- Bank Name
- Account Number
- IFSC Code
- UPI ID (e.g. business@upi)

"Save Changes" button

**Section 3 — Change Password**
Form fields:
- Current Password
- New Password
- Confirm New Password

Validation: new password ≥ 8 chars, passwords match
On success: re-hashes, updates `business.web_password_hash`, shows success toast

**Section 4 — Telegram Integration (read-only display)**
- Bot Token: `••••••••••••••••••••••1234` (last 4 chars visible, rest masked)
- Connected Telegram User ID: `123456789`
- Gateway Status: 🟢 Running (if PM2 process is alive) — checks via `ps aux` or PM2 API
- Note: "To change Telegram settings, contact your HERMES administrator"

**Section 5 — About**
- HERMES version string
- nanobot fork version
- Customer ID (e.g. c001)
- Setup date
- "Powered by HERMES" footer

---

## PHASE 23 — Full E2E Test on YOUR GVM

**Goal:** Before touching any customer's machine, deploy HERMES on your own GVM and run all 40+ scenarios yourself. This is your QA gate. Nothing ships to a customer until this passes clean.

**Your GVM is a throwaway test environment.** Spin up a fresh Ubuntu 22.04 VM in your own Google account. Run install.sh and provision.sh exactly as you will for a real customer. Treat your own test business as the customer. When all scenarios pass, tear it down or keep it as your staging environment. The customer gets a fresh VM.

### Task 23.1 — Agent test scenarios (via Telegram)
Run each of these manually and confirm correct behavior:

**Invoices (8 scenarios)**
1. Create invoice for new client → auto-creates client + invoice + PDF
2. Create invoice for existing client
3. Create invoice with multiple line items
4. Create invoice with 18% GST
5. Retrieve invoice by number
6. List all overdue invoices
7. Send payment reminder for overdue invoice
8. Cancel an invoice

**Payments (4 scenarios)**
9. Record full payment via UPI
10. Record partial payment → invoice stays "sent"
11. Record second payment that fully settles → auto-mark paid
12. Generate payment receipt PDF

**Expenses (5 scenarios)**
13. Log expense by text
14. Log expense by photo (test with actual receipt image)
15. Log expense by voice note
16. List expenses for current month
17. Filter expenses by category

**Quotations (3 scenarios)**
18. Create quotation for a client
19. Convert quotation to invoice
20. Mark quotation as rejected

**Udhaar (3 scenarios)**
21. Add given udhaar entry
22. Add received udhaar entry
23. Settle udhaar, check balance

**Reports (5 scenarios)**
24. Generate P&L for current month
25. Generate outstanding invoices report
26. Generate expense report for last 30 days
27. Generate GST report for current quarter
28. Generate CA export bundle for last quarter

**Cron & Briefing (2 scenarios)**
29. Trigger morning briefing manually: "Good morning briefing start karo"
30. Verify briefing format is correct (overdue, due today, due in 3 days, collections, MTD)

**Clients (3 scenarios)**
31. Create a new client
32. Update client's phone number
33. Query client's total outstanding

**Settings (2 scenarios)**
34. "Mera GSTIN update karo" → agent updates via DbUpdateBusinessInfoTool
35. "Business ka address kya hai?" → agent reads via DbGetBusinessInfoTool

**Edge cases (5 scenarios)**
36. Invoice for unknown client (auto-create or ask?)
37. Payment larger than invoice amount (handle gracefully)
38. OCR fails (bad image) → agent asks user to enter manually
39. Voice note in English only → still transcribes correctly
40. Send "kuch nahi karna" (irrelevant message) → agent responds gracefully, no tool calls

### Task 23.2 — Webapp test scenarios
Run these manually in a browser:

1. Login with correct password → dashboard loads
2. Login with wrong password → error shown, no redirect
3. Dashboard KPI cards show correct numbers (cross-check with DB)
4. Recent activity feed shows last 10 items correctly
5. Invoices page — filter by "Overdue" → only overdue invoices shown
6. Invoices page — search by client name → filtered correctly
7. Invoice detail → shows all items, payments, correct balance
8. Download PDF from invoice detail → PDF opens correctly
9. Clients page → search by phone number
10. Client detail → invoice history and payment history correct
11. Expenses page → filter by category
12. Receipt lightbox → opens, shows image, closes
13. Reports page → Generate P&L → PDF downloads
14. Reports page → Generate CA Export → ZIP downloads
15. Files page → invoices listed → download works
16. Settings → update business name → saves → refreshes with new name
17. Settings → change password → login with new password works
18. Logout → cookie cleared → redirect to login → can't access dashboard

---

## PHASE 24 — Deploy to Customer's GVM (Handover)

**Goal:** SSH into the customer's own Google VM (their account, their billing), run two scripts, hand over credentials, and walk away. After this, you do nothing. The customer runs everything.

**The deployment model:**
- Customer creates a GVM themselves (or you guide them to) — e2-medium, Ubuntu 22.04, 10GB disk is enough
- Customer pays for the VM directly to Google
- Customer has their own OpenRouter account and API key — they pay API costs directly
- Customer creates their own Telegram bot via @BotFather
- You SSH in once, run install.sh + onboard-tui.js, hand over the web dashboard URL and password, and leave
- After handover: zero involvement. No monthly maintenance. No support obligation (define this in your contract).

### Task 24.1 — Write scripts/install.sh
This script runs once on a fresh customer Ubuntu 22.04 VM. It sets up everything needed to run HERMES.

1. System update: `apt update && apt upgrade -y`
2. Install system dependencies:
   - `python3.11`, `python3.11-venv`, `python3.11-dev`
   - `ffmpeg` — for Whisper audio conversion
   - `libpango-1.0-0`, `libpangoft2-1.0-0`, `libharfbuzz0b`, `libffi-dev`, `libssl-dev` — for WeasyPrint
   - `nginx`
   - `certbot`, `python3-certbot-nginx`
   - `nodejs`, `npm` — for onboard-tui.js
   - `pm2` (via npm global)
3. Create system user `hermes` with home at `/home/hermes`
4. Create directories: `/home/hermes/app`, `/home/hermes/data`, `/home/hermes/backups`
5. Clone the hermes repo into `/home/hermes/app`
6. Create venv: `/home/hermes/app/.venv`
7. Install all Python deps: `pip install -e .`
8. Pre-download Whisper `small` model at install time (not at first runtime): `python -c "import whisper; whisper.load_model('small')"`
9. Set up PM2 to start on boot: `pm2 startup systemd -u hermes --hp /home/hermes`
10. Set permissions: `chown -R hermes:hermes /home/hermes`
11. Print success and instruct: "Run: node /home/hermes/app/scripts/onboard-tui.js"

### Task 24.2 — Write scripts/provision.sh
This script runs once, after install.sh. It sets up the single business on this VM.

Takes arguments: `BUSINESS_NAME`, `GSTIN`, `OWNER_NAME`, `ADDRESS`, `CITY`, `STATE`, `PIN`, `PHONE`, `BOT_TOKEN`, `TG_USER_ID`, `OR_KEY`, `DOMAIN`, `WEB_PASSWORD`

No `CUSTOMER_ID` argument — this is a single-customer VM. All data lives at `/home/hermes/data/`.

Steps:
1. Create data directory structure at `/home/hermes/data/` (db, invoices, expenses/originals, expenses/processed, reports, exports, uploads, logs, webapp)
2. Initialize SQLite DB: `python3 -c "from hermes.db import init_db; init_db('/home/hermes/data/db/hermes.db')"`
3. Set initial business info in DB (name, GSTIN, owner name, address, phone, etc.)
4. Hash and store web password: `update_business(web_password_hash=...)`
5. Fill SOUL.md from template — sed substitution of `{{BUSINESS_NAME}}`, `{{OWNER_NAME}}`, `{{GSTIN}}`, `{{ADDRESS}}`, `{{PHONE}}` into `/home/hermes/data/workspace/SOUL.md`
6. Symlink `workspace/skills/` → `/home/hermes/app/workspace/skills/`
7. Write `/home/hermes/data/config.json`:
   - providers: openrouter API key
   - agents: workspace = `/home/hermes/data/workspace`, maxToolIterations: 20
   - channels: telegram token + allowFrom TG_USER_ID
   - No MCP block (tools are native)
8. Write `/home/hermes/data/webapp/.env`: DB_PATH, CUSTOMER_DATA_DIR, JWT_SECRET (generated), PORT=5000
9. Start PM2 nanobot gateway: `pm2 start nanobot --name hermes-agent -- gateway --config /home/hermes/data/config.json`
10. Start PM2 webapp: `pm2 start uvicorn --name hermes-web -- webapp.main:app --host 127.0.0.1 --port 5000`
11. Add morning briefing cron: `nanobot --config /home/hermes/data/config.json cron add --name morning-briefing --message "Run morning briefing..." --cron "0 8 * * *"`
12. Write nginx config for `$DOMAIN` (single domain, not subdomain — this is one business):
    ```
    server {
      listen 443 ssl; server_name $DOMAIN;
      ssl_certificate ...
      location / { proxy_pass http://127.0.0.1:5000; }
      location /files/ { alias /home/hermes/data/; add_header Content-Disposition attachment; }
    }
    ```
13. Reload nginx
14. Save PM2: `pm2 save`
15. Print: "✅ HERMES is live at https://$DOMAIN — Login with your web password"

### Task 24.3 — Write scripts/onboard-tui.js
Interactive terminal UI using Node.js `readline`. This is what you run after install.sh. It collects all business info and calls provision.sh.

Fields to collect (in order, with validation):
- Business name (required)
- Owner name (required)
- GSTIN (15-char alphanumeric validation, can skip if not registered)
- Address (multiline — just one text field)
- City, State, PIN
- Phone number
- Telegram bot token — show guide: "1. Open Telegram → search @BotFather → /newbot → follow steps → copy the token here"
- Telegram user ID — show guide: "Send any message to @userinfobot on Telegram → it will reply with your ID"
- OpenRouter API key — show guide: "Get this from openrouter.ai/keys — the customer pays their own usage there"
- Web dashboard password (typed twice to confirm, min 8 chars)
- Domain for the web dashboard (e.g. `hermes.theirbusiness.com`) — note: customer must point DNS to this VM's IP before this step

Validation at each step with clear error messages. Summary confirmation screen before proceeding. Then calls provision.sh with all args.

### Task 24.4 — SSL Certificate
Run before or during the first customer deployment. The domain must already point to the VM's IP (customer sets this in their DNS or you guide them).

```bash
certbot --nginx -d theirbusiness.com
```

This handles nginx config automatically. Auto-renewal is configured by certbot on Ubuntu by default (systemd timer). Verify: `systemctl status certbot.timer`

If the customer has their own domain: guide them to add an A record pointing to the GVM's external IP. This takes ~5 minutes to propagate.

### Task 24.5 — Nightly DB Backup
Built into the VM itself — the customer's data stays on their VM. Add to root crontab at provision time:

```
0 2 * * * tar -czf /home/hermes/backups/hermes_$(date +%Y%m%d).tar.gz \
  -C /home/hermes/data db/ invoices/ reports/ && \
  find /home/hermes/backups/ -mtime +30 -delete
```

This keeps 30 days of local backups. All on the customer's own disk. You are not involved.

Optional: guide the customer to enable GVM's built-in snapshot/backup feature in the Google Cloud Console — one checkbox, automated daily snapshots. Recommend this during handover.

### Task 24.6 — Handover Walkthrough
Do this with the customer over screen share or in person. Budget 45–60 minutes.

**Pre-requisites the customer must have ready before this call:**
- GVM is running (Ubuntu 22.04, e2-medium or higher)
- SSH access granted to you (or you SSH using their credentials)
- Domain A record pointing to VM's external IP
- Telegram account active
- OpenRouter account created at openrouter.ai, API key ready, billing added

**The session:**
1. SSH into their VM
2. Run `curl -sSL https://raw.githubusercontent.com/YOURNAME/hermes/main/scripts/install.sh | bash`
3. Wait for install (~5–10 min for Whisper model download)
4. Run SSL cert: `certbot --nginx -d theirdomain.com`
5. Run `node /home/hermes/app/scripts/onboard-tui.js` — fill in all fields together
6. Script finishes → PM2 starts both processes → nginx reloaded
7. Customer sends `/start` to their Telegram bot — first message test
8. Together: send first invoice message: "Raj ko invoice banao ₹5000 web development ke liye"
9. Verify PDF arrives in Telegram (30–60 seconds)
10. Open `https://theirdomain.com` in browser, log in with their web password
11. Show dashboard: KPI card updated from the invoice just created
12. Add dashboard URL to Home Screen on their phone
13. Brief walkthrough of 5 core flows: invoice, payment, expense (photo), outstanding query, morning briefing
14. Handover document: give them a 1-page PDF with their bot name, dashboard URL, daily usage guide in Hinglish

**You are now done.** Close SSH session. Do not retain credentials.

### Task 24.7 — Customer Self-Ops (What They Do After Handover)
The customer needs zero technical knowledge to use HERMES day-to-day. Everything is Telegram.

For the rare case something breaks, write a 1-page "If something stops working" guide:
- "Bot not responding" → GVM may have rebooted (Google does this for maintenance) → Go to Google Cloud Console → VM Instances → Start the VM → PM2 auto-restarts on boot
- "Dashboard not loading" → Same as above, or check VM is running
- "Bot token stopped working" → Telegram revoked it → Go to @BotFather → /mybots → regenerate token → send to you for a 5-minute fix (this is your one exception to zero support — it's a 2-line config change)

For your own reference — if you ever need to SSH in for that one exception:
```bash
# Check processes
pm2 list

# View agent logs
pm2 logs hermes-agent --lines 50

# View webapp logs
pm2 logs hermes-web --lines 50

# Restart everything
pm2 restart all
```

---

## APPENDIX A — Dependency Reference

```
# Python package (pyproject.toml)

# Inherited from nanobot (keep all):
# litellm, httpx, pyyaml, python-telegram-bot, discord.py, slack-sdk, etc.

# HERMES additions:
weasyprint                   # HTML → PDF generation
jinja2                       # PDF HTML templates (may already be present)
Pillow                       # Image resize before OCR
openai-whisper               # Voice transcription (loads model locally)
httpx                        # HTTP client for vision LLM OCR calls
fastapi                      # Web dashboard framework
uvicorn[standard]            # ASGI server for FastAPI
python-jose[cryptography]    # JWT for web dashboard auth
passlib[bcrypt]              # Password hashing
python-multipart             # File upload support in FastAPI
python-dotenv                # .env file loading
python-dateutil              # Date parsing for natural language dates
babel                        # Indian number formatting (₹ symbols, lakh/crore)
aiofiles                     # Async file reading in FastAPI

# System packages (apt install):
ffmpeg                       # Audio conversion for Whisper
libpango-1.0-0               # WeasyPrint text rendering
libpangoft2-1.0-0
libharfbuzz0b
libffi-dev
libssl-dev
```

---

## APPENDIX B — What Each Version Got Wrong

| Version | The Problem |
|---|---|
| v2 | Built in JavaScript (Grammy, better-sqlite3, Puppeteer). Nanobot is Python. Wrong runtime entirely. |
| v3 | Switched to Python. But built a custom Telegram handler, custom main.py, custom session history, custom agent loop. Nanobot does all of that. Threw away when the actual nanobot source was read. |
| v4 | Built correctly ON nanobot. Used MCP stdio as the tool bridge. Right approach for open-source distribution. Wrong for a self-hosted, one-time-fee product where you own the stack and never want upstream changes breaking your tools. |
| v5 | Forks nanobot. Freezes it. Builds tool classes natively inside the fork. No MCP subprocess. No upstream dependency. One Python process per customer. One VM per customer (their account, their billing). You deploy once and walk away. |

---

## APPENDIX C — Webapp UX Design Notes

**Visual design principles:**
- Mobile-first. Customers are Indian SMB owners — they use phones, not desktops.
- Clean, high-contrast. No dark mode needed. White background, dark text, accent color: deep green or saffron.
- Large touch targets. 44px minimum for all interactive elements.
- Indian number formatting throughout: ₹1,23,456 (lakh/crore notation), not ₹1,234,56.
- Dates in DD Mon YYYY format (12 Jan 2026), never MM/DD/YYYY.

**Fonts:** System font stack. No Google Fonts (privacy, load speed on Indian connections).

**No JavaScript frameworks.** Plain HTML + minimal vanilla JS for:
- The receipt lightbox modal
- Form validation feedback
- Fetch API calls for report generation (progress feedback)
- Pagination without full page reload (optional enhancement)

**FastAPI + Jinja2** renders full HTML pages server-side. No React, no Vue, no build step.

**PWA basics:**
- Add `<meta name="mobile-web-app-capable" content="yes">` for "Add to Home Screen"
- Add a `manifest.json` with app name, icon, start URL
- Basic service worker for offline-capable login page (optional)

---

## APPENDIX D — Security Notes

- All web dashboard routes are protected by JWT middleware (except `/login`)
- JWT cookie is `HttpOnly` + `Secure` + `SameSite=Lax`
- JWT expires in 24 hours; dashboard auto-redirects to login on expiry
- SQLite is read-only for the webapp (opened with `?mode=ro` URI)
- File downloads go through nginx directly with `Content-Disposition: attachment` — no Python in the path
- Nginx restricts `/files/` alias to only `/home/hermes/data/` — nothing outside that path is served
- Telegram `allowFrom` in config.json restricts the bot to the owner's chat ID only — no other Telegram user can interact with their HERMES
- One VM = one business = one SQLite DB. No cross-customer risk possible at the architecture level.
- You do not retain SSH credentials after handover. Customer controls their own VM entirely.
- Customer's OpenRouter API key is stored only in `/home/hermes/data/config.json` on their own VM — you never hold it.

---

*HERMES Implementation Plan v5.0 — Nanobot Fork, Native Tools, Full Ownership.*
*nanobot frozen and forked. Tools are Python subclasses. No MCP. No upstream risk.*
*One codebase. One install per customer. One-time fee. Their VM. Their API costs. You do nothing after handover.*
