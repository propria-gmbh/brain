#!/usr/bin/env python3
"""
priority.py — scan all task files and rank by priority.

Priority formula:
  P = C*2 + D*3 + S*2 + G*2
  C (color): 🟧=4  🔴=3  🟢=2  gray=1
  D (deadline urgency): overdue=6  <1wk=5  1-2wk=4  2-4wk=3  1-3mo=2  3-6mo=1  >6mo=0  none=0
  S (stakes): [$]=1  [$$]=2  [$$$]=3  [$$$$]=4  [$$$$$]=5  none=0
  G (goal match): 1 if task tag matches active goal in 05_PLANS/goals.md, else 0

Usage:
  python3 tools/priority.py              # top 30 by priority
  python3 tools/priority.py --top 20     # top 20
  python3 tools/priority.py --someday    # only active pool ([someday])
  python3 tools/priority.py --red        # only 🔴 and 🟧
  python3 tools/priority.py --green      # only 🟢 and 🟧
  python3 tools/priority.py --all        # all tasks, no limit
  python3 tools/priority.py --done --today    # completed today
  python3 tools/priority.py --done --week     # completed this week
  python3 tools/priority.py --done --month    # completed this month
  python3 tools/priority.py --done --year     # completed this year
"""

import re
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent

SKIP_DIRS = {'.git', '.obsidian', '__pycache__', '00_META', '04_THINKING', '07_KNOWLEDGE', '06_ARCHIVE'}


def load_active_goals():
    goals_file = ROOT / '05_PLANS' / 'goals.md'
    tags = set()
    try:
        with open(goals_file, encoding='utf-8') as f:
            in_section = False
            for line in f:
                if line.strip() == '## Активные сейчас':
                    in_section = True
                    continue
                if in_section and line.startswith('## '):
                    break
                if in_section:
                    m = re.search(r'`(#\S+)`', line)
                    if m:
                        tags.add(m.group(1))
    except Exception:
        pass
    return tags


def deadline_score(deadline_str, today):
    if not deadline_str:
        return 0
    try:
        d = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        days = (d - today).days
        if days < 0:    return 6
        if days < 7:    return 5
        if days < 14:   return 4
        if days < 28:   return 3
        if days < 90:   return 2
        if days < 180:  return 1
        return 0
    except ValueError:
        return 0


def color_score(line):
    if '🟧' in line:
        return 4, '🟧'
    if '🔴' in line:
        return 3, '🔴  '
    if '🟢' in line:
        return 2, '🟢  '
    return 1, '    '


def stakes_score(line):
    m = re.search(r'\[(\$+)\]', line)
    if not m:
        return 0, ''
    s = len(m.group(1))
    return min(s, 5), m.group(1)


def parse_tasks(filepath, today, active_goals=None):
    tasks = []
    if active_goals is None:
        active_goals = set()
    try:
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^- \[ \] (.+)', line)
                if not m:
                    continue
                content = m.group(1).strip()

                deadline_m = re.search(r'\((\d{4}-\d{2}-\d{2})\)', content)
                deadline = deadline_m.group(1) if deadline_m else None

                someday = '[someday]' in content

                tags = set(re.findall(r'#\S+', content))
                g_score = 1 if tags & active_goals else 0

                c_score, c_label = color_score(content)
                d_score = deadline_score(deadline, today)
                s_score, s_label = stakes_score(content)
                p = c_score * 2 + d_score * 3 + s_score * 2 + g_score * 2

                name = content
                name = re.sub(r'🟧|🔴|🟢', '', name)
                name = re.sub(r'\[someday\]', '', name)
                name = re.sub(r'\(\d{4}-\d{2}-\d{2}\)', '', name)
                name = re.sub(r'\[\$+\]', '', name)
                name = re.sub(r'https?://\S+', '', name)
                name = re.sub(r'\s+', ' ', name).strip()
                name = name[:72]

                tasks.append({
                    'p': p,
                    'color': c_label,
                    'deadline': deadline,
                    'stakes': s_label,
                    'someday': someday,
                    'name': name,
                    'file': str(filepath.relative_to(ROOT)),
                })
    except Exception:
        pass
    return tasks


