<div align="center" style="margin-bottom: 20px">
  <img
    src="./img/matrix-directory-mark.svg"
    alt="Matrix Directory"
    width="140"
  />

  <h1>Matrix Directory</h1>

  <em>A community directory for bots, frameworks, SDKs, and tools in the Matrix ecosystem.</em>
</div>

<div align="center" markdown>

[Get Started](development.md){ .md-button .md-button--primary }
[HTTP API](reference/api.md){ .md-button }

</div>

<div align="center">

<p>
  <a href="https://discord.gg/code-society-823178343943897088">
    <img
      src="https://discordapp.com/api/guilds/823178343943897088/widget.png?style=shield"
      alt="Join Discord"
    />
  </a>

  <a href="https://matrix.to/#/%23codesociety:matrix.org">
    <img
      src="https://img.shields.io/matrix/codesociety%3Amatrix.org?logo=matrix&label=%20&labelColor=%23202020&color=%23202020"
      alt="Join Matrix"
    />
  </a>

  <a href="https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/tests.yml">
    <img
      src="https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/tests.yml/badge.svg"
      alt="Tests"
    />
  </a>

  <a href="https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/codeql.yml">
    <img
      src="https://github.com/Code-Society-Lab/matrix-directory/actions/workflows/codeql.yml/badge.svg"
      alt="CodeQL Advanced"
    />
  </a>

  <a href="https://securityscorecards.dev/viewer/?uri=github.com/Code-Society-Lab/matrix-directory">
    <img
      src="https://api.securityscorecards.dev/projects/github.com/Code-Society-Lab/matrix-directory/badge"
      alt="OpenSSF Scorecard"
    />
  </a>
</p>

</div>

---

Matrix Directory is a community-driven web application for discovering projects
in the [Matrix](https://matrix.org) ecosystem. Its Vue frontend provides the
directory experience, while its FastAPI backend handles authentication,
profiles, project ownership, and directory data.

!!! note "Proof of concept"
    Matrix Directory is under active development. Interfaces and development
    workflows may change as the project evolves.

- **Discoverable** — find bots, frameworks, SDKs, and other Matrix tools
- **Matrix-native** — sign in with a Matrix account through OpenID Connect
- **Ownership-aware** — manage project listings through an authenticated session
- **Typed end to end** — Vue and TypeScript on the frontend, FastAPI and SQLModel on the backend

## Quickstart

=== "Start"

    **Requirements:** Docker with Docker Compose

    ```bash
    git clone git@github.com:Code-Society-Lab/matrix-directory.git
    cd matrix-directory
    docker compose up --build
    ```

    Database migrations run automatically when the backend starts.

=== "Open"

    Once the services are ready, open:

    - [Matrix Directory](http://localhost:5173)
    - [Interactive API documentation](http://localhost:8000/api/docs)

=== "Stop or reset"

    Stop the services while preserving local data:

    ```bash
    docker compose down
    ```

    Remove the services and local database volume:

    ```bash
    docker compose down -v
    ```

## Technology

| Area | Technology |
| --- | --- |
| Frontend | Vue 3, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLModel |
| Database | PostgreSQL |
| Migrations | Pelican |
| Authentication | Matrix Authentication Service and OpenID Connect |
| Local development | Docker Compose |

## Where to go next

<div class="grid cards" markdown>

- :material-upload: **Submit a project**

    ---

    Publish a listing and understand project types, labels, and Markdown.

    [:octicons-arrow-right-24: Read the submission guide](guides/submitting-a-project.md)

- :fontawesome-solid-code: **Development**

    ---

    Set up the application, run its checks, and build the documentation locally.

    [:octicons-arrow-right-24: Read the development guide](development.md)

- :material-api: **HTTP API**

    ---

    Explore the endpoints, authentication requirements, and project data model.

    [:octicons-arrow-right-24: Browse the API reference](reference/api.md)

- :material-shield-account: **Authentication**

    ---

    Understand Matrix login, sessions, application identities, and authorization.

    [:octicons-arrow-right-24: Read the architecture guide](architecture/authentication.md)

- :fontawesome-brands-github: **Source code**

    ---

    Browse the source, open an issue, or contribute a change on GitHub.

    [:octicons-arrow-right-24: View on GitHub](https://github.com/Code-Society-Lab/matrix-directory)

</div>

## Contributing

Contributions are welcome, whether they fix bugs, suggest features, or improve
the documentation.

- [Submit an issue](https://github.com/Code-Society-Lab/matrix-directory/issues)
- [Open a pull request](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CONTRIBUTING.md)
- Join the community on [Matrix](https://matrix.to/#/%23codesociety:matrix.org)
  or [Discord](https://discord.gg/code-society-823178343943897088)

Please read the [contributing guide](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CONTRIBUTING.md)
and follow the [code of conduct](https://github.com/Code-Society-Lab/matrix-directory/blob/main/CODE_OF_CONDUCT.md).

## License

Released under the [MIT License](https://github.com/Code-Society-Lab/matrix-directory/blob/main/LICENSE).
