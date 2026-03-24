# HERMES Webapp — UI Design Guidelines
### Reference Document for AI Coding Agents
### Version 1.0 — Read this before writing any UI code

---

> **How to use this document:**
> This is the single source of truth for all visual and interaction decisions in the HERMES webapp.
> Before writing any component, page, or style — check this document first.
> Every color, spacing value, font size, and component behavior is specified here.
> Never use a value not defined in this document unless it is a derived calculation from these values.

---

## SECTION 1 — TECH STACK & CONSTRAINTS

```
Frontend:    React 18 + TypeScript + Vite
Styling:     Tailwind CSS 3 + CSS Custom Properties (CSS variables)
Icons:       Phosphor Icons (@phosphor-icons/react) — Regular weight default, Bold for active states
Charts:      Recharts
PDF Viewer:  react-pdf (PDF.js wrapper)
Routing:     React Router v6
Fonts:       IBM Plex Sans + IBM Plex Mono (self-hosted in /public/fonts/, NOT Google CDN)
```

**Hard rules for this stack:**
- NEVER use `styled-components`, `emotion`, or any CSS-in-JS library
- NEVER import fonts from `fonts.googleapis.com` — only from `/fonts/` local path
- NEVER hardcode a hex color anywhere. Every color must reference a CSS variable
- NEVER use `px` values for colors, spacing, or font sizes outside of the token definitions
- ALWAYS use Tailwind utility classes where possible; use inline `style={{ }}` only for dynamic values that can't be expressed as Tailwind classes

---

## SECTION 2 — THEMING SYSTEM

### How the theme works

The root `<html>` element carries a `data-theme` attribute:
- Light mode: no attribute (default) or `data-theme="light"`
- Dark mode: `data-theme="dark"`

All CSS variables are defined in `src/styles/tokens.css`.

Theme toggle code in `src/hooks/useTheme.ts`:
```typescript
const stored = localStorage.getItem('hermes-theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const initial = stored ?? (prefersDark ? 'dark' : 'light');
document.documentElement.setAttribute('data-theme', initial);
```

**Critical:** Every single color in every component must use a CSS variable. If you find yourself
writing `#FFFFFF` or `bg-white` or `text-gray-900`, stop and use the correct token instead.

---

## SECTION 3 — COMPLETE CSS TOKENS REFERENCE

Copy this exactly into `src/styles/tokens.css`.

```css
/* ─── LIGHT MODE (default) ─────────────────────────────────────── */
:root {

  /* Backgrounds */
  --bg-base:     #F7F6F3;   /* Page background — warm off-white */
  --bg-surface:  #FFFFFF;   /* Cards, panels, modals, dropdowns */
  --bg-subtle:   #EFEFEB;   /* Table alternating rows, input backgrounds */
  --bg-overlay:  #E8E7E2;   /* Hover states, secondary inputs */

  /* Borders */
  --border:        #DDD9D1; /* All borders and dividers */
  --border-strong: #B8B3A8; /* Focused inputs, active/hover borders */

  /* Text */
  --text-primary:   #1A1917; /* Headings, body text, primary labels */
  --text-secondary: #5C5852; /* Subheadings, metadata, descriptions */
  --text-muted:     #9C9890; /* Placeholder text, disabled labels, captions */
  --text-inverse:   #FFFFFF; /* Text on dark/colored backgrounds */

  /* Accent (primary interactive color) */
  --accent:        #1A56DB;
  --accent-hover:  #1544B8;
  --accent-subtle: #EBF0FD; /* Accent-tinted backgrounds for badges, highlights */

  /* Semantic: Success */
  --success:    #0D7E54;
  --success-bg: #E9F6F0;

  /* Semantic: Warning */
  --warning:    #B45309;
  --warning-bg: #FEF3C7;

  /* Semantic: Danger */
  --danger:     #C81E1E;
  --danger-bg:  #FEE2E2;

  /* Semantic: Neutral */
  --neutral:    #6B7280;
  --neutral-bg: #F3F4F6;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.07);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.14);

  /* Typography */
  --font-sans: 'IBM Plex Sans', -apple-system, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Courier New', monospace;

  /* Spacing (base unit: 4px) */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-12: 48px;
  --space-16: 64px;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Layout */
  --sidebar-width: 240px;
  --sidebar-collapsed: 60px;
  --topbar-height: 56px;
  --bottom-bar-height: 64px;
  --content-max-width: 1280px;
}

/* ─── DARK MODE ────────────────────────────────────────────────── */
[data-theme="dark"] {

  --bg-base:     #0F0F0E;
  --bg-surface:  #1A1917;
  --bg-subtle:   #242320;
  --bg-overlay:  #2C2B28;

  --border:        #333230;
  --border-strong: #55524D;

  --text-primary:   #F5F4F1;
  --text-secondary: #A8A49D;
  --text-muted:     #6B6760;
  --text-inverse:   #0F0F0E;

  --accent:        #4B7FE8;
  --accent-hover:  #3A6ED4;
  --accent-subtle: #1A2D4F;

  --success:    #34C987;
  --success-bg: #0D2E20;

  --warning:    #FBBF24;
  --warning-bg: #2D2000;

  --danger:     #F87171;
  --danger-bg:  #2D0A0A;

  --neutral:    #9CA3AF;
  --neutral-bg: #1F2937;

  --shadow-sm: 0 1px 3px rgba(0,0,0,0.30);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.40);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.55);
}
```

