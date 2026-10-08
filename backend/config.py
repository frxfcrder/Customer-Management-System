import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")


class Config:

    DB_HOST = os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "127.0.0.1"))
    DB_PORT = os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres"))
    DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", ""))
    DB_NAME = os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "customer_management"))

    _explicit_url = os.getenv("DATABASE_URL")
    if _explicit_url:
        DATABASE_URL = _explicit_url
    else:
        DATABASE_URL = (
            f"postgresql+psycopg://{DB_USER}:{quote_plus(DB_PASSWORD)}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-long-random-secret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")


config = Config()
