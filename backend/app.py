from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from routes import router
from services.db import get_db, init_migrations

# Main FastAPI Application & DI Config
app = FastAPI(title="Customer Management System")
app.include_router(router)


@app.on_event("startup")
def init_db():
    """Initialize database schema on boot (non-fatal if DB is unreachable)."""
    try:
        init_migrations()
    except Exception:
        pass


@app.get("/")
def root():
    return {"message": "API is running", "version": "1.0.0"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