---

## SECTION 4 — TYPOGRAPHY

### Font loading

In `src/styles/globals.css`:
```css
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('/fonts/IBMPlexSans-Regular.woff2') format('woff2');
  font-weight: 400; font-style: normal;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('/fonts/IBMPlexSans-Medium.woff2') format('woff2');
  font-weight: 500; font-style: normal;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('/fonts/IBMPlexSans-SemiBold.woff2') format('woff2');
  font-weight: 600; font-style: normal;
}
@font-face {
  font-family: 'IBM Plex Sans';
  src: url('/fonts/IBMPlexSans-Bold.woff2') format('woff2');
  font-weight: 700; font-style: normal;
}
@font-face {
  font-family: 'IBM Plex Mono';
  src: url('/fonts/IBMPlexMono-Regular.woff2') format('woff2');
  font-weight: 400; font-style: normal;
}

body {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--bg-base);
  -webkit-font-smoothing: antialiased;
}
```

### Type scale

| Class name | font-size | font-weight | line-height | Use |
|---|---|---|---|---|
| `.t-display` | 28px | 700 | 1.2 | Page titles (desktop) |
| `.t-display-sm` | 22px | 700 | 1.2 | Page titles (mobile) |
| `.t-heading` | 20px | 600 | 1.3 | Card titles, section headings |
| `.t-subheading` | 16px | 600 | 1.4 | Sub-section labels |
| `.t-body` | 14px | 400 | 1.6 | Default body (already on `body`) |
| `.t-body-sm` | 13px | 400 | 1.5 | Table cells, metadata |
| `.t-label` | 12px | 500 | 1.4 | Column headers, form labels |
| `.t-caption` | 11px | 400 | 1.4 | Timestamps, fine print |
| `.t-mono` | 13px | 400 | 1.5 | Invoice #s, amounts, IDs, codes |

`.t-mono` also sets `font-family: var(--font-mono)`.

Add all these as utility classes in `src/styles/globals.css`:
```css
.t-display    { font-size: 28px; font-weight: 700; line-height: 1.2; }
.t-display-sm { font-size: 22px; font-weight: 700; line-height: 1.2; }
.t-heading    { font-size: 20px; font-weight: 600; line-height: 1.3; }
.t-subheading { font-size: 16px; font-weight: 600; line-height: 1.4; }
.t-body       { font-size: 14px; font-weight: 400; line-height: 1.6; }
.t-body-sm    { font-size: 13px; font-weight: 400; line-height: 1.5; }
.t-label      { font-size: 12px; font-weight: 500; line-height: 1.4; }
.t-caption    { font-size: 11px; font-weight: 400; line-height: 1.4; }
.t-mono       { font-size: 13px; font-weight: 400; line-height: 1.5; font-family: var(--font-mono); }
```

### Typography rules

- **Minimum font size anywhere in the UI: 11px** (`.t-caption`). Never smaller.
- **All currency amounts and invoice numbers must use `.t-mono`** or `font-family: var(--font-mono)`.
  This ensures digit alignment in columns without needing `font-variant-numeric: tabular-nums`.
- **All column headers in tables: `.t-label` + uppercase + `letter-spacing: 0.05em`**
- **Page titles: `.t-display` on ≥ 1024px, `.t-display-sm` on < 1024px**
  (use responsive Tailwind `md:` prefix: `className="t-display-sm md:t-display"`)

---

## SECTION 5 — RESPONSIVE BREAKPOINTS

| Name | Min width | Target devices |
|---|---|---|
| (default, mobile) | 0px | Smartphones — PRIMARY target |
| `sm:` | 640px | Large phones, small tablets |
| `md:` | 1024px | Laptops, tablets landscape — PRIMARY target |
| `lg:` | 1280px | Large desktop screens |

