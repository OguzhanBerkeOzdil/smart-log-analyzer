import pytest
from typing import Callable, List, AsyncIterable

from smart_log_analyzer.core.strategies import (
    ErrorAnalyzer,
    PerformanceAnalyzer,
)
from smart_log_analyzer.core.models import LogEntry

MockStream = Callable[[List[LogEntry]], AsyncIterable[LogEntry]]


@pytest.mark.asyncio
async def test_group_errors_aggregates_counts(
    sample_logs: list[LogEntry],
    mock_stream: MockStream,
) -> None:
    # Arrange
    analyzer = ErrorAnalyzer()
    stream = mock_stream(sample_logs)

    # Act
    result = await analyzer.analyze(stream)
    groups = result["top_errors"]

    # Assert
    assert len(groups) == 2
    assert groups[0].service == "db"
    assert groups[0].count == 2
    assert groups[1].service == "auth"
    assert groups[1].count == 1


@pytest.mark.asyncio
async def test_slow_requests_filtering(
    sample_logs: list[LogEntry],
    mock_stream: MockStream,
) -> None:
    # Arrange
    analyzer = PerformanceAnalyzer()
    stream = mock_stream(sample_logs)

    # Act
    result = await analyzer.analyze(stream)
    slow_requests = result["slowest_requests"]

    # Assert
    assert len(slow_requests) == 2
    assert slow_requests[0].duration_ms == 5000
    assert slow_requests[1].duration_ms == 10


@pytest.mark.asyncio
async def test_slow_requests_limit(
    sample_logs: list[LogEntry],
    mock_stream: MockStream,
) -> None:
    # Arrange
    analyzer = PerformanceAnalyzer()
    stream = mock_stream(sample_logs)

    # Act
    result = await analyzer.analyze(stream)
    slow_requests = result["slowest_requests"]

    # Assert
    assert len(slow_requests) <= 10
    if slow_requests:
        assert slow_requests[0].duration_ms == 5000
