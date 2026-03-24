# HERMES — Full System Testing Guide
### Pre-Shipping QA Checklist
### Complete every section in order. Do not skip ahead.
### Mark each item ✅ when confirmed working, ❌ when broken (note the issue inline).

---

> **Before you start:**
> This guide assumes a fresh VM deployment using `install.sh` and `provision.sh`.
> Do NOT test on a customer's VM. Use your own test GVM.
> Have a phone (Android or iPhone) ready alongside your laptop throughout.
> Have Telegram open on both devices logged into the test bot.
> Have the webapp URL open in Chrome on laptop and Safari/Chrome on phone.

---

## STAGE 1 — Infrastructure & Process Health

*Verify the VM is alive and all processes are running before touching any feature.*

### 1.1 — VM & Process Check

- [ ] SSH into the test VM successfully
- [ ] Run `pm2 list` — confirm exactly two processes are shown:
  - `hermes-agent` — status: `online`
  - `hermes-web` — status: `online`
- [ ] Run `pm2 logs hermes-agent --lines 20` — no crash errors in last 20 lines
- [ ] Run `pm2 logs hermes-web --lines 20` — no crash errors in last 20 lines
- [ ] Run `nginx -t` — returns `syntax is ok` and `test is successful`
- [ ] Run `curl http://localhost:5000/api/health` — returns `{"status":"ok","version":"1.0"}`
- [ ] Open webapp URL in laptop browser — page loads, no blank screen, no JS console errors
  (Open DevTools → Console tab — should be clean)

### 1.2 — Database Integrity Check

- [ ] Run `sqlite3 /home/hermes/data/db/hermes.db ".tables"` — confirm ALL these tables exist:
  `business`, `clients`, `invoices`, `invoice_items`, `payments`, `expenses`,
  `quotations`, `quotation_items`, `reminders`, `udhaar`, `hsn_master`,
  `item_gst_cache`, `gst_filing_periods`, `tds_categories`, `indian_states`,
  `notifications`, `anomalies`, `chat_messages`, `upload_queue`
- [ ] Run `sqlite3 /home/hermes/data/db/hermes.db "SELECT COUNT(*) FROM hsn_master;"` — returns a number greater than 50 (HSN data loaded)
- [ ] Run `sqlite3 /home/hermes/data/db/hermes.db "SELECT COUNT(*) FROM tds_categories;"` — returns 9
- [ ] Run `sqlite3 /home/hermes/data/db/hermes.db "SELECT name, gstin, webapp_domain FROM business;"` — returns your test business name, GSTIN, and domain

### 1.3 — Disk & System Resources

- [ ] Run `df -h /home/hermes/data` — disk usage below 80%
- [ ] Run `free -h` — at least 500MB RAM free
- [ ] Open webapp `/system` page — Backend Status card shows green "RUNNING"
- [ ] Disk usage bar on `/system` matches `df -h` reading approximately
- [ ] Uptime on `/system` shows a reasonable time since last PM2 start

---

## STAGE 2 — Business Setup & Settings

*Verify the business profile is correct before creating any financial data.*

### 2.1 — Business Profile

- [ ] Open webapp `/settings` — Business Profile section loads with correct data
- [ ] Business name matches what was entered in `onboard-tui.js`
- [ ] GSTIN is displayed correctly
- [ ] State of registration is set (GST Settings section)
- [ ] Default GST rate is set (should be 18% unless changed)
- [ ] Financial year start is correct (April for Indian businesses)
- [ ] Invoice number format shows correct preview (e.g. `INV-0001`)
- [ ] Change business name to "Test Business Updated" → Save → refresh page → new name persists
- [ ] Change it back to the correct name → Save

### 2.2 — Onboarding Checklist

- [ ] Dashboard shows the setup checklist widget if not all steps are done
- [ ] Each item in the checklist links to the correct page
- [ ] Dismiss the checklist with the X button — it disappears and does not come back on refresh

---

## STAGE 3 — Telegram Agent: Core Flows

*Test every major agent capability via Telegram first. The agent must work on Telegram
before you test the webapp. If Telegram is broken, the webapp data layer is also broken.*

### 3.1 — Basic Connectivity

- [ ] Send `/start` to the bot — agent responds in Hinglish
- [ ] Send "Namaste" — agent replies conversationally, does not call any tools
- [ ] Send a completely irrelevant message ("What is the capital of France?") —
  agent responds that it only handles business/financial topics, does not hallucinate
- [ ] Send "Mera business ka naam kya hai?" — agent calls `DbGetBusinessInfoTool`
  and returns the correct business name

### 3.2 — Client Management

- [ ] Send "Ek naya client banao — Sharma Textiles, phone 9876543210, Delhi" —
  agent creates client, confirms in Hinglish
- [ ] Send "Sharma Textiles ka GSTIN update karo — 07AABCS1234D1Z5" —
  agent updates, confirms
- [ ] Send "Sharma Textiles ki details dikhao" — agent returns correct info
- [ ] Verify on webapp `/contacts` — Sharma Textiles appears with correct details

### 3.3 — Invoice Creation with GST Lookup

- [ ] Send "Sharma Textiles ke liye invoice banao — 100 meters cotton fabric ₹450/meter" —
  agent should call `gst_lookup("cotton fabric")`, return HSN 5208 at 5%,
  NOT ask the user (cache/FTS should find it)
