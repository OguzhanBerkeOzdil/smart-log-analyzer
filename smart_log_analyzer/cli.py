import argparse
import sys  # <--- Added to handle exit codes if needed
from pathlib import Path
from .reader import read_log_file
from .analysis import group_errors, slow_requests
from .report import format_report
from .ai_insight import get_error_explanation  # <--- Import the new function


def main():
    parser = argparse.ArgumentParser(description="Smart Log Analyzer")
    parser.add_argument("path", type=Path, help="Path to JSONL log file")
    parser.add_argument("--limit", type=int, default=10, help="Number of slow requests to show")
    parser.add_argument("--ai", action="store_true", help="Ask AI to explain the top error") # <--- New Flag
    
    args = parser.parse_args()
    
    logs = read_log_file(args.path)
    error_groups = group_errors(logs)
    slow_reqs = slow_requests(logs, limit=args.limit)
    
    report = format_report(error_groups, slow_reqs)
    print(report)

    # --- New AI Section ---
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