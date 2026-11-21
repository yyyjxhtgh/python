"""Day 7 project, finished version: a command-line to-do app.

Try building todo.py yourself first! Run this with:
    python day7/todo_solution.py

It uses ideas from every day of the week:
  Day 1  strings and f-strings        Day 4  functions and imports
  Day 2  if/elif and a while loop     Day 5  JSON files and try/except
  Day 3  a list of dicts              Day 6  tests in test_todo.py
"""

import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "tasks.json"


# --- Storage -----------------------------------------------------------

def load_tasks(path):
    """Return the saved list of tasks, or [] if the file is missing or broken."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(path, tasks):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


# --- Task operations ---------------------------------------------------

def add_task(tasks, title):
    """Add a new, unfinished task and return it. Empty titles aren't allowed."""
    title = title.strip()
    if not title:
        raise ValueError("Task title can't be empty")
    task = {"title": title, "done": False, "created": date.today().isoformat()}
    tasks.append(task)
    return task


def _index_for(tasks, number):
    """Turn a 1-based task number into a list index, checking that it exists."""
    if not 1 <= number <= len(tasks):
        raise ValueError(f"There is no task #{number}")
    return number - 1


def complete_task(tasks, number):
    """Mark task `number` (counting from 1) as done and return it."""
    task = tasks[_index_for(tasks, number)]
    task["done"] = True
    return task


def delete_task(tasks, number):
    """Remove task `number` (counting from 1) and return it."""
    return tasks.pop(_index_for(tasks, number))


def clear_completed(tasks):
    """Remove every finished task in place and return how many were removed."""
    before = len(tasks)
    tasks[:] = [task for task in tasks if not task["done"]]
    return before - len(tasks)


def pending_count(tasks):
    return sum(1 for task in tasks if not task["done"])


def format_tasks(tasks):
    """Return the task list as text, for example "1. [x] Buy milk"."""
    if not tasks:
        return "No tasks yet."
    lines = []
    for number, task in enumerate(tasks, start=1):
        mark = "x" if task["done"] else " "
        lines.append(f"{number}. [{mark}] {task['title']}")
    return "\n".join(lines)


# --- User interface ----------------------------------------------------

MENU = """
What would you like to do?
  [l] List tasks     [a] Add task      [d] Mark done
  [r] Remove task    [c] Clear done    [q] Quit
"""


def ask_number(prompt):
    while True:
        text = input(prompt)
        try:
            return int(text)
        except ValueError:
            print("Please type a number.")


def main():
    tasks = load_tasks(DATA_FILE)
    print(f"📝 To-do list: {pending_count(tasks)} task(s) left to do.")

    while True:
        print(MENU)
        choice = input("> ").strip().lower()

        try:
            if choice == "l":
                print(format_tasks(tasks))
            elif choice == "a":
                task = add_task(tasks, input("Task: "))
                print(f"Added: {task['title']}")
            elif choice == "d":
                print(format_tasks(tasks))
                task = complete_task(tasks, ask_number("Number to mark done: "))
                print(f"Nice work! Finished: {task['title']}")
            elif choice == "r":
                print(format_tasks(tasks))
                task = delete_task(tasks, ask_number("Number to remove: "))
                print(f"Removed: {task['title']}")
            elif choice == "c":
                print(f"Cleared {clear_completed(tasks)} finished task(s).")
            elif choice == "q":
                print("Bye!")
                break
            else:
                print("Unknown option, try again.")
                continue
        except ValueError as error:
            print(f"⚠️  {error}")
            continue

        save_tasks(DATA_FILE, tasks)   # save after every change


if __name__ == "__main__":
    main()
