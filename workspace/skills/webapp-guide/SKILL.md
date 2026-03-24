---
name: webapp-guide
description: Navigate users through the HERMES webapp — page locations, features, troubleshooting, notifications, reports, GST filing, and document management.
---
# webapp-guide

## When to use this skill

Use when the user:
- Asks where something is on the webapp or how to find it
- Reports something missing, blank, or wrong on the webapp
- Asks how to download a report, invoice, or document
- Asks about their webapp URL or how to open it on their phone
- Reports the webapp not loading
- Asks what a section or page does
- Asks how to do something that can be done on the webapp
- Asks about a notification or anomaly they saw on the webapp
- Asks about uploading a bill or reviewing an extracted document

---

## What the webapp is

HERMES has a full web dashboard at the customer's domain (e.g. `https://theirbusiness.com`).
It works on both phone and laptop — same URL, responsive layout.

The webapp and the agent share one SQLite database on the same VM.
Anything the agent creates, modifies, or deletes is instantly visible on the webapp.
No sync. No delay. No refresh needed in most cases.

The webapp has its own Chat tab where the owner can talk to the agent from a browser.
It is the same agent with the same tools. Conversation history is separate from Telegram
but all data (invoices, payments, contacts) is fully shared.

On first load, a setup wizard runs if the business profile is not filled in.
After setup, all pages are accessible immediately with no login required — the VM is
the security boundary (accessed via SSH tunnel or local network).

---

## Complete page map

### OVERVIEW

**Dashboard** — `/`
- 6 KPI cards: Revenue MTD, Expenses MTD, Net Profit, Outstanding Receivables,
  Overdue Invoices, GST Liability estimate
- Each card shows delta vs previous period and a 7-day sparkline
- Revenue vs Expenses line chart (last 12 months, toggle 3M/6M/12M)
- Expense breakdown donut chart by category
- Invoice status stacked bar chart (last 6 months)
- Quick Actions: Upload Documents, Chat with HERMES, View Reports
- Activity feed: last 20 events (invoice created, payment received, etc.) — live, polls every 30s
- Overdue alert banner appears automatically when any invoice is overdue
- Setup checklist widget (visible until all 5 onboarding steps are completed)

---

### OPERATIONS

**Chat with HERMES** — `/chat`
- Full chat interface identical in capability to Telegram
- Desktop: 60% chat, 40% live invoice preview panel (updates as invoice is discussed)
- Mobile: full screen chat, preview via "Preview" button bottom sheet
- When agent creates an invoice here, an inline invoice card appears in the chat
  with "View Invoice" and "Download PDF" buttons
- Conversation history sidebar on desktop — past conversations searchable
- Suggested prompts shown when chat is empty
- Attach documents directly in chat via paperclip icon — agent processes them
- Voice input button (microphone) for hands-free dictation
- Floating chat bubble on every page (desktop: opens a popover, mobile: opens full chat)

**Upload Documents** — `/upload`
- Drag-and-drop zone for vendor bill documents
- Accepted: PDF, JPG, PNG, TIFF — up to 25MB per file, up to 20 files at once
- Each file gets a row in the processing queue table showing live status:
  QUEUED → PROCESSING → REVIEW NEEDED or FINALIZED or ERROR
- "Review →" button appears on REVIEW NEEDED rows — takes user to Bill Review page
- "Retry" button on ERROR rows — requeues the file for another OCR attempt
- Processing is automatic and background — user does not need to wait on the page
- Note: bills uploaded here go through OCR and require user confirmation before saving.
  Bills logged via Telegram photo go through the same OCR but are confirmed via Telegram.

---

### FINANCE

**Sales Invoices** — `/invoices/sales`
- All outgoing invoices to customers
- Filter by: status (Draft/Sent/Paid/Overdue/Void), customer, date range, amount range
- Filter bar is always visible — "Clear filters" appears when any filter is active
- Summary bar above table: "Showing X invoices · Total ₹X · Paid ₹X · Outstanding ₹X"
- Table columns: Invoice #, Customer, Issue Date, Due Date (red if overdue),
  Amount, GST, Status badge, Supply Type (INTRA/INTER), Actions
