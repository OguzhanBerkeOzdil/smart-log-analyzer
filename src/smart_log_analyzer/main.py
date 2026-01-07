import asyncio
import argparse
from pathlib import Path
from .core.engine import AnalysisEngine
from .utils.generator import LogGenerator
from .io.report import ConsoleReporter


def get_parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Log Analyzer (Async & Modular)")
    parser.add_argument("path", type=Path, nargs="?", help="Path to JSONL log file")
    parser.add_argument(
        "--generate", action="store_true", help="Generate synthetic logs"
    )
    parser.add_argument(
        "--count", type=int, default=1000, help="Number of logs to generate"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/synthetic_logs.jsonl"),
        help="Output path for generated logs",
    )
    parser.add_argument("--ai", action="store_true", help="Enable AI insights")
    return parser.parse_args()


async def async_main() -> None:
    args = get_parser_args()
    path = args.path

    # 1. Generate Logs if requested
    if args.generate:
        LogGenerator(args.output, count=args.count).generate()
        path = path or args.output

    if not path:
        print("Error: No log file provided and --generate not used.")
        print("Usage: python -m smart_log_analyzer.main <path_to_logs> OR --generate")
        return

    # 2. Run Analysis Engine
    results = await AnalysisEngine(enable_ai=args.ai).run(path)

    # 3. Report Results
    ConsoleReporter().report(results)


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")


if __name__ == "__main__":
    main()
