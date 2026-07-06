#!/usr/bin/env python3
"""Append completed task titles to 04_THINKING/daylogs/YYYY-MM-DD.md and commit."""
import re
import subprocess
from pathlib import Path

BRAIN = Path(__file__).parent.parent
DAYLOGS_DIR = BRAIN / "04_THINKING/daylogs"


def write_daylog_entries(date_str, titles):
    """Create or update the daylog for date_str with titles. Returns path if changed, else None."""
    titles = [t.strip() for t in titles if t and t.strip()]
    if not titles:
        return None

    DAYLOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = DAYLOGS_DIR / f"{date_str}.md"

    if path.exists():
        content = path.read_text(encoding="utf-8")
        existing = set()
        for line in content.splitlines():
            m = re.match(r"^- (.+)$", line)
            if m:
                existing.add(m.group(1).strip())
        new_entries = [t for t in titles if t not in existing]
        if not new_entries:
            return None
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
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            entries_block = "\n".join(f"- {t}" for t in new_entries)
            path.write_text(content.rstrip() + f"\n\n## Задачи выполнены\n{entries_block}\n", encoding="utf-8")
    else:
        entries_block = "\n".join(f"- {t}" for t in titles)
        path.write_text(
            f"# Лог дня {date_str}\n\n"
            f"## Задачи выполнены\n{entries_block}\n\n"
            f"## Не сделано\n_(заполнить в конце дня)_\n\n"
            f"## Заметки\n_(заполнить в конце дня)_\n",
            encoding="utf-8",
        )

    rel = str(path.relative_to(BRAIN))
    subprocess.run(["git", "add", rel], cwd=str(BRAIN), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"daylog: {date_str}", "--", rel],
        cwd=str(BRAIN), capture_output=True,
    )
    return path
