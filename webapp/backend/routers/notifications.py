from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from fastapi import Depends
import hermes.db as db
from ..database import get_db_path

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("")
async def list_notifications(
    tab: str = "all",
    page: int = 1,
    per_page: int = 30,
    db_path: str = Depends(get_db_path)
):
    conn = db.get_conn(db_path)
    where = []
    params = []

    if tab == "unread":
        where.append("is_read = 0")
    elif tab == "anomalies":
        where.append("type = 'anomaly'")
    elif tab == "system":
        where.append("type = 'system'")

    where_clause = ("WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) FROM notifications {where_clause}", params
    ).fetchone()[0]

    offset = (page - 1) * per_page
    rows = conn.execute(
        f"SELECT * FROM notifications {where_clause} "
        f"ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, offset]
    ).fetchall()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "page": page
    }

@router.get("/count/unread")
async def get_unread_count(db_path: str = Depends(get_db_path)):
    count = db.get_unread_notification_count(db_path)
    return {"count": count}

class MarkReadRequest(BaseModel):
    ids: List[int] = []
    all: bool = False

@router.post("/mark-read")
async def mark_read(req: MarkReadRequest, db_path: str = Depends(get_db_path)):
    conn = db.get_conn(db_path)
    if req.all:
        conn.execute("UPDATE notifications SET is_read = 1")
    elif req.ids:
        conn.execute(
            f"UPDATE notifications SET is_read = 1 "
            f"WHERE id IN ({','.join('?' * len(req.ids))})",
            req.ids
        )
    conn.commit()
    conn.close()
    return {"marked": True}
