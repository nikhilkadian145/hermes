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
