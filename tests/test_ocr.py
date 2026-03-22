import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw

from hermes.ocr import extract_receipt

def create_dummy_receipt(path: str):
    """Creates a basic image to use as a dummy receipt."""
    img = Image.new('RGB', (400, 600), color='white')
    d = ImageDraw.Draw(img)
    d.text((50, 50), "ACME GROCERY", fill='black')
    d.text((50, 100), "Date: 2023-10-25", fill='black')
    d.text((50, 150), "Milk - 2.50", fill='black')
    d.text((50, 180), "Bread - 3.00", fill='black')
    d.text((50, 220), "Total Amount: 5.50", fill='black')
    img.save(path)

@patch("hermes.ocr.requests.post")
def test_extract_receipt_success(mock_post):
    # Mock OpenRouter response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": '''```json
{
  "vendor": "ACME GROCERY",
  "date": "2023-10-25",
  "amount": 5.50,
  "items": [
    {"description": "Milk", "amount": 2.50},
    {"description": "Bread", "amount": 3.00}
  ],
  "category": "food",
  "confidence": 0.95
}
```'''
            }
        }]
    }
    mock_post.return_value = mock_response

    with TemporaryDirectory() as tmpdir:
        img_path = str(Path(tmpdir) / "receipt.jpg")
        create_dummy_receipt(img_path)
        
        result = extract_receipt(img_path, "dummy-key")
        
        assert result["success"] is True
        assert result["vendor"] == "ACME GROCERY"
        assert result["date"] == "2023-10-25"
        assert result["amount"] == 5.50
        assert result["category"] == "food"
        assert result["confidence"] == 0.95
        assert len(result["items"]) == 2

@patch("hermes.ocr.requests.post")
def test_extract_receipt_invalid_json(mock_post):
    # Mock LLM sending raw text instead of JSON
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "This receipt is from Acme Grocery for 5.50 on Oct 25."
            }
        }]
    }
    mock_post.return_value = mock_response

    with TemporaryDirectory() as tmpdir:
        img_path = str(Path(tmpdir) / "receipt.jpg")
        create_dummy_receipt(img_path)
        
        result = extract_receipt(img_path, "dummy-key")
        
        # It should fail cleanly, returning raw text but success=False
        assert result["success"] is False
        assert result["raw_response"] == "This receipt is from Acme Grocery for 5.50 on Oct 25."
        assert result["vendor"] is None

def test_extract_receipt_missing_file():
    result = extract_receipt("non_existent_file.jpg", "dummy-key")
    assert result["success"] is False
    assert "File not found" in result["raw_response"]
