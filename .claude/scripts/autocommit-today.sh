#!/bin/bash
# Auto-commit today.md if it belongs to a previous day (runs at session start)
TODAY=$(date +%Y-%m-%d)
FILE="/Users/dister/Projects/brain/05_PLANS/today.md"

[ -f "$FILE" ] || exit 0

FILE_DATE=$(head -1 "$FILE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')

[ -z "$FILE_DATE" ] && exit 0
[ "$FILE_DATE" = "$TODAY" ] && exit 0

cd /Users/dister/Projects/brain || exit 0

git diff --quiet HEAD -- 05_PLANS/today.md 2>/dev/null && exit 0

git add 05_PLANS/today.md
git commit -m "day log: $FILE_DATE"
