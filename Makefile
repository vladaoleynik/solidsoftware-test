.PHONY: setup run migrate test

setup:
	uv sync
	@test -f .env || cp .env.example .env
	uv run pre-commit install

run:
	docker compose up --build

migrate:
	docker compose exec app flask db upgrade

test:
	uv run pytest
