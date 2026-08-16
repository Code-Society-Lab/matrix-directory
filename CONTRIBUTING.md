# Contributing to Matrix Directory

Thank you for your interest in contributing to Matrix Directory! As an open source project, many kinds of contributions are welcome.

## How can you contribute?

You can contribute to the project in several ways:

- Report bugs
- Add new features
- Fix existing issues
- Improve the documentation
- Improve the UI/UX
- Add or improve tests

**Note:** Non-trivial pull requests should have a [GitHub issue](https://github.com/Code-Society-Lab/matrix-directory/issues) proposing or discussing the change first.

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Code-Society-Lab/matrix-directory.git
cd matrix-directory
```

2. Start the development environment:

```bash
docker compose up --build
```

Docker with Docker Compose is required.

The services will be available at:

- Frontend: http://localhost:5173
- API documentation: http://localhost:8000/docs

To stop the environment:

```bash
docker compose down
```

To reset the local database:

```bash
docker compose down -v
```

### Authentication

Matrix Directory normally uses the Matrix Authentication Service (MAS) for authentication.

For local testing with a Matrix account:

1. Install [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
2. Run:

```bash
python scripts/dev_matrix_tunnel.py
```

The helper starts an HTTPS tunnel, registers a temporary OAuth client, updates
the root `.env` file, and starts the Docker Compose services. The tunnel must
remain running while you test authentication.

See [Authentication Architecture](docs/architecture/authentication.md) for details.

## Guidelines

Read the related issue carefully before starting. Feel free to ask for clarification when requirements or expected behavior are unclear.

Keep changes focused and consistent with the existing architecture.

### Backend

- Use type hints.
- Use explicit request and response schemas.
- Validate user input.
- Enforce authentication and authorization on the backend.
- Never trust a client-provided project owner.
- Add a Pelican migration for database schema changes.
- Do not modify migrations that have already been merged.

### Frontend

- Keep components focused and reusable.
- Follow the existing design system.
- Keep interfaces responsive.
- Preserve keyboard and basic accessibility support.
- Avoid hiding functionality on smaller screens without providing an alternative.

### Tests

Write tests for behavior you add or change.

- Bug fixes should include a regression test when practical.
- New features should include tests for their important behavior.
- Authentication and authorization changes should test failure cases as well as successful ones.

## Before opening a PR

Before opening your pull request, make sure you've checked the items that apply:

- [ ] The change has a related issue if it is non-trivial
- [ ] The code is clean and follows the existing project style
- [ ] Python code is typed
- [ ] Relevant tests have been added or updated
- [ ] Existing tests pass
- [ ] Authorization is enforced server-side where required
- [ ] Database changes include a Pelican migration
- [ ] Documentation has been updated when behavior or architecture changed
- [ ] UI changes work on both desktop and mobile
- [ ] No credentials, tokens, cookies, or other secrets have been committed
- [ ] Code, documentation, and other project text are written in English

For significant UI changes, include screenshots in the pull request.

## After opening a PR

A maintainer will review your changes.

During review, we may:

- Ask questions about implementation decisions
- Request code changes
- Request additional tests
- Request documentation updates
- Suggest a simpler or more consistent approach

Code review is a normal part of contributing and helps keep Matrix Directory maintainable as the project grows.

## Security

Do not open a public issue containing details of an exploitable security vulnerability.

Avoid including credentials, session cookies, access tokens, or other secrets in issues, logs, or pull requests.

## Join the community

Need help, have questions, or want to participate in the project?

Join the [Code Society Matrix room](https://matrix.to/#/%23codesociety:matrix.org).
