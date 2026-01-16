import random
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class ServiceName(str, Enum):
    AUTH_SERVICE = "auth-service"
    PAYMENT_SERVICE = "payment-service"
    USER_SERVICE = "user-service"
    INVENTORY_SERVICE = "inventory-service"
    API_GATEWAY = "api-gateway"


class LogSchema(BaseModel):
    """Structure of a generated log entry."""

    timestamp: str
    level: LogLevel
    service: ServiceName
    message: str
    request_id: str
    duration_ms: Optional[int] = None
    user_id: Optional[int] = None


class LogGenerator:
    """Synthetic log generator for testing."""

    def __init__(self, output_path: Path, count: int = 1000):
        self.output_path = output_path
        self.count = count
        self.fake_users = [random.randint(1000, 9999) for _ in range(50)]
        self.endpoints = ["/api/v1/users", "/api/v1/orders", "/api/v2/products", "/health", "/metrics"]
        self.http_codes = [200, 201, 400, 401, 403, 404, 500, 502, 503]

        # Define varied messages per service with dynamic parts
        self.service_messages = {
            ServiceName.AUTH_SERVICE: [
                ("User login successful", LogLevel.INFO),
                ("Token validation failed: expired token", LogLevel.ERROR),
                ("Token validation failed: invalid signature", LogLevel.ERROR),
                ("Password reset requested", LogLevel.INFO),
                ("Invalid credentials for user", LogLevel.WARNING),
                ("Session expired", LogLevel.WARNING),
                ("MFA verification failed", LogLevel.ERROR),
                ("OAuth callback error", LogLevel.ERROR),
                ("JWT decode error: malformed token", LogLevel.ERROR),
            ],
            ServiceName.PAYMENT_SERVICE: [
                ("Payment processed successfully", LogLevel.INFO),
                ("Payment gateway timeout after 30s", LogLevel.ERROR),
                ("Payment gateway timeout after 60s", LogLevel.ERROR),
                ("Insufficient funds for transaction", LogLevel.WARNING),
                ("Refund initiated", LogLevel.INFO),
                ("Card declined: insufficient balance", LogLevel.ERROR),
                ("Card declined: expired card", LogLevel.ERROR),
                ("Stripe API connection refused", LogLevel.ERROR),
                ("Currency conversion failed", LogLevel.ERROR),
                ("Duplicate transaction detected", LogLevel.WARNING),
            ],
            ServiceName.USER_SERVICE: [
                ("Profile updated", LogLevel.INFO),
                ("User not found", LogLevel.ERROR),
                ("Avatar uploaded", LogLevel.INFO),
                ("Email validation failed", LogLevel.ERROR),
                ("Database connection pool exhausted", LogLevel.ERROR),
                ("Cache miss for user profile", LogLevel.DEBUG),
                ("Password hash mismatch", LogLevel.ERROR),
                ("Account locked: too many attempts", LogLevel.WARNING),
            ],
            ServiceName.INVENTORY_SERVICE: [
                ("Stock checked", LogLevel.INFO),
                ("Item out of stock", LogLevel.WARNING),
                ("Inventory sync failed: timeout", LogLevel.ERROR),
                ("Inventory sync failed: data mismatch", LogLevel.ERROR),
                ("Warehouse API unavailable", LogLevel.ERROR),
                ("Stock reservation expired", LogLevel.WARNING),
                ("Bulk update failed: constraint violation", LogLevel.ERROR),
                ("Redis cache connection lost", LogLevel.ERROR),
            ],
            ServiceName.API_GATEWAY: [
                ("Request routed", LogLevel.INFO),
                ("Rate limit exceeded", LogLevel.WARNING),
                ("Service unavailable: auth-service", LogLevel.ERROR),
                ("Service unavailable: payment-service", LogLevel.ERROR),
                ("Circuit breaker opened", LogLevel.ERROR),
                ("Request timeout: upstream unresponsive", LogLevel.ERROR),
                ("SSL handshake failed", LogLevel.ERROR),
                ("Load balancer health check failed", LogLevel.WARNING),
                ("DNS resolution failed", LogLevel.ERROR),
            ],
        }

    def _generate_request_id(self) -> str:
        return f"req-{random.randint(100000, 999999)}"

    def _generate_timestamp(self) -> str:
        now = datetime.now(timezone.utc)
        return (now - timedelta(minutes=random.randint(0, 24 * 60))).isoformat()

    def generate(self) -> None:
        print(f"Generating {self.count} logs to {self.output_path}...")

        # Dynamic error scenarios that vary per run
        error_scenarios = [
            f"Connection refused to port {random.randint(3000, 9000)}",
            f"Timeout after {random.randint(10, 120)}s",
            f"HTTP {random.choice([500, 502, 503, 504])} from upstream",
            f"Memory limit exceeded: {random.randint(512, 2048)}MB",
            f"Disk space critical: {random.randint(90, 99)}% used",
            f"CPU throttling at {random.randint(80, 100)}%",
            f"Queue depth exceeded: {random.randint(1000, 10000)} pending",
            f"SSL certificate expires in {random.randint(1, 30)} days",
        ]

        with open(self.output_path, "w", encoding="utf-8") as f:
            for i in range(self.count):
                service = random.choice(list(ServiceName))
                message_template, level = random.choice(self.service_messages[service])

                # Simulate performance issues: 5% chance of very slow request
                duration = random.randint(10, 200)
                if random.random() < 0.05:
                    duration = random.randint(1000, 5000)  # Anomaly!

                # Simulate error spikes: 15% chance to use dynamic error
                if random.random() < 0.15:
                    level = LogLevel.ERROR
                    message_template = random.choice(error_scenarios)

                # Add request context to some messages
                if random.random() < 0.3 and level == LogLevel.ERROR:
                    endpoint = random.choice(self.endpoints)
                    message_template = f"{message_template} at {endpoint}"

                log_entry = LogSchema(
                    timestamp=self._generate_timestamp(),
                    level=level,
                    service=service,
                    message=message_template,
                    request_id=self._generate_request_id(),
                    duration_ms=duration,
                    user_id=(
                        random.choice(self.fake_users)
                        if random.random() > 0.2
                        else None
                    ),
                )

                f.write(log_entry.model_dump_json() + "\n")

        print("Generation complete.")


if __name__ == "__main__":
    # Quick test run
    output = Path("data/synthetic_logs.jsonl")
    generator = LogGenerator(output, count=500)
    generator.generate()
