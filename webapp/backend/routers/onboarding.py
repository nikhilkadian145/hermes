"""Onboarding API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os, sys, sqlite3, json

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import hermes.db as db


def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/status")
def onboarding_status():
    """Check if onboarding has been completed."""
    db_path = get_db_path()
    business = db.get_business(db_path) or {}

    # Check system_config for onboarding state
    conn = _get_conn()
    cur = conn.cursor()
    steps_done = []
    completed = False
    try:
        cur.execute("SELECT value FROM system_config WHERE key = 'onboarding_steps_done'")
        row = cur.fetchone()
        if row:
            steps_done = json.loads(row[0])
    except Exception:
        pass
    try:
        cur.execute("SELECT value FROM system_config WHERE key = 'onboarding_completed'")
        row = cur.fetchone()
        if row:
            completed = row[0] == "true"
    except Exception:
        pass
    conn.close()

    # Also consider it completed if business_name exists
    if business.get("business_name") and len(steps_done) >= 4:
        completed = True

    return {
        "completed": completed,
        "steps_done": steps_done,
        "business": business,
    }


class StepComplete(BaseModel):
    step: int
    data: Optional[dict] = None


@router.post("/complete-step")
def complete_step(body: StepComplete):
    """Mark an onboarding step as done and optionally save data."""
    conn = _get_conn()
    cur = conn.cursor()

    # Get current steps
    steps_done = []
    try:
        cur.execute("SELECT value FROM system_config WHERE key = 'onboarding_steps_done'")
        row = cur.fetchone()
        if row:
            steps_done = json.loads(row[0])
    except Exception:
        pass

    if body.step not in steps_done:
        steps_done.append(body.step)

    cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('onboarding_steps_done', ?)", (json.dumps(steps_done),))

    # Save business data if provided
    if body.data:
        db_path = get_db_path()
        profile_fields = {k: v for k, v in body.data.items() if v is not None and v != ""}
        if profile_fields:
            db.update_business(db_path, **profile_fields)

        # Save financial config
        financial_keys = {"fy_start_month", "default_payment_terms", "default_gst_rates"}
        financial_data = {k: v for k, v in body.data.items() if k in financial_keys and v}
        if financial_data:
            try:
                cur.execute("SELECT value FROM system_config WHERE key = 'financial_config'")
                row = cur.fetchone()
                existing = json.loads(row[0]) if row else {}
                existing.update(financial_data)
                cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('financial_config', ?)", (json.dumps(existing),))
            except Exception:
                pass

    # Mark complete if step 5
    if body.step >= 5:
        cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('onboarding_completed', 'true')")

    conn.commit()
    conn.close()
    return {"success": True, "steps_done": steps_done}
