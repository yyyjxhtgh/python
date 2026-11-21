"""Day 5 exercises: files, exceptions and JSON.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day5/exercises.py

The checks use a temporary folder, so no files are left behind.
"""

import json  # you'll need this for save_json / load_json


def safe_divide(a, b):
    """Return a / b, or None if b is zero. Use try/except, not an if."""
    raise NotImplementedError


def parse_int(text, default=0):
    """Turn text into an int. If that's not possible, return default.

    parse_int("42") -> 42,  parse_int("abc") -> 0,  parse_int("x", -1) -> -1
    """
    raise NotImplementedError


def write_lines(path, lines):
    """Write each string in `lines` to the file at `path`, one per line."""
    raise NotImplementedError


def read_lines(path):
    """Return a list of the lines in the file, without the trailing newlines.
    If the file doesn't exist, return an empty list.
    """
    raise NotImplementedError


def count_matching_lines(path, word):
    """Return how many lines in the file contain `word` (ignoring case)."""
    raise NotImplementedError


def save_json(path, data):
    """Save `data` (a dict or list) to `path` as JSON."""
    raise NotImplementedError


def load_json(path, default=None):
    """Load and return JSON data from `path`.
    If the file is missing or isn't valid JSON, return `default`.

    Hint: catch (FileNotFoundError, json.JSONDecodeError)
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

import tempfile
from pathlib import Path


def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _check_safe_divide():
    _expect("safe_divide(10, 4)", safe_divide(10, 4), 2.5)
    _expect("safe_divide(1, 0)", safe_divide(1, 0), None)


def _check_parse_int():
    _expect('parse_int("42")', parse_int("42"), 42)
    _expect('parse_int("abc")', parse_int("abc"), 0)
    _expect('parse_int("x", -1)', parse_int("x", -1), -1)
    _expect('parse_int(" 7 ")', parse_int(" 7 "), 7)


def _check_write_and_read_lines():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "lines.txt"
        write_lines(path, ["one", "two", "three"])
        _expect("read_lines(path) after write_lines", read_lines(path), ["one", "two", "three"])
        _expect("read_lines(missing file)", read_lines(Path(folder) / "missing.txt"), [])


def _check_count_matching_lines():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "log.txt"
        path.write_text("ERROR disk full\ninfo ok\nerror again\nall good\n", encoding="utf-8")
        _expect('count_matching_lines(path, "error")', count_matching_lines(path, "error"), 2)
        _expect('count_matching_lines(path, "missing")', count_matching_lines(path, "missing"), 0)


def _check_json():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "data.json"
        data = {"name": "Ada", "skills": ["maths", "code"]}
        save_json(path, data)
        _expect("load_json(path) after save_json", load_json(path), data)
        _expect("load_json(missing, [])", load_json(Path(folder) / "missing.json", []), [])
        bad = Path(folder) / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        _expect("load_json(bad file, {})", load_json(bad, {}), {})


CHECKS = [
    ("safe_divide", _check_safe_divide),
    ("parse_int", _check_parse_int),
    ("write_lines / read_lines", _check_write_and_read_lines),
    ("count_matching_lines", _check_count_matching_lines),
    ("save_json / load_json", _check_json),
]


def run_checks(checks):
    passed = 0
    for name, check in checks:
        try:
            check()
        except NotImplementedError:
            print(f"⏳ {name}: not done yet")
        except AssertionError as error:
            print(f"❌ {name}: {error}")
        except Exception as error:  # a crash inside your code
            print(f"💥 {name}: {type(error).__name__}: {error}")
        else:
            print(f"✅ {name}")
            passed += 1
    print(f"\n{passed}/{len(checks)} passed")


if __name__ == "__main__":
    run_checks(CHECKS)
