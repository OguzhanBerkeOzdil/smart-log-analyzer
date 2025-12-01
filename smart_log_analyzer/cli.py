import argparse
from pathlib import Path
from .reader import read_log_file
from .analysis import group_errors, slow_requests
from .report import format_report


def main():
    parser = argparse.ArgumentParser(description="Smart Log Analyzer")
    parser.add_argument("path", type=Path, help="Path to JSONL log file")
    parser.add_argument("--limit", type=int, default=10, help="Number of slow requests to show")
    
    args = parser.parse_args()
    
    logs = read_log_file(args.path)
    error_groups = group_errors(logs)
    slow_reqs = slow_requests(logs, limit=args.limit)
    
    report = format_report(error_groups, slow_reqs)
    print(report)


if __name__ == "__main__":
    main()
