from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .models import LogEntry

class AnalyzerStrategy(ABC):
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
    def analyze(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """
        Performs analysis on the provided logs.
        Returns a dictionary containing the results.
        """
        pass