- Row actions: View, Download PDF, Mark as Paid, Void
- Bulk actions (appear when rows selected): Download ZIP, Mark as Paid, Export CSV
- Pagination: 50 rows per page
- "New Invoice" button opens Chat with a prefilled context — invoices are created by talking

**Invoice Detail** — `/invoices/sales/:id`
- Desktop: rendered invoice preview (left 60%) + action panel (right 40%)
- Mobile: invoice preview on top, action panel scrolled below
- Invoice preview shows: business logo, addresses, line items with HSN codes,
  CGST/SGST or IGST breakdown, grand total, amount in words
- Action panel: status badge, Download PDF (primary button), Mark as Paid,
  Void button, invoice timeline (Created → Sent → Paid), payment history table
- Notes field auto-saves on blur
- Download PDF: fetches file directly from VM filesystem — should complete in under 2 seconds

**Purchase Bills** — `/invoices/purchases`
- All vendor bills — both Telegram-logged and webapp-uploaded
- Same filter/sort/pagination as sales invoices
- REVIEW status rows have a highlighted left border — these need user action
- PROCESSING rows show a pulsing badge — auto-refreshes every 5 seconds
- Click any row → Bill Detail page

**Bill Review** — `/invoices/purchases/review/:id`
- Side-by-side layout: original document (left), extracted data form (right)
- Left panel: original PDF or image exactly as uploaded — zoom, rotate, fit-to-width controls
- Right panel: all OCR-extracted fields as editable inputs
- Each field has a confidence indicator dot: green ≥90%, amber 70–90%, red <70%
- Red-confidence fields are focused on page load — draw attention to uncertain extractions
- Editable line items table with add/remove row capability
- HERMES Notes box: AI observations about this specific document
  (e.g. "This vendor billed the same amount 12 days ago — possible duplicate")
- "Confirm & Finalize" → saves to expenses table, navigates to bills list
- "Reject & Re-upload" → discards and removes from queue

**Contacts** — `/contacts`
- Combined customer and vendor list — toggle All / Customers / Vendors
- Outstanding balance column: green (zero), amber (has balance), red (overdue)
- Search by name, GSTIN, or phone

**Contact Detail** — `/contacts/:id`
- 4 tabs: Overview, Transactions, Ledger, Notes
- Overview: total billed, total paid, outstanding balance, last payment date,
  "Download Statement" button (generates PDF)
- Transactions tab: all linked invoices with same filters as invoice list
- Ledger tab: running balance (date, description, debit, credit, balance columns),
  date range filter, "Download CSV" button
- Notes tab: free text, auto-saves

**Payments** — `/payments`
- All payment records across all clients/vendors
- "Record Payment" primary button — opens modal (desktop) or bottom sheet (mobile)
- Payment form: select invoice(s), amount, date, mode (Cash/UPI/Bank/Cheque/Card),
  reference number, notes
- Live remaining balance shown as user fills in amount
- Payments sub-page: `/payments/reconciliation` — manual bank statement matching

---

### RECORDS

**Reports** — `/reports`
- Hub page: card grid grouped by category
- Each card shows last generated date and a "Run Report →" button
- Report runs in-page (not a new tab), then download buttons appear

Report types available:

*Financial Reports:*
- P&L Statement — revenue, expenses, net profit for any date range
- Balance Sheet — assets, liabilities, equity as of any date
- Cash Flow Statement
- Trial Balance
- General Ledger — per account, any date range
- Day Book — all transactions for a specific date

*GST Reports* (also at `/reports/gst` as a dedicated page):
- GSTR-1 Summary — B2B, B2C large, B2C small sections, invoice-wise detail
- GSTR-2B Reconciliation
- GST Liability Statement — output tax minus ITC
- ITC Tracker — input tax credit from eligible vendor bills
- HSN/SAC Summary — code-wise breakdown of all supplies
- GST-3B Helper — pre-filled form matching GST-3B sections for portal filing
- Export for Portal — downloads GSTN-format JSON, upload directly at gstn.gov.in
- Filing Status tab — mark periods as filed or locked

