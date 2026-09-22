from app.config import PROJECT_ROOT, normalized_database_url, use_postgres
from app.repositories.base import TaskRepository
from app.repositories.sqlite_repository import SQLiteTaskRepository


def create_repository() -> TaskRepository:
    if use_postgres():
        from app.repositories.postgres_repository import PostgresTaskRepository

        return PostgresTaskRepository(normalized_database_url())
    return SQLiteTaskRepository(PROJECT_ROOT / "tasks.db")
