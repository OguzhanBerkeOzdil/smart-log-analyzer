from typing import Dict, cast
from pytest import CaptureFixture

from smart_log_analyzer.io.report import ConsoleReporter
from smart_log_analyzer.core.models import (
    LogEntry,
    ErrorGroup,
    AnalysisResult,
)


def test_report_error_analysis(capsys: CaptureFixture[str]) -> None:
    # Arrange
    reporter = ConsoleReporter()

    results: Dict[str, AnalysisResult] = {
        "Error Analysis": cast(
            AnalysisResult,
            {
                "kind": "error",
                "total_errors": 2,
                "unique_errors": 1,
                "top_errors": [ErrorGroup(service="db", message="timeout", count=2)],
            },
        )
    }

    # Act
    reporter.report(results)
    out = capsys.readouterr().out

    # Assert
    assert "Total Errors: 2" in out
    assert "db: timeout" in out


def test_report_performance_analysis(capsys: CaptureFixture[str]) -> None:
    # Arrange
    reporter = ConsoleReporter()

    results: Dict[str, AnalysisResult] = {
        "Performance Analysis": cast(
            AnalysisResult,
            {
                "kind": "performance",
                "average_duration_ms": 100.0,
                "total_requests_with_duration": 1,
                "slowest_requests": [],
            },
        )
    }

    # Act
    reporter.report(results)
    out = capsys.readouterr().out

    # Assert
    assert "Average Duration: 100.0 ms" in out
    assert "Analyzed Requests: 1" in out


def test_report_ai_analysis(capsys: CaptureFixture[str]) -> None:
    # Arrange
    reporter = ConsoleReporter()

    results: Dict[str, AnalysisResult] = {
        "AI Insight Analysis": cast(
            AnalysisResult,
            {
                "kind": "ai",
                "top_error": None,
                "insight": "ok",
            },
        )
    }

    # Act
    reporter.report(results)
    out = capsys.readouterr().out

    # Assert
    assert "AI Insight:" in out
    assert "ok" in out


def test_report_performance_with_slowest_requests(
    capsys: CaptureFixture[str],
) -> None:
    # Arrange
    reporter = ConsoleReporter()

    slow = LogEntry(
        timestamp="2023",
        level="INFO",
        service="api",
        message="slow",
        duration_ms=500,
        request_id="req-1",
    )

    results: Dict[str, AnalysisResult] = {
        "Performance Analysis": cast(
            AnalysisResult,
            {
                "kind": "performance",
                "average_duration_ms": 500.0,
                "total_requests_with_duration": 1,
                "slowest_requests": [slow],
            },
        )
    }

    # Act
    reporter.report(results)
    out = capsys.readouterr().out

    # Assert
    assert "500ms | api | req-1" in out


def test_report_ai_with_top_error(capsys: CaptureFixture[str]) -> None:
    # Arrange
    reporter = ConsoleReporter()

    error = ErrorGroup(service="db", message="timeout", count=3)

    results: Dict[str, AnalysisResult] = {
        "AI Insight Analysis": cast(
            AnalysisResult,
            {
                "kind": "ai",
                "top_error": error,
                "insight": "fix it",
            },
        )
    }

    # Act
    reporter.report(results)
    out = capsys.readouterr().out

    # Assert
    assert "Top Error Analyzed" in out
    assert "timeout" in out
