from collections import defaultdict
from typing import List, Dict, Tuple
from .models import LogEntry, ErrorGroup, ErrorAnalysisResult, PerformanceAnalysisResult
from .interfaces import AnalyzerStrategy


class ErrorAnalyzer(AnalyzerStrategy[ErrorAnalysisResult]):
    """Groups and counts error logs."""

    @property
    def name(self) -> str:
        return "Error Analysis"

    def analyze(self, logs: List[LogEntry]) -> ErrorAnalysisResult:
        counts: Dict[Tuple[str, str], int] = defaultdict(int)
        for entry in logs:
            if entry.level == "ERROR":
                counts[(entry.service, entry.message)] += 1

        groups = sorted(
            [ErrorGroup(service=s, message=m, count=c) for (s, m), c in counts.items()],
            key=lambda g: g.count,
            reverse=True,
        )
        return {
            "kind": "error",
            "total_errors": sum(g.count for g in groups),
            "unique_errors": len(groups),
            "top_errors": groups,
        }


class PerformanceAnalyzer(AnalyzerStrategy[PerformanceAnalysisResult]):
    """Finds slow requests and performance anomalies."""

    @property
    def name(self) -> str:
        return "Performance Analysis"

    def analyze(self, logs: List[LogEntry]) -> PerformanceAnalysisResult:
        if not (with_duration := [e for e in logs if e.duration_ms is not None]):
            return {
                "kind": "performance",
                "average_duration_ms": 0.0,
                "total_requests_with_duration": 0,
                "slowest_requests": [],
            }

        with_duration.sort(key=lambda e: e.duration_ms or 0, reverse=True)
        avg = sum(e.duration_ms or 0 for e in with_duration) / len(with_duration)

        return {
            "kind": "performance",
            "slowest_requests": with_duration[:10],
            "average_duration_ms": round(avg, 2),
            "total_requests_with_duration": len(with_duration),
        }
