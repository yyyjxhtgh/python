# Day 4 — Functions & Modules

**Goal:** package code into reusable functions and use Python's standard library.

## 1. Defining a function

```python
def greet(name):
    """Return a friendly greeting."""     # a docstring describes the function
    return f"Hello, {name}!"

message = greet("Ada")    # call it
print(message)
```

- `name` is a **parameter**, and `"Ada"` is the **argument** you pass in.
- `return` sends a value back to the caller and ends the function.
- A function without a `return` gives back `None`.

### `print` vs `return`

```python
def add_print(a, b):
    print(a + b)       # shows the result, but the caller can't use it

def add_return(a, b):
    return a + b       # gives the result back so it can be used

x = add_return(2, 3) * 10   # 50
y = add_print(2, 3)         # prints 5, but y is None
```

Use `return` in almost every function. Only print at the "edges" of your
program, where you show results to the user.

## 2. Parameters

```python
def power(base, exponent=2):          # default value
    return base ** exponent

power(3)              # 9
power(3, 3)           # 27
power(exponent=3, base=2)   # 8   keyword arguments can go in any order
```

### Any number of arguments

```python
def total(*numbers):          # numbers arrives as a tuple
    return sum(numbers)

total(1, 2, 3)        # 6

def describe(**info):         # info arrives as a dict
    for key, value in info.items():
        print(f"{key} = {value}")

describe(name="Ada", job="programmer")
```

### Returning several values

```python
def min_max(numbers):
    return min(numbers), max(numbers)     # actually returns a tuple

low, high = min_max([4, 1, 9])
```

## 3. Scope

Variables created inside a function only exist inside that function:

```python
def f():
    secret = 42
f()
# print(secret)   # NameError
```

A function can *read* variables from outside, but it's better to pass in
what it needs as parameters and `return` what it produces. That makes
functions easy to test and to reuse.

## 4. Functions are values

You can pass a function to another function:

```python
def shout(text):
    return text.upper()

def apply(func, value):
    return func(value)

apply(shout, "hi")          # 'HI'
sorted(["bb", "a", "ccc"], key=len)   # len is passed as a value

# lambda = a tiny, nameless function
apply(lambda t: t + "!", "hi")       # 'hi!'
```

## 5. Modules and `import`

A **module** is just a `.py` file. Python comes with a big **standard library**:

```python
import math
math.sqrt(16)          # 4.0
math.pi                # 3.14159...

from random import choice, randint
choice(["rock", "paper", "scissors"])
randint(1, 6)

from datetime import date
date.today()
(date(2026, 12, 25) - date(2026, 1, 1)).days    # 358

import statistics
statistics.mean([1, 2, 3, 4])    # 2.5
```

### Your own modules

Make `helpers.py`:

```python
def double(x):
    return x * 2
```

Then, in another file **in the same folder**:

```python
from helpers import double
print(double(21))
```

### `if __name__ == "__main__":`

```python
def main():
    print("Running as a script")

if __name__ == "__main__":
    main()
```

The code under this `if` runs when you start the file directly with
`python file.py`, but **not** when another file imports it. Every exercise
file in this course uses this pattern.

## 6. Writing good functions

- Give each function **one job** and a name that starts with a verb: `calculate_total`, `load_tasks`.
- Keep functions short. If one gets long, split it up.
- Write a docstring that says what goes in and what comes out.

---

## Practice

1. Rewrite your Day 2 guessing game so that it's built from functions:
   `get_guess()`, `check_guess(guess, secret)` and `play()`.
2. Write a module `converters.py` with a few unit converters, and import it
   from another script.
3. **Exercises:** `python day4/exercises.py`

## Checklist

- [ ] I know why `return` is usually better than `print` inside functions
- [ ] I can use default and keyword arguments
- [ ] I can import from the standard library and from my own file
- [ ] I understand what `if __name__ == "__main__":` is for