- [ ] Agent shows invoice summary with CGST + SGST breakdown (intrastate, both Delhi) before creating
- [ ] Confirm → agent creates invoice, sends PDF in Telegram
- [ ] PDF received in Telegram — open it, verify:
  - Business name and GSTIN correct
  - Client name correct
  - HSN column visible with code 5208
  - CGST and SGST each at 2.5% (half of 5%)
  - Grand total correct (100 × ₹450 = ₹45,000 + ₹1,125 CGST + ₹1,125 SGST = ₹47,250)
  - Amount in words printed correctly
- [ ] Invoice appears on webapp `/invoices/sales` — status: Sent

- [ ] Send "Sharma Textiles ke liye consulting service invoice banao ₹25,000" —
  agent should find SAC 9983 at 18%
- [ ] Verify interstate vs intrastate: if your business state differs from Delhi (state 07),
  IGST should be used instead of CGST+SGST
- [ ] PDF received — tax breakdown correct for the supply type

- [ ] Send invoice for an item that is NOT in HSN master —
  "Sharma Textiles ke liye widget X invoice banao ₹5000" —
  agent should ask: "Is item ka GST rate kya hai?"
- [ ] Reply "12%" — agent saves to item cache, creates invoice at 12%
- [ ] Send same message again — agent should NOT ask again (cache hit), uses 12% silently

### 3.4 — Item GST Cache

- [ ] Run `sqlite3 /home/hermes/data/db/hermes.db "SELECT * FROM item_gst_cache;"` —
  confirm "widget x" (or normalized version) is stored with 12% and `confirmed_by='user'`
- [ ] "Cotton fabric" entry should exist with 5% and `confirmed_by='agent'` or `'user'`

### 3.5 — Payment Recording

- [ ] Send "Sharma Textiles ne ₹47,250 bheja UPI se, INV-0001 ke liye" —
  agent records payment, confirms
- [ ] Invoice status on webapp updates to "Paid" — verify on `/invoices/sales`
- [ ] Send "Sharma Textiles ne ₹10,000 advance diya, INV-0002 ke liye" (partial payment) —
  agent records partial payment, confirms ₹15,250 still outstanding
- [ ] Invoice status remains "Sent" (not Paid) — verified on webapp
- [ ] Payment receipt PDF sent by agent — verify it has correct receipt number, mode (UPI), reference

### 3.6 — Expense Logging

- [ ] Send "Aaj office supplies pe ₹850 kharcha Sharma Stationery se" —
  agent logs expense, confirms
- [ ] Expense appears on webapp `/invoices/purchases` — verify
- [ ] Send "Rent expense ₹25,000 — December" — agent logs, confirms
- [ ] Verify on webapp — both expenses visible with correct categories

### 3.7 — Expense via Photo OCR

- [ ] Take a photo of any receipt (grocery, stationery, anything with an amount printed)
- [ ] Send it to the Telegram bot
- [ ] Agent should extract: vendor, amount, date, category — show to user
- [ ] Confirm ("haan sahi hai") — agent saves expense
- [ ] Expense appears on webapp with receipt thumbnail visible
- [ ] Click receipt thumbnail on webapp — full image opens in lightbox

### 3.8 — Quotation Flow

- [ ] Send "Sharma Textiles ke liye quotation banao — website design ₹50,000, valid 15 din" —
  agent creates quotation, sends PDF
- [ ] PDF received — verify it says QUOTATION, has valid-until date
- [ ] Send "Sharma Textiles ne quotation accept kar liya, invoice banao" —
  agent converts quotation to invoice, items copied correctly
- [ ] Verify new invoice on webapp with same line items as quotation

### 3.9 — Udhaar Tracking

- [ ] Send "Ramesh ko ₹3,000 udhaar diya aaj" — agent logs, confirms
- [ ] Send "Ramesh ne ₹1,500 wapas kiya" — agent records partial settlement
- [ ] Send "Ramesh ka udhaar balance kya hai?" — agent returns ₹1,500 outstanding
- [ ] Send "Ramesh ne baaki ₹1,500 bhi de diya" — agent settles completely, confirms zero balance

### 3.10 — Bookkeeping Queries

- [ ] Send "Is mahine ka revenue kya hai?" — agent calls `DbGetMtdSummaryTool`, returns correct figure
- [ ] Send "Sharma Textiles ka outstanding kya hai?" — returns correct remaining balance
- [ ] Send "Kaun se invoices overdue hain?" — returns list (create an overdue one first if needed:
  create an invoice with due date in the past)
- [ ] Send "Total expenses is mahine?" — returns correct sum

---

## STAGE 4 — Reports via Telegram

### 4.1 — All Five Report Types

- [ ] Send "Is mahine ka P&L report chahiye" — agent generates PDF, sends in Telegram
  - Open PDF — revenue, expense, net profit sections all present
  - Numbers match what MTD summary reported
- [ ] Send "Outstanding dues ki list chahiye" — PDF received, shows Sharma Textiles with correct balance
- [ ] Send "Is mahine ke expenses ka report" — PDF received, expense list correct
- [ ] Send "GST report chahiye is quarter ka" — PDF received, shows CGST/SGST breakdown
- [ ] Send "CA ke liye export banao is quarter ka" — ZIP file received
  - Unzip it, verify it contains: `summary/pl_report.pdf`, `summary/gst_report.pdf`,
    `invoices/INV-0001.pdf`, `data/invoices.csv`, `data/payments.csv`, `data/expenses.csv`

