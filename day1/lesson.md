# Day 1 — Setup & Basics

**Goal:** run Python code, store values in variables, and work with numbers and text.

## 1. Your first program

Create a file called `hello.py`:

```python
print("Hello, world!")
```

Run it from the terminal:

```
python hello.py
```

`print()` is a **function**. You *call* it by writing its name followed by
parentheses, and whatever you put inside the parentheses gets shown on screen.

### The REPL

Type `python` by itself to get an interactive prompt:

```
>>> 2 + 3
5
>>> "ha" * 3
'hahaha'
>>> exit()
```

Use it to test small ideas quickly.

## 2. Variables

A variable is a name that points to a value. Use `=` to assign one.

```python
name = "Ada"
age = 36
height_m = 1.65
is_programmer = True

print(name, age)          # Ada 36
age = age + 1             # variables can change
print(age)                # 37
```

Naming rules: use letters, numbers and `_`, and don't start with a number.
Python style is `snake_case` (lowercase words joined by underscores).

## 3. Core types

| Type | Example | Meaning |
|------|---------|---------|
| `int` | `42`, `-7` | whole numbers |
| `float` | `3.14`, `2.0` | decimal numbers |
| `str` | `"hello"`, `'hi'` | text (a *string*) |
| `bool` | `True`, `False` | yes/no |
| `NoneType` | `None` | "nothing here" |

```python
print(type(42))       # <class 'int'>
print(type("42"))     # <class 'str'>   <- the quotes make it text!
```

### Converting between types

```python
int("42")      # 42
float("3.5")   # 3.5
str(10)        # "10"
int(3.9)       # 3  (cuts off the decimal part, no rounding)
round(3.9)     # 4
```

## 4. Arithmetic

```python
7 + 2    # 9      addition
7 - 2    # 5      subtraction
7 * 2    # 14     multiplication
7 / 2    # 3.5    division (always gives a float)
7 // 2   # 3      floor division (whole part)
7 % 2    # 1      modulo (remainder)
7 ** 2   # 49     power
```

`//` and `%` work well together. For example, 125 minutes is
`125 // 60` = 2 hours and `125 % 60` = 5 minutes.

There are also shortcuts: `x += 1` means `x = x + 1`. The same goes for `-=`, `*=` and `/=`.

## 5. Strings

```python
first = "Ada"
last = "Lovelace"

full = first + " " + last        # joining strings: "Ada Lovelace"
print(len(full))                 # 12 characters
print(full.upper())              # ADA LOVELACE
print(full.lower())              # ada lovelace
print(full.replace("Ada", "A."))  # A. Lovelace
print("  padded  ".strip())      # "padded"
```

### Indexing and slicing

Each character has a position, and positions **start at 0**.

```python
word = "Python"
word[0]      # 'P'
word[-1]     # 'n'   (negative indexes count from the end)
word[0:3]    # 'Pyt' (from 0 up to, but not including, 3)
word[2:]     # 'thon'
```

### f-strings: the easiest way to format text

Put an `f` before the quotes, then write variables inside `{}`:

```python
name = "Ada"
age = 36
print(f"{name} is {age} years old")         # Ada is 36 years old
print(f"Next year: {age + 1}")              # expressions work too
price = 3.14159
print(f"Price: {price:.2f}")                # Price: 3.14  (2 decimal places)
print(f"{7:02d}")                           # 07  (pad with zeros to width 2)
```

## 6. Getting input from the user

`input()` pauses, waits for the user to type, and **always returns a string**.

```python
name = input("What's your name? ")
age = int(input("How old are you? "))   # convert to int to do maths
print(f"Hi {name}! In 10 years you'll be {age + 10}.")
```

## 7. Comments

```python
# This line is a comment. Python ignores it.
total = 5  # comments can go at the end of a line too
```

Use comments to explain *why* something is done. The code itself already shows *what* it does.

---

## Practice

1. **Warm-up (try it in the REPL):** work out how many seconds are in a week.
2. **Mini-program:** write `tip.py`. It asks for a bill amount and a tip
   percentage, then prints the tip and the total rounded to 2 decimal places.
3. **Exercises:** open `day1/exercises.py`, fill in each function, and run
   `python day1/exercises.py` until everything passes.

## Checklist

- [ ] I can run a `.py` file from the terminal
- [ ] I know the difference between `"5"` and `5`
- [ ] I can use `//` and `%`
- [ ] I can slice a string and use an f-string
