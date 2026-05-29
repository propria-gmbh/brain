#!/usr/bin/env python3
"""Migrate tasks.json: project+section → area hierarchy with parent_id."""

import json
import re
from pathlib import Path
from collections import defaultdict

TASKS_FILE = Path(__file__).parent.parent / "05_PLANS/tasks/tasks.json"
BAK_FILE = TASKS_FILE.with_suffix(".json.bak2")

PROJ_ORDER = [
    "health", "ecom", "propria", "ai-systems",
    "personal/finance", "personal/home", "personal/purchases", "personal/media",
    "personal/family", "personal/sailing", "personal/development", "projects",
]

PROJ_LABELS = {
    "health": "Здоровье",
    "ecom": "Ecom",
    "propria": "Propria",
    "ai-systems": "AI Системы",
    "personal/finance": "Финансы",
    "personal/home": "Дом",
    "personal/purchases": "Покупки",
    "personal/media": "Медиа",
    "personal/family": "Семья",
    "personal/sailing": "Парус",
    "personal/development": "Развитие",
    "projects": "Проекты",
}

# Sections that are NOT areas — tasks fall directly under project area
NON_AREA_SECTIONS = {"Срочное", "Someday / Изучить"}


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-zа-яё0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text[:30]


def main():
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    BAK_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Backup saved: {BAK_FILE}")

    # Determine section order per project (by first appearance in sorted tasks)
    # Top-level tasks only
    top_tasks = [t for t in tasks if not t.get("parent_id")]
    proj_section_order = defaultdict(list)
    seen = set()
    for t in sorted(top_tasks, key=lambda t: t.get("order", 0)):
        proj = t.get("project", "")
        sec = t.get("section") or ""
        key = (proj, sec)
        if key not in seen and sec and sec not in NON_AREA_SECTIONS:
            seen.add(key)
            proj_section_order[proj].append(sec)

    new_tasks = []

    # Step 1: create project area nodes
    proj_area_ids = {}
    for i, proj in enumerate(PROJ_ORDER):
        area_id = f"area-{proj.replace('/', '-')}"
        proj_area_ids[proj] = area_id
        new_tasks.append({
            "id": area_id,
            "title": PROJ_LABELS.get(proj, proj),
            "type": "area",
            "parent_id": None,
            "status": "active",
            "order": float(i),
            "created_at": "2026-05-25",
        })

    # Step 2: create section area nodes
    section_area_ids = {}  # (proj, sec) → id
    for proj, sections in proj_section_order.items():
        for i, sec in enumerate(sections):
            area_id = f"area-{proj.replace('/', '-')}-{slugify(sec)}"
            section_area_ids[(proj, sec)] = area_id
            new_tasks.append({
                "id": area_id,
                "title": sec,
                "type": "area",
                "parent_id": proj_area_ids.get(proj),
                "status": "active",
                "order": float(i),
                "created_at": "2026-05-25",
            })

    # Step 3: re-parent existing tasks
    for t in tasks:
        proj = t.get("project", "")
        sec = t.get("section") or ""
        existing_parent = t.get("parent_id")

        if not existing_parent:
            # Top-level task: assign to section area or project area
            if sec and sec not in NON_AREA_SECTIONS and (proj, sec) in section_area_ids:
                t["parent_id"] = section_area_ids[(proj, sec)]
            else:
                t["parent_id"] = proj_area_ids.get(proj)

        # Set type if not set
        if not t.get("type") or t["type"] == "checklist":
            t["type"] = "task"

        # Remove section field (now encoded in hierarchy)
        t.pop("section", None)

        new_tasks.append(t)

    TASKS_FILE.write_text(json.dumps(new_tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    areas = sum(1 for t in new_tasks if t.get("type") == "area")
    task_nodes = sum(1 for t in new_tasks if t.get("type") == "task")
    print(f"Done. Areas: {areas}, Tasks: {task_nodes}, Total: {len(new_tasks)}")


if __name__ == "__main__":
    main()
