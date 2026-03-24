from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    dashboard, invoices, purchases, contacts, payments,
    accounts, reports, anomalies, audit, notifications,
    search, files, settings, system, chat, upload, import_export, onboarding
)
import os
import sys

app = FastAPI(title="HERMES Backend")

@app.on_event("startup")
def startup_event():
    # Ensure database is initialized with the latest schema and HSN data
    # Adds project root to path, then imports hermes.db
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    try:
        import hermes.db as hermes_db
        from database import get_db_path
        db_path = get_db_path()
        print(f"Initializing database at {db_path}...")
        hermes_db.init_db(db_path)
        print("Database initialization complete.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

app.include_router(dashboard.router)
app.include_router(invoices.router)
app.include_router(purchases.router)
app.include_router(upload.router)
app.include_router(contacts.router)
app.include_router(payments.router)
app.include_router(accounts.router)
app.include_router(reports.router)
app.include_router(anomalies.router)
app.include_router(audit.router)
app.include_router(notifications.router)
app.include_router(search.router)
app.include_router(files.router)
app.include_router(settings.router)
app.include_router(system.router)
app.include_router(chat.router)
app.include_router(import_export.router)
app.include_router(onboarding.router)
