install:
	uv sync

format:
	uv run black .

check:
	uv run black --check .
	uv run mypy .
	uv run pyright

test:
	uv run pytest

all: format check test