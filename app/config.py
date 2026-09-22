import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")


def normalized_database_url() -> str:
    if DATABASE_URL.startswith("postgres://"):
        return "postgresql://" + DATABASE_URL.removeprefix("postgres://")
    return DATABASE_URL


def use_postgres() -> bool:
    return DATABASE_URL.startswith(("postgres://", "postgresql://"))