**Rule: Mobile-first.** Write base styles for mobile. Use `md:` prefix to override for desktop.

```tsx
/* Correct pattern */
<div className="flex flex-col md:flex-row">

/* Never do desktop-first like this */
<div className="flex flex-row sm:flex-col">
```

**Primary targets are phone and laptop equally.** Every layout must work perfectly at both.

---

## SECTION 6 — LAYOUT RULES

### Shell dimensions

```
Top bar:         height var(--topbar-height) = 56px desktop / 52px mobile
                 background var(--bg-surface)
                 border-bottom 1px var(--border)
                 position: fixed; top: 0; z-index: 100

Sidebar:         width var(--sidebar-width) = 240px expanded / 60px collapsed
                 position: fixed; left: 0; top: var(--topbar-height)
                 height: calc(100vh - var(--topbar-height))
                 background var(--bg-surface)
                 border-right 1px var(--border)
                 [mobile] position: fixed; transform: translateX(-100%) when closed

Content area:    margin-left var(--sidebar-width) [desktop only]
                 margin-top var(--topbar-height)
                 padding: var(--space-6) [desktop] / var(--space-4) [mobile]
                 max-width: var(--content-max-width); margin-right: auto; margin-left: auto
                 [mobile] margin-left: 0; padding-bottom: var(--bottom-bar-height)

Bottom tab bar:  [mobile only] height var(--bottom-bar-height) = 64px
                 position: fixed; bottom: 0; width: 100%
                 background var(--bg-surface)
                 border-top 1px var(--border)
                 padding-bottom: env(safe-area-inset-bottom)
```

### Content width

Max content width is 1280px. Content is centered with `margin: 0 auto`:

```tsx
<main style={{ maxWidth: 'var(--content-max-width)', margin: '0 auto' }}>
```

### Grid patterns

**KPI cards:** `grid grid-cols-2 md:grid-cols-3 gap-4`
**Report cards:** `grid grid-cols-1 md:grid-cols-3 gap-6`
**Contact cards:** `grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4`
**Settings form:** `max-w-2xl` (keep forms narrow for readability)

---

## SECTION 7 — COMPONENT REFERENCE

### 7.1 Buttons

**Props:** `variant`, `size`, `loading`, `disabled`, `icon`, `fullWidth`

**CSS for each variant:**

Primary:
```css
background: var(--accent);
color: var(--text-inverse);
border: none;
border-radius: var(--radius-md);
font-weight: 500;
transition: background 120ms ease;
```
```css
:hover { background: var(--accent-hover); }
:disabled { opacity: 0.45; cursor: not-allowed; }
```

Secondary:
```css
background: var(--bg-surface);
color: var(--text-primary);
border: 1px solid var(--border);
border-radius: var(--radius-md);
```
```css
:hover { background: var(--bg-overlay); border-color: var(--border-strong); }
```

Ghost:
```css
background: transparent;
color: var(--accent);
border: none;
```
```css
:hover { background: var(--accent-subtle); }
```

Danger (modifier — can be combined with primary/secondary/ghost):
- Replace `--accent` with `--danger`, `--accent-hover` with a darker danger, `--accent-subtle` with `--danger-bg`

**Heights:**
- `sm`: 28px, padding 0 10px, font-size 12px
- `md`: 36px, padding 0 14px, font-size 14px
- `lg`: 44px, padding 0 18px, font-size 14px (use lg for all mobile primary CTAs)

**Loading state:**
```tsx
{loading ? (
  <span className="spinner" style={{ width: 16, height: 16 }} />
) : null}
{children}
```
Button width must not change when loading. Pre-reserve space with `min-width` matching expected content width.

**Full-width on mobile:**
```tsx
<button className={`... ${fullWidth ? 'w-full' : ''}`}>
```

---

### 7.2 Status Badges

**All status badges:**
- `border-radius: var(--radius-full)`
- padding: 2px 8px
- `font-size: 11px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase`
- Display as `inline-flex; align-items: center; gap: 4px`

| `status` prop | Background token | Text token |
|---|---|---|
| `paid` | `--success-bg` | `--success` |
| `sent` | `--accent-subtle` | `--accent` |
| `draft` | `--neutral-bg` | `--neutral` |
| `overdue` | `--danger-bg` | `--danger` |
| `due-soon` | `--warning-bg` | `--warning` |
| `processing` | `--accent-subtle` | `--accent` |
| `review` | `--warning-bg` | `--warning` |
| `error` | `--danger-bg` | `--danger` |
| `void` | `--neutral-bg` | `--neutral` |
| `finalized` | `--success-bg` | `--success` |

