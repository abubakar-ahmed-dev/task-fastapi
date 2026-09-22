from typing import Any

from app.repositories.base import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def list_tasks(self) -> list[dict]:
        return self.repository.list_tasks()

    def get_task(self, task_id: int) -> dict | None:
        return self.repository.get_task(task_id)

    def create_task(self, payload: Any) -> tuple[dict | None, str | None]:
        error = validate_title(payload)
        if error:
            return None, error
        return self.repository.create_task(payload["title"].strip()), None

    def update_task(self, task_id: int, payload: Any) -> tuple[dict | None, str | None, bool]:
        task = self.repository.get_task(task_id)
        if task is None:
            return None, None, False

        error = validate_update(payload)
        if error:
            return None, error, True

        title = payload.get("title", task["title"])
        done = payload.get("done", task["done"])
        return self.repository.update_task(task_id, title.strip(), done), None, True

    def delete_task(self, task_id: int) -> bool:
        return self.repository.delete_task(task_id)


def validate_title(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return "title is required and must not be empty"
    return None


def validate_update(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    if "title" not in payload and "done" not in payload:
        return "Request body must include title or done"
    if "title" in payload and (not isinstance(payload["title"], str) or not payload["title"].strip()):
        return "title must not be empty"
    if "done" in payload and not isinstance(payload["done"], bool):
        return "done must be true or false"
    return None
