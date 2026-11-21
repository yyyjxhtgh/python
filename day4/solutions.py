"""Day 4 solutions. Try the exercises first!

Run: python day4/solutions.py
"""

from datetime import date


def rectangle_area(width, height=None):
    if height is None:
        height = width
    return width * height


def make_sentence(*words, ending="."):
    sentence = " ".join(words)
    return sentence.capitalize() + ending


def clamp(value, low, high):
    return max(low, min(value, high))


def summary(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)


def apply_twice(func, value):
    return func(func(value))


def days_between(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


if __name__ == "__main__":
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
