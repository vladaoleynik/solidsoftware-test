# solidsoftware-test

Python Flask API with SQLAlchemy.

## Setup

```bash
make setup
```

## Run

```bash
make run
```

## Checks

```bash
uv run pre-commit run --all-files
```

The API listens on http://127.0.0.1:5000.

## Endpoints

| Method | Path | Description  |
|--------|------|--------------|
| GET    | `/`  | Health check |

## Project layout

```
app/
  __init__.py       # application factory
  config.py         # app config
  extensions.py     # SQLAlchemy instance
  models/           # ORM models
  routes/           # blueprints / endpoints
run.py              # entrypoint
pyproject.toml
uv.lock
```
