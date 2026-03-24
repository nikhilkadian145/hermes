# HERMES — Implementation Plan v5.5
### Webapp Design, Build & Integration
### Version 5.5 | Continues from v5 Phase 17 · Supersedes Webapp Phases 18–24 of v5

---

> **What changed from v5 webapp plan (Phases 18–24):**
>
> v5 planned a minimal FastAPI + Jinja2 + vanilla JS webapp — server-side rendered, basic dashboard,
> invoice list, expense gallery. Appropriate for a v1 but undershoots the product.
>
> v5.5 replaces the entire webapp section with a full-featured, production-grade frontend.
>
> Key changes:
> - **Tech stack upgrade:** React (Vite) frontend + FastAPI JSON API backend, served by nginx.
>   Jinja2 templates are dropped entirely. The Jinja2 HTML→PDF templates in `templates/` (for
>   WeasyPrint) are untouched — those are the agent's PDF generator, not the webapp.
> - **No auth:** Webapp is accessed over SSH tunnel or local VM network. No login page, no JWT.
>   All routes open. Security is at the network/SSH layer, not the app layer.
> - **Mobile + laptop are co-primary targets.** Every phase includes mobile-specific work.
> - **Dark mode + light mode.** Theme toggle, CSS custom properties throughout.
> - **Chat interface.** The primary invoice creation UX is a chat window, not forms.
> - **Full feature surface.** All features from HERMES Webapp Feature Specification V1.0 are covered.
>
> Phases 1–17 are complete. This document covers Phases 18–44.

---

## WHAT THE WEBAPP STACK IS

```
webapp/
├── backend/                         ← FastAPI JSON API (Python)
│   ├── main.py                      ← app init, CORS, router includes
│   ├── database.py                  ← SQLite read/write layer for webapp
│   ├── routers/
│   │   ├── dashboard.py
│   │   ├── invoices.py
│   │   ├── bills.py
│   │   ├── contacts.py
│   │   ├── payments.py
│   │   ├── accounts.py
│   │   ├── reports.py
│   │   ├── anomalies.py
│   │   ├── audit.py
│   │   ├── notifications.py
│   │   ├── search.py
│   │   ├── files.py
│   │   ├── settings.py
│   │   ├── system.py
│   │   └── chat.py
│   └── models.py                    ← Pydantic response models
│
└── frontend/                        ← React + Vite (TypeScript)
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── styles/
    │   │   ├── tokens.css           ← ALL CSS custom properties (colors, spacing, typography)
    │   │   └── globals.css          ← resets, base styles, typography classes
    │   ├── components/
    │   │   └── ui/                  ← all reusable UI components
    │   ├── pages/                   ← one file per route
    │   ├── hooks/                   ← custom React hooks
    │   ├── api/                     ← API client functions (fetch wrappers)
    │   └── utils/                   ← formatting, date, number helpers
    ├── public/
    │   ├── fonts/                   ← IBM Plex Sans + Mono (self-hosted, not CDN)
    │   └── manifest.json            ← PWA manifest
    ├── index.html
    ├── vite.config.ts
    └── tsconfig.json
```

**Why React + Vite and not Jinja2 + vanilla JS:**
The chat interface, real-time processing queue, side-by-side document review, theme toggle, and
live dashboard updates all require component state management that vanilla JS makes painful at scale.
React + Vite gives a zero-config build pipeline, fast HMR in development, and a ~150KB gzipped
production bundle — reasonable for a local-network app.

**Why TypeScript:**
The webapp will grow. TS catches schema mismatches between FastAPI response types and frontend
consumption at build time, not at runtime in front of the customer.

**Why self-hosted fonts:**
The VM may not always have internet access. Bundling IBM Plex Sans + Mono into `public/fonts/`
guarantees consistent rendering without any CDN dependency.

---

## ARCHITECTURE DIAGRAM — WEBAPP LAYER

```
BROWSER (phone or laptop, on local network or SSH tunnel)
       │
       ▼ HTTPS via nginx
┌──────────────────────────────────────────────────────┐
│  nginx                                               │
│  /          → serves React build (static files)      │
│  /api/      → proxy_pass to FastAPI :5000            │
│  /files/    → alias /home/hermes/data/ (direct serve)│
└──────────────────────────────────────────────────────┘
       │               │
       ▼               ▼
  React App      FastAPI :5000
  (static)       (JSON API only)
                      │
                      ▼ read-only + write (settings, payments)
               SQLite hermes.db
               (same DB as agent)
```

**Notes on DB access:**
- Dashboard, invoices, contacts, reports, files — **read-only** (agent writes, webapp reads)
- Settings, payments recorded via webapp — **write** (these are the exceptions)
- Chat relay — **pass-through** (webapp proxies chat messages to nanobot agent)

---

## PHASES AT A GLANCE (v5.5)

| Phase | Name | Deliverable |
|---|---|---|
| 18 | Webapp Architecture Setup | Vite scaffold, FastAPI API shell, dev server wired |
| 19 | Design System & Tokens | All CSS tokens, self-hosted fonts, Tailwind config |
| 20 | Core UI Component Library | Button, Badge, Input, Card, Table, Toast, Modal, Skeleton |
| 21 | App Shell — Layout & Navigation | Top bar, sidebar, bottom tab bar, breadcrumbs, theme toggle |
| 22 | Dashboard Page | KPI cards, charts, activity feed, quick actions |
| 23 | AI Chat Interface | Full chat page, floating widget, live invoice preview |
| 24 | Sales Invoices | List, detail, download, status management |
| 25 | Purchase Bills & Upload | Upload zone, processing queue, bill review (side-by-side) |
| 26 | Document Viewer & File Center | File center, inline viewer drawer, bulk download |
| 27 | Contacts | List, detail, tabs, ledger, statement download |
| 28 | Payments & Reconciliation | Record payment, payments list, manual reconciliation |
| 29 | Chart of Accounts | Tree view, inline edit, mapping rules |
| 30 | Reports Hub & Financial Reports | Hub page, P&L, Balance Sheet, Cash Flow, Trial Balance |
| 31 | GST Reports | GSTR-1, ITC tracker, portal JSON export, all GST views |
| 32 | Intelligence & Specialty Reports | Anomaly report, vendor analysis, processing quality |
| 33 | Custom Report Builder | Dimension/metric selector, live preview, save template |
| 34 | Anomaly & Alert Center | Anomaly cards, acknowledge/escalate/dismiss, nav badge |
| 35 | Audit Trail | Full-width log table, filters, CSV export |
| 36 | Notifications | Slide-in panel, tabs, mark read, email pref settings |
| 37 | Global Search | Cmd+K modal, multi-type results, keyboard nav |
| 38 | Import / Export | Import center (CSV flows), bulk ZIP export, full backup |
| 39 | System Health Panel | Status cards, queue table, perf graph, error log |
| 40 | Business Settings | All 5 settings sections with save |
| 41 | Onboarding Flow | 5-step wizard, setup checklist widget |
| 42 | FastAPI Backend — All API Endpoints | Every endpoint wired to DB/filesystem |
| 43 | Frontend–Backend Integration | API client, error handling, loading states |
| 44 | Responsive Polish & QA Pass | Mobile audit, touch targets, dark mode all pages |
| 45 | Full E2E Webapp Testing | 60+ scenarios pass on your own GVM |
| 46 | Production Build, Nginx & PM2 | Vite build, nginx update, PM2, install.sh updated |
| 47 | Handover Script Update | provision.sh, onboard-tui.js updated for new webapp |

---

## PHASE 18 — Webapp Architecture Setup

**Goal:** Get the React + FastAPI development environment running. A blank app shell that
builds cleanly, dev server proxies to FastAPI, and the folder structure matches the spec.

### Task 18.1 — Initialize React + Vite project

Inside the `webapp/frontend/` directory:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

Install core dependencies:
```bash
npm install react-router-dom@6          # client-side routing
npm install @phosphor-icons/react       # Phosphor icons
npm install recharts                    # charts (Revenue/Expense trends)
npm install react-dropzone              # drag-and-drop file upload
npm install react-pdf                  # PDF.js wrapper for document viewer
npm install date-fns                   # date formatting and parsing
npm install clsx                       # conditional className utility
```

Dev dependencies:
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Task 18.2 — Configure Tailwind

`tailwind.config.ts`:
- Set `content` to `["./index.html", "./src/**/*.{ts,tsx}"]`
- Extend the theme to expose HERMES CSS custom properties (do NOT hardcode colors in Tailwind — use `var(--token)` references)
- Disable Tailwind's preflight reset for elements managed by our own `globals.css`

`vite.config.ts`:
- Set `server.proxy` so that `'/api'` proxies to `http://localhost:5000` during development
- Set `server.host: true` to allow LAN access (for testing on phone)
- Set `build.outDir: '../static'` so the Vite build writes into `webapp/static/` which nginx serves

### Task 18.3 — Initialize FastAPI backend

Inside `webapp/backend/`:

```bash
# In the hermes venv (already created in Phase 3)
# FastAPI + uvicorn already installed in Phase 3 requirements
```

Create `webapp/backend/main.py`:
- FastAPI app initialization
- Mount CORS middleware: allow origins `["*"]` (local-only, no internet exposure)
- Include all routers from `webapp/backend/routers/`
- `GET /api/health` endpoint returning `{"status": "ok", "version": "1.0"}`

Create `webapp/backend/database.py`:
- Single function `get_db()` context manager — opens read-only SQLite connection
- Single function `get_db_write()` context manager — opens read-write connection (for settings + payments)
- DB path read from `os.environ["DB_PATH"]`

Create stub routers (empty, just `APIRouter()` + one health-check GET each):
- `dashboard.py`, `invoices.py`, `bills.py`, `contacts.py`, `payments.py`
- `accounts.py`, `reports.py`, `anomalies.py`, `audit.py`, `notifications.py`
- `search.py`, `files.py`, `settings.py`, `system.py`, `chat.py`

### Task 18.4 — Self-host fonts

Download IBM Plex Sans (weights 400, 500, 600, 700) and IBM Plex Mono (weight 400) from
Google Fonts as WOFF2 files. Place in `webapp/frontend/public/fonts/`.

Create `@font-face` declarations in `src/styles/globals.css` pointing to `/fonts/*.woff2`.

Test: load the app with internet disabled — fonts must render correctly.

### Task 18.5 — Verify dev setup

Start FastAPI: `uvicorn webapp.backend.main:app --reload --port 5000`
Start Vite dev server: `cd webapp/frontend && npm run dev`

Confirm:
- `http://localhost:5173` shows React app (blank page with "HERMES" title is enough)
- `http://localhost:5173/api/health` proxies through to FastAPI and returns `{"status": "ok"}`
- `http://localhost:5173` loads IBM Plex Sans font (check Network tab — fonts should be from localhost, not fonts.googleapis.com)

### Task 18.6 — Environment configuration

`webapp/backend/.env` (per customer, written by provision.sh):
```
DB_PATH=/home/hermes/data/db/hermes.db
CUSTOMER_DATA_DIR=/home/hermes/data
PORT=5000
BUSINESS_NAME=Business Name Here
NANOBOT_SOCKET=/home/hermes/data/nanobot.sock
```

`webapp/backend/config.py`:
- Read all env vars with `python-dotenv`
- Export as constants used by all routers

---

## PHASE 19 — Design System & Tokens

**Goal:** Define every design token as a CSS custom property. No color, font size, or spacing
value anywhere in the codebase except via these variables. This is the foundation for
dark/light mode and consistency.

### Task 19.1 — Write `src/styles/tokens.css`

Define all tokens under `:root` (light mode defaults) and `[data-theme="dark"]` overrides.

**All tokens to implement** (exact values from HERMES Feature Specification §2.1):

Light mode root block includes:
- All `--bg-*` tokens (base, surface, subtle, overlay)
- All `--border`, `--border-strong` tokens
- All `--text-*` tokens (primary, secondary, muted, inverse)
- All `--accent`, `--accent-hover`, `--accent-subtle` tokens
- All semantic colors: `--success`, `--success-bg`, `--warning`, `--warning-bg`,
  `--danger`, `--danger-bg`, `--neutral`, `--neutral-bg`
