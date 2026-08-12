# Matrix Bot Directory

Matrix bot directory POC.

## Run

```bash
docker compose up --build
```

- http://localhost:5173 — frontend
- http://localhost:8000/docs — API docs

The API runs migrations and seeds the database with [Ada](https://github.com/Code-Society-Lab/ada).

Stop the services:

```bash
docker compose down
```

Reset the local database:

```bash
docker compose down -v
```

## API

```text
GET  /api/health
GET  /api/projects/
GET  /api/projects/{project_id}
POST /api/projects/
PATCH /api/projects/{project_id}
DELETE /api/projects/{project_id}
```

Project IDs are UUIDs.

## Migrations

Migrations are in `backend/db/migrations` and use [Pelican](https://github.com/PenguinBoi12/pelican).

```bash
cd backend
export DATABASE_URL='postgresql+psycopg://matrix:matrix@localhost:5432/matrix_directory'
pelican status
pelican up
pelican down
```
