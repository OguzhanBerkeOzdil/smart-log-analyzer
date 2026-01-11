# Utils Module Documentation

The `utils/` module contains helper utilities for development and testing.

---

## 📄 generator.py - Synthetic Log Generator

### What It Does

Creates realistic fake log data for testing the analyzer without needing production logs.

### Why It Exists

1. **Testing**: Need consistent test data
2. **Demo**: Show analyzer capabilities without real data
3. **Development**: Test edge cases (many errors, slow requests)

### Code Structure

#### Enums for Type Safety

```python
class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

class ServiceName(str, Enum):
    AUTH_SERVICE = "auth-service"
    PAYMENT_SERVICE = "payment-service"
    # ...
```

**Why `str, Enum`?**

Inheriting from `str` allows JSON serialization:

```python
>>> LogLevel.INFO.value  # "INFO"
>>> str(LogLevel.INFO)   # "INFO"
```

Without `str`, you'd need `.value` everywhere.

#### Class-Level Constants

```python
class LogGenerator:
    SERVICE_MESSAGES = {
        ServiceName.AUTH_SERVICE: [
            ("User login successful", LogLevel.INFO),
            ("Token validation failed", LogLevel.ERROR),
            # ...
        ],
        # ...
    }
```

**Why class-level?**

- Shared across all instances
- Defined once, not recreated per instance
- Easy to modify/extend

#### Generation Logic

```python
def generate(self) -> None:
    for _ in range(self.count):
        service = random.choice(list(ServiceName))
        message, level = random.choice(self.SERVICE_MESSAGES[service])

        # 5% chance of slow request (performance anomaly)
        duration = random.randint(1000, 5000) if random.random() < 0.05 else random.randint(10, 200)

        # 10% chance of error spike
        if random.random() < 0.1:
            level, message = LogLevel.ERROR, f"Unexpected error in {service}"
```

**Realistic Patterns**:

- Most requests are fast (10-200ms)
- 5% are anomalously slow (1-5 seconds)
- 10% override to ERROR to simulate spikes

### Key Techniques

**Conditional Expression (Ternary)**

```python
duration = random.randint(1000, 5000) if random.random() < 0.05 else random.randint(10, 200)
```

Equivalent to:

```python
if random.random() < 0.05:
    duration = random.randint(1000, 5000)
else:
    duration = random.randint(10, 200)
```

**Tuple Unpacking**

```python
level, message = LogLevel.ERROR, f"Unexpected error in {service}"
```

Assigns multiple values in one line.

**F-string Formatting**

```python
request_id=f"req-{random.randint(100000, 999999)}"
```

Modern string formatting - cleaner than `.format()` or `%`.

### Alternative Approaches

**Using Faker library**:

```python
from faker import Faker
fake = Faker()

log = {
    "timestamp": fake.iso8601(),
    "service": fake.random_element(["auth", "api"]),
    "message": fake.sentence(),
}
```

More variety but less control over patterns.

**Using Factory Boy**:

```python
class LogFactory(factory.Factory):
    class Meta:
        model = LogEntry
    
    timestamp = factory.LazyFunction(datetime.now().isoformat)
    level = factory.Iterator(["INFO", "ERROR"])
```

Better for test fixtures but heavier dependency.

### Usage Examples

**Command Line**:

```bash
python -m smart_log_analyzer.main --generate --count 500
```

**Programmatic**:

```python
from smart_log_analyzer.utils.generator import LogGenerator
from pathlib import Path

LogGenerator(Path("test_logs.jsonl"), count=100).generate()
```