- All `--shadow-*` tokens
- All `--space-*` tokens (1 through 16)
- Font family tokens: `--font-sans: 'IBM Plex Sans', sans-serif` and `--font-mono: 'IBM Plex Mono', monospace`
- Font size tokens matching the type scale table in the spec

Dark mode `[data-theme="dark"]` block overrides every `--bg-*`, `--border*`, `--text-*`,
`--accent*`, and semantic color token with dark mode values.

**Critical rule:** The `[data-theme="dark"]` block must ONLY redefine values that actually change
between light and dark. Spacing, font, and shadow-structure tokens are defined once in `:root`.

### Task 19.2 — Write `src/styles/globals.css`

- CSS reset (box-sizing, margin 0, etc.)
- `body` uses `--bg-base` background, `--text-primary` color, `--font-sans` font, `font-size` 14px
- Typography utility classes:
  `.text-display`, `.text-heading`, `.text-subheading`, `.text-body`, `.text-body-sm`,
  `.text-label`, `.text-caption`, `.text-mono` — each sets `font-size`, `font-weight`,
  `line-height`, and for `.text-mono` also sets `font-family: var(--font-mono)`
- Scrollbar styling for dark/light mode (thin scrollbar, `--border` color track)
- `::selection` background using `--accent-subtle`

### Task 19.3 — Configure Tailwind to use CSS tokens

In `tailwind.config.ts`, extend the color palette to include HERMES token references:
```typescript
colors: {
  'bg-base': 'var(--bg-base)',
  'bg-surface': 'var(--bg-surface)',
  'bg-subtle': 'var(--bg-subtle)',
  'accent': 'var(--accent)',
  'danger': 'var(--danger)',
  // ... all tokens
}
```

This allows using classes like `bg-bg-surface`, `text-accent`, `border-border` in JSX while
all actual values come from CSS variables and theme-switch correctly.

### Task 19.4 — Theme toggle logic

Create `src/hooks/useTheme.ts`:
- Reads `localStorage.getItem('hermes-theme')` on init
- Falls back to `window.matchMedia('(prefers-color-scheme: dark)').matches`
- Applies `document.documentElement.setAttribute('data-theme', theme)` on mount and on toggle
- Exports `{ theme, toggleTheme }` — used by the top bar theme toggle button

### Task 19.5 — Number and date formatting utilities

Create `src/utils/format.ts`:

`formatCurrency(amount: number): string`
- Indian lakh/crore notation: ₹1,23,456 (not ₹1,234,56)
- Use `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })`
- Abbreviation for large values: ₹1.2L (lakh), ₹2.4Cr (crore) — for KPI cards and chart axes

`formatDate(dateString: string): string`
- Output: "14 Mar 2025" (DD Mon YYYY)
- Never MM/DD/YYYY

`formatRelativeTime(dateString: string): string`
- "2 minutes ago", "Yesterday 4:32 PM", "14 Mar 2025"
- Uses `date-fns` `formatDistanceToNow` with a threshold — beyond 7 days use absolute date

`formatInvoiceNumber(num: string): string`
- Ensures proper display of invoice/bill numbers (monospace, no decoration)

---

## PHASE 20 — Core UI Component Library

**Goal:** Build every reusable component that all pages will consume. These must be built first —
pages are assembled from these components, not the other way around. All components use only
CSS tokens via Tailwind token classes or inline CSS variables. No hardcoded colors anywhere.

### Task 20.1 — Button component (`src/components/ui/Button.tsx`)

Props: `variant` (primary | secondary | ghost | danger), `size` (sm | md | lg),
`loading` (boolean), `disabled` (boolean), `icon` (ReactNode), `iconPosition` (left | right),
`fullWidth` (boolean), plus all standard `<button>` HTML attributes.

- **Primary:** `bg-accent text-inverse`, hover `bg-accent-hover`, 6px border-radius
- **Secondary:** `bg-bg-surface border border-border text-text-primary`, hover `bg-bg-overlay`
- **Ghost:** `text-accent`, hover `bg-accent-subtle`
- **Danger variants:** replace accent with danger token equivalents
- Loading state: spinner icon (animated SVG) replaces/precedes label; button width locked (no layout shift)
- All sizes: sm=28px height, md=36px height, lg=44px height
- Mobile: ensure lg size is used for all primary CTAs in forms
- Transition: 120ms ease on background, border-color

### Task 20.2 — Badge component (`src/components/ui/Badge.tsx`)

Props: `status` (paid | sent | draft | overdue | due-soon | processing | review | error | void | custom),
`label` (string override), `size` (sm | md).

- Rendered as a `<span>` pill (rounded-full)
- Each status maps to a specific bg + text token pair (see spec §2.4 Badges table)
- Font: 12px, weight 500, uppercase, letter-spacing 0.05em
- Padding: 2px 8px

### Task 20.3 — Input components (`src/components/ui/Input.tsx`, `Select.tsx`, `DatePicker.tsx`)

**Input:**
- Label always above (prop `label: string`)
- Controlled: `value` + `onChange` props
- Error state: prop `error: string` — shows error below in danger color
- Focused state: accent border + accent-subtle shadow ring
- Height: 36px desktop, 44px mobile (via CSS `@media`)

**Select:**
- Custom styled dropdown (no browser native)
- Options as prop array
- Max-height 280px with overflow scroll
- On mobile: renders as a bottom sheet (full-width list from bottom), not floating dropdown

**DatePicker:**
- Wrapper around native `<input type="date">` with custom styling
- Label + error support same as Input
- Date output always formatted to ISO string internally

### Task 20.4 — Card component (`src/components/ui/Card.tsx`)

Props: `clickable` (boolean), `padding` (sm | md | lg), `className`.

- Background `--bg-surface`, border `--border`, radius 10px, shadow `--shadow-sm`
- Clickable variant: hover border `--border-strong`, shadow `--shadow-md`, cursor pointer
- Padding: sm=16px, md=24px, lg=32px

### Task 20.5 — DataTable component (`src/components/ui/DataTable.tsx`)

Props: `columns` (array of column defs), `data` (array), `loading` (boolean),
`emptyState` (ReactNode), `onRowClick`, `selectable` (boolean), `selectedRows`, `onSelectChange`.

Column def shape: `{ key, header, width?, align?, render?: (row) => ReactNode }`

- Column headers: 12px, weight 500, uppercase, `--text-secondary` color, `--bg-subtle` background
- Row height: 48px desktop, 52px mobile
- Alternate row shading: even rows `--bg-subtle`
- Row hover: `--bg-overlay`
- Selected row: 2px left border `--accent`, background `--accent-subtle`
- Sticky header on scroll
- Sticky first column on horizontal scroll (mobile)
- Loading state: 8 skeleton rows — grey pulsing bars matching column widths
- Empty state: renders the `emptyState` prop centered in the table body
- Selectable: checkbox column prepended, bulk selection via header checkbox

### Task 20.6 — Toast notification system (`src/components/ui/Toast.tsx` + `src/hooks/useToast.ts`)

Toast store (Zustand or React Context): array of `{ id, type, title, message, duration }`.

`useToast()` hook exports:
- `toast.success(title, message?)` — left border `--success`
- `toast.error(title, message?)` — left border `--danger`
- `toast.warning(title, message?)` — left border `--warning`
- `toast.info(title, message?)` — left border `--accent`

`<ToastContainer />` component:
- Fixed position: bottom-right on desktop (24px margin), bottom-center on mobile
- Auto-dismiss after 4 seconds (configurable)
- Manual X dismiss button
- Stack up to 3, oldest dismisses first
- Slide-in animation from right (desktop) / bottom (mobile)

### Task 20.7 — Modal component (`src/components/ui/Modal.tsx`)

Props: `open`, `onClose`, `title`, `size` (sm | md | lg | full), `children`, `footer`.

- Desktop: centered overlay, max-width by size (sm=400, md=600, lg=800, full=screen)
- Mobile: full-screen (100vw × 100vh), slide up from bottom
- Backdrop: semi-transparent dark overlay, click to close
- Focus trap: Tab cycles within modal when open
- ESC key closes modal
- Scroll lock on body when open

### Task 20.8 — Bottom Sheet component (`src/components/ui/BottomSheet.tsx`)

Mobile-only pattern. Used instead of dropdowns, date pickers, and modals on small screens.

Props: `open`, `onClose`, `title`, `children`, `snapPoints` (partial | full).

- Slides up from bottom, 90% screen height max
- Handle bar at top (drag to dismiss)
- Backdrop tap to close

### Task 20.9 — Skeleton loaders (`src/components/ui/Skeleton.tsx`)

Props: `width`, `height`, `variant` (text | rect | circle), `lines` (for text stacks).

- Animated CSS gradient sweep (shimmer effect)
- Colors use `--bg-subtle` to `--bg-overlay` for the shimmer

### Task 20.10 — Tooltip component (`src/components/ui/Tooltip.tsx`)

Props: `content`, `delay` (ms, default 600), `children`.

- Desktop only (never renders on mobile)
- Appears above element, max-width 200px
- Background `--text-primary`, text `--text-inverse`, 4px border-radius
- Delay before show: 600ms (prevents tooltip flash on casual mouse movement)

---

## PHASE 21 — App Shell: Navigation, Layout & Theme Toggle

**Goal:** The persistent app frame that surrounds every page. Sidebar, top bar, bottom tab bar,
breadcrumbs, and the content area with correct padding at every breakpoint.

### Task 21.1 — Top Bar (`src/components/layout/TopBar.tsx`)

Fixed at top, full width, height 56px (desktop) / 52px (mobile).
Background `--bg-surface`. Bottom border 1px `--border`.

**Contents left → right:**
- Hamburger icon (mobile only, opens sidebar overlay) — `List` icon from Phosphor
- HERMES logotype (text mark, links to `/`) — use `--text-primary` color, weight 700
- `flex-1` spacer
- Global search icon button → fires `Cmd+K` handler (opens search modal)
- Notification bell — Phosphor `Bell` icon, with unread count badge overlaid (shown when count > 0)
- System status dot — small 8px circle, color `--success`/`--warning`/`--danger` based on health ping.
  Has a tooltip "System: Healthy / Degraded / Unreachable". Clicks to `/system`.
- Theme toggle — Phosphor `Sun` (light) / `Moon` (dark) icon button. Calls `toggleTheme()`.

All icon buttons: 36×36px hit area, Ghost variant styling (transparent bg, hover `--bg-overlay`).

### Task 21.2 — Sidebar Navigation (`src/components/layout/Sidebar.tsx`)

Width: 240px expanded, 60px collapsed (icon-only, toggle via arrow at sidebar bottom).
On mobile: off-canvas, slides in as overlay from left (280px wide), backdrop behind.

State: `expanded` boolean in `localStorage` (persists collapse preference).

**Navigation structure** (hardcoded, not data-driven):

```
OVERVIEW
  Dashboard             /

OPERATIONS
  Chat with HERMES      /chat
  Upload Documents      /upload

FINANCE
  Invoices              (accordion parent, no route)
    Sales               /invoices/sales
    Purchases           /invoices/purchases
  Contacts              /contacts
  Payments              /payments

RECORDS
  Reports               /reports
  Documents             /documents
  Anomalies             /anomalies

ACCOUNTS
  Chart of Accounts     /accounts
  Audit Trail           /audit

SYSTEM
  Settings              /settings
  System Health         /system
```

Active item: background `--accent-subtle`, text `--accent`, 2px left border `--accent`.
Hover: background `--bg-overlay`.
Sub-items (under Invoices): 12px additional indent, `--body-sm` font size, accordion open/close.
Group labels (OVERVIEW, OPERATIONS, etc.): `--text-muted`, `--caption` size, uppercase, weight 500.
Collapsed mode: show only icons, hide labels and group headers.

### Task 21.3 — Bottom Tab Bar (`src/components/layout/BottomTabBar.tsx`)

**Mobile only** (hidden on `md:` breakpoint and above via Tailwind).

Height 64px. Fixed bottom. Background `--bg-surface`. Top border 1px `--border`.
Safe area inset-bottom padding (for iOS notched devices: `padding-bottom: env(safe-area-inset-bottom)`).

