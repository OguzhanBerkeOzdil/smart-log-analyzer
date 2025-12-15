from typing import Dict, Any


class ConsoleReporter:
    """
    Reports analysis results to the console.
    """

    def report(self, results: Dict[str, Any]) -> None:
        print("\n" + "=" * 60)
        print("SMART LOG ANALYZER REPORT")
        print("=" * 60)

        for strategy_name, data in results.items():
            print(f"\n--- {strategy_name} ---")

            if strategy_name == "Error Analysis":
                print(f"Total Errors: {data['total_errors']}")
                print(f"Unique Errors: {data['unique_errors']}")
                print("\nTop Recurring Errors:")
                for i, group in enumerate(data["top_errors"][:5], 1):
                    print(f"  {i}. [{group.count}x] {group.service}: {group.message}")

            elif strategy_name == "Performance Analysis":
                print(f"Average Duration: {data['average_duration_ms']} ms")
                print(f"Analyzed Requests: {data['total_requests_with_duration']}")
                print("\nSlowest Requests:")
                for i, req in enumerate(data["slowest_requests"], 1):
                    print(
                        f"  {i}. {req.duration_ms}ms | {req.service} | {req.request_id}"
                    )

            elif strategy_name == "AI Insight Analysis":
                print(f"\nTop Error Analyzed: {data['top_error_analyzed'].message}")
                print(f"AI Insight:\n{data['ai_insight']}")

            else:
                # Fallback for unknown strategies
                print(data)

        print("\n" + "=" * 60)
