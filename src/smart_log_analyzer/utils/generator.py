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
    """
    Represents the structure of a generated log entry.
    """

    timestamp: str
    level: LogLevel
    service: ServiceName
    message: str
    request_id: str
    duration_ms: Optional[int] = None
    user_id: Optional[int] = None


class LogGenerator:
    """
    A robust synthetic log generator for testing the Smart Log Analyzer.
    Uses weighted random choices to simulate realistic traffic patterns.
    """

    def __init__(self, output_path: Path, count: int = 1000):
        self.output_path = output_path
        self.count = count
        self.fake_users = [random.randint(1000, 9999) for _ in range(50)]

        # Define common messages per service to ensure consistency
        self.service_messages = {
            ServiceName.AUTH_SERVICE: [
                ("User login successful", LogLevel.INFO),
                ("Token validation failed", LogLevel.ERROR),
                ("Password reset requested", LogLevel.INFO),
                ("Invalid credentials", LogLevel.WARNING),
            ],
            ServiceName.PAYMENT_SERVICE: [
                ("Payment processed successfully", LogLevel.INFO),
                ("Payment gateway timeout", LogLevel.ERROR),
                ("Insufficient funds", LogLevel.WARNING),
                ("Refund initiated", LogLevel.INFO),
            ],
            ServiceName.USER_SERVICE: [
                ("Profile updated", LogLevel.INFO),
                ("User not found", LogLevel.ERROR),
                ("Avatar uploaded", LogLevel.INFO),
            ],
            ServiceName.INVENTORY_SERVICE: [
                ("Stock checked", LogLevel.INFO),
                ("Item out of stock", LogLevel.WARNING),
                ("Inventory sync failed", LogLevel.ERROR),
            ],
            ServiceName.API_GATEWAY: [
                ("Request routed", LogLevel.INFO),
                ("Rate limit exceeded", LogLevel.WARNING),
                ("Service unavailable", LogLevel.ERROR),
            ],
        }

    def _generate_request_id(self) -> str:
        """Generates a random request ID."""
        return f"req-{random.randint(100000, 999999)}"

    def _generate_timestamp(self) -> str:
        """Generates a timestamp within the last 24 hours."""
        now = datetime.now(timezone.utc)
        delta = timedelta(minutes=random.randint(0, 24 * 60))
        return (now - delta).isoformat()

    def generate(self) -> None:
        """
        Generates logs and writes them to the specified file in JSONL format.
        """
        print(f"Generating {self.count} logs to {self.output_path}...")

        with open(self.output_path, "w", encoding="utf-8") as f:
            for _ in range(self.count):
                service = random.choice(list(ServiceName))
                message_template, level = random.choice(self.service_messages[service])

                # Simulate performance issues: 5% chance of very slow request
                duration = random.randint(10, 200)
                if random.random() < 0.05:
                    duration = random.randint(1000, 5000)  # Anomaly!

                # Simulate error spikes: 10% chance to override level to ERROR
                if random.random() < 0.1:
                    level = LogLevel.ERROR
                    message_template = f"Unexpected error in {service}"

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
