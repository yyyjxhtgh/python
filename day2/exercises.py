"""Day 2 exercises: conditions and loops.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day2/exercises.py
"""


def letter_grade(score):
    """Return "A" for 90+, "B" for 80-89, "C" for 70-79, "D" for 60-69, else "F"."""
    raise NotImplementedError


def fizzbuzz(n):
    """Return "FizzBuzz" if n is divisible by 3 and 5, "Fizz" if only by 3,
    "Buzz" if only by 5, otherwise the number as a string, e.g. "7".

    Hint: n % 3 == 0 means "n is divisible by 3". Check the 15 case first!
    """
    raise NotImplementedError


def sum_of_multiples(limit):
    """Return the sum of all numbers below `limit` that are multiples of 3 or 5.

    sum_of_multiples(10) -> 23   (3 + 5 + 6 + 9)
    """
    raise NotImplementedError


def count_vowels(text):
    """Return how many vowels (a, e, i, o, u, upper or lower case) are in text.

    Hint: `if letter in "aeiou":` checks whether a letter is a vowel.
    """
    raise NotImplementedError


def is_prime(n):
    """Return True if n is a prime number, otherwise False.

    A prime is a whole number above 1 that only divides evenly by 1 and itself.
    """
    raise NotImplementedError


def countdown(start):
    """Return a string counting down from start to 1, then "Go!".

    countdown(3) -> "3 2 1 Go!"
    Use a while loop for practice.
    """
    raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _check_letter_grade():
    for score, grade in [(95, "A"), (90, "A"), (85, "B"), (72, "C"), (60, "D"), (59, "F"), (0, "F")]:
        _expect(f"letter_grade({score})", letter_grade(score), grade)


def _check_fizzbuzz():
    for n, out in [(3, "Fizz"), (5, "Buzz"), (15, "FizzBuzz"), (30, "FizzBuzz"), (7, "7"), (1, "1")]:
        _expect(f"fizzbuzz({n})", fizzbuzz(n), out)


def _check_sum_of_multiples():
    _expect("sum_of_multiples(10)", sum_of_multiples(10), 23)
    _expect("sum_of_multiples(1000)", sum_of_multiples(1000), 233168)
    _expect("sum_of_multiples(1)", sum_of_multiples(1), 0)


def _check_count_vowels():
    _expect('count_vowels("Hello World")', count_vowels("Hello World"), 3)
    _expect('count_vowels("AEIOU")', count_vowels("AEIOU"), 5)
    _expect('count_vowels("rhythm")', count_vowels("rhythm"), 0)


def _check_is_prime():
    for n, expected in [(2, True), (3, True), (4, False), (17, True), (21, False), (1, False), (0, False), (97, True)]:
        _expect(f"is_prime({n})", is_prime(n), expected)


def _check_countdown():
    _expect("countdown(3)", countdown(3), "3 2 1 Go!")
    _expect("countdown(1)", countdown(1), "1 Go!")


CHECKS = [
    ("letter_grade", _check_letter_grade),
    ("fizzbuzz", _check_fizzbuzz),
    ("sum_of_multiples", _check_sum_of_multiples),
    ("count_vowels", _check_count_vowels),
    ("is_prime", _check_is_prime),
    ("countdown", _check_countdown),
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
