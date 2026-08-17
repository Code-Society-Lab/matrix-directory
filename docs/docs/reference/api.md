# HTTP API

The FastAPI backend exposes JSON application endpoints under `/api`. This
page describes the stable behaviors a client needs; the running application
provides the complete generated schemas in its
[Swagger UI](https://matrix-directory.codesociety.xyz/docs).

## At a glance

- Public reads do not require authentication.
- Profile and project-management endpoints use a browser session cookie.
- Project IDs, category IDs, and user IDs are UUIDs.
- Request validation failures use FastAPI's standard `422` response.
- Project ownership is derived from the session and cannot be supplied by a client.

## Conventions

### Requests and responses

Request bodies use JSON. Successful endpoints that return data also return JSON,
except logout and project deletion, which return an empty `204 No Content`
response.

For requests made from a browser frontend on another origin, include
credentials so the application session cookie is sent:

```javascript
const response = await fetch("http://localhost:8000/api/auth/me", {
  credentials: "include",
});
```

The backend only allows credentialed cross-origin requests from the configured
`FRONTEND_ORIGIN`.

### Authentication levels

| Level | Meaning |
| --- | --- |
| Public | No session is required |
| Authenticated | A valid Matrix Directory session is required |
| Owner | The authenticated user must own the project |

Owner-only mutations return `404 Not Found` when the project does not exist
or is not owned by the current user. This avoids revealing another user's
private management state.

### Errors

Application errors use a JSON `detail` field:

```json
{
  "detail": "Authentication required"
}
```

| Status | Typical cause |
| --- | --- |
| `400 Bad Request` | A supplied category ID does not exist |
| `401 Unauthorized` | The session cookie is missing, invalid, or expired |
| `404 Not Found` | The resource is missing or unavailable to its current user |
| `422 Unprocessable Content` | The request body or path parameters are invalid |
| `503 Service Unavailable` | Matrix login has not been configured |

Validation errors contain FastAPI's structured list of field errors rather than
a single string.

## System

### Check API health

```http
GET /api/health
```

```json
{
  "status": "ok"
}
```

| Method | Path | Access | Success |
| --- | --- | --- | --- |
| `GET` | `/api/health` | Public | `200 OK` |

## Projects

### Endpoints

| Method | Path | Access | Success | Description |
| --- | --- | --- | --- | --- |
| `GET` | `/api/projects/` | Public | `200 OK` | List all projects |
| `GET` | `/api/projects/mine/` | Authenticated | `200 OK` | List projects owned by the current user |
| `GET` | `/api/projects/{project_id}` | Public | `200 OK` | Get one project |
| `POST` | `/api/projects/` | Authenticated | `201 Created` | Create a project |
| `PATCH` | `/api/projects/{project_id}` | Owner | `200 OK` | Update supplied fields |
| `DELETE` | `/api/projects/{project_id}` | Owner | `204 No Content` | Delete a project |

### Create a project

A project requires at least one valid category. The authenticated user becomes
the owner; there is no writable `user_id` field.

```json
{
  "name": "Example Bot",
  "description": "A longer description of the project.",
  "short_description": "A concise project summary.",
  "repository_url": "https://github.com/example/example-bot",
  "website_url": null,
  "matrix_server_url": null,
  "supports_e2ee": true,
  "category_ids": [
    "11111111-1111-1111-1111-111111111111"
  ]
}
```

| Field | Required | Constraints |
| --- | --- | --- |
| `name` | Yes | 2–100 characters |
| `description` | Yes | String |
| `short_description` | Yes | At most 240 characters |
| `repository_url` | No | String or `null` |
| `website_url` | No | String or `null` |
| `matrix_server_url` | No | String or `null` |
| `supports_e2ee` | No | Boolean; defaults to `false` |
| `category_ids` | Yes | Non-empty list of existing category UUIDs |

### Update a project

`PATCH` changes only supplied fields:

```json
{
  "name": "Renamed Bot",
  "supports_e2ee": true
}
```

The required project fields—`name`, `description`, `short_description`,
`supports_e2ee`, and `category_ids`—may be omitted from a patch but cannot
be explicitly set to `null`. URL fields may be cleared with `null`.

### Project response

Project responses include public owner details and expanded categories:

```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "name": "Example Bot",
  "description": "A longer description of the project.",
  "short_description": "A concise project summary.",
  "repository_url": "https://github.com/example/example-bot",
  "website_url": null,
  "matrix_server_url": null,
  "supports_e2ee": true,
  "user_id": "33333333-3333-3333-3333-333333333333",
  "owner": {
    "id": "33333333-3333-3333-3333-333333333333",
    "display_name": "Example Maintainer",
    "matrix_id": "@maintainer:example.org",
    "avatar_url": null
  },
  "categories": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "name": "Bots"
    }
  ]
}
```

## Authentication

Authentication endpoints are browser-oriented because login redirects through
the configured Matrix Authentication Service.

| Method | Path | Access | Success | Description |
| --- | --- | --- | --- | --- |
| `GET` | `/api/auth/matrix/login` | Public | Redirect | Begin Matrix OIDC login |
| `GET` | `/api/auth/matrix/callback` | OIDC flow | Redirect | Complete login and create a session |
| `GET` | `/api/auth/me` | Authenticated | `200 OK` | Return the current user and profile |
| `POST` | `/api/auth/logout` | Public | `204 No Content` | Revoke any current session and clear its cookie |

The application session cookie is HTTP-only. Signing in does not grant Matrix
Directory access to Matrix rooms or messages. See
[Authentication architecture](../architecture/authentication.md) for the
identity model and complete login flow.

## Profile

| Method | Path | Access | Success | Description |
| --- | --- | --- | --- | --- |
| `PUT` | `/api/profile/me` | Authenticated | `200 OK` | Replace the current user's public profile |

The profile body accepts these nullable fields:

```json
{
  "matrix_id": "@maintainer:example.org",
  "display_name": "Example Maintainer",
  "bio": "Maintains useful Matrix projects.",
  "avatar_url": null,
  "github_url": "https://github.com/example",
  "website_url": null
}
```

Because this is a `PUT` endpoint, omitted fields are stored as `null`.
Changing `matrix_id` clears any existing verification. Clients cannot set
`matrix_id_verified`.

## Related documentation

- [Development guide](../development.md)
- [Authentication architecture](../architecture/authentication.md)
- [Interactive API documentation](https://matrix-directory.codesociety.xyz/docs)
