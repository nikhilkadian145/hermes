-- =============================================================================
-- HERMES Database Schema
-- SQLite · One file per business · All financial data
-- =============================================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- business — single row, the owner's business settings
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS business (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    name            TEXT NOT NULL DEFAULT '',
    owner_name      TEXT NOT NULL DEFAULT '',
    address         TEXT NOT NULL DEFAULT '',
    city            TEXT NOT NULL DEFAULT '',
    state           TEXT NOT NULL DEFAULT '',
    pin             TEXT NOT NULL DEFAULT '',
    gstin           TEXT NOT NULL DEFAULT '',
    phone           TEXT NOT NULL DEFAULT '',
    email           TEXT NOT NULL DEFAULT '',
    bank_name       TEXT NOT NULL DEFAULT '',
    account_number  TEXT NOT NULL DEFAULT '',
    ifsc            TEXT NOT NULL DEFAULT '',
    upi_id          TEXT NOT NULL DEFAULT '',
    web_password_hash TEXT NOT NULL DEFAULT '',
    currency        TEXT NOT NULL DEFAULT 'INR',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Ensure exactly one row exists
INSERT OR IGNORE INTO business (id) VALUES (1);

-- ---------------------------------------------------------------------------
-- clients — customers of the business
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    phone       TEXT NOT NULL DEFAULT '',
    email       TEXT NOT NULL DEFAULT '',
    address     TEXT NOT NULL DEFAULT '',
    gstin       TEXT NOT NULL DEFAULT '',
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- invoices — invoice header
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number  TEXT NOT NULL UNIQUE,
    client_id       INTEGER NOT NULL REFERENCES clients(id),
    issue_date      TEXT NOT NULL DEFAULT (date('now')),
    due_date        TEXT NOT NULL,
    subtotal        REAL NOT NULL DEFAULT 0,
    tax_rate        REAL NOT NULL DEFAULT 0,
    tax_amount      REAL NOT NULL DEFAULT 0,
    total           REAL NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft','sent','paid','overdue','cancelled')),
    notes           TEXT NOT NULL DEFAULT '',
    pdf_path        TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- invoice_items — line items on an invoice
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoice_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id  INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity    REAL NOT NULL DEFAULT 1,
    unit_price  REAL NOT NULL DEFAULT 0,
    amount      REAL NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- payments — payments received against invoices
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER NOT NULL REFERENCES invoices(id),
    client_id       INTEGER NOT NULL REFERENCES clients(id),
    amount          REAL NOT NULL,
    payment_date    TEXT NOT NULL DEFAULT (date('now')),
    mode            TEXT NOT NULL DEFAULT 'other'
                        CHECK (mode IN ('cash','upi','bank','cheque','other')),
    reference       TEXT NOT NULL DEFAULT '',
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- expenses — business expenses
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL DEFAULT (date('now')),
    description     TEXT NOT NULL DEFAULT '',
    category        TEXT NOT NULL DEFAULT 'other'
                        CHECK (category IN ('rent','utilities','supplies','travel',
                                            'food','salary','other')),
    amount          REAL NOT NULL DEFAULT 0,
    vendor          TEXT NOT NULL DEFAULT '',
    receipt_path    TEXT NOT NULL DEFAULT '',
    ocr_raw         TEXT NOT NULL DEFAULT '',
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- quotations — quotes before invoice
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quotations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_number    TEXT NOT NULL UNIQUE,
    client_id           INTEGER NOT NULL REFERENCES clients(id),
    issue_date          TEXT NOT NULL DEFAULT (date('now')),
    valid_until         TEXT NOT NULL,
    subtotal            REAL NOT NULL DEFAULT 0,
    tax_rate            REAL NOT NULL DEFAULT 0,
    tax_amount          REAL NOT NULL DEFAULT 0,
    total               REAL NOT NULL DEFAULT 0,
    status              TEXT NOT NULL DEFAULT 'draft'
                            CHECK (status IN ('draft','sent','accepted','rejected')),
    notes               TEXT NOT NULL DEFAULT '',
    pdf_path            TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- quotation_items — line items on a quotation
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quotation_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_id    INTEGER NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    quantity        REAL NOT NULL DEFAULT 1,
    unit_price      REAL NOT NULL DEFAULT 0,
    amount          REAL NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- reminders — payment reminders sent
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reminders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER NOT NULL REFERENCES invoices(id),
    client_id       INTEGER NOT NULL REFERENCES clients(id),
    sent_at         TEXT NOT NULL DEFAULT (datetime('now')),
    channel         TEXT NOT NULL DEFAULT 'telegram'
                        CHECK (channel IN ('telegram','whatsapp','sms')),
    message_text    TEXT NOT NULL DEFAULT ''
);

