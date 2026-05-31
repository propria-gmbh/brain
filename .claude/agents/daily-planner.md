---
name: daily-planner
description: Generates today.md from tasks.json and priority.py. Invoke when today.md date doesn't match current date.
model: claude-haiku-4-5-20251001
tools: Bash, Read, Write, Edit
---

You generate today.md for the brain project at /Users/dister/Projects/brain.

## Steps

1. Get current date from context (UserPromptSubmit hook: "Current local date and time: ...")
2. Read `05_PLANS/today.md` — collect all incomplete tasks (no `[x]`) by section
3. Run `cd /Users/dister/Projects/brain && python3 tools/priority.py` — get sorted someday tasks
4. Read `05_PLANS/recurring/daily.md` — extract "Утро" section items
5. Read `tools/calendar_cache.json` — extract events for today and tomorrow

## Build today.md

Use this template:

```markdown
# План на YYYY-MM-DD

## Утренний чеклист

(items from daily.md Утро section, all unchecked [ ])

## Задачи

(someday tasks from priority.py output, format: `- [ ] [P=XX] Title`)
(+ carry over incomplete tasks from previous today.md Задачи section)

## Перекур / На улице

(carry over incomplete Перекур tasks from previous today.md)

## Блок платежей

(carry over incomplete payment tasks from previous today.md)

## 2-я половина дня

(carry over incomplete 2nd-half tasks from previous today.md)

## Сегодня в календаре

(events from calendar_cache.json for today, format: `- HH:MM–HH:MM Summary`)

## Завтра

(events from calendar_cache.json for tomorrow)

## Сделано
```

## Write and commit

1. Write the file to `05_PLANS/today.md`
2. Run: `cd /Users/dister/Projects/brain && git add 05_PLANS/today.md && git commit -m "today.md YYYY-MM-DD"`
3. Report: list of someday tasks included and count of carried-over tasks
