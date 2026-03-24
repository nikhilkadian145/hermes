"""Settings API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os, sys, sqlite3, json

router = APIRouter(prefix="/api/settings", tags=["settings"])

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..database import get_db_path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import hermes.db as db


def _get_conn():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/health")
def health():
    return {"status": "ok", "router": "settings"}


# ---------------------------------------------------------------------------
# GET all settings
# ---------------------------------------------------------------------------
@router.get("")
def get_all_settings():
    db_path = get_db_path()
    business = db.get_business(db_path) or {}

    # Also fetch notification prefs and invoice appearance from system_config
    conn = _get_conn()
    cur = conn.cursor()
    extra = {}
    for key in ("notification_prefs", "invoice_appearance", "financial_config"):
        try:
            cur.execute("SELECT value FROM system_config WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                extra[key] = json.loads(row[0])
        except Exception:
            pass
    conn.close()
    return {**business, **extra}


@router.get("/business")
def get_business():
    db_path = get_db_path()
    return db.get_business(db_path) or {}


# ---------------------------------------------------------------------------
# PATCH endpoints
# ---------------------------------------------------------------------------
class ProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None


@router.patch("/profile")
def update_profile(body: ProfileUpdate):
    db_path = get_db_path()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        db.update_business(db_path, **updates)
    return db.get_business(db_path) or {}


class BankUpdate(BaseModel):
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    branch: Optional[str] = None
    upi_id: Optional[str] = None


@router.patch("/bank")
def update_bank(body: BankUpdate):
    db_path = get_db_path()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        db.update_business(db_path, **updates)
    return db.get_business(db_path) or {}


class FinancialUpdate(BaseModel):
    fy_start_month: Optional[str] = None
    default_payment_terms: Optional[str] = None
    default_gst_rates: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_separator: Optional[str] = None
    invoice_start_number: Optional[int] = None


@router.patch("/financial")
def update_financial(body: FinancialUpdate):
    conn = _get_conn()
    cur = conn.cursor()
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        cur.execute("SELECT value FROM system_config WHERE key = 'financial_config'")
        row = cur.fetchone()
        existing = json.loads(row[0]) if row else {}
        existing.update(data)
        cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('financial_config', ?)", (json.dumps(existing),))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return {"success": True, **data}


class NotificationUpdate(BaseModel):
    prefs: Optional[Dict[str, Any]] = None


@router.patch("/notifications")
def update_notifications(body: NotificationUpdate):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('notification_prefs', ?)", (json.dumps(body.prefs or {}),))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return {"success": True}


class InvoiceAppearanceUpdate(BaseModel):
    template: Optional[str] = None
    accent_color: Optional[str] = None
    footer_text: Optional[str] = None
    show_hsn: Optional[bool] = None
    show_unit_price: Optional[bool] = None
    show_discount: Optional[bool] = None


@router.patch("/invoice-appearance")
def update_invoice_appearance(body: InvoiceAppearanceUpdate):
    conn = _get_conn()
    cur = conn.cursor()
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        cur.execute("SELECT value FROM system_config WHERE key = 'invoice_appearance'")
        row = cur.fetchone()
        existing = json.loads(row[0]) if row else {}
        existing.update(data)
        cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('invoice_appearance', ?)", (json.dumps(existing),))
        conn.commit()
    except Exception:
        pass
    conn.close()
    return {"success": True, **data}


# Keep legacy GST endpoint
class GstSettingsUpdate(BaseModel):
    gstin: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    registration_type: Optional[str] = None
    composition_rate: Optional[float] = None
    gst_filing_frequency: Optional[str] = None
    pan: Optional[str] = None
    default_gst_rate: Optional[float] = None


@router.patch("/gst")
def update_gst_settings(body: GstSettingsUpdate):
    db_path = get_db_path()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        db.update_business(db_path, **updates)
    return db.get_business(db_path) or {}


# ---------------------------------------------------------------------------
# Agent config.json  (read / write)
# ---------------------------------------------------------------------------

def _find_config_path() -> str | None:
    """Locate config.json next to the database file (customer folder)."""
    db = get_db_path()
    candidate = os.path.join(os.path.dirname(os.path.abspath(db)), "config.json")
    if os.path.isfile(candidate):
        return candidate
    # Fallback: check env
    env = os.environ.get("CONFIG_PATH")
    if env and os.path.isfile(env):
        return env
    return None


class ConfigUpdate(BaseModel):
    """Writable subset of config.json — safe fields only."""
    provider_name: Optional[str] = None      # e.g. "openrouter", "anthropic"
    api_key: Optional[str] = None
    model: Optional[str] = None
    telegram_token: Optional[str] = None
    telegram_allow_from: Optional[list] = None
    cron_jobs: Optional[list] = None         # list of {name, cron, message}


@router.get("/config")
def get_config():
    """Return the current config.json contents (API key is masked)."""
    path = _find_config_path()
    if not path:
        return {"error": "config.json not found", "config_path": None}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Detect which provider is configured
    providers = raw.get("providers", {})
    provider_name = ""
    api_key_raw = ""
    for pname, pconf in providers.items():
        if isinstance(pconf, dict) and pconf.get("api_key"):
            provider_name = pname
            api_key_raw = pconf["api_key"]
            break

    # Mask key for display (show first 8 + last 4 chars)
    if len(api_key_raw) > 12:
        api_key_display = api_key_raw[:8] + "..." + api_key_raw[-4:]
    else:
        api_key_display = "***" if api_key_raw else ""

    model = raw.get("agents", {}).get("defaults", {}).get("model", "")
    telegram = raw.get("channels", {}).get("telegram", {})
    cron_jobs = raw.get("channels", {}).get("cron", raw.get("cron", []))

    return {
        "config_path": path,
        "provider_name": provider_name,
        "api_key_display": api_key_display,
        "model": model,
        "telegram_token_set": bool(telegram.get("token", "").replace("dummy_bot_token", "")),
        "telegram_allow_from": telegram.get("allowFrom", []),
        "cron_jobs": cron_jobs,
    }


@router.put("/config")
def update_config(body: ConfigUpdate):
    """Update config.json with the provided fields."""
    path = _find_config_path()
    if not path:
        return {"error": "config.json not found"}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    changed = False

    # Provider + API key
    if body.provider_name and body.api_key:
        raw.setdefault("providers", {})
        raw["providers"] = {body.provider_name: {"api_key": body.api_key}}
        changed = True
    elif body.api_key:
        # Update existing provider's key
        providers = raw.get("providers", {})
        for pname in providers:
            if isinstance(providers[pname], dict):
                providers[pname]["api_key"] = body.api_key
                changed = True
                break

    # Model
    if body.model:
        raw.setdefault("agents", {}).setdefault("defaults", {})["model"] = body.model
        changed = True

    # Telegram
    if body.telegram_token is not None:
        raw.setdefault("channels", {}).setdefault("telegram", {})["token"] = body.telegram_token
        changed = True
    if body.telegram_allow_from is not None:
        raw.setdefault("channels", {}).setdefault("telegram", {})["allowFrom"] = body.telegram_allow_from
        changed = True

    # Cron jobs
    if body.cron_jobs is not None:
        raw.setdefault("channels", {})["cron"] = body.cron_jobs
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)

    return {"success": True, "changed": changed}

