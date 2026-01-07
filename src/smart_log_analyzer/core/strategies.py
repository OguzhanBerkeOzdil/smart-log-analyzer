from collections import defaultdict
from typing import List, Dict, Any, Tuple
from .models import LogEntry, ErrorGroup, ErrorAnalysisResult, PerformanceAnalysisResult
from .interfaces import AnalyzerStrategy


class ErrorAnalyzer(AnalyzerStrategy[ErrorAnalysisResult]):
    """
    Analyzes logs to group and count errors.
    """

    @property
    def name(self) -> str:
        return "Error Analysis"

    def analyze(self, logs: List[LogEntry]) -> ErrorAnalysisResult:
        counts: Dict[Tuple[str, str], int] = defaultdict(int)

        for entry in logs:
            if entry.level == "ERROR":
                key = (entry.service, entry.message)
                counts[key] += 1

        groups = [
            ErrorGroup(service=service, message=message, count=count)
            for (service, message), count in counts.items()
        ]

        # Sort by count descending
        groups.sort(key=lambda g: g.count, reverse=True)

        return {
            "kind": "error",
            "total_errors": sum(g.count for g in groups),
            "unique_errors": len(groups),
            "top_errors": groups,
        }


class PerformanceAnalyzer(AnalyzerStrategy[PerformanceAnalysisResult]):
    """
    Analyzes logs to find slow requests and performance anomalies.
    """

    @property
    def name(self) -> str:
        return "Performance Analysis"

    def analyze(self, logs: List[LogEntry]) -> PerformanceAnalysisResult:
        with_duration = [e for e in logs if e.duration_ms is not None]

        if not with_duration:
            return {
                "kind": "performance",
                "average_duration_ms": 0.0,
                "total_requests_with_duration": 0,
                "slowest_requests": [],
            }

        # Sort by duration descending
        with_duration.sort(key=lambda e: e.duration_ms or 0, reverse=True)

        total_duration = sum(e.duration_ms or 0 for e in with_duration)
        avg_duration = total_duration / len(with_duration)

        return {
            "kind": "performance",
            "slowest_requests": with_duration[:10],
            "average_duration_ms": round(avg_duration, 2),
            "total_requests_with_duration": len(with_duration),
        }