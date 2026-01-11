import asyncio
from pathlib import Path
from typing import List, Dict, Any
from .models import AnalysisResult
from .interfaces import AnalyzerStrategy
from .strategies import ErrorAnalyzer, PerformanceAnalyzer
from .ai_strategy import AIAnalyzer
from ..io.async_reader import AsyncLogReader


class AnalysisEngine:
    """Orchestrates log analysis using the Strategy Pattern."""

    def __init__(self, enable_ai: bool = False):
        self.strategies: List[AnalyzerStrategy[Any]] = [
            ErrorAnalyzer(),
            PerformanceAnalyzer(),
        ]
        if enable_ai:
            self.strategies.append(AIAnalyzer())

    def register_strategy(self, strategy: AnalyzerStrategy[Any]) -> None:
        self.strategies.append(strategy)

    async def run(self, file_path: Path) -> Dict[str, AnalysisResult]:
        print(f"Reading logs from {file_path}...")

        results: Dict[str, AnalysisResult] = {}
        strategies_to_run = [
            s for s in self.strategies if not isinstance(s, AIAnalyzer)
        ]

        print(f"Streaming logs to {len(strategies_to_run)} strategies...")

        futures = {
            s.name: s.analyze(AsyncLogReader.read_file(file_path))
            for s in strategies_to_run
        }

        computed_results = await asyncio.gather(*futures.values())

        for strategy, result in zip(strategies_to_run, computed_results):
            results[strategy.name] = result

        error_result = results.get("Error Analysis")
        ai_strategy = next(
            (s for s in self.strategies if isinstance(s, AIAnalyzer)), None
        )

        if ai_strategy and error_result and error_result["kind"] == "error":
            print(f"Running {ai_strategy.name}...")
            results[ai_strategy.name] = ai_strategy.analyze_from_error_result(
                error_result
            )

        return results
