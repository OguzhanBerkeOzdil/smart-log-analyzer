from abc import ABC, abstractmethod
from typing import AsyncIterable, TypeVar, Generic
from .models import LogEntry

TResult = TypeVar("TResult")


class AnalyzerStrategy(ABC, Generic[TResult]):
    """Abstract Base Class for pluggable analysis strategies (Strategy Pattern)."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def analyze(self, logs: AsyncIterable[LogEntry]) -> TResult: ...
