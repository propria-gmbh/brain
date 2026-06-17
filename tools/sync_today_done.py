#!/usr/bin/env python3
"""
PostToolUse hook: when today.md is edited, sync [x] items to tasks.json.
Reads tool call info from stdin (JSON), checks if today.md was modified,
then marks matching tasks as done in tasks.json.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

TODAY_MD = Path("/Users/dister/Projects/brain/05_PLANS/today.md")
TASKS_JSON = Path("/Users/dister/Projects/brain/05_PLANS/tasks/tasks.json")


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

    # Write back
    if isinstance(data, list):
        out = tasks
    else:
        data["tasks"] = tasks
        out = data

    with open(TASKS_JSON, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Commit
    import subprocess
    result = subprocess.run(
        ["git", "commit", "-m", f"sync: close {changed} task(s) from today.md",
         "--", "05_PLANS/tasks/tasks.json"],
        cwd="/Users/dister/Projects/brain",
        capture_output=True,
    )
    if result.returncode != 0:
        sys.stderr.write(f"git commit failed: {result.stderr.decode()}\n")


if __name__ == "__main__":
    main()
