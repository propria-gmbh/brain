#!/usr/bin/env python3
"""
Migrate markdown task files to tasks.json.
Only migrates open (uncompleted) tasks.
"""

import json
import re
import unicodedata
from pathlib import Path
from datetime import date

BRAIN_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BRAIN_DIR / "05_PLANS/tasks/tasks.json"
TODAY = str(date.today())

FILE_TO_PROJECT = {
    "ecom.md": "ecom",
    "propria.md": "propria",
    "ai-systems.md": "ai-systems",
    "projects.md": "projects",
    "personal/development.md": "personal/development",
    "personal/family.md": "personal/family",
    "personal/finance.md": "personal/finance",
    "personal/home.md": "personal/home",
    "personal/media.md": "personal/media",
    "personal/purchases.md": "personal/purchases",
    "personal/sailing.md": "personal/sailing",
}

PRIORITY_MAP = {"🔴": "red", "🟢": "green", "🟧": "orange"}
STAKES_MAP = {"$$$$$": 5, "$$$$": 4, "$$$": 3, "$$": 2, "$": 1}
SKIP_SECTIONS = {"Сделано", "Правила работы с AB Coaching"}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text.strip())
    return text.lower()[:45].rstrip("-")


def parse_deadline(raw: str):
    m = re.search(r"\(дедлайн (\d{4}-\d{2}-\d{2})\)", raw)
    if m:
        return m.group(1)
    # (YYYY-MM-DD) or (YYYY-MM-DD extra text) — date must come first inside parens
    m = re.search(r"\((\d{4}-\d{2}-\d{2})(?:\s+[^)]+)?\)", raw)
    if m:
        return m.group(1)
    return None


def parse_stakes(raw: str):
    m = re.search(r"\[(\$+)\]", raw)
    return STAKES_MAP.get(m.group(1)) if m else None


def parse_tags(raw: str) -> list:
    hashtags = re.findall(r"#([\w-]+)", raw)
    bracket_tags = re.findall(r"\[(after-[^\]]+|optimizing)\]", raw)
    return hashtags + bracket_tags


def clean_title(raw: str) -> str:
    t = raw
    for emoji in PRIORITY_MAP:
        t = t.replace(emoji, "")
    t = re.sub(r"\[someday\]", "", t)
    t = re.sub(r"\[\$+\]", "", t)
    t = re.sub(r"#[\w-]+", "", t)
    t = re.sub(r"\[after-[^\]]+\]", "", t)
    t = re.sub(r"\[optimizing\]", "", t)
    t = re.sub(r"\(дедлайн \d{4}-\d{2}-\d{2}\)", "", t)
    t = re.sub(r"\(\d{4}-\d{2}-\d{2}(?:\s+[^)]+)?\)", "", t)
    return re.sub(r"\s+", " ", t).strip()


def make_id(project: str, title: str, used: set) -> str:
    prefix = project.replace("/", "-")
    base = f"{prefix}-{slugify(title)}"
    if base not in used:
        return base
    i = 2
    while f"{base}-{i}" in used:
        i += 1
    return f"{base}-{i}"


def parse_file(path: Path, project: str) -> list:
    tasks = []
    used_ids: set = set()
    current_section = None
    parent_stack: list[tuple[int, str]] = []
    order_counter: dict = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        # Section header (##)
        if re.match(r"^## ", line):
            section_name = line[3:].strip()
            current_section = None if section_name in SKIP_SECTIONS else section_name
            # Only pop top-level parents on section change
            parent_stack = [e for e in parent_stack if e[0] < 0]  # clear all
            continue

        if current_section is None and any(
            s in (line[3:].strip() if line.startswith("## ") else "") for s in SKIP_SECTIONS
        ):
            continue

        m = re.match(r"^(\s*)- \[ \] (.+)$", line)
        if not m:
            continue

        indent = len(m.group(1))
        raw = m.group(2).strip()

        priority = next((v for k, v in PRIORITY_MAP.items() if k in raw), None)
        someday = "[someday]" in raw
        deadline = parse_deadline(raw)
        stakes = parse_stakes(raw)
        tags = parse_tags(raw)
        title = clean_title(raw)
        if not title:
            continue

        # Update parent stack
        while parent_stack and parent_stack[-1][0] >= indent:
            parent_stack.pop()

        parent_id = parent_stack[-1][1] if parent_stack else None
        task_type = "checklist" if parent_id else "task"

        key = (project, current_section, parent_id)
        order_counter[key] = order_counter.get(key, 0) + 1

        task_id = make_id(project, title, used_ids)
        used_ids.add(task_id)

        task = {
            "id": task_id,
            "title": title,
            "type": task_type,
            "project": project,
            "section": current_section,
            "parent_id": parent_id,
            "status": "todo",
            "someday": someday,
            "deadline": deadline,
            "priority": priority,
            "stakes": stakes,
            "context": None,
            "goal": "health" if project == "health" else None,
            "tags": tags,
            "notes": None,
            "waiting_for": None,
            "done_at": None,
            "created_at": TODAY,
            "order": float(order_counter[key]),
        }
        tasks.append(task)
        parent_stack.append((indent, task_id))

    return tasks


def main():
    tasks_dir = BRAIN_DIR / "05_PLANS/tasks"
    all_tasks = []

    health_file = BRAIN_DIR / "08_PROJECTS/health.md"
    if health_file.exists():
        tasks = parse_file(health_file, "health")
        all_tasks.extend(tasks)
        print(f"  health.md: {len(tasks)} tasks")

    for rel, project in FILE_TO_PROJECT.items():
        path = tasks_dir / rel
        if path.exists():
            tasks = parse_file(path, project)
            all_tasks.extend(tasks)
            print(f"  {rel}: {len(tasks)} tasks")
        else:
            print(f"  {rel}: NOT FOUND")

    OUTPUT_FILE.write_text(
        json.dumps(all_tasks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nTotal: {len(all_tasks)} tasks → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