*Receivables Reports:*
- Receivables Aging (0–30, 31–60, 61–90, 90+ days buckets)
- Customer-wise Outstanding
- Invoice Status Summary

*Payables Reports:*
- Payables Aging
- Vendor-wise Outstanding
- Bill Status Summary

*Expense Reports:*
- By Category
- By Vendor
- Month-on-Month Trend

*HERMES Intelligence Reports:*
- Anomaly Report — all flagged transactions with resolution status
- Duplicate Invoice Detection — suspected duplicate pairs
- Vendor Spend Analysis — price drift per vendor over time
- Processing Quality Report — OCR confidence scores, correction rates, error rates
- Audit Trail Report — filtered, exportable version of the full audit log

*Custom Report Builder* — `/reports/custom`
- Pick dimensions (Vendor, Customer, Category, Month, Quarter)
- Pick metrics (Total Amount, Count, Average, Min, Max)
- Add filters (date range, vendor/customer, status, amount range)
- Live preview table updates as config changes
- Save as template, download as PDF or CSV

All reports: Download PDF button and Download Excel button.
PDF generation calls the WeasyPrint engine on the VM — may take 2–5 seconds for large reports.

**Documents** — `/documents`
- File Center: every file HERMES has ever touched
- Left sidebar filter: Uploaded Documents / Generated (Invoices + Reports) / Exports
- List or grid view (toggle)
- Search by filename or linked entity
- Click any file → document viewer drawer slides in from right (desktop) / full screen (mobile)
- Viewer shows PDF or image inline — no download required to preview
- Download button in viewer header — always visible
- "Download Original" for uploaded vendor bills — serves the exact file as uploaded
- Bulk select + "Download ZIP" for multiple files

**Anomalies** — `/anomalies`
- All anomalies detected by the nightly scan (runs at 3 AM)
- Detection types: Duplicate Bill, Price Drift, Round Number Billing
- Each anomaly is a card (not a table row) with: type badge, confidence %, description,
  links to the affected records, flagged timestamp
- Three actions per card:
  - Acknowledge: "I reviewed this, it's acceptable" — card mutes
  - Escalate: flag for accountant review, add a note
  - Dismiss: mark as false positive, select a reason so agent learns
- Filter by status (Unreviewed / Acknowledged / Escalated / Dismissed) and type
- Nav sidebar badge shows unreviewed count — updates every 60 seconds
- New anomalies also appear in the Notifications bell

---

### ACCOUNTS

**Chart of Accounts** — `/accounts`
- Full tree: Assets, Liabilities, Income, Expenses, Equity
- Expand/collapse per group
- Each account: code (monospace), name, type, current balance
- Add account inline within the tree
- Edit account name — inline edit mode on pencil click
- Deactivate (not delete) accounts that have transactions

**Mapping Rules** — sub-page under `/accounts`
- Auto-categorization rules: "If vendor = X, map to account Y"
- "If description contains Z, map to account W"
- Rules are ordered — drag to reorder priority
- Toggle rules active/inactive without deleting

**Audit Trail** — `/audit`
- Immutable, read-only log of every action ever taken
- Columns: Timestamp, Source (Agent/Webapp), Action Type badge, Record (linked), Details
- Expand any row to see before/after values for edits
- Filter by date range, action type, record type
- Action types: CREATE, EDIT, DELETE, DOWNLOAD, PROCESS, EXPORT, SETTING_CHANGE
- "Export to CSV" — date-range scoped, opens a date picker modal first
- Banner states: "This log is read-only and cannot be modified"

---

### SYSTEM

**Settings** — `/settings`
Five sections in left-tab navigation (desktop) / accordion (mobile):

*Business Profile:*
Business name, logo upload (shown on all PDFs), address, GSTIN, PAN, phone, email,
industry type. Save triggers immediate update to all future PDF generation.

*Financial Configuration:*
Financial year start (April or January), default payment terms, default GST rates
(add/remove rate chips: 0% 5% 12% 18% 28%), invoice number format with live preview.