-- ---------------------------------------------------------------------------
-- udhaar — informal credit tracking
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS udhaar (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT NOT NULL,
    phone       TEXT NOT NULL DEFAULT '',
    amount      REAL NOT NULL,
    direction   TEXT NOT NULL CHECK (direction IN ('given','received')),
    date        TEXT NOT NULL DEFAULT (date('now')),
    notes       TEXT NOT NULL DEFAULT '',
    settled     INTEGER NOT NULL DEFAULT 0,
    settled_at  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- chat_messages — webapp chat interface messages
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'done')),
  metadata TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_conv ON chat_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_pending ON chat_messages(status, created_at)
  WHERE status = 'pending' AND role = 'user';

-- ===========================================================================
-- GST & TAX SYSTEM TABLES
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- hsn_master — HSN/SAC code → GST rate lookup (populated from CSV)
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- item_gst_cache — business-specific learned HSN mappings
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- gst_filing_periods — filing period tracking
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- tds_categories — standard TDS sections and rates
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tds_categories (
  id          INTEGER PRIMARY KEY,
  section     TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  rate_individual REAL NOT NULL,
  rate_company    REAL NOT NULL,
  threshold   REAL NOT NULL,
  is_active   INTEGER DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- notifications — in-app notifications written by agent, read by webapp
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- anomalies — anomaly detection results
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- indian_states — all 38 Indian state/UT codes
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- Seed TDS categories
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- upload_queue — handles background processing of uploaded bills
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS upload_queue (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  filename    TEXT NOT NULL,
  file_size   INTEGER NOT NULL,
  status      TEXT NOT NULL DEFAULT 'queued'
              CHECK(status IN ('queued', 'processing', 'review_needed', 'finalized', 'error')),
  expense_id  INTEGER REFERENCES expenses(id),
  error_message TEXT,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- expense_items — line items on a purchase bill (expense)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expense_items (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  expense_id  INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  quantity    REAL NOT NULL DEFAULT 1,
  unit_price  REAL NOT NULL DEFAULT 0,
  amount      REAL NOT NULL DEFAULT 0,
  hsn_code    TEXT,
  gst_rate    REAL DEFAULT 0,
  cgst_amount REAL DEFAULT 0,
  sgst_amount REAL DEFAULT 0,
  igst_amount REAL DEFAULT 0,
  cess_amount REAL DEFAULT 0,
  taxable_amount REAL DEFAULT 0
);

-- ===========================================================================
-- ALTER existing tables for GST columns (safe ADD COLUMN with defaults)
-- ===========================================================================

-- invoice_items: per-item GST tracking
ALTER TABLE invoice_items ADD COLUMN hsn_code TEXT DEFAULT NULL;
ALTER TABLE invoice_items ADD COLUMN gst_rate REAL DEFAULT NULL;
ALTER TABLE invoice_items ADD COLUMN cgst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN sgst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN igst_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN cess_amount REAL DEFAULT 0;
ALTER TABLE invoice_items ADD COLUMN taxable_amount REAL DEFAULT NULL;

-- invoices: supply type and full tax breakdown
ALTER TABLE invoices ADD COLUMN supply_type TEXT DEFAULT 'intrastate';
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
ALTER TABLE invoices ADD COLUMN total_in_words TEXT DEFAULT NULL;

-- clients: GST registration details
ALTER TABLE clients ADD COLUMN registration_type TEXT DEFAULT 'regular';
ALTER TABLE clients ADD COLUMN state_code TEXT DEFAULT NULL;
ALTER TABLE clients ADD COLUMN pan TEXT DEFAULT NULL;
ALTER TABLE clients ADD COLUMN client_type TEXT DEFAULT 'customer';
ALTER TABLE clients ADD COLUMN tds_applicable INTEGER DEFAULT 0;
ALTER TABLE clients ADD COLUMN tds_section TEXT DEFAULT NULL;

-- expenses: GST on purchases (ITC tracking)
ALTER TABLE expenses ADD COLUMN hsn_code TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN gst_rate REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN cgst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN sgst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN igst_amount REAL DEFAULT 0;
ALTER TABLE expenses ADD COLUMN itc_eligible INTEGER DEFAULT 1;
ALTER TABLE expenses ADD COLUMN vendor_gstin TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN bill_number TEXT DEFAULT NULL;
ALTER TABLE expenses ADD COLUMN bill_date TEXT DEFAULT NULL;

-- business: GST registration details
ALTER TABLE business ADD COLUMN state_code TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN state_name TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN registration_type TEXT DEFAULT 'regular';
ALTER TABLE business ADD COLUMN composition_rate REAL DEFAULT NULL;
ALTER TABLE business ADD COLUMN gst_filing_frequency TEXT DEFAULT 'monthly';
ALTER TABLE business ADD COLUMN pan TEXT DEFAULT NULL;
ALTER TABLE business ADD COLUMN default_gst_rate REAL DEFAULT 18.0;

-- ---------------------------------------------------------------------------
-- bank_statement_entries — imported rows for reconciliation
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bank_statement_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    description TEXT NOT NULL,
    reference   TEXT NOT NULL DEFAULT '',
    amount      REAL NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('debit','credit')),
    status      TEXT NOT NULL DEFAULT 'unmatched' CHECK (status IN ('unmatched','matched','ignored')),
    matched_to_payment_id INTEGER REFERENCES payments(id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- accounts — Chart of Accounts
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('asset','liability','equity','revenue','expense')),
    parent_id   INTEGER REFERENCES accounts(id),
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Insert default chart of accounts (basic skeleton)
INSERT OR IGNORE INTO accounts (id, code, name, type, parent_id) VALUES 
(1, '1000', 'Assets', 'asset', NULL),
(2, '1100', 'Cash & Cash Equivalents', 'asset', 1),
(3, '1200', 'Accounts Receivable', 'asset', 1),
(4, '2000', 'Liabilities', 'liability', NULL),
(5, '2100', 'Accounts Payable', 'liability', 4),
(6, '2200', 'GST Payable', 'liability', 4),
(7, '3000', 'Equity', 'equity', NULL),
(8, '4000', 'Revenue', 'revenue', NULL),
(9, '4100', 'Sales', 'revenue', 8),
(10, '5000', 'Expenses', 'expense', NULL),
(11, '5100', 'Cost of Goods Sold', 'expense', 10),
(12, '5200', 'Operating Expenses', 'expense', 10);

-- ---------------------------------------------------------------------------
-- mapping_rules — Auto-categorization rules
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mapping_rules (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_type    TEXT NOT NULL CHECK (condition_type IN ('exact_match', 'contains', 'starts_with')),
    match_value       TEXT NOT NULL,
    map_to_account_id INTEGER NOT NULL REFERENCES accounts(id),
    active            INTEGER NOT NULL DEFAULT 1,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);



CREATE TABLE IF NOT EXISTS upload_queue (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  original_path   TEXT NOT NULL,
  filename        TEXT NOT NULL,
  file_type       TEXT NOT NULL CHECK(file_type IN ('pdf', 'jpg', 'jpeg', 'png', 'tiff')),
  status          TEXT NOT NULL DEFAULT 'queued'
                  CHECK(status IN ('queued', 'processing', 'review', 'finalized', 'error')),
  source          TEXT NOT NULL DEFAULT 'webapp'
                  CHECK(source IN ('webapp', 'telegram')),
  ocr_result      TEXT,          -- JSON string of extracted data
  ocr_confidence  REAL,          -- overall confidence score 0.0-1.0
  error_message   TEXT,          -- populated if status = 'error'
  linked_bill_id  INTEGER,       -- FK to invoice_items or a bills table once created
  retry_count     INTEGER DEFAULT 0,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_upload_queue_status
  ON upload_queue(status, created_at);