`processing` badge gets a CSS pulse animation on its background:
```css
@keyframes badge-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
.badge-processing { animation: badge-pulse 1.4s ease infinite; }
```

---

### 7.3 Cards

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);  /* 10px */
  box-shadow: var(--shadow-sm);
  padding: var(--space-6);          /* 24px */
}

@media (max-width: 1024px) {
  .card { padding: var(--space-4); } /* 16px on mobile */
}

.card.clickable:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
  cursor: pointer;
}
```

---

### 7.4 Form Inputs

```css
.input {
  height: 36px;                    /* 44px on mobile */
  padding: 0 var(--space-3);
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 14px;
  width: 100%;
  transition: border-color 120ms ease, box-shadow 120ms ease;
}

.input:focus {
  outline: none;
  border-color: var(--border-strong);
  box-shadow: 0 0 0 3px var(--accent-subtle);
}

.input::placeholder { color: var(--text-muted); }

.input.error {
  border-color: var(--danger);
}

@media (max-width: 1024px) {
  .input { height: 44px; }  /* Larger touch target on mobile */
}
```

**Label pattern — ALWAYS use this structure:**
```tsx
<div className="flex flex-col gap-1">
  <label className="t-label" style={{ color: 'var(--text-secondary)' }}>
    Invoice Date
  </label>
  <input className="input" ... />
  {error && (
    <span className="t-caption" style={{ color: 'var(--danger)' }}>
      {error}
    </span>
  )}
