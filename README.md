# Task API

A small FastAPI CRUD API for managing a to-do list. Tasks are stored in memory, so changes are lost when the server restarts.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn main:app --reload --port 8000
```

Open the API at:

```text
http://localhost:8000
```

Open Swagger UI at:

```text
http://localhost:8000/docs
```

## Endpoints

| Method | Path | Description | Success |
|---|---|---|---|
| `GET` | `/` | API information | `200` |
| `GET` | `/health` | Health check | `200` |
| `GET` | `/tasks` | List all tasks | `200` |
| `GET` | `/tasks/{id}` | Get one task | `200` |
| `POST` | `/tasks` | Create a task | `201` |
| `PUT` | `/tasks/{id}` | Update a task title and/or done status | `200` |
| `DELETE` | `/tasks/{id}` | Delete a task | `204` |

Error behavior:

| Case | Status |
|---|---:|
| Missing or empty `title` on create | `400` |
| Empty or invalid update body | `400` |
| Unknown task id | `404` |

## Example Curl Output

Command:

```bash
curl -i http://localhost:8000/tasks/1
```

Output:

```text
HTTP/1.1 200 OK
date: Thu, 17 Sep 2026 18:19:01 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"id":1,"title":"Learn HTTP basics","done":false}
```

## Example Requests

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Update a task:

```bash
curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d "{\"title\":\"Updated task\",\"done\":true}"
```

Delete a task:

```bash
curl -i -X DELETE http://localhost:8000/tasks/4
```

## Swagger UI

![Swagger UI screenshot](docs/swagger-docs.png)

Swagger UI lists the API endpoints and can run the full create, read, update, and delete flow with "Try it out".
