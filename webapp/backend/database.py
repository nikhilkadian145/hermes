"""
HERMES Database Query Functions.

Each function returns Python dicts (not SQLite Row objects).
All dates are returned as ISO strings.
Pagination returns: {items: [...], total: N, pages: N, page: N}
"""
import os
import math
import sqlite3
from contextlib import contextmanager
from typing import Optional


def get_db_path():
    return os.environ.get("DB_PATH", "hermes.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(get_db_path(), uri=True, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_write():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def execute_query_dict(query: str, params=()) -> list:
    with get_db() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def _paginate(query: str, count_query: str, params: tuple, page: int, per_page: int) -> dict:
    """Execute a paginated query and return standardized response."""
    with get_db() as conn:
        # Get total count
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()[0]
        pages = max(1, math.ceil(total / per_page))
        offset = (page - 1) * per_page

        # Get items
        cursor = conn.execute(f"{query} LIMIT ? OFFSET ?", params + (per_page, offset))
        items = [dict(row) for row in cursor.fetchall()]

    return {"items": items, "total": total, "pages": pages, "page": page}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def get_dashboard_kpis() -> dict:
    with get_db() as conn:
        cur = conn.cursor()
        kpis = {}
        try:
            # Revenue MTD
            cur.execute("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status IN ('paid', 'sent') AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
            kpis["revenue_mtd"] = cur.fetchone()[0]

            # Expenses MTD
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
            kpis["expenses_mtd"] = cur.fetchone()[0]

            kpis["net_profit_mtd"] = kpis["revenue_mtd"] - kpis["expenses_mtd"]

            # Outstanding receivables
            cur.execute("SELECT COALESCE(SUM(balance_due), 0), COUNT(*) FROM invoices WHERE balance_due > 0")
            row = cur.fetchone()
            kpis["outstanding_receivables"] = row[0]
            kpis["outstanding_count"] = row[1]

            # Overdue
            cur.execute("SELECT COALESCE(SUM(balance_due), 0), COUNT(*) FROM invoices WHERE balance_due > 0 AND due_date < date('now')")
            row = cur.fetchone()
            kpis["overdue_total"] = row[0]
            kpis["overdue_count"] = row[1]

            # GST liability estimate
            cur.execute("SELECT COALESCE(SUM(gst_amount), 0) FROM invoices WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')")
            kpis["gst_liability_est"] = cur.fetchone()[0]

            # Previous month comparison
            cur.execute("SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status IN ('paid', 'sent') AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now', '-1 month')")
            kpis["revenue_prev_month"] = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now', '-1 month')")
            kpis["expenses_prev_month"] = cur.fetchone()[0]

            kpis["outstanding_prev_week"] = kpis["outstanding_receivables"]
        except Exception:
            # Fallback to empty data if tables don't exist
            kpis = {
                "revenue_mtd": 0, "expenses_mtd": 0, "net_profit_mtd": 0,
                "outstanding_receivables": 0, "outstanding_count": 0,
                "overdue_total": 0, "overdue_count": 0,
                "gst_liability_est": 0,
                "revenue_prev_month": 0, "expenses_prev_month": 0,
                "outstanding_prev_week": 0,
            }
    return kpis


def get_revenue_expenses(months: int) -> list:
    try:
        return execute_query_dict("""
            SELECT strftime('%b', date) as month,
                   SUM(CASE WHEN type = 'revenue' THEN amount ELSE 0 END) as revenue,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expenses
            FROM (
                SELECT date, total as amount, 'revenue' as type FROM invoices WHERE status IN ('paid', 'sent')
                UNION ALL
                SELECT date, amount as amount, 'expense' as type FROM expenses
            )
            GROUP BY strftime('%Y-%m', date)
            ORDER BY date DESC
            LIMIT ?
        """, (months,))
    except Exception:
        # Fallback to empty chart
        return []


def get_expense_breakdown(month: str) -> list:
    try:
        return execute_query_dict("""
            SELECT COALESCE(category, 'Uncategorized') as category, SUM(amount) as total
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY category
            ORDER BY total DESC
        """, (month,))
    except Exception:
        return []


def get_invoice_status(months: int) -> list:
    try:
        return execute_query_dict("""
            SELECT strftime('%b', date) as month,
                SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid,
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as overdue,
                SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as draft
            FROM invoices
            GROUP BY strftime('%Y-%m', date)
            ORDER BY date DESC
            LIMIT ?
        """, (months,))
    except Exception:
        return []


def get_recent_activity(limit: int) -> list:
    try:
        results = execute_query_dict("""
            SELECT 'invoice_created' as type, 'Invoice ' || invoice_number || ' created' as description,
                   total as amount, created_at as timestamp, invoice_number as link_id, 'invoice' as link_type
            FROM invoices ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        if results:
            return results
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Invoices (Sales)
# ---------------------------------------------------------------------------
def get_invoice_list(status: Optional[str] = None, client_id: Optional[int] = None,
                     search: Optional[str] = None, page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if status:
        conditions.append("status = ?")
        params.append(status)
    if client_id:
        conditions.append("client_id = ?")
        params.append(client_id)
    if search:
        conditions.append("(invoice_number LIKE ? OR client_name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where = " AND ".join(conditions)
    query = f"SELECT * FROM invoices WHERE {where} ORDER BY date DESC"
    count_query = f"SELECT COUNT(*) FROM invoices WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


def get_invoice_detail(invoice_id: int) -> Optional[dict]:
    rows = execute_query_dict("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    return rows[0] if rows else None


def get_invoice_by_number(invoice_number: str) -> Optional[dict]:
    rows = execute_query_dict("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    return rows[0] if rows else None


def get_invoice_line_items(invoice_id: int) -> list:
    return execute_query_dict("SELECT * FROM invoice_line_items WHERE invoice_id = ?", (invoice_id,))


def get_purchase_bill_list(status: Optional[str] = None, vendor_id: Optional[int] = None,
                           search: Optional[str] = None, page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if status:
        # Expenses doesn't have a status in current schema, ignore or adjust if added
        pass
    if vendor_id:
        # vendor_id is just vendor string in schema right now. You can match string if needed.
        pass
    if search:
        conditions.append("(id LIKE ? OR vendor LIKE ? OR description LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    where = " AND ".join(conditions)
    query = f"SELECT *, id as bill_number, amount as total, amount as balance_due, vendor as vendor_name, 'paid' as status FROM expenses WHERE {where} ORDER BY date DESC"
    count_query = f"SELECT COUNT(*) FROM expenses WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


def get_purchase_bill_detail(bill_id: int) -> Optional[dict]:
    rows = execute_query_dict("SELECT *, id as bill_number, amount as total, amount as balance_due, vendor as vendor_name, 'paid' as status FROM expenses WHERE id = ?", (bill_id,))
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------
def get_contact_list(contact_type: Optional[str] = None, search: Optional[str] = None,
                     page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if contact_type:
        conditions.append("type = ?")
        params.append(contact_type)
    if search:
        conditions.append("(name LIKE ? OR gstin LIKE ? OR email LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    where = " AND ".join(conditions)
    query = f"SELECT * FROM contacts WHERE {where} ORDER BY name ASC"
    count_query = f"SELECT COUNT(*) FROM contacts WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


def get_contact_detail(contact_id: int) -> Optional[dict]:
    rows = execute_query_dict("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
def get_payment_list(payment_type: Optional[str] = None, page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if payment_type:
        conditions.append("type = ?")
        params.append(payment_type)

    where = " AND ".join(conditions)
    query = f"SELECT * FROM payments WHERE {where} ORDER BY date DESC"
    count_query = f"SELECT COUNT(*) FROM payments WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
def get_file_list(file_type: Optional[str] = None, search: Optional[str] = None,
                  page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if file_type:
        conditions.append("file_type = ?")
        params.append(file_type)
    if search:
        conditions.append("filename LIKE ?")
        params.append(f"%{search}%")

    where = " AND ".join(conditions)
    query = f"SELECT * FROM uploaded_files WHERE {where} ORDER BY uploaded_at DESC"
    count_query = f"SELECT COUNT(*) FROM uploaded_files WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


def get_file_detail(file_id: int) -> Optional[dict]:
    rows = execute_query_dict("SELECT * FROM uploaded_files WHERE id = ?", (file_id,))
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Accounts (Chart of Accounts)
# ---------------------------------------------------------------------------
def get_account_list(account_type: Optional[str] = None, search: Optional[str] = None) -> list:
    conditions = ["1=1"]
    params: list = []
    if account_type:
        conditions.append("type = ?")
        params.append(account_type)
    if search:
        conditions.append("(name LIKE ? OR code LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where = " AND ".join(conditions)
    return execute_query_dict(f"SELECT * FROM accounts WHERE {where} ORDER BY code ASC", tuple(params))


# ---------------------------------------------------------------------------
# Anomalies
# ---------------------------------------------------------------------------
def get_anomaly_list(status: Optional[str] = None, anomaly_type: Optional[str] = None,
                     page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if status:
        conditions.append("status = ?")
        params.append(status)
    if anomaly_type:
        conditions.append("type = ?")
        params.append(anomaly_type)

    where = " AND ".join(conditions)
    query = f"SELECT * FROM anomalies WHERE {where} ORDER BY created_at DESC"
    count_query = f"SELECT COUNT(*) FROM anomalies WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------
def get_audit_list(user: Optional[str] = None, action_type: Optional[str] = None,
                   from_date: Optional[str] = None, to_date: Optional[str] = None,
                   page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if user:
        conditions.append("user = ?")
        params.append(user)
    if action_type:
        for at in action_type.split(","):
            conditions.append("action_type = ?")
            params.append(at.strip())
    if from_date:
        conditions.append("timestamp >= ?")
        params.append(from_date)
    if to_date:
        conditions.append("timestamp <= ?")
        params.append(to_date)

    where = " AND ".join(conditions)
    query = f"SELECT * FROM audit_log WHERE {where} ORDER BY timestamp DESC"
    count_query = f"SELECT COUNT(*) FROM audit_log WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def get_notification_list(tab: str = "all", page: int = 1, per_page: int = 20) -> dict:
    conditions = ["1=1"]
    params: list = []
    if tab == "unread":
        conditions.append("read = 0")
    elif tab in ("anomalies", "system"):
        conditions.append("type = ?")
        params.append(tab)

    where = " AND ".join(conditions)
    query = f"SELECT * FROM notifications WHERE {where} ORDER BY created_at DESC"
    count_query = f"SELECT COUNT(*) FROM notifications WHERE {where}"
    return _paginate(query, count_query, tuple(params), page, per_page)


def get_unread_count() -> int:
    rows = execute_query_dict("SELECT COUNT(*) as count FROM notifications WHERE read = 0")
    return rows[0]["count"] if rows else 0
