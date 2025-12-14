from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    timestamp: str
    level: str
    service: str
    message: str
    duration_ms: Optional[int] = None
    request_id: Optional[str] = None


class ErrorGroup(BaseModel):
    service: str
    message: str
    count: int
