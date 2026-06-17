#!/usr/bin/env python3
"""
PostToolUse hook: when today.md is edited, sync [x] items to tasks.json
and update today's daylog automatically.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

BRAIN = Path("/Users/dister/Projects/brain")
TODAY_MD = BRAIN / "05_PLANS/today.md"
TASKS_JSON = BRAIN / "05_PLANS/tasks/tasks.json"
DAYLOGS_DIR = BRAIN / "04_THINKING/daylogs"


def clean_title(raw: str) -> str:
    """Strip prefixes/suffixes added by daily-planner or carry-over logic."""
    title = raw.strip()
    # Remove [P=XX] prefix
    title = re.sub(r"^\[P=\d+\]\s*", "", title)
    # Remove deadline suffixes like "(дедлайн...)" or "(дедлайн просрочен...)"
    title = re.sub(r"\s*\(дедлайн[^)]*\)", "", title)
    # Remove trailing emoji
    title = re.sub(r"\s*[🔴🟢🟧]+$", "", title)
    return title.strip()


def extract_done_titles(content: str) -> list[str]:
    """Extract task titles from [x] lines in today.md."""
    titles = []
    for line in content.splitlines():
        # Match: - [x] YYYY-MM-DD Title  OR  - [x] Title
        m = re.match(r"^\s*-\s+\[x\]\s+(?:\d{4}-\d{2}-\d{2}\s+)?(.+)$", line)
        if m:
            titles.append(clean_title(m.group(1)))
    return titles


def main():
    # Read hook stdin to check which file was modified
    try:
        hook_data = json.load(sys.stdin)
    except Exception:
        return

    # Check if today.md was the file being written/edited
    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if "today.md" not in file_path:
        return

    if not TODAY_MD.exists() or not TASKS_JSON.exists():
        return

    today_content = TODAY_MD.read_text()
    done_titles = extract_done_titles(today_content)
    if not done_titles:
        return

    with open(TASKS_JSON) as f:
        data = json.load(f)

    tasks = data if isinstance(data, list) else data.get("tasks", [])
    today_str = date.today().isoformat()
    changed = 0

    for task in tasks:
        if task.get("status") == "done":
            continue
        if task.get("type") in ("area", "project"):
            continue
        task_title = task.get("title", "").strip()
        for done_title in done_titles:
            # Exact match only — prefix/substring matching caused false positives
            if done_title and done_title == task_title:
                task["status"] = "done"
                task["done_at"] = today_str
                changed += 1
                break

    if not changed:
        return

    # Write back tasks.json
    if isinstance(data, list):
        out = tasks
    else:
        data["tasks"] = tasks
        out = data

    with open(TASKS_JSON, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Update daylog
    daylog_path = update_daylog(today_str, done_titles)

    # Commit
    import subprocess
    commit_files = ["05_PLANS/tasks/tasks.json"]
    if daylog_path:
        rel = str(daylog_path.relative_to(BRAIN))
        commit_files.append(rel)

    result = subprocess.run(
        ["git", "add"] + commit_files,
        cwd=str(BRAIN),
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "commit", "-m", f"sync: close {changed} task(s) from today.md + daylog",
         "--", *commit_files],
        cwd=str(BRAIN),
        capture_output=True,
    )
    if result.returncode != 0:
        sys.stderr.write(f"git commit failed: {result.stderr.decode()}\n")


def update_daylog(date_str: str, done_titles: list[str]) -> Path | None:
    """Create or update daylog for date_str with done_titles. Returns path if changed."""
    DAYLOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = DAYLOGS_DIR / f"{date_str}.md"

    if path.exists():
        content = path.read_text()
        # Find existing entries to avoid duplicates
        existing = set()
        for line in content.splitlines():
            m = re.match(r"^- (.+)$", line)
            if m:
                existing.add(m.group(1).strip())

        new_entries = [t for t in done_titles if t and t not in existing]
        if not new_entries:
            return None

        # Append to "Задачи выполнены" section if it exists, otherwise append at end
        if "## Задачи выполнены" in content:
            lines = content.splitlines()
            insert_at = None
            in_section = False
            for i, line in enumerate(lines):
                if line.strip() == "## Задачи выполнены":
                    in_section = True
                    continue
                if in_section and line.startswith("## "):
                    insert_at = i
                    break
            if insert_at is None:
                insert_at = len(lines)
            for entry in new_entries:
                lines.insert(insert_at, f"- {entry}")
                insert_at += 1
            path.write_text("\n".join(lines) + "\n")
        else:
            entries_block = "\n".join(f"- {t}" for t in new_entries)
            path.write_text(content.rstrip() + f"\n\n## Задачи выполнены\n{entries_block}\n")
    else:
        entries_block = "\n".join(f"- {t}" for t in done_titles if t)
        path.write_text(
            f"# Лог дня {date_str}\n\n"
            f"## Задачи выполнены\n{entries_block}\n\n"
            f"## Не сделано\n_(заполнить в конце дня)_\n\n"
            f"## Заметки\n_(заполнить в конце дня)_\n"
        )

    return path


if __name__ == "__main__":
    main()
