import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

DB_PATH = Path(__file__).with_name("tasks.db")

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small SQLite-backed CRUD API for managing to-do tasks.",
)

SEED_TASKS = [
    ("Learn HTTP basics", 0),
    ("Build CRUD endpoints", 0),
    ("Test with Swagger UI", 0),
]


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
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


init_db()


def row_to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def find_task_in_db(task_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return row_to_task(row) if row else None


def validate_title(payload: Any):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return "title is required and must not be empty"
    return None


def validate_update(payload: Any):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    if "title" not in payload and "done" not in payload:
        return "Request body must include title or done"
    if "title" in payload and (not isinstance(payload["title"], str) or not payload["title"].strip()):
        return "title must not be empty"
    if "done" in payload and not isinstance(payload["done"], bool):
        return "done must be true or false"
    return None


@app.get("/", summary="Show API information", tags=["System"])
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check server health", tags=["System"])
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", tags=["Tasks"])
def list_tasks():
    with get_connection() as connection:
        rows = connection.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get one task", tags=["Tasks"])
def get_task(task_id: int):
    task = find_task_in_db(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", summary="Create a task", status_code=201, tags=["Tasks"])
def create_task(payload: Any = Body(default=None)):
    error = validate_title(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (payload["title"].strip(),),
        )
        connection.commit()
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return JSONResponse(status_code=201, content=row_to_task(row))


@app.put("/tasks/{task_id}", summary="Update a task", tags=["Tasks"])
def update_task(task_id: int, payload: Any = Body(default=None)):
    task = find_task_in_db(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    error = validate_update(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    title = payload.get("title", task["title"])
    done = payload.get("done", task["done"])
    with get_connection() as connection:
        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title.strip(), int(done), task_id),
        )
        connection.commit()
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return row_to_task(row)


@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204, tags=["Tasks"])
def delete_task(task_id: int):
    task = find_task_in_db(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
    return Response(status_code=204)
