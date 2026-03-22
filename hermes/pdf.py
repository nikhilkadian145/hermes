"""
HERMES — PDF Generator module
Uses Jinja2 and WeasyPrint to generate professional PDFs for Indian SMBs.
"""

from pathlib import Path
from typing import Any
import jinja2

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(_TEMPLATES_DIR))

# Common CSS shared across all templates for a neat, professional look.
_BASE_CSS_STRING = '''
    @page { size: A4; margin: 2cm; }
    body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 11pt; color: #333; line-height: 1.4; }
    h1, h2, h3 { margin-top: 0; color: #111; }
    .header { border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }
    .business-name { font-size: 24pt; font-weight: bold; color: #2c3e50; }
    .doc-title { font-size: 20pt; text-align: right; color: #7f8c8d; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 20px; }
    th { background-color: #f8f9fa; border-bottom: 2px solid #dee2e6; text-align: left; padding: 10px; font-weight: bold; }
    td { border-bottom: 1px solid #dee2e6; padding: 10px; }
    .text-right { text-align: right; }
    .text-center { text-align: center; }
    .totals { width: 50%; float: right; margin-top: 20px; }
    .totals table { margin-top: 0; }
    .totals th, .totals td { padding: 6px 10px; }
    .totals .grand-total th, .totals .grand-total td { font-size: 14pt; font-weight: bold; border-top: 2px solid #333; border-bottom: 2px solid #333; }
    .footer { position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 9pt; color: #7f8c8d; border-top: 1px solid #ccc; margin-top: 50px; padding-top: 10px; }
    .grid { display: flex; justify-content: space-between; margin-bottom: 20px;}
    .col-half { width: 48%; display: inline-block; vertical-align: top;}
    .watermark { position: absolute; top: 40%; left: 30%; font-size: 80pt; color: rgba(46, 204, 113, 0.2); transform: rotate(-45deg); z-index: -1; }
    .notes-box { margin-top: 30px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #3498db; }
'''

import tempfile
import subprocess
import sys
import os

def _render_pdf(template_name: str, context: dict[str, Any], output_path: str) -> str:
    """Render a Jinja2 template and convert it to PDF using Playwright."""
    template = _JINJA_ENV.get_template(template_name)
    html_content = template.render(**context)
    
    # Inject structural CSS
    css_tag = f"<style>{_BASE_CSS_STRING}</style>"
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", css_tag + "\n</head>")
    else:
        html_content = css_tag + "\n" + html_content
        
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_content)
        temp_html = f.name
        
    try:
        subprocess.run(
            [sys.executable, "-m", "hermes.pdf_worker", temp_html, output_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PDF generation failed: {e.stderr}")
    finally:
        try:
            os.remove(temp_html)
        except OSError:
            pass
            
    return output_path


def generate_invoice_pdf(invoice_dict: dict[str, Any], business_dict: dict[str, Any], output_path: str) -> str:
    context = {"invoice": invoice_dict, "business": business_dict, "client": invoice_dict.get("client", {})}
    return _render_pdf("invoice.html", context, output_path)


def generate_receipt_pdf(payment_dict: dict[str, Any], invoice_dict: dict[str, Any], business_dict: dict[str, Any], output_path: str) -> str:
    context = {"payment": payment_dict, "invoice": invoice_dict, "business": business_dict, "client": invoice_dict.get("client", {})}
    return _render_pdf("receipt.html", context, output_path)


def generate_quotation_pdf(quotation_dict: dict[str, Any], business_dict: dict[str, Any], output_path: str) -> str:
    context = {"quotation": quotation_dict, "business": business_dict, "client": quotation_dict.get("client", {})}
    return _render_pdf("quotation.html", context, output_path)


def generate_pl_report_pdf(pl_data: dict[str, Any], business_dict: dict[str, Any], from_date: str, to_date: str, output_path: str) -> str:
    context = {"report": pl_data, "business": business_dict, "from_date": from_date, "to_date": to_date}
    return _render_pdf("report_pl.html", context, output_path)


def generate_outstanding_report_pdf(outstanding_data: list[dict[str, Any]], business_dict: dict[str, Any], output_path: str) -> str:
    grand_total = sum(d["total_outstanding"] for d in outstanding_data)
    context = {"clients": outstanding_data, "business": business_dict, "grand_total": grand_total}
    return _render_pdf("report_outstanding.html", context, output_path)


def generate_expense_report_pdf(expense_data: list[dict[str, Any]], totals: dict[str, float], business_dict: dict[str, Any], from_date: str, to_date: str, output_path: str) -> str:
    total_amount = sum(totals.values())
    context = {"expenses": expense_data, "totals": totals, "total_amount": total_amount, "business": business_dict, "from_date": from_date, "to_date": to_date}
    return _render_pdf("report_expenses.html", context, output_path)


def generate_gst_report_pdf(gst_data: dict[str, Any], business_dict: dict[str, Any], from_date: str, to_date: str, output_path: str) -> str:
    context = {"report": gst_data, "business": business_dict, "from_date": from_date, "to_date": to_date}
    return _render_pdf("report_gst.html", context, output_path)
