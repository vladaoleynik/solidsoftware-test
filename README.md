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
make run     # start postgres, redis, api, and worker
```

Verify the API:

```bash
curl http://localhost:5000/health
# {"status":"ok"}
```

## Development

After `make setup`, [pre-commit](https://pre-commit.com/) runs automatically on each commit:

- Ruff (lint + format check)
- mypy
- pytest

Run the same checks manually:

```bash
make check        # lint + test (matches CI)
make lint         # ruff + mypy only
make test         # pytest (in-memory SQLite via test fixtures; no Docker required)
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
3. pytest

## Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 5000 | HTTP API |
| `postgres` | 5432 | Persistent storage |

## Project layout

```
app/
  __init__.py       # application factory
  config.py         # app config
  extensions.py     # SQLAlchemy instance
  models/           # ORM models
  routes/           # blueprints / endpoints
run.py              # entrypoint
Dockerfile
docker-compose.yml
pyproject.toml
uv.lock
```
