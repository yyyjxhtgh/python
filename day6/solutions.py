"""Day 6 solutions. Try the exercises first!

Run: python day6/solutions.py
"""

from dataclasses import dataclass


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def __str__(self):
        return f"{self.owner}: ${self.balance:.2f}"


class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)


@dataclass
class Book:
    title: str
    author: str
    year: int


class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        self.books.append(book)

    def by_author(self, author):
        return sorted(book.title for book in self.books if book.author == author)

    def oldest(self):
        if not self.books:
            return None
        return min(self.books, key=lambda book: book.year)

    def __len__(self):
        return len(self.books)


if __name__ == "__main__":
    import exercises

    for name, value in list(globals().items()):
        if not name.startswith("_") and hasattr(exercises, name):
            setattr(exercises, name, value)
    exercises.run_checks(exercises.CHECKS)
