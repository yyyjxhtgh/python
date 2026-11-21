# Day 5 — Files, Errors & JSON

**Goal:** make data last after your program closes, and handle problems without crashing.

## 1. Errors (exceptions)

When something goes wrong, Python *raises an exception*:

```python
int("hello")        # ValueError: invalid literal for int()
10 / 0              # ZeroDivisionError
[1, 2][5]           # IndexError
{"a": 1}["b"]       # KeyError
open("nope.txt")    # FileNotFoundError
"a" + 1             # TypeError
```

### Reading a traceback

```
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    total = add("5", 3)
  File "app.py", line 2, in add
    return a + b
TypeError: can only concatenate str (not "int") to str
```

Start at the **last line** to see what went wrong. The lines above it show
*where*, ending with the exact line that failed.

## 2. Handling errors with `try` / `except`

```python
try:
    age = int(input("Age: "))
except ValueError:
    print("That's not a number!")
    age = 0
```

Here's the full structure:

```python
try:
    result = 10 / int(text)
except ValueError:
    print("Not a number")
except ZeroDivisionError:
    print("Can't divide by zero")
else:
    print("Worked:", result)     # runs only if nothing went wrong
finally:
    print("Always runs")         # good for cleaning up
```

A common pattern is to keep asking until the input is valid:

```python
while True:
    try:
        n = int(input("Pick a number: "))
        break
    except ValueError:
        print("Try again.")
```

**Catch specific exceptions.** A bare `except:` hides bugs you'd want to know about.

### Raising your own errors

```python
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount
```

## 3. Reading and writing text files

Always use `with`. It closes the file for you, even if an error happens.

```python
# Write (mode "w" creates the file or replaces what's in it)
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")

# Append (mode "a" adds to the end)
with open("notes.txt", "a", encoding="utf-8") as f:
    f.write("Third line\n")

# Read everything at once
with open("notes.txt", encoding="utf-8") as f:
    content = f.read()

# Read line by line (good for big files)
with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        print(line.strip())      # strip() removes the "\n" at the end
```

## 4. Paths with `pathlib`

```python
from pathlib import Path

path = Path("data") / "notes.txt"     # works on Windows, macOS and Linux
path.parent.mkdir(exist_ok=True)      # create the folder if it's missing
path.write_text("hi\n", encoding="utf-8")
print(path.read_text(encoding="utf-8"))
print(path.exists(), path.name, path.suffix)   # True notes.txt .txt

for file in Path(".").glob("*.py"):   # list files that match a pattern
    print(file)
```

## 5. JSON: saving structured data

JSON is a text format that maps neatly onto Python dicts and lists.

```python
import json

data = {"name": "Ada", "skills": ["maths", "programming"], "age": 36}

# Save
with open("person.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Load
with open("person.json", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded["skills"][0])    # maths

# To and from strings
text = json.dumps(data)
back = json.loads(text)
```

## 6. CSV files (spreadsheet data)

```python
import csv

with open("scores.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "score"])
    writer.writerow(["Ada", 92])

with open("scores.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["score"]))
```

---

## Practice

1. **Journal:** write a script that asks for a one-line entry and appends it
   to `journal.txt` with today's date. Run it a few times, then write a
   second script that prints every entry.
2. **Safe calculator:** ask for two numbers and an operator, and handle bad
   numbers and division by zero politely.
3. **Exercises:** `python day5/exercises.py`

## Checklist

- [ ] I can read a traceback and find the failing line
- [ ] I can use `try`/`except` with a specific exception
- [ ] I open files with `with open(...)`
- [ ] I can save a dict to JSON and load it back
