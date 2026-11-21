# Day 6 — Classes, Packages & Testing

**Goal:** model real things with classes, install third-party packages, and
write automated tests.

## Part A: Classes (object-oriented programming)

A **class** is a blueprint. An **object** (or *instance*) is one thing built from it.
Objects bundle **data** (attributes) together with **behaviour** (methods).

```python
class Dog:
    species = "Canis familiaris"        # class attribute, shared by all dogs

    def __init__(self, name, age):      # runs when you create a Dog
        self.name = name                # instance attributes
        self.age = age

    def bark(self):                     # a method
        return f"{self.name} says woof!"

    def birthday(self):
        self.age += 1

rex = Dog("Rex", 3)
print(rex.bark())       # Rex says woof!
rex.birthday()
print(rex.age)          # 4
```

- `self` is the object the method was called on. When you write
  `rex.bark()`, Python runs `Dog.bark(rex)` for you.
- `__init__` sets up the starting state of a new object.

### Special ("dunder") methods

These let your objects work with Python's built-in features:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):                 # used by print() and str()
        return f"({self.x}, {self.y})"

    def __eq__(self, other):           # used by ==
        return self.x == other.x and self.y == other.y

    def __add__(self, other):          # used by +
        return Point(self.x + other.x, self.y + other.y)

print(Point(1, 2) + Point(3, 4))   # (4, 6)
```

There are others too: `__len__` for `len(obj)` and `__repr__` for the developer-facing display.

### Inheritance

A **child class** gets everything the parent class has, and can change or add to it:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Cat(Animal):
    def speak(self):                   # override the parent's version
        return f"{self.name} says meow"

class Kitten(Cat):
    def __init__(self, name, toy):
        super().__init__(name)         # run the parent's __init__
        self.toy = toy
```

### Properties

A property looks like an attribute to the caller, but it's worked out by a method:

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14159 * self.radius ** 2

Circle(2).area     # no parentheses needed
```

### Dataclasses: less typing for "data holder" classes

```python
from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    pages: int = 0

b = Book("Dune", "Frank Herbert", 412)
print(b)          # Book(title='Dune', author='Frank Herbert', pages=412)
```

A dataclass writes `__init__`, `__repr__` and `__eq__` for you.

### When to use a class

Use a class when you have **data plus the operations on that data** that
belong together. Examples are a bank account (balance plus deposit and withdraw),
a game character, or a shopping cart.
For a quick one-off calculation, a plain function is fine.

## Part B: Virtual environments & pip

There are thousands of free packages on [PyPI](https://pypi.org). Install
them into a **virtual environment**: a private, per-project folder of
packages that keeps your projects from interfering with each other.

```bash
# create one (once per project)
python -m venv .venv

# activate it (each time you open a new terminal)
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# install packages
pip install requests pytest

# record what you installed so others can reproduce it
pip freeze > requirements.txt
pip install -r requirements.txt

deactivate                        # leave the environment
```

Try a package:

```python
import requests
response = requests.get("https://api.github.com")
print(response.status_code, response.json()["current_user_url"])
```

## Part C: Automated tests with pytest

So far, the `exercises.py` files have been checking your code for you. Now
you'll write tests of your own. Make `test_math_utils.py` next to `math_utils.py`:

```python
# math_utils.py
def add(a, b):
    return a + b
```

```python
# test_math_utils.py
import pytest
from math_utils import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_bad_input():
    with pytest.raises(TypeError):
        add("a", 1)
```

Run them with:

```bash
pip install pytest
pytest            # finds files named test_*.py and runs functions named test_*
```

`assert something` does nothing if `something` is true. If it's false, it
raises an error, and pytest reports that as a failure.

---

## Practice

1. Make a `Player` class for a game, with `name`, `health` and a
   `take_damage(amount)` method. Health should never go below 0.
2. Create a virtual environment, install `requests`, and print the title
   of a GitHub repository you like using the GitHub API.
3. **Exercises:** `python day6/exercises.py`
4. **Bonus:** write pytest tests for your `BankAccount` class.

## Checklist

- [ ] I can write a class with `__init__` and methods, and I understand `self`
- [ ] I can make a child class with inheritance
- [ ] I can create a virtual environment and `pip install` a package
- [ ] I can write and run a pytest test
