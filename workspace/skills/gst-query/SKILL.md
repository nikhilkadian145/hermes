---
name: gst-query
description: Answer GST-related questions. Use when the user asks about GST rates, HSN/SAC codes, GSTIN validation, ITC eligibility, supply type, filing deadlines, or any Indian tax regulation question.
---

# GST Query

Quick GST lookups and tax knowledge for Indian businesses.

## What This Handles

- "What's the GST on laptops?" → gst_lookup("laptops")
- "Is GSTIN 27AABCT1234H1ZS valid?" → validate format + check state code
- "Can I claim ITC on food?" → Answer based on ITC rules
- "What forms do I file?" → GSTR-1, GSTR-3B, CMP-08 based on registration type
- "My client is in Karnataka, I'm in Maharashtra — inter or intra?" → Interstate

## GSTIN Validation Rules

Format: `NNAAAAAAAAAA NZN` (15 characters)
- Pos 1-2: State code (01-38)
- Pos 3-12: PAN number
- Pos 13: Entity number
- Pos 14: Z (default)
- Pos 15: Check digit

## ITC Rules (Quick Reference)

**Eligible:** Raw materials, capital goods, input services used for business
**Blocked (Section 17(5)):** Food/beverages, club memberships, personal vehicles, beauty/health, works contract for immovable property, goods lost/stolen/destroyed
**Partial:** Goods used for both business and personal → proportionate claim

## Filing Calendar

| Return  | Due Date                | Who Files            |
|---------|-------------------------|----------------------|
| GSTR-1  | 11th of next month      | Regular taxpayers    |
| GSTR-3B | 20th of next month      | Regular taxpayers    |
| CMP-08  | 18th of month after Qtr | Composition dealers  |
| GSTR-9  | 31st December           | Annual return        |

## Tools to Use

- `gst_lookup(item)` — HSN code + rate
- `get_gst_liability(from, to)` — Output tax vs ITC vs net payable
- `get_hsn_summary(from, to)` — HSN-wise supply summary