---

## STAGE 5 — Morning Briefing & Cron

### 5.1 — Morning Briefing

- [ ] Trigger manually: send "Morning briefing start karo" — agent sends the briefing
- [ ] Briefing format correct:
  - 🌅 Good Morning greeting with business owner name
  - OVERDUE section (if any overdue invoices)
  - DUE TODAY section
  - DUE IN 3 DAYS section
  - YESTERDAY'S COLLECTIONS
  - THIS MONTH SO FAR (Invoiced / Collected / Expenses)
- [ ] If anomalies exist: 🚨 ANOMALIES section appears in briefing with count and top titles
- [ ] If no anomalies: no anomaly section in briefing (clean)

### 5.2 — Cron Verification

- [ ] Run `pm2 logs hermes-agent --lines 100 | grep cron` — cron entries visible
- [ ] Verify these three cron jobs are registered in nanobot config:
  - `morning-briefing` at `0 8 * * *`
  - `anomaly-detection` at `0 3 * * *`
  - `overdue-check` at `30 7 * * *`

---

## STAGE 6 — Webapp: Foundation & Navigation (Laptop)

*All webapp testing in this stage on laptop browser. Mobile stage comes later.*

### 6.1 — App Shell

- [ ] Open webapp — Dashboard loads in under 2 seconds
- [ ] Sidebar visible with all navigation groups and items
- [ ] HERMES logotype in top bar, links to Dashboard on click
- [ ] Theme toggle in top bar — click it, entire app switches to dark mode instantly
  - No hardcoded white backgrounds anywhere in dark mode (except document viewer)
  - All text readable in dark mode
  - All charts render correctly in dark mode
- [ ] Click theme toggle again — switches back to light mode
- [ ] Refresh page — theme preference persists (still in the mode you left it)
- [ ] Keyboard shortcut `Cmd+K` / `Ctrl+K` — global search modal opens
- [ ] Press Escape — search modal closes
- [ ] Collapse sidebar via the arrow toggle at its bottom — sidebar collapses to icon-only
- [ ] All icons still visible with tooltips on hover in collapsed mode
- [ ] Expand sidebar again — labels return

### 6.2 — System Status Dot

- [ ] Small colored dot in top bar is green
- [ ] Hover over it — tooltip shows "System: Healthy"
- [ ] Click it — navigates to `/system`

### 6.3 — Breadcrumbs

- [ ] Navigate to `/invoices/sales` — breadcrumb shows: Dashboard > Invoices > Sales
- [ ] Navigate to an invoice detail — breadcrumb shows: Dashboard > Invoices > Sales > INV-XXXX
- [ ] Click "Invoices" in the breadcrumb — navigates back to sales list
- [ ] Click "Dashboard" in the breadcrumb — navigates to dashboard

---

## STAGE 7 — Webapp: Dashboard

### 7.1 — KPI Cards

- [ ] Six KPI cards visible: Revenue MTD, Expenses MTD, Net Profit, Outstanding, Overdue, GST Liability
- [ ] All values match what the agent reported via `DbGetMtdSummaryTool`
- [ ] Delta percentages are shown on each card
- [ ] Overdue card has a red/danger left border (if overdue invoices exist)
- [ ] Each card has a 7-day sparkline at the bottom

### 7.2 — Charts

- [ ] Revenue vs Expenses line chart renders — two distinct colored lines
- [ ] Period toggle works: click 3M → chart shows 3 months, click 12M → 12 months
- [ ] Hover over chart line — crosshair and tooltip appear with both values
- [ ] Expense breakdown donut renders — segments match expense categories logged
- [ ] Invoice status stacked bar chart renders
- [ ] All chart axis labels use Indian number formatting (L, Cr for large values)
- [ ] Charts re-render correctly after toggling theme (dark mode — no invisible text)

### 7.3 — Activity Feed

- [ ] Last 20 events visible in the feed
- [ ] Each entry has the correct icon for its type (invoice = document icon, payment = rupee icon)
- [ ] Timestamps are relative ("2 hours ago", "Yesterday 4:32 PM")
- [ ] Click an activity item — navigates to the correct linked record
- [ ] "View full audit trail →" link at bottom navigates to `/audit`
- [ ] Wait 30 seconds — create a new invoice via Telegram — feed auto-updates without refresh

### 7.4 — Quick Actions

- [ ] "Upload Documents" button — navigates to `/upload`
- [ ] "Chat with HERMES" button — navigates to `/chat`
- [ ] "View Reports" button — navigates to `/reports`

---

## STAGE 8 — Webapp: Chat Interface (Laptop)

### 8.1 — Basic Chat

- [ ] Open `/chat` — desktop layout: 60% chat left, 40% preview panel right
- [ ] Suggested prompt chips visible when chat is empty
- [ ] Click a suggested prompt — fills textarea
- [ ] Clear the textarea — chips reappear
- [ ] Type "Namaste" and send — typing indicator (animated dots) appears immediately
- [ ] Agent responds within 10 seconds — response appears in chat bubble
- [ ] Typing indicator disappears when response arrives
- [ ] User message: right-aligned, accent-colored bubble
- [ ] Agent message: left-aligned, surface-colored bubble with HERMES avatar icon
- [ ] Timestamp visible on hover for each message

### 8.2 — Invoice Creation via Webapp Chat

