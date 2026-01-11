import json
from pathlib import Path
from typing import AsyncIterator
from pydantic import ValidationError
import aiofiles
from ..core.models import LogEntry


class AsyncLogReader:
    """
    Asynchronous log reader using aiofiles for non-blocking I/O.
    """

    @staticmethod
    async def read_file(path: Path) -> AsyncIterator[LogEntry]:  # Return type changes
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {path}")

        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            async for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    yield LogEntry(**data)  # Yield one item at a time
                except (json.JSONDecodeError, ValidationError):
                    continue
