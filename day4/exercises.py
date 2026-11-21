"""Day 4 exercises: functions and modules.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day4/exercises.py
"""

from datetime import date  # you'll need this for days_between


def rectangle_area(width, height=None):
    """Return width * height. If height isn't given, treat it as a square."""
    raise NotImplementedError


def make_sentence(*words, ending="."):
    """Join the words with spaces, capitalise the first letter, add the ending.

    make_sentence("hello", "world")              -> "Hello world."
    make_sentence("is", "it", "done", ending="?") -> "Is it done?"
    """
    raise NotImplementedError


def clamp(value, low, high):
    """Keep value inside the range low..high.

    clamp(15, 0, 10) -> 10,  clamp(-5, 0, 10) -> 0,  clamp(5, 0, 10) -> 5
    """
    raise NotImplementedError


def summary(numbers):
    """Return a tuple (smallest, largest, average) for a list of numbers."""
    raise NotImplementedError


def apply_twice(func, value):
    """Call func on value, then call func again on the result.

    apply_twice(lambda x: x + 3, 10) -> 16
    """
    raise NotImplementedError


def days_between(start, end):
    """Return the number of days from start to end. Both are strings in "YYYY-MM-DD" form.

    days_between("2026-01-01", "2026-03-01") -> 59
    Hint: date.fromisoformat("2026-01-01") turns a string into a date.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _check_rectangle_area():
    _expect("rectangle_area(3, 4)", rectangle_area(3, 4), 12)
    _expect("rectangle_area(5)", rectangle_area(5), 25)


def _check_make_sentence():
    _expect('make_sentence("hello", "world")', make_sentence("hello", "world"), "Hello world.")
    _expect(
        'make_sentence("is", "it", "done", ending="?")',
        make_sentence("is", "it", "done", ending="?"),
        "Is it done?",
    )


def _check_clamp():
    _expect("clamp(15, 0, 10)", clamp(15, 0, 10), 10)
    _expect("clamp(-5, 0, 10)", clamp(-5, 0, 10), 0)
    _expect("clamp(5, 0, 10)", clamp(5, 0, 10), 5)


def _check_summary():
    _expect("summary([4, 1, 7])", summary([4, 1, 7]), (1, 7, 4))
    _expect("summary([2])", summary([2]), (2, 2, 2))


def _check_apply_twice():
    _expect("apply_twice(lambda x: x + 3, 10)", apply_twice(lambda x: x + 3, 10), 16)
    _expect('apply_twice(str.upper, "hi")', apply_twice(str.upper, "hi"), "HI")


def _check_days_between():
    _expect('days_between("2026-01-01", "2026-03-01")', days_between("2026-01-01", "2026-03-01"), 59)
    _expect('days_between("2026-05-10", "2026-05-10")', days_between("2026-05-10", "2026-05-10"), 0)


CHECKS = [
    ("rectangle_area", _check_rectangle_area),
    ("make_sentence", _check_make_sentence),
    ("clamp", _check_clamp),
    ("summary", _check_summary),
    ("apply_twice", _check_apply_twice),
    ("days_between", _check_days_between),
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
