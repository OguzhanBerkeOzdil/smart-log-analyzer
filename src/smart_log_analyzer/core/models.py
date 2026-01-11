from typing import Optional, TypedDict, Literal, Union
from pydantic import BaseModel


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


class ErrorAnalysisResult(TypedDict):
    kind: Literal["error"]
    total_errors: int
    unique_errors: int
    top_errors: list[ErrorGroup]


class PerformanceAnalysisResult(TypedDict):
    kind: Literal["performance"]
    average_duration_ms: float
    total_requests_with_duration: int
    slowest_requests: list[LogEntry]


class AIAnalysisResult(TypedDict):
    kind: Literal["ai"]
    top_error: Optional[ErrorGroup]
    insight: str


AnalysisResult = Union[
    ErrorAnalysisResult,
    PerformanceAnalysisResult,
    AIAnalysisResult,
]