Tabs (5): **Home** (`/`), **Chat** (`/chat`), **Invoices** (`/invoices/sales`),
**Reports** (`/reports`), **More** (opens drawer with remaining nav items).

Active tab: icon filled-weight (Phosphor Bold), label in `--accent` color.
Inactive tab: icon regular-weight, label `--text-muted`.

"More" tab opens a `<BottomSheet>` listing all remaining navigation items.

### Task 21.4 — App Layout wrapper (`src/components/layout/AppLayout.tsx`)

Wraps all authenticated pages. Renders:
1. `<TopBar />`
2. `<Sidebar />` (positioned left, below top bar)
3. `<main>` content area (flex-1, scrollable, correct left-margin = sidebar width on desktop)
4. `<BottomTabBar />` (mobile only, positioned fixed bottom)
5. `<ToastContainer />` (fixed position, z-index highest)
6. `<SearchModal />` (initially closed)
7. `<FloatingChatWidget />` (floating button on all pages except `/chat`)

Content area inner padding: 24px all sides on desktop, 16px on mobile.
Max-width 1280px centered.

### Task 21.5 — Breadcrumbs (`src/components/layout/Breadcrumbs.tsx`)

Reads current route and renders a trail. Each segment is a link except the last (current page).

Format: `Dashboard > Invoices > Sales > INV-0042`

Font: `--caption` size, `--text-muted` color. Separator: `/` or `>` in `--text-muted`.

Shown below page title in the page header region, not in the top bar.

### Task 21.6 — Page Header pattern (`src/components/layout/PageHeader.tsx`)

Rendered at the top of every page's content area. Props: `title`, `breadcrumbs`, `actions`.

- `title`: `--display` size on desktop, `--display-sm` on mobile
- `breadcrumbs`: renders `<Breadcrumbs />`
- `actions`: ReactNode slot — renders primary action buttons top-right on desktop

On mobile: actions move to a sticky bottom bar (fixed, above bottom tab bar) to keep them
accessible without scrolling.

### Task 21.7 — React Router setup (`src/App.tsx`)

Set up all routes using `react-router-dom` v6 `<Routes>`:

```
/                → Dashboard
/chat            → ChatPage
/upload          → UploadPage
/invoices/sales  → SalesInvoicesPage
/invoices/sales/:id → InvoiceDetailPage
/invoices/purchases → PurchasesPage
/invoices/purchases/:id → BillDetailPage
/invoices/purchases/review/:id → BillReviewPage
/contacts        → ContactsPage
/contacts/:id    → ContactDetailPage
/payments        → PaymentsPage
/reports         → ReportsHubPage
/reports/:type   → ReportViewerPage
/documents       → FileCenterPage
/anomalies       → AnomaliesPage
/accounts        → AccountsPage
/audit           → AuditPage
/settings        → SettingsPage
/system          → SystemHealthPage
*                → 404 page
```

All routes wrapped in `<AppLayout>`.

---

## PHASE 22 — Dashboard Page

**Goal:** The first thing a user sees. Must load fast and answer three questions instantly:
How am I doing? What needs attention? What happened recently?

### Task 22.1 — Backend: Dashboard API endpoint

In `webapp/backend/routers/dashboard.py`:

`GET /api/dashboard/kpis` → returns:
```json
{
  "revenue_mtd": 125000,
  "expenses_mtd": 43000,
  "net_profit_mtd": 82000,
  "outstanding_receivables": 215000,
  "outstanding_count": 12,
  "overdue_total": 45000,
  "overdue_count": 3,
  "gst_liability_est": 22500,
  "revenue_prev_month": 98000,
  "expenses_prev_month": 52000,
  "outstanding_prev_week": 198000
}
```

`GET /api/dashboard/charts/revenue-expenses?months=12` → returns array of
`{month: "2025-03", revenue: 98000, expenses: 52000}` for the last N months.

`GET /api/dashboard/charts/expense-breakdown?month=current` → returns
`[{category: "Rent", total: 12000}, ...]` for the current month.

`GET /api/dashboard/charts/invoice-status?months=6` → returns
`[{month: "2025-03", paid: 8, sent: 3, overdue: 2, draft: 1}, ...]`.

`GET /api/dashboard/activity?limit=20` → returns array of recent activity items
`{type: "invoice_created"|"payment_received"|"expense_logged"|"anomaly_detected",
  description, amount, timestamp, link_id, link_type}`.

Write all these as SQLite queries in `webapp/backend/database.py`.

### Task 22.2 — KPI Cards

Create `src/pages/Dashboard.tsx`.

6 KPI cards in a 3×2 grid (desktop), 2×3 (tablet), horizontal scroll strip (mobile).

Each card is a `<Card>` component containing:
- Metric name: `--label` size, `--text-secondary`
- Main value: `--heading` size, `--text-primary`, wrapped in `<span className="text-mono">`
- Delta indicator: arrow icon + percentage + "vs last month" label in `--caption` size
  - Color logic: Revenue/Profit up = `--success`, down = `--danger`
  - Expenses up = `--danger` (more spending = bad), down = `--success`
  - Overdue up = `--danger`, down = `--success`
- Sparkline: 40px tall, no axis, just a line chart using a minimal SVG renderer
  (query last 7 daily values from `/api/dashboard/sparkline/:metric`)

Overdue Invoices card: add `border-l-2 border-danger` when count > 0.

Loading state: 6 skeleton cards pulsing.

### Task 22.3 — Charts section

Use `recharts` for all three charts.

**Revenue vs Expenses Line Chart:**
- `<LineChart>` with two `<Line>` components
- Colors: `var(--accent)` for Revenue, `var(--danger)` for Expenses
- X-axis: month abbreviations ("Jan", "Feb", etc.)
- Y-axis: formatted with `formatCurrency` abbreviation (1.2L, 4.5L)
- Custom `<Tooltip>` component styled with CSS tokens
- Period toggle buttons (3M / 6M / 12M): plain `<button>` elements, active state with `--accent-subtle` bg
- Responsive: use `<ResponsiveContainer width="100%" height={220}>`

**Expense Breakdown Donut:**
- `<PieChart>` with `innerRadius={60}` (donut hole)
- Center text: total expense amount in `--heading` size
- Colors: use a 6-color semantic palette derived from CSS token set (not random)
- Legend: below the chart, horizontal wrap, colored swatches + labels + amounts

**Invoice Status Distribution:**
- `<BarChart>` stacked
- Colors: paid=`--success`, sent=`--accent`, overdue=`--danger`, draft=`--neutral`
- X-axis: month abbreviations
- No Y-axis labels (just the stacked bars convey the trend)

All charts must rerender correctly when theme changes (recharts uses SVG, so they inherit CSS text colors automatically if `fill="currentColor"` is used for labels).

### Task 22.4 — Quick Actions Bar

Horizontal strip of 3 `<Button size="md" variant="secondary">` buttons with icons:
- `<UploadSimple />` **Upload Documents** → `navigate('/upload')`
- `<Chat />` **Chat with HERMES** → `navigate('/chat')`
- `<ChartLine />` **View Reports** → `navigate('/reports')`

On mobile: render as a 3-column grid, each button full-width in its column.

### Task 22.5 — Activity Feed

Scrollable list of the last 20 activity items from `/api/dashboard/activity`.

Each item:
- Left: a 32px circle icon with type-specific Phosphor icon (FileText, CurrencyDollar, Warning, etc.)
  inside a `--bg-subtle` circle
- Middle: description (bold entity names e.g. "**INV-0042** created for **Krishna Textiles**"),
  amount if applicable
- Right: relative timestamp in `--caption` size, `--text-muted`
- Full row is clickable → navigates to relevant detail page

Poll every 30 seconds using `setInterval` + `fetch`. Use a React state update to append new items
without full re-render.

Loading state: 8 skeleton list items.

Empty state: "No activity yet. Upload a document or start a conversation with HERMES."

"View full audit trail →" link at the bottom.

---

## PHASE 23 — AI Chat Interface

**Goal:** The most important creation surface in HERMES. Users speak to the agent to create
invoices, query data, and get insight. The UI must feel immediate and capable.

### Task 23.1 — Backend: Chat relay endpoint

In `webapp/backend/routers/chat.py`:

`POST /api/chat/message`
Request: `{ "message": string, "conversation_id": string, "attachments": [] }`
Response: streamed or polled

The nanobot agent runs as a separate PM2 process communicating via Telegram. The webapp chat
is a **second interface** into the same agent. Two implementation options:

**Option A (simpler):** The chat endpoint calls a local HTTP endpoint exposed by a thin FastAPI
shim inside nanobot. The nanobot gateway gets a `POST /agent/message` endpoint added that
accepts a message and returns a response. This requires a small modification to nanobot.

**Option B (queue-based):** Write messages to a `chat_messages` table in SQLite. A background
thread in nanobot polls this table, processes messages, writes responses back. The webapp polls
`GET /api/chat/messages/:conversation_id` for responses.

**Implement Option B** — it requires zero changes to nanobot's internal architecture.

Schema for chat (add to `hermes/schema.sql`):
```sql
CREATE TABLE IF NOT EXISTS chat_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL,          -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT               -- JSON: linked invoice id, bill id, etc.
);
```

Add a `hermes_tools.py` tool `WebChatReadTool` that the agent uses to read pending user messages
from this table, and `WebChatRespondTool` to write responses back. Add a cron or loop in nanobot
that checks this table every 2 seconds for new user messages.

`GET /api/chat/history/:conversation_id` → returns last 50 messages for the conversation.
`GET /api/chat/conversations` → returns list of conversation stubs (id, last message, timestamp).

### Task 23.2 — Full Chat Page layout (`src/pages/ChatPage.tsx`)

**Desktop:** CSS Grid, 60% left / 40% right.
- Left column: full-height chat (header + message list + input bar)
- Right column: context preview panel (shows live invoice preview or query results)

**Mobile:** Single column, full screen chat. "Preview" button (top right) opens bottom sheet.

### Task 23.3 — Message History area

Scrollable `<div>` with `overflow-y: auto`. Auto-scrolls to bottom on new messages.

User messages:
- Right-aligned flex row
- Bubble: background `--accent`, text `--text-inverse`, border-radius `16px 16px 4px 16px`
- Max-width 75% of chat area

HERMES messages:
- Left-aligned flex row
- 32px HERMES avatar circle (logomark icon) at left of bubble
- Bubble: background `--bg-surface`, border 1px `--border`, text `--text-primary`,
  border-radius `4px 16px 16px 16px`
- Max-width 80%

Timestamps: appear below each bubble on hover (desktop) / always visible (mobile) in `--caption`
size, `--text-muted`.

**Typing indicator:** Three animated dots in a HERMES-style bubble, shown while awaiting response.
CSS: `@keyframes typing-dot` with staggered `animation-delay` on each dot.

**Inline structured cards:** When HERMES responds with an invoice creation confirmation, the message
`metadata` field indicates a linked invoice ID. The message renderer checks for this and appends
an `<InvoicePreviewCard>` component inline below the text message.

`<InvoicePreviewCard>`:
- Compact card showing: invoice number, client name, total, due date, status badge
- Two buttons: "View Full Invoice" (navigates to detail page) and "Download PDF"
- Background `--bg-subtle`, 8px border-radius, subtle border

### Task 23.4 — Input Bar

Sticky at the bottom of the chat column. Background `--bg-surface`. Top border 1px `--border`.

Components (left → right in a flex row):
1. **Attach button** — Phosphor `Paperclip` icon, Ghost variant, 36px.
   Opens a file picker (PDF/JPG/PNG). Attached files shown as chips above the input.
2. **Textarea** — auto-growing (1 to 5 lines). Placeholder "Message HERMES…". Background `--bg-subtle`.
   `Enter` to send (Shift+Enter for new line). On mobile: use `<textarea rows={1}>`.
3. **Voice button** — Phosphor `Microphone` icon. On tap: starts browser Web Speech API transcription.
   While recording: button turns `--danger` color with a pulse animation. Transcript fills textarea.
4. **Send button** — Phosphor `PaperPlaneRight`, Primary variant, 36px square. Enabled only when textarea has content.

### Task 23.5 — Suggested prompts

When the message history is empty (new conversation), show 4 clickable prompt chips above the input bar:

