# Task API

A small FastAPI CRUD API for managing a to-do list. The API started with in-memory storage, moved to SQLite, and now runs against PostgreSQL in Docker.

## Run The Full Stack

Create a local `.env` from the committed example:

```bash
cp .env.example .env
```

Start the API and Postgres together:

```bash
docker compose up --build
```

Open the API at:

```text
http://localhost:8000
```

Open Swagger UI at:

```text
http://localhost:8000/docs
```

## Configuration

The app reads its database connection from `DATABASE_URL`.

Local `.env` example:

```text
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
POSTGRES_PASSWORD=dev
POSTGRES_DB=tasks
```

Inside Docker Compose, the API connects to Postgres through the Compose service name `db`:

```text
postgres://postgres:dev@db:5432/tasks
```

`.env` is gitignored. `.env.example` is committed so a clean clone knows which variables to set.

## Storage Architecture

Routes call the service layer, and the service calls a repository. The Postgres-specific SQL lives in `app/repositories/postgres_repository.py`.

Before the Postgres swap, the project was refactored to isolate storage behind the repository boundary. After that, the API route behavior stayed the same while the storage engine changed from SQLite to Postgres.

## Database

Postgres runs in Docker using the official `postgres:16` image. Data is stored in a named Docker volume:

```text
taskdata
```

The app creates the `tasks` table automatically if it is missing and seeds three example tasks only when the table is empty.

Schema:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
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
curl -i http://localhost:8000/tasks
```

Output:

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

[{"id":1,"title":"Learn HTTP basics","done":false},{"id":2,"title":"Build CRUD endpoints","done":false},{"id":3,"title":"Test with Swagger UI","done":false}]
```

## Example Requests

Create a task:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Postgres task\"}"
```

Update a task:

```bash
curl -i -X PUT http://localhost:8000/tasks/4 -H "Content-Type: application/json" -d "{\"title\":\"Updated Postgres task\",\"done\":true}"
```

Delete a task:

```bash
curl -i -X DELETE http://localhost:8000/tasks/4
```

## Persistence Check

To prove persistence across a full stack restart:

```bash
docker compose up --build
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Survives restart\"}"
docker compose down
docker compose up
curl -i http://localhost:8000/tasks
```

The created task should still appear after `docker compose down` and `docker compose up` because Postgres stores data in the `taskdata` volume.

## Inspect Data In Postgres

```bash
docker compose exec db psql -U postgres -d tasks -c "\dt"
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

Postgres data view:

![Postgres data screenshot](docs/assignment-3/screenshots/postgres-data.png)

Previous assignment screenshots are stored under `docs/assignment-1/` and `docs/assignment-2/`.
