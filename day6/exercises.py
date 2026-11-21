"""Day 6 exercises: classes.

Replace each `raise NotImplementedError` line with your own code,
then run:  python day6/exercises.py
"""

from dataclasses import dataclass


class BankAccount:
    """A simple bank account.

    account = BankAccount("Ada", 100)
    account.deposit(50)     -> balance is now 150
    account.withdraw(30)    -> balance is now 120
    account.withdraw(1000)  -> raises ValueError("Insufficient funds")
    str(account)            -> "Ada: $120.00"
    """

    def __init__(self, owner, balance=0):
        raise NotImplementedError

    def deposit(self, amount):
        """Add amount to the balance. Raise ValueError if amount <= 0."""
        raise NotImplementedError

    def withdraw(self, amount):
        """Take amount out. Raise ValueError if there isn't enough money."""
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class Rectangle:
    def __init__(self, width, height):
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def is_square(self):
        raise NotImplementedError


class Square(Rectangle):
    """A Square is a Rectangle with equal sides: Square(3) is a 3x3 rectangle.
    Only __init__ is needed. Use super().__init__(...).
    """

    def __init__(self, side):
        raise NotImplementedError


@dataclass
class Book:
    # This one is done for you. Notice how little code a dataclass needs.
    title: str
    author: str
    year: int


class Library:
    """A collection of Book objects."""

    def __init__(self):
        raise NotImplementedError

    def add(self, book):
        raise NotImplementedError

    def by_author(self, author):
        """Return a list of titles by that author, sorted alphabetically."""
        raise NotImplementedError

    def oldest(self):
        """Return the Book with the earliest year, or None if the library is empty."""
        raise NotImplementedError

    def __len__(self):
        """Lets len(library) give the number of books."""
        raise NotImplementedError


# ----------------------------------------------------------------------
# Checks: you don't need to change anything below this line.
# ----------------------------------------------------------------------

def _expect(call, got, expected):
    assert got == expected, f"{call} should be {expected!r}, got {got!r}"


def _expect_raises(call, func, *args):
    try:
        func(*args)
    except ValueError:
        return
    raise AssertionError(f"{call} should raise ValueError")


def _check_bank_account():
    account = BankAccount("Ada", 100)
    _expect("BankAccount('Ada', 100).balance", account.balance, 100)
    account.deposit(50)
    _expect("balance after deposit(50)", account.balance, 150)
    account.withdraw(30)
    _expect("balance after withdraw(30)", account.balance, 120)
    _expect_raises("withdraw(1000)", account.withdraw, 1000)
    _expect("balance after failed withdraw", account.balance, 120)
    _expect_raises("deposit(-5)", account.deposit, -5)
    _expect("str(account)", str(account), "Ada: $120.00")
    _expect("BankAccount('Sam').balance", BankAccount("Sam").balance, 0)


def _check_rectangle():
    r = Rectangle(3, 4)
    _expect("Rectangle(3, 4).area()", r.area(), 12)
    _expect("Rectangle(3, 4).perimeter()", r.perimeter(), 14)
    _expect("Rectangle(3, 4).is_square()", r.is_square(), False)


def _check_square():
    s = Square(5)
    _expect("Square(5).area()", s.area(), 25)
    _expect("Square(5).is_square()", s.is_square(), True)
    _expect("isinstance(Square(5), Rectangle)", isinstance(s, Rectangle), True)


def _check_library():
    lib = Library()
    _expect("len(Library())", len(lib), 0)
    _expect("Library().oldest()", lib.oldest(), None)
    lib.add(Book("Emma", "Jane Austen", 1815))
    lib.add(Book("Dune", "Frank Herbert", 1965))
    lib.add(Book("Persuasion", "Jane Austen", 1817))
    _expect("len(lib)", len(lib), 3)
    _expect('lib.by_author("Jane Austen")', lib.by_author("Jane Austen"), ["Emma", "Persuasion"])
    _expect('lib.by_author("Nobody")', lib.by_author("Nobody"), [])
    _expect("lib.oldest().title", lib.oldest().title, "Emma")


CHECKS = [
    ("BankAccount", _check_bank_account),
    ("Rectangle", _check_rectangle),
    ("Square", _check_square),
    ("Library", _check_library),
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
