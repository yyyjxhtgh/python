"""Day 1 solutions. Try the exercises first!

Run: python day1/solutions.py
"""


def greet(name):
    return f"Hello, {name}!"


def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32


def seconds_to_hms(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def shout(text):
    return text.strip().upper() + "!"


def first_and_last(word):
    return word[0] + word[-1]


if __name__ == "__main__":
    # Re-use the checks from exercises.py, but point them at these solutions.
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
