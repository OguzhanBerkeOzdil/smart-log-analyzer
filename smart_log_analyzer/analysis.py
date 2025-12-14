from collections import defaultdict
from .models import LogEntry, ErrorGroup


def group_errors(logs: list[LogEntry]) -> list[ErrorGroup]:
    """Group error entries by service and message, return sorted by count."""
    counts = defaultdict(int)
    
    for entry in logs:
        if entry.level == "ERROR":
            key = (entry.service, entry.message)
            counts[key] += 1
    
    groups = [
        ErrorGroup(service=service, message=message, count=count)
        for (service, message), count in counts.items()
    ]
    
    groups.sort(key=lambda g: g.count, reverse=True)
    return groups


def slow_requests(logs: list[LogEntry], limit: int = 10) -> list[LogEntry]:
    """Return the slowest requests by duration_ms."""
    with_duration = [entry for entry in logs if entry.duration_ms is not None]
    with_duration.sort(key=lambda e: e.duration_ms or 0, reverse=True)
    return with_duration[:limit]
