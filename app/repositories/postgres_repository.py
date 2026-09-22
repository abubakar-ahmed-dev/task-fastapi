import time

import psycopg
from psycopg.rows import dict_row


SEED_TASKS = [
    ("Learn HTTP basics", False),
    ("Build CRUD endpoints", False),
    ("Test with Swagger UI", False),
]


class PostgresTaskRepository:
    def __init__(self, database_url: str, retries: int = 10, retry_delay: float = 1.0):
        self.database_url = database_url
        self.retries = retries
        self.retry_delay = retry_delay

    def get_connection(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def init_db(self) -> None:
        last_error = None
        for _ in range(self.retries):
            try:
                with self.get_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            CREATE TABLE IF NOT EXISTS tasks (
                                id SERIAL PRIMARY KEY,
                                title TEXT NOT NULL,
                                done BOOLEAN NOT NULL DEFAULT FALSE
                            )
                            """
                        )
                        cursor.execute("SELECT COUNT(*) AS task_count FROM tasks")
                        task_count = cursor.fetchone()["task_count"]
                        if task_count == 0:
                            cursor.executemany(
                                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                                SEED_TASKS,
                            )
                    connection.commit()
                return
            except psycopg.OperationalError as error:
                last_error = error
                time.sleep(self.retry_delay)
        raise RuntimeError("Could not connect to Postgres") from last_error

    def list_tasks(self) -> list[dict]:
        raise NotImplementedError("Postgres reads are added in Stage 2")

    def get_task(self, task_id: int) -> dict | None:
        raise NotImplementedError("Postgres reads are added in Stage 2")

    def create_task(self, title: str) -> dict:
        raise NotImplementedError("Postgres writes are added in Stage 3")

    def update_task(self, task_id: int, title: str, done: bool) -> dict | None:
        raise NotImplementedError("Postgres writes are added in Stage 3")

    def delete_task(self, task_id: int) -> bool:
        raise NotImplementedError("Postgres writes are added in Stage 3")
