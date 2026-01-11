# Core Module Documentation

The `core/` module contains all business logic for log analysis.

---

## 📄 models.py - Data Models

### Purpose

Defines all data structures used throughout the application using **Pydantic** for input validation and **TypedDict** for typed output.

### Classes

#### `LogEntry` (Pydantic BaseModel)

```python
class LogEntry(BaseModel):
    timestamp: str
    level: str
    service: str
    message: str
    duration_ms: Optional[int] = None
    request_id: Optional[str] = None
```

**Why Pydantic?**

- Automatic validation when parsing JSON
- Type coercion (e.g., string "100" → int 100)
- Clear error messages for invalid data

**Alternative**: `dataclasses` - lighter but no validation

#### `ErrorGroup` (Pydantic BaseModel)

```python
class ErrorGroup(BaseModel):
    service: str
    message: str
    count: int
```

Groups errors by service+message for aggregation.

#### Result TypedDicts

```python
class ErrorAnalysisResult(TypedDict):
    kind: Literal["error"]
    total_errors: int
    unique_errors: int
    top_errors: list[ErrorGroup]
```

**Why TypedDict instead of Pydantic?**

- Results are created internally, not from external input
- No validation needed (we control the data)
- Lighter memory footprint
- Native dict syntax (`result["key"]`)

**Union Type for Results**:

```python
AnalysisResult = Union[ErrorAnalysisResult, PerformanceAnalysisResult, AIAnalysisResult]
```

This allows the engine to handle all result types uniformly.

---

## 📄 interfaces.py - Strategy Interface

### Purpose

Defines the abstract contract for all analyzers using **ABC** (Abstract Base Class) and **Generics**.

### Code

```python
TResult = TypeVar("TResult", bound=AnalysisResult)

class AnalyzerStrategy(ABC, Generic[TResult]):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def analyze(self, logs: List[LogEntry]) -> TResult:
        pass
```

### Why Generics?

```python
class ErrorAnalyzer(AnalyzerStrategy[ErrorAnalysisResult]):
    def analyze(self, logs) -> ErrorAnalysisResult:  # ← Specific type!
        ...
```

Each analyzer declares its exact return type, enabling:

- IDE autocomplete
- Static type checking (mypy/pyright)
- Self-documenting code

**Alternative**: Return `Dict[str, Any]` - works but loses type safety

---

## 📄 strategies.py - Analysis Implementations

### ErrorAnalyzer

```python
def analyze(self, logs: List[LogEntry]) -> ErrorAnalysisResult:
    counts: Dict[Tuple[str, str], int] = defaultdict(int)
    for entry in logs:
        if entry.level == "ERROR":
            counts[(entry.service, entry.message)] += 1
    # ... create sorted groups
```

**Key Techniques**:

1. **`defaultdict(int)`** - Auto-initializes missing keys to 0
2. **Tuple as dict key** - Groups by (service, message) pair
3. **`sorted()` with `key=lambda`** - Functional sorting

**Why not Counter?**

```python
# Alternative with Counter:
from collections import Counter
counts = Counter((e.service, e.message) for e in logs if e.level == "ERROR")
```

Both work! Counter is more concise but less explicit for teaching.

### PerformanceAnalyzer

```python
def analyze(self, logs: List[LogEntry]) -> PerformanceAnalysisResult:
    with_duration = sorted(
        [e for e in logs if e.duration_ms is not None],
        key=lambda e: e.duration_ms or 0,
        reverse=True,
    )
```

**Key Techniques**:

1. **List comprehension with filter** - Pythonic filtering
2. **Inline sorting** - Combines filter + sort in one expression
3. **`or 0` fallback** - Type-safe handling of Optional

---

## 📄 ai_strategy.py - AI Integration

### Purpose

Integrates Google Gemini API for intelligent error explanations.

### Key Design Decisions

**Why separate from other strategies?**

```python
def analyze(self, logs: List[LogEntry]) -> AIAnalysisResult:
    raise RuntimeError("Use analyze_from_error_result()")
```

AIAnalyzer **cannot** work on raw logs - it needs `ErrorAnalyzer` results first. This explicit error prevents misuse.

**Alternative**: Chain analyzers automatically, but that hides dependencies.

### API Integration

```python
def _get_explanation(self, error: ErrorGroup) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "(!) AI features disabled: GEMINI_API_KEY not found."
    # ... API call
```

**Graceful degradation**: Missing API key doesn't crash - returns warning message.

---

## 📄 engine.py - Orchestrator

### Purpose

Coordinates all analyzers and manages execution flow.

### Code

```python
class AnalysisEngine:
    def __init__(self, enable_ai: bool = False):
        self.strategies: List[AnalyzerStrategy[Any]] = [
            ErrorAnalyzer(), 
            PerformanceAnalyzer()
        ]
        if enable_ai:
            self.strategies.append(AIAnalyzer())
```

**Why `Any` here?**

The engine holds different strategy types (`ErrorAnalyzer`, `PerformanceAnalyzer`, etc.). At this orchestration boundary, we lose specific types. This is intentional - the engine doesn't need to know specific result types.

### Strategy Registration

```python
def register_strategy(self, strategy: AnalyzerStrategy[Any]) -> None:
    self.strategies.append(strategy)
```

**Extensibility**: Add custom analyzers at runtime without modifying engine code.

### Execution Flow

```python
async def run(self, file_path: Path) -> Dict[str, AnalysisResult]:
    logs = await AsyncLogReader.read_file(file_path)
    
    for strategy in self.strategies:
        if isinstance(strategy, AIAnalyzer):
            # Special handling - needs error results
            results[strategy.name] = strategy.analyze_from_error_result(error_result)
        else:
            results[strategy.name] = strategy.analyze(logs)
```

**Why `isinstance` check?**

AIAnalyzer has a different interface (`analyze_from_error_result`). This keeps the Strategy Pattern clean while handling the special case.

**Alternative**: Visitor Pattern - more complex but eliminates isinstance checks.
