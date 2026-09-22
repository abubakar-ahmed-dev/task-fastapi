import sqlite3
from pathlib import Path


SEED_TASKS = [
    ("Learn HTTP basics", 0),
    ("Build CRUD endpoints", 0),
    ("Test with Swagger UI", 0),
]


class SQLiteTaskRepository:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or Path(__file__).resolve().parents[2] / "tasks.db"

    def get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_db(self) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            task_count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            if task_count == 0:
                connection.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS)
            connection.commit()

    def list_tasks(self) -> list[dict]:
        with self.get_connection() as connection:
            rows = connection.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [self.row_to_task(row) for row in rows]

    def get_task(self, task_id: int) -> dict | None:
        with self.get_connection() as connection:
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return self.row_to_task(row) if row else None

    def create_task(self, title: str) -> dict:
        with self.get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, 0)",
                (title,),
            )
            connection.commit()
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return self.row_to_task(row)

    def update_task(self, task_id: int, title: str, done: bool) -> dict | None:
        with self.get_connection() as connection:
            connection.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (title, int(done), task_id),
            )
            connection.commit()
            row = connection.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return self.row_to_task(row) if row else None

    def delete_task(self, task_id: int) -> bool:
        with self.get_connection() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            connection.commit()
        return cursor.rowcount > 0

    @staticmethod
    def row_to_task(row) -> dict:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
