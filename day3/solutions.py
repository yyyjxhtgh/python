"""Day 3 solutions. Try the exercises first!

Run: python day3/solutions.py
"""


def average(numbers):
    if not numbers:          # an empty list counts as False
        return 0
    return sum(numbers) / len(numbers)


def unique_sorted(items):
    return sorted(set(items))


def word_count(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def invert(d):
    return {value: key for key, value in d.items()}


def squares_of_evens(numbers):
    return [n * n for n in numbers if n % 2 == 0]


def top_scorers(scores, n):
    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:n]


def common_friends(friends_a, friends_b):
    return sorted(set(friends_a) & set(friends_b))


if __name__ == "__main__":
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
