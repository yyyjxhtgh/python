"""Day 1 exercises: variables, numbers and strings.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day1/exercises.py
"""


def greet(name):
    """Return a greeting such as "Hello, Ada!" for the given name."""
    raise NotImplementedError


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit using the formula F = C * 9 / 5 + 32."""
    raise NotImplementedError


def seconds_to_hms(total_seconds):
    """Return a string in the form "H:MM:SS".

    Examples:
        seconds_to_hms(3725) -> "1:02:05"
        seconds_to_hms(59)   -> "0:00:59"

    Hint: use // and %, and an f-string with {value:02d} to pad with zeros.
    """
    raise NotImplementedError


def shout(text):
    """Remove extra spaces from both ends, make it uppercase and add "!".

    shout("  hello there ") -> "HELLO THERE!"
    """
    raise NotImplementedError


def first_and_last(word):
    """Return the first and last characters of word joined together.

    first_and_last("Python") -> "Pn"
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _check_greet():
    _expect('greet("Ada")', greet("Ada"), "Hello, Ada!")
    _expect('greet("Sam")', greet("Sam"), "Hello, Sam!")


def _check_celsius_to_fahrenheit():
    _expect("celsius_to_fahrenheit(100)", celsius_to_fahrenheit(100), 212)
    _expect("celsius_to_fahrenheit(0)", celsius_to_fahrenheit(0), 32)
    _expect("celsius_to_fahrenheit(-40)", celsius_to_fahrenheit(-40), -40)


def _check_seconds_to_hms():
    _expect("seconds_to_hms(3725)", seconds_to_hms(3725), "1:02:05")
    _expect("seconds_to_hms(59)", seconds_to_hms(59), "0:00:59")
    _expect("seconds_to_hms(36000)", seconds_to_hms(36000), "10:00:00")


def _check_shout():
    _expect('shout("  hello there ")', shout("  hello there "), "HELLO THERE!")
    _expect('shout("hi")', shout("hi"), "HI!")


def _check_first_and_last():
    _expect('first_and_last("Python")', first_and_last("Python"), "Pn")
    _expect('first_and_last("ab")', first_and_last("ab"), "ab")


CHECKS = [
    ("greet", _check_greet),
    ("celsius_to_fahrenheit", _check_celsius_to_fahrenheit),
    ("seconds_to_hms", _check_seconds_to_hms),
    ("shout", _check_shout),
    ("first_and_last", _check_first_and_last),
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
