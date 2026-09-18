# Assignment 2 SQL Exploration

These SQL statements were executed manually against `tasks.db` with the SQLite CLI.

```sql
SELECT * FROM tasks;
SELECT * FROM tasks WHERE done = 1;
SELECT COUNT(*) FROM tasks;
UPDATE tasks SET done = 1;
DELETE FROM tasks WHERE done = 1;
```

After the manual update/delete queries, the API reflected the database changes through `GET /tasks` because the API now reads from SQLite instead of memory.
