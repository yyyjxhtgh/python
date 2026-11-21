"""Tests for the Day 7 to-do app.

Run with pytest (see Day 6):   pytest day7
Or without pytest:            python day7/test_todo.py

These tests check YOUR todo.py. To run them against the finished version,
set TODO_MODULE=todo_solution first, for example:
    TODO_MODULE=todo_solution pytest day7          (macOS / Linux)
    $env:TODO_MODULE="todo_solution"; pytest day7  (Windows PowerShell)
"""

import importlib
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
todo = importlib.import_module(os.environ.get("TODO_MODULE", "todo"))


def make_tasks():
    tasks = []
    todo.add_task(tasks, "Buy milk")
    todo.add_task(tasks, "Learn Python")
    todo.add_task(tasks, "Call mum")
    return tasks


def expect_value_error(func, *args):
    try:
        func(*args)
    except ValueError:
        return
    raise AssertionError(f"{func.__name__}{args} should raise ValueError")


def test_add_task():
    tasks = []
    task = todo.add_task(tasks, "  Buy milk  ")
    assert task == {"title": "Buy milk", "done": False, "created": date.today().isoformat()}
    assert tasks == [task]


def test_add_empty_task_is_rejected():
    tasks = []
    expect_value_error(todo.add_task, tasks, "   ")
    assert tasks == []


def test_complete_task():
    tasks = make_tasks()
    task = todo.complete_task(tasks, 2)
    assert task["title"] == "Learn Python"
    assert tasks[1]["done"] is True
    assert tasks[0]["done"] is False


def test_complete_bad_number():
    tasks = make_tasks()
    expect_value_error(todo.complete_task, tasks, 0)
    expect_value_error(todo.complete_task, tasks, 4)


def test_delete_task():
    tasks = make_tasks()
    removed = todo.delete_task(tasks, 1)
    assert removed["title"] == "Buy milk"
    assert [t["title"] for t in tasks] == ["Learn Python", "Call mum"]
    expect_value_error(todo.delete_task, tasks, 3)


def test_clear_completed_changes_the_same_list():
    tasks = make_tasks()
    original = tasks
    todo.complete_task(tasks, 1)
    todo.complete_task(tasks, 3)
    assert todo.clear_completed(tasks) == 2
    assert original is tasks
    assert [t["title"] for t in tasks] == ["Learn Python"]


def test_pending_count():
    tasks = make_tasks()
    assert todo.pending_count(tasks) == 3
    todo.complete_task(tasks, 1)
    assert todo.pending_count(tasks) == 2


def test_format_tasks():
    assert todo.format_tasks([]) == "No tasks yet."
    tasks = make_tasks()
    todo.complete_task(tasks, 2)
    assert todo.format_tasks(tasks) == "1. [ ] Buy milk\n2. [x] Learn Python\n3. [ ] Call mum"


def test_save_and_load(tmp_path):
    path = tmp_path / "tasks.json"
    assert todo.load_tasks(path) == []          # missing file
    tasks = make_tasks()
    todo.save_tasks(path, tasks)
    assert todo.load_tasks(path) == tasks
    path.write_text("{broken", encoding="utf-8")
    assert todo.load_tasks(path) == []          # broken file


if __name__ == "__main__":
    # A tiny stand-in for pytest so this file also runs on its own.
    import tempfile

    tests = [(name, func) for name, func in sorted(globals().items()) if name.startswith("test_")]
    passed = 0
    for name, func in tests:
        try:
            if "tmp_path" in func.__code__.co_varnames[: func.__code__.co_argcount]:
                with tempfile.TemporaryDirectory() as folder:
                    func(Path(folder))
            else:
                func()
        except NotImplementedError:
            print(f"⏳ {name}: not done yet")
        except AssertionError as error:
            print(f"❌ {name}: {error or 'assertion failed'}")
        except Exception as error:
            print(f"💥 {name}: {type(error).__name__}: {error}")
        else:
            print(f"✅ {name}")
            passed += 1
    print(f"\n{passed}/{len(tests)} passed")
