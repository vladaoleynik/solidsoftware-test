.PHONY: setup run migrate

setup:
	uv sync
	@test -f .env || cp .env.example .env
	uv run pre-commit install

run:
	docker compose up --build

migrate:
	uv run flask db upgrade
