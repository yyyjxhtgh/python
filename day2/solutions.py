"""Day 2 solutions. Try the exercises first!

Run: python day2/solutions.py
"""


def letter_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def fizzbuzz(n):
    if n % 15 == 0:          # divisible by both 3 and 5
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)


def sum_of_multiples(limit):
    total = 0
    for n in range(limit):
        if n % 3 == 0 or n % 5 == 0:
            total += n
    return total


def count_vowels(text):
    count = 0
    for letter in text.lower():
        if letter in "aeiou":
            count += 1
    return count


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:   # only need to test up to the square root
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def countdown(start):
    result = ""
    n = start
    while n > 0:
        result += f"{n} "
        n -= 1
    return result + "Go!"


if __name__ == "__main__":
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
