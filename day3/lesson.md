# Day 3 — Collections: Lists, Tuples, Dictionaries, Sets

**Goal:** store many values together, then search, sort and transform them.

## 1. Lists: ordered and changeable

```python
fruits = ["apple", "banana", "cherry"]

fruits[0]              # 'apple'
fruits[-1]             # 'cherry'
fruits[1:]             # ['banana', 'cherry']
len(fruits)            # 3

fruits.append("date")          # add to the end
fruits.insert(0, "avocado")    # add at a position
fruits.remove("banana")        # remove by value
last = fruits.pop()            # remove and return the last item
fruits[0] = "apricot"          # replace an item

"apple" in fruits      # True / False membership test
```

### Looping over lists

```python
for fruit in fruits:
    print(fruit)

for i, fruit in enumerate(fruits):     # if you also need the position
    print(i, fruit)
```

### Useful functions

```python
nums = [5, 2, 9, 1]
sum(nums)          # 17
min(nums)          # 1
max(nums)          # 9
sorted(nums)       # [1, 2, 5, 9]   new list; nums is unchanged
nums.sort()        # sorts nums itself
sorted(nums, reverse=True)   # [9, 5, 2, 1]
```

### Strings ↔ lists

```python
"a,b,c".split(",")          # ['a', 'b', 'c']
"the quick fox".split()     # ['the', 'quick', 'fox']   splits on spaces
"-".join(["a", "b", "c"])   # 'a-b-c'
```

## 2. Tuples: ordered and *unchangeable*

```python
point = (3, 4)
x, y = point            # "unpacking"
print(x)                # 3
# point[0] = 10         # TypeError: tuples can't be changed
```

Use a tuple for a fixed group of values that belong together, like
coordinates or an RGB colour.

## 3. Dictionaries: key → value lookup

```python
ages = {"Ada": 36, "Alan": 41}

ages["Ada"]                 # 36
ages["Grace"] = 85          # add or update
del ages["Alan"]            # remove
"Ada" in ages               # True  (checks the keys)
ages.get("Bob")             # None  (no error if missing)
ages.get("Bob", 0)          # 0     (default value)

for name, age in ages.items():
    print(f"{name} is {age}")

list(ages.keys())     # ['Ada', 'Grace']
list(ages.values())   # [36, 85]
```

### The counting pattern

```python
text = "the cat and the hat"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)   # {'the': 2, 'cat': 1, 'and': 1, 'hat': 1}
```

## 4. Sets: unique items, no order

```python
colours = {"red", "green", "red"}   # {'red', 'green'}  duplicates are dropped
colours.add("blue")

a = {1, 2, 3}
b = {2, 3, 4}
a | b     # {1, 2, 3, 4}   union
a & b     # {2, 3}         intersection
a - b     # {1}            difference

unique = list(set([3, 1, 3, 2]))   # quick way to remove duplicates
```

## 5. Comprehensions: build a collection in one line

```python
nums = [1, 2, 3, 4, 5, 6]

squares = [n * n for n in nums]                 # [1, 4, 9, 16, 25, 36]
evens   = [n for n in nums if n % 2 == 0]       # [2, 4, 6]
lengths = {word: len(word) for word in ["hi", "hello"]}  # {'hi': 2, 'hello': 5}
```

Read a comprehension aloud as: "*n times n*, for each *n* in *nums*".
Here is the same thing as a normal loop:

```python
squares = []
for n in nums:
    squares.append(n * n)
```

## 6. Sorting with a `key`

```python
words = ["banana", "kiwi", "apple"]
sorted(words, key=len)        # ['kiwi', 'apple', 'banana']

scores = {"Ada": 92, "Alan": 85, "Grace": 98}
sorted(scores, key=scores.get, reverse=True)   # ['Grace', 'Ada', 'Alan']
```

## 7. Nesting

Collections can hold other collections. Real data often looks like this:

```python
students = [
    {"name": "Ada", "grades": [90, 95]},
    {"name": "Alan", "grades": [80, 70]},
]
for s in students:
    avg = sum(s["grades"]) / len(s["grades"])
    print(f"{s['name']}: {avg:.1f}")
```

## Watch out: copying vs. pointing

```python
a = [1, 2, 3]
b = a          # b is the SAME list, not a copy
b.append(4)
print(a)       # [1, 2, 3, 4]  (!)
c = a.copy()   # a real copy
```

---

## Practice

1. Make a shopping list program. Keep asking for items and add each to a
   list. When the user types `done`, print the list sorted, with numbers in front.
2. Given `{"apple": 1.2, "bread": 2.5, "milk": 0.99}`, print the most
   expensive item.
3. **Exercises:** `python day3/exercises.py`

## Checklist

- [ ] I can add, remove and loop over list items
- [ ] I can look things up in a dictionary and loop over `.items()`
- [ ] I can use a set to remove duplicates
- [ ] I can read and write a simple list comprehension
