import sys
import os
from playwright.sync_api import sync_playwright

def main(html_path, pdf_path):
    # Ensure paths are absolute for playwright file:// URIs
    html_abs = os.path.abspath(html_path)
    # Windows absolute paths need a leading slash for file URI, or just use pathlib
    from pathlib import Path
    uri = Path(html_abs).as_uri()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(uri, wait_until="networkidle")
        page.pdf(
            path=pdf_path, 
            format="A4", 
            margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"},
            print_background=True
        )
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Usage: python -m hermes.pdf_worker <html_path> <pdf_path>")
    main(sys.argv[1], sys.argv[2])
