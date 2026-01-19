import json
from pathlib import Path

from smart_log_analyzer.utils.generator import LogGenerator


def test_log_generator_creates_file(tmp_path: Path) -> None:
    # Arrange
    output = tmp_path / "logs.jsonl"
    generator = LogGenerator(output_path=output, count=5)

    # Act
    generator.generate()

    # Assert
    assert output.exists()


def test_log_generator_writes_correct_number_of_lines(
    tmp_path: Path,
) -> None:
    # Arrange
    output = tmp_path / "logs.jsonl"
    generator = LogGenerator(output_path=output, count=3)

    # Act
    generator.generate()

    # Assert
    lines = output.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3


def test_log_generator_output_contains_required_fields(
    tmp_path: Path,
) -> None:
    # Arrange
    output = tmp_path / "logs.jsonl"
    generator = LogGenerator(output_path=output, count=1)

    # Act
    generator.generate()

    # Assert
    data = json.loads(output.read_text(encoding="utf-8").strip())
    assert "timestamp" in data
    assert "request_id" in data
    assert "service" in data
    assert "level" in data
