---
name: settings-manage
description: View or change HERMES system settings and business configuration. Use when the user says "settings dikhao", "OpenRouter key change karo", "business name update karo", "GST number add karo", "briefing time change karo", "bank details update karo", "logo change karo", or any configuration or setup change for the HERMES system.
---

# Settings Manage

View and update all HERMES configuration — business info, API keys, preferences, and system settings.

## Settings Categories

### 1. Business Information

Fields the user can view/update:
- Business name
- Owner name
- GSTIN (15-character GST number)
- Business address (for invoice headers)
- Phone number
- Email
- Business logo (image file)
- State (for GST calculations)

```
Tool: db.getBusinessInfo()
Tool: db.updateBusinessInfo({field: value})
```

### 2. Bank & Payment Details

Shown on invoice footer:
- Bank name
- Account number
- IFSC code
- Account holder name
- UPI ID (for QR code on invoices)

```
Tool: db.getBankDetails()
Tool: db.updateBankDetails({...})
```

### 3. OpenRouter API Key

Critical — without this, LLM features don't work.

```
"OpenRouter key change karo" →
Ask: "Naya API key paste karein (sk-or-v1-...)"
Validate format: starts with sk-or-v1-
Tool: config.setApiKey(newKey)
Test: make a small test API call to verify
```

On success: "✅ API key update ho gayi aur work kar rahi hai!"
On failure: "❌ Key kaam nahi kar rahi. OpenRouter dashboard pe check karein."

### 4. Notification Preferences

- Morning briefing time (default: 8:00 AM)
- Briefing timezone (default: Asia/Kolkata)
- Payment reminder days before due (default: 3 days)
- Overdue reminder frequency (default: every 2 days)

```
"Briefing time 9 baje karo" →
Tool: config.set('briefing_time', '09:00')
Tool: wakeup.reschedule('briefing-morning', '09:00 Asia/Kolkata')
"✅ Ab se subah 9 baje briefing milegi!"
```

### 5. Invoice Defaults

- Default GST rate (default: 18%)
- Default due days (default: 30)
- Invoice prefix (default: INV)
- Invoice starting number
- Invoice footer note (custom thank-you text)

### 6. View All Settings

"Settings dikhao" → display full settings panel:

```
⚙️ HERMES Settings

BUSINESS:
  Name:     [Business Name]
  GSTIN:    07AABCR1234A1Z5
  Address:  [Address]
  State:    Delhi
  Phone:    9876543210
  Logo:     ✅ Uploaded

BANK DETAILS:
  Bank:     HDFC Bank
  Account:  XXXXXXXX5678
  IFSC:     HDFC0001234
  UPI:      business@upi

OPENROUTER:
  API Key:  sk-or-v1-••••••••••• [Update]
  Model:    anthropic/claude-3-haiku
  Status:   ✅ Connected

NOTIFICATIONS:
  Morning briefing: 8:00 AM IST ✅
  Reminder lead time: 3 days
  Overdue frequency: Every 2 days

INVOICE DEFAULTS:
  GST Rate:  18%
  Due days:  30
  Prefix:    INV
  Footer:    "Thank you for your business!"

Kya change karna hai?
```

## Logo Upload

"Logo upload karo" → user sends image via Telegram:
```
1. telegram.downloadFile(fileId)
2. Validate: image format, size < 2MB
3. Resize to 300×100px if needed
4. Save to data/config/logo.png
5. db.updateBusinessInfo({logo_path: ...})
"✅ Logo update ho gaya! Agli invoice pe dikhega."
```

## First-Time Setup

If running for first time (settings empty):
Walk through setup step by step:
1. Business name
2. GSTIN
3. Address
4. Bank details
5. OpenRouter key
6. Briefing time preference

"Chalo setup karte hain! Kuch simple sawaal hain."
