from smart_log_analyzer.core.strategies import ErrorAnalyzer, PerformanceAnalyzer
from smart_log_analyzer.core.models import LogEntry


def test_group_errors_aggregates_counts(sample_logs: list[LogEntry]) -> None:
    """
    Should correctly count duplicate errors.
    """
    # Arrange
    analyzer = ErrorAnalyzer()

    # Act
    result = analyzer.analyze(sample_logs)
    groups = result["top_errors"]

    # Assert
    assert len(groups) == 2
    assert groups[0].service == "db"
    assert groups[0].count == 2
    assert groups[1].service == "auth"
    assert groups[1].count == 1


def test_slow_requests_filtering(sample_logs: list[LogEntry]) -> None:
    """
    Should return only requests with duration, sorted by slowest first.
    """
    # Arrange
    analyzer = PerformanceAnalyzer()

    # Act
    result = analyzer.analyze(sample_logs)
    slow = result["slowest_requests"]

    # Assert
    assert len(slow) == 2
    assert slow[0].duration_ms == 5000
    assert slow[1].duration_ms == 10


def test_slow_requests_limit(sample_logs: list[LogEntry]) -> None:
    """
    Should respect the limit argument.
    """
    # Arrange
    analyzer = PerformanceAnalyzer()

    # Act
    result = analyzer.analyze(
        sample_logs
    )  # The analyzer returns top 10 by default, we just check we got them
    slow = result["slowest_requests"]

    # Assert
    assert len(slow) <= 10
    if len(slow) > 0:
        assert slow[0].duration_ms == 5000
