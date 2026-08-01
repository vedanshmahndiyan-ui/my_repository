"""
Unit tests for to_do_app.py

Run with:  pytest test_to_do_app.py -v

Testing notes for future-you:
- The app keeps its data in module-level globals (`tasks`, `finished_tasks`)
  and a module-level `FILENAME`. Tests patch these per-test so nothing here
  ever touches your real tasks.txt, and so tests can't leak state into
  each other.
- `input()` is faked with `monkeypatch` so no test ever waits for a
  real keypress.
"""
import pytest
import to_do_app


@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """Runs before every test: fresh task lists + a throwaway file path."""
    monkeypatch.setattr(to_do_app, "tasks", [])
    monkeypatch.setattr(to_do_app, "finished_tasks", [])
    monkeypatch.setattr(to_do_app, "FILENAME", str(tmp_path / "test_tasks.txt"))
    yield


def fake_input(responses):
    """Returns a stand-in for input() that yields each item in `responses`
    in order, one per call. Raising when exhausted catches tests that
    ask for more input than they set up (a bug in the test, not the app)."""
    it = iter(responses)

    def _fake(prompt=""):
        return next(it)
    return _fake


# ---------- load_tasks / save_tasks ----------

def test_load_tasks_from_existing_file(tmp_path, monkeypatch):
    f = tmp_path / "existing.txt"
    f.write_text("Buy milk\nWalk the dog\n")
    monkeypatch.setattr(to_do_app, "FILENAME", str(f))

    to_do_app.load_tasks()

    assert to_do_app.tasks == ["Buy milk", "Walk the dog"]


def test_load_tasks_no_file_leaves_empty_list(tmp_path, monkeypatch):
    monkeypatch.setattr(to_do_app, "FILENAME", str(tmp_path / "does_not_exist.txt"))

    to_do_app.load_tasks()

    assert to_do_app.tasks == []


def test_save_tasks_writes_each_task_on_its_own_line():
    to_do_app.tasks.extend(["Buy milk", "Walk the dog"])

    to_do_app.save_tasks()

    with open(to_do_app.FILENAME) as f:
        assert f.read() == "Buy milk\nWalk the dog\n"


# ---------- initial_tasks ----------

def test_initial_tasks_adds_the_requested_number(monkeypatch):
    monkeypatch.setattr("builtins.input", fake_input(["2", "Buy milk", "Walk the dog"]))

    to_do_app.initial_tasks()

    assert to_do_app.tasks == ["Buy milk", "Walk the dog"]


def test_initial_tasks_rejects_non_numeric_input(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", fake_input(["banana"]))

    to_do_app.initial_tasks()

    assert to_do_app.tasks == []
    assert "Invalid input" in capsys.readouterr().out


# ---------- view_tasks ----------

def test_view_tasks_lists_items_with_1_based_numbering(capsys):
    to_do_app.tasks.extend(["Buy milk", "Walk the dog"])

    to_do_app.view_tasks()

    out = capsys.readouterr().out
    assert "1. Buy milk" in out
    assert "2. Walk the dog" in out


def test_view_tasks_empty_list_shows_empty_message(capsys):
    to_do_app.view_tasks()

    assert "empty" in capsys.readouterr().out.lower()


# ---------- add_task ----------

def test_add_task_appends_and_saves(monkeypatch):
    monkeypatch.setattr("builtins.input", fake_input(["Buy milk"]))

    to_do_app.add_task()

    assert to_do_app.tasks == ["Buy milk"]
    with open(to_do_app.FILENAME) as f:
        assert f.read() == "Buy milk\n"


# ---------- finish_task ----------

def test_finish_task_on_empty_list_does_nothing(capsys):
    to_do_app.finish_task()

    assert "empty" in capsys.readouterr().out.lower()


def test_finish_task_moves_valid_task_to_finished(monkeypatch):
    to_do_app.tasks.extend(["Buy milk", "Walk the dog"])
    monkeypatch.setattr("builtins.input", fake_input(["1"]))

    to_do_app.finish_task()

    assert to_do_app.tasks == ["Walk the dog"]
    assert to_do_app.finished_tasks == ["Buy milk"]


def test_finish_task_rejects_out_of_range_number(monkeypatch, capsys):
    to_do_app.tasks.append("Buy milk")
    monkeypatch.setattr("builtins.input", fake_input(["5"]))

    to_do_app.finish_task()

    assert to_do_app.tasks == ["Buy milk"]
    assert "Invalid task number" in capsys.readouterr().out


def test_finish_task_rejects_non_numeric_choice(monkeypatch, capsys):
    to_do_app.tasks.append("Buy milk")
    monkeypatch.setattr("builtins.input", fake_input(["abc"]))

    to_do_app.finish_task()

    assert to_do_app.tasks == ["Buy milk"]
    assert "valid numeric digit" in capsys.readouterr().out


# ---------- task_update ----------

def test_task_update_with_only_start_date_updates_in_place(monkeypatch):
    to_do_app.tasks.append("Buy milk")
    # inputs in order: task number, start date, end date (blank = not finished)
    monkeypatch.setattr("builtins.input", fake_input(["1", "2026-08-01", ""]))

    to_do_app.task_update()

    assert to_do_app.tasks == ["Buy milk | 2026-08-01"]
    assert to_do_app.finished_tasks == []


def test_task_update_with_end_date_marks_finished(monkeypatch):
    to_do_app.tasks.append("Buy milk")
    monkeypatch.setattr("builtins.input", fake_input(["1", "2026-08-01", "2026-08-02"]))

    to_do_app.task_update()

    assert to_do_app.tasks == []
    assert to_do_app.finished_tasks == ["Buy milk | 2026-08-01 | 2026-08-02"]


def test_task_update_on_empty_list_does_nothing(capsys):
    to_do_app.task_update()

    assert "empty" in capsys.readouterr().out.lower()


def test_task_update_rejects_out_of_range_number(monkeypatch, capsys):
    to_do_app.tasks.append("Buy milk")
    monkeypatch.setattr("builtins.input", fake_input(["9"]))

    to_do_app.task_update()

    assert to_do_app.tasks == ["Buy milk"]
    assert "Invalid task number" in capsys.readouterr().out


# ---------- quit_app ----------

def test_quit_app_exits(capsys):
    with pytest.raises(SystemExit):
        to_do_app.quit_app()

    assert "Goodbye" in capsys.readouterr().out
