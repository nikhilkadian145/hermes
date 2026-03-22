---
name: client-manage
description: Add, update, view, or manage client records. Use when the user says "naya client add karo", "Raj ka address update karo", "client list dikhao", "client details kya hain", "GSTIN add karo", "client delete karo", or any action related to managing client contact and billing information.
---

# Client Manage

Add, view, edit, and maintain client records for invoicing and tracking.

## Operations

### 1. Add New Client

Triggered by: "naya client", "client add karo", "new client"

Collect (ask in one message):
- **Name** (required)
- **Phone number** (optional but recommended)
- **Email** (optional)
- **Business address** (for invoice)
- **GSTIN** (for B2B invoicing — 15-char alphanumeric)
- **State** (for IGST vs CGST+SGST determination)

```
Tool: db.createClient({name, phone, email, address, gstin, state})
```

Confirm:
```
✅ Client saved!

👤 Raj Traders
📞 9876543210
📍 Delhi (Same state — CGST+SGST applicable)
🏷️ GSTIN: 07AABCR1234A1Z5

Invoice banani ho to batao!
```

### 2. View Client Details

Triggered by: "Raj ki details dikhao", "client info"

```
Tool: db.getClient(name)
```

Display:
```
👤 Raj Traders
────────────────────────────────
Phone:    9876543210
Email:    raj@example.com
Address:  Shop 12, Karol Bagh, Delhi
GSTIN:    07AABCR1234A1Z5
State:    Delhi

Invoice History:
  Total invoiced: ₹2,34,000 (12 invoices)
  Total paid:     ₹2,12,760
  Outstanding:    ₹21,240

Last invoice: INV-2024-0042 (01 Jan 2025)
```

### 3. List All Clients

Triggered by: "clients dikhao", "client list", "sab clients"

```
Tool: db.getAllClients()
```

Display sorted by recent activity:
```
👥 Clients (8 total)

1. Raj Traders          ₹21,240 due  📞 9876543210
2. Meena Stores         ₹8,500 due   📞 9812345678
3. Kumar & Sons         ✅ No dues   📞 9823456789
4. Sharma Tech          ₹25,000 due  📞 9834567890
...
```

### 4. Update Client

Triggered by: "Raj ka phone update karo", "address change karo", "GSTIN add karo"

```
Tool: db.updateClient(clientId, {field: newValue})
```

Confirm the specific change before saving:
"Raj Traders ka phone 9876543210 se 9999999999 karna hai — sahi hai?"

### 5. Delete / Archive Client

Triggered by: "Raj ko hatao", "client delete karo"

- Never hard-delete if invoices exist — archive instead
- Show warning: "Raj Traders ke 12 invoices hain. Delete ki jagah archive karein?"
- On archive: `db.archiveClient(clientId)` — hidden from lists but data preserved

## GSTIN Validation

When GSTIN entered, validate format:
- 15 characters
- First 2 digits = state code (01–38)
- Characters 3–12 = PAN number
- Character 13 = entity number
- Character 14 = Z (default)
- Character 15 = checksum digit

If invalid: "GSTIN format sahi nahi lagta. Check karke dobara enter karo."

## Duplicate Detection

Before creating: check if client with similar name exists.
"'Raj Trade' naam ka client already hai — same hai ya alag?"
