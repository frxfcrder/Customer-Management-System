import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
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


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


# Serve the frontend at "/" (registered last so API + /health win the match;
# same origin as the API => no CORS middleware needed). Prefers the Vite
# build output (frontend/dist) over the raw source folder.
_default_frontend = Path(__file__).resolve().parent.parent / "frontend"
FRONTEND_DIR = Path(
    os.getenv("FRONTEND_DIR")
    or ((_default_frontend / "dist") if (_default_frontend / "dist").is_dir() else _default_frontend)
)
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
