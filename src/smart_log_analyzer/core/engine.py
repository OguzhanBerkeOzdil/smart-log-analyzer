from pathlib import Path
from typing import List, Dict, Any
from .models import AnalysisResult
from .interfaces import AnalyzerStrategy
from .strategies import ErrorAnalyzer, PerformanceAnalyzer
from .ai_strategy import AIAnalyzer
from ..io.async_reader import AsyncLogReader


class AnalysisEngine:
    """
    The core engine that orchestrates the log analysis process.
    Uses the Strategy Pattern to apply multiple analyzers.

    NOTE:
    AnalyzerStrategy is generic over different result types.
    The engine holds heterogeneous strategies, so `Any` is used
    intentionally at this orchestration boundary.
    """

    def __init__(self, enable_ai: bool = False):
        self.strategies: List[AnalyzerStrategy[Any]] = [
            ErrorAnalyzer(),
            PerformanceAnalyzer(),
        ]
        if enable_ai:
            self.strategies.append(AIAnalyzer())

    def register_strategy(self, strategy: AnalyzerStrategy[Any]) -> None:
        """Allows dynamic registration of new analysis strategies."""
        self.strategies.append(strategy)

    async def run(self, file_path: Path) -> Dict[str, AnalysisResult]:
        print(f"Reading logs from {file_path}...")
        logs = await AsyncLogReader.read_file(file_path)
        print(f"Successfully read {len(logs)} log entries.")

        results: Dict[str, AnalysisResult] = {}
        error_result = None

        for strategy in self.strategies:
            print(f"Running {strategy.name}...")

            if isinstance(strategy, ErrorAnalyzer):
                error_result = strategy.analyze(logs)
                results[strategy.name] = error_result

            elif isinstance(strategy, AIAnalyzer):
                if error_result is None:
                    raise RuntimeError(
                        "AIAnalyzer requires ErrorAnalyzer to run first"
                    )
                results[strategy.name] = strategy.analyze_from_error_result(
                    error_result
                )

            else:
                results[strategy.name] = strategy.analyze(logs)

        return results