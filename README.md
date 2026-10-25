# Solid Software Test Task

## Stack

| Component | Choice                                |
|-----------|---------------------------------------|
| API | Flask                 |
| Database | PostgreSQL                            |
| ORM | SQLAlchemy                        |
| Dependencies | [uv](https://docs.astral.sh/uv/)      |
| Orchestration | Docker Compose                        |
| Lint / format | [Ruff](https://docs.astral.sh/ruff/)  |
| Type checking | [mypy](https://mypy-lang.org/)        |
| Git hooks | [pre-commit](https://pre-commit.com/) |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quick start

```bash
make setup   # install dependencies, create .env, install pre-commit hooks
make run     # start postgres and api (runs migrations, then loads db/seed.sql)
```

Schema changes: update models, then `uv run flask db migrate -m "..."`, commit the new file under `migrations/versions/`, and restart (or `make migrate`).

Verify the API:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

## Development

After `make setup`, [pre-commit](https://pre-commit.com/) runs automatically on each commit:

- Ruff (lint + format check)
- mypy

Run the same checks manually:

```bash
make check        # lint (matches CI)
make lint         # ruff + mypy only
make pre-commit   # all pre-commit hooks
```

Fix formatting issues:

```bash
uv run ruff format .
```

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push and pull requests to `main`, `develop`, and all other branches:

1. Ruff check and format check
2. mypy

## Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | HTTP API |
| `postgres` | 5432 | Persistent storage |
