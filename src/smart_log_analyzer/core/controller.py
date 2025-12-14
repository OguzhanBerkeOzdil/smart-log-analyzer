from pathlib import Path
from .analysis import group_errors, slow_requests
from .models import ErrorGroup
from ..io.reader import read_log_file
from ..io.report import format_report


def run_analysis(log_path: Path, limit: int) -> tuple[str, list[ErrorGroup]]:
    """
    Orchestrates the log analysis workflow.
    Reads the log file, analyzes it, and formats the report.
    """
    logs = read_log_file(log_path)
    error_groups = group_errors(logs)
    slow_reqs = slow_requests(logs, limit=limit)

    return format_report(error_groups, slow_reqs), error_groups