def parse_done(filepath):
    done = []
    try:
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^- \[x\] (\d{4}-\d{2}-\d{2}) (.+)', line)
                if not m:
                    continue
                done_date = m.group(1)
                name = m.group(2).strip()
                name = re.sub(r'https?://\S+', '', name)
                name = re.sub(r'\s+', ' ', name).strip()[:72]
                done.append({
                    'date': done_date,
                    'name': name,
                    'file': str(filepath.relative_to(ROOT)),
                })
    except Exception:
        pass
    return done


def main():
    parser = argparse.ArgumentParser(description='Task priority viewer')
    parser.add_argument('--top',    type=int, default=30)
    parser.add_argument('--someday', action='store_true')
    parser.add_argument('--red',    action='store_true')
    parser.add_argument('--green',  action='store_true')
    parser.add_argument('--all',    action='store_true')
    parser.add_argument('--done',   action='store_true', help='Show completed tasks')
    parser.add_argument('--save-today', action='store_true', help='Save someday tasks to 05_PLANS/today.md')
    parser.add_argument('--today',  action='store_true')
    parser.add_argument('--week',   action='store_true')
    parser.add_argument('--month',  action='store_true')
    parser.add_argument('--year',   action='store_true')
    args = parser.parse_args()

    today = date.today()
    active_goals = load_active_goals()

    if args.done:
        all_done = []
        for md_file in sorted(ROOT.rglob('*.md')):
            if any(skip in md_file.parts for skip in SKIP_DIRS):
                continue
            all_done.extend(parse_done(md_file))

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

        filtered = [d for d in all_done if since is None or d['date'] >= since]
        filtered.sort(key=lambda d: d['date'], reverse=True)

        if not filtered:
            print(f'Нет выполненных задач за: {label}')
            return

        print(f"\n Выполнено — {label}  ({len(filtered)} задач)")
        print('─' * 90)
        for d in filtered:
            print(f" {d['date']}  {d['name']}")
            print(f"            {d['file']}")
            print()
        return

    all_tasks = []
    for md_file in sorted(ROOT.rglob('*.md')):
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue
        all_tasks.extend(parse_tasks(md_file, today, active_goals))

    filtered = all_tasks
    if args.someday:
        filtered = [t for t in filtered if t['someday']]
    if args.red:
        filtered = [t for t in filtered if t['color'] in ('🔴  ', '🟧')]
    if args.green:
        filtered = [t for t in filtered if t['color'] in ('🟢  ', '🟧')]

    filtered.sort(key=lambda t: (-t['p'], t['deadline'] or '9999-99-99'))

    if not args.all and not args.someday and not args.save_today:
        filtered = filtered[:args.top]

    if not filtered:
        print('Задачи не найдены.')
        return

    if args.save_today:
        today_file = ROOT / '05_PLANS' / 'today.md'
        emoji_map = {'🟧': '🟧', '🔴  ': '🔴', '🟢  ': '🟢', '    ': ''}
        lines = [
            f'# План на {today.strftime("%Y-%m-%d")}',
            '',
        ]
        for i, t in enumerate(filtered, 1):
            dl = f' ({t["deadline"]})' if t['deadline'] else ''
            emoji = emoji_map.get(t['color'], '').strip()
            prefix = f'{emoji} ' if emoji else ''
            lines.append(f'- [ ] {prefix}{t["name"]}{dl}')
        lines += ['', '## Сделано', '']
        today_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f'Сохранено в {today_file}')
        return

    print(f"\n {'P':>3}  {'Тип':5}  {'$':5}  {'Дедлайн':12}  {'★':1}  Задача")
    print('─' * 95)
    for t in filtered:
        dl = t['deadline'] or '—'
        star = '★' if t['someday'] else ' '
        st = t['stakes'] or '—'
        print(f" {t['p']:>3}  {t['color']:5}  {st:5}  {dl:12}  {star}  {t['name']}")
        print(f"       {'':5}  {'':5}  {'':12}     {t['file']}")
        print()


if __name__ == '__main__':
    main()
