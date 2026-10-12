import json

from pewpy.generators.compact_json import WIDTH, compact_json


def test_json_is_written_compactly_lines_fitting() -> None:
    value = {"short": [1, 2], "long": ["x" * 60, "y" * 60, {"z": "z" * 50}], "empty": []}
    text = compact_json(value)
    assert json.loads(text) == value
    assert all(len(line) <= WIDTH for line in text.splitlines())
    assert '"short": [1, 2]' in text
    assert compact_json([]) == "[]\n"


def test_what_fits_stays_on_one_line_and_what_doesnt_is_indented_by_2() -> None:
    assert compact_json({"a": 1, "b": [1, 2]}) == '{"a": 1, "b": [1, 2]}\n'
    long = ["x" * 80, "y" * 80]
    assert compact_json(long) == f'[\n  "{"x" * 80}",\n  "{"y" * 80}"\n]\n'
