from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from .models import LogEntry

TResult = TypeVar("TResult")


class AnalyzerStrategy(ABC, Generic[TResult]):
    """Abstract Base Class for pluggable analysis strategies (Strategy Pattern)."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def analyze(self, logs: List[LogEntry]) -> TResult: ...
