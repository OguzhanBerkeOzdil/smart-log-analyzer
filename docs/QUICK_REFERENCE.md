# Quick Reference Card

## 🚀 Run Commands

```bash
# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Analyze logs
python -m smart_log_analyzer.main data/sample_logs.jsonl

# With AI insights
python -m smart_log_analyzer.main data/sample_logs.jsonl --ai

# Generate synthetic logs
python -m smart_log_analyzer.main --generate --count 500

# Run tests
uv run pytest -v
```

## 📁 File Purposes

| File | One-Line Purpose |
| ---- | ---------------- |
| `main.py` | CLI entry point, argument parsing |
| `models.py` | Data structures (LogEntry, results) |
| `interfaces.py` | Abstract Strategy interface |
| `strategies.py` | Error & Performance analyzers |
| `ai_strategy.py` | Google Gemini integration |
| `engine.py` | Orchestrates all analyzers |
| `async_reader.py` | Async JSONL file reader |
| `report.py` | Console output formatting |
| `generator.py` | Synthetic log creation |

## 🎯 Key Design Decisions

| What | Why |
| ---- | --- |
| Strategy Pattern | Add analyzers without changing engine |
| Pydantic | Auto-validation of input data |
| TypedDict | Lightweight typed results |
| Async I/O | Non-blocking file reading |
| Generics | Type-safe strategy returns |

## 📝 Code Patterns to Remember

### Strategy Interface

```python
class AnalyzerStrategy(ABC, Generic[TResult]):
    @abstractmethod
    def analyze(self, logs: List[LogEntry]) -> TResult:
        pass
```

### Error Counting

```python
counts = defaultdict(int)
for entry in logs:
    if entry.level == "ERROR":
        counts[(entry.service, entry.message)] += 1
```

### Sorted Results

```python
sorted(items, key=lambda x: x.count, reverse=True)
```

### Pattern Matching

```python
match data["kind"]:
    case "error": handle_error(data)
    case "performance": handle_perf(data)
```

### Async File Reading

```python
async with aiofiles.open(path) as f:
    async for line in f:
        process(line)
```

## ⚡ Exam Tips

1. **Strategy Pattern**: "New analyzer = new class, no engine changes"
2. **Generics**: "Each strategy knows its exact return type"
3. **TypedDict vs Pydantic**: "TypedDict for output, Pydantic for input"
4. **Async**: "Non-blocking I/O for scalability"
5. **Match statement**: "Cleaner than if/elif chains"
