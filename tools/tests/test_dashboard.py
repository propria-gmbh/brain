"""Tests for today_server.py — scheduled_date feature."""
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


def write_today(tmp_path, content):
    f = tmp_path / "today.md"
    f.write_text(content, encoding="utf-8")
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
    today_file = write_today(tmp_path, "# План на " + TODAY + "\n\n## Утренний чеклист\n\n## Сделано\n")
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "TODAY", today_file), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"):
        html = srv.render_today(today_file)
    assert "Deep Work Task" in html


def test_render_today_shows_deadline_task(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Deadline Task", deadline=TODAY, context="afternoon")
    ])
    today_file = write_today(tmp_path, "# План\n\n## Утренний чеклист\n\n## Сделано\n")
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "TODAY", today_file), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"):
        html = srv.render_today(today_file)
    assert "Deadline Task" in html


def test_render_today_excludes_future_scheduled(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Future Task", scheduled_date=TOMORROW, context="deep")
    ])
    today_file = write_today(tmp_path, "# План\n\n## Утренний чеклист\n\n## Сделано\n")
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "TODAY", today_file), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"):
        html = srv.render_today(today_file)
    assert "Future Task" not in html


def test_render_today_excludes_done_tasks(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Done Task", scheduled_date=TODAY, status="done")
    ])
    today_file = write_today(tmp_path, "# План\n\n## Утренний чеклист\n\n## Сделано\n")
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "TODAY", today_file), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"):
        html = srv.render_today(today_file)
    assert "Done Task" not in html


def test_render_today_groups_by_context(tmp_path):
    tasks_file = write_tasks(tmp_path, [
        make_task("t1", title="Deep Task", scheduled_date=TODAY, context="deep"),
        make_task("t2", title="Perekur Task", scheduled_date=TODAY, context="perekur"),
        make_task("t3", title="Afternoon Task", scheduled_date=TODAY, context="afternoon"),
    ])
    today_file = write_today(tmp_path, "# План\n\n## Утренний чеклист\n\n## Сделано\n")
    with patch.object(srv, "TASKS_FILE", tasks_file), \
         patch.object(srv, "TODAY", today_file), \
         patch.object(srv, "CALENDAR_CACHE", tmp_path / "cal.json"):
        html = srv.render_today(today_file)
    # All three tasks present
    assert "Deep Task" in html
    assert "Perekur Task" in html
    assert "Afternoon Task" in html
    # Section headers present
    assert "Задачи" in html
    assert "Перекур" in html
    assert "половина" in html


# ── task_row contains schedule button ────────────────────

def test_task_row_contains_schedule_button():
    task = make_task("t1", title="Sample")
    html = srv.render_task_row(task, [task])
    assert "today-btn" in html


def test_task_row_schedule_button_active_when_scheduled_today():
    task = make_task("t1", title="Sample", scheduled_date=TODAY)
    html = srv.render_task_row(task, [task])
    assert "active" in html and "today-btn" in html


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
