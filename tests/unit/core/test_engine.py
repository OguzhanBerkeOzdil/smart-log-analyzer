import pytest
from pathlib import Path
from typing import AsyncIterable, Any
from unittest.mock import AsyncMock, MagicMock

from smart_log_analyzer.core.engine import AnalysisEngine
from smart_log_analyzer.core.ai_strategy import AIAnalyzer
from smart_log_analyzer.core.models import LogEntry, ErrorGroup


async def empty_stream(_: Path) -> AsyncIterable[LogEntry]:
    if False:
        yield


@pytest.mark.asyncio
async def test_engine_without_ai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    engine = AnalysisEngine(enable_ai=False)

    monkeypatch.setattr(
        "smart_log_analyzer.core.engine.AsyncLogReader.read_file",
        empty_stream,
    )

    for s in engine.strategies:
        monkeypatch.setattr(
            s,
            "analyze",
            AsyncMock(return_value={"kind": "performance"}),
        )

    # Act
    results = await engine.run(Path("dummy.jsonl"))

    # Assert
    assert "AI Insight Analysis" not in results
    assert len(results) == 2


@pytest.mark.asyncio
async def test_engine_with_ai_and_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    engine = AnalysisEngine(enable_ai=True)

    monkeypatch.setattr(
        "smart_log_analyzer.core.engine.AsyncLogReader.read_file",
        empty_stream,
    )

    error_result: dict[str, Any] = {
        "kind": "error",
        "total_errors": 1,
        "unique_errors": 1,
        "top_errors": [ErrorGroup(service="db", message="timeout", count=1)],
    }

    for s in engine.strategies:
        if s.name == "Error Analysis":
            monkeypatch.setattr(
                s,
                "analyze",
                AsyncMock(return_value=error_result),
            )
        elif s.name == "Performance Analysis":
            monkeypatch.setattr(
                s,
                "analyze",
                AsyncMock(return_value={"kind": "performance"}),
            )

    ai = next(s for s in engine.strategies if isinstance(s, AIAnalyzer))

    mock_ai = MagicMock(
        return_value={
            "kind": "ai",
            "top_error": None,
            "insight": "ok",
        }
    )

    monkeypatch.setattr(
        ai,
        "analyze_from_error_result",
        mock_ai,
    )

    # Act
    results = await engine.run(Path("dummy.jsonl"))

    # Assert
    assert "AI Insight Analysis" in results
    mock_ai.assert_called_once()


@pytest.mark.asyncio
async def test_engine_with_ai_but_no_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    engine = AnalysisEngine(enable_ai=True)

    monkeypatch.setattr(
        "smart_log_analyzer.core.engine.AsyncLogReader.read_file",
        empty_stream,
    )

    for s in engine.strategies:
        if s.name != "AI Insight Analysis":
            monkeypatch.setattr(
                s,
                "analyze",
                AsyncMock(return_value={"kind": "performance"}),
            )

    ai = next(s for s in engine.strategies if isinstance(s, AIAnalyzer))

    mock_ai = MagicMock()

    monkeypatch.setattr(
        ai,
        "analyze_from_error_result",
        mock_ai,
    )

    # Act
    results = await engine.run(Path("dummy.jsonl"))

    # Assert
    assert "AI Insight Analysis" not in results
    mock_ai.assert_not_called()
