#!/usr/bin/env python3
"""Stop hook: reads transcript JSONL, appends summary to session-log.jsonl."""

import json
import os
import sys
from datetime import datetime, timezone


def extract_text(content):
    """Extract plain text from message content (string or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                # Skip injected IDE/system wrappers
                if text.startswith("<ide_") or text.startswith("<system-"):
                    continue
                parts.append(text)
        return " ".join(parts).strip()
    return ""


def parse_transcript(path):
    if not os.path.exists(path):
        return {}

    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    user_msgs = [e for e in entries if e.get("type") == "user"]
    assistant_msgs = [e for e in entries if e.get("type") == "assistant"]

    # Session title from last ai-title entry
    titles = [e.get("aiTitle") for e in entries if e.get("type") == "ai-title" and e.get("aiTitle")]
    title = titles[-1] if titles else ""

    # First real user message (skip pure wrapper messages)
    first_msg = ""
    for e in user_msgs:
        text = extract_text(e.get("message", {}).get("content", ""))
        if text:
            first_msg = text[:300]
            break

    # Session timing
    timestamps = [e.get("timestamp") for e in entries if e.get("timestamp")]
    started_at = timestamps[0] if timestamps else None
    ended_at = timestamps[-1] if timestamps else None

    duration_min = 0
    if started_at and ended_at:
        try:
            t0 = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
            duration_min = round((t1 - t0).total_seconds() / 60)
        except Exception:
            pass

    # Tool usage
    tool_counts = {}
    files_modified = []
    files_read = []

    for e in assistant_msgs:
        content = e.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name = block.get("name", "unknown")
            tool_counts[name] = tool_counts.get(name, 0) + 1
            inp = block.get("input", {})
            if name in ("Write", "Edit"):
                fp = inp.get("file_path", "")
                if fp and fp not in files_modified:
                    files_modified.append(fp)
            elif name == "Read":
                fp = inp.get("file_path", "")
                if fp and fp not in files_read:
                    files_read.append(fp)

    return {
        "title": title,
        "first_msg": first_msg,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_min": duration_min,
        "turns": len(user_msgs),
        "tool_counts": tool_counts,
        "files_modified": files_modified,
        "files_read": files_read[:20],
    }


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit(0)

    try:
        hook = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = hook.get("session_id", "")
    transcript_path = hook.get("transcript_path", "")
    cwd = hook.get("cwd", "")
    last_msg = hook.get("last_assistant_message", "")

    info = parse_transcript(transcript_path)

    record = {
        "session_id": session_id,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "started_at": info.get("started_at"),
        "duration_min": info.get("duration_min", 0),
        "cwd": cwd,
        "title": info.get("title", ""),
        "first_msg": info.get("first_msg", ""),
        "last_msg": last_msg[:300] if last_msg else "",
        "turns": info.get("turns", 0),
        "tool_counts": info.get("tool_counts", {}),
        "files_modified": info.get("files_modified", []),
    }

    # Find brain root from cwd or script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    brain_root = os.path.dirname(script_dir)  # tools/ -> brain/
    log_path = os.path.join(brain_root, "04_THINKING", "session-log.jsonl")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        err_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "04_THINKING", "session-indexer-errors.log")
        with open(err_path, "a") as ef:
            ef.write(f"{datetime.now(timezone.utc).isoformat()} ERROR: {e}\n{traceback.format_exc()}\n")
        sys.exit(1)
