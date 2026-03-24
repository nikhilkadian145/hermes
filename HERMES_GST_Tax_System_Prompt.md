# HERMES — GST & Tax System Build Prompt
### Pass this entire document to your AI coding agent as context + instructions

---

## WHAT YOU ARE BUILDING

You are adding a complete, production-grade GST and Indian tax compliance system to HERMES — an AI-powered bookkeeping agent for Indian SMBs built on a nanobot fork. The system currently has basic `tax_rate` and `tax_amount` fields on invoices but treats GST as a single flat number. That is wrong and needs to be replaced entirely.

This prompt covers every change needed across the full stack: database schema, Python business logic, PDF templates, nanobot agent tools, skill files, FastAPI webapp endpoints, and the React frontend. Read everything before writing a single line. Understand the whole picture first, then implement layer by layer from the bottom up (DB → Python → Tools → Skills → PDF → API → Frontend).

---

## CONTEXT: THE CURRENT STATE (what already exists)

The following files and systems are already built and working. Do not break them:

- `hermes/schema.sql` — SQLite schema with tables: `business`, `clients`, `invoices`, `invoice_items`, `payments`, `expenses`, `quotations`, `quotation_items`, `reminders`, `udhaar`
- `hermes/db.py` — all database operation functions
- `hermes/pdf.py` — WeasyPrint PDF generation using Jinja2 templates
- `templates/invoice.html`, `templates/receipt.html`, `templates/quotation.html`, `templates/report_gst.html` and other report templates
- `nanobot/agent/tools/hermes_tools.py` — all native Tool subclasses including `DbCreateInvoiceTool`, `PdfGenerateInvoiceTool`, `DbGetGstReportTool`, etc.
- `workspace/skills/invoice-create/SKILL.md`, `workspace/skills/report-gst/SKILL.md`, and all other 22 skill files
- `webapp/backend/` — FastAPI JSON API with routers for dashboard, invoices, reports, etc.
- `webapp/frontend/` — React + TypeScript + Vite frontend with all pages built

The current `invoices` table has: `tax_rate REAL` and `tax_amount REAL` — a single rate applied to the whole invoice. The current `invoice_items` table has: `id, invoice_id, description, quantity, unit_price, amount` — no HSN code, no per-item GST rate.

The current `report-gst/SKILL.md` calls `DbGetGstReportTool` which calls `get_gst_report(db_path, from_date, to_date)` which returns a simple aggregate. This is not GSTR-1 compliant.

Everything you build must be backward compatible — existing invoices in the DB must continue to display and report correctly.

---

## PART 1 — DATABASE LAYER

### 1.1 — New tables to add to `hermes/schema.sql`

Add these tables. Do not modify or drop any existing tables.

**`hsn_master`** — The complete HSN/SAC rate lookup table. This is the government's published mapping of product/service codes to GST rates. It gets populated once at install time from a bundled CSV.

```sql
CREATE TABLE IF NOT EXISTS hsn_master (
  id          INTEGER PRIMARY KEY,
  code        TEXT NOT NULL UNIQUE,
  type        TEXT NOT NULL CHECK(type IN ('HSN', 'SAC')),
  description TEXT NOT NULL,
  gst_rate    REAL NOT NULL,
  chapter     TEXT,
  cess_rate   REAL DEFAULT 0,
  last_updated TEXT,
  is_active   INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_hsn_code ON hsn_master(code);
CREATE INDEX IF NOT EXISTS idx_hsn_type ON hsn_master(type);

CREATE VIRTUAL TABLE IF NOT EXISTS hsn_fts
  USING fts5(description, code, content=hsn_master, content_rowid=id);

CREATE TRIGGER IF NOT EXISTS hsn_fts_ai AFTER INSERT ON hsn_master BEGIN
  INSERT INTO hsn_fts(rowid, description, code) VALUES (new.id, new.description, new.code);
END;

CREATE TRIGGER IF NOT EXISTS hsn_fts_ad AFTER DELETE ON hsn_master BEGIN
  INSERT INTO hsn_fts(hsn_fts, rowid, description, code) VALUES ('delete', old.id, old.description, old.code);
END;

CREATE TRIGGER IF NOT EXISTS hsn_fts_au AFTER UPDATE ON hsn_master BEGIN
  INSERT INTO hsn_fts(hsn_fts, rowid, description, code) VALUES ('delete', old.id, old.description, old.code);
  INSERT INTO hsn_fts(rowid, description, code) VALUES (new.id, new.description, new.code);
END;
```

**`item_gst_cache`** — Business-specific learned mappings. Once a business owner confirms that "cotton fabric" is HSN 5208 at 5%, it is saved here and looked up instantly on all future invoices. This is the most important performance optimization — after a few weeks of use, almost every item is cached and no FTS search is needed.

```sql
CREATE TABLE IF NOT EXISTS item_gst_cache (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  item_description TEXT NOT NULL,
  item_normalized  TEXT NOT NULL UNIQUE,
  hsn_code        TEXT NOT NULL,
  gst_rate        REAL NOT NULL,
  confirmed_by    TEXT NOT NULL CHECK(confirmed_by IN ('user', 'agent')),
  use_count       INTEGER DEFAULT 1,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**`gst_filing_periods`** — Tracks which GST filing periods have been filed, locked, or are in progress. Prevents accidental changes to historical data.

```sql
CREATE TABLE IF NOT EXISTS gst_filing_periods (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  period_type TEXT NOT NULL CHECK(period_type IN ('monthly', 'quarterly')),
  from_date   TEXT NOT NULL,
  to_date     TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'filed', 'locked')),
  filed_at    TIMESTAMP,
  notes       TEXT,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(from_date, to_date)
);
```

**`tds_categories`** — TDS rate lookup for vendors. Many Indian SMBs deduct TDS on vendor payments. This table stores the standard sections and rates.

```sql
CREATE TABLE IF NOT EXISTS tds_categories (
  id          INTEGER PRIMARY KEY,
  section     TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  rate_individual REAL NOT NULL,
  rate_company    REAL NOT NULL,
  threshold   REAL NOT NULL,
  is_active   INTEGER DEFAULT 1
);
```

**`notifications`** — In-app notifications written by agent tools, read by webapp. Already referenced in v5.5 Phase 36 but the table was never defined.

```sql
CREATE TABLE IF NOT EXISTS notifications (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  type        TEXT NOT NULL,
  title       TEXT NOT NULL,
  message     TEXT NOT NULL,
  link_type   TEXT,
  link_id     INTEGER,
  is_read     INTEGER DEFAULT 0,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read, created_at);