- [ ] Send "Ek invoice banao Sharma Textiles ke liye ₹10,000 + 18% GST"
- [ ] Agent responds with invoice summary, asks for confirmation
- [ ] Confirm — agent creates invoice
- [ ] Inline invoice card appears in the chat thread (not just text):
  - Shows invoice number, client name, total, status badge
  - "View Invoice" button present
  - "Download PDF" button present
- [ ] Click "View Invoice" — navigates to correct invoice detail page
- [ ] Click browser back — returns to chat with history intact
- [ ] Click "Download PDF" on the inline card — PDF downloads with correct filename
- [ ] Right panel (preview) showed a live invoice preview while building the invoice

### 8.3 — Data Query via Webapp Chat

- [ ] Send "Sharma Textiles ka outstanding balance kya hai?" —
  agent responds with correct figure (same as Telegram reported)
- [ ] Send "Show me all overdue invoices" — agent responds with list
- [ ] Send "Is mahine ka revenue?" — agent responds with correct MTD figure

### 8.4 — Cross-Channel Data Consistency

- [ ] Create an invoice via Telegram (not webapp chat)
- [ ] Without refreshing webapp, send in WEBAPP chat: "Last invoice kya tha?"
- [ ] Agent responds with the invoice just created via Telegram
  (Confirms shared database — same agent, same data, different channel)

### 8.5 — Chat History

- [ ] Refresh the `/chat` page — previous conversation history loads
- [ ] Navigate away (go to Dashboard) and come back to `/chat` — history still there
- [ ] Conversation history sidebar shows past conversations
- [ ] Click a past conversation — that conversation's messages load

### 8.6 — Floating Chat Widget

- [ ] Navigate to Dashboard — floating chat bubble visible bottom-right
- [ ] Click it — a popover chat panel opens (not a new page)
- [ ] Send a message in the popover — agent responds
- [ ] Open `/chat` in the same tab — the popover conversation is visible here too
  (same `conversation_id` shared between floating widget and full chat page)
- [ ] Close the popover by clicking outside — it closes without losing history

---

## STAGE 9 — Webapp: Sales Invoices

### 9.1 — Invoice List

- [ ] Navigate to `/invoices/sales` — all test invoices visible
- [ ] Summary bar shows correct totals
- [ ] Status badges: correct color for each status (green=Paid, amber=Sent, red=Overdue)
- [ ] Supply type badges visible (INTRA or INTER)
- [ ] Filter by status "Paid" — only paid invoices shown, summary bar updates
- [ ] Filter by status "Overdue" — only overdue shown
- [ ] Filter by client name "Sharma" — only Sharma Textiles invoices shown
- [ ] Set date range to last month — correct subset shown
- [ ] Click "Clear filters" — all invoices return
- [ ] Click a column header — list sorts by that column
- [ ] Click same header again — sort reverses

### 9.2 — Invoice Row Actions

- [ ] Three-dot menu on any invoice row — all expected actions appear
- [ ] "Download PDF" from row action — PDF downloads
- [ ] "Mark as Paid" on an unpaid invoice — status updates to Paid, badge changes, success toast appears
- [ ] "Void" on a draft invoice (with confirmation modal) — status updates to Void

### 9.3 — Bulk Actions

- [ ] Check two invoice checkboxes — bulk actions bar appears at top
- [ ] "Download ZIP" — ZIP file downloads containing both PDFs
- [ ] "Export CSV" — CSV file downloads with correct columns and data

### 9.4 — Invoice Detail Page

- [ ] Click any invoice — detail page opens at `/invoices/sales/:id`
- [ ] Invoice preview (left panel) shows: logo placeholder, business info, client info,
  line items with HSN codes, CGST/SGST or IGST breakdown, grand total, amount in words
- [ ] Action panel (right): correct status badge, Download PDF, Mark as Paid / Record Payment
- [ ] Invoice timeline step-line shows correct completed steps
- [ ] Payment history table shows all payments recorded against this invoice
- [ ] "Amount Paid: ₹X | Remaining: ₹X" below payment history is correct
- [ ] Download PDF button — PDF matches invoice preview exactly
- [ ] Notes field — type something, click elsewhere — saves automatically
  (Verify by refreshing page — note still there)

---

## STAGE 10 — Webapp: Purchase Bills & Upload

### 10.1 — Upload Flow

- [ ] Navigate to `/upload`
- [ ] Drag a PDF vendor bill onto the upload zone — zone highlights in accent color
- [ ] Drop it — file appears in queue table with status QUEUED
- [ ] Within 5 seconds — status changes to PROCESSING (pulsing badge)
- [ ] Within 30–60 seconds — status changes to REVIEW NEEDED
  (actual time depends on OCR API response time)
- [ ] "Review →" button appears on the REVIEW NEEDED row

### 10.2 — Bill Review Page

- [ ] Click "Review →" — navigates to `/invoices/purchases/review/:id`
- [ ] Left panel: original document renders (PDF or image as uploaded)
- [ ] Zoom controls work (+ / - buttons and percentage display)
- [ ] Right panel: extracted fields are pre-filled (vendor, amount, date, category)
- [ ] Confidence dots visible on each field label
  - At least one green dot (high confidence field)
  - Red-confidence fields are visually highlighted
- [ ] Edit the vendor name field — input is editable
- [ ] Change the category via the dropdown — updates correctly
- [ ] GST fields present (CGST / SGST / IGST) if the OCR extracted tax info
- [ ] "Confirm & Finalize" button — click it
  - Success toast appears
  - Navigated back to `/invoices/purchases`
  - The bill now shows status FINALIZED
