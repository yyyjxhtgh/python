# Day 2 — Making Decisions & Repeating

**Goal:** make programs choose what to do with `if`, and repeat work with loops.

## 1. Comparisons and booleans

Comparisons give back `True` or `False`:

```python
5 > 3        # True
5 == 5       # True   (== compares, = assigns!)
5 != 4       # True   (not equal)
"a" < "b"    # True   (alphabetical order)
3 <= 3       # True
```

Combine them with `and`, `or`, `not`:

```python
age = 25
has_ticket = True
age >= 18 and has_ticket     # True
age < 13 or age > 65         # False
not has_ticket               # False
10 < age < 30                # True  (Python lets you chain comparisons)
```

**Truthiness:** `0`, `""` (an empty string), `None`, `[]` and `{}` all count as `False`
inside an `if`. Almost everything else counts as `True`.

## 2. `if` / `elif` / `else`

```python
temperature = 22

if temperature > 30:
    print("It's hot")
elif temperature > 15:
    print("It's nice")       # this one runs
else:
    print("It's cold")
```

**Indentation matters.** The indented lines (4 spaces) belong to the block
above them. A colon `:` always comes before an indented block.

Python checks `elif` branches from top to bottom, and only the **first** one
that's true runs.

## 3. `for` loops

A `for` loop goes through each item in a sequence, one at a time:

```python
for letter in "abc":
    print(letter)            # a, then b, then c

for i in range(5):           # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 11, 2):    # start, stop (excluded), step → 1, 3, 5, 7, 9
    print(i)
```

### The accumulator pattern

This pattern is very common. Start with an empty value and add to it inside the loop:

```python
total = 0
for n in range(1, 101):
    total += n
print(total)   # 5050
```

## 4. `while` loops

A `while` loop repeats *as long as* its condition stays true:

```python
count = 3
while count > 0:
    print(count)
    count -= 1      # forget this and the loop never ends! (Ctrl+C stops it)
print("Lift off!")
```

Use `for` when you know what you're looping over. Use `while` when you're
waiting for something to happen.

## 5. `break` and `continue`

```python
for n in range(10):
    if n == 3:
        continue     # skip the rest of this round, go to the next n
    if n == 6:
        break        # leave the loop completely
    print(n)         # 0 1 2 4 5
```

## 6. Putting it together: a guessing game

Type this one out and play it:

```python
import random

secret = random.randint(1, 20)
attempts = 0

print("I'm thinking of a number between 1 and 20.")
while True:
    guess = int(input("Your guess: "))
    attempts += 1
    if guess < secret:
        print("Too low!")
    elif guess > secret:
        print("Too high!")
    else:
        print(f"Got it in {attempts} attempts!")
        break
```

**Extensions:** give the player only 5 attempts, or ask "Play again?" at the end.

## 7. Nested loops

You can put a loop inside another loop:

```python
for row in range(1, 4):
    line = ""
    for col in range(1, 4):
        line += f"{row * col:4}"
    print(line)
#    1   2   3
#    2   4   6
#    3   6   9
```

---

## Practice

1. Print every number from 1 to 50 that is divisible by 7.
2. Write a program that keeps asking for numbers until the user types `0`,
   then prints their sum.
3. **Exercises:** `python day2/exercises.py`

## Checklist

- [ ] I know the difference between `=` and `==`
- [ ] I can write an `if`/`elif`/`else` chain
- [ ] I can loop with `for ... in range(...)`
- [ ] I can use a `while` loop and stop it with `break`
