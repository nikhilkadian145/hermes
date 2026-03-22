---
name: expense-ocr
description: Extract and log expense details from a photo or image of a bill, receipt, or invoice sent by the user. Use when the user sends a photo/image along with "bill scan karo", "receipt add karo", "ye dekho", "expense hai ye", or simply sends a receipt/bill image without much text. Uses OCR to read the document and auto-fill expense fields.
---

# Expense OCR

Automatically extract expense details from bill/receipt photos using OCR.

## Trigger Conditions

This skill activates when:
- User sends an **image file** (jpg/png/pdf) in Telegram
- Message suggests it's a receipt/bill (or no message at all with an image)
- User explicitly asks to "scan" or "read" a bill

## Tool Call Sequence

```
1. telegram.downloadFile(fileId)           → save image to disk
2. ocr.extractText(imagePath)              → Tesseract OCR → raw text
3. llm.parseExpenseFromText(rawText)       → extract structured fields
4. [show to user for confirmation]
5. DbLogExpenseTool({...confirmed fields...})
6. db.saveReceiptImage(expenseId, path)    → link image to expense record
```

## OCR Parsing — What to Extract

From raw OCR text, identify:
- **Vendor name** — shop/restaurant/company name (usually at top)
- **Total amount** — look for "Total", "Grand Total", "Amount Due", "₹" near bottom
- **Date** — parse any date format (DD/MM/YY, DD Mon YYYY, etc.)
- **GST number** — 15-char alphanumeric starting with state code
- **Bill number** — invoice/bill/receipt number
- **Individual items** — if itemized, extract line items
- **GST amounts** — CGST, SGST, IGST amounts

## Confirmation Before Logging

Always show extracted data and ask for correction:

```
📷 Bill scan ho gayi! Ye details mili:

Vendor: Sharma Stationery
Amount: ₹1,240
Date: 14 Jan 2025
GST (18%): ₹189
Bill No: INV-887

Category suggestion: Office Supplies 📎

Sahi hai? (Category change karni ho to batao)
✅ Save | ✏️ Edit
```

## Category Auto-Suggestion

Use vendor name + line items to suggest category:
- Petrol pump → Travel
- Restaurant → Food & Entertainment  
- Electricity board → Utilities
- Hardware store → Equipment or Office Supplies
- Medical → Miscellaneous (or Employee Benefits)

If unsure, ask user to confirm category.

## Poor Quality Images

If OCR confidence is low:
```
⚠️ Image thodi blur hai, poori tarah read nahi ho paya.

Jo mila:
Amount: ₹??? (unclear)
Vendor: [unclear]

Manually enter karein? Ya clearer photo bhejein?
```

## Storage

- Original image saved to `data/expenses/originals/YYYY-MM/`
- Processed/cropped copy saved to `data/expenses/processed/`
- Linked to expense record via `receipt_image_path` field

## Batch Processing

If user sends multiple images at once, process each sequentially and confirm all before saving:
```
3 receipts mili. Ek ek check karte hain:
[1/3] Sharma Stationery...
```
