# I/O Module Documentation

The `io/` module handles all input/output operations.

---

## 📄 async_reader.py - Asynchronous Log Reader

### What It Does

Reads JSONL (JSON Lines) files asynchronously using `aiofiles`.

### Code

```python
class AsyncLogReader:
    @staticmethod
    async def read_file(path: Path) -> List[LogEntry]:
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {path}")

        logs: List[LogEntry] = []
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            async for line in f:
                if not (line := line.strip()):
                    continue
                try:
                    logs.append(LogEntry(**json.loads(line)))
                except (json.JSONDecodeError, ValidationError):
                    continue
        return logs
```

### Why Async?

| Aspect | Sync I/O | Async I/O |
| ------ | -------- | --------- |
| Large files | Blocks entire program | Other tasks can run |
| Memory | Load all at once | Stream line-by-line |
| Complexity | Simple | Requires async/await |

For this project, async prepares for future scalability (multiple files, network sources).

### Key Techniques

**Walrus Operator (`:=`)**

```python
if not (line := line.strip()):
    continue
```

Assigns AND checks in one line. Equivalent to:

```python
line = line.strip()
if not line:
    continue
```

**Silent Error Handling**

```python
except (json.JSONDecodeError, ValidationError):
    continue  # Skip bad lines
```

In production, you might log these errors. Here, we gracefully skip invalid data.

### Alternative Approaches

**Sync version** (simpler but blocks):

```python
def read_file_sync(path: Path) -> List[LogEntry]:
    with open(path) as f:
        return [LogEntry(**json.loads(line)) for line in f if line.strip()]
```

**Generator version** (memory efficient):

```python
async def read_file_generator(path: Path):
    async with aiofiles.open(path) as f:
        async for line in f:
            yield LogEntry(**json.loads(line.strip()))
```

---

## 📄 report.py - Console Reporter

### What It Does

Formats analysis results for human-readable console output.

### Code

```python
class ConsoleReporter:
    def report(self, results: Dict[str, AnalysisResult]) -> None:
        for name, data in results.items():
            print(f"\n--- {name} ---")
            match data["kind"]:
                case "error":
                    self._report_error(data)
                case "performance":
                    self._report_performance(data)
                case "ai":
                    self._report_ai(data)
        print("\n" + "=" * 60)
```

### Key Techniques

**Structural Pattern Matching (Python 3.10+)**

```python
match data["kind"]:
    case "error":
        self._report_error(data)
```

This is cleaner than if/elif chains:

```python
# Old way:
if data["kind"] == "error":
    self._report_error(data)
elif data["kind"] == "performance":
    self._report_performance(data)
```

**Private Methods (`_prefix`)**

```python
def _report_error(self, data: ErrorAnalysisResult) -> None:
```

The underscore signals "internal use only" - not part of public API.

### Alternative Implementations

**Dictionary dispatch** (no match statement):

```python
handlers = {
    "error": self._report_error,
    "performance": self._report_performance,
    "ai": self._report_ai,
}
handlers[data["kind"]](data)
```

**Rich library** (prettier output):

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Error Analysis")
table.add_column("Service")
table.add_column("Count")
# ...
console.print(table)
```

### Why Separate Reporter Class?

**Single Responsibility Principle**: Engine analyzes, Reporter displays. This allows:

- Adding JSON output without changing analysis
- Testing analysis without console output
- Swapping reporters (console, file, HTML)