```
"Create invoice for [Client] for ₹50,000 + 18% GST"
"Show all unpaid invoices from this month"
"What's our GST liability for October?"
"Flag any duplicate bills from last week"
```

These are ghost-styled `<button>` elements. On click: fill textarea + auto-send.
Hidden once the conversation has any messages.

### Task 23.6 — Context Preview Panel (desktop right column)

Default state: shows a placeholder illustration + "Start a conversation — HERMES will show previews here."

When the user is discussing an invoice (detected via metadata in latest assistant message):
- Shows a `<InvoicePreviewFull>` component — a rendered HTML representation of the invoice
  matching the PDF layout as closely as possible (Jinja2 PDF template is for WeasyPrint;
  this is a separate HTML re-implementation for live preview)
- Updates in real-time as the conversation progresses (e.g., after "Change the rate to ₹500",
  the preview updates)

When the user asks a data query:
- Shows a simple table or stat display of the query result

### Task 23.7 — Chat History Sidebar (desktop only)

Left sidebar within the chat page, 200px wide, showing past conversations.

Each item: first message excerpt, date. Click → loads that conversation's messages.
Search input at top to filter by content.

On mobile: accessible via a "History" icon button in the chat page's top bar.

### Task 23.8 — Floating Chat Widget (`src/components/chat/FloatingChatWidget.tsx`)

Renders on all pages EXCEPT `/chat`. A 52px circular button fixed bottom-right (desktop: 24px margin,
mobile: 16px margin, above bottom tab bar).

Icon: Phosphor `Chat` filled. Background `--accent`. Color `--text-inverse`.

On click:
- Desktop: opens a 380px×520px chat popover panel (floating, above all content, right-anchored)
- Mobile: navigates to `/chat` (full-screen chat)

The popover has the same message history, input bar, and typing indicator as the full chat page.
It shares the same conversation (same `conversation_id` as the `/chat` page).

---

## PHASE 24 — Sales Invoices (List + Detail + Actions)

**Goal:** The primary outgoing invoice management surface. List with filters, detail view,
PDF download, and status management.

### Task 24.1 — Backend: Sales Invoice API

In `webapp/backend/routers/invoices.py`:

`GET /api/invoices/sales` query params: `status`, `client_id`, `search`, `from_date`, `to_date`,
`page` (default 1), `per_page` (default 50) → paginated list with `{items, total, pages, summary}`

`summary` sub-object: `{total_amount, paid_amount, outstanding_amount, count_by_status}`

`GET /api/invoices/sales/:id` → full invoice detail with items, payment history, client info

`POST /api/invoices/sales/:id/mark-paid` → updates invoice status (write endpoint)
`POST /api/invoices/sales/:id/void` → voids invoice

