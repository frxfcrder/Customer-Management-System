from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text

from services.db import get_db

# Main FastAPI Application & DI Config
app = FastAPI(title="Customer Management System")


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
