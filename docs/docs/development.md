# Development guide

Matrix Directory is a full-stack application for discovering bots, frameworks,
SDKs, and tools in the [Matrix](https://matrix.org) ecosystem. This guide takes
you from a fresh checkout to a running development environment and the same
quality checks used in continuous integration.

## What you will set up

- A Vue 3 and TypeScript frontend with hot reload
- A FastAPI backend with interactive API documentation
- A PostgreSQL database with migrations applied at startup
- Optional Matrix login through an HTTPS development tunnel

## Quickstart

### Requirements

| Tool | When it is needed |
| --- | --- |
| Docker with Docker Compose | Running the complete application |
| Python 3.10 or newer | Backend checks, documentation, and helper scripts |
| Node.js 24 and npm | Running frontend checks outside Docker |
| [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) | Testing Matrix login locally |

!!! tip
    Only Docker is required for the basic quickstart. Install the language
    toolchains when you need to run an individual component or its checks.

### Run the application

From the repository root:

```bash
docker compose up --build
```

The backend applies database migrations automatically during startup. Once the
services are ready, open:

| Service | Address |
| --- | --- |
| Frontend | <http://localhost:5173> |
| Swagger UI | <http://localhost:8000/api/docs> |

You now have the frontend, backend, and database running together. The frontend
reloads as its source changes; restart the API service after backend changes.

### Stop or reset

Stop the services while preserving the local database:

```bash
docker compose down
```

To remove the database volume and start with clean local data:

```bash
docker compose down -v
```

!!! warning
    The reset command permanently removes data stored in the local Docker
    database volume.

## Work on the backend

Create a virtual environment and install the backend with its development
dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the same backend checks as CI:

```bash
black --check app db tests
mypy app db tests
pytest -q
```

During development, run an individual test by its node ID:

```bash
pytest tests/test_project_validation.py::test_create_with_no_categories__expect_validation_error -q
```

## Work on the frontend

Install the locked dependencies:

```bash
cd frontend
npm ci
```

Run the development server outside Docker:

```bash
npm run dev
```

Before opening a pull request, run the same frontend checks as CI:

```bash
npm run lint
npm run build
```

The production build includes TypeScript checking through `vue-tsc`.

## Test Matrix login locally

Matrix login requires a public HTTPS callback. From the repository root, run:

```bash
python scripts/dev_matrix_tunnel.py
```

The helper registers a temporary OAuth client, starts a Cloudflare tunnel,
updates the root `.env`, and launches Docker Compose. Keep it running while
testing authentication.

See [Authentication architecture](architecture/authentication.md) for the
identity, session, and authorization model.

## Build the documentation

Install the documentation dependencies into a backend virtual environment:

```bash
cd backend
python -m pip install -e ".[docs]"
cd ../docs
```

Preview changes with live reload:

```bash
mkdocs serve
```

Before committing documentation changes, verify a strict production build:

```bash
mkdocs build --strict
```

## Resources

- [HTTP API reference](reference/api.md)
- [Authentication architecture](architecture/authentication.md)
- [Matrix documentation](https://matrix.org/docs/)
- [Contributing guide](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CONTRIBUTING.md)
- [Code of conduct](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CODE_OF_CONDUCT.md)
- [Issue tracker](https://github.com/Code-Society-Lab/matrix-directory/issues)
