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

## Payment Provider Mock

The application uses a mock payment provider (`MockPaymentProvider`) for testing purposes. No real payment gateway integration is required.

**Behavior:**
- Payment tokens ending with `"fail"` → Payment fails with error "Payment declined by provider"
- All other tokens → Payment succeeds with a generated transaction ID

**Example usage:**
```python
from app.services.payment_provider import MockPaymentProvider

provider = MockPaymentProvider()

# This will succeed
result = provider.process_payment("tok_valid_card", Decimal("99.99"), "USD")
# result.success = True, result.transaction_id = "txn_abc123..."

# This will fail
result = provider.process_payment("tok_card_fail", Decimal("99.99"), "USD")
# result.success = False, result.error = "Payment declined by provider"
```
