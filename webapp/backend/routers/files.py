"""
Phase 26 — File Center API
Unified repository for every file HERMES has touched.
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import os
import sys
import io
import zipfile
import math

# Ensure hermes package is importable
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

router = APIRouter(prefix="/api/files", tags=["files"])


def _get_db():
    from ..database import get_db_path
    return get_db_path()


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@router.get("")
def list_files(
    type: Optional[str] = Query(None, description="uploaded|generated|reports|exports"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    """
    Aggregate files from invoices, expenses, upload_queue, and quotations
    into a unified listing.
    """
    import sqlite3
    db_path = _get_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    files = []

    # 1) Generated: Sales Invoice PDFs
    if type is None or type == "generated":
        cur.execute("""
            SELECT i.id, i.invoice_number, i.pdf_path, i.created_at,
                   c.name as client_name
            FROM invoices i
            LEFT JOIN clients c ON c.id = i.client_id
            WHERE i.pdf_path != ''
        """)
        for row in cur.fetchall():
            path = row["pdf_path"]
            size = 0
            if path and os.path.isfile(path):
                size = os.path.getsize(path)
            files.append({
                "id": f"inv-{row['id']}",
                "filename": os.path.basename(path) if path else f"INV-{row['invoice_number']}.pdf",
                "display_name": f"Invoice {row['invoice_number']} — {row['client_name'] or 'Unknown'}",
                "type": "generated",
                "sub_type": "Sales Invoices",
                "linked_to": "Invoice",
                "linked_id": row["id"],
                "created_at": row["created_at"],
                "file_size": size,
                "file_size_display": _human_size(size),
                "path": path or "",
                "extension": "pdf",
            })

    # 2) Generated: Quotation PDFs
    if type is None or type == "generated":
        cur.execute("""
            SELECT q.id, q.quotation_number, q.pdf_path, q.created_at,
                   c.name as client_name
            FROM quotations q
            LEFT JOIN clients c ON c.id = q.client_id
            WHERE q.pdf_path != ''
        """)
        for row in cur.fetchall():
            path = row["pdf_path"]
            size = 0
            if path and os.path.isfile(path):
                size = os.path.getsize(path)
            files.append({
                "id": f"quot-{row['id']}",
                "filename": os.path.basename(path) if path else f"QUOT-{row['quotation_number']}.pdf",
                "display_name": f"Quotation {row['quotation_number']} — {row['client_name'] or 'Unknown'}",
                "type": "generated",
                "sub_type": "Quotations",
                "linked_to": "Quotation",
                "linked_id": row["id"],
                "created_at": row["created_at"],
                "file_size": size,
                "file_size_display": _human_size(size),
                "path": path or "",
                "extension": "pdf",
            })

    # 3) Uploaded: Expense receipts
    if type is None or type == "uploaded":
        cur.execute("""
            SELECT id, description, vendor, receipt_path, created_at
            FROM expenses
            WHERE receipt_path != ''
        """)
        for row in cur.fetchall():
            path = row["receipt_path"]
            size = 0
            if path and os.path.isfile(path):
                size = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lstrip('.').lower() if path else ''
            files.append({
                "id": f"exp-{row['id']}",
                "filename": os.path.basename(path) if path else "receipt",
                "display_name": f"Receipt — {row['vendor'] or row['description'] or 'Expense'}",
                "type": "uploaded",
                "sub_type": "Vendor Invoices",
                "linked_to": "Expense",
                "linked_id": row["id"],
                "created_at": row["created_at"],
                "file_size": size,
                "file_size_display": _human_size(size),
                "path": path or "",
                "extension": ext or "pdf",
            })

    # 4) Uploaded: Upload queue items
    if type is None or type == "uploaded":
        cur.execute("""
            SELECT id, filename, file_size, status, created_at
            FROM upload_queue
        """)
        for row in cur.fetchall():
            # Check if uploaded files are stored in a known directory
            uploads_dir = os.path.join(root_dir, "uploads")
            path = os.path.join(uploads_dir, row["filename"]) if row["filename"] else ""
            ext = os.path.splitext(row["filename"])[1].lstrip('.').lower() if row["filename"] else ''
            files.append({
                "id": f"upl-{row['id']}",
                "filename": row["filename"],
                "display_name": f"Upload — {row['filename']}",
                "type": "uploaded",
                "sub_type": "Others",
                "linked_to": "Upload Queue",
                "linked_id": row["id"],
                "created_at": row["created_at"],
                "file_size": row["file_size"],
                "file_size_display": _human_size(row["file_size"]),
                "path": path,
                "extension": ext or "pdf",
            })

    conn.close()

    # Apply search filter
    if search:
        q = search.lower()
        files = [f for f in files if q in f["filename"].lower() or q in f["display_name"].lower()]

    # Sort by date descending
    files.sort(key=lambda f: f["created_at"] or "", reverse=True)

    total = len(files)
    total_pages = max(1, math.ceil(total / per_page))
    start = (page - 1) * per_page
    page_files = files[start : start + per_page]

    return {
        "files": page_files,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@router.get("/download/{file_id}")
def download_file(file_id: str):
    """Stream a single file by its composite ID."""
    path = _resolve_file_path(file_id)
    if not path or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    filename = os.path.basename(path)
    return FileResponse(
        path,
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/preview/{file_id}")
def preview_file(file_id: str):
    """Stream a file for inline preview (images / PDFs)."""
    path = _resolve_file_path(file_id)
    if not path or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    ext = os.path.splitext(path)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".tiff": "image/tiff",
    }
    media = media_types.get(ext, "application/octet-stream")
    return FileResponse(path, media_type=media)


@router.post("/bulk-download")
def bulk_download(file_ids: list[str]):
    """Create a ZIP of selected files and stream it."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fid in file_ids:
            try:
                path = _resolve_file_path(fid)
                if path and os.path.isfile(path):
                    zf.write(path, os.path.basename(path))
            except Exception:
                continue

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="hermes_documents.zip"'},
    )


