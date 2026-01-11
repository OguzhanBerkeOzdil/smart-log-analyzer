import pytest
from smart_log_analyzer.core.models import LogEntry, ErrorGroup


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
