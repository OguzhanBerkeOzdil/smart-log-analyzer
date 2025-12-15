import asyncio
from pathlib import Path
from typing import List, Dict, Any
from .models import LogEntry
from .interfaces import AnalyzerStrategy
from .strategies import ErrorAnalyzer, PerformanceAnalyzer
from .ai_strategy import AIAnalyzer
from ..io.async_reader import AsyncLogReader

class AnalysisEngine:
    """
    The core engine that orchestrates the log analysis process.
    Uses the Strategy Pattern to apply multiple analyzers.
    """
    
    def __init__(self, enable_ai: bool = False):
        self.strategies: List[AnalyzerStrategy] = [
            ErrorAnalyzer(),
            PerformanceAnalyzer()
        ]
        if enable_ai:
            self.strategies.append(AIAnalyzer())
    
    def register_strategy(self, strategy: AnalyzerStrategy) -> None:
        """Allows dynamic registration of new analysis strategies."""
        self.strategies.append(strategy)

    async def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Runs the full analysis pipeline asynchronously.
        """
        print(f"Reading logs from {file_path}...")
        logs = await AsyncLogReader.read_file(file_path)
        print(f"Successfully read {len(logs)} log entries.")
        
        results = {}
        
        # Run all strategies
        for strategy in self.strategies:
            print(f"Running {strategy.name}...")
            results[strategy.name] = strategy.analyze(logs)
            
        return results
