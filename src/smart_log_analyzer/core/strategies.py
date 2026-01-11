import heapq
from collections import defaultdict
from typing import AsyncIterable, Dict, Tuple, List
from .models import LogEntry, ErrorGroup, ErrorAnalysisResult, PerformanceAnalysisResult
from .interfaces import AnalyzerStrategy


class ErrorAnalyzer(AnalyzerStrategy[ErrorAnalysisResult]):
    """Groups and counts error logs."""

    @property
    def name(self) -> str:
        return "Error Analysis"

    async def analyze(self, logs: AsyncIterable[LogEntry]) -> ErrorAnalysisResult:
        counts: Dict[Tuple[str, str], int] = defaultdict(int)

        async for entry in logs:
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

    async def analyze(self, logs: AsyncIterable[LogEntry]) -> PerformanceAnalysisResult:
        heap: List[Tuple[int, int, LogEntry]] = []
        total_duration = 0.0
        count = 0
        tie_breaker = 0

        async for entry in logs:
            if entry.duration_ms is not None:
                count += 1
                total_duration += entry.duration_ms
                tie_breaker += 1

                item = (entry.duration_ms, tie_breaker, entry)
                if len(heap) < 10:
                    heapq.heappush(heap, item)
                else:
                    heapq.heappushpop(heap, item)

        if count == 0:
            return {
                "kind": "performance",
                "average_duration_ms": 0.0,
                "total_requests_with_duration": 0,
                "slowest_requests": [],
            }

        slowest_sorted = [
            item[2] for item in sorted(heap, key=lambda x: x[0], reverse=True)
        ]

        return {
            "kind": "performance",
            "slowest_requests": slowest_sorted,
            "average_duration_ms": round(total_duration / count, 2),
            "total_requests_with_duration": count,
        }
