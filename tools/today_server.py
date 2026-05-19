#!/usr/bin/env python3
"""Brain Task Manager — today.md + task files in browser."""

import http.server
import json
import re
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

PORT = 7777
BRAIN = Path(__file__).parent.parent
TODAY = BRAIN / "05_PLANS/today.md"
CALENDAR_CACHE = BRAIN / "tools/calendar_cache.json"
PROJECTS = [
    ("Здоровье", BRAIN / "08_PROJECTS/health.md"),
    ("Ecom", BRAIN / "05_PLANS/tasks/ecom.md"),
    ("Propria", BRAIN / "05_PLANS/tasks/propria.md"),
    ("AI", BRAIN / "05_PLANS/tasks/ai-systems.md"),
    ("Финансы", BRAIN / "05_PLANS/tasks/personal/finance.md"),
    ("Дом", BRAIN / "05_PLANS/tasks/personal/home.md"),
    ("Семья", BRAIN / "05_PLANS/tasks/personal/family.md"),
    ("Развитие", BRAIN / "05_PLANS/tasks/personal/development.md"),
]

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 24px; max-width: 860px; margin: 0 auto; }
nav { display: flex; gap: 8px; margin-bottom: 28px; }
nav a { padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; color: #888; background: #1a1a1a; }
nav a.active { background: #2a2a2a; color: #fff; }
h1 { font-size: 1.3rem; color: #fff; margin-bottom: 20px; }
/* today */
.progress { margin-bottom: 24px; }
.bar { background: #1e1e1e; border-radius: 4px; height: 5px; margin-top: 6px; overflow: hidden; }
.fill { background: #2ecc71; height: 100%; border-radius: 4px; }
.pct { font-size: 0.8rem; color: #555; }
h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #555; margin: 24px 0 8px; }
ul { list-style: none; }
li.item { padding: 7px 10px; margin: 3px 0; border-radius: 5px; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; cursor: pointer; }
li.item:hover { filter: brightness(1.15); }
li.todo { background: #1a1a1a; color: #ccc; }
li.done-item { background: #141414; color: #444; text-decoration: line-through; }
li.red { border-left: 3px solid #e74c3c; }
li.green { border-left: 3px solid #2ecc71; }
li.orange { border-left: 3px solid #f39c12; }
.chk { flex-shrink: 0; width: 16px; height: 16px; border-radius: 3px; background: #252525; color: #444; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; }
li.done-item .chk { color: #2ecc71; }
/* tasks */
details { margin: 6px 0; }
details > summary { cursor: pointer; padding: 8px 10px; background: #1a1a1a; border-radius: 6px; font-size: 0.85rem; font-weight: 600; color: #bbb; list-style: none; display: flex; align-items: center; gap: 6px; }
details > summary::-webkit-details-marker { display: none; }
details > summary::before { content: '▶'; font-size: 0.6rem; color: #555; transition: transform 0.15s; }
details[open] > summary::before { transform: rotate(90deg); }
details details > summary { background: #161616; font-weight: 400; color: #888; font-size: 0.8rem; padding: 6px 10px 6px 20px; }
.task-row { display: flex; align-items: center; gap: 6px; padding: 6px 10px; margin: 2px 0; border-radius: 5px; background: #141414; font-size: 0.88rem; color: #ccc; }
.task-row:hover { background: #1c1c1c; }
.task-row.done-task { color: #444; text-decoration: line-through; }
.task-row.someday { opacity: 0.5; }
.task-chk { flex-shrink: 0; width: 15px; height: 15px; border-radius: 3px; background: #222; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; color: #444; }
.task-chk:hover { background: #333; }
.task-text { flex: 1; }
.deadline { font-size: 0.75rem; color: #555; flex-shrink: 0; }
/* calendar */
.cal-day { margin-bottom: 20px; }
.cal-day-header { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #555; margin-bottom: 6px; padding: 4px 0; border-bottom: 1px solid #1e1e1e; }
.cal-day-header.today { color: #5b8dd9; }
.cal-event { display: flex; align-items: baseline; gap: 10px; padding: 6px 10px; margin: 2px 0; border-radius: 5px; background: #141414; font-size: 0.88rem; }
.cal-event:hover { background: #1a1a1a; }
.cal-time { color: #555; font-size: 0.78rem; flex-shrink: 0; min-width: 80px; font-variant-numeric: tabular-nums; }
.cal-title { color: #ccc; flex: 1; }
.cal-loc { font-size: 0.75rem; color: #444; flex-shrink: 0; }
.cal-event.travel { border-left: 3px solid #9b59b6; }
.cal-event.recurring { opacity: 0.4; }
.cal-stale { font-size: 0.75rem; color: #c0392b; margin-bottom: 12px; }
.btn { flex-shrink: 0; padding: 2px 6px; border-radius: 3px; font-size: 0.7rem; cursor: pointer; border: none; background: #222; color: #666; }
.btn:hover { background: #333; color: #999; }
.btn.s-btn { color: #5b8dd9; }
.btn.s-btn.active { background: #1a2a40; color: #5b8dd9; }
.indent1 { padding-left: 24px; }
.indent2 { padding-left: 40px; }
.indent3 { padding-left: 56px; }
.ts { font-size: 0.7rem; color: #2a2a2a; position: fixed; bottom: 12px; right: 16px; }
"""

JS = """
// persist details open state
document.querySelectorAll('details').forEach(d => {
  const key = 'det:' + d.dataset.key;
  if (localStorage.getItem(key) === '1') d.open = true;
  d.addEventListener('toggle', () => localStorage.setItem(key, d.open ? '1' : '0'));
});

function post(url, data, cb) {
  fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
    .then(() => cb ? cb() : location.reload());
}

// today checkboxes
document.querySelectorAll('li[data-idx]').forEach(li => {
  li.addEventListener('click', () => post('/toggle', {idx: parseInt(li.dataset.idx)}));
});

// task checkboxes
document.querySelectorAll('.task-chk[data-file]').forEach(el => {
  el.addEventListener('click', e => {
    e.stopPropagation();
    post('/toggle-task', {file: el.dataset.file, line: parseInt(el.dataset.line)});
  });
});

// someday buttons
document.querySelectorAll('.s-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    post('/someday', {file: btn.dataset.file, line: parseInt(btn.dataset.line)});
  });
});

// delete buttons
document.querySelectorAll('.del-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    if (confirm('Удалить?')) post('/delete', {file: btn.dataset.file, line: parseInt(btn.dataset.line), count: parseInt(btn.dataset.count)});
  });
});
"""

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
{refresh}
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<nav>
  <a href="/" class="{nav_today}">Сегодня</a>
  <a href="/tasks" class="{nav_tasks}">Задачи</a>
</nav>

{body}
<div class="ts">обновляется каждые 5 с</div>
<script>{js}</script>
</body>
</html>"""


def today_str():
    return date.today().strftime("%Y-%m-%d")


def extract_deadline(text):
    m = re.search(r'\((\d{4}-\d{2}-\d{2})\)', text)
    return m.group(1) if m else None


def clean_text(text):
    text = re.sub(r'^\d{4}-\d{2}-\d{2} ', '', text)
    return text.strip()


# ── TODAY ────────────────────────────────────────────────

def parse_today(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    sections, current_sec, current_items, title = [], None, [], ""
    idx = 0
    all_items = []

    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            if current_sec is not None:
                sections.append((current_sec, current_items))
            current_sec, current_items = line[3:].strip(), []
        elif re.match(r'\s*- \[.\]', line):
            done = bool(re.match(r'\s*- \[x\]', line, re.I))
            text = re.sub(r'\s*- \[.\] ', '', line).strip()
            text = clean_text(text)
            item = {"done": done, "text": text, "line": i, "idx": idx}
            current_items.append(item)
            all_items.append(item)
            idx += 1

    if current_sec is not None:
        sections.append((current_sec, current_items))
    return title, sections, all_items


def render_today(path):
    title, sections, all_items = parse_today(path)
    total = len(all_items)
    done_n = sum(1 for i in all_items if i["done"])
    pct = int(done_n / total * 100) if total else 0

    b = f"<h1>{title}</h1>\n"
    b += f'<div class="progress"><span class="pct">{done_n}/{total} — {pct}%</span><div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>\n'

    done_all = []
    for sec, items in sections:
        todo = [i for i in items if not i["done"]]
        done_all += [i for i in items if i["done"]]
        if not todo:
            continue
        b += f"<h2>{sec}</h2><ul>\n"
        for item in todo:
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            b += f'<li class="item todo{extra}" data-idx="{item["idx"]}"><span class="chk">·</span><span>{item["text"]}</span></li>\n'
        b += "</ul>\n"

    if done_all:
        b += "<h2>Сделано</h2><ul>\n"
        for item in done_all:
            b += f'<li class="item done-item" data-idx="{item["idx"]}"><span class="chk">✓</span><span>{item["text"]}</span></li>\n'
        b += "</ul>\n"

    return b


def toggle_today(path, idx):
    lines = path.read_text(encoding="utf-8").splitlines()
    _, _, all_items = parse_today(path)
    item = next((i for i in all_items if i["idx"] == idx), None)
    if not item:
        return
    line = lines[item["line"]]
    if item["done"]:
        line = re.sub(r'- \[x\] \d{4}-\d{2}-\d{2} ', '- [ ] ', line, flags=re.I)
        line = re.sub(r'- \[x\] ', '- [ ] ', line, flags=re.I)
    else:
        line = re.sub(r'- \[ \] ', f'- [x] {today_str()} ', line)
    lines[item["line"]] = line
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── TASKS ────────────────────────────────────────────────

def parse_tasks(path):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    sections, current_sec, current_items = [], None, []

    for i, line in enumerate(lines):
        if line.startswith("## "):
            if current_sec is not None:
                sections.append((current_sec, current_items))
            current_sec, current_items = line[3:].strip(), []
        elif re.match(r'\s*- \[.\]', line):
            done = bool(re.match(r'\s*- \[x\]', line, re.I))
            indent = len(line) - len(line.lstrip())
            raw = re.sub(r'\s*- \[.\] ', '', line).strip()
            raw = re.sub(r'^\d{4}-\d{2}-\d{2} ', '', raw).strip()
            someday = '[someday]' in raw
            deadline = extract_deadline(raw)
            text = re.sub(r'\[someday\]', '', raw).strip()
            text = re.sub(r'#\w+', '', text).strip()
            current_items.append({
                "done": done, "text": text, "deadline": deadline,
                "someday": someday, "indent": indent // 2,
                "file": str(path), "line": i,
            })

    if current_sec is not None:
        sections.append((current_sec, current_items))

    return sections


def count_subtasks(path, line_no, indent):
    lines = path.read_text(encoding="utf-8").splitlines()
    count = 0
    for line in lines[line_no + 1:]:
        if not re.match(r'\s*- \[.\]', line):
            if line.strip() and not line.startswith(' '):
                break
            continue
        cur_indent = (len(line) - len(line.lstrip())) // 2
        if cur_indent > indent:
            count += 1
        else:
            break
    return count


def render_tasks():
    b = "<h1>Задачи</h1>\n"
    b += render_calendar_inline()

    for proj_name, proj_file in PROJECTS:
        sections = parse_tasks(proj_file)
        if not sections:
            continue
        key = proj_name.replace(' ', '_')
        b += f'<details data-key="{key}"><summary>{proj_name}</summary>\n'
        for sec_name, items in sections:
            if not items:
                continue
            skey = f"{key}_{sec_name.replace(' ', '_')[:20]}"
            b += f'<details data-key="{skey}"><summary>{sec_name}</summary>\n'
            for item in items:
                indent_cls = f" indent{min(item['indent'], 3)}" if item['indent'] > 0 else ""
                done_cls = " done-task" if item["done"] else ""
                someday_cls = " someday" if item["someday"] else ""
                chk_icon = "✓" if item["done"] else "·"
                s_active = " active" if item["someday"] else ""
                s_label = "S" if not item["someday"] else "✕S"
                deadline_html = f'<span class="deadline">{item["deadline"]}</span>' if item["deadline"] else ""
                subtask_count = count_subtasks(Path(item["file"]), item["line"], item["indent"])

                b += f'''<div class="task-row{indent_cls}{done_cls}{someday_cls}">
  <span class="task-chk" data-file="{item['file']}" data-line="{item['line']}">{chk_icon}</span>
  <span class="task-text">{item['text']}</span>
  {deadline_html}
  <button class="btn s-btn{s_active}" data-file="{item['file']}" data-line="{item['line']}">{s_label}</button>
  <button class="btn del-btn" data-file="{item['file']}" data-line="{item['line']}" data-count="{subtask_count + 1}">×</button>
</div>\n'''
            b += "</details>\n"
        b += "</details>\n"
    return b


def toggle_task(file_path, line_no):
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    line = lines[line_no]
    if re.match(r'\s*- \[x\]', line, re.I):
        line = re.sub(r'- \[x\] \d{4}-\d{2}-\d{2} ', '- [ ] ', line, flags=re.I)
        line = re.sub(r'- \[x\] ', '- [ ] ', line, flags=re.I)
    else:
        line = re.sub(r'- \[ \] ', f'- [x] {today_str()} ', line)
    lines[line_no] = line
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def toggle_someday(file_path, line_no):
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    line = lines[line_no]
    if '[someday]' in line:
        line = line.replace(' [someday]', '').replace('[someday]', '')
    else:
        line = line.rstrip() + ' [someday]'
    lines[line_no] = line
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def delete_task(file_path, line_no, count):
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    del lines[line_no:line_no + count]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── CALENDAR ─────────────────────────────────────────────

def render_calendar_inline():
    if not CALENDAR_CACHE.exists():
        return ''
    data = json.loads(CALENDAR_CACHE.read_text(encoding="utf-8"))
    events = data.get("events", [])
    updated = data.get("updated", "")

    stale = ""
    try:
        cache_dt = datetime.fromisoformat(updated)
        age_h = (datetime.now(cache_dt.tzinfo) - cache_dt).total_seconds() / 3600
        if age_h > 24:
            stale = f'<span style="color:#c0392b;font-size:0.72rem;margin-left:8px">устарел {int(age_h)}ч</span>'
    except Exception:
        pass

    today = today_str()
    by_date = {}
    for ev in events:
        by_date.setdefault(ev["date"], []).append(ev)

    b = f'<details data-key="calendar_inline" style="margin-bottom:20px"><summary>Календарь{stale}</summary>\n'
    for day_str in sorted(by_date.keys()):
        try:
            d = datetime.strptime(day_str, "%Y-%m-%d")
            dow = DAY_NAMES[d.weekday()]
            mon = MONTH_NAMES[d.month - 1]
            label = f"{dow} {d.day} {mon}"
        except Exception:
            label = day_str
        is_today = day_str == today
        header_cls = " today" if is_today else ""
        b += f'<div class="cal-day-header{header_cls}" style="margin:10px 10px 4px">{label}</div>\n'
        for ev in sorted(by_date[day_str], key=lambda x: x.get("start", "")):
            t = ev.get("type", "default")
            time_str = ev.get("start", "")
            end_str = ev.get("end", "")
            time_html = f"{time_str}–{end_str}" if time_str and end_str else (time_str or "весь день")
            b += f'<div class="cal-event {t}"><span class="cal-time">{time_html}</span><span class="cal-title">{ev["summary"]}</span></div>\n'
    b += "</details>\n"
    return b



DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTH_NAMES = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


def render_calendar():
    b = "<h1>Календарь</h1>\n"
    if not CALENDAR_CACHE.exists():
        return b + '<p style="color:#555">Кэш не найден. Попроси Claude обновить calendar_cache.json.</p>'

    data = json.loads(CALENDAR_CACHE.read_text(encoding="utf-8"))
    updated = data.get("updated", "")
    events = data.get("events", [])

    # stale warning if cache older than 24h
    try:
        cache_dt = datetime.fromisoformat(updated)
        age_h = (datetime.now(cache_dt.tzinfo) - cache_dt).total_seconds() / 3600
        if age_h > 24:
            b += f'<div class="cal-stale">Кэш устарел ({int(age_h)}ч назад) — попроси Claude обновить</div>\n'
    except Exception:
        pass

    # group by date
    by_date = {}
    for ev in events:
        by_date.setdefault(ev["date"], []).append(ev)

    today = today_str()
    for day_str in sorted(by_date.keys()):
        try:
            d = datetime.strptime(day_str, "%Y-%m-%d")
            dow = DAY_NAMES[d.weekday()]
            mon = MONTH_NAMES[d.month - 1]
            label = f"{dow}, {d.day} {mon}"
        except Exception:
            label = day_str

        is_today = day_str == today
        header_cls = " today" if is_today else ""
        b += f'<div class="cal-day"><div class="cal-day-header{header_cls}">{label}</div>\n'

        for ev in sorted(by_date[day_str], key=lambda x: x.get("start", "")):
            t = ev.get("type", "default")
            time_str = ev.get("start", "")
            end_str = ev.get("end", "")
            if time_str and end_str:
                time_html = f"{time_str}–{end_str}"
            elif time_str:
                time_html = time_str
            else:
                time_html = "весь день"
            loc = ev.get("location", "")
            loc_html = f'<span class="cal-loc">{loc[:40]}</span>' if loc else ""
            b += f'<div class="cal-event {t}"><span class="cal-time">{time_html}</span><span class="cal-title">{ev["summary"]}</span>{loc_html}</div>\n'

        b += "</div>\n"

    if updated:
        try:
            cache_dt = datetime.fromisoformat(updated)
            upd_label = cache_dt.strftime("%d.%m %H:%M")
        except Exception:
            upd_label = updated
        b += f'<div class="ts" style="position:static;margin-top:20px">обновлено {upd_label}</div>\n'

    return b


# ── SERVER ───────────────────────────────────────────────

def make_page(body, page):
    return HTML.format(
        title="Сегодня" if page == "today" else "Задачи",
        refresh='<meta http-equiv="refresh" content="5">' if page == "today" else "",
        css=CSS, js=JS, body=body,
        nav_today="active" if page == "today" else "",
        nav_tasks="active" if page == "tasks" else "",
    ).encode("utf-8")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = render_today(TODAY)
            data = make_page(body, "today")
        elif self.path == "/tasks":
            body = render_tasks()
            data = make_page(body, "tasks")
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(length))
        if self.path == "/toggle":
            toggle_today(TODAY, d["idx"])
        elif self.path == "/toggle-task":
            toggle_task(d["file"], d["line"])
        elif self.path == "/someday":
            toggle_someday(d["file"], d["line"])
        elif self.path == "/delete":
            delete_task(d["file"], d["line"], d["count"])
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print(f"Открываю {url}  (Ctrl+C чтобы остановить)")
    webbrowser.open(url)
    with http.server.HTTPServer(("", PORT), Handler) as srv:
        srv.serve_forever()
