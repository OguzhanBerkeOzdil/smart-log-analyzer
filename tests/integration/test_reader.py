import json
import pytest
from pathlib import Path
from smart_log_analyzer.io.reader import read_log_file


def test_read_valid_log_file(tmp_path: Path) -> None:
    """
    Writes a real file and reads it back.
    """
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

    with open(log_file, "w") as f:
        for entry in log_data:
            f.write(json.dumps(entry) + "\n")

    entries = list(read_log_file(log_file))

    assert len(entries) == 2
    assert entries[0].service == "test"
    assert entries[0].duration_ms == 100
    assert entries[1].level == "ERROR"


def test_read_skips_malformed_lines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ensures reader doesn't crash on bad JSON."""
    log_file = tmp_path / "bad.jsonl"
    with open(log_file, "w") as f:
        f.write('{"valid": "json"}\n')  # Missing required fields
        f.write("THIS IS NOT JSON\n")  # Syntax error
        f.write("\n")  # Empty line

    entries = list(read_log_file(log_file))

    # Should skip both invalid lines and return empty list (or handle as needed)
    # Since our model requires fields like 'timestamp', the first line fails validation.
    assert len(entries) == 0

    captured = capsys.readouterr()
    assert "parse error" in captured.err
