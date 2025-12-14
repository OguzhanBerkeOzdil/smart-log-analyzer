from smart_log_analyzer.core.analysis import group_errors, slow_requests
from smart_log_analyzer.core.models import LogEntry


def test_group_errors_aggregates_counts(sample_logs: list[LogEntry]) -> None:
    """
    Should correctly count duplicate errors.
    """
    groups = group_errors(sample_logs)

    assert len(groups) == 2

    assert groups[0].service == "db"
    assert groups[0].count == 2
    assert groups[1].service == "auth"
    assert groups[1].count == 1


def test_slow_requests_filtering(sample_logs: list[LogEntry]) -> None:
    """
    Should return only requests with duration, sorted by slowest first.
    """
    slow = slow_requests(sample_logs, limit=10)

    assert len(slow) == 2
    assert slow[0].duration_ms == 5000
    assert slow[1].duration_ms == 10


def test_slow_requests_limit(sample_logs: list[LogEntry]) -> None:
    """
    Should respect the limit argument.
    """
    slow = slow_requests(sample_logs, limit=1)
    assert len(slow) == 1
    assert slow[0].duration_ms == 5000