</div>
```

**NEVER use placeholder as the label.** Labels are always above inputs.

---

### 7.5 Data Tables

**Table structure:**
```tsx
<div style={{ overflowX: 'auto' }}>
  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
    <thead>
      <tr style={{ background: 'var(--bg-subtle)' }}>
        <th className="t-label" style={{
          padding: '10px 16px',
          textAlign: 'left',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: 'var(--text-secondary)',
          borderBottom: '1px solid var(--border)',
          position: 'sticky',
          top: 0,
        }}>
          Column Header
        </th>
      </tr>
    </thead>
    <tbody>
      {data.map((row, i) => (
        <tr
          key={row.id}
          style={{
            background: i % 2 === 1 ? 'var(--bg-subtle)' : 'var(--bg-surface)',
            borderBottom: '1px solid var(--border)',
            height: 48,
            cursor: onRowClick ? 'pointer' : 'default',
            transition: 'background 80ms ease',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-overlay)')}
          onMouseLeave={e => (e.currentTarget.style.background = i % 2 === 1 ? 'var(--bg-subtle)' : 'var(--bg-surface)')}
          onClick={() => onRowClick?.(row)}
        >
          <td style={{ padding: '0 16px' }}>...</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
```

**Selected row:**
```css
tr.selected {
  background: var(--accent-subtle) !important;
  border-left: 2px solid var(--accent);
}
```

**Amount columns:** Always `text-align: right` + `font-family: var(--font-mono)`.

**Sticky first column on mobile:**
```css
tbody td:first-child,
thead th:first-child {
  position: sticky;
  left: 0;
  background: inherit;  /* inherits from row */
  z-index: 1;
}
```

**Empty state:**
```tsx
<tbody>
  <tr>
    <td colSpan={columns.length}>
      <div style={{
        padding: 'var(--space-16)',
        textAlign: 'center',
        color: 'var(--text-muted)',
      }}>
        <PhosphorIcon size={48} style={{ marginBottom: 'var(--space-4)', opacity: 0.4 }} />
        <p className="t-body" style={{ marginBottom: 'var(--space-4)' }}>No invoices found.</p>
        <Button variant="primary" size="sm">Create Invoice</Button>
      </div>
    </td>
  </tr>
</tbody>
```

**Loading skeleton rows:**
```tsx
{loading && Array.from({ length: 8 }).map((_, i) => (
  <tr key={i} style={{ height: 48, borderBottom: '1px solid var(--border)' }}>
    {columns.map((col, j) => (
      <td key={j} style={{ padding: '0 16px' }}>
        <div className="skeleton" style={{ height: 14, borderRadius: 4, width: '80%' }} />
      </td>
    ))}
  </tr>
))}
```

Skeleton CSS:
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-subtle) 25%,
    var(--bg-overlay) 50%,
    var(--bg-subtle) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

### 7.6 Toasts

Position: `fixed; bottom: 24px; right: 24px; z-index: 9999` on desktop.
On mobile: `fixed; bottom: calc(var(--bottom-bar-height) + 16px); left: 50%; transform: translateX(-50%)`.

Each toast:
```css
.toast {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-4);
  min-width: 280px;
  max-width: 360px;
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  animation: toast-in 200ms ease;
}

.toast.success { border-left: 3px solid var(--success); }
.toast.error   { border-left: 3px solid var(--danger); }
.toast.warning { border-left: 3px solid var(--warning); }
.toast.info    { border-left: 3px solid var(--accent); }

@keyframes toast-in {
  from { opacity: 0; transform: translateX(20px); }  /* desktop */
  to   { opacity: 1; transform: translateX(0); }
}
```

---

### 7.7 Modals

```css
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 200;
  display: flex; align-items: center; justify-content: center;
  animation: fade-in 150ms ease;
}

.modal {
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: var(--space-6);
  width: 600px; max-width: calc(100vw - 48px);
  max-height: calc(100vh - 96px);
  overflow-y: auto;
  animation: modal-in 150ms ease;
}

/* Mobile: full screen */
@media (max-width: 1024px) {
  .modal {
    width: 100vw;
    max-width: 100vw;
    max-height: 100vh;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    position: fixed; bottom: 0; left: 0;
    animation: sheet-in 250ms ease;
  }
}

@keyframes fade-in  { from { opacity: 0; } to { opacity: 1; } }
@keyframes modal-in { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
@keyframes sheet-in { from { transform: translateY(100%); } to { transform: translateY(0); } }
```

**Modal structure:**
```tsx
<div className="modal-backdrop" onClick={onClose}>
  <div className="modal" onClick={e => e.stopPropagation()}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-5)' }}>
      <h2 className="t-heading">{title}</h2>
      <button onClick={onClose}><X size={20} /></button>
    </div>
    {children}
    {footer && <div style={{ marginTop: 'var(--space-6)', borderTop: '1px solid var(--border)', paddingTop: 'var(--space-5)' }}>{footer}</div>}
  </div>
</div>
```

---

### 7.8 Dropdowns (custom)

On **desktop**: floating popover below the trigger.
On **mobile**: render as a bottom sheet instead.

Desktop popover:
```css
.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 180px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  z-index: 50;
  overflow: hidden;
  animation: dropdown-in 120ms ease;
}

@keyframes dropdown-in {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.dropdown-item {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: background 80ms ease;
}

.dropdown-item:hover { background: var(--bg-subtle); }
.dropdown-item.danger { color: var(--danger); }
.dropdown-item.danger:hover { background: var(--danger-bg); }
```

---

## SECTION 8 — NUMBER & DATE FORMATTING

**Always use these utilities. Never format numbers or dates inline.**

```typescript
// src/utils/format.ts

// Indian currency formatting: ₹1,23,456
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

// Abbreviated for chart axes and KPI cards: ₹1.2L, ₹4.5Cr
export function formatCurrencyShort(amount: number): string {
  if (amount >= 1_00_00_000) return `₹${(amount / 1_00_00_000).toFixed(1)}Cr`;
  if (amount >= 1_00_000)    return `₹${(amount / 1_00_000).toFixed(1)}L`;
  if (amount >= 1_000)       return `₹${(amount / 1_000).toFixed(0)}K`;
  return `₹${amount}`;
}

// Date: 14 Mar 2025
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
  });
}

// Relative: "2 min ago", "Yesterday", "14 Mar 2025" (beyond 7 days)
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1)    return 'Just now';
  if (diffMins < 60)   return `${diffMins} min ago`;
  if (diffHours < 24)  return `${diffHours}h ago`;
  if (diffDays === 1)  return `Yesterday ${date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;
  if (diffDays <= 7)   return `${diffDays} days ago`;
  return formatDate(dateString);
}
```

---

## SECTION 9 — RESPONSIVE PATTERNS

### When to swap UI patterns by breakpoint

| Desktop pattern | Mobile replacement |
|---|---|
| Floating dropdown | `<BottomSheet>` (slides up from bottom) |
| Multi-column layout | Single column stack |
| Data table | Horizontal scroll + sticky first column |
| Side-by-side panels | Stacked, document above form |
| Sidebar navigation | Off-canvas overlay + bottom tab bar |
| Modals (centered float) | Full-screen (slides up) |
| Hover tooltips | Not rendered (not accessible on touch) |
| Date picker (custom) | Native `<input type="date">` |

### Touch targets

**Every tappable element on mobile must have a minimum 44 × 44px hit area.**

