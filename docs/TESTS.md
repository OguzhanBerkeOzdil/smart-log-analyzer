# Tests Documentation

This project follows **pytest** conventions with separate unit and integration tests.

---

## 📁 Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
│   ├── test_analysis.py # Strategy tests
│   └── test_ai.py       # AI mocking tests
└── integration/         # Tests with real I/O
    └── test_reader.py   # File reading tests
```

---

## 📄 conftest.py - Shared Fixtures

### What Are Fixtures?

Reusable test data/setup provided by pytest.

```python
@pytest.fixture
def sample_logs() -> list[LogEntry]:
    return [
        LogEntry(timestamp="2023-01-01", level="INFO", service="api", message="Health check", duration_ms=10),
        LogEntry(timestamp="2023-01-01", level="ERROR", service="db", message="Connection timeout"),
        # ...
    ]
```

### How Fixtures Work

```python
# Test function receives fixture by name
def test_error_aggregation(sample_logs: list[LogEntry]) -> None:
    result = ErrorAnalyzer().analyze(sample_logs)
    # sample_logs is automatically injected!
```

**Why `conftest.py`?**

- Pytest auto-discovers it
- Fixtures available to all tests in directory
- No imports needed

---

## 📄 test_analysis.py - Unit Tests

### Testing ErrorAnalyzer

```python
def test_error_aggregation(sample_logs: list[LogEntry]) -> None:
    result = ErrorAnalyzer().analyze(sample_logs)
    groups = result["top_errors"]

    assert len(groups) == 2
    assert groups[0].service == "db" and groups[0].count == 2
    assert groups[1].service == "auth" and groups[1].count == 1
```

**What It Tests**:

1. Groups errors correctly
2. Counts duplicates
3. Sorts by count (descending)

### Testing PerformanceAnalyzer

```python
def test_slow_requests_sorted(sample_logs: list[LogEntry]) -> None:
    result = PerformanceAnalyzer().analyze(sample_logs)
    slow = result["slowest_requests"]

    assert len(slow) == 2
    assert slow[0].duration_ms == 5000  # Slowest first
    assert slow[1].duration_ms == 10
```

**What It Tests**:

1. Filters logs with duration
2. Sorts by duration (descending)
3. Respects limit (max 10)

---

## 📄 test_ai.py - Mocking External APIs

### Why Mock?

- Tests should be **fast** (no network calls)
- Tests should be **reliable** (no API quota issues)
- Tests should be **free** (no API costs)

### Using unittest.mock

```python
@patch("google.genai.Client")
@patch("os.getenv")
def test_ai_explanation_success(
    mock_getenv: MagicMock, mock_client_class: MagicMock, sample_error_group: ErrorGroup
) -> None:
    # Setup mocks
    mock_getenv.return_value = "FAKE_API_KEY"
    mock_response = MagicMock(text="Try restarting the database.")
    mock_client_class.return_value.models.generate_content.return_value = mock_response

    # Run test
    result = AIAnalyzer()._get_explanation(sample_error_group)

    # Verify
    assert result == "Try restarting the database."
```

**How `@patch` Works**:

1. Replaces target with `MagicMock`
2. MagicMock accepts any method call
3. We configure return values
4. After test, originals are restored

### Testing Graceful Degradation

```python
def test_ai_disabled_without_key(sample_error_group: ErrorGroup) -> None:
    with patch("os.getenv", return_value=None):
        result = AIAnalyzer()._get_explanation(sample_error_group)
    assert "disabled" in result
```

Ensures app doesn't crash without API key.

---

## 📄 test_reader.py - Integration Tests

### Why Integration Tests?

Unit tests mock everything. Integration tests use real resources (files, databases).

```python
@pytest.mark.asyncio
async def test_read_valid_log_file(tmp_path: Path) -> None:
    # Create real file
    log_file = tmp_path / "test.jsonl"
    log_file.write_text('{"timestamp":"2023","level":"INFO","service":"test","message":"hi"}')

    # Read with real async I/O
    entries = await AsyncLogReader.read_file(log_file)

    assert len(entries) == 1
```

**`tmp_path` Fixture**:

- Pytest built-in
- Creates temporary directory
- Auto-cleaned after test

**`@pytest.mark.asyncio`**:

- Required for async test functions
- Provided by `pytest-asyncio` plugin

---

## 🧪 Running Tests

### All Tests

```bash
uv run pytest
```

### With Verbose Output

```bash
uv run pytest -v
```

### Specific File

```bash
uv run pytest tests/unit/test_analysis.py
```

### Specific Test

```bash
uv run pytest tests/unit/test_analysis.py::test_error_aggregation
```

### With Coverage

```bash
uv run pytest --cov=smart_log_analyzer
```

---

## 📊 Test Best Practices Used

| Practice | Example |
| -------- | ------- |
| Descriptive names | `test_error_aggregation` not `test1` |
| Single assertion focus | One logical concept per test |
| Fixtures for shared data | `sample_logs` reused across tests |
| Mocking external services | No real API calls in tests |
| Separate unit/integration | Fast unit tests, thorough integration |