def _resolve_file_path(file_id: str) -> Optional[str]:
    """Resolve a composite file ID to an absolute file path with path traversal prevention."""
    import sqlite3
    db_path = _get_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    path = None
    parts = file_id.split("-", 1)
    if len(parts) != 2:
        conn.close()
        return None

    prefix, record_id = parts

    if prefix == "inv":
        cur.execute("SELECT pdf_path FROM invoices WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if row:
            path = row["pdf_path"]
    elif prefix == "quot":
        cur.execute("SELECT pdf_path FROM quotations WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if row:
            path = row["pdf_path"]
    elif prefix == "exp":
        cur.execute("SELECT receipt_path FROM expenses WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if row:
            path = row["receipt_path"]
    elif prefix == "upl":
        cur.execute("SELECT filename FROM upload_queue WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if row and row["filename"]:
            uploads_dir = os.path.join(root_dir, "uploads")
            path = os.path.join(uploads_dir, row["filename"])

    conn.close()

    # Path traversal prevention: ensure resolved path is within allowed directories
    if path:
        path = _validate_path(path)
    return path


# Allowed base directories for file serving
_ALLOWED_DIRS = [
    os.path.realpath(root_dir),  # project root
    os.path.realpath(os.path.expanduser("~/data")),  # user data dir
    os.path.realpath(os.path.expanduser("~/hermes")),
]


def _validate_path(path: str) -> Optional[str]:
    """Validate a file path is within allowed directories (prevents path traversal)."""
    try:
        real_path = os.path.realpath(path)
        for allowed in _ALLOWED_DIRS:
            if real_path.startswith(allowed + os.sep) or real_path == allowed:
                return real_path
        return None
    except (ValueError, OSError):
        return None


@router.get("/serve")
def serve_file(path: str = Query(..., description="Absolute path to file")):
    """Serve a file by absolute path with path traversal prevention."""
    validated = _validate_path(path)
    if not validated or not os.path.isfile(validated):
        raise HTTPException(status_code=404, detail="File not found or access denied")

    filename = os.path.basename(validated)
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".zip": "application/zip",
    }
    media = media_types.get(ext, "application/octet-stream")
    return FileResponse(
        validated,
        filename=filename,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

