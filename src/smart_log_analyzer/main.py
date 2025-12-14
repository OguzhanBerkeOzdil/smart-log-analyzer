import argparse
import sys
from pathlib import Path
from .core.controller import run_analysis
from .io.ai_insight import get_error_explanation


def get_parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Log Analyzer")
    parser.add_argument("path", type=Path, help="Path to JSONL log file")
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of slow requests to show"
    )
    parser.add_argument(
        "--ai", action="store_true", help="Ask AI to explain the top error"
    )
    return parser.parse_args()


def main() -> None:
    args = get_parser_args()

    report, error_groups = run_analysis(args.path, limit=args.limit)

    print(report)

    if args.ai:
        print("\nAsking AI for insights on the top error...")
        if not error_groups:
            print("No errors found to analyze.")
        else:
            top_error = error_groups[0]
            explanation = get_error_explanation(top_error)
            print("-" * 50)
            print(f"AI Insight for: {top_error.message}")
            print(explanation)
            print("-" * 50)


if __name__ == "__main__":
    main()
