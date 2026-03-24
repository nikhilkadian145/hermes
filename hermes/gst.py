"""
hermes/gst.py — All GST calculation logic for HERMES.

Imported by hermes/db.py and nanobot/agent/tools/hermes_tools.py.
Keeps tax logic in one place.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Supply type determination
# ---------------------------------------------------------------------------

def determine_supply_type(business_state_code: str,
                          client_state_code: str,
                          client_gstin: str | None) -> str:
    """
    Returns 'intrastate', 'interstate', or 'unregistered'.
    """
    if not client_gstin:
        return 'unregistered'
    client_state = client_gstin[:2] if client_gstin else client_state_code
    if client_state == business_state_code:
        return 'intrastate'
    return 'interstate'


# ---------------------------------------------------------------------------
# Per-item tax calculation
# ---------------------------------------------------------------------------

def calculate_item_tax(unit_price: float, quantity: float,
                        gst_rate: float, supply_type: str,
                        cess_rate: float = 0.0) -> dict:
    """
    Compute all tax amounts for a single line item.
    """
    taxable = round(unit_price * quantity, 2)
    total_gst = round(taxable * gst_rate / 100, 2)
    cess_amount = round(taxable * cess_rate / 100, 2)

    if supply_type == 'interstate':
        return {
            'taxable_amount': taxable,
            'cgst_rate': 0, 'cgst_amount': 0,
            'sgst_rate': 0, 'sgst_amount': 0,
            'igst_rate': gst_rate,
            'igst_amount': total_gst,
            'cess_amount': cess_amount,
            'total_tax': round(total_gst + cess_amount, 2),
            'line_total': round(taxable + total_gst + cess_amount, 2),
        }
    else:  # intrastate or unregistered
        half = round(total_gst / 2, 2)
        return {
            'taxable_amount': taxable,
            'cgst_rate': gst_rate / 2,
            'cgst_amount': half,
            'sgst_rate': gst_rate / 2,
            'sgst_amount': round(total_gst - half, 2),  # handles odd paise
            'igst_rate': 0, 'igst_amount': 0,
            'cess_amount': cess_amount,
            'total_tax': round(total_gst + cess_amount, 2),
            'line_total': round(taxable + total_gst + cess_amount, 2),
        }


# ---------------------------------------------------------------------------
# Invoice-level totals
# ---------------------------------------------------------------------------

def calculate_invoice_totals(items: list[dict]) -> dict:
    """
    Aggregate all item-level tax dicts into invoice totals.
    """
    grand_total = round(sum(i['line_total'] for i in items), 2)
    return {
        'subtotal':       round(sum(i['taxable_amount'] for i in items), 2),
        'total_cgst':     round(sum(i['cgst_amount'] for i in items), 2),
        'total_sgst':     round(sum(i['sgst_amount'] for i in items), 2),
        'total_igst':     round(sum(i['igst_amount'] for i in items), 2),
        'total_cess':     round(sum(i.get('cess_amount', 0) for i in items), 2),
        'total_tax':      round(sum(i['total_tax'] for i in items), 2),
        'grand_total':    grand_total,
        'total_in_words': amount_to_words_inr(grand_total),
    }


# ---------------------------------------------------------------------------
# Amount to words — Indian English (pure Python, no external libs)
# ---------------------------------------------------------------------------

_ONES = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
    'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
    'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen',
]
_TENS = [
    '', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
    'Sixty', 'Seventy', 'Eighty', 'Ninety',
]


def _two_digit(n: int) -> str:
    """Convert 0-99 to words."""
    if n < 20:
        return _ONES[n]
    t, o = divmod(n, 10)
    return (_TENS[t] + ' ' + _ONES[o]).strip()


def _chunk_to_words(n: int) -> str:
    """Convert 0-999 to words."""
    if n == 0:
        return ''
    h, remainder = divmod(n, 100)
    parts: list[str] = []
    if h:
        parts.append(_ONES[h] + ' Hundred')
    if remainder:
        parts.append(_two_digit(remainder))
    return ' '.join(parts)


def amount_to_words_inr(amount: float) -> str:
    """
    Converts e.g. 125430.50 →
      'Rupees One Lakh Twenty Five Thousand Four Hundred Thirty and Paise Fifty Only'

    Handles values from ₹0 to ₹99,99,99,999 (99 crore+).
    Uses Indian number system: ones, hundreds, thousands, lakhs, crores.
    """
    if amount < 0:
        return 'Minus ' + amount_to_words_inr(-amount)

    rupees = int(amount)
    paise = round((amount - rupees) * 100)

    if rupees == 0 and paise == 0:
        return 'Rupees Zero Only'

    # Decompose into Indian groups: crores, lakhs, thousands, hundreds, ones
    parts: list[str] = []

    crores, remainder = divmod(rupees, 10000000)
    if crores:
        parts.append(_chunk_to_words(crores) + ' Crore')

    lakhs, remainder = divmod(remainder, 100000)
    if lakhs:
        parts.append(_two_digit(lakhs) + ' Lakh')

    thousands, remainder = divmod(remainder, 1000)
    if thousands:
        parts.append(_two_digit(thousands) + ' Thousand')

    if remainder:
        parts.append(_chunk_to_words(remainder))

    result = 'Rupees ' + ' '.join(parts) if parts else ''

    if paise:
        paise_words = _two_digit(paise)
        if result:
            result += ' and Paise ' + paise_words
        else:
            result = 'Paise ' + paise_words

    result += ' Only'
    return result
