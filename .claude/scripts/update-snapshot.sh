#!/bin/bash
# Runs after each Claude turn. Updates snapshot.md max once per hour.

SNAPSHOT="/Users/dister/Projects/brain/00_META/snapshot.md"
MARKER="/tmp/brain-snapshot-last-update"
CLAUDE="/Users/dister/.local/bin/claude"

# Only run once per hour max
if [ -f "$MARKER" ]; then
  LAST=$(cat "$MARKER")
  NOW=$(date +%s)
  DIFF=$((NOW - LAST))
  if [ $DIFF -lt 3600 ]; then
    exit 0
  fi
fi

PROMPT="Read the file /Users/dister/Projects/brain/00_META/snapshot.md. Also read /Users/dister/Projects/brain/05_PLANS/tasks/ (all files) and /Users/dister/Projects/brain/08_PROJECTS/ (top-level files). Update snapshot.md to reflect current state: active projects, blockers, recent changes. Keep the exact same structure and format. Output only the updated file content, nothing else."

$CLAUDE --model claude-haiku-4-5-20251001 --print "$PROMPT" > /tmp/snapshot-new.md 2>/dev/null

if [ -s /tmp/snapshot-new.md ]; then
  mv /tmp/snapshot-new.md "$SNAPSHOT"
  date +%s > "$MARKER"
fi
