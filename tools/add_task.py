#!/usr/bin/env python3
"""Quick task creation: python3 tools/add_task.py "Title" [--area ID] [--someday] [--notes "..."] [--deadline YYYY-MM-DD]"""

import argparse
import json
import os
import re
import subprocess
from datetime import date

TASKS_FILE = os.path.join(os.path.dirname(__file__), "../05_PLANS/tasks/tasks.json")
DEFAULT_AREA = "area-inbox"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[\s/\\]+", "-", text)
    text = re.sub(r"[^\w\-а-яёА-ЯЁ]", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]


def main():
    parser = argparse.ArgumentParser(description="Add a task to tasks.json")
    parser.add_argument("title", help="Task title")
    parser.add_argument("--area", default=DEFAULT_AREA, help="Area ID (default: area-inbox)")
    parser.add_argument("--someday", action="store_true", help="Mark as someday")
    parser.add_argument("--notes", default=None, help="Notes")
    parser.add_argument("--deadline", default=None, help="Deadline YYYY-MM-DD")
    args = parser.parse_args()

    with open(TASKS_FILE) as f:
        data = json.load(f)

    # Validate area exists
    area_ids = {x["id"] for x in data if x.get("type") == "area"}
    parent_id = args.area if args.area in area_ids else DEFAULT_AREA
    if parent_id != args.area:
        print(f"[warn] area '{args.area}' not found, using {DEFAULT_AREA}")

    task_id = slugify(args.title)
    # Avoid collision
    existing_ids = {x.get("id", "") for x in data}
    base_id = task_id
    counter = 2
    while task_id in existing_ids:
        task_id = f"{base_id}-{counter}"
        counter += 1

    task = {
        "id": task_id,
        "title": args.title,
        "type": "task",
        "parent_id": parent_id,
        "status": "todo",
        "someday": args.someday,
        "deadline": args.deadline,
        "priority": None,
        "stakes": None,
        "context": None,
        "goal": None,
        "tags": [],
        "notes": args.notes,
        "waiting_for": None,
        "done_at": None,
        "created_at": date.today().isoformat(),
        "order": 0.0,
    }

    data.append(task)

    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    repo = os.path.join(os.path.dirname(__file__), "..")
    subprocess.run(
        ["git", "add", "05_PLANS/tasks/tasks.json"],
        cwd=repo, check=True
    )
    subprocess.run(
        ["git", "commit", "-m", f"add: {args.title}"],
        cwd=repo, check=True
    )

    area_label = parent_id.replace("area-", "")
    print(f"[задача создана: \"{args.title}\" / {area_label}]")


if __name__ == "__main__":
    main()
