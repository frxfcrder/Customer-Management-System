from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import config
from models.base import Base

# Database Engine Setup
engine = create_engine(config.DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class SessionManager:
    def __init__(self, url: str | None = None):
        self.engine = create_engine(url or config.DATABASE_URL, echo=False)
        self._factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def get_session(self) -> Session:
        """Create database session for transaction"""
        return self._factory()

    def init_schema(self):
        """Init DB schema and tables (SQLAlchemy)"""
        Base.metadata.create_all(self.engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI DI: yield a session, always close it (never return None)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Global default manager (never None so callers don't hit NoneType errors)
db_session = SessionManager()


def init_migrations():
    """Create database migration schema"""
    Base.metadata.create_all(engine)

