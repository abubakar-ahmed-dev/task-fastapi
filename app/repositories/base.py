from typing import Protocol


class TaskRepository(Protocol):
    def init_db(self) -> None:
        ...

    def list_tasks(self) -> list[dict]:
        ...

    def get_task(self, task_id: int) -> dict | None:
        ...

    def create_task(self, title: str) -> dict:
        ...

    def update_task(self, task_id: int, title: str, done: bool) -> dict | None:
        ...

    def delete_task(self, task_id: int) -> bool:
        ...
