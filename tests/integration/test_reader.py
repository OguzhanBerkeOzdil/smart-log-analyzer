import json
import pytest
from pathlib import Path
from smart_log_analyzer.io.async_reader import AsyncLogReader


@pytest.mark.asyncio
async def test_read_valid_log_file(tmp_path: Path) -> None:
    """
    Writes a real file and reads it back using AsyncLogReader.
    """

    # Arrange 
    log_file = tmp_path / "test.jsonl"
    log_data = [
        {
            "timestamp": "2023-10-10",
            "level": "INFO",
            "service": "test",
            "message": "hello",
            "duration_ms": 100,
        },
        {
            "timestamp": "2023-10-10",
            "level": "ERROR",
            "service": "test",
            "message": "broken",
        },
    ]

    with open(log_file, "w", encoding="utf-8") as f:
        for entry in log_data:
            f.write(json.dumps(entry) + "\n")

    # Act
    entries = await AsyncLogReader.read_file(log_file)

    # Assert
    assert len(entries) == 2
    assert entries[0].service == "test"
    assert entries[0].duration_ms == 100
    assert entries[1].level == "ERROR"


@pytest.mark.asyncio
async def test_read_skips_malformed_lines(tmp_path: Path) -> None:
    """
    Ensures reader doesn't crash on bad JSON or invalid schema.
    """

    # Arrange
    log_file = tmp_path / "bad.jsonl"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write('{"valid": "json"}\n')   # Missing required fields
        f.write("THIS IS NOT JSON\n")     # Syntax error
        f.write("\n")                     # Empty line

    # Act
    entries = await AsyncLogReader.read_file(log_file)

    # Assert
    assert len(entries) == 0
