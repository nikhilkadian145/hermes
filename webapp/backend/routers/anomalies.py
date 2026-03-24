from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import hermes.db as db
from ..database import get_db_path

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("")
async def list_anomalies(
    status: str = "all",
    type: str = None,
    from_date: str = None,
    to_date: str = None,
    page: int = 1,
    per_page: int = 20,
    db_path: str = Depends(get_db_path)
):
    conn = db.get_conn(db_path)
    where = []
    params = []

    if status != "all":
        where.append("status = ?")
        params.append(status)
    if type:
        where.append("type = ?")
        params.append(type)
    if from_date:
        where.append("created_at >= ?")
        params.append(from_date)
    if to_date:
        where.append("created_at <= ?")
        params.append(to_date)

    where_clause = ("WHERE " + " AND ".join(where)) if where else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM anomalies {where_clause}", params
    ).fetchone()[0]

    offset = (page - 1) * per_page
    rows = conn.execute(
        f"SELECT * FROM anomalies {where_clause} "
        f"ORDER BY confidence DESC, created_at DESC "
        f"LIMIT ? OFFSET ?",
        params + [per_page, offset]
    ).fetchall()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "page": page
    }


@router.get("/count/unreviewed")
async def get_unreviewed_count(db_path: str = Depends(get_db_path)):
    count = db.get_conn(db_path).execute(
        "SELECT COUNT(*) FROM anomalies WHERE status = 'unreviewed'"
    ).fetchone()[0]
    return {"count": count}


class AnomalyActionRequest(BaseModel):
    note: str = None
    reason: str = None


@router.patch("/{anomaly_id}/acknowledge")
async def acknowledge(anomaly_id: int, db_path: str = Depends(get_db_path)):
    conn = db.get_conn(db_path)
    conn.execute(
        "UPDATE anomalies SET status = 'acknowledged', resolved_at = CURRENT_TIMESTAMP "
        "WHERE id = ?", (anomaly_id,)
    )
    conn.commit()
    return {"status": "acknowledged"}


@router.patch("/{anomaly_id}/escalate")
async def escalate(anomaly_id: int, req: AnomalyActionRequest, db_path: str = Depends(get_db_path)):
    conn = db.get_conn(db_path)
    conn.execute(
        "UPDATE anomalies SET status = 'escalated', escalation_note = ? WHERE id = ?",
        (req.note, anomaly_id)
    )
    conn.commit()
    return {"status": "escalated"}


@router.patch("/{anomaly_id}/dismiss")
async def dismiss(anomaly_id: int, req: AnomalyActionRequest, db_path: str = Depends(get_db_path)):
    conn = db.get_conn(db_path)
    conn.execute(
        "UPDATE anomalies SET status = 'dismissed', dismiss_reason = ?, "
        "resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
        (req.reason, anomaly_id)
    )
    conn.commit()
    return {"status": "dismissed"}

@router.post("/run-detection")
async def run_detection(db_path: str = Depends(get_db_path)):
    count = db.run_anomaly_detection(db_path)
    return {"new_anomalies": count}
