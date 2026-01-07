import json
from pathlib import Path
from typing import List
from pydantic import ValidationError
import aiofiles
from ..core.models import LogEntry


class AsyncLogReader:
    """
    Asynchronous log reader using aiofiles for non-blocking I/O.
    """

    @staticmethod
    async def read_file(path: Path) -> List[LogEntry]:
        logs: List[LogEntry] = []
        
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {path}")

        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            async for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parsing is CPU-bound, but for simplicity we do it here.
                    # In very high load, we might offload to a process pool.
                    data = json.loads(line)
                    logs.append(LogEntry(**data))
                except (json.JSONDecodeError, ValidationError):
                    # In a real app, we might log this to a separate error file
                    continue

        return logs
