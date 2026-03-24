import sqlite3
import os

schema_addition = """
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
"""

schema_path = r"d:\HERMES\hermes\schema.sql"
with open(schema_path, "a", encoding="utf-8") as f:
    f.write("\n\n" + schema_addition)
    
print("Added schema.")
