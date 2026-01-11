# Smart Log Analyzer - Architecture Overview

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    (CLI Entry Point)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AnalysisEngine                           │
│              (Orchestrator - Strategy Pattern)              │
└──────┬──────────────┬──────────────────┬────────────────────┘
       │              │                  │
       ▼              ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ ErrorAnalyzer│ │ Performance  │ │  AIAnalyzer  │
│              │ │   Analyzer   │ │  (Optional)  │
└──────────────┘ └──────────────┘ └──────────────┘
       │              │                  │
       └──────────────┴──────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   ConsoleReporter                           │
│                  (Output Formatter)                         │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Design Patterns Used

### 1. **Strategy Pattern** (Core Architecture)
- **Why**: Allows adding new analyzers without modifying existing code (Open/Closed Principle)
- **How**: `AnalyzerStrategy` abstract base class with `analyze()` method
- **Benefit**: Exam-friendly! Easy to explain: "New analyzer = new class implementing interface"

### 2. **TypedDict for Results** (Type Safety)
- **Why**: Strict typing for analysis results without runtime overhead
- **Alternative**: Could use Pydantic models, but TypedDict is lighter for simple data transfer

### 3. **Generic Types** (`TResult`)
- **Why**: Each strategy returns its own typed result while sharing interface
- **How**: `AnalyzerStrategy[TResult]` where `TResult` is bound to `AnalysisResult`

## 📁 Project Structure

```
smart_log_analyzer/
├── main.py          # Entry point, CLI parsing
├── core/            # Business logic
│   ├── models.py    # Data models (Pydantic + TypedDict)
│   ├── interfaces.py# Abstract Strategy interface
│   ├── strategies.py# Error & Performance analyzers
│   ├── ai_strategy.py# AI-powered analysis
│   └── engine.py    # Orchestrator
├── io/              # Input/Output
│   ├── async_reader.py # Async JSONL parsing
│   └── report.py    # Console output formatting
└── utils/           # Helpers
    └── generator.py # Synthetic log generation
```

## 🔄 Data Flow

1. **Input**: JSONL file → `AsyncLogReader` → `List[LogEntry]`
2. **Process**: `AnalysisEngine` runs each strategy sequentially
3. **Output**: `ConsoleReporter` formats and prints results

## ❓ Why These Choices?

| Decision | Reason | Alternative |
|----------|--------|-------------|
| `asyncio` + `aiofiles` | Non-blocking I/O for large files | Sync I/O (simpler but blocks) |
| `Pydantic` models | Validation + serialization | `dataclasses` (no validation) |
| `TypedDict` results | Lightweight, typed dicts | Pydantic (heavier) |
| Strategy Pattern | Extensibility | Simple if/else (not scalable) |
| JSONL format | Line-by-line streaming | JSON array (must load all) |
