from smart_log_analyzer.core.strategies import ErrorAnalyzer, PerformanceAnalyzer
from smart_log_analyzer.core.models import LogEntry


def test_group_errors_aggregates_counts(sample_logs: list[LogEntry]) -> None:
    result = ErrorAnalyzer().analyze(sample_logs)
    groups = result["top_errors"]

    assert len(groups) == 2
    assert groups[0].service == "db"
    assert groups[0].count == 2
    assert groups[1].service == "auth"
    assert groups[1].count == 1


def test_slow_requests_filtering(sample_logs: list[LogEntry]) -> None:
    result = PerformanceAnalyzer().analyze(sample_logs)
    slow = result["slowest_requests"]

    assert len(slow) == 2
    assert slow[0].duration_ms == 5000
    assert slow[1].duration_ms == 10


def test_slow_requests_limit(sample_logs: list[LogEntry]) -> None:
    result = PerformanceAnalyzer().analyze(sample_logs)
    slow = result["slowest_requests"]

    assert len(slow) <= 10
    if slow:
        assert slow[0].duration_ms == 5000
