.PHONY: setup run

setup:
	uv sync
	@test -f .env || cp .env.example .env
	uv run pre-commit install

run:
	uv run flask run