If the visual element is smaller (e.g., a 16px icon), add invisible padding:
```css
.icon-button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Mobile-specific interactions

**Pull to refresh:** Add to all list pages:
```tsx
// Simple pull-to-refresh indicator at top of scrollable lists
// Triggers refetch when user pulls down past 80px threshold
```

**Long press for bulk select:** On `touchstart`, start a 500ms timer. If not cancelled (touch moved or ended), enter bulk-select mode. Cancel on scroll.

**Swipe to dismiss:** For toasts and bottom sheet handles.

### Safe area insets

Always add to bottom-fixed elements:
```css
.bottom-tab-bar {
  padding-bottom: env(safe-area-inset-bottom);
}
```

---

## SECTION 10 — CHARTS (Recharts)

### General rules

- All charts must use `<ResponsiveContainer width="100%" height={H}>` as the outer wrapper
- Never hardcode colors in chart configs — use CSS variables:
  ```tsx
  const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
  ```
- Re-read CSS variables whenever the theme changes (subscribe to `data-theme` attribute changes)
- Custom `<Tooltip>` content must use `--bg-surface` background and `--border` border

### Color assignments for chart lines/bars

```typescript
const CHART_COLORS = {
  revenue:   'var(--accent)',
  expenses:  'var(--danger)',
  paid:      'var(--success)',
  overdue:   'var(--danger)',
  pending:   'var(--warning)',
  draft:     'var(--neutral)',
};
```

For multi-series charts needing distinct colors (e.g., expense categories):
```typescript
const SERIES_COLORS = [
  'var(--accent)',
  'var(--success)',
  'var(--warning)',
  '#7C3AED', // purple
  '#0891B2', // cyan
  'var(--neutral)',
];
```

### Custom Tooltip template

```tsx
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-3)',
      boxShadow: 'var(--shadow-md)',
    }}>
      <p className="t-label" style={{ color: 'var(--text-muted)', marginBottom: 4 }}>{label}</p>
      {payload.map(entry => (
        <p key={entry.name} className="t-mono" style={{ color: entry.color }}>
          {entry.name}: {formatCurrency(entry.value)}
        </p>
      ))}
    </div>
  );
}
```

### Y-axis formatting

```tsx
<YAxis tickFormatter={(v) => formatCurrencyShort(v)} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
```

### X-axis formatting

```tsx
<XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
```

---

## SECTION 11 — CHAT INTERFACE SPECIFICS

### Message bubble CSS

User message:
```css
.msg-user {
  background: var(--accent);
  color: var(--text-inverse);
  border-radius: 16px 16px 4px 16px;
  padding: var(--space-3) var(--space-4);
  max-width: 75%;
  align-self: flex-end;
}
```

HERMES message:
```css
.msg-hermes {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 4px 16px 16px 16px;
  padding: var(--space-3) var(--space-4);
  max-width: 80%;
  align-self: flex-start;
}
```

Typing indicator:
```css
.typing-dot {
  width: 6px; height: 6px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: typing-bounce 1s infinite ease;
}
.typing-dot:nth-child(2) { animation-delay: 0.15s; }
.typing-dot:nth-child(3) { animation-delay: 0.30s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40%           { transform: scale(1.1); opacity: 1; }
}
```

### Inline document cards in chat

When HERMES creates an invoice (response metadata contains `invoice_id`):
```tsx
<div style={{
  background: 'var(--bg-subtle)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 'var(--space-4)',
  marginTop: 'var(--space-3)',
}}>
  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
    <span className="t-mono" style={{ color: 'var(--accent)' }}>INV-0042</span>
    <Badge status="sent" />
  </div>
  <p className="t-body-sm" style={{ color: 'var(--text-secondary)' }}>Krishna Textiles</p>
  <p className="t-mono" style={{ fontSize: 18, fontWeight: 600, margin: 'var(--space-1) 0' }}>
    {formatCurrency(100800)}
  </p>
  <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-3)' }}>
    <Button variant="secondary" size="sm">View Invoice</Button>
    <Button variant="ghost" size="sm">Download PDF</Button>
  </div>
</div>
```

---

## SECTION 12 — DOCUMENT VIEWER

### Critical: Report and document viewer backgrounds

**PDFs and generated reports must always have a white background**, even in dark mode.
This is intentional — they are meant for printing/sharing and must look correct.

```tsx
/* Wrap document viewer in a light-mode forced container */
<div data-theme="light" style={{ background: '#FFFFFF', color: '#1A1917' }}>
  <Document file={url}>
    <Page pageNumber={pageNum} />
  </Document>
</div>
```

Note in the UI: add a small badge above the viewer:
```tsx
<span className="t-caption" style={{ color: 'var(--text-muted)' }}>
  Shown in light mode for accurate print preview