- [ ] Verified on webapp `/invoices/purchases` — finalized bill in the list with correct vendor, amount

### 10.3 — Error Handling

- [ ] Upload a very blurry or unreadable image (or a non-invoice file)
- [ ] Status eventually reaches ERROR
- [ ] "Retry" button appears — click it — status resets to QUEUED and reprocesses
- [ ] Upload 5 files at once — all 5 appear in queue and process sequentially

---

## STAGE 11 — Webapp: Contacts

### 11.1 — Contact List

- [ ] Navigate to `/contacts` — Sharma Textiles and any vendors created via agent visible
- [ ] Type "Sharma" in search — filters correctly
- [ ] Type phone number — filters correctly
- [ ] Toggle "Vendors" — only vendor-type contacts shown
- [ ] Outstanding column: Sharma Textiles shows correct remaining balance in correct color

### 11.2 — Contact Detail

- [ ] Click Sharma Textiles — detail page opens
- [ ] Overview tab: correct totals (Total Billed, Total Paid, Outstanding)
- [ ] Transactions tab: all Sharma Textiles invoices listed
- [ ] Ledger tab: running balance correct
  - Opening balance row at top
  - Each transaction row shows correct debit/credit/balance
  - Balance column adds up correctly
- [ ] "Download Statement" button — PDF downloads, shows Sharma Textiles ledger
- [ ] Notes tab: type a note, navigate away, come back — note persists

---

## STAGE 12 — Webapp: Payments & Reconciliation

### 12.1 — Payments List

- [ ] Navigate to `/payments` — all recorded payments listed
- [ ] Filter by mode (UPI) — only UPI payments shown
- [ ] Filter by date range — correct subset

### 12.2 — Record Payment via Webapp

- [ ] Click "Record Payment" — modal opens (desktop) correctly
- [ ] Search for Sharma Textiles in the invoice selector — unpaid invoices appear
- [ ] Select an invoice — amount field pre-fills with outstanding balance
- [ ] Change amount to a partial amount — "₹X remaining" shows below
- [ ] Select mode "UPI", enter a reference number
- [ ] Submit — success toast, modal closes, invoice balance updated
- [ ] Verify on invoice detail page — partial payment visible in payment history

---

## STAGE 13 — Webapp: Reports

### 13.1 — Reports Hub

- [ ] Navigate to `/reports` — card grid loads with all report categories
- [ ] "Last generated" date shows on cards where reports have been generated before
- [ ] Every report category visible: Financial, GST, Receivables, Payables, Expenses, Intelligence

### 13.2 — Financial Reports

- [ ] Click "Run Report →" on P&L Statement
- [ ] Date range selector appears — select "This Month"
- [ ] Report renders in the page (not a new tab)
- [ ] Numbers match what agent reported via Telegram
- [ ] "Download PDF" button — PDF downloads, formatting correct (Indian number format, ₹ prefix)
- [ ] "Download Excel" button — .xlsx file downloads, opens in Excel/Sheets
- [ ] Run Balance Sheet — renders correctly as of today
- [ ] Run Trial Balance — all accounts balanced (debits = credits)

### 13.3 — GST Reports Page

- [ ] Navigate to `/reports/gst`
- [ ] Quarter selector at top — select current quarter
- [ ] Three summary cards load: Output Tax, ITC, Net Payable
- [ ] GSTR-1 tab: B2B table shows invoices with GSTIN, B2C section shows unregistered
- [ ] ITC Tracker tab: vendor bills with eligible ITC listed
- [ ] HSN Summary tab: items grouped by HSN code with taxable amounts
- [ ] GST-3B Helper tab: pre-filled form matching GST-3B sections — numbers match GSTR-1 tab
- [ ] Filing Status tab: current quarter shows "Open" status
  - Click "Mark as Filed" — status changes to "Filed"
  - Click again — "Locked" option appears, confirms locking
- [ ] "Export for Portal (JSON)" button — JSON file downloads
  - Open the file — valid JSON, contains b2b and b2c arrays with correct data

### 13.4 — Custom Report Builder

- [ ] Navigate to `/reports/custom`
- [ ] Add dimension "Customer" + metric "Total Amount" → live preview shows per-customer totals
- [ ] Add filter "Status = Paid" → preview updates to only paid invoices
- [ ] "Save Template" — enter a name, save
- [ ] Navigate away and come back — saved template still listed
- [ ] Load the template — config restores correctly
- [ ] "Run Full Report" → "Download CSV" — CSV file with correct data

### 13.5 — Aging Reports

- [ ] Run Receivables Aging — four buckets shown (0–30, 31–60, 61–90, 90+)
- [ ] Sharma Textiles outstanding appears in the correct bucket
- [ ] Total matches outstanding balance shown on contact detail

---

## STAGE 14 — Webapp: Document Center

### 14.1 — File Center

- [ ] Navigate to `/documents` — all generated PDFs and uploaded files listed
- [ ] Left sidebar filter: click "Generated → Sales Invoices" — only invoice PDFs shown
- [ ] Click "Uploaded Documents" — only uploaded vendor bills shown
- [ ] Search for "INV-0001" — that invoice file appears
- [ ] Switch to Grid view — thumbnails render for each file

### 14.2 — Document Viewer

