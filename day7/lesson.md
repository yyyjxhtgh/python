# Day 7 — Project: Build a To-Do App

**Goal:** build a complete program from start to finish using everything
from this week. After that, plan what to learn next.

## What you're building

A to-do list that runs in the terminal and remembers your tasks between runs:

```
📝 To-do list: 2 task(s) left to do.

What would you like to do?
  [l] List tasks     [a] Add task      [d] Mark done
  [r] Remove task    [c] Clear done    [q] Quit

> l
1. [ ] Buy milk
2. [x] Learn Python
3. [ ] Call mum
```

| File | Purpose |
|------|---------|
| `todo.py` | **Your version.** The menu is written for you, and you fill in the functions. |
| `test_todo.py` | Tests that tell you whether each function works. |
| `todo_solution.py` | A finished version to compare with once you're done. |

## Step by step (about 2–3 hours)

### Step 1: Read before you write (15 min)
Open `todo.py` and read `main()` from top to bottom. Find:
- the `while True` loop (Day 2)
- the `if`/`elif` menu (Day 2)
- `try`/`except ValueError` (Day 5)
- the list of dicts that holds the tasks (Day 3)

Work out which of your functions each menu option calls.

### Step 2: Build the task operations (60 min)
Fill these in, in this order, and run the tests after each one:

1. `add_task`
2. `format_tasks`
3. `pending_count`
4. `complete_task` and `delete_task` (remember that the user counts from 1, but list indexes start at 0)
5. `clear_completed`

```bash
python day7/test_todo.py      # or: pytest day7
```

### Step 3: Add saving and loading (20 min)
Write `load_tasks` and `save_tasks` with `json` (Day 5).

### Step 4: Use it (15 min)
```bash
python day7/todo.py
```
Add some real tasks, quit, start it again, and check they're still there.
Try to break it: type letters where it wants a number, choose task 99,
or add an empty task. It should never crash.

### Step 5: Compare (15 min)
Read `todo_solution.py`. Differences are fine. For each one, ask yourself
which version is easier to read.

## Extensions (pick any)

- ⭐ **Due dates:** ask for an optional due date and show `(overdue!)` for tasks past it.
- ⭐ **Priorities:** add `high`/`normal`/`low` and list high-priority tasks first.
- ⭐⭐ **Edit:** add an `[e]` option to rename a task.
- ⭐⭐ **Search:** add `[s]` to show only the tasks that contain a word.
- ⭐⭐ **Classes:** rewrite it with a `Task` dataclass and a `TodoList` class (Day 6).
- ⭐⭐⭐ **Command-line arguments:** use the `argparse` module so that
  `python todo.py add "Buy milk"` works without the menu.

Write a test for each feature you add.

---

## 🎉 You finished the week. What's next?

You now know the core of Python. Here's how to keep going:

### 1. Keep coding every day, even for 20 minutes
Short, regular practice works better than a long weekend session.
- [Exercism Python track](https://exercism.org/tracks/python): free exercises with mentor feedback
- [Advent of Code](https://adventofcode.com): puzzles that are good for practice, especially in December

### 2. Pick a direction and build something in it

| If you like... | Learn | First project idea |
|----------------|-------|--------------------|
| Automating boring tasks | `pathlib`, `shutil`, `csv`, `openpyxl` | Rename or organise the files in your Downloads folder |
| Data & charts | `pandas`, `matplotlib`, Jupyter | Analyse your bank statement CSV |
| Websites & APIs | `requests`, Flask or FastAPI | A small web API for your to-do list |
| Web scraping | `requests`, `BeautifulSoup` | Track the price of a product |
| Games | `pygame` | Snake or Pong |
| AI & machine learning | `numpy`, `scikit-learn` | Predict house prices from a dataset |

### 3. Level-up topics for week 2
- `git` and GitHub, to save and share your code
- Type hints: `def add(a: int, b: int) -> int:`
- More of the standard library: `collections`, `itertools`, `argparse`, `logging`
- Generators and `yield`, decorators, context managers
- Reading other people's code on GitHub

### 4. References to keep open
- The official tutorial: <https://docs.python.org/3/tutorial/>
- The standard library docs: <https://docs.python.org/3/library/>
- *Automate the Boring Stuff with Python*, which is free to read online

## Final checklist

- [ ] My `todo.py` passes all the tests
- [ ] The app keeps my tasks after a restart
- [ ] Bad input doesn't crash it
- [ ] I've built at least one extension
- [ ] I've picked my next project