</span>
```

---

## SECTION 13 — ICON USAGE

**Icon library:** `@phosphor-icons/react`

```tsx
import { Invoice, CurrencyDollar, Warning, ChartLine } from '@phosphor-icons/react';
```

**Standard sizes:**
- 14px: inline in text (e.g., status icon next to a label)
- 16px: inside buttons, in table rows
- 20px: standalone icon buttons (with 44px touch target wrapper)
- 24px: section headers, empty state icons (smaller)
- 48px: empty state hero icons

**Weight:**
- `Regular` (default): all inactive/neutral states
- `Bold`: active nav items, primary CTAs that include an icon
- `Fill`: active bottom tab icons

```tsx
// Regular (default weight)
<Invoice size={20} />

// Bold
<Invoice size={20} weight="bold" />

// Fill for active tab
<Invoice size={24} weight="fill" />
```

**Color:** Icons inherit `currentColor` by default. Control via parent's CSS `color` property.

**Never use icon-only buttons on mobile without a visible label.**
On desktop: icon-only buttons get a `<Tooltip>` with `delay={600}`.

---

## SECTION 14 — NAVIGATION ACTIVE STATES

### Sidebar active item

```css
.nav-item { /* all nav items */
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 8px var(--space-4);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
  transition: background 80ms ease, color 80ms ease;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  background: var(--bg-overlay);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent-subtle);
  color: var(--accent);
  border-left-color: var(--accent);
  font-weight: 500;
}
```

Use `useLocation()` from React Router to determine active state:
```tsx
const location = useLocation();
const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
```

### Bottom tab bar active state

```css
.tab-item.active .tab-label { color: var(--accent); }
.tab-item.active .tab-icon  { color: var(--accent); }
.tab-item:not(.active)      { color: var(--text-muted); }
```

---

## SECTION 15 — LOADING & EMPTY STATES

### Three-state pattern for every data-driven component

```tsx
function InvoiceList() {
  const { data, loading, error } = useInvoices(filters);

  if (loading) return <InvoiceListSkeleton />;

  if (error) return (
    <div style={{ textAlign: 'center', padding: 'var(--space-16)', color: 'var(--text-muted)' }}>
      <Warning size={48} style={{ marginBottom: 'var(--space-4)', opacity: 0.4 }} />
      <p className="t-body">Failed to load invoices.</p>
      <Button variant="secondary" size="sm" onClick={refetch} style={{ marginTop: 'var(--space-4)' }}>
        Try again
      </Button>
    </div>
  );

  if (data.items.length === 0) return <InvoiceListEmpty />;

  return <InvoiceTable data={data.items} />;
}
```

**Skeleton loaders** should always match the shape of the content they replace.
For list pages: use skeleton table rows.
For cards: use skeleton card shapes.
For charts: use a grey rectangle matching chart dimensions.

**Empty states** always include:
1. Icon (48px, `opacity: 0.4`)
2. Message explaining WHY it's empty
3. A primary CTA that helps the user fill it

---

## SECTION 16 — FOCUS & ACCESSIBILITY

### Focus ring (apply globally)

```css
/* In globals.css */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Remove outline for mouse users (only show for keyboard) */
:focus:not(:focus-visible) {
  outline: none;
}
```

### Aria labels

Every icon-only button MUST have `aria-label`:
```tsx
<button aria-label="Download invoice PDF">
  <DownloadSimple size={20} />
</button>
```

Every status badge should have descriptive text for screen readers:
```tsx
<span aria-label={`Status: ${status}`}>
  <Badge status={status} />
</span>
```

### Color is never the only differentiator

Every status shown with color must also have text. ✓ "OVERDUE" badge (text + color). ✗ Red dot alone.

### Form error accessibility

```tsx
<input
  id="invoice-date"
  aria-describedby={error ? "invoice-date-error" : undefined}
  aria-invalid={!!error}
