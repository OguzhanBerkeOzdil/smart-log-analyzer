from typing import Dict
from ..core.models import (
    ErrorAnalysisResult,
    PerformanceAnalysisResult,
    AIAnalysisResult,
    AnalysisResult,
)


class ConsoleReporter:
    """Reports analysis results to the console."""

    def report(self, results: Dict[str, AnalysisResult]) -> None:
        for strategy_name, data in results.items():
            print(f"\n--- {strategy_name} ---")
            match data["kind"]:
                case "error":
                    self._report_error_analysis(data)
                case "performance":
                    self._report_performance_analysis(data)
                case "ai":
                    self._report_ai_analysis(data)
                case _:
                    raise ValueError(f"Unknown analysis kind: {data['kind']}")
        print("\n" + "=" * 60)

    def _report_error_analysis(self, data: ErrorAnalysisResult) -> None:
        print(f"Total Errors: {data['total_errors']}")
        print(f"Unique Errors: {data['unique_errors']}")
        print("\nTop Recurring Errors:")

        for i, group in enumerate(data["top_errors"][:5], 1):
            print(f"  {i}. [{group.count}x] {group.service}: {group.message}")

    def _report_performance_analysis(self, data: PerformanceAnalysisResult) -> None:
        print(f"Average Duration: {data['average_duration_ms']} ms")
        print(f"Analyzed Requests: {data['total_requests_with_duration']}")
        print("\nSlowest Requests:")

        for i, req in enumerate(data["slowest_requests"], 1):
            print(f"  {i}. {req.duration_ms}ms | {req.service} | {req.request_id}")

    def _report_ai_analysis(self, data: AIAnalysisResult) -> None:
        if data["top_error"] is not None:
            print(f"\nTop Error Analyzed: {data['top_error'].message}")

        print(f"AI Insight:\n{data['insight']}")
