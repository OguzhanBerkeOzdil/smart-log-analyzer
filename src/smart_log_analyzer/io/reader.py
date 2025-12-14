import json
import sys
from pathlib import Path
from typing import Iterator
from pydantic import ValidationError
from ..core.models import LogEntry


def read_log_file(path: Path) -> Iterator[LogEntry]:
    """
    Parse JSONL file into LogEntry objects.
    """
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                yield LogEntry(**data)
            except (json.JSONDecodeError, ValidationError):
                print(f"Line {line_num}: parse error, skipping", file=sys.stderr)
