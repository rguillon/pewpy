import json
import pytest
from pathlib import Path
from pewpy.config import load_json

# Test that load_json raises RuntimeError on invalid JSON

def test_load_json_invalid():
    # Create a temporary file with invalid JSON
    tmp = Path("/tmp/opencode/invalid.json")
    tmp.write_text("{ malformed json")
    with pytest.raises(RuntimeError):
        load_json(tmp)
    tmp.unlink()
