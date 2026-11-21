"""Day 5 solutions. Try the exercises first!

Run: python day5/solutions.py
"""

import json


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


def parse_int(text, default=0):
    try:
        return int(text)          # int() ignores spaces around the number
    except ValueError:
        return default


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def read_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]
    except FileNotFoundError:
        return []


def count_matching_lines(path, word):
    word = word.lower()
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if word in line.lower():
                count += 1
    return count


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


if __name__ == "__main__":
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