```

**`anomalies`** — Anomaly detection results written by detection jobs, read by webapp. Already referenced in v5.5 Phase 34 but never defined.

```sql
CREATE TABLE IF NOT EXISTS anomalies (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  type          TEXT NOT NULL,
  confidence    REAL NOT NULL DEFAULT 0.9,
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,
  affected_id_1 INTEGER,
  affected_type_1 TEXT,
  affected_id_2 INTEGER,
  affected_type_2 TEXT,
  status        TEXT NOT NULL DEFAULT 'unreviewed'
                CHECK(status IN ('unreviewed', 'acknowledged', 'escalated', 'dismissed')),
  dismiss_reason TEXT,
  escalation_note TEXT,
  resolved_at   TIMESTAMP,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**`chat_messages`** — Webapp chat relay. Already specified in v5.5 Phase 23 addendum. Including here for completeness so all new tables are added in one migration.

```sql
CREATE TABLE IF NOT EXISTS chat_messages (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
  content         TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK(status IN ('pending', 'processing', 'done')),
  metadata        TEXT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_conv ON chat_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_pending ON chat_messages(status, created_at)
  WHERE status = 'pending' AND role = 'user';
```

### 1.2 — Modify existing tables (ALTER TABLE, do not recreate)

Add these columns to existing tables. Use `ALTER TABLE ... ADD COLUMN` with DEFAULT values so existing rows are not broken.

**`invoice_items`** — add per-item GST tracking:
```sql
ALTER TABLE invoice_items ADD COLUMN hsn_code TEXT DEFAULT NULL;
ALTER TABLE invoice_items ADD COLUMN gst_rate REAL DEFAULT NULL;
ALTER TABLE invoice_items ADD COLUMN cgst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN sgst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN igst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN cess_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN taxable_amount REAL DEFAULT NULL;
```

**`invoices`** — add transaction type, supply type, and tax breakdown:
```sql
ALTER TABLE invoices ADD COLUMN supply_type TEXT DEFAULT 'intrastate'
  CHECK(supply_type IN ('intrastate', 'interstate', 'exempt', 'zero_rated', 'non_gst'));
ALTER TABLE invoices ADD COLUMN place_of_supply TEXT DEFAULT NULL;
ALTER TABLE invoices ADD COLUMN reverse_charge INTEGER DEFAULT 0;
ALTER TABLE invoices ADD COLUMN total_taxable_amount REAL DEFAULT 0;
ALTER TABLE invoices ADD COLUMN total_cgst REAL DEFAULT 0;
ALTER TABLE invoices ADD COLUMN total_sgst REAL DEFAULT 0;
ALTER TABLE invoices ADD COLUMN total_igst REAL DEFAULT 0;
ALTER TABLE invoices ADD COLUMN total_cess REAL DEFAULT 0;
ALTER TABLE invoices ADD COLUMN is_export INTEGER DEFAULT 0;
ALTER TABLE invoices ADD COLUMN lut_number TEXT DEFAULT NULL;
ALTER TABLE invoices ADD COLUMN einvoice_irn TEXT DEFAULT NULL;
ALTER TABLE invoices ADD COLUMN einvoice_ack_number TEXT DEFAULT NULL;
```

**`clients`** — add GST registration type and state:
```sql
ALTER TABLE clients ADD COLUMN registration_type TEXT DEFAULT 'regular'
  CHECK(registration_type IN ('regular', 'composition', 'unregistered', 'consumer'));
ALTER TABLE clients ADD COLUMN state_code TEXT DEFAULT NULL;
ALTER TABLE clients ADD COLUMN pan TEXT DEFAULT NULL;
ALTER TABLE clients ADD COLUMN client_type TEXT DEFAULT 'customer'
  CHECK(client_type IN ('customer', 'vendor', 'both'));
ALTER TABLE clients ADD COLUMN tds_applicable INTEGER DEFAULT 0;
ALTER TABLE clients ADD COLUMN tds_section TEXT DEFAULT NULL;
```

**`expenses`** — add GST on purchases (ITC tracking):
```sql
ALTER TABLE expenses ADD COLUMN hsn_code TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN gst_rate REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN cgst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN sgst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN igst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN itc_eligible INTEGER DEFAULT 1;
ALTER TABLE expenses ADD COLUMN vendor_gstin TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN bill_number TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN bill_date TEXT DEFAULT NULL;
```

**`business`** — add GST registration details:
```sql
ALTER TABLE business ADD COLUMN state_code TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN state_name TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN registration_type TEXT DEFAULT 'regular'
  CHECK(registration_type IN ('regular', 'composition', 'unregistered'));
ALTER TABLE business ADD COLUMN composition_rate REAL DEFAULT NULL;
ALTER TABLE business ADD COLUMN gst_filing_frequency TEXT DEFAULT 'monthly'
  CHECK(gst_filing_frequency IN ('monthly', 'quarterly'));
ALTER TABLE business ADD COLUMN pan TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN default_gst_rate REAL DEFAULT 18.0;
```

### 1.3 — Seed data to insert at init time

After creating the `tds_categories` table, insert the standard Indian TDS sections:

```sql
INSERT OR IGNORE INTO tds_categories
  (section, description, rate_individual, rate_company, threshold) VALUES
  ('194C', 'Contractor payments', 1.0, 2.0, 30000),
  ('194J', 'Professional / Technical services', 10.0, 10.0, 30000),
  ('194A', 'Interest (other than securities)', 10.0, 10.0, 40000),
  ('194H', 'Commission or brokerage', 5.0, 5.0, 15000),
  ('194I', 'Rent', 10.0, 10.0, 240000),
  ('194Q', 'Purchase of goods', 0.1, 0.1, 5000000),
  ('194B', 'Lottery winnings', 30.0, 30.0, 10000),
  ('192',  'Salary', 0.0, 0.0, 250000),
  ('206C', 'TCS on sale of goods', 0.1, 0.1, 5000000);
```

Also insert the 36 Indian state/UT codes:

```sql
CREATE TABLE IF NOT EXISTS indian_states (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

INSERT OR IGNORE INTO indian_states VALUES
  ('01','Jammu & Kashmir'),('02','Himachal Pradesh'),
  ('03','Punjab'),('04','Chandigarh'),
  ('05','Uttarakhand'),('06','Haryana'),
  ('07','Delhi'),('08','Rajasthan'),
  ('09','Uttar Pradesh'),('10','Bihar'),
  ('11','Sikkim'),('12','Arunachal Pradesh'),
  ('13','Nagaland'),('14','Manipur'),
  ('15','Mizoram'),('16','Tripura'),
  ('17','Meghalaya'),('18','Assam'),
  ('19','West Bengal'),('20','Jharkhand'),
  ('21','Odisha'),('22','Chhattisgarh'),
  ('23','Madhya Pradesh'),('24','Gujarat'),
  ('25','Daman & Diu'),('26','Dadra & Nagar Haveli'),
  ('27','Maharashtra'),('28','Andhra Pradesh'),
  ('29','Karnataka'),('30','Goa'),
  ('31','Lakshadweep'),('32','Kerala'),
  ('33','Tamil Nadu'),('34','Puducherry'),
  ('35','Andaman & Nicobar'),('36','Telangana'),
  ('37','Andhra Pradesh (new)'),('38','Ladakh');
```

---

## PART 2 — PYTHON BUSINESS LOGIC (`hermes/db.py` and new `hermes/gst.py`)

### 2.1 — New file: `hermes/gst.py`

Create this file. It contains all GST calculation logic. Import it from `hermes/db.py` and from `hermes_tools.py`. This keeps tax logic in one place.

**`determine_supply_type(business_state_code, client_state_code, client_gstin)`**

Returns `'intrastate'`, `'interstate'`, or `'unregistered'`.
- If client has no GSTIN: `'unregistered'` (B2C)
- If business state code == client state code: `'intrastate'` (split into CGST + SGST)
- If different state codes: `'interstate'` (single IGST)
- If client GSTIN starts with state code different from business: `'interstate'`

```python
def determine_supply_type(business_state_code: str,
                           client_state_code: str,
                           client_gstin: str | None) -> str:
    if not client_gstin:
        return 'unregistered'
    client_state = client_gstin[:2] if client_gstin else client_state_code
    if client_state == business_state_code:
        return 'intrastate'
    return 'interstate'
```

**`calculate_item_tax(unit_price, quantity, gst_rate, supply_type)`**

Returns a dict with all computed amounts for a single line item.

```python
def calculate_item_tax(unit_price: float, quantity: float,
                        gst_rate: float, supply_type: str) -> dict:
    taxable = round(unit_price * quantity, 2)
    total_gst = round(taxable * gst_rate / 100, 2)

    if supply_type == 'interstate':
        return {
            'taxable_amount': taxable,
            'cgst_rate': 0, 'cgst_amount': 0,
            'sgst_rate': 0, 'sgst_amount': 0,
            'igst_rate': gst_rate,
            'igst_amount': total_gst,
            'total_tax': total_gst,
            'line_total': round(taxable + total_gst, 2)
        }
    else:  # intrastate or unregistered
        half = round(total_gst / 2, 2)
        return {
            'taxable_amount': taxable,
            'cgst_rate': gst_rate / 2,
            'cgst_amount': half,
            'sgst_rate': gst_rate / 2,
            'sgst_amount': round(total_gst - half, 2),  # handles odd paise
            'igst_rate': 0, 'igst_amount': 0,
            'total_tax': total_gst,
            'line_total': round(taxable + total_gst, 2)
        }
```

**`calculate_invoice_totals(items_with_tax)`**

Takes a list of item dicts (each with the output of `calculate_item_tax` merged in) and returns the invoice-level totals.

```python
def calculate_invoice_totals(items: list[dict]) -> dict:
    return {
        'subtotal':             round(sum(i['taxable_amount'] for i in items), 2),
        'total_cgst':           round(sum(i['cgst_amount'] for i in items), 2),
        'total_sgst':           round(sum(i['sgst_amount'] for i in items), 2),
        'total_igst':           round(sum(i['igst_amount'] for i in items), 2),
        'total_cess':           round(sum(i.get('cess_amount', 0) for i in items), 2),
        'total_tax':            round(sum(i['total_tax'] for i in items), 2),
        'grand_total':          round(sum(i['line_total'] for i in items), 2),
        'total_in_words':       amount_to_words_inr(
                                    round(sum(i['line_total'] for i in items), 2)
                                ),
    }
```

**`amount_to_words_inr(amount)`**

Converts a rupee amount to Indian English words. Required on invoices by GST law for amounts above ₹5,000.

```python
def amount_to_words_inr(amount: float) -> str:
    """
    Converts 125430.50 → "Rupees One Lakh Twenty Five Thousand
                           Four Hundred Thirty and Paise Fifty Only"
    Implement using Indian number system (ones, tens, hundreds, thousands,
    ten-thousands, lakhs, ten-lakhs, crores).
    """
```

Implement this fully. Do not use any external library for this — write the pure Python implementation. It needs to handle values from ₹0 to ₹99,99,99,999 (99 crore+).

### 2.2 — New HSN lookup functions in `hermes/db.py`

Add these functions. They are called by the GstLookupTool.

```python
def search_hsn(db_path: str, query: str, limit: int = 5) -> list[dict]:
    """FTS5 search on HSN/SAC descriptions. Returns top matches ranked by relevance."""
    conn = get_conn(db_path)
    try:
        rows = conn.execute("""
            SELECT m.code, m.type, m.description,
                   m.gst_rate, m.chapter, m.cess_rate, rank
            FROM hsn_fts
            JOIN hsn_master m ON hsn_fts.rowid = m.id
            WHERE hsn_fts MATCH ? AND m.is_active = 1
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        # FTS query failed (special chars etc.) — fall back to LIKE
        rows = conn.execute("""
            SELECT code, type, description, gst_rate, chapter, cess_rate
            FROM hsn_master
            WHERE description LIKE ? AND is_active = 1
            LIMIT ?
        """, (f'%{query}%', limit)).fetchall()
        return [dict(r) for r in rows]

def get_hsn_by_code(db_path: str, code: str) -> dict | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM hsn_master WHERE code = ?", (code,)
    ).fetchone()
    return dict(row) if row else None

def get_cached_item_gst(db_path: str, description: str) -> dict | None:
    normalized = description.lower().strip()
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM item_gst_cache WHERE item_normalized = ?",
        (normalized,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE item_gst_cache SET use_count = use_count + 1, "
            "updated_at = CURRENT_TIMESTAMP WHERE item_normalized = ?",
            (normalized,)
        )
        conn.commit()
    return dict(row) if row else None

def save_item_gst_cache(db_path: str, description: str, hsn_code: str,
                         gst_rate: float, confirmed_by: str = 'agent') -> None:
    normalized = description.lower().strip()
    conn = get_conn(db_path)
    conn.execute("""
        INSERT INTO item_gst_cache
          (item_description, item_normalized, hsn_code, gst_rate, confirmed_by)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_normalized) DO UPDATE SET
          hsn_code     = excluded.hsn_code,
          gst_rate     = excluded.gst_rate,
          confirmed_by = excluded.confirmed_by,
          use_count    = item_gst_cache.use_count + 1,
          updated_at   = CURRENT_TIMESTAMP
    """, (description, normalized, hsn_code, gst_rate, confirmed_by))
    conn.commit()
```

### 2.3 — Update `create_invoice` in `hermes/db.py`

The current `create_invoice` function takes `tax_rate` and applies it uniformly. Replace this with a version that accepts fully calculated items including per-item HSN and tax amounts.

The new signature:

```python
def create_invoice(
    db_path: str,
    client_id: int,
    items: list[dict],       # Each item: {description, quantity, unit_price,
                              #   hsn_code, gst_rate, cgst_amount, sgst_amount,
                              #   igst_amount, taxable_amount, line_total}
    due_date: str,
    supply_type: str,         # 'intrastate' | 'interstate' | 'unregistered'
    place_of_supply: str,     # state code e.g. '27'
    notes: str = None,
    reverse_charge: bool = False,
    is_export: bool = False,
    lut_number: str = None
) -> int:
```

Inside the function:
1. Call `calculate_invoice_totals(items)` to get all totals
2. Insert into `invoices` with all new columns populated
3. Insert each item into `invoice_items` with all new columns
4. Return invoice_id

Maintain the old `tax_rate` and `tax_amount` columns on the `invoices` table for backward compatibility with existing rows — just don't populate them for new invoices. New code reads the new columns; old display code falls back to old columns.

### 2.4 — Updated GST report query in `hermes/db.py`

Replace the existing `get_gst_report` with a GSTR-1-compliant version:

```python
def get_gst_report(db_path: str, from_date: str, to_date: str) -> dict:
    """
    Returns structured GSTR-1 data grouped as required by GST law:
    - b2b: B2B invoices (client has GSTIN), invoice-wise detail
    - b2c_large: B2C invoices above ₹2.5L, invoice-wise
    - b2c_small: B2C invoices below ₹2.5L, rate-wise summary only
    - cdnr: Credit/debit notes against registered clients
    - exports: Export invoices
    - nil_rated: Nil/exempt/non-GST supplies
    - hsn_summary: HSN-wise summary of all supplies (mandatory above ₹5Cr turnover)
    - summary: totals by rate slab for the summary table
    """
```

The function should query the new columns (`total_cgst`, `total_sgst`, `total_igst`, etc.) for new invoices. For old invoices that have `tax_rate` but not the new columns, derive approximate values: `cgst = tax_amount / 2`, `sgst = tax_amount / 2`.

Also add:

```python
def get_itc_summary(db_path: str, from_date: str, to_date: str) -> dict:
    """
    Input Tax Credit from vendor bills (expenses with itc_eligible=1 and vendor_gstin set).
    Groups by tax rate slab.
    Returns: {total_itc, by_rate: [{rate, cgst, sgst, igst, total}]}
    """

def get_gst_liability(db_path: str, from_date: str, to_date: str) -> dict:
    """
    Net GST payable = output tax (from invoices) - ITC (from eligible expenses).
    Returns all the numbers needed for GST-3B filing.
    """
```

### 2.5 — Notification helpers in `hermes/db.py`

```python
def create_notification(db_path: str, type: str, title: str,
                         message: str, link_type: str = None,
                         link_id: int = None) -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO notifications (type, title, message, link_type, link_id) "
        "VALUES (?, ?, ?, ?, ?)",
        (type, title, message, link_type, link_id)
    )
    conn.commit()
    return cur.lastrowid

def get_unread_notification_count(db_path: str) -> int:
    conn = get_conn(db_path)
    return conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE is_read = 0"
    ).fetchone()[0]
```

Add `create_notification()` calls inside these existing functions:
- `create_invoice()` — notify "Invoice {number} created for {client}"
- `record_payment()` — notify "Payment ₹{amount} received from {client}"
- `auto_update_invoice_status_after_payment()` — if now fully paid, notify "Invoice {number} fully paid"
- Any new anomaly detection function — notify for each anomaly found

### 2.6 — Anomaly detection in `hermes/db.py`

Add these functions. They are called by a nightly cron job.

```python
def detect_duplicate_bills(db_path: str) -> list[dict]:
    """
    Find pairs of invoices/expenses that are likely duplicates:
    same vendor + same amount + dates within 30 days + not already flagged.
    Returns list of {type, id1, id2, vendor, amount, date1, date2, confidence}
    """

def detect_price_drift(db_path: str, threshold_pct: float = 20.0) -> list[dict]:
    """
    For each vendor, find items where the unit price has changed by more than
    threshold_pct compared to the average of the last 3 occurrences.
    Returns list of {vendor, item_description, current_price, avg_price, drift_pct}
    """

def detect_round_number_billing(db_path: str) -> list[dict]:
    """
    Flag invoices/bills where the total is suspiciously round
    (exactly divisible by 1000, above ₹10,000).
    Returns list of flagged invoice ids with amounts.
    """

def run_anomaly_detection(db_path: str) -> int:
    """
    Run all detection functions and write results to the anomalies table.
    Skip pairs that already exist in the anomalies table (check by affected ids).
    Returns count of new anomalies written.
    """
```

---

## PART 3 — DATA FILE: `scripts/data/hsn_gst_rates.csv`

You need to create this CSV file. It must be committed to the repo and bundled with HERMES. It is the authoritative GST rate table.

The CSV must have columns: `code, type, description, gst_rate, chapter, cess_rate, last_updated`

Include at minimum the following HSN entries covering the most common goods traded by Indian SMBs. Use the official GST Council rate schedule. Key entries to include (not exhaustive — add all you know):

**Textiles (Chapter 50–63):**
- 5007: Silk woven fabrics — 5%
- 5111: Wool woven fabrics — 5%
- 5208: Cotton woven fabrics — 5%
- 5309: Flax woven fabrics — 5%
- 5407: Synthetic filament yarn fabrics — 5%
- 5512: Synthetic staple fibre fabrics — 5%
- 6101: Men's overcoats, knitted — 5% (below ₹1000), 12% (above ₹1000)
- 6201: Men's overcoats, woven — 5% (below ₹1000), 12% (above ₹1000)

**Electronics (Chapter 84–85):**
- 8471: Computers and peripherals — 18%
- 8517: Telephones, smartphones — 18%
- 8528: Monitors, TVs — 28%
- 8544: Wires and cables — 18%

**Food (Chapter 1–24):**
- 0101–0106: Live animals — 0%
- 0201–0210: Meat — 0% (fresh), 12% (processed)
- 0401: Milk — 0%
- 0701–0714: Vegetables — 0%
- 0801–0814: Fruits — 0%
- 1001: Wheat — 0%
- 1006: Rice — 0%
- 1901: Malt extract, food preparations — 18%
- 2101: Coffee/tea extracts — 18%
- 2201: Water — 18%
- 2202: Aerated drinks — 28% + 12% cess

**Pharmaceuticals (Chapter 30):**
- 3003: Medicaments — 12%
- 3004: Medicaments in measured doses — 12%
- 3005: Bandages, wadding — 12%

**Construction (Chapter 68–70):**
- 6810: Cement articles — 28%
- 7214: Iron/steel bars — 18%
- 7308: Structural steel — 18%

**Paper/Stationery (Chapter 48):**
- 4801: Newsprint — 5%
- 4802: Uncoated paper — 12%
- 4820: Registers, notebooks — 12%
- 4821: Labels — 12%

**Packaging (Chapter 39, 48, 63):**
- 3923: Plastic articles for conveying goods — 18%
- 4819: Paper cartons, boxes — 12%
- 6305: Sacks and bags — 5%

**Chemicals (Chapter 28–38):**
- 2814: Ammonia — 18%
- 3402: Soap, detergent — 18%
- 3808: Insecticides, pesticides — 18%

**Vehicles (Chapter 87):**
- 8703: Cars — 28% + cess (1–22% depending on engine size)
- 8711: Motorcycles — 28%

**SAC (Services):**
- 9954: Construction services — 18%
- 9961: Wholesale trade services — 18%
- 9962: Retail trade services — 18%
- 9971: Financial services — 18%
- 9972: Real estate services — 12%/18%
- 9973: Leasing/rental services — 18%
- 9981: R&D services — 18%
- 9982: Legal/accounting services — 18%
- 9983: Management consulting — 18%
- 9984: Telecommunications — 18%
- 9985: Business support services — 18%
- 9986: Agriculture support services — 0%/18%
- 9987: Maintenance/repair services — 18%
- 9988: Manufacturing services — 5%/12%/18%
- 9991: Education services — 0%
- 9993: Health services — 0%/5%/12%
- 9994: Sewage/waste management — 0%
- 9996: Recreational services — 18%
- 9997: Other services — 18%

For each entry where the rate depends on value (e.g., garments below/above ₹1000), use the higher rate as the default and add a note in the description. The agent will surface this to the user during invoice creation.

Add as many additional HSN codes as you know. The more complete this file is, the better the lookup quality.

### 2.7 — Script: `scripts/load_hsn_data.py`

```python
"""
Loads hsn_gst_rates.csv into the hermes.db hsn_master table.
Run once at provision time: python scripts/load_hsn_data.py <db_path>
Safe to re-run — uses INSERT OR IGNORE.
"""
import sqlite3, csv, sys, os

def load(db_path: str):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'hsn_gst_rates.csv')
    conn = sqlite3.connect(db_path)
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [
            (r['code'], r['type'], r['description'],
             float(r['gst_rate']), r.get('chapter', r['code'][:2]),
             float(r.get('cess_rate', 0)), r.get('last_updated', '2024-07-01'))
            for r in reader
        ]
    conn.executemany(
        "INSERT OR IGNORE INTO hsn_master "
        "(code, type, description, gst_rate, chapter, cess_rate, last_updated)"
        " VALUES (?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM hsn_master").fetchone()[0]
    conn.close()
    print(f"HSN master loaded: {count} entries in database")

if __name__ == '__main__':
    load(sys.argv[1])
```

Add to `scripts/provision.sh` after `init_db` call:
```bash
python3 /home/hermes/app/scripts/load_hsn_data.py /home/hermes/data/db/hermes.db
echo "HSN/SAC data loaded."
```

---

## PART 4 — AGENT TOOLS (`nanobot/agent/tools/hermes_tools.py`)

Add these new Tool subclasses. Do not touch or remove any existing tools.

### 4.1 — `GstLookupTool`

```python
class GstLookupTool(Tool):
    name = "gst_lookup"
    description = (
        "Look up the correct GST rate and HSN/SAC code for any product or service. "
        "ALWAYS call this for every line item before creating an invoice or recording an expense. "
        "Never guess or assume a GST rate. This tool checks the business's item cache first "
        "(instant for known items), then searches the official HSN/SAC master table. "
        "If multiple rates are possible, it returns candidates for you to present to the user."
    )
    parameters = {
        "type": "object",
        "properties": {
            "item_description": {
                "type": "string",
                "description": "The product or service description as stated by the user."
            }
        },
        "required": ["item_description"]
    }

    def execute(self, item_description: str, **kwargs) -> str:
        db_path = get_db_path()

        # Layer 1: business cache
        cached = db.get_cached_item_gst(db_path, item_description)
        if cached:
            return json.dumps({
                "hsn_code": cached["hsn_code"],
                "gst_rate": cached["gst_rate"],
                "source": "cache",
                "confidence": "high",
                "message": f"HSN {cached['hsn_code']}, GST {cached['gst_rate']}% (previously confirmed)"
            })

        # Layer 2: FTS search
        results = db.search_hsn(db_path, item_description, limit=5)

        if not results:
            business = db.get_business(db_path)
            default = business.get("default_gst_rate", 18.0)
            return json.dumps({
                "hsn_code": None,
                "gst_rate": default,
                "source": "default",
                "confidence": "low",
                "message": (
                    f"No HSN match found for '{item_description}'. "
                    f"Using business default {default}%. "
                    f"Please ask the user to confirm the correct rate."
                )
            })

        # Check if there's a clear top result
        top = results[0]
        if len(results) == 1:
            db.save_item_gst_cache(
                db_path, item_description,
                top['code'], top['gst_rate'], 'agent'
            )
            return json.dumps({
                "hsn_code": top['code'],
                "gst_rate": top['gst_rate'],
                "source": "hsn_lookup",
                "confidence": "medium",
                "matched_description": top['description'],
                "message": (
                    f"HSN {top['code']} — {top['description']} — {top['gst_rate']}% GST"
                )
            })

        # Multiple candidates — return them all for disambiguation
        return json.dumps({
            "hsn_code": None,
            "gst_rate": None,
            "source": "hsn_lookup",
            "confidence": "low",
            "candidates": [
                {"code": r['code'], "description": r['description'], "gst_rate": r['gst_rate']}
                for r in results[:3]
            ],
            "message": (
                f"Multiple HSN matches for '{item_description}'. "
                f"Present these options to the user and ask them to pick one."
            )
        })
```

### 4.2 — `ConfirmItemGstTool`

Called after the user confirms which HSN code is correct from the candidates list.

```python
class ConfirmItemGstTool(Tool):
    name = "confirm_item_gst"
    description = (
        "Save a confirmed HSN code and GST rate for an item. "
        "Call this after the user picks the correct rate from candidates returned by gst_lookup. "
        "This saves the mapping permanently so the user is never asked again for this item."
    )
    parameters = {
        "type": "object",
        "properties": {
            "item_description": {"type": "string"},
            "hsn_code": {"type": "string"},
            "gst_rate": {"type": "number"}
        },
        "required": ["item_description", "hsn_code", "gst_rate"]
    }

    def execute(self, item_description: str, hsn_code: str, gst_rate: float, **kwargs) -> str:
        db_path = get_db_path()
        db.save_item_gst_cache(db_path, item_description, hsn_code, gst_rate, 'user')
        return json.dumps({"success": True, "message": f"Saved: {item_description} → HSN {hsn_code}, {gst_rate}% GST"})
```

### 4.3 — `CalculateInvoiceTaxTool`

Called by the agent after all line items have HSN codes resolved. Does the full tax math.

```python
class CalculateInvoiceTaxTool(Tool):
    name = "calculate_invoice_tax"
    description = (
        "Calculate CGST, SGST, IGST, and totals for an invoice based on line items, "
        "supply type (intrastate/interstate), and per-item GST rates. "
        "Call this after all line items have confirmed HSN codes, before creating the invoice."
    )
    parameters = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "Line items with description, quantity, unit_price, hsn_code, gst_rate",
                "items": {"type": "object"}
            },
            "client_id": {"type": "integer"},
        },
        "required": ["items", "client_id"]
    }

    def execute(self, items: list, client_id: int, **kwargs) -> str:
        from hermes.gst import determine_supply_type, calculate_item_tax, calculate_invoice_totals
        db_path = get_db_path()
        business = db.get_business(db_path)
        client = db.get_client(db_path, client_id)

        supply_type = determine_supply_type(
            business.get('state_code', ''),
            client.get('state_code', ''),
            client.get('gstin')
        )

        enriched_items = []
        for item in items:
            tax = calculate_item_tax(
                item['unit_price'], item['quantity'],
                item['gst_rate'], supply_type
            )
            enriched_items.append({**item, **tax})

        totals = calculate_invoice_totals(enriched_items)
        return json.dumps({
            "supply_type": supply_type,
            "items": enriched_items,
            "totals": totals,
            "summary": (
                f"Taxable: ₹{totals['subtotal']:,.0f} | "
                f"{'CGST+SGST' if supply_type == 'intrastate' else 'IGST'}: "
                f"₹{totals['total_tax']:,.0f} | "
                f"Total: ₹{totals['grand_total']:,.0f}"
            )
        })
```

### 4.4 — `GetGstLiabilityTool`

```python
class GetGstLiabilityTool(Tool):
    name = "get_gst_liability"
    description = (
        "Get the net GST payable for a period — output tax minus input tax credit (ITC). "
        "Use for GST-3B filing queries."
    )
    parameters = {
        "type": "object",
        "properties": {
            "from_date": {"type": "string", "description": "YYYY-MM-DD"},
            "to_date":   {"type": "string", "description": "YYYY-MM-DD"}
        },
        "required": ["from_date", "to_date"]
    }

    def execute(self, from_date: str, to_date: str, **kwargs) -> str:
        db_path = get_db_path()
        liability = db.get_gst_liability(db_path, from_date, to_date)
        return json.dumps(liability)
```

### 4.5 — `GetHsnSummaryTool`

```python
class GetHsnSummaryTool(Tool):
    name = "get_hsn_summary"
    description = "Get HSN/SAC-wise summary of supplies for a period. Required for GSTR-1 filing."
    parameters = {
        "type": "object",
        "properties": {
            "from_date": {"type": "string"},
            "to_date":   {"type": "string"}
        },
        "required": ["from_date", "to_date"]
    }

    def execute(self, from_date: str, to_date: str, **kwargs) -> str:
        db_path = get_db_path()
        result = db.get_hsn_summary(db_path, from_date, to_date)
        return json.dumps(result)
```

### 4.6 — `RunAnomalyDetectionTool`

```python
class RunAnomalyDetectionTool(Tool):
    name = "run_anomaly_detection"
    description = (
        "Scan all transactions for anomalies: duplicate bills, price drift, "
        "round-number billing. Writes results to the anomalies table. "
        "Called by the nightly cron job automatically."
    )
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs) -> str:
        db_path = get_db_path()
        count = db.run_anomaly_detection(db_path)
        return json.dumps({"new_anomalies": count, "message": f"Detection complete. {count} new anomalies found."})
```

### 4.7 — Register all new tools in `registry.py`

Add these to the tool registry alongside all existing HERMES tools:
`GstLookupTool`, `ConfirmItemGstTool`, `CalculateInvoiceTaxTool`,
`GetGstLiabilityTool`, `GetHsnSummaryTool`, `RunAnomalyDetectionTool`

---

## PART 5 — SKILL FILES

### 5.1 — Rewrite `workspace/skills/invoice-create/SKILL.md`

Replace the GST section entirely:

```markdown
## Invoice Creation — GST Rules

For EVERY line item in a new invoice, follow this exact sequence:

STEP 1 — Resolve HSN and GST rate
  Call `gst_lookup` with the item description.
  
  If confidence is "high" (cached): use it silently. Do not mention HSN to the user.
  If confidence is "medium" (single FTS match): use it silently.
  If confidence is "low" with candidates: show user in Hinglish:
    "Ek cheez confirm karo — [item] ke liye GST rate:
     a) HSN [code] — [description] — [rate]%
     b) HSN [code] — [description] — [rate]%
     Kaun sahi hai?"
  If no match: ask "Is item ka GST rate kya hai? Default [X]% use karoon?"
  
  After user picks: call `confirm_item_gst` to save for next time.

STEP 2 — Calculate taxes
  Once ALL items have HSN codes and rates confirmed,
  call `calculate_invoice_tax` with all items and the client_id.
  
  This returns enriched items + totals + supply_type (intrastate/interstate).

STEP 3 — Show summary to user before creating
  Show: "Invoice summary:
  [Item 1] x [qty] — ₹[taxable] + [rate]% GST = ₹[total]
  [Item 2] x [qty] — ₹[taxable] + [rate]% GST = ₹[total]
  ---
  Subtotal: ₹[X]
  CGST ([rate]%): ₹[X]   ← show CGST+SGST for intrastate
  SGST ([rate]%): ₹[X]   ← show IGST for interstate
  Total: ₹[X]
  
  Banao invoice?"

STEP 4 — Create invoice
  On user confirmation, call `db_create_invoice` with
  the enriched items and totals from Step 2.

IMPORTANT RULES:
- Never create an invoice without calling gst_lookup first.
- Never apply a flat GST rate to the whole invoice — it's per line item.
- Intrastate = CGST + SGST (split equally). Interstate = IGST (full rate).
- If client has no GSTIN, it's B2C — use intrastate rates regardless.
- Composition scheme clients: no GST on invoice, add note "Tax payable under RCM" if applicable.
```

### 5.2 — Update `workspace/skills/report-gst/SKILL.md`

```markdown
## GST Report

This skill handles all GST-related reporting queries.

QUERY PATTERNS:
- "GST report chahiye" → ask for period (month or quarter)
- "GSTR-1 data dikhao" → call get_gst_report for the period
- "ITC kitna hai" → call get_gst_liability for the period
- "GST kitna bhar na padega" → call get_gst_liability, show net payable
- "HSN summary chahiye" → call get_hsn_summary for the period

REPORT TYPES AND WHEN TO USE EACH:
- GSTR-1: Outward supplies — call get_gst_report (agent tool: DbGetGstReportTool)
- ITC Tracker: Input credit — call get_itc_summary
- Net Liability: Output − ITC — call get_gst_liability (agent tool: GetGstLiabilityTool)
- HSN Summary: Item-wise — call get_hsn_summary (agent tool: GetHsnSummaryTool)

PDF GENERATION:
After showing summary, offer: "PDF chahiye? Portal ke liye JSON bhi export kar sakta hoon."
For PDF: call PdfGenerateGstReportTool
For portal JSON: call ExportGstPortalJsonTool (new tool — see Part 4)

ALWAYS state the period clearly in Hinglish:
"April se June 2025 ka GST report:"
```

### 5.3 — Add new `workspace/skills/gst-query/SKILL.md`

```markdown
## GST Query

For quick GST questions that don't need a full report.

TRIGGERS:
- "Is item ka GST kitna hai?" → call gst_lookup
- "HSN code kya hai [item] ka?" → call gst_lookup
- "CGST SGST kya hoga?" → call gst_lookup + explain intrastate split
- "ITC claim ho sakta hai?" → explain ITC eligibility rules
- "GST number valid hai?" → validate GSTIN format (15 chars, check digit)

GSTIN VALIDATION RULE:
Format: [2 digit state code][10 char PAN][1 entity code][1 Z][1 check digit]
Validate format with regex: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
State code must be valid (01–38).

ITC ELIGIBILITY RULES (explain these in Hinglish when asked):
- Eligible: goods/services used for business
- Not eligible: personal use, food/beverages, club memberships, beauty treatment,
  motor vehicles (exceptions apply), works contract for immovable property
- Partially eligible: some blocked credits under Section 17(5) apply
```

---

## PART 6 — PDF TEMPLATES

### 6.1 — Update `templates/invoice.html`

The existing template uses `{{ invoice.tax_rate }}` and `{{ invoice.tax_amount }}`. Update it to handle both old-style (single rate) and new-style (per-item) invoices.

In the line items table, add a column for HSN code (right after description). Make it conditionally shown: only display if at least one item has an HSN code.

Replace the tax summary section with:

```html
<!-- Tax summary — handles both old and new invoice format -->
<tr class="subtotal-row">
  <td colspan="3" class="text-right">Taxable Amount</td>
  <td class="amount">
    {% if invoice.total_taxable_amount %}
      ₹{{ invoice.total_taxable_amount | indian_number }}
    {% else %}
      ₹{{ invoice.subtotal | indian_number }}
    {% endif %}
  </td>
</tr>

{% if invoice.total_cgst and invoice.total_cgst > 0 %}
<tr>
  <td colspan="3" class="text-right">CGST</td>
  <td class="amount">₹{{ invoice.total_cgst | indian_number }}</td>
</tr>
<tr>
  <td colspan="3" class="text-right">SGST</td>
  <td class="amount">₹{{ invoice.total_sgst | indian_number }}</td>
</tr>
{% elif invoice.total_igst and invoice.total_igst > 0 %}
<tr>
  <td colspan="3" class="text-right">IGST</td>
  <td class="amount">₹{{ invoice.total_igst | indian_number }}</td>
</tr>
{% else %}
<!-- Old invoice format fallback -->
<tr>
  <td colspan="3" class="text-right">GST ({{ invoice.tax_rate }}%)</td>
  <td class="amount">₹{{ invoice.tax_amount | indian_number }}</td>
</tr>
{% endif %}

{% if invoice.total_cess and invoice.total_cess > 0 %}
<tr>
  <td colspan="3" class="text-right">Cess</td>
  <td class="amount">₹{{ invoice.total_cess | indian_number }}</td>
</tr>
{% endif %}

<tr class="grand-total-row">
  <td colspan="3" class="text-right"><strong>Grand Total</strong></td>
  <td class="amount"><strong>₹{{ invoice.total | indian_number }}</strong></td>
</tr>

{% if invoice.total_in_words %}
<tr>
  <td colspan="4" class="amount-in-words">
    <em>{{ invoice.total_in_words }}</em>
  </td>
</tr>
{% endif %}
```

Add a Jinja2 custom filter `indian_number` in `hermes/pdf.py`:

```python
def indian_number_filter(value):
    """Format number in Indian style: 1,23,456.00"""
    try:
        v = float(value)
        # Use babel for Indian formatting
        from babel.numbers import format_currency
        return format_currency(v, 'INR', locale='en_IN').replace('₹', '').strip()
    except:
        return str(value)

# Register it on your Jinja2 environment:
env.filters['indian_number'] = indian_number_filter
```

### 6.2 — Update `templates/report_gst.html`

Rewrite this template to show GSTR-1-style sections instead of a single aggregate table:

**Section 1: Summary cards** (Output Tax, ITC, Net Payable)
**Section 2: B2B Supplies** (invoice-wise table with client GSTIN, taxable value, CGST, SGST, IGST)
**Section 3: B2C Large** (invoices above ₹2.5L to unregistered customers)
**Section 4: B2C Small** (rate-wise summary for unregistered, below ₹2.5L)
**Section 5: HSN Summary** (code, description, UQC, quantity, taxable value, CGST, SGST, IGST)
**Section 6: ITC Summary** (from eligible vendor bills)

Each section has a "Total" row at the bottom. Numbers are right-aligned and use the `indian_number` filter.

---

## PART 7 — FASTAPI BACKEND (`webapp/backend/routers/reports.py` and others)

### 7.1 — Update GST report endpoints

In `webapp/backend/routers/reports.py`, update the GST report endpoints to use the new `get_gst_report` which returns the GSTR-1 structured data.

`GET /api/reports/gst/gstr1?from_date=&to_date=`
→ calls `db.get_gst_report(db_path, from_date, to_date)`
→ returns the full structured dict with b2b, b2c_large, b2c_small, cdnr, exports, hsn_summary, summary

`GET /api/reports/gst/itc?from_date=&to_date=`
→ calls `db.get_itc_summary(db_path, from_date, to_date)`

`GET /api/reports/gst/liability?from_date=&to_date=`
→ calls `db.get_gst_liability(db_path, from_date, to_date)`

`GET /api/reports/gst/hsn?from_date=&to_date=`
→ calls `db.get_hsn_summary(db_path, from_date, to_date)` (separate from gst_report)

`POST /api/reports/gst/export-json?from_date=&to_date=`
→ generates the GSTN portal-compatible JSON (exact format per GSTN schema)
→ saves to `/home/hermes/data/exports/gstr1_{period}.json`
→ returns download URL

### 7.2 — New endpoint: GST settings

`GET /api/settings/gst`
→ returns business GST settings: state_code, registration_type, filing_frequency, default_gst_rate

`PATCH /api/settings/gst`
→ updates GST-specific settings

### 7.3 — New endpoint: HSN lookup (for webapp invoice creation via chat)

`GET /api/hsn/search?q=`
→ calls `db.search_hsn(db_path, q, limit=5)`
→ returns candidate list for the frontend (used in the chat invoice preview panel)

`GET /api/hsn/code/:code`
→ calls `db.get_hsn_by_code(db_path, code)`

### 7.4 — New endpoint: GST filing periods

`GET /api/gst/filing-periods`
→ returns list of quarters/months with filing status

`PATCH /api/gst/filing-periods/:id`
→ update status (open → filed → locked)

### 7.5 — Update notifications and anomalies endpoints

These were specified in v5.5 (Phases 34 and 36) but now have the actual DB tables.

`GET /api/anomalies` and all anomaly mutation endpoints — wire to the new `anomalies` table.
`GET /api/notifications` and `POST /api/notifications/mark-read` — wire to the new `notifications` table.
`GET /api/notifications/count/unread` — calls `db.get_unread_notification_count(db_path)`.

---

## PART 8 — REACT FRONTEND

### 8.1 — GST Reports page (`src/pages/GSTReportsPage.tsx`)

The GST reports page at `/reports/gst` already exists from v5.5 Phase 31. Update it to consume the new structured API responses.

The page now has **5 tabs**:

**Tab 1: GSTR-1 Summary**
- 3 summary cards: Total Output Tax | Total ITC | Net GST Payable
- B2B table: columns Invoice #, Client, GSTIN, Date, Taxable, CGST, SGST, IGST, Total
- B2C large table: same columns without GSTIN
- B2C small: a simple rate-slab summary table (5%, 12%, 18%, 28% rows)

**Tab 2: ITC Tracker**
- Vendor-wise table: Vendor, GSTIN, Invoice #, Date, Amount, CGST, SGST, IGST
- Total ITC row at bottom in bold

**Tab 3: HSN Summary**
- Code, Description, UQC (unit), Quantity, Taxable Value, CGST, SGST, IGST columns
- Rate-wise totals at bottom

**Tab 4: GST-3B Helper**
- Pre-filled table matching GST-3B form sections:
  - 3.1(a) Outward taxable supplies (other than zero/nil/exempted)
  - 3.1(b) Outward taxable zero rated
  - 3.1(c) Other outward supplies (nil/exempt)
  - 4(A) ITC available
  - 4(B) ITC reversed
  - Net tax payable row
- User can see exactly what to enter on the GST portal

**Tab 5: Filing Status**
- Table of GST filing periods (from `/api/gst/filing-periods`)
- Each row: Period, From, To, Status badge, Filed Date, "Mark as Filed" button
- Locked periods shown with a padlock icon — data is read-only for locked periods

**Export buttons** (top right of page):
- "Download PDF" → `POST /api/reports/gst/pdf`
- "Export for Portal (JSON)" → `POST /api/reports/gst/export-json` → triggers download of the GSTN-format JSON file
- Helper text below the button: "Upload this file at gstn.gov.in → Returns → GSTR-1 → Upload JSON"

### 8.2 — Invoice creation — HSN display in preview

In the invoice preview panel on the Chat page (`/chat`, right column) and on the Invoice Detail page, show the HSN column in the line items table.

HSN code: displayed in `.t-mono` style, `--text-muted` color, in a small column to the right of the description. Label the column "HSN/SAC".

Show the tax breakdown in the invoice preview exactly matching the new PDF template layout (CGST+SGST for intrastate, IGST for interstate, with the "Amount in Words" line below the grand total).

### 8.3 — Settings page — GST Configuration section

In the Settings page (`/settings`), the "Financial Configuration" section needs a new "GST Settings" subsection:

Fields:
- State of Registration: `<Select>` with all 38 states/UTs (from `/api/hsn/states` or hardcoded)
- GST Registration Type: Regular | Composition | Unregistered
- If Composition: show Composition Rate input (1%, 2%, 5%, 6%)
- Default GST Rate: `<Select>` with 0%, 5%, 12%, 18%, 28% (used when HSN lookup fails)
- GST Filing Frequency: Monthly | Quarterly

"Save GST Settings" button → `PATCH /api/settings/gst`.

### 8.4 — Invoice list — add supply type column

In the Sales Invoices list table, add a small "Supply Type" column showing INTRA or INTER badge to the right of the Status column. Style: same badge component, INTRA uses `--accent-subtle`/`--accent`, INTER uses `--neutral-bg`/`--neutral`.

---

## PART 9 — NANOBOT CRON: Nightly anomaly detection

In the nanobot configuration or cron setup, add a nightly job that runs anomaly detection:

```
cron: "0 3 * * *"   (3 AM every night, after backup)
message: "Run anomaly detection scan"
```

The `briefing-morning/SKILL.md` should check for unreviewed anomalies and include them in the morning briefing if any exist:

```
🚨 ANOMALIES (2 unreviewed)
→ Possible duplicate: BILL-0041 and BILL-0029 from Rajan Traders — same amount
→ Price change: Packaging material from ABC Suppliers — 25% higher than usual
```

---

## PART 10 — TESTING

After implementing everything, test these specific scenarios end to end:

**GST Lookup tests:**
1. Message: "Cotton fabric ke liye invoice banao Raj ke liye, 200 meters ₹450/meter" → agent must call `gst_lookup("cotton fabric")`, get HSN 5208 at 5%, proceed without asking
2. Message: "Consulting service ke liye invoice banao ₹25000" → SAC 9983 at 18%
3. Message: "New item X ke liye invoice banao ₹1000" → agent gets no match, asks user for rate
4. After user confirms rate in scenario 3 → `confirm_item_gst` called → next time same item → cache hit
5. Interstate invoice: business in Maharashtra (state 27), client in Delhi (state 07) → IGST applied, not CGST+SGST
6. Intrastate invoice: both in Maharashtra → CGST+SGST applied, each at half the GST rate

**GST Report tests:**
7. "Is mahine ka GST report dikhao" → structured GSTR-1 data returned
8. "ITC kitna hai Q3 mein" → ITC summary from eligible vendor bills
9. "Portal ke liye JSON export karo" → valid JSON file downloaded
10. "GST kitna bharna padega October mein" → net liability = output tax − ITC

**PDF tests:**
11. Generate an invoice PDF → HSN column visible, CGST+SGST breakdown correct, amount in words correct
12. Generate GST report PDF → all 5 sections present, numbers match what agent reported

**Webapp tests:**
13. GST Reports page: all 5 tabs load with correct data
14. "Export for Portal" button: JSON file downloads and is parseable
15. Filing Status tab: "Mark as Filed" updates status badge
16. Settings page: update state of registration → next invoice uses new state code for supply type determination

---

## SUMMARY OF FILES CHANGED

| File | Change Type |
|---|---|
| `hermes/schema.sql` | ADD 7 new tables, ALTER 5 existing tables, seed data |
| `hermes/gst.py` | NEW — all GST calculation functions |
| `hermes/db.py` | ADD ~15 new functions, UPDATE create_invoice, UPDATE get_gst_report |
| `scripts/data/hsn_gst_rates.csv` | NEW — HSN/SAC rate master data |
| `scripts/load_hsn_data.py` | NEW — one-time data loader |
| `scripts/provision.sh` | UPDATE — add load_hsn_data.py call |
| `nanobot/agent/tools/hermes_tools.py` | ADD 6 new tool classes, register them |
| `nanobot/agent/tools/registry.py` | UPDATE — register new tools |
| `workspace/skills/invoice-create/SKILL.md` | REWRITE GST section |
| `workspace/skills/report-gst/SKILL.md` | UPDATE |
| `workspace/skills/gst-query/SKILL.md` | NEW |
| `templates/invoice.html` | UPDATE tax breakdown section, add HSN column, add amount in words |
| `templates/report_gst.html` | REWRITE — GSTR-1 style sections |
| `webapp/backend/routers/reports.py` | UPDATE GST endpoints |
| `webapp/backend/routers/settings.py` | ADD GST settings endpoints |
| `webapp/backend/database.py` | ADD HSN lookup, GST report, ITC, liability query functions |
| `webapp/frontend/src/pages/GSTReportsPage.tsx` | UPDATE — 5 tabs, new data structure |
| `webapp/frontend/src/pages/SettingsPage.tsx` | ADD GST settings section |
| `webapp/frontend/src/pages/SalesInvoicesPage.tsx` | ADD supply type column |
| `webapp/frontend/src/pages/ChatPage.tsx` | UPDATE invoice preview — HSN + tax breakdown |
| `webapp/frontend/src/pages/InvoiceDetailPage.tsx` | UPDATE tax display — CGST/SGST/IGST |

---

*Read this entire document before writing any code.*
*Implement bottom-up: DB schema → gst.py → db.py → tools → skills → PDF templates → API → frontend.*
*Run the 16 test scenarios before declaring this complete.*
