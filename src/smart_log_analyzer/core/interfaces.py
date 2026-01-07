from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from .models import LogEntry

# Generic type for analyzer results.
# Allows each AnalyzerStrategy to declare its own precise return type
# instead of falling back to Dict[str, Any), enabling strict type checking.
TResult = TypeVar("TResult")


class AnalyzerStrategy(ABC, Generic[TResult]):
    """
    Abstract Base Class for all analysis strategies.
    Follows the Strategy Pattern to allow pluggable analysis modules.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the analyzer."""
        pass

    @abstractmethod
    def analyze(self, logs: List[LogEntry]) -> TResult:
        """
        Performs analysis on the provided logs.
        Returns a dictionary containing the results.
        """
        pass
