# Matrix Directory

Matrix directory is a web application for discovering and managing Matrix ecosystems (bots, frameworks, SDKs, etc). It provides a frontend for users to browse and interact with projects, and a backend API for managing project data.

## Run

```bash
docker compose up --build
```

- http://localhost:5173 — frontend
- http://localhost:8000/docs — API docs

The API runs migrations and seeds the database with [Ada](https://github.com/Code-Society-Lab/ada).

## Matrix login

The directory signs users in through the Matrix Authentication Service (MAS). The
first version uses `account.matrix.org` and requests only the OpenID Connect
`openid` scope—never Matrix API access.

`account.matrix.org` rejects localhost and non-HTTPS OAuth URLs. For local
development, expose the frontend through a temporary HTTPS tunnel. Its `/api`
requests are proxied to the backend:

```bash
cloudflared tunnel --url http://localhost:5173
```

Copy the generated `https://….trycloudflare.com` URL, then register it:

```bash
curl https://account.matrix.org/oauth2/registration \
  -H 'Content-Type: application/json' \
  -d '{
    "client_name": "Matrix Directory",
    "client_uri": "https://newer-linux-distributor-brief.trycloudflare.com",
    "redirect_uris": ["https://newer-linux-distributor-brief.trycloudflare.com/api/auth/matrix/callback"],
    "grant_types": ["authorization_code"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "client_secret_basic"
  }'
```

Copy `.env.example` to `.env`, then set `MATRIX_OIDC_CLIENT_ID` and
`MATRIX_OIDC_CLIENT_SECRET` from that response. Set `MATRIX_OIDC_REDIRECT_URI` to
the same tunnel URL plus `/api/auth/matrix/callback`, set `FRONTEND_ORIGIN` to the
tunnel URL, set `SESSION_COOKIE_SECURE=true`, and replace `APP_SECRET` with a long
random value. Restart the application and use the tunnel URL—not localhost—to sign
in.

Quick Tunnel URLs change when restarted, requiring a new client registration. A
stable HTTPS domain or named tunnel avoids that in production.

MAS returns an opaque account identifier, not the user's full Matrix ID. The app
therefore keys accounts by the secure `(issuer, subject)` pair; a public Matrix ID
can be added to the profile separately. In production, register HTTPS URLs, set
`SESSION_COOKIE_SECURE=true`, and store both secrets in a secret manager.

For quick local testing, a script is provided to register a client and start a tunnel:

```bash
python scripts/dev_matrix_tunnel.py
```

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
GET  /api/auth/matrix/login
GET  /api/auth/matrix/callback
GET  /api/auth/me
POST /api/auth/logout
```

Project IDs are UUIDs.

Project creation, updates, and deletion require a verified session. Ownership is
derived from that session; callers can no longer choose a project `user_id`.

## Migrations

Migrations are in `backend/db/migrations` and use [Pelican](https://github.com/PenguinBoi12/pelican).

```bash
cd backend
export DATABASE_URL='postgresql+psycopg://matrix:matrix@localhost:5432/matrix_directory'
pelican status
pelican up
pelican down
```
