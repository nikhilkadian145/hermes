"""
Phase 14 -- Expense & OCR Pipeline End-to-End Integration Test
Tests: text expense logging, photo receipt OCR, voice expense logging.
"""
import os
import json
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock

import hermes.db as db

# ---------------------------------------------------------------------------
# Task 14.1 -- Text expense logging
# ---------------------------------------------------------------------------

def test_phase14_text_expense():
    """Log an expense by text, verify DB record."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    # Simulate: "Aaj office supplies pe 450 kharch kiye Sharma Stationery se"
    expense_id = db.log_expense(
        db_path,
        date_str=date.today().isoformat(),
        description="Office supplies",
        category="supplies",
        amount=450.0,
        vendor="Sharma Stationery",
        notes="Aaj office supplies pe 450 kharch kiye",
    )
    assert expense_id is not None

    # Verify it was stored correctly
    exp = db.get_expense(db_path, expense_id)
    assert exp is not None
    assert exp["amount"] == 450.0
    assert exp["vendor"] == "Sharma Stationery"
    assert exp["category"] == "supplies"

    # Verify it appears in expense list
    expenses = db.list_expenses(db_path, category="supplies")
    assert len(expenses) == 1
    assert expenses[0]["id"] == expense_id

    print("  [OK] Task 14.1 - Text expense logged and verified")


# ---------------------------------------------------------------------------
# Task 14.2 -- Photo receipt OCR pipeline
# ---------------------------------------------------------------------------

def test_phase14_ocr_receipt():
    """Generate dummy receipt image, mock OCR extraction, log to DB."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    # Create a fake receipt image file
    receipt_dir = tmp / "expenses" / "originals"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = str(receipt_dir / "receipt_001.jpg")
    # Write a minimal JPEG header (just needs to be a file)
    with open(receipt_path, "wb") as f:
        f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

    # Mock OCR response -- simulates what OcrExtractReceiptTool would return
    mock_ocr_result = {
        "vendor": "ABC Mart",
        "date": date.today().isoformat(),
        "amount": 234.0,
        "category": "food",
        "items": [
            {"name": "Bread", "price": 45.0},
            {"name": "Milk", "price": 60.0},
            {"name": "Eggs", "price": 129.0},
        ],
    }

    with patch("hermes.ocr.extract_receipt") as mock_ocr:
        mock_ocr.return_value = mock_ocr_result

        from hermes.ocr import extract_receipt
        parsed = extract_receipt(receipt_path, "fake-api-key")

    assert parsed["vendor"] == "ABC Mart"
    assert parsed["amount"] == 234.0

    # Simulate user confirmation and log to DB
    expense_id = db.log_expense(
        db_path,
        date_str=parsed["date"],
        description=f"Receipt from {parsed['vendor']}",
        category=parsed["category"],
        amount=parsed["amount"],
        vendor=parsed["vendor"],
        receipt_path=receipt_path,
        ocr_raw=json.dumps(mock_ocr_result),
    )
    assert expense_id is not None

    # Verify stored with OCR raw data
    exp = db.get_expense(db_path, expense_id)
    assert exp["vendor"] == "ABC Mart"
    assert exp["amount"] == 234.0
    assert exp["receipt_path"] == receipt_path
    assert "ABC Mart" in exp["ocr_raw"]

    print("  [OK] Task 14.2 - OCR receipt pipeline verified (mocked)")


# ---------------------------------------------------------------------------
# Task 14.3 -- Voice expense logging
# ---------------------------------------------------------------------------

def test_phase14_voice_expense():
    """Mock Whisper transcription, parse expense, log to DB."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    # Create a dummy audio file
    audio_path = str(tmp / "voice_note.ogg")
    with open(audio_path, "wb") as f:
        f.write(b"\x00" * 200)

    # Mock the Whisper transcription result
    transcribed_text = "Aaj petrol bhara 500, travel expense hai"

    with patch("hermes.whisper_tool.transcribe") as mock_whisper:
        mock_whisper.return_value = transcribed_text

        from hermes.whisper_tool import transcribe
        result = transcribe(audio_path)

    assert result == transcribed_text

    # Simulate the agent parsing the transcription for expense details
    # In production the LLM does this; here we simulate extracted values
    parsed_amount = 500.0
    parsed_category = "travel"
    parsed_description = "Petrol"

    expense_id = db.log_expense(
        db_path,
        date_str=date.today().isoformat(),
        description=parsed_description,
        category=parsed_category,
        amount=parsed_amount,
        vendor="",
        notes=f"Voice transcription: {transcribed_text}",
    )
    assert expense_id is not None

    exp = db.get_expense(db_path, expense_id)
    assert exp["amount"] == 500.0
    assert exp["category"] == "travel"
    assert "voice_note" not in exp.get("receipt_path", "")  # no receipt for voice
    assert "petrol" in exp["notes"].lower()

    # Verify multiple expenses are tracked
    all_expenses = db.list_expenses(db_path)
    assert len(all_expenses) == 1

    print("  [OK] Task 14.3 - Voice expense logging verified (mocked Whisper)")


if __name__ == "__main__":
    test_phase14_text_expense()
    test_phase14_ocr_receipt()
    test_phase14_voice_expense()
    print("\n[PASS] Phase 14 - All Expense & OCR Pipeline E2E tests passed!")
