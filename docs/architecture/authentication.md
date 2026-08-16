# Authentication Architecture

Matrix Directory uses the [Matrix Authentication Service (MAS)](https://element-hq.github.io/matrix-authentication-service/) with OpenID Connect for authentication.

Authentication is intentionally separate from Matrix Client API access. Signing in does not give Matrix Directory access to rooms, messages, or other Matrix account data.

## Identity

MAS provides an OIDC `sub` claim. This value is an opaque account identifier and is **not** a Matrix ID.

Users are therefore identified by:

```text
(oidc_issuer, oidc_subject)
```

These values are private authentication data and must not be exposed through public API responses.

## User and Profile

Authentication and public identity are separate:

```text
User
├── id
├── oidc_issuer
└── oidc_subject
      |
      | 1:1
      v
Profile
├── matrix_id
├── matrix_id_verified
├── display_name
├── bio
├── avatar_url
├── github_url
└── website_url
```

In that design, `User` remains private authentication and ownership data while
`Profile` contains public information. A user-provided `matrix_id` is not
automatically trusted, and clients cannot set `matrix_id_verified`.

## Login flow

```text
Browser
   ↓
GET /api/auth/matrix/login
   ↓
MAS
   ↓
GET /api/auth/matrix/callback
   ↓
Resolve user by (issuer, subject)
   ↓
Create application session
   ↓
Browser session cookie
```

Matrix Directory creates its own session after successful OIDC authentication.

The application currently requests:

```text
openid
```

It does not request Matrix Client API scopes.

See the [MAS scope documentation](https://element-hq.github.io/matrix-authentication-service/reference/scopes.html).

## Authorization

Project ownership is always derived from the authenticated session.

```text
Authenticated User
       ↓
Project.user_id
```

Clients must never be allowed to choose an arbitrary project `user_id`.

Authorization checks must always happen on the backend.

## Security rules

The following must remain true:

- Matrix passwords are never handled by Matrix Directory.
- OIDC `sub` is never treated as a Matrix ID.
- Users are identified by `(issuer, subject)`.
- Authentication fields are private.
- Project ownership comes from the authenticated session.
- If profile verification is added, `matrix_id_verified` cannot be set by clients.
- Matrix Client API access is not requested unless a feature explicitly requires it.

## References

- [Matrix Authentication Service](https://element-hq.github.io/matrix-authentication-service/)
- [MAS authorization documentation](https://element-hq.github.io/matrix-authentication-service/topics/authorization.html)
- [MAS OAuth scopes](https://element-hq.github.io/matrix-authentication-service/reference/scopes.html)
- [MAS API reference](https://element-hq.github.io/matrix-authentication-service/api/index.html)
