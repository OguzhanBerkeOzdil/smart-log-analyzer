import json
import sys
from pathlib import Path
from pydantic import ValidationError
from .models import LogEntry


def read_log_file(path: Path) -> list[LogEntry]:
    """Parse JSONL file into LogEntry objects."""
    entries = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                entry = LogEntry(**data)
                entries.append(entry)
            except (json.JSONDecodeError, ValidationError) as e:
                print(f"Line {line_num}: parse error, skipping", file=sys.stderr)
    
    return entries
