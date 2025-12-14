from .models import LogEntry, ErrorGroup


def format_report(error_groups: list[ErrorGroup], slow_reqs: list[LogEntry]) -> str:
    """Format analysis results as plain text report."""
    lines = []
    lines.append("Smart Log Analyzer Report")
    lines.append("=" * 50)
    lines.append("")
    
    lines.append("Top error groups:")
    if error_groups:
        for group in error_groups:
            lines.append(f"  - {group.service} | \"{group.message}\" | {group.count} occurrences")
    else:
        lines.append("  (no errors found)")
    
    lines.append("")
    lines.append("Slowest requests:")
    if slow_reqs:
        for entry in slow_reqs:
            req_id = entry.request_id or "(no id)"
            lines.append(f"  - {entry.duration_ms} ms | {entry.service} | {entry.message} | {req_id}")
    else:
        lines.append("  (no requests with duration found)")
    
    lines.append("")
    return "\n".join(lines)
