db_addition = """
def enqueue_upload(db_path: str, original_path: str, filename: str,
                   file_type: str, source: str = 'webapp') -> int:
    \"\"\"Add a file to the processing queue. Returns queue item id.\"\"\"
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO upload_queue (original_path, filename, file_type, source) "
        "VALUES (?, ?, ?, ?)",
        (original_path, filename, file_type, source)
    )
    conn.commit()
    return cur.lastrowid

def get_queued_upload(db_path: str) -> dict | None:
    \"\"\"Returns the oldest queued item, or None. Called by background thread.\"\"\"
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM upload_queue WHERE status = 'queued' "
        "ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None

def update_upload_status(db_path: str, queue_id: int, status: str,
                          ocr_result: str = None, ocr_confidence: float = None,
                          error_message: str = None, linked_bill_id: int = None) -> None:
    conn = get_conn(db_path)
    conn.execute(\"\"\"
        UPDATE upload_queue SET
          status         = ?,
          ocr_result     = COALESCE(?, ocr_result),
          ocr_confidence = COALESCE(?, ocr_confidence),
          error_message  = COALESCE(?, error_message),
          linked_bill_id = COALESCE(?, linked_bill_id),
          updated_at     = CURRENT_TIMESTAMP
        WHERE id = ?
    \"\"\", (status, ocr_result, ocr_confidence, error_message, linked_bill_id, queue_id))
    conn.commit()

def increment_retry_count(db_path: str, queue_id: int) -> int:
    \"\"\"Increments retry count. Returns new count.\"\"\"
    conn = get_conn(db_path)
    cur = conn.execute(
        "UPDATE upload_queue SET retry_count = retry_count + 1 WHERE id = ? "
        "RETURNING retry_count", (queue_id,)
    )
    conn.commit()
    row = cur.fetchone()
    return row[0] if row else 0

def get_queue_listing(db_path: str, limit: int = 50) -> list[dict]:
    \"\"\"Returns recent queue items for the webapp queue status display.\"\"\"
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM upload_queue ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    return [dict(r) for r in rows]

def get_queue_item(db_path: str, queue_id: int) -> dict | None:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM upload_queue WHERE id = ?", (queue_id,)
    ).fetchone()
    return dict(row) if row else None
"""

db_path = r"d:\HERMES\hermes\db.py"
with open(db_path, "a", encoding="utf-8") as f:
    f.write("\n\n" + db_addition)
    
print("Added DB functions.")
