import base64
import json
import os
import requests
from io import BytesIO
from PIL import Image

def _resize_and_encode_image(image_path: str, max_size: int = 1024) -> str:
    """Resize an image to a maximum dimension and return its base64 encoding."""
    with Image.open(image_path) as img:
        # Convert to RGB to avoid issues with alpha channels inside JPEGs
        if img.mode != "RGB":
            img = img.convert("RGB")
            
        width, height = img.size
        
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(max_size * (height / width))
            else:
                new_height = max_size
                new_width = int(max_size * (width / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def extract_receipt(image_path: str, openrouter_api_key: str, ocr_model: str = "google/gemini-2.5-flash") -> dict:
    """
    Extracts expense details from a receipt image using an OpenRouter Vision LLM.
    Returns: {vendor, date, amount, items, category, confidence, raw_response, success}
    """
    error_dict = {
        "vendor": None,
        "date": None,
        "amount": None,
        "items": [],
        "category": "other",
        "confidence": 0.0,
        "raw_response": "",
        "success": False
    }

    if not os.path.exists(image_path):
        error_dict["raw_response"] = f"File not found: {image_path}"
        return error_dict

    try:
        base64_image = _resize_and_encode_image(image_path)
    except Exception as e:
        error_dict["raw_response"] = f"Image processing failed: {str(e)}"
        return error_dict

    prompt = (
        "Extract from this receipt: vendor name, date (YYYY-MM-DD), total amount (number only), "
        "line items if visible (list of objects with 'description', 'amount'), and expense category "
        "(choose one: rent/utilities/supplies/travel/food/salary/other). "
        "Return ONLY valid JSON with keys: vendor, date, amount, items, category, confidence (0.0 to 1.0). "
        "Do not include markdown blocks like ```json."
    )

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nanobot-hermes.local", 
        "X-Title": "HERMES OCR Pipeline"
    }

    payload = {
        "model": ocr_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        # Ensure we got a valid response structure
        if "choices" not in data or len(data["choices"]) == 0:
            error_dict["raw_response"] = f"Invalid API response: {json.dumps(data)}"
            return error_dict

        content = data["choices"][0].get("message", {}).get("content", "").strip()
        
        # Clean up potential markdown formatting if the model ignored instructions
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        error_dict["raw_response"] = content

        try:
            parsed = json.loads(content)
            
            # Map parsed JSON properties to expected output
            return {
                "vendor": parsed.get("vendor"),
                "date": parsed.get("date"),
                "amount": parsed.get("amount"),
                "items": parsed.get("items", []),
                "category": parsed.get("category", "other"),
                "confidence": float(parsed.get("confidence", 0.0)),
                "raw_response": content,
                "success": True
            }
        except json.JSONDecodeError:
            return error_dict

    except Exception as e:
        error_dict["raw_response"] = f"API request failed: {str(e)}"
        return error_dict
