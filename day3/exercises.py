"""Day 3 exercises: lists, tuples, dictionaries, sets.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day3/exercises.py
"""


def average(numbers):
    """Return the average of a list of numbers, or 0 if the list is empty."""
    raise NotImplementedError


def unique_sorted(items):
    """Return a new sorted list with all duplicates removed.

    unique_sorted([3, 1, 3, 2, 1]) -> [1, 2, 3]
    """
    raise NotImplementedError


def word_count(text):
    """Return a dict that maps each word (lowercased) to how many times it appears.

    word_count("The cat the hat") -> {"the": 2, "cat": 1, "hat": 1}
    """
    raise NotImplementedError


def invert(d):
    """Swap keys and values.

    invert({"a": 1, "b": 2}) -> {1: "a", 2: "b"}
    """
    raise NotImplementedError


def squares_of_evens(numbers):
    """Return the squares of only the even numbers. Use a list comprehension!

    squares_of_evens([1, 2, 3, 4]) -> [4, 16]
    """
    raise NotImplementedError


def top_scorers(scores, n):
    """Given a dict of name -> score, return the names of the top n scorers,
    highest score first.

    top_scorers({"Ada": 92, "Alan": 85, "Grace": 98}, 2) -> ["Grace", "Ada"]
    """
    raise NotImplementedError


def common_friends(friends_a, friends_b):
    """Return a sorted list of names that appear in both lists."""
    raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _check_average():
    _expect("average([1, 2, 3, 4])", average([1, 2, 3, 4]), 2.5)
    _expect("average([10])", average([10]), 10)
    _expect("average([])", average([]), 0)


def _check_unique_sorted():
    _expect("unique_sorted([3, 1, 3, 2, 1])", unique_sorted([3, 1, 3, 2, 1]), [1, 2, 3])
    _expect('unique_sorted(["b", "a", "b"])', unique_sorted(["b", "a", "b"]), ["a", "b"])
    _expect("unique_sorted([])", unique_sorted([]), [])


def _check_word_count():
    _expect('word_count("The cat the hat")', word_count("The cat the hat"), {"the": 2, "cat": 1, "hat": 1})
    _expect('word_count("")', word_count(""), {})


def _check_invert():
    _expect('invert({"a": 1, "b": 2})', invert({"a": 1, "b": 2}), {1: "a", 2: "b"})


def _check_squares_of_evens():
    _expect("squares_of_evens([1, 2, 3, 4])", squares_of_evens([1, 2, 3, 4]), [4, 16])
    _expect("squares_of_evens([1, 3])", squares_of_evens([1, 3]), [])


def _check_top_scorers():
    scores = {"Ada": 92, "Alan": 85, "Grace": 98, "Linus": 70}
    _expect("top_scorers(scores, 2)", top_scorers(scores, 2), ["Grace", "Ada"])
    _expect("top_scorers(scores, 1)", top_scorers(scores, 1), ["Grace"])


def _check_common_friends():
    _expect(
        'common_friends(["Sam", "Ali", "Jo"], ["Jo", "Kim", "Sam"])',
        common_friends(["Sam", "Ali", "Jo"], ["Jo", "Kim", "Sam"]),
        ["Jo", "Sam"],
    )
    _expect('common_friends(["A"], ["B"])', common_friends(["A"], ["B"]), [])


CHECKS = [
    ("average", _check_average),
    ("unique_sorted", _check_unique_sorted),
    ("word_count", _check_word_count),
    ("invert", _check_invert),
    ("squares_of_evens", _check_squares_of_evens),
    ("top_scorers", _check_top_scorers),
    ("common_friends", _check_common_friends),
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
