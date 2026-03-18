dev:
	uv run uvicorn app.main:app --reload

migrate:
	uv run alembic upgrade head

test:
	uv run pytest