/>
{error && (
  <span id="invoice-date-error" role="alert">
    {error}
  </span>
)}
```

---

## SECTION 17 — ANIMATION PRINCIPLES

**Less is more.** Use animations purposefully, not decoratively.

### When to animate

- Component mount/unmount: subtle fade + translate (max 200ms)
- Modal open: scale up + fade (150ms)
- Bottom sheet: slide up (250ms)
- Toast: slide in from right/bottom (200ms)
- Dropdown open: fade + translateY(-6px) to Y(0) (120ms)
- Status badge `processing`: continuous pulse (indefinite)
- Loading skeleton: shimmer sweep (1.5s loop)
- Typing indicator dots: bounce stagger (1s loop)

### When NOT to animate

- Data loading transitions (skeletons replace content — no animation)
- Tab switching within a page (immediate)
- Filter changes (immediate results, no fade)
- Navigation between pages (no page transitions — too slow on low-end phones)

### Easing

Use `ease` (cubic-bezier(0.25, 0.1, 0.25, 1)) for most transitions.
Use `ease-out` (cubic-bezier(0, 0, 0.2, 1)) for things entering the screen.
Use `ease-in` (cubic-bezier(0.4, 0, 1, 1)) for things leaving the screen.

---

## SECTION 18 — NEVER DO LIST

These are hard rules. Do not violate them.

1. **NEVER hardcode a color hex/rgb value** anywhere outside `tokens.css`. Use `var(--token)`.
2. **NEVER use `white` or `black`** in CSS. Use `var(--bg-surface)` and `var(--text-primary)`.
3. **NEVER use Google Fonts CDN.** All fonts are self-hosted in `/public/fonts/`.
4. **NEVER put a label only in a placeholder.** Always have a visible `<label>` element above inputs.
5. **NEVER use `display: none` to hide the sidebar on mobile.** Use `transform: translateX(-100%)` so CSS transitions work.
6. **NEVER write a `color:` CSS property with a hardcoded value** (except in the tokens file).
7. **NEVER render a Tooltip on mobile.** Tooltips are desktop-only.
8. **NEVER use browser-default `<select>` without custom styling.** Use the custom Select component.
9. **NEVER add `border-radius: 0` or `border: none` to override component defaults** — pass the correct variant prop instead.
10. **NEVER write inline styles for colors** when a Tailwind token class exists.
11. **NEVER assume the sidebar is visible on mobile** — always check breakpoint before using sidebar-dependent layout math.
12. **NEVER use `z-index` values above 1000** except for the toast container (9999) and modal backdrop (200).
13. **NEVER show a floating modal on screens below 1024px.** Use the bottom sheet pattern instead.
14. **NEVER use `font-size` below 11px** anywhere.

---

## SECTION 19 — QUICK REFERENCE: COMMON PATTERNS

### KPI Card pattern
```tsx
<Card>
  <p className="t-label" style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-2)' }}>
    Total Revenue
  </p>
  <p className="t-mono" style={{ fontSize: 24, fontWeight: 600, color: 'var(--text-primary)' }}>
    {formatCurrency(125000)}
  </p>
  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)', marginTop: 'var(--space-2)' }}>
    <TrendUp size={14} style={{ color: 'var(--success)' }} />
    <span className="t-caption" style={{ color: 'var(--success)' }}>+14% vs last month</span>
  </div>
</Card>
```

### Page header pattern
```tsx
<div style={{ marginBottom: 'var(--space-8)' }}>
  <Breadcrumbs items={['Dashboard', 'Invoices', 'Sales']} />
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'var(--space-2)' }}>
    <h1 className="t-display-sm md:t-display">Sales Invoices</h1>
    <div className="hidden md:flex" style={{ gap: 'var(--space-3)' }}>
      <Button variant="secondary" icon={<DownloadSimple />}>Export</Button>
      <Button variant="primary" icon={<Plus />}>New Invoice</Button>
    </div>
  </div>
  {/* Mobile: sticky bottom bar for actions */}
  <div className="md:hidden" style={{
    position: 'fixed', bottom: 'var(--bottom-bar-height)', left: 0, right: 0,
    padding: 'var(--space-3) var(--space-4)',
    background: 'var(--bg-surface)',
    borderTop: '1px solid var(--border)',
    display: 'flex', gap: 'var(--space-3)',
  }}>
    <Button variant="primary" size="lg" fullWidth>New Invoice</Button>
  </div>
</div>
```

### Section divider pattern
```tsx
<div style={{ borderTop: '1px solid var(--border)', margin: 'var(--space-6) 0' }} />
```

### Info callout pattern (for HERMES notes, tips)
```tsx
<div style={{
  background: 'var(--warning-bg)',
  border: '1px solid var(--warning)',
  borderRadius: 'var(--radius-md)',
  padding: 'var(--space-4)',
  display: 'flex', gap: 'var(--space-3)',
}}>
  <Warning size={16} style={{ color: 'var(--warning)', flexShrink: 0, marginTop: 2 }} />
  <p className="t-body-sm" style={{ color: 'var(--text-primary)' }}>
    {note}
  </p>
</div>
```

---

*HERMES UI Design Guidelines v1.0*
*This document is the reference for all visual decisions in the HERMES webapp.*
*Questions about a color, size, or interaction pattern? The answer is in this document.*
