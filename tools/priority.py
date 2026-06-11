#!/usr/bin/env python3
"""
priority.py — rank tasks from tasks.json by priority.

Priority formula:
  P = C*2 + D*3 + S*2 + G*2
  C (color/priority): orange=4  red=3  green=2  none=1
  D (deadline urgency): <1wk=5  1-2wk=4  2-4wk=3  1-3mo=2  overdue=4  3mo+=0  none=0
  S (stakes): 1-5 (number of $)
  G (goal_rank on area, inherited up tree): rank1=5  rank2=3  rank3=1  none=0

Usage:
  python3 tools/priority.py              # top 30 someday tasks
  python3 tools/priority.py --top 20
  python3 tools/priority.py --all        # all todo tasks (not just someday)
  python3 tools/priority.py --done --today
  python3 tools/priority.py --done --week
  python3 tools/priority.py --done --month
  python3 tools/priority.py --done --year
"""

import json
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
TASKS_FILE = ROOT / '05_PLANS' / 'tasks' / 'tasks.json'

GOAL_RANK_SCORES = {1: 5, 2: 3, 3: 1}


def load_tasks():
    with open(TASKS_FILE, encoding='utf-8') as f:
        return json.load(f)


def build_task_map(data):
    return {t['id']: t for t in data if isinstance(t, dict) and 'id' in t}


def infer_goal_rank(task, task_map):
    # Check task itself first, then walk up parent_id tree
    node = task
    seen = set()
    while node:
        nid = node.get('id', '')
        if nid in seen:
            break
        seen.add(nid)
        if node.get('goal_rank'):
            return node['goal_rank']
        pid = node.get('parent_id', '')
        node = task_map.get(pid) if pid else None
    return None


def infer_deadline(task, task_map):
    if task.get('deadline'):
        return task['deadline']
    pid = task.get('parent_id', '')
    seen = set()
    while pid and pid not in seen:
        seen.add(pid)
        parent = task_map.get(pid)
        if parent:
            if parent.get('deadline'):
                return parent['deadline']
            pid = parent.get('parent_id', '')
        else:
            break
    return None


def deadline_score(deadline_str, today, is_reminder=False):
    if not deadline_str:
        return 0
    try:
        d = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        days = (d - today).days
        if is_reminder:
            # Reminders only score when due today or tomorrow
            if days <= 0:  return 5
            if days <= 1:  return 3
            return 0
        if days < 0:    return 4
        if days < 7:    return 5
        if days < 14:   return 4
        if days < 28:   return 3
        if days < 90:   return 2
        return 0
    except ValueError:
        return 0


def color_score(priority):
    return {'orange': 4, 'red': 3, 'green': 2}.get(priority or '', 1)


def color_label(priority):
    return {'orange': '🟧', 'red': '🔴 ', 'green': '🟢 '}.get(priority or '', '   ')


def stakes_score(stakes):
    if stakes is None:
        return 0, ''
    if isinstance(stakes, int):
        s = min(stakes, 5)
        return s, '$' * s
    if isinstance(stakes, str):
        s = len([c for c in stakes if c == '$'])
        return min(s, 5), '$' * min(s, 5)
    return 0, ''


def score_task(task, task_map, today):
    c = color_score(task.get('priority'))
    deadline = infer_deadline(task, task_map)
    is_reminder = 'reminder' in (task.get('tags') or [])
    d = deadline_score(deadline, today, is_reminder)
    s, s_label = stakes_score(task.get('stakes'))
    goal_rank = infer_goal_rank(task, task_map)
    g = GOAL_RANK_SCORES.get(goal_rank, 0)
    p = c * 2 + d * 3 + s * 2 + g * 2
    return p, c, d, s, s_label, g, goal_rank, deadline


def format_area(task, task_map):
    pid = task.get('parent_id', '')
    parent = task_map.get(pid)
    if parent:
        return parent.get('title', pid)[:30]
    return pid[:30]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=30)
    parser.add_argument('--all', action='store_true', help='All todo tasks (not just someday)')
    parser.add_argument('--done', action='store_true')
    parser.add_argument('--today', action='store_true')
    parser.add_argument('--week', action='store_true')
    parser.add_argument('--month', action='store_true')
    parser.add_argument('--year', action='store_true')
    args = parser.parse_args()

    data = load_tasks()
    task_map = build_task_map(data)
    today = date.today()

    if args.done:
        done_tasks = [
            t for t in data
            if isinstance(t, dict) and t.get('status') == 'done' and t.get('done_at')
        ]

        if args.today:
            since = today.isoformat()
            label = f'сегодня ({today})'
        elif args.week:
            since = (today - timedelta(days=today.weekday())).isoformat()
            label = f'эта неделя (с {since})'
        elif args.month:
            since = today.replace(day=1).isoformat()
            label = f'этот месяц (с {since})'
        elif args.year:
            since = today.replace(month=1, day=1).isoformat()
            label = f'этот год (с {since})'
        else:
            since = None
            label = 'все время'

        filtered = [t for t in done_tasks if since is None or (t['done_at'] or '') >= since]
        filtered.sort(key=lambda t: t.get('done_at', ''), reverse=True)

        if not filtered:
            print(f'Нет выполненных задач за: {label}')
            return

        print(f"\n Выполнено — {label}  ({len(filtered)} задач)")
        print('─' * 90)
        for t in filtered:
            print(f" {t['done_at']}  {t['title'][:70]}")
        return

    tasks = [
        t for t in data
        if isinstance(t, dict)
        and t.get('type') in ('task', 'subtask')
        and t.get('status') != 'done'
        and (args.all or t.get('someday'))
    ]

    scored = []
    for t in tasks:
        p, c, d, s, s_label, g, goal_rank, deadline = score_task(t, task_map, today)
        scored.append({
            'p': p,
            'title': t.get('title', '')[:72],
            'priority': t.get('priority'),
            'deadline': deadline,
            'stakes_label': s_label,
            'goal_rank': goal_rank,
            'area': format_area(t, task_map),
        })

    scored.sort(key=lambda t: (-t['p'], t['deadline'] or '9999-99-99'))

    if not args.all:
        scored = scored[:args.top]

    if not scored:
        print('Задачи не найдены.')
        return

    print(f"\n {'P':>3}  {'Тип':4}  {'$':5}  {'Дедлайн':12}  {'G':4}  Задача")
    print('─' * 100)
    for t in scored:
        cl = color_label(t['priority'])
        dl = t['deadline'] or '—'
        st = t['stakes_label'] or '—'
        gl = f"G{t['goal_rank']}" if t['goal_rank'] else '—'
        print(f" {t['p']:>3}  {cl}  {st:5}  {dl:12}  {gl:4}  {t['title']}")


if __name__ == '__main__':
    main()
