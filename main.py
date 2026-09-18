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

tasks = [
    {"id": 1, "title": "Learn HTTP basics", "done": False},
    {"id": 2, "title": "Build CRUD endpoints", "done": False},
    {"id": 3, "title": "Test with Swagger UI", "done": False},
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


def find_task(task_id: int):
    return next((task for task in tasks if task["id"] == task_id), None)


def next_task_id():
    return max((task["id"] for task in tasks), default=0) + 1


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
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task", tags=["Tasks"])
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", summary="Create a task", status_code=201, tags=["Tasks"])
def create_task(payload: Any = Body(default=None)):
    error = validate_title(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    task = {"id": next_task_id(), "title": payload["title"].strip(), "done": False}
    tasks.append(task)
    return JSONResponse(status_code=201, content=task)


@app.put("/tasks/{task_id}", summary="Update a task", tags=["Tasks"])
def update_task(task_id: int, payload: Any = Body(default=None)):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    error = validate_update(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    if "title" in payload:
        task["title"] = payload["title"].strip()
    if "done" in payload:
        task["done"] = payload["done"]
    return task


@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204, tags=["Tasks"])
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})

    tasks.remove(task)
    return Response(status_code=204)
