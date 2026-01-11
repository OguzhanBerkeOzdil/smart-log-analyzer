# Advanced Python Concepts - Exam Cheat Sheet

Quick reference for all advanced Python concepts used in this project.

---

## 🔷 Type Hints & Generics

### Basic Type Hints

```python
def analyze(self, logs: List[LogEntry]) -> ErrorAnalysisResult:
    pass
```

- `List[LogEntry]` - List containing LogEntry objects
- `-> ErrorAnalysisResult` - Return type annotation

### Optional Types

```python
duration_ms: Optional[int] = None  # Can be int or None
```

### Union Types

```python
AnalysisResult = Union[ErrorAnalysisResult, PerformanceAnalysisResult, AIAnalysisResult]
```

### Generic Types

```python
TResult = TypeVar("TResult", bound=AnalysisResult)

class AnalyzerStrategy(ABC, Generic[TResult]):
    def analyze(self, logs: List[LogEntry]) -> TResult:
        pass

# Usage - specifies concrete type:
class ErrorAnalyzer(AnalyzerStrategy[ErrorAnalysisResult]):
    pass
```

### Literal Types

```python
kind: Literal["error"]  # Can ONLY be the string "error"
```

---

## 🔷 Pydantic

### BaseModel

```python
class LogEntry(BaseModel):
    timestamp: str
    level: str
    duration_ms: Optional[int] = None  # Optional with default

# Auto-validates on creation:
entry = LogEntry(timestamp="2023", level="INFO")  # ✓
entry = LogEntry(timestamp="2023")  # ✗ ValidationError
```

### TypedDict (Alternative)

```python
class ErrorAnalysisResult(TypedDict):
    kind: Literal["error"]
    total_errors: int
```

- No validation
- Lighter than Pydantic
- Native dict access: `result["kind"]`

---

## 🔷 ABC (Abstract Base Class)

```python
from abc import ABC, abstractmethod

class AnalyzerStrategy(ABC):
    @abstractmethod
    def analyze(self, logs):
        pass  # No implementation

# Cannot instantiate ABC directly:
strategy = AnalyzerStrategy()  # ✗ TypeError

# Must implement all abstract methods:
class ErrorAnalyzer(AnalyzerStrategy):
    def analyze(self, logs):  # ✓ Implements abstract method
        return {"errors": []}
```

---

## 🔷 Async/Await

### Basic Async Function

```python
async def read_file(path: Path) -> List[LogEntry]:
    async with aiofiles.open(path) as f:
        async for line in f:
            yield process(line)
```

### Running Async Code

```python
import asyncio

async def main():
    result = await some_async_function()

asyncio.run(main())
```

### Why Async?

- Non-blocking I/O
- Other tasks run while waiting for file/network

---

## 🔷 Collections

### defaultdict

```python
from collections import defaultdict

counts = defaultdict(int)  # Missing keys default to 0
counts["new_key"] += 1     # No KeyError!
```

### Sorting

```python
# Sort by attribute
sorted(groups, key=lambda g: g.count, reverse=True)

# Sort in-place
groups.sort(key=lambda g: g.count, reverse=True)
```

---

## 🔷 Pattern Matching (Python 3.10+)

```python
match data["kind"]:
    case "error":
        handle_error(data)
    case "performance":
        handle_perf(data)
    case _:  # Default case
        raise ValueError("Unknown")
```

---

## 🔷 Walrus Operator `:=`

```python
# Assign AND use in same expression
if not (line := line.strip()):
    continue

# Equivalent to:
line = line.strip()
if not line:
    continue
```

---

## 🔷 Comprehensions

### List Comprehension

```python
errors = [e for e in logs if e.level == "ERROR"]
```

### Dict Comprehension

```python
counts = {k: v for k, v in items if v > 0}
```

### Generator Expression

```python
total = sum(e.duration_ms for e in logs if e.duration_ms)
```

---

## 🔷 Enums

```python
from enum import Enum

class LogLevel(str, Enum):  # str mixin for JSON serialization
    INFO = "INFO"
    ERROR = "ERROR"

# Usage:
level = LogLevel.INFO
level.value  # "INFO"
str(level)   # "INFO" (because of str mixin)
```

---

## 🔷 Decorators

### Property Decorator

```python
class Analyzer:
    @property
    def name(self) -> str:
        return "Error Analysis"

# Access like attribute, not method:
analyzer.name  # Not analyzer.name()
```

### Static Method

```python
class AsyncLogReader:
    @staticmethod
    async def read_file(path: Path):
        pass

# No self parameter, can call without instance:
AsyncLogReader.read_file(path)
```

---

## 🔷 Context Managers

```python
# File automatically closed after block:
with open(path) as f:
    data = f.read()

# Async version:
async with aiofiles.open(path) as f:
    data = await f.read()
```

---

## 🔷 Testing

### Fixtures

```python
@pytest.fixture
def sample_data():
    return [1, 2, 3]

def test_something(sample_data):  # Auto-injected!
    assert len(sample_data) == 3
```

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch("module.external_function")
def test_with_mock(mock_func):
    mock_func.return_value = "fake"
    result = code_that_calls_external_function()
    assert result == "fake"
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

---

## 🔷 F-Strings

```python
name = "Alice"
count = 42

# Basic
f"Hello {name}"  # "Hello Alice"

# Expressions
f"Count: {count * 2}"  # "Count: 84"

# Formatting
f"{3.14159:.2f}"  # "3.14"
```

---

## 🔷 Design Patterns in This Project

| Pattern | Where | Why |
| ------- | ----- | --- |
| Strategy | AnalyzerStrategy | Pluggable algorithms |
| Factory | AnalysisEngine | Creates strategies |
| Template | Report methods | Common structure, varying details |
