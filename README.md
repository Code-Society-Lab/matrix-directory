<div align="center">
  <img
    src="frontend/src/assets/matrix-directory-mark.svg"
    alt="Matrix Directory"
    width="120"
  />

  <h1>Matrix Directory</h1>

  <p>
    <em>A community directory for bots, frameworks, SDKs, and tools in the Matrix ecosystem.</em>
  </p>
</div>

<div align="center">

[![Join Matrix](https://img.shields.io/matrix/codesociety%3Amatrix.org?logo=matrix&label=%20&labelColor=%23202020&color=%23202020)](https://matrix.to/#/%23codesociety:matrix.org)
[![Tests](https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/tests.yml/badge.svg)](https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/tests.yml)
[![CodeQL Advanced](https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/codeql.yml/badge.svg)](https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Code-Society-Lab/matrix-directory/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Code-Society-Lab/matrix-directory)

</div>

Matrix Directory is a community-driven web application for discovering projects
in the Matrix ecosystem, including bots, frameworks, SDKs, and other tools.

It provides a Vue frontend for discovering and managing projects and a FastAPI
backend for authentication, profiles, project ownership, and directory data.

## Tech stack

- **Frontend:** Vue 3, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLModel
- **Database:** PostgreSQL
- **Migrations:** Pelican
- **Authentication:** Matrix Authentication Service / OpenID Connect
- **Development:** Docker Compose

## Development

### Requirements

- Docker with Docker Compose
- [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) only when testing Matrix login locally

Start the application with Docker Compose:

```bash
docker compose up --build
```

The services will be available at:

- [Frontend](http://localhost:5173)
- [Swagger UI](http://localhost:8000/api/docs)

The backend automatically applies database migrations on startup.

Stop the services:

```bash
docker compose down
```

Reset the local database:

```bash
docker compose down -v
```

## Authentication

Matrix Directory authenticates users through the Matrix Authentication Service
(MAS) using OpenID Connect.

Application accounts are identified by the OIDC `(issuer, subject)` pair. During
login, the backend resolves the authoritative Matrix ID by calling the
homeserver `/_matrix/client/v3/account/whoami` endpoint with the MAS access
token.

Matrix avatars use an authenticated backend thumbnail proxy. Set a stable
`MATRIX_TOKEN_ENCRYPTION_KEY` (a Fernet key) before enabling Matrix login:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

The backend encrypts the OAuth refresh token, then uses it only to stream the
Matrix v1 thumbnail endpoint. Neither Matrix OAuth token is exposed to the
browser.

For local development with a real Matrix account, use the helper script to
register an OAuth client and start an HTTPS tunnel:

```bash
python scripts/dev_matrix_tunnel.py
```

See [Authentication Architecture](docs/docs/architecture/authentication.md) for details about identity, sessions, and authorization.

## API

Interactive API documentation is available at:

- [Swagger UI](http://localhost:8000/api/docs)

Core endpoints include:

```text
GET  /api/health
GET  /api/projects/
GET  /api/projects/mine/
GET  /api/projects/{project_id}
POST /api/projects/
PATCH /api/projects/{project_id}
DELETE /api/projects/{project_id}

GET  /api/project-types/
GET  /api/labels/

GET  /api/auth/matrix/login
GET  /api/auth/matrix/callback
GET  /api/auth/me
POST /api/auth/logout
```

Project IDs are UUIDs.

Project creation, updates, and deletion require an authenticated session.
Ownership is derived from that session; callers cannot choose a project `user_id`.

## Migrations

Migrations are in `backend/db/migrations` and use [Pelican](https://github.com/PenguinBoi12/pelican).

```bash
cd backend
export DATABASE_URL='postgresql+psycopg://matrix:matrix@localhost:5432/matrix_directory'
pelican status
pelican up
pelican down
```

## Contributing

We welcome everyone to contribute! Whether it's fixing bugs, suggesting features, or improving the docs. Every bit helps.

- [Submit an issue](https://github.com/Code-Society-Lab/matrix-directory/issues)
- [Open a pull request](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CONTRIBUTING.md)
- Hop into our [Matrix](https://matrix.to/#/%23codesociety:matrix.org)
  or [Discord](https://discord.gg/code-society-823178343943897088) and say hi!

Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) and follow the [code of conduct](./CODE_OF_CONDUCT.md).

## License

Released under the [MIT License](https://github.com/Code-Society-Lab/matrix-directory/blob/main/LICENSE).
