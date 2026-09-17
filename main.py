from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Learn HTTP basics", "done": False},
    {"id": 2, "title": "Build CRUD endpoints", "done": False},
    {"id": 3, "title": "Test with Swagger UI", "done": False},
]


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


@app.get("/", summary="Show API information")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check server health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", summary="Create a task", status_code=201)
def create_task(payload: Any = Body(default=None)):
    error = validate_title(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})

    task = {"id": next_task_id(), "title": payload["title"].strip(), "done": False}
    tasks.append(task)
    return JSONResponse(status_code=201, content=task)
