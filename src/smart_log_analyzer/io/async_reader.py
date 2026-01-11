import json
from pathlib import Path
from typing import AsyncIterator
from pydantic import ValidationError
import aiofiles
from ..core.models import LogEntry


class AsyncLogReader:
    """Async log reader using aiofiles for non-blocking I/O."""

    @staticmethod
    async def read_file(path: Path) -> AsyncIterator[LogEntry]:
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {path}")

        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            async for line in f:
                if not (line := line.strip()):
                    continue
                try:
                    yield LogEntry(**json.loads(line))
                except (json.JSONDecodeError, ValidationError):
                    continue