- [ ] Click any PDF file — viewer drawer slides in from the right
- [ ] PDF renders inline in the drawer
- [ ] PDF is shown with white background even in dark mode
  (Note "shown in light mode for print preview" message visible)
- [ ] Zoom controls work
- [ ] Download button in drawer header downloads the file with clean filename
- [ ] Navigate to next/previous file using arrow buttons
- [ ] Click outside drawer (or X button) — drawer closes

### 14.3 — Bulk Download

- [ ] Select 3 files using checkboxes
- [ ] "Download ZIP" button appears — click it
- [ ] "Building your download… 3 files" loading modal appears
- [ ] ZIP downloads — contains exactly those 3 files with correct names

---

## STAGE 15 — Webapp: Anomalies

### 15.1 — Trigger Anomaly Detection

- [ ] Create test data: two expenses from "Rajan Traders" for ₹42,500 dated 12 days apart
  (via Telegram: "Rajan Traders se ₹42,500 ka bill aaya" twice with different dates)
- [ ] Send in Telegram: "Run anomaly detection scan now"
- [ ] Agent responds: "X naye issues mile" (should include the duplicate)

### 15.2 — Anomalies Page

- [ ] Navigate to `/anomalies` — at least one anomaly card visible
- [ ] Nav sidebar "Anomalies" item shows badge with correct count
- [ ] Anomaly card shows: type badge (DUPLICATE BILL), confidence %, description with both affected records
- [ ] "View Expense #X" links in the card navigate to the correct record

### 15.3 — Anomaly Actions

- [ ] Click "Acknowledge" on the duplicate bill card
  - Card left border changes from warning to success/muted
  - Nav badge decrements by 1
  - Toast confirms action
- [ ] Create a round-number expense (₹50,000) — run detection again
- [ ] Dismiss the round-number anomaly — select reason "Already verified externally"
  - Card greys out with opacity
  - Badge decrements
- [ ] Run detection again — dismissed anomaly does NOT reappear (correctly excluded)

---

## STAGE 16 — Webapp: Notifications

### 16.1 — Bell Badge

- [ ] Create a new invoice via Telegram — bell badge increments (may take up to 30 seconds due to polling)
- [ ] Bell badge shows correct unread count
- [ ] Badge hidden when count is 0

### 16.2 — Notification Panel

- [ ] Click bell icon — notification panel slides in from the right
- [ ] "Invoice Created" notification visible for the invoice just created
- [ ] Notification item: icon, title (bold = unread), description, timestamp
- [ ] Unread indicator: blue dot on left side of unread items
- [ ] Click a notification — marks as read (blue dot disappears), navigates to linked record, panel closes
- [ ] "Mark all as read" button — all dots disappear, badge drops to 0

### 16.3 — Notification Tabs

- [ ] "Unread" tab — only unread items
- [ ] "Anomalies" tab — only anomaly-type notifications
- [ ] "System" tab — only system-type notifications (if any)

### 16.4 — Overdue Notification

- [ ] Create an invoice with due date set to yesterday
- [ ] Trigger overdue check manually via Telegram: "Run overdue invoice check now"
- [ ] Notification appears: "Invoice Overdue — INV-XXXX"
- [ ] Invoice status on webapp updated to "Overdue" automatically
- [ ] Bell badge reflects the new notification

---

## STAGE 17 — Webapp: Audit Trail

### 17.1 — Audit Log

- [ ] Navigate to `/audit` — log entries visible
- [ ] Every action taken in testing above should have an entry here
- [ ] "This log is read-only and cannot be modified" banner visible
- [ ] Columns: Timestamp (monospace), Source, Action Type badge, Record (linked), Details
- [ ] Click a linked record chip — navigates to that entity

### 17.2 — Filters & Export

- [ ] Filter by action type "CREATE" — only create events shown
- [ ] Filter by date range — correct subset
- [ ] Click "Export to CSV" — date range picker modal opens
- [ ] Select a range — CSV downloads with all audit entries in that range
- [ ] Open CSV — columns and data correct, timestamps in readable format

---

## STAGE 18 — Webapp: Chart of Accounts

### 18.1 — Account Tree

- [ ] Navigate to `/accounts` — full account tree visible (Assets, Liabilities, Income, Expenses, Equity)
- [ ] Expand "Expenses" group — sub-accounts visible
- [ ] Account code (monospace), name, type, balance shown per row
- [ ] Click "Add Account" — inline form appears at the correct level of the tree
- [ ] Enter a test account name — save — new account appears in tree
- [ ] Click pencil icon on any account — inline edit mode, change name, save — updates
- [ ] Deactivate the test account — it becomes greyed out

### 18.2 — Mapping Rules

- [ ] Navigate to mapping rules sub-page
- [ ] "Add Rule" — create: "Vendor = Sharma Stationery → map to Office Supplies"
- [ ] Rule appears in the table with active status
- [ ] Toggle rule inactive — status changes
- [ ] Delete the test rule

---

## STAGE 19 — Webapp: System Health (Deep Check)

### 19.1 — All Cards

- [ ] Backend Status: green RUNNING
- [ ] Queue Depth: shows a number (0 if queue is empty)
- [ ] Avg Processing Time: shows a reasonable number (not 0, not NULL)
- [ ] Disk Usage: progress bar matches disk percentage from `df -h`
- [ ] Uptime: shows time since last PM2 restart

### 19.2 — Processing Queue

