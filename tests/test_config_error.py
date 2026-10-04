from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from pewpy.config import load_json

# Test that load_json raises RuntimeError on invalid JSON


def test_load_json_invalid() -> None:
    # Create a temporary file with invalid JSON
    with NamedTemporaryFile("w", delete=False, suffix=".json") as tmp_file:
        tmp_file.write("{ malformed json")
        tmp_file_path = Path(tmp_file.name)
    try:
        with pytest.raises(RuntimeError):
            load_json(tmp_file_path)
    finally:
        tmp_file_path.unlink(missing_ok=True)