`GET /api/invoices/sales/:id/pdf` → streams PDF file from filesystem
(reads invoice's `pdf_path` from DB, serves file via `FileResponse`)

`GET /api/invoices/sales/:id/payment-history` → list of payments recorded against this invoice

### Task 24.2 — Sales Invoice List page (`src/pages/SalesInvoicesPage.tsx`)

**Page header:** "Sales Invoices" + "New Invoice" button (navigates to `/chat` with prefill).

**Filter bar** (persistent, horizontal, above table):
- Date range picker (preset chips: This Month / Last Month / This Quarter / This FY + Custom)
- Status multi-select (pill-style toggle buttons: All, Draft, Sent, Paid, Overdue, Void)
- Customer search input (debounced 300ms, calls `/api/contacts?search=` and shows dropdown)
- "Clear filters" ghost link (visible only when any filter is active)
- On mobile: filters hidden behind a "Filter" button that opens a bottom sheet

**Summary bar** above the table (updates with filters):
`"Showing 45 invoices · Total ₹X · Paid ₹X · Outstanding ₹X"`
Numbers in `--text-mono` class. `--body-sm` size.

**Table using `<DataTable>` component:**

Columns: Invoice #, Customer, Issue Date, Due Date (red if past due), Amount, GST, Status, Actions.

Row actions (three-dot `<DropdownMenu>` — a small popover component):
- View Invoice
- Download PDF
- Mark as Paid (hidden if already paid/void)
- Void (hidden if paid)

Row click (anywhere except actions column) → navigate to `/invoices/sales/:id`.

**Bulk actions bar** (appears as sticky top bar when any row selected):
- "X selected" count
- Download selected (ZIP) button
- Mark selected as Paid button
- Export selected to CSV button
- Deselect all link

**Pagination:** "< Prev · 1 · 2 · 3 · Next >" below table. Shows "Showing 1–50 of 127 invoices".

**Empty state:** Illustration + "No invoices found. Chat with HERMES to create your first invoice."
with a "Open Chat →" primary button.

### Task 24.3 — Invoice Detail page (`src/pages/InvoiceDetailPage.tsx`)

Route: `/invoices/sales/:id`. Fetches from `/api/invoices/sales/:id`.

**Desktop layout:** 60% left (invoice preview) / 40% right (action panel).
**Mobile layout:** invoice preview card on top, action panel below (scrolled).

**Left panel — Invoice preview:**
- Rendered HTML representation of the invoice (matching the PDF template aesthetics)
- Business logo top-right, business name/address top-left
- Client info, invoice number, dates
- Line items table with proper Indian number formatting
- Subtotal, GST breakdown, Grand Total
- Notes section

**Right panel — Action panel:**
- Large status badge (current status)
- `"Download PDF"` — Primary button, full-width. Calls `/api/invoices/sales/:id/pdf`,
  triggers browser download with filename `INV-0042_ClientName_2025-03-14.pdf`.
  Show brief loading state while PDF is being fetched.
- `"Mark as Paid"` or `"Record Payment"` — Secondary button (hidden if paid/void)
- `"Void Invoice"` — Danger ghost button (with confirmation modal)
- Horizontal rule
- **Invoice timeline:** Visual step-line: Created → Sent → Paid (or Overdue). Each step has
  a date below it. Completed steps: filled circle in `--accent`. Current/overdue: amber or danger.
- **Payment history table:** If any payments recorded: Date | Amount | Mode | Reference columns.
  "Total Paid: ₹X | Remaining: ₹X" below table.
- **Notes:** Editable text area. Auto-saves on blur via `PATCH /api/invoices/sales/:id/notes`.

---

## PHASE 25 — Purchase Bills & Upload Flow

**Goal:** The inbound document processing surface. Upload → background processing → review.
The bill review page is the most complex UX surface in the entire webapp.

### Task 25.1 — Backend: Bills API

`GET /api/invoices/purchases` → same pagination structure as sales invoices but for bills
`GET /api/invoices/purchases/:id` → full bill detail with items + original file path
`GET /api/invoices/purchases/:id/original` → serves the original uploaded file (PDF or image)
`POST /api/invoices/purchases/:id/finalize` → marks a REVIEW-status bill as finalized with corrected data
`POST /api/upload/bills` → accepts multipart file upload, saves to disk, queues for processing

Queue mechanism: the upload endpoint writes a row to an `upload_queue` table in SQLite.
A background thread in the nanobot agent polls this table and processes documents via OCR.

`GET /api/upload/queue` → returns current queue status
`POST /api/upload/queue/:id/reprocess` → requeues a failed item

### Task 25.2 — Purchase Bills List page

Same structure as Sales Invoices list. Key differences:
- Status column includes PROCESSING (pulsing badge) and REVIEW (warning badge)
- REVIEW rows: entire row has a left border `--warning` and slightly highlighted background
- Filter includes "Needs Review" quick filter
- No "Download PDF" action in row actions (originals are served differently)

Auto-refresh: the list polls `GET /api/invoices/purchases?status=processing` every 5 seconds
and updates status badges in-place without a full page reload.

### Task 25.3 — Upload Page (`src/pages/UploadPage.tsx`)

Route: `/upload`. Also reachable by dragging files into the Purchases page.

**Upload Zone:**
- Large dashed-border box, center of page
- Phosphor `UploadSimple` icon (48px) centered
- Text: "Drop invoices here" in `--heading` size
- Below: "or click to browse" in `--body-sm`, `--text-muted`
- Accepted types: PDF, JPG, PNG, TIFF. Max size: 25MB per file. Max 20 files per batch.
- Drag-over state: border becomes solid `--accent`, background `--accent-subtle`
- Use `react-dropzone` for drag-drop + file picker

**Processing Queue Table** (appears below upload zone after files are added):

Columns: Filename, Size, Status, Action

Status cells:
- QUEUED: grey badge, no action
- PROCESSING: animated pulsing blue badge (`--accent` with opacity animation)
- REVIEW NEEDED: amber badge + "Review →" button
- FINALIZED: green badge + "View" link
- ERROR: red badge + "Retry" button

This table is live — poll `/api/upload/queue` every 3 seconds, update rows.
A `<AnimatePresence>` transition (or CSS transition) fades in new status changes.

On mobile: table becomes a card-per-file stack (not horizontal table scroll).

### Task 25.4 — Bill Review Page (`src/pages/BillReviewPage.tsx`)

Route: `/invoices/purchases/review/:id`.

This is the most important UX in the entire app. Layout is strict: side-by-side on desktop,
stacked (document on top, form below) on mobile.

**Desktop layout: 60% document / 40% form panel.**

**Left panel — Original Document Viewer:**
- Renders the original uploaded file
- If PDF: use `react-pdf`'s `<Document>` + `<Page>` component
  - Navigation: Page X of Y, Prev/Next page buttons
  - Zoom: percentage display, `+` `-` buttons, keyboard `+`/`-` support
- If image: `<img>` tag with CSS transform-based zoom on pinch/scroll
- Rotate button (rotates the render 90° clockwise)
- Fit-to-width button (resets zoom to fill panel width)
- "Download Original" link (fetches from `/api/invoices/purchases/:id/original`)

**Right panel — Extracted Data Form:**
Header: "HERMES extracted this data. Review and confirm."

Fields (each an `<Input>` or `<Select>` component, pre-filled with OCR output):
- Vendor Name
- Vendor GSTIN (with format validation: 15 chars, alphanumeric)
- Vendor Invoice Number
- Invoice Date (`<DatePicker>`)
- Due Date (`<DatePicker>`)
- Expense Account (`<Select>` from chart of accounts)

**Confidence indicator per field:** A small colored dot (green/amber/red) to the right of each
label. Green = OCR confidence ≥ 90%. Amber = 70–90%. Red = < 70%. Tooltip on hover:
"OCR confidence: 87%". Red fields are focused/highlighted on page load.

**Line Items table (editable):**
- Inline table with Description, Qty, Rate, Amount columns
- Each cell is an editable `<input>` on click
- "Add row" button at bottom of table
- Delete row: trash icon on each row (appears on hover)
- Totals row: auto-calculated, read-only

**Tax summary:** CGST / SGST / IGST fields, auto-summed from line items GST percentages.

**HERMES Notes section:**
A non-editable info box styled with `--warning-bg` background (or `--accent-subtle` for
informational notes). Shows any observations HERMES flagged during processing.
Example: "⚠ This vendor billed ₹42,500 on 14 Feb. This bill is for the same amount."

**Action buttons (bottom of form panel):**
- `"Confirm & Finalize"` — Primary. POSTs corrected data to `/api/invoices/purchases/:id/finalize`.
  On success: navigates to bill detail page with success toast.
- `"Reject & Re-upload"` — Danger ghost. Opens confirmation modal.

---

## PHASE 26 — Document Viewer & File Center

**Goal:** The unified repository for every file HERMES has touched. First-class section,
not an attachment panel.

### Task 26.1 — Backend: File Center API

`GET /api/files` query params: `type` (uploaded | generated | reports | exports), `search`,
`page` → returns file listing with metadata

Each file item: `{filename, display_name, type, linked_to, linked_id, created_at, file_size, path}`

`GET /api/files/download/:file_id` → streams file from VM filesystem via `FileResponse`.
Filename in Content-Disposition header formatted as: `INV-0042_ClientName_2025-03.pdf`.

`GET /api/files/bulk-download` → accepts array of file IDs, creates ZIP in temp dir,
streams ZIP. This is a synchronous endpoint that waits for the ZIP to be built.

### Task 26.2 — File Center page (`src/pages/FileCenterPage.tsx`)

Route: `/documents`.

**Left sidebar filter tree (200px, desktop only):**
```
All Documents
├── Uploaded Documents
│   ├── Vendor Invoices
│   └── Others
├── Generated Documents
│   ├── Sales Invoices (PDF)
│   └── Reports
└── Exports
```

Clicking a node filters the main list. Active node highlighted with `--accent-subtle` background.
On mobile: replace with a horizontal scroll filter chip row above the list.

**Main area controls:**
- Search input (search by filename or linked entity name)
- List/Grid toggle (two icon buttons: `<List />` and `<SquaresFour />`)
- "Bulk Download" button (appears when any file is selected)

**List view columns:** Filename (with file type icon), Linked To, Date, Size, Actions (Preview, Download).

**Grid view:** 3 columns on desktop, 2 on tablet, 1 on mobile. Card per file:
- File icon (large: PDF icon, image thumbnail, ZIP icon based on type)
- Filename (truncated at 2 lines)
- Date
- Download icon overlay on hover

### Task 26.3 — Document Viewer Drawer

When "Preview" is clicked, instead of opening a new page, open a **right-side drawer panel.**
Width: 520px on desktop (content area shrinks left). Full-screen on mobile.

Drawer contents:
- Header: filename, close (X) button, "Download" button (top right, always visible)
- Document rendered inline (PDF via `react-pdf`, images via `<img>`)
- Bottom panel: file metadata (linked transaction, upload date, size, processing notes)
- Navigate previous/next file (arrows at top)

Opening animation: slides in from right, 250ms ease. Background dims slightly.

---

## PHASE 27 — Contacts

**Goal:** Customer and vendor management with full ledger visibility.

### Task 27.1 — Backend: Contacts API

`GET /api/contacts` query params: `type` (customer | vendor | all), `search` → list
`GET /api/contacts/:id` → full contact with invoice history, payment history, totals
`GET /api/contacts/:id/ledger` → running balance ledger entries (date, description, debit, credit, balance)
`GET /api/contacts/:id/statement/pdf` → generates and streams a contact statement PDF

### Task 27.2 — Contacts List page (`src/pages/ContactsPage.tsx`)

**Type toggle:** "All / Customers / Vendors" pill buttons at top, updates the list.

**Search bar:** Debounced 300ms, searches name + GSTIN + phone.

**Table columns:** Name, Type (badge), GSTIN, Outstanding (color-coded), Total Transactions, Actions.

Outstanding color logic:
- Zero: `--success` colored "₹0"
- Non-zero: `--warning` colored amount
- Overdue items: `--danger` colored amount

Row click → `/contacts/:id`.

### Task 27.3 — Contact Detail page (`src/pages/ContactDetailPage.tsx`)

**Header card:** Name, type badge, GSTIN, email, phone, address. "Edit" button (opens modal form).

**4 tabs:** Overview | Transactions | Ledger | Notes

**Overview tab:**
- 4 stat cards: Total Billed, Total Paid, Outstanding, Last Payment Date
- "Download Statement" button → calls `/api/contacts/:id/statement/pdf`, triggers download

**Transactions tab:**
- Same `<DataTable>` as invoices list, filtered to this contact
- "Amount Paid" / "Balance" summary below table

**Ledger tab:**
- Running balance table: Date | Description | Debit | Credit | Balance
- Opening balance row at top (pinned)
- All amounts in `--text-mono`
- Date range filter (affects displayed range, not the opening balance calculation)
- "Download CSV" button (exports visible range)

**Notes tab:**
- Free-text `<textarea>`, auto-saves on blur via `PATCH /api/contacts/:id/notes`

---

## PHASE 28 — Payments & Reconciliation

**Goal:** Record payments against invoices and perform manual bank statement reconciliation.

### Task 28.1 — Backend: Payments API

`GET /api/payments` query params: date range, mode, contact → paginated list
`POST /api/payments` → record a new payment (write endpoint)
  Body: `{invoice_ids, amount, date, mode, reference, notes}`
`GET /api/payments/reconciliation` → returns HERMES payments + imported bank entries with match suggestions

`POST /api/upload/bank-statement` → accepts CSV file, parses into `bank_statement_entries` table
`POST /api/payments/reconciliation/confirm-match` → confirms a match between HERMES payment and bank entry

### Task 28.2 — Record Payment (modal/bottom sheet)

`<RecordPaymentModal>` component, rendered as `<Modal>` on desktop, `<BottomSheet>` on mobile.

Fields:
- Invoice(s) being paid: multi-select searchable dropdown (searches by invoice number or client name)
  Pre-filled if opened from an invoice detail page.
- Amount paid: number input with ₹ prefix
- Payment date: `<DatePicker>` defaulting to today
- Payment mode: `<Select>` with options Cash | Bank Transfer (NEFT/RTGS/IMPS) | UPI | Cheque | Card
- Reference number: text input (UTR, cheque no., UPI transaction ID, etc.)
- Notes: optional text input

Live calculation below the form: "Paying ₹X against total ₹Y. ₹Z will remain outstanding."

On submit: `POST /api/payments`, close modal, show success toast, refresh the parent page.

### Task 28.3 — Payments List page (`src/pages/PaymentsPage.tsx`)

Standard list page. Table columns: Date, Mode, Amount, Reference, Linked Invoices (count + client name), Actions.

"Record Payment" primary button in page header.

### Task 28.4 — Reconciliation view

Sub-page at `/payments/reconciliation`.

**Two-panel layout:** HERMES payments (left) | Bank statement entries (right).
On mobile: tabbed view (HERMES tab / Bank tab) with a "Matches" tab showing confirmed matches.

Summary strip at top: "X matched · Y unmatched in HERMES · Z unmatched in bank"

Each unmatched HERMES payment shown with suggested bank match (if any) at a confidence ≥ 70%.
Suggestion shown as: "Possible match ↔ [bank entry] (₹X, [date]) — 92% confidence"
"✓ Confirm Match" button and "✗ Ignore" button.

Confirmed matches collapse into a "Matched" section at the bottom.

---

## PHASE 29 — Chart of Accounts & Mapping Rules

**Goal:** View and manage the account structure used for categorizing all transactions.

### Task 29.1 — Backend: Accounts API

`GET /api/accounts` → full tree structure with balances per account
`POST /api/accounts` → create new account
`PATCH /api/accounts/:id` → update account name or type
`DELETE /api/accounts/:id` → deactivate (not hard delete; fails if account has transactions)
`GET /api/accounts/mapping-rules` → list of auto-categorization rules
`POST /api/accounts/mapping-rules` → create rule
`PATCH /api/accounts/mapping-rules/:id` → update or toggle rule
`DELETE /api/accounts/mapping-rules/:id` → delete rule

### Task 29.2 — Chart of Accounts page (`src/pages/AccountsPage.tsx`)

**Tree view** with expand/collapse per group. Use a recursive `<AccountTreeNode>` component.

Each node: account code (monospace), account name, type badge, current balance (right-aligned).
Expand/collapse: arrow icon rotates on toggle. CSS transition on height.

Add account: "+ Add Account" button opens inline form inserted at the correct tree level.
Edit: pencil icon on hover → inline edit mode for name.
Deactivate: disabled icon with confirmation popover.

### Task 29.3 — Mapping Rules sub-page

Table of current rules with columns: Condition Type, Match Value, Maps To Account, Status (active/inactive), Actions.

"Add Rule" opens a simple form:
- Rule type: Vendor Name | Description Contains
- Match value: text input
- Map to account: `<Select>` from chart of accounts tree
- Active toggle

Rules are reorderable via drag handle (HTML5 drag-and-drop or a simple up/down arrow approach).

---

## PHASE 30 — Reports Hub & Financial Reports

**Goal:** The full reports surface covering all report types.

### Task 30.1 — Backend: Reports API

`GET /api/reports/pl?from=&to=` → P&L data (structured JSON for HTML render)
`GET /api/reports/balance-sheet?as_of=` → Balance Sheet data
`GET /api/reports/cash-flow?from=&to=` → Cash Flow data
`GET /api/reports/trial-balance?as_of=` → Trial Balance data
`GET /api/reports/general-ledger?account_id=&from=&to=` → General Ledger entries
`GET /api/reports/day-book?date=` → Day Book entries for a specific date
`GET /api/reports/receivables-aging` → aging buckets (0-30, 31-60, 61-90, 90+ days)
`GET /api/reports/payables-aging` → same for payables
`GET /api/reports/customer-outstanding` → per-customer breakdown
`GET /api/reports/vendor-outstanding` → per-vendor breakdown
`GET /api/reports/expense-category?from=&to=` → expense by category
`GET /api/reports/expense-vendor?from=&to=` → expense by vendor

For PDF generation (each report type):
`POST /api/reports/:type/pdf` → triggers WeasyPrint generation via `hermes.pdf`, returns `{url: "/files/reports/..."}`
`POST /api/reports/:type/excel` → generates XLSX via `openpyxl`, returns download URL

### Task 30.2 — Reports Hub page (`src/pages/ReportsHubPage.tsx`)

Clean card grid. No sidebar — the hub is the navigation.

**3-column grid on desktop, 1 column on mobile.**

Each card: icon (48px, Phosphor), report title in `--subheading` size, 1-line description
in `--body-sm` `--text-secondary`, last generated date in `--caption`, "Run Report →" button.

Sections (card groups with a `--subheading` header per section):
- Financial Reports (P&L, Balance Sheet, Cash Flow, Trial Balance, General Ledger, Day Book)
- GST Reports (GSTR-1, GSTR-2B Reconciliation, GST Liability, ITC Tracker, HSN/SAC Summary, GST Export)
- Receivables (Aging, Customer Outstanding, Invoice Status)
- Payables (Aging, Vendor Outstanding, Bill Status)
- Expenses (By Category, By Vendor, Month-on-Month Trend)
- HERMES Intelligence (Anomaly, Duplicate Detection, Vendor Price Drift, Processing Quality, Audit Trail)

Custom Report Builder card at the bottom of the hub with a distinct "Build →" button.

### Task 30.3 — Report Viewer page (`src/pages/ReportViewerPage.tsx`)

Route: `/reports/:type` with query params for date range.

**Layout:** Date range selector at top → Report content area → Download bar at bottom.

Date range selector (varies per report type):
- P&L, Expenses: `from_date` + `to_date` date pickers + preset chips (This Month, Last Month, etc.)
- Balance Sheet: single "as of" date picker
- GST: quarter selector (Q1 Apr-Jun, Q2 Jul-Sep, Q3 Oct-Dec, Q4 Jan-Mar + year)
- Aging reports: no date selection (always current)

"Run Report" button → calls the API endpoint → displays structured HTML report in the content area.

Report content area styling:
- White background even in dark mode (reports must print correctly — they use their own styling)
- Report header: business name + logo, report title, period, generated-on timestamp
- Numbers: right-aligned, `--font-mono`
- Subtotal rows: bold, `--bg-subtle` background
- Total rows: bold, slightly larger font, `--bg-overlay` background
- Negative values: parentheses notation `(₹1,23,456)`, `--danger` color

**Download bar** (sticky bottom of content area):
- "Download PDF" primary button → `POST /api/reports/:type/pdf` → polls for completion → triggers download
- "Download Excel" secondary button → `POST /api/reports/:type/excel` → triggers download
- "Print" ghost button → `window.print()` with a `@media print` stylesheet that removes the nav

Loading state for report generation: spinner inside the report content area, "Generating…" text.

---

## PHASE 31 — GST Reports

**Goal:** GST is critical for Indian SMBs. GST reports need dedicated UX beyond the generic report viewer.

### Task 31.1 — Backend: GST API

`GET /api/reports/gst/gstr1?quarter=Q1&year=2025` → structured GSTR-1 data:
```json
{
  "b2b": [{invoice details...}],
  "b2c_large": [...],
  "b2c_small_summary": [...],
  "cdn": [...],
  "summary": {
    "total_taxable": 450000,
    "total_igst": 0,
    "total_cgst": 40500,
    "total_sgst": 40500
  }
}
```

`GET /api/reports/gst/itc-tracker?quarter=` → ITC data (input tax from vendor bills)
`GET /api/reports/gst/hsn-summary?quarter=` → HSN/SAC summary
`POST /api/reports/gst/export-json?quarter=` → generates GST portal-ready JSON, returns download URL

### Task 31.2 — GST Reports page

Dedicated page at `/reports/gst`. Not the generic report viewer — a custom page.

**Quarter selector at top:** Q1 (Apr-Jun) / Q2 (Jul-Sep) / Q3 (Oct-Dec) / Q4 (Jan-Mar) + year picker.

**Summary cards (3 cards):**
- Output Tax Collected: ₹X (CGST + SGST or IGST)
- Input Tax Credit: ₹X
- Net GST Payable: ₹X (difference, highlighted in `--danger` if positive)

**Tabs:** GSTR-1 | Input Tax Credit | HSN/SAC Summary

**GSTR-1 tab:**
- B2B invoices table (invoice-wise detail)
- B2C summary row
- Total row

**ITC tab:**
- Vendor-wise ITC table
- Category summary

**Export section:**
- "Export for GST Portal (JSON)" primary button
- Downloads a JSON file in exact GST portal format
- Helper text: "Upload this JSON at gstn.org → Returns → GSTR-1 → Upload JSON"

---

## PHASE 32 — Intelligence & Specialty Reports

### Task 32.1 — Backend: Intelligence Reports API

`GET /api/reports/anomaly-report` → all flagged anomalies with resolution status
`GET /api/reports/duplicate-detection` → pairs of suspected duplicate bills
`GET /api/reports/vendor-spend-analysis?vendor_id=&months=12` → price drift data per vendor
`GET /api/reports/processing-quality?from=&to=` → OCR stats (avg confidence, correction rate, error rate)
`GET /api/reports/audit-trail?from=&to=&user=&action_type=` → paginated audit log

### Task 32.2 — Intelligence report pages

Each renders in the generic Report Viewer page with custom rendering components for each type.

**Vendor Spend Analysis:** line chart per vendor showing price per unit over time.
If price jumps > 20% in a period, the data point is marked with a warning indicator.

**Processing Quality:** a dashboard-style report with:
- Average OCR confidence (gauge or large number)
- Correction rate (% of fields manually edited after extraction)
- Error rate (% of documents that failed processing)
- Per-vendor OCR quality table (some vendors have worse scan quality than others)

---

## PHASE 33 — Custom Report Builder

**Goal:** Allow power users to build ad-hoc reports without writing SQL.

### Task 33.1 — Backend: Custom Report Builder API

`POST /api/reports/custom/preview` → accepts builder config, returns data (up to 100 rows for preview)
`POST /api/reports/custom/generate` → full run, generates PDF/Excel
`GET /api/reports/custom/templates` → list of saved templates
`POST /api/reports/custom/templates` → save a template
`DELETE /api/reports/custom/templates/:id` → delete saved template

### Task 33.2 — Custom Report Builder page (`src/pages/CustomReportBuilderPage.tsx`)

Route: `/reports/custom`.

**Left panel (300px, desktop):** Builder controls.
- "Add Dimension" — dropdown: Vendor | Customer | Category | Month | Quarter
- "Add Metric" — dropdown: Total Amount | Count | Average | Min | Max
- "Add Filter" — date range, vendor/customer search, status, amount range
- Dimensions and metrics shown as draggable chips with remove (×) buttons
- "Save Template" — opens a name-input modal and saves to API
- Saved templates listed below controls (click to load)

**Right panel:** Live preview table. Updates when builder config changes (debounced 500ms, calls `/preview`).

**Bottom action bar:**
- "Run Full Report" → POST `/generate` → download PDF or Excel (user's choice via a toggle)

---

## PHASE 34 — Anomaly & Alert Center

**Goal:** A dedicated workspace for reviewing all anomalies HERMES has flagged.

### Task 34.1 — Backend: Anomalies API

`GET /api/anomalies` query params: `status` (all | unreviewed | acknowledged | escalated | dismissed),
`type`, `from_date`, `to_date` → paginated list

`PATCH /api/anomalies/:id/acknowledge` → marks anomaly as reviewed and acceptable
`PATCH /api/anomalies/:id/escalate` → marks for escalation with optional comment
`PATCH /api/anomalies/:id/dismiss` → marks as false positive with a reason code

`GET /api/anomalies/count/unreviewed` → returns `{count: N}` — used by the nav badge

### Task 34.2 — Anomalies page (`src/pages/AnomaliesPage.tsx`)

Route: `/anomalies`.

**Page header:** "Anomalies" + unreviewed count in a large `--danger` badge.

**Filter bar:** Status filter (All / Unreviewed / Acknowledged / Escalated / Dismissed),
anomaly type filter, date range.

**Anomaly Cards** (card per anomaly, not table rows — they need more real estate):

```
┌─────────────────────────────────────────────────────────┐
│ [⚠ DUPLICATE INVOICE badge]           [Confidence: 94%] │
│                                                          │
│  Possible Duplicate Invoice                              │
│  BILL-0041 from Rajan Traders (₹42,500) closely matches │
│  BILL-0029 from the same vendor 12 days prior.          │
│                                                          │
│  [View BILL-0041 →]  [View BILL-0029 →]                 │
│                                                          │
│  Flagged: 14 Mar 2025, 4:22 PM                          │
│  [Acknowledge]  [Escalate]  [Dismiss ↓]                 │
└─────────────────────────────────────────────────────────┘
```

Card background: `--bg-surface`. Left border: 3px `--warning` for unreviewed.
Once acknowledged: left border `--success`, background slightly muted.
Once dismissed: `opacity: 0.6`, left border `--neutral`.

**Acknowledge action:** Immediately updates card status (optimistic UI), sends PATCH to API.

**Escalate action:** Opens a small modal with a text input for escalation comment.

**Dismiss action:** Opens a small popover with radio options:
"Same vendor, different branch" | "One-time price change" | "Already verified externally" | "Other"
Then dismisses on confirm. Reason sent to API.

### Task 34.3 — Nav badge for anomalies

In `<Sidebar>` and `<BottomTabBar>`, the "Anomalies" nav item shows an unread count badge.
Poll `/api/anomalies/count/unreviewed` every 60 seconds. Badge uses `--danger` background.

---

## PHASE 35 — Audit Trail & Compliance Log

### Task 35.1 — Backend: Audit API

Audit trail is written by the agent (`hermes_tools.py` should call `db.log_audit_event()` at the
end of every tool that modifies data). The webapp only reads.

`GET /api/audit` query params: from, to, user (always "agent" or "webapp"), action_type, record_type → paginated

Action types: CREATE | EDIT | DELETE | DOWNLOAD | PROCESS | EXPORT | SETTING_CHANGE | NOTE_ADDED

`GET /api/audit/export` query params: from, to → streams CSV file

### Task 35.2 — Audit Trail page (`src/pages/AuditPage.tsx`)

Full-width table. Info banner at top: "This log is read-only and cannot be modified."

Columns: Timestamp (monospace), Source (Agent / Webapp), Action Type (colored badge),
Record (linked chip — clickable, navigates to the entity), Details (truncated, "expand" link).

"Expand" row: expands below to show full detail including before/after values for EDIT actions.

Sticky filter bar: date range, action type multi-select, record type.

"Export to CSV" button in page header. On click: opens a date range selector modal,
then calls `/api/audit/export`, triggers CSV download.

---

## PHASE 36 — Notifications Center

### Task 36.1 — Backend: Notifications API

Notifications are generated and stored in a `notifications` table by the agent tools.
The webapp reads and manages them.

`GET /api/notifications` query params: `tab` (all | unread | anomalies | system), `page`
`GET /api/notifications/count/unread` → `{count: N}` — used by bell badge
`POST /api/notifications/mark-read` → body: `{ids: []}` or `{all: true}`

### Task 36.2 — Notification Panel (`src/components/notifications/NotificationPanel.tsx`)

A slide-in drawer from the right side. Width 380px on desktop, full-width on mobile.

**Triggered by:** clicking the bell icon in the top bar.

Header: "Notifications" title + "Mark all as read" ghost button.

**Tabs:** All | Unread | Anomalies | System

Each notification item:
- 32px icon circle (type-specific icon, colored background per type)
- Title: `--body-sm` weight 600 (unread) / 400 (read)
- Description: `--caption` size, `--text-secondary`, single line truncated
- Timestamp: `--caption` size, `--text-muted`, right-aligned
- Left side: 6px blue dot indicator (only for unread)
- Full row clickable → marks as read + navigates to relevant page + closes panel

Unread notifications: `--bg-subtle` row background. Read: `--bg-surface`.

### Task 36.3 — Bell badge in TopBar

Subscribe to `/api/notifications/count/unread` (polling every 30 seconds).
Badge: small red circle with count number, overlaid top-right of the bell icon.
Hidden when count = 0. Shows count up to 99, then "99+" for more.

---

## PHASE 37 — Global Search

### Task 37.1 — Backend: Search API

`GET /api/search?q=&types=` → searches across multiple entity types simultaneously

Returns:
```json
{
  "invoices": [{id, number, client_name, amount, status}],
  "contacts": [{id, name, type, gstin}],
  "documents": [{id, filename, type, linked_to}],
  "reports": [{id, name, type, created_at}]
}
```

Each type limited to 5 results. All results limited to 20 total.

Debounced server-side search — queries SQLite with FTS5 (full-text search) where available,
otherwise `LIKE '%query%'` on key columns.

### Task 37.2 — Search Modal (`src/components/search/SearchModal.tsx`)

**Trigger:** `Cmd+K` (Mac) / `Ctrl+K` (Windows/Linux). Also the search icon in TopBar.

**Appearance:** centered modal overlay, 600px wide on desktop, full-width on mobile.
Backdrop darkens. Opens with a smooth scale + fade animation (150ms).

**Input:** Large (18px), auto-focused on open. Placeholder "Search invoices, contacts, documents…"
Debounce: 200ms before calling API.

**Results:**
- Grouped by type (INVOICES, CONTACTS, DOCUMENTS, REPORTS)
- Each group has a section label in `--label` size, `--text-muted`
- Max 5 items per group, link to "View all X results →" if more
- Each result item: icon + primary text + secondary text (amount, status, date)

**Empty states:**
- Empty input: show "Recent searches" (last 5, stored in `localStorage`)
- No results: "No results for '[query]'"

**Keyboard navigation:**
- Arrow Up/Down: move selection highlight
- Enter: navigate to selected result
- Escape: close modal

---

## PHASE 38 — Import / Export

### Task 38.1 — Backend: Import/Export API

`POST /api/import/contacts` → accepts CSV file, validates, returns preview + import result
`POST /api/import/opening-balances` → accepts CSV/Excel, validates structure
`POST /api/import/bank-statement` → accepts CSV, parses into bank_statement_entries table

`POST /api/export/data` → full data backup as JSON/CSV ZIP (generates async, returns job ID)
`GET /api/export/data/:job_id/status` → checks if export is ready
`GET /api/export/data/:job_id/download` → streams the ZIP once ready

### Task 38.2 — Import Center page (sub-page under Settings)

Route: `/settings/import`.

Three sections — one per import type.

Each section follows the same 4-step flow:
1. Download sample template (link to `/api/import/:type/sample.csv`)
2. Upload file (drag-drop zone, limited to 1 file)
3. Preview table: first 20 rows, validation status per row (green ✓ valid, red ✗ error with reason)
4. Confirm import: "Import X valid rows, skip Y with errors" primary button

After import: results toast + downloadable error report if any rows failed.

### Task 38.3 — Bulk document download

In File Center: when rows are selected, "Download Selected (ZIP)" button appears.

On click: shows a loading modal "Building your download… X files" with a spinner.
Calls `GET /api/files/bulk-download?ids=[...]`.
When response arrives, triggers browser download. Modal closes.

For large batches (> 20 files): shows an estimated size warning before download.

---

## PHASE 39 — System Health Panel

**Goal:** Give the owner visibility into the HERMES backend running on their VM.

### Task 39.1 — Backend: System API

`GET /api/system/status` → returns:
```json
{
  "agent_status": "running" | "degraded" | "stopped",
  "queue_depth": 3,
  "queue_processing": 1,
  "avg_processing_time_secs": 12,
  "disk_total_gb": 100,
  "disk_used_gb": 18.4,
  "last_backup": "2025-03-14T02:00:00Z",
  "uptime_seconds": 302400,
  "version": "1.0.0"
}
```

Agent status detection: check if PM2 process `hermes-agent` is in `online` state
via `pm2 jlist` subprocess call. Cache result for 10 seconds.

`GET /api/system/queue` → current queue items from `upload_queue` table
`POST /api/system/queue/:id/requeue` → resets status to 'queued'
`POST /api/system/queue/pause` → sets a `queue_paused` flag in a `system_config` table
`POST /api/system/queue/resume` → clears the flag

`GET /api/system/performance?hours=24` → returns hourly API response times and document processing rates

`GET /api/system/errors?limit=100&severity=` → reads last N lines from the HERMES log file
(`/home/hermes/data/logs/hermes.log`), parses log format, returns structured list

### Task 39.2 — System Health page (`src/pages/SystemHealthPage.tsx`)

**Status Cards (prominent, top row):**

Backend Status card: full colored background (green for running, amber for degraded, red for stopped).
Large text "RUNNING" / "DEGRADED" / "STOPPED". This is the first thing the eye goes to.

Other cards: Queue Depth, Avg Processing Time, Disk Usage (with progress bar), Uptime.

**Processing Queue Table:**
Live table (polls every 5 seconds).
Columns: Filename, Upload Time, Time in Queue, Status, Actions (Requeue / Cancel).
"Pause Queue" / "Resume Queue" toggle button at top.
"Reprocess All Failed" button — calls requeue on all ERROR items.

**Performance Graph:**
24-hour rolling chart (recharts `<ComposedChart>`).
Two lines: API Response Time (ms) on left Y-axis, Documents/Hour on right Y-axis.

**Error Log:**
Last 100 log entries in a monospace-font `<pre>` block with syntax-like coloring
(ERROR = `--danger`, WARNING = `--warning`, INFO = `--text-muted`).
Severity filter chips above. "Copy All" and "Download .log" buttons.

---

## PHASE 40 — Business Settings

### Task 40.1 — Backend: Settings API

`GET /api/settings` → all settings from `business` table
`PATCH /api/settings/profile` → update business name, address, GSTIN, etc.
`PATCH /api/settings/bank` → update bank/UPI details
`PATCH /api/settings/financial` → update fiscal year start, default payment terms, GST rates, invoice numbering
`PATCH /api/settings/notifications` → update notification preferences
`PATCH /api/settings/invoice-appearance` → template choice, accent color, footer text, column visibility

All write endpoints call `hermes.db.update_business()` with the relevant fields.

### Task 40.2 — Settings page (`src/pages/SettingsPage.tsx`)

Route: `/settings`.

**Layout:** Left vertical tab navigation (desktop, 200px), accordion sections (mobile).

Tab sections and their forms:

**Business Profile:**
- Business Name, Logo upload (`<input type="file">` → preview image above), Address, City, State, PIN, GSTIN, PAN, Contact Email, Phone, Industry type
- "Save Changes" primary button → `PATCH /api/settings/profile` → success toast

**Financial Configuration:**
- Financial year start month (`<Select>` April or January)
- Default payment terms (`<Select>` Net 15 / Net 30 / Net 45 / Custom)
- Default GST rates (add/remove rate chips: 0%, 5%, 12%, 18%, 28%)
- Invoice number format: prefix input + separator + starting number input +
  live preview: "INV-0001" (updates as user types)

**Invoice Appearance:**
- Template selector: 2–3 thumbnail cards (click to select, selected has accent border)
- Accent color picker (affects generated PDFs)
- Footer text textarea
- Column toggle switches: HSN Code | Per-unit price | Discount column

**Notifications:**
- Per-type section with in-app toggle and email toggle per notification type
- Email digest frequency `<Select>` (Real-time / Daily Summary / Weekly Summary)
- Overdue reminder cadence: checkbox array (Day 1 / Day 7 / Day 15 / Custom days input)

**Data Management:**
- "Export All Data" button → calls `/api/export/data` → polls for completion → downloads ZIP
- "Import Data" link → navigates to `/settings/import`
- Danger zone: "Clear Processing Queue" button with a confirmation modal
  (type "CLEAR" to confirm pattern)

---

## PHASE 41 — Onboarding Flow

**Goal:** First-time setup wizard for new business configuration.

### Task 41.1 — Backend: Onboarding API

`GET /api/onboarding/status` → returns `{completed: bool, steps_done: [...]}`.
Determined by whether the `business` table has required fields filled.

`POST /api/onboarding/complete-step` → body `{step: N}` → marks step as done.

### Task 41.2 — Onboarding detection

In `App.tsx`, on first render, call `/api/onboarding/status`. If `completed: false`,
redirect to `/onboarding` instead of the dashboard. The `<AppLayout>` sidebar is hidden
during onboarding.

### Task 41.3 — Onboarding Wizard page (`src/pages/OnboardingPage.tsx`)

Full-page centered layout (no sidebar, no top bar nav items — just the HERMES logo and the wizard).

**Step indicator:** 5 numbered circles connected by lines at the top.
Current step: filled `--accent` circle. Completed steps: `--success` circle with checkmark.
Future steps: empty `--border` circle.

**Step 1 — Welcome:**
Large heading: "Welcome to HERMES." Sub-text: "Let's set up your business in under 2 minutes."
Single large "Get Started →" primary button. Animated fade-in on mount.

**Step 2 — Business Profile:**
Form: Business Name (required), GSTIN (optional, with format hint), Industry type, Address.
"Continue →" primary button. "Skip for now" ghost link.
Validation before advancing: Business Name must not be empty.

**Step 3 — Financial Year:**
Financial year start (April / January toggle, large clickable cards, not a dropdown).
Default payment terms (3 large option cards: "Net 15 / Quick payment", "Net 30 / Standard",
"Net 45 / Extended").
Default GST rates (checkbox array).

**Step 4 — Invite Accountant (optional):**
"If someone else manages your books, add them here."
Single email input + role selector. "Send Invite" secondary button.
"Skip, I'll do this myself →" ghost link (large, prominent — this is the expected path for most).

**Step 5 — Ready:**
Checkmark animation (CSS, not a library). "HERMES is ready."
Two large equal-weight cards:
- "Upload your first document" → navigates to `/upload`
- "Chat with HERMES" → navigates to `/chat`

### Task 41.4 — Setup Checklist widget

A collapsible card at the top of the Dashboard (only shown until all items checked):

```
Getting started with HERMES [2/5 complete]   [×]

✓ Business profile set up
✓ Financial year configured
○ Upload your first document                  → Upload
○ Create your first invoice                   → Chat
○ Set up Chart of Accounts                    → Accounts
```

X button permanently dismisses it (sets `localStorage.setItem('checklist-dismissed', '1')`).
Each unchecked item is a clickable row that navigates to the relevant page.
The "2/5 complete" tally updates in real-time as items are completed.

---

## PHASE 42 — FastAPI Backend: All API Endpoints

**Goal:** Wire up every stub router from Phase 18 with real SQLite queries and filesystem operations.
This phase is done in parallel with the frontend phases but is formalized here.

### Task 42.1 — Write all database queries in `webapp/backend/database.py`

Group by router module. For each query:
- Write as a named function (e.g., `get_invoice_list(db_path, status, client_id, search, page, per_page)`)
- Return Python dicts (not SQLite Row objects — serialize in the function)
- Indian number formatting NOT applied here — the frontend does all formatting
- All dates returned as ISO strings (the frontend formats to DD Mon YYYY)
- Pagination: return `{items: [...], total: N, pages: N, page: N}`

### Task 42.2 — Wire all routers

Each router function:
- Gets `db_path` from `config.DB_PATH` (imported from `config.py`)
- Calls the appropriate database function
- Returns a Pydantic model or dict
- Error handling: `try/except` wrapping all DB calls, returns 500 with error message if DB fails

### Task 42.3 — File serving endpoints

For PDF and image downloads:
- Use FastAPI's `FileResponse` class
- Validate the requested path is within `CUSTOMER_DATA_DIR` before serving (path traversal prevention)
- Set `Content-Disposition: attachment; filename="..."` with the clean formatted filename
- Set correct `Content-Type` (application/pdf, image/jpeg, etc.)

### Task 42.4 — Report generation endpoints

For PDF reports (`POST /api/reports/:type/pdf`):
- Call the appropriate function from `hermes.pdf` module (the WeasyPrint PDF generator)
- Pass the DB path and date params
- Save PDF to `/home/hermes/data/reports/` with timestamped filename
- Return `{url: "/files/reports/filename.pdf", filename: "filename.pdf"}`

The `/files/` URL is served by nginx directly (not through Python). This is already configured
in Phase 24 of v5 in the nginx config.

---

## PHASE 43 — Frontend–Backend Integration

**Goal:** Wire every page to its API endpoints. Implement proper loading states, error handling,
and optimistic updates throughout.

### Task 43.1 — API client (`src/api/client.ts`)

Base fetch wrapper:
```typescript
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T>
```
- Prepends `/api` to all paths
- Sets `Content-Type: application/json` on POST/PATCH requests
- On non-2xx response: parses error body and throws an `ApiError` with `message` and `status`
- No auth headers needed (no auth in this system)

Typed API function modules:
- `src/api/dashboard.ts` — all dashboard API calls
- `src/api/invoices.ts`
- `src/api/contacts.ts`
- etc.

Each function returns a typed Promise. TypeScript interfaces match the FastAPI Pydantic models.

### Task 43.2 — Data fetching hooks (`src/hooks/`)

Create custom hooks for each major data entity using `useSWR` or a simple `useEffect`+`useState` pattern:

`useInvoices(filters)` — fetches paginated invoice list, returns `{data, loading, error, refetch}`
`useInvoiceDetail(id)` — fetches single invoice
`useDashboardKPIs()` — fetches KPI data, auto-refetches every 60 seconds
`useActivityFeed()` — fetches activity, auto-refetches every 30 seconds
`useAnomalyCount()` — fetches unreviewed count, auto-refetches every 60 seconds
`useNotificationCount()` — fetches unread count, auto-refetches every 30 seconds

### Task 43.3 — Optimistic updates

For actions that change state:
- Mark as Paid: update the invoice status in local state immediately, then send PATCH to API.
  If API fails, revert and show error toast.
- Acknowledge anomaly: update card status in local state immediately.
- Mark notification as read: update immediately in local state.

### Task 43.4 — Error handling

Global: if any API call returns a 5xx error, show an error toast.
Inline: if a specific form submission fails, show the error message inline below the form.
Network failure: if `fetch` throws (no internet / server down), show a persistent top banner:
"⚠ Cannot reach HERMES backend. Check that the service is running." with a "Retry" button.

---

## PHASE 44 — Responsive Polish & QA Pass

**Goal:** Audit every page at every breakpoint. Fix anything that doesn't work correctly on mobile.

### Task 44.1 — Mobile audit checklist

For every page in the app, verify on a 390px viewport (iPhone 14 size):
- [ ] No horizontal scroll on the page itself (only inside explicitly scrollable components like tables)
- [ ] All buttons have a minimum 44×44px touch target
- [ ] All text is readable (no font below 12px)
- [ ] Tables either scroll horizontally with sticky first column OR convert to card layout
- [ ] Modals are full-screen (not floating boxes on small screens)
- [ ] Dropdowns and selects use bottom sheets, not floating dropdowns
- [ ] All forms are usable with the iOS virtual keyboard visible (bottom half of screen)
- [ ] The floating chat widget doesn't overlap with bottom tab bar
- [ ] Safe area insets applied (notched devices: `env(safe-area-inset-bottom)`)

### Task 44.2 — Dark mode audit checklist

Toggle to dark mode. For every page:
- [ ] No hardcoded white or black colors visible (all use CSS token variables)
- [ ] Charts render correctly in dark mode (axis labels, grid lines, tooltips use tokens)
- [ ] The document viewer (white background for PDFs) is intentionally white even in dark mode
  with a note "Document shown in light mode for accurate print preview"
- [ ] Report viewer pages keep white background even in dark mode (same reason)
- [ ] Toast notifications render correctly in both themes
- [ ] Status badges readable in both themes

### Task 44.3 — Performance audit

Run Lighthouse on the production build (served from nginx). Targets:
- First Contentful Paint < 1.5s
- Time to Interactive < 2.5s
- Lighthouse Performance score > 85

If bundle size is too large:
- Lazy-load route components (`React.lazy` + `<Suspense>`)
- Lazy-load `react-pdf` and `recharts` (they're large)
- Ensure fonts are preloaded in `<head>` with `<link rel="preload">`

### Task 44.4 — Cross-browser check

Test in:
- Chrome (latest) — desktop + Android mobile
- Safari (latest) — desktop + iPhone
- Firefox (latest) — desktop

Known issues to watch for:
- Safari: `env(safe-area-inset-bottom)` required for iOS toolbar clearance
- Firefox: some CSS grid behaviors differ; verify layout on all critical pages
- Safari: `position: sticky` on table headers works but may need `-webkit-sticky`

---

## PHASE 45 — Full E2E Webapp Testing

**Goal:** Before any customer deployment, run all scenarios on your own GVM with a test dataset
loaded (run Phase 23 from v5 first to create realistic data).

### Task 45.1 — Pre-test: load test data

Run the following via Telegram to your test HERMES bot to create a realistic dataset:
- Create 10 clients (mix of customers and vendors)
- Create 20 invoices (mix of paid, unpaid, overdue, draft)
- Log 15 expenses (mix of categories, some with receipt photos)
- Record payments against 8 invoices (some full, some partial)
- Create 2 quotations (one converted to invoice, one rejected)
- Run P&L and GST reports to generate some report PDFs
- Process 5 uploaded vendor bills (mix of finalized and review-needed)

### Task 45.2 — Dashboard test scenarios

1. KPI cards show correct numbers (cross-verify each with a direct SQLite query)
2. Revenue vs Expenses chart shows correct data for last 12 months
3. Expense breakdown donut: percentages add to 100%
4. Activity feed shows latest 20 events in correct order
5. Overdue alert banner appears when overdue invoices exist; hidden when none
6. Theme toggle: switch dark→light→dark. All pages remain correct in both.

### Task 45.3 — Invoice test scenarios

7. Sales list: filter by "Overdue" → only overdue invoices shown
8. Sales list: filter by client name → correct subset
9. Sales list: date range filter → correct subset
10. Sales list: bulk select 3 invoices → "Download ZIP" → ZIP contains 3 PDFs
11. Invoice detail: all line items, GST, total shown correctly
12. Invoice detail: "Download PDF" → correct PDF opens in browser
13. Invoice detail: "Mark as Paid" → status updates, timeline updates, success toast
14. Purchase list: newly uploaded bill shows PROCESSING then REVIEW correctly
15. Bill review page: original document renders on left, fields pre-filled on right
16. Bill review page: correct OCR confidence indicators on fields
17. Bill review page: "Confirm & Finalize" → bill finalized, navigates to detail

### Task 45.4 — Chat interface test scenarios

18. Empty chat shows suggested prompts
19. Send "Create an invoice for Test Client for ₹10,000 + 18% GST" → agent responds + inline invoice card
20. Inline invoice card "Download PDF" → PDF downloads correctly
21. Send "Show me overdue invoices" → agent responds with list
22. Attach a document in chat + "Process this" → agent processes and responds
23. Floating chat widget opens on dashboard page, sends a message, closes
24. Chat history shows previous conversation

### Task 45.5 — File Center test scenarios

25. File center: all uploaded documents listed with correct metadata
26. Click a PDF → viewer drawer opens, document renders
27. Download from viewer drawer → correct file served
28. Bulk select 5 files → "Download ZIP" → ZIP arrives with 5 files

### Task 45.6 — Reports test scenarios

29. Run P&L report for current month → renders correctly with correct numbers
30. Download P&L as PDF → PDF opens, formatting correct
31. Run GST report → GSTR-1 data matches invoice records
32. Export GST portal JSON → JSON validates against GSTN schema
33. Custom report builder: build a "Customer × Total Amount" report, download as CSV
34. Saved report template: save a custom report, close page, reopen, template still there

### Task 45.7 — Remaining page scenarios

35. Contacts list: search by phone number → correct result
36. Contact detail: ledger tab → running balance correct
37. Contact statement PDF → downloads, shows correct data
38. Anomalies: "Acknowledge" an anomaly → status updates, nav badge decrements
39. Anomalies: "Dismiss" with reason → reason saved, anomaly greyed out
40. Audit trail: filter by action type "CREATE" → only create events shown
41. Audit trail: "Export to CSV" → CSV downloads with correct data
42. Notifications: bell shows unread count, click item marks as read, navigates to entity
43. Global search: type "Krishna" → shows matching invoices + contact
44. Global search: keyboard navigation (arrows + enter) works
45. System health: status card shows RUNNING, queue depth updates in real-time
46. Settings: update business name → save → refresh → new name shown
47. Settings: update GST rate → save → new invoice creates with updated default
48. Import contacts CSV: upload sample CSV → preview shows → import → contacts appear in list
49. Full data export → ZIP downloads with all CSVs + PDFs
50. Onboarding: factory-reset test DB → open webapp → wizard shows → complete all 5 steps → dashboard

---

## PHASE 46 — Production Build, Nginx & PM2 Integration

**Goal:** The Vite build output is served by nginx. The FastAPI backend runs under PM2.
Both are integrated into the existing install.sh and provision.sh scripts.

### Task 46.1 — Vite production build

`vite.config.ts` build settings:
- `build.outDir: '../static'` (outputs to `webapp/static/`)
- `build.sourcemap: false` (production)
- Enable Rollup chunking: separate vendor chunk for `recharts`, `react-pdf`

Build command: `cd webapp/frontend && npm run build`

The output in `webapp/static/` is a standard SPA: `index.html` + `assets/` directory.

### Task 46.2 — Nginx configuration update

Update the nginx config written by `provision.sh` (from Phase 24 of v5):

```nginx
server {
    listen 443 ssl;
    server_name $DOMAIN;

    # SSL config (managed by certbot)

    # React SPA — serve index.html for all non-API, non-file routes
    root /home/hermes/app/webapp/static;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API — proxy to FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # File downloads — direct filesystem serve (no Python in path)
    location /files/ {
        alias /home/hermes/data/;
        add_header Content-Disposition attachment;
        # Only allow access to known subdirectories
        location ~ \.(pdf|jpg|jpeg|png|zip|csv)$ {
            allow all;
        }
        deny all;
    }
}
```

The `try_files $uri $uri/ /index.html` directive is critical — it enables React Router's
client-side routing (navigating to `/invoices/sales/42` returns `index.html` so React can handle it).

### Task 46.3 — PM2 process for FastAPI

In `provision.sh`, start the FastAPI backend as a PM2 process:

```bash
pm2 start uvicorn \
  --name hermes-web \
  --interpreter /home/hermes/app/.venv/bin/uvicorn \
  -- webapp.backend.main:app \
  --host 127.0.0.1 \
  --port 5000 \
  --workers 1
```

`pm2 save` after starting both processes.

### Task 46.4 — Build step in install.sh

Add to `scripts/install.sh` (after Python deps are installed):

```bash
# Build webapp frontend
echo "Building webapp..."
cd /home/hermes/app/webapp/frontend
npm install --production=false
npm run build
echo "Webapp built successfully."
cd /home/hermes/app
```

This runs once at install time. On future updates (if you push code changes), the customer (or you)
can re-run just the build step: `cd /home/hermes/app/webapp/frontend && npm run build`.

### Task 46.5 — Verify production deployment

On your GVM (test environment):
1. Run `npm run build` in `webapp/frontend`
2. Confirm `webapp/static/index.html` exists and is populated
3. Restart nginx: `nginx -s reload`
4. Open `https://yourdomain.com` — React app loads without any console errors
5. Open `https://yourdomain.com/api/health` — FastAPI responds `{"status": "ok"}`
6. Navigate to `/invoices/sales` directly (hard refresh) — React app loads correctly (SPA routing via nginx)
7. Download a PDF from invoice detail — file served correctly via nginx `/files/` route

---

## PHASE 47 — Handover Script Update

**Goal:** Update `provision.sh` and `onboard-tui.js` to reflect the new webapp stack.
Update the handover walkthrough.

### Task 47.1 — Update provision.sh

Remove all references to the old Jinja2/auth webapp configuration.
Add:
- The new nginx config block from Phase 46.2
- PM2 start command for `hermes-web` (uvicorn)
- Environment variables: `DB_PATH`, `CUSTOMER_DATA_DIR`, `PORT=5000`, `BUSINESS_NAME`
- Write `.env` file to `webapp/backend/.env`

No `JWT_SECRET` needed (auth removed).

### Task 47.2 — Update onboard-tui.js

Remove the "Web dashboard password" prompt (no auth needed).
Add: confirmation step that shows the webapp URL the customer will use.

### Task 47.3 — Update handover walkthrough

Updated handover session (replaces Phase 24.6 in v5):

1. SSH into their VM
2. Run `curl -sSL https://raw.githubusercontent.com/YOURNAME/hermes/main/scripts/install.sh | bash`
   (This now includes npm install + npm run build for the webapp)
3. Run `certbot --nginx -d theirdomain.com`
4. Run `node /home/hermes/app/scripts/onboard-tui.js` — fill in business info
5. `pm2 list` — verify both `hermes-agent` and `hermes-web` show as `online`
6. Customer sends `/start` to their Telegram bot — first message test
7. Send a test message: "Ek invoice banao ABC ke liye ₹5000"
8. Open `https://theirdomain.com` in browser (no login — direct to dashboard)
9. Verify KPI cards show the invoice just created
10. Open the invoice, download the PDF, confirm it's correct
11. Open Chat tab in the webapp, send a message, verify agent responds
12. Add `https://theirdomain.com` to Home Screen on their phone (PWA)
13. Walk through 5 core flows: invoice, payment, expense (photo), outstanding query, report download
14. Hand them the 1-page guide (update it to mention webapp URL and Chat interface)

**You are done. Close SSH. Do not retain credentials.**

---

## APPENDIX A — New Dependencies

### Python (add to pyproject.toml)
```
openpyxl          # Excel export for reports (.xlsx generation)
```

### Node.js (webapp/frontend)
```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "react-router-dom": "^6",
    "@phosphor-icons/react": "^2",
    "recharts": "^2",
    "react-dropzone": "^14",
    "react-pdf": "^7",
    "date-fns": "^3",
    "clsx": "^2"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/react": "^18",
    "vite": "^5",
    "@vitejs/plugin-react": "^4",
    "tailwindcss": "^3",
    "postcss": "^8",
    "autoprefixer": "^10"
  }
}
```

### System packages (add to install.sh)
```bash
nodejs npm      # For webapp build step
```

---

## APPENDIX B — Decisions Log

| Decision | Rationale |
|---|---|
| React + Vite over Jinja2 | Chat interface, real-time queue, theme toggle require state management that vanilla JS makes unmaintainable at this feature count |
| No JWT auth | Webapp is accessed over SSH tunnel or local VM network. SSH is the auth layer. Adding web auth just adds friction for the business owner. |
| Self-hosted fonts | VM may not have internet access. CDN fonts would break rendering offline. |
| CSS custom properties for theming | Single data-theme attribute toggle changes all colors instantly with zero JS. More performant than class-based theming. |
| Nginx serves SPA, proxies API | Separation of concerns. Static files are served at native nginx speed. API calls go to FastAPI. File downloads never touch Python. |
| react-pdf for document viewer | Browser-native PDF viewing is inconsistent across devices. react-pdf (PDF.js wrapper) gives consistent rendering on all platforms. |
| SWR / polling over WebSockets | WebSockets require server infrastructure changes. Polling with short intervals is sufficient for this use case (local network, low latency). |
| IBM Plex Sans + Mono | Excellent numeral rendering (critical for financial data), distinctive but professional character, available in both variable and static weights. |

---

*HERMES Implementation Plan v5.5 — Webapp Design, Build & Integration.*
*Phases 1–17 complete (backend, agent, tools, Telegram, reports, PDF generation).*
*This document covers Phases 18–47: full React webapp from scaffold to customer handover.*
*One codebase. One install. Their VM. Their data.*
