from typing import Any

from fastapi import Body, FastAPI, Response
from fastapi.responses import JSONResponse

from app.repositories.sqlite_repository import SQLiteTaskRepository
from app.service import TaskService

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small SQLite-backed CRUD API for managing to-do tasks.",
)

repository = SQLiteTaskRepository()
repository.init_db()
service = TaskService(repository)


@app.get("/", summary="Show API information", tags=["System"])
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Check server health", tags=["System"])
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", tags=["Tasks"])
def list_tasks():
    return service.list_tasks()


@app.get("/tasks/{task_id}", summary="Get one task", tags=["Tasks"])
def get_task(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return task


@app.post("/tasks", summary="Create a task", status_code=201, tags=["Tasks"])
def create_task(payload: Any = Body(default=None)):
    task, error = service.create_task(payload)
    if error:
        return JSONResponse(status_code=400, content={"error": error})
    return JSONResponse(status_code=201, content=task)


@app.put("/tasks/{task_id}", summary="Update a task", tags=["Tasks"])
def update_task(task_id: int, payload: Any = Body(default=None)):
    task, error, exists = service.update_task(task_id, payload)
    if not exists:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    if error:
        return JSONResponse(status_code=400, content={"error": error})
    return task


@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204, tags=["Tasks"])
def delete_task(task_id: int):
    deleted = service.delete_task(task_id)
    if not deleted:
        return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})
    return Response(status_code=204)
