from fastapi import APIRouter

router = APIRouter(prefix="/api/bills", tags=["bills"])

@router.get("/health")
def health():
    return {"status": "ok", "router": "bills"}
