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

ui:
	uv run streamlit run src/smart_log_analyzer/ui/app.py

all: format check test
