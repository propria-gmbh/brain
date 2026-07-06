"""Tests for today_server.py — tasks.json-only dashboard."""
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))
import today_server as srv

TODAY = date.today().isoformat()
TOMORROW = (date.today().replace(day=date.today().day + 1)).isoformat()


def make_task(task_id="t1", title="Test Task", **kwargs):
    return {"id": task_id, "title": title, "type": "task", "status": "todo", "order": 0.0, **kwargs}


def write_tasks(tmp_path, tasks):
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(tasks), encoding="utf-8")
    return f


# ── set_task_scheduled_date ───────────────────────────────

def test_set_scheduled_date_sets_field(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1")])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_scheduled_date("t1", TODAY)
    result = json.loads(tasks_file.read_text())
    assert result[0]["scheduled_date"] == TODAY


def test_set_scheduled_date_clears_field(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1", scheduled_date=TODAY)])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_scheduled_date("t1", None)
    result = json.loads(tasks_file.read_text())
    assert "scheduled_date" not in result[0]


def test_set_scheduled_date_unknown_id_is_noop(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1")])
    original = tasks_file.read_text()
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_scheduled_date("nonexistent", TODAY)
    assert json.loads(tasks_file.read_text()) == json.loads(original)


# ── set_task_context ──────────────────────────────────────

def test_set_context_sets_field(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1")])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_context("t1", "perekur")
    result = json.loads(tasks_file.read_text())
    assert result[0]["context"] == "perekur"


def test_set_context_clears_field(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1", context="deep")])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_context("t1", None)
    result = json.loads(tasks_file.read_text())
    assert result[0].get("context") is None


# ── scheduled tasks appear in render_today ───────────────

def test_render_today_shows_scheduled_date_task(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Deep Work Task", scheduled_date=TODAY, context="deep")
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"), \
         patch("subprocess.run"):
        html = srv.render_today()
    assert "Deep Work Task" in html


def test_render_today_shows_deadline_task(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Deadline Task", deadline=TODAY, context="afternoon")
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"), \
         patch("subprocess.run"):
        html = srv.render_today()
    assert "Deadline Task" in html


def test_render_today_excludes_future_scheduled(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Future Task", scheduled_date=TOMORROW, context="deep")
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"), \
         patch("subprocess.run"):
        html = srv.render_today()
    assert "Future Task" not in html


def test_render_today_excludes_done_tasks(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Done Task", scheduled_date=TODAY, status="done")
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"), \
         patch("subprocess.run"):
        html = srv.render_today()
    assert "Done Task" not in html


def test_render_today_groups_by_context(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Deep Task", scheduled_date=TODAY, context="deep"),
        make_task("t2", title="Perekur Task", scheduled_date=TODAY, context="perekur"),
        make_task("t3", title="Afternoon Task", scheduled_date=TODAY, context="afternoon"),
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"), \
         patch("subprocess.run"):
        html = srv.render_today()
    # All three tasks present
    assert "Deep Task" in html
    assert "Perekur Task" in html
    assert "Afternoon Task" in html
    # Section headers present
    assert "Задачи" in html
    assert "Перекур" in html
    assert "половина" in html


# ── reset_daily_recurring ─────────────────────────────────

def test_reset_daily_recurring_resets_status_and_counts_miss(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", recurring="daily", status="todo", last_reset_date="2020-01-01", missed_count=0)
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        tasks = srv.load_tasks()
        srv.reset_daily_recurring(tasks)
    result = json.loads(tasks_file.read_text())
    assert result[0]["status"] == "todo"
    assert result[0]["last_reset_date"] == TODAY
    assert result[0]["missed_count"] == 1


def test_reset_daily_recurring_no_miss_if_done(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", recurring="daily", status="done", last_reset_date="2020-01-01", missed_count=0)
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        tasks = srv.load_tasks()
        srv.reset_daily_recurring(tasks)
    result = json.loads(tasks_file.read_text())
    assert result[0]["status"] == "todo"
    assert result[0]["missed_count"] == 0


def test_reset_daily_recurring_noop_if_already_reset_today(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", recurring="daily", status="done", last_reset_date=TODAY, missed_count=0)
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        tasks = srv.load_tasks()
        srv.reset_daily_recurring(tasks)
    result = json.loads(tasks_file.read_text())
    assert result[0]["status"] == "done"


# ── set_main_task_date ────────────────────────────────────

def test_set_main_task_date_sets_and_clears_others(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", main_task_date=TODAY),
        make_task("t2"),
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_main_task_date("t2")
    result = json.loads(tasks_file.read_text())
    by_id = {t["id"]: t for t in result}
    assert "main_task_date" not in by_id["t1"]
    assert by_id["t2"]["main_task_date"] == TODAY


# ── set_task_assignee ─────────────────────────────────────

def test_set_task_assignee_toggles(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("t1")])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_assignee("t1")
    result = json.loads(tasks_file.read_text())
    assert result[0]["assignee"] == "claude"
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.set_task_assignee("t1")
    result = json.loads(tasks_file.read_text())
    assert result[0]["assignee"] is None


# ── mark_event_done ───────────────────────────────────────

def test_mark_event_done_creates_linked_task(tmp_path):
    tasks_file = write_tasks(tmp_path, [])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "write_daylog_entries"), \
         patch("subprocess.run"):
        srv.mark_event_done("Team Meeting", TODAY)
    result = json.loads(tasks_file.read_text())
    ev = next(t for t in result if t.get("type") == "event")
    assert ev["event_summary"] == "Team Meeting"
    assert ev["event_date"] == TODAY
    assert ev["status"] == "done"


def test_mark_event_done_toggles_existing(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        {"id": "event-x", "title": "X", "type": "event", "event_summary": "X",
         "event_date": TODAY, "status": "done", "done_at": TODAY}
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch.object(srv, "write_daylog_entries"), \
         patch("subprocess.run"):
        srv.mark_event_done("X", TODAY)
    result = json.loads(tasks_file.read_text())
    assert result[0]["status"] == "todo"


# ── task without children invariant ───────────────────────

def test_add_subtask_promotes_parent_to_area(tmp_path):
    tasks_file = write_tasks(tmp_path, [make_task("parent", title="Parent")])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.add_task_inbox("Child", parent_id="parent")
    result = json.loads(tasks_file.read_text())
    parent = next(t for t in result if t["id"] == "parent")
    assert parent["type"] == "area"


# ── task_row contains schedule button ────────────────────

def test_task_row_contains_schedule_button():
    task = make_task("t1", title="Sample")
    html = srv.render_task_row(task, [task])
    assert "today-btn" in html


def test_task_row_schedule_button_active_when_scheduled_today():
    task = make_task("t1", title="Sample", scheduled_date=TODAY)
    html = srv.render_task_row(task, [task])
    assert "active" in html and "today-btn" in html


# ── add_task_inbox with context and marker ───────────────

def test_add_task_inbox_sets_context(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        {"id": "area-inbox", "title": "Inbox", "type": "area", "order": -1}
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.add_task_inbox("Test task", context="perekur", marker="🔴")
    result = json.loads(tasks_file.read_text())
    new_task = next(t for t in result if t.get("title") == "Test task")
    assert new_task["context"] == "perekur"
    assert new_task["marker"] == "🔴"
    assert new_task["priority"] == "red"


def test_add_task_inbox_no_context_marker(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        {"id": "area-inbox", "title": "Inbox", "type": "area", "order": -1}
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "UNDO_FILE", tmp_path / "undo.json"), \
         patch("subprocess.run"):
        srv.add_task_inbox("Plain task")
    result = json.loads(tasks_file.read_text())
    new_task = next(t for t in result if t.get("title") == "Plain task")
    assert "context" not in new_task
    assert "marker" not in new_task


# ── api/task includes scheduled_date and context ─────────

def test_api_task_includes_scheduled_date(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", scheduled_date=TODAY, context="perekur")
    ])
    with patch.object(srv, "TASKS_FILE", tasks_file):
        tasks = srv.load_tasks()
    t = next(x for x in tasks if x["id"] == "t1")
    assert t["scheduled_date"] == TODAY
    assert t["context"] == "perekur"