- [ ] Upload a document via webapp — it appears in the queue table on `/system`
- [ ] Queue table auto-refreshes every 5 seconds without page reload
- [ ] "Pause Queue" button — click it — new uploads stop processing (stay at QUEUED)
- [ ] "Resume Queue" — processing resumes

### 19.3 — Performance Graph

- [ ] 24-hour chart renders with API response times and documents/hour
- [ ] Both lines are visible and not flat zero

### 19.4 — Error Log

- [ ] Error log shows last 100 lines
- [ ] Severity filter chips work (ERROR, WARNING, INFO)
- [ ] "Download .log" button — downloads the file

---

## STAGE 20 — Global Search

### 20.1 — Search Functionality

- [ ] Press `Cmd+K` — search modal opens, input is auto-focused
- [ ] Type "Sharma" — results appear within 300ms:
  - INVOICES section: all Sharma Textiles invoices
  - CONTACTS section: Sharma Textiles entry
- [ ] Type "INV-0001" — exact invoice found
- [ ] Type a random string with no matches — "No results" message shown
- [ ] Empty input — "Recent searches" shown

### 20.2 — Keyboard Navigation

- [ ] Arrow Down — moves selection highlight down through results
- [ ] Arrow Up — moves back up
- [ ] Enter on a selected result — navigates to that page
- [ ] Escape — closes modal

### 20.3 — Navigation via Search

- [ ] Search "Sharma" → select the contact result → navigates to `/contacts/:id`
- [ ] Open search again → select an invoice → navigates to invoice detail

---

## STAGE 21 — Mobile Testing (Phone)

*Repeat the critical flows on a phone browser. This stage confirms responsive layout.*

### 21.1 — App Shell on Mobile

- [ ] Open webapp URL on phone — page loads correctly, no horizontal scroll on the page
- [ ] Sidebar is NOT visible — bottom tab bar visible at bottom
- [ ] Bottom tab bar: Home, Chat, Invoices, Reports, More — all tappable
- [ ] "More" tab — opens a bottom sheet with remaining navigation items
- [ ] Tap the hamburger icon (if present) — sidebar slides in as overlay from left
- [ ] Backdrop behind sidebar — tap it — sidebar closes

### 21.2 — Dashboard on Mobile

- [ ] KPI cards are a horizontal scrollable strip (swipe to see all 6)
- [ ] Charts are stacked vertically, full width
- [ ] Activity feed readable on small screen
- [ ] All touch targets are large enough (minimum 44×44px — nothing feels tiny to tap)

### 21.3 — Invoice List on Mobile