*GST Settings:*
State of registration (all 38 states/UTs), registration type (Regular/Composition/Unregistered),
composition rate if applicable, GST filing frequency (Monthly/Quarterly).
This setting determines CGST+SGST vs IGST on all new invoices.

*Invoice Appearance:*
Template selector (2–3 professional templates), accent color for PDFs,
footer text (bank details, thank you message), column toggles (HSN code,
per-unit price, discount).

*Notifications:*
Per-type toggles for in-app and email. Email digest frequency (Real-time/Daily/Weekly).
Overdue reminder cadence (Day 1 / Day 7 / Day 15).

*Data Management:*
Export all data as ZIP (full backup). Link to Import Center.
"Clear Processing Queue" in danger zone.

**Import Center** — `/settings/import`
Three import types, each with a 4-step flow:
1. Download sample CSV template
2. Upload file
3. Preview table with per-row validation (green=valid, red=error with reason)
4. "Import X valid rows, skip Y errors" confirmation

Import types: Contacts (CSV), Opening Balances (CSV/Excel), Bank Statement (CSV for reconciliation).

**System Health** — `/system`
- Backend Status card: RUNNING / DEGRADED / STOPPED — full colored background (green/amber/red)
- Queue depth, average processing time, disk usage with progress bar, uptime
- Processing Queue table: live, polls every 5 seconds
  - "Pause Queue" / "Resume Queue" toggle
  - "Reprocess All Failed" button
- Performance graph: 24-hour rolling API response time + documents/hour
- Error log: last 100 lines, syntax-colored by severity, "Download .log" button
- System status dot in top bar (green/amber/red) links here

---

## What the agent creates → where it appears

| Agent action | Appears on webapp |
|---|---|
| Create invoice | `/invoices/sales` — instantly |
| Record payment | `/payments` + invoice detail payment history |
| Log expense (text) | `/invoices/purchases` as finalized bill |
| Log expense (Telegram photo OCR, confirmed) | `/invoices/purchases` as finalized bill |
| Create client | `/contacts` |
| Update business info | `/settings` profile section |
| Generate P&L PDF | `/reports` — "Download Last Generated" link |
| Generate GST report | `/reports/gst` |
| Generate CA export bundle | `/documents` Exports section |
| Create quotation | Not directly visible — convert to invoice for it to appear |
| Run anomaly detection (nightly 3 AM) | `/anomalies` — new cards |
| Any action | `/audit` — new row immediately |

Upload via Telegram photo vs webapp upload are separate flows but both save to the same
expenses table. Telegram-logged bills appear immediately after agent confirms.
Webapp-uploaded bills appear after user confirms on the Bill Review page.

---

## Notifications — what triggers them

The bell icon badge in the top bar shows unread count. Clicking opens the panel.

| Event | Notification title |
|---|---|
| Invoice created by agent | "Invoice INV-XXXX Created" |
| Payment recorded | "Payment Received — ₹X from [client]" |
| Invoice fully paid | "Invoice INV-XXXX Fully Paid" |
| Expense logged | "Expense Recorded — ₹X [category]" |
| Bill OCR ready | "Bill Ready for Review — [filename]" |
| New anomaly detected | "[Anomaly type] — [vendor]" |
| Report PDF generated | "[Report name] Ready" |
| Invoice newly overdue | "Invoice Overdue — INV-XXXX" (runs at 7:30 AM daily) |

Notifications panel has tabs: All / Unread / Anomalies / System.
Clicking a notification marks it read and navigates to the linked record.
"Mark all as read" button in panel header.

---

## GST functionality — agent's role vs webapp's role

The agent handles GST at the transaction level:
- Calls `gst_lookup` for every line item before creating an invoice
- Determines CGST+SGST (intrastate) vs IGST (interstate) based on business and client state codes
- Stores HSN code, per-item tax breakdown, and supply type on every new invoice
- Learns from confirmed HSN codes via the item cache — same item never asked twice

