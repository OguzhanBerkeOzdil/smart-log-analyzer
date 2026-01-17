import pytest
from typing import List, AsyncIterable, TypeVar, Callable
from smart_log_analyzer.core.models import LogEntry, ErrorGroup

T = TypeVar("T")


async def async_generator(items: List[T]) -> AsyncIterable[T]:
    for item in items:
        yield item


@pytest.fixture
def mock_stream() -> Callable[[List[LogEntry]], AsyncIterable[LogEntry]]:
    """Returns a function that converts a list into an async iterable."""
    return async_generator


@pytest.fixture
def sample_logs() -> list[LogEntry]:
    return [
        LogEntry(
            timestamp="2023-01-01",
            level="INFO",
            service="api",
            message="Health check",
            duration_ms=10,
        ),
        LogEntry(
            timestamp="2023-01-01",
            level="ERROR",
            service="db",
            message="Connection timeout",
        ),
        LogEntry(
            timestamp="2023-01-01",
            level="ERROR",
            service="db",
            message="Connection timeout",
        ),
        LogEntry(
            timestamp="2023-01-01",
            level="ERROR",
            service="auth",
            message="Invalid token",
        ),
        LogEntry(
            timestamp="2023-01-01",
            level="INFO",
            service="api",
            message="Slow endpoint",
            duration_ms=5000,
        ),
    ]


@pytest.fixture
def sample_error_group() -> ErrorGroup:
    return ErrorGroup(service="db", message="Connection timeout", count=5)