- [ ] Navigate to Invoices via bottom tab
- [ ] Table scrolls horizontally — first column (Invoice #) is sticky
- [ ] Filters: "Filter" button opens a bottom sheet (not a floating dropdown)
- [ ] Date range picker: uses native mobile date input (not a custom floating calendar)
- [ ] Row tap → navigates to invoice detail
- [ ] Invoice detail: invoice preview on top, action panel scrolled below
- [ ] "Download PDF" button: minimum 44px height, tappable without zoom

### 21.4 — Chat on Mobile

- [ ] Open Chat via bottom tab — full screen chat
- [ ] No preview panel (desktop-only) — no broken layout
- [ ] Input bar at bottom — textarea expands correctly when typing
- [ ] Virtual keyboard appears — input stays visible above keyboard (not hidden behind it)
- [ ] Voice button present — tap it — microphone permission requested (accept it)
- [ ] Record a voice message: "Invoice banao Sharma ke liye" — transcript appears in textarea
- [ ] Send — agent responds

### 21.5 — File Upload on Mobile

- [ ] Navigate to `/upload` — upload zone visible
- [ ] No drag-and-drop (mobile) — "Tap to browse files" works instead
- [ ] Tap it — iOS/Android file picker opens
- [ ] Select a photo — file appears in queue table, processes correctly

### 21.6 — Add to Home Screen (PWA)

- [ ] On iPhone (Safari): share button → "Add to Home Screen" → add
- [ ] On Android (Chrome): three-dot menu → "Add to Home Screen" → add
- [ ] Open from home screen — opens full screen, no browser chrome visible
- [ ] App name shown correctly under icon

### 21.7 — Touch Interactions

- [ ] Pull to refresh on Invoice list — list refreshes
- [ ] Long press on an invoice row — enters bulk select mode
- [ ] Swipe to dismiss a toast notification
- [ ] Pinch to zoom on document viewer — image zooms in/out

### 21.8 — Modal Behavior on Mobile

- [ ] "Record Payment" — opens as a bottom sheet (slides up from bottom)
- [ ] Drag the bottom sheet handle downward — sheet dismisses
- [ ] All dropdowns open as bottom sheets (not floating)

---

## STAGE 22 — Cross-Browser Check (Laptop)

### 22.1 — Chrome (already tested above)

- [ ] All stages above were done in Chrome — confirmed working

### 22.2 — Safari (macOS)

- [ ] Open webapp in Safari
- [ ] Dashboard loads correctly
- [ ] Charts render
- [ ] Document viewer (PDF) renders
- [ ] `position: sticky` on table headers works
- [ ] Theme toggle works

### 22.3 — Firefox

- [ ] Open webapp in Firefox
- [ ] Dashboard loads
- [ ] Charts render
- [ ] Sidebar layout correct
- [ ] No CSS grid layout breaks on any page

---

## STAGE 23 — Data Integrity Final Checks

*Cross-verify key numbers between Telegram, webapp, and direct DB queries.*

### 23.1 — Revenue Reconciliation

- [ ] Ask agent (Telegram): "Is mahine ka total revenue kya hai?" — note the number
- [ ] Open webapp Dashboard — Revenue MTD card — same number (within rounding)
- [ ] Run P&L report on webapp — Revenue figure matches
- [ ] Direct DB query:
  ```
  sqlite3 /home/hermes/data/db/hermes.db
  "SELECT SUM(total) FROM invoices
   WHERE strftime('%Y-%m', issue_date) = strftime('%Y-%m', 'now')
   AND status IN ('sent','paid','overdue');"
  ```
  Result should match what agent and webapp both reported.

### 23.2 — GST Reconciliation

- [ ] Ask agent: "Is quarter ka GST kitna hai?" — note output tax figure
- [ ] Open webapp `/reports/gst` — Output Tax card — same figure
- [ ] Direct DB query:
  ```
  sqlite3 /home/hermes/data/db/hermes.db
  "SELECT SUM(total_cgst + total_sgst + total_igst) FROM invoices
   WHERE issue_date >= '2025-01-01';"
  ```
  (adjust date for current quarter) — matches above.

### 23.3 — Outstanding Reconciliation

- [ ] Ask agent: "Sharma Textiles ka outstanding?" — note figure
- [ ] Open webapp `/contacts` → Sharma Textiles — outstanding column — same figure
- [ ] Ledger tab on contact detail — final balance row — same figure
- [ ] Direct DB query verifies it matches invoice totals minus payments

---

## STAGE 24 — Edge Cases & Error Handling

### 24.1 — Agent Edge Cases

- [ ] Send a payment amount LARGER than the invoice total —
  agent should handle gracefully (either cap at invoice total or ask to confirm)
- [ ] Send an invoice for a client that doesn't exist yet —
  agent should auto-create the client and then create the invoice
- [ ] Send a completely garbled message: "asdfjkl; 12345 ###" —
  agent responds gracefully without calling any tools or crashing
- [ ] Send an image that is NOT a receipt (e.g., a selfie) —
  agent attempts OCR, low confidence result, asks user to enter details manually

### 24.2 — Webapp Edge Cases

- [ ] Visit a route that doesn't exist (e.g., `/notapage`) — 404 page shown, not a crash
- [ ] Hard refresh on `/invoices/sales/99999` (non-existent invoice) — graceful error, not blank screen
- [ ] Upload a file that exceeds 25MB — error message shown, file rejected
- [ ] Upload an unsupported file type (.doc) — error message shown
- [ ] Mark an already-paid invoice as paid again — should be a no-op or show an appropriate message

### 24.3 — Network Failure Simulation

- [ ] Stop the FastAPI process: `pm2 stop hermes-web`
- [ ] Try to use the webapp — red "Cannot reach HERMES backend" banner appears at top
- [ ] "Retry" button in the banner is clickable
- [ ] Restart the process: `pm2 start hermes-web`
- [ ] Banner disappears automatically within 30 seconds (next poll cycle)

---

## STAGE 25 — Performance Check

### 25.1 — Load Times

- [ ] Open DevTools → Network tab → Hard refresh Dashboard
  - First Contentful Paint under 1.5 seconds
  - All API calls complete under 500ms each
- [ ] Navigate to Invoice list with 20+ invoices — table renders under 800ms
- [ ] Generate P&L PDF — complete under 10 seconds
- [ ] Generate CA export bundle — complete under 30 seconds
- [ ] Search "Sharma" in global search — results appear under 300ms

### 25.2 — Bundle Size

- [ ] DevTools → Network → filter JS — total JavaScript transferred (gzipped) under 500KB
  (If over 500KB, lazy loading of `recharts` and `react-pdf` may need to be implemented)

---

## STAGE 26 — Final Smoke Test (Simulate Real Customer Day 1)

*Do this entire sequence without any prior test data — on a fresh DB, as if you are a new customer.*

- [ ] Complete the onboarding wizard (all 5 steps)
- [ ] Send first invoice via Telegram: "Raj Enterprises ke liye invoice banao ₹15,000 website design, 18% GST"
- [ ] PDF received in Telegram ✓
- [ ] Invoice visible on webapp ✓
- [ ] Send "Raj ne ₹15,000 bheja" — payment recorded
- [ ] Invoice marked Paid on webapp ✓
- [ ] Upload a vendor bill PDF via webapp — review and confirm it
- [ ] Run P&L report on webapp — shows the ₹15,000 revenue and the expense
- [ ] Run GST report — shows the ₹2,700 GST collected
- [ ] Morning briefing triggered manually — correct format with the day's data
- [ ] Open webapp on phone — everything works the same as laptop

---

## ISSUE TRACKER

*Log any failures here as you go. Come back and re-test after fixing.*

| # | Stage | Issue Description | Fixed? |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## SIGN-OFF

Complete all stages above with all items checked ✅ before shipping to any customer.

- [ ] All 26 stages complete with zero ❌ items
- [ ] Issue tracker above is empty (or all issues marked Fixed)
- [ ] Test DB wiped: `rm /home/hermes/data/db/hermes.db` and `init_db()` re-run
  (Start fresh — do not ship to customer with test data in their DB)
- [ ] PM2 processes confirmed `online` after fresh start
- [ ] `pm2 save` run — ensures processes auto-restart on VM reboot

**HERMES is ready to ship.**
