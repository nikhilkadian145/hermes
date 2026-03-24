"""
Phase 29 — Accounts & Mapping Rules API
"""

from fastapi import APIRouter, HTTPException, Body
import sqlite3

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

def _get_conn():
    from ..database import get_db_path
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------------------------------------------------------
# Chart of Accounts Endpoints
# -----------------------------------------------------------------------------

@router.get("")
def get_accounts():
    """Returns the full Chart of Accounts, including balances (simplified)."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE active = 1 ORDER BY code ASC")
    accounts = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    # Ideally, we would join with journal entries to compute real balances.
    # For Phase 29, we just return the accounts structure with a placeholder balance.
    for acc in accounts:
        acc["balance"] = 0.0
        
    return {"accounts": accounts}

@router.post("")
def create_account(
    code: str = Body(...),
    name: str = Body(...),
    type: str = Body(...),
    parent_id: int = Body(None)
):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO accounts (code, name, type, parent_id) VALUES (?, ?, ?, ?)",
            (code, name, type, parent_id)
        )
        conn.commit()
        return {"status": "success", "id": cur.lastrowid}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Account code already exists.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.patch("/{account_id}")
def update_account(account_id: int, name: str = Body(None), type: str = Body(None)):
    conn = _get_conn()
    cur = conn.cursor()
    
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if type is not None:
        updates.append("type = ?")
        params.append(type)
        
    if not updates:
        conn.close()
        return {"status": "success"}
        
    params.append(account_id)
    cur.execute(f"UPDATE accounts SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return {"status": "success"}

@router.delete("/{account_id}")
def deactivate_account(account_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    
    # We would check for transactions here, but for now just deactivate
    cur.execute("UPDATE accounts SET active = 0 WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# -----------------------------------------------------------------------------
# Mapping Rules Endpoints
# -----------------------------------------------------------------------------

@router.get("/mapping-rules")
def get_mapping_rules():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, a.code as account_code, a.name as account_name 
        FROM mapping_rules m
        JOIN accounts a ON a.id = m.map_to_account_id
        ORDER BY m.id DESC
    """)
    rules = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"rules": rules}

@router.post("/mapping-rules")
def create_mapping_rule(
    condition_type: str = Body(...),
    match_value: str = Body(...),
    map_to_account_id: int = Body(...)
):
    if condition_type not in ["exact_match", "contains", "starts_with"]:
        raise HTTPException(status_code=400, detail="Invalid condition_type")
        
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mapping_rules (condition_type, match_value, map_to_account_id) VALUES (?, ?, ?)",
        (condition_type, match_value, map_to_account_id)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"status": "success", "id": new_id}

@router.patch("/mapping-rules/{rule_id}")
def toggle_mapping_rule(rule_id: int, active: int = Body(...)):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE mapping_rules SET active = ? WHERE id = ?", (active, rule_id))
    conn.commit()
    conn.close()
    return {"status": "success"}

@router.delete("/mapping-rules/{rule_id}")
def delete_mapping_rule(rule_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM mapping_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