The webapp handles GST at the reporting and filing level:
- `/reports/gst` shows GSTR-1 structured data (B2B, B2C, HSN summary)
- GST-3B Helper tab pre-fills the portal form sections
- "Export for Portal (JSON)" downloads GSTN-format file — user uploads manually at gstn.gov.in
- Filing Status tab tracks which periods are filed or locked

If a user asks "GST kitna bharna padega" — call `GetGstLiabilityTool` and answer directly.
If they want to file — guide them to `/reports/gst` → GST-3B Helper tab → Export JSON.

---

## Troubleshooting guide

**Dashboard blank or numbers all zero:**
Usually the VM restarted. Check `/system` — is Backend Status green?
If red: VM may be off. Guide: Google Cloud Console → Compute Engine → VM Instances → Start.
PM2 auto-starts on VM boot so webapp comes back within ~30 seconds of VM start.
If status is green but dashboard is still blank: hard refresh (Ctrl+Shift+R).

**Invoice not showing in list:**
Check the filter bar — Status filter may be hiding it. Reset to "All".
Check date range filter — if set to "This Month" and invoice is from a past month, it hides.
If filters are clear and it's missing: ask agent "INV-XXXX ka status kya hai" to verify it exists.

**PDF download not working:**
The browser may be blocking downloads from this domain. Allow downloads in browser settings.
If button is missing: PDF was not generated at creation time. Tell agent
"INV-XXXX ka PDF dobara generate karo" — agent calls `PdfGenerateInvoiceTool`.

**Bill stuck in PROCESSING or REVIEW for hours:**
Go to `/upload`. Find the stuck item, click Retry.
If it keeps failing: image quality may be too poor — re-photograph the bill in better light.

**Anomalies page empty:**
Detection runs nightly at 3 AM. On a fresh setup with little data, nothing will be flagged.
After several weeks of transactions, anomalies will appear naturally.
If it has been running for weeks and is still empty: the cron may not be firing.
That is a technical issue — contact administrator.

**Report PDF taking too long:**
Large date ranges (full financial year) with many transactions can take 10–15 seconds.
The button shows a spinner — wait for it. If it times out, try a shorter date range first.

**Webapp says "Cannot reach HERMES backend":**
Persistent red banner at top of page. FastAPI process has stopped.
VM is likely running but PM2 process `hermes-web` has crashed.
Technical fix required — contact administrator. Tell them: "PM2 hermes-web process needs restart."

**Numbers on webapp don't match what agent reported:**
Both read the same database so numbers cannot truly differ.
Most likely cause: different date range filters. Verify by asking agent with the exact same period.

**GST export JSON shows wrong data:**
The JSON reflects whatever invoices exist in the DB for that period.
If a specific invoice is missing: check if its `supply_type` is set correctly (intrastate/interstate).
If all invoices are missing: check the date range on the export — financial year vs calendar year.

---

## What the agent can and cannot do about webapp issues

**Can do:**
- Navigate user to the right page and explain what they will find there
- Regenerate a missing PDF (`PdfGenerateInvoiceTool`)
- Correct wrong data via the appropriate DB tool
- Tell user current DB values so they can compare with webapp display
- Guide non-technical users through Google Cloud Console to restart a VM
- Explain what each section and feature of the webapp does
- Run an immediate anomaly scan if user asks
- Re-trigger a report generation

**Cannot do:**
- Restart PM2 processes (no shell access from agent loop)
- Fix nginx, SSL, or DNS issues
- Modify React frontend code
- Change environment variables or .env configuration
- Access the webapp's API endpoints directly

For anything beyond the above, respond:
"Yeh technical issue hai — apne HERMES administrator ko contact karo aur yeh batao:
[describe the exact symptom in plain English for the admin]."

---

## Webapp URL

Call `DbGetBusinessInfoTool` and read the `webapp_domain` field.
If set: "Aapka webapp yahan hai: https://[domain]"
If blank: "Webapp URL setup ke time configure hota hai. Apne HERMES administrator se pooch lo."

To add the webapp to phone home screen:
Open the URL in Chrome (Android) or Safari (iOS) → tap the share/menu button →
"Add to Home Screen". The webapp is a PWA — it opens full screen like a native app.
