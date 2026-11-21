"""Day 7 project: a command-line to-do app. Your version!

Fill in the functions marked TODO, in order. Test as you go with:
    pytest day7          (or: python day7/test_todo.py)
Then use the app for real:
    python day7/todo.py

Each task is stored as a dict, like this:
    {"title": "Buy milk", "done": False, "created": "2026-11-21"}
and the whole to-do list is a list of those dicts.
"""

import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "tasks.json"


# --- Storage (Day 5) ---------------------------------------------------

def load_tasks(path):
    """Return the saved list of tasks, or [] if the file is missing or broken."""
    # TODO: open the file and json.load it. Catch FileNotFoundError and
    #       json.JSONDecodeError and return [] in that case.
    raise NotImplementedError


def save_tasks(path, tasks):
    """Write the tasks list to `path` as JSON."""
    # TODO
    raise NotImplementedError


# --- Task operations (Days 2-4) ----------------------------------------

def add_task(tasks, title):
    """Add a new, unfinished task to `tasks` and return it.

    - Strip spaces from the title. If it's empty, raise ValueError.
    - "created" should be today's date: date.today().isoformat()
    """
    # TODO
    raise NotImplementedError


def complete_task(tasks, number):
    """Mark task `number` as done and return it.

    `number` counts from 1, the way people count, so task 1 is tasks[0].
    Raise ValueError if there's no task with that number.
    """
    # TODO
    raise NotImplementedError


def delete_task(tasks, number):
    """Remove task `number` (counting from 1) and return it.
    Raise ValueError if there's no task with that number.
    """
    # TODO
    raise NotImplementedError


def clear_completed(tasks):
    """Remove every finished task and return how many were removed.

    Careful: change the list itself, don't make a new one. Tip: assigning
    to tasks[:] replaces the contents of the existing list.
    """
    # TODO
    raise NotImplementedError


def pending_count(tasks):
    """Return how many tasks aren't done yet."""
    # TODO
    raise NotImplementedError


def format_tasks(tasks):
    """Return the tasks as text, one per line, numbered from 1:

        1. [ ] Buy milk
        2. [x] Learn Python

    If there are no tasks, return "No tasks yet."
    Hint: enumerate(tasks, start=1) and "\\n".join(lines)
    """
    # TODO
    raise NotImplementedError


# --- User interface (done for you, but read it!) -----------------------

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
