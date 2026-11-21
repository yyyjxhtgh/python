# Learn Python in 7 Days

A hands-on plan that takes you from zero to writing your own small programs.
Plan on about **1.5–2.5 hours a day**: roughly 30–45 minutes reading the lesson
and typing out the examples, then the rest on the exercises.

## How each day works

Each `dayN/` folder has three files:

| File | What it is for |
|------|----------------|
| `lesson.md` | The concepts, with short examples. **Type the examples out yourself** instead of copy-pasting. |
| `exercises.py` | Functions for you to fill in. Run the file and it checks your work. |
| `solutions.py` | Worked answers. Open it only after a real attempt, or when you've been stuck for 15+ minutes. |

Running the exercises gives you feedback right away:

```
$ python day1/exercises.py
✅ greet
❌ celsius_to_fahrenheit: celsius_to_fahrenheit(100) should be 212, got 180
⏳ seconds_to_hms: not done yet
...
1/5 passed
```

Keep editing and re-running until every line shows ✅.

## The 7-day schedule

| Day | Topic | You will be able to... |
|-----|-------|------------------------|
| [1](day1/lesson.md) | **Setup & basics**: `print`, variables, numbers, strings, `input` | Write and run a script that does calculations and formats text |
| [2](day2/lesson.md) | **Making decisions & repeating**: `if`/`elif`/`else`, `for`, `while`, `range` | Write programs that react to data and loop over it |
| [3](day3/lesson.md) | **Collections**: lists, tuples, dictionaries, sets, comprehensions | Store and transform groups of data |
| [4](day4/lesson.md) | **Functions & modules**: parameters, return values, scope, `import` | Split a program into reusable pieces and use the standard library |
| [5](day5/lesson.md) | **Files & errors**: reading/writing files, `try`/`except`, JSON | Save and load data and handle things going wrong |
| [6](day6/lesson.md) | **Classes & tools**: OOP basics, virtual environments, `pip`, testing | Model real things with classes and use other people's packages |
| [7](day7/lesson.md) | **Project**: build a command-line to-do app | Put everything together in a real program, then plan what to learn next |

## Setup (do this before Day 1)

1. **Install Python 3.10 or newer** from <https://www.python.org/downloads/>.
   On Windows, tick **"Add Python to PATH"** in the installer.
2. Check that it works. Open a terminal (Terminal on macOS/Linux, PowerShell on Windows):
   ```
   python --version
   ```
   If that fails, try `python3 --version` and use `python3` everywhere this course says `python`.
3. **Install an editor.** [VS Code](https://code.visualstudio.com/) with the
   *Python* extension is a good free choice.
4. Get this folder onto your computer (`git clone` it or download the ZIP),
   open it in your editor, and run the following from the folder:
   ```
   python day1/exercises.py
   ```
   You should see a list of ⏳ "not done yet" lines. That means you're ready.

## Tips that make the week work

- **Type, don't paste.** Your fingers learn the syntax faster than your eyes do.
- **Use the REPL.** Run `python` with no file to get an interactive `>>>` prompt
  where you can try one line at a time. Type `exit()` to leave it.
- **Read error messages from the bottom up.** The last line says *what* went
  wrong, and the lines above it say *where*.
- **Break things on purpose.** Remove a colon or misspell a variable, then
  read the error. You'll recognize it the next time you see it.
- **Use `print()` everywhere.** When you're confused, print the value and its
  type: `print(x, type(x))`.
- **Don't skip days to catch up.** If you fall behind, slide the schedule back.
  Each day builds on the one before.
