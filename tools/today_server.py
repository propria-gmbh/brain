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
_SORTABLE_JS = (Path(__file__).parent / "sortable.min.js").read_text(encoding="utf-8")
TODAY = BRAIN / "05_PLANS/today.md"
CALENDAR_CACHE = BRAIN / "tools/calendar_cache.json"
PROJECTS = [
    ("Здоровье", BRAIN / "08_PROJECTS/health.md"),
    ("Ecom", BRAIN / "05_PLANS/tasks/ecom.md"),
    ("Propria", BRAIN / "05_PLANS/tasks/propria.md"),
    ("AI", BRAIN / "05_PLANS/tasks/ai-systems.md"),
    ("Финансы", BRAIN / "05_PLANS/tasks/personal/finance.md"),
    ("Дом", BRAIN / "05_PLANS/tasks/personal/home.md"),
    ("Покупки", BRAIN / "05_PLANS/tasks/personal/purchases.md"),
    ("Медиа", BRAIN / "05_PLANS/tasks/personal/media.md"),
    ("Семья", BRAIN / "05_PLANS/tasks/personal/family.md"),
    ("Парус", BRAIN / "05_PLANS/tasks/personal/sailing.md"),
    ("Развитие", BRAIN / "05_PLANS/tasks/personal/development.md"),
]

CSS = """
:root {
  --bg:#0f0f0f;--bg2:#1a1a1a;--bg3:#141414;--bg4:#222;--bg5:#1e1e1e;
  --text:#e0e0e0;--text2:#ccc;--text3:#888;--text4:#555;--text5:#444;
  --nav-act:#2a2a2a;--row-hov:#1c1c1c;--chk:#222;--chk-hov:#333;
  --btn:#222;--btn-hov:#333;--btn-c:#666;--btn-hov-c:#999;--s-act:#1a2a40;--bdr:#1e1e1e;
}
body.light {
  --bg:#f5f5f5;--bg2:#fff;--bg3:#fafafa;--bg4:#e0e0e0;--bg5:#ebebeb;
  --text:#111;--text2:#333;--text3:#666;--text4:#888;--text5:#aaa;
  --nav-act:#e0e0e0;--row-hov:#ececec;--chk:#ddd;--chk-hov:#ccc;
  --btn:#e8e8e8;--btn-hov:#d8d8d8;--btn-c:#666;--btn-hov-c:#333;--s-act:#d0e4ff;--bdr:#ddd;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 24px; max-width: 1100px; margin: 0 auto; transition: background .2s, color .2s; }
.two-col { display: grid; grid-template-columns: 1fr 340px; gap: 32px; align-items: start; }
nav { display: flex; gap: 8px; margin-bottom: 28px; align-items: center; }
nav a { padding: 8px 20px; border-radius: 6px; text-decoration: none; font-size: .9rem; color: var(--text3); background: var(--bg2); }
nav a.active { background: var(--nav-act); color: var(--text); }
.theme-btn { margin-left: auto; padding: 6px 10px; border-radius: 6px; border: none; background: var(--bg2); color: var(--text3); cursor: pointer; font-size: .85rem; }
.theme-btn:hover { background: var(--nav-act); }
h1 { font-size: 1.3rem; color: var(--text); margin-bottom: 20px; }
.progress { margin-bottom: 24px; }
.bar { background: var(--bg5); border-radius: 4px; height: 5px; margin-top: 6px; overflow: hidden; }
.fill { background: #2ecc71; height: 100%; border-radius: 4px; }
.pct { font-size: .8rem; color: var(--text4); }
h2 { font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; color: var(--text4); margin: 24px 0 8px; }
ul { list-style: none; }
li.item { padding: 7px 10px; margin: 3px 0; border-radius: 5px; font-size: .9rem; display: flex; align-items: center; gap: 8px; cursor: pointer; }
li.item:hover { filter: brightness(1.15); }
li.todo { background: var(--bg2); color: var(--text2); }
li.done-item { background: var(--bg3); color: var(--text5); text-decoration: line-through; }
li.red { border-left: 3px solid #e74c3c; }
li.green { border-left: 3px solid #2ecc71; }
li.orange { border-left: 3px solid #f39c12; }
.chk { flex-shrink: 0; width: 16px; height: 16px; border-radius: 3px; background: var(--bg4); color: var(--text5); display: flex; align-items: center; justify-content: center; font-size: .7rem; }
li.done-item .chk { color: #2ecc71; }
details { margin: 6px 0; }
details > summary { cursor: pointer; padding: 8px 10px; background: var(--bg2); border-radius: 6px; font-size: .85rem; font-weight: 600; color: var(--text3); list-style: none; display: flex; align-items: center; gap: 6px; }
details > summary::-webkit-details-marker { display: none; }
details > summary::before { content: '▶'; font-size: .6rem; color: var(--text4); transition: transform .15s; }
details[open] > summary::before { transform: rotate(90deg); }
details details > summary { background: var(--bg3); font-weight: 400; color: var(--text3); font-size: .8rem; padding: 6px 10px 6px 20px; }
.task-row { display: flex; align-items: center; gap: 6px; padding: 6px 10px; margin: 2px 0; border-radius: 5px; background: var(--bg3); font-size: .88rem; color: var(--text2); cursor: grab; position: relative; }
.task-row:hover { background: var(--row-hov); }
.task-row.done-task { color: var(--text5); text-decoration: line-through; }
.task-row.someday { opacity: .5; }
.task-row.sortable-ghost { opacity: .25; background: var(--bg2); }
.task-row.drop-child { border-left: 3px solid #5b8dd9; }
.task-chk { flex-shrink: 0; width: 15px; height: 15px; border-radius: 3px; background: var(--chk); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: .65rem; color: var(--text5); }
.task-chk:hover { background: var(--chk-hov); }
.task-text { flex: 1; }
.task-text[data-file]:hover { text-decoration: underline dotted var(--text4); cursor: text; }
.task-text[contenteditable=true] { outline: 1px solid #5b8dd9; border-radius: 3px; padding: 1px 4px; background: var(--bg2); cursor: text; text-decoration: none !important; }
.deadline { font-size: .75rem; color: var(--text4); flex-shrink: 0; }
.cal-day { margin-bottom: 20px; }
.cal-day-header { font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; color: var(--text4); margin-bottom: 6px; padding: 4px 0; border-bottom: 1px solid var(--bdr); }
.cal-day-header.today { color: #5b8dd9; }
.cal-event { display: flex; align-items: baseline; gap: 10px; padding: 6px 10px; margin: 2px 0; border-radius: 5px; background: var(--bg3); font-size: .88rem; }
.cal-event:hover { background: var(--bg2); }
.cal-event[data-summary] { cursor: pointer; }
.cal-event.cal-done { opacity: .35; text-decoration: line-through; }
.cal-time { color: var(--text4); font-size: .78rem; flex-shrink: 0; min-width: 80px; font-variant-numeric: tabular-nums; }
.cal-title { color: var(--text2); flex: 1; }
.cal-loc { font-size: .75rem; color: var(--text5); flex-shrink: 0; }
.cal-event.travel { border-left: 3px solid #9b59b6; }
.cal-event.recurring { opacity: .4; }
.cal-stale { font-size: .75rem; color: #c0392b; margin-bottom: 12px; }
.btn { flex-shrink: 0; padding: 2px 6px; border-radius: 3px; font-size: .7rem; cursor: pointer; border: none; background: var(--btn); color: var(--btn-c); }
.btn:hover { background: var(--btn-hov); color: var(--btn-hov-c); }
.btn.s-btn { color: #5b8dd9; }
.btn.s-btn.active { background: var(--s-act); color: #5b8dd9; }
.indent1 { padding-left: 24px; }
.indent2 { padding-left: 40px; }
.indent3 { padding-left: 56px; }
.ts { font-size: .7rem; color: var(--bg5); position: fixed; bottom: 12px; right: 16px; }
"""

JS = """
(function() {
  var b = document.body;
  if (localStorage.getItem('theme') === 'light') b.classList.add('light');
  var btn = document.querySelector('.theme-btn');
  if (btn) btn.textContent = b.classList.contains('light') ? '☀️' : '🌙';
  window.toggleTheme = function() {
    b.classList.toggle('light');
    var light = b.classList.contains('light');
    localStorage.setItem('theme', light ? 'light' : 'dark');
    if (btn) btn.textContent = light ? '☀️' : '🌙';
  };
})();

document.querySelectorAll('details').forEach(function(d) {
  var key = 'det:' + d.dataset.key;
  if (localStorage.getItem(key) === '1') d.open = true;
  d.addEventListener('toggle', function() { localStorage.setItem(key, d.open ? '1' : '0'); });
});

function post(url, data, cb) {
  fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
    .then(function() { if (cb) cb(); else location.reload(); });
}

document.querySelectorAll('li[data-idx]').forEach(function(li) {
  li.addEventListener('click', function() { post('/toggle', {idx: parseInt(li.dataset.idx)}); });
});

document.querySelectorAll('.task-chk[data-file]').forEach(function(el) {
  el.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/toggle-task', {file: el.dataset.file, line: parseInt(el.dataset.line)});
  });
});

document.querySelectorAll('.s-btn').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/someday', {file: btn.dataset.file, line: parseInt(btn.dataset.line)});
  });
});

document.querySelectorAll('.cal-event[data-summary]').forEach(function(el) {
  el.addEventListener('click', function() {
    post('/done-event', {summary: el.dataset.summary, date: el.dataset.date});
  });
});

document.querySelectorAll('.del-btn').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    if (confirm('Удалить?')) post('/delete', {file: btn.dataset.file, line: parseInt(btn.dataset.line), count: parseInt(btn.dataset.count)});
  });
});

document.querySelectorAll('.task-text[data-file]').forEach(function(el) {
  el.addEventListener('dblclick', function(e) {
    e.stopPropagation();
    if (el.contentEditable === 'true') return;
    var orig = el.textContent;
    el.contentEditable = 'true';
    el.focus();
    var range = document.createRange();
    range.selectNodeContents(el);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    function save() {
      el.contentEditable = 'false';
      var txt = el.textContent.trim();
      if (txt && txt !== orig) post('/rename', {file: el.dataset.file, line: parseInt(el.dataset.line), text: txt});
      else el.textContent = orig;
    }
    function cancel() { el.contentEditable = 'false'; el.textContent = orig; }
    function cleanup() { el.removeEventListener('keydown', onKey); el.removeEventListener('blur', onBlur); }
    function onKey(e) {
      if (e.key === 'Enter') { e.preventDefault(); cleanup(); save(); }
      if (e.key === 'Escape') { cleanup(); cancel(); }
    }
    function onBlur() { cleanup(); save(); }
    el.addEventListener('keydown', onKey);
    el.addEventListener('blur', onBlur);
  });
});

window.isDragging = false;
var _childTarget = null;
var _lastOver = null;
var _hoverStart = null;

document.addEventListener('dragover', function(e) {
  var row = e.target.closest ? e.target.closest('.task-row[data-file]') : null;
  if (row !== _lastOver) {
    _lastOver = row;
    _hoverStart = row ? Date.now() : null;
    if (_childTarget && _childTarget !== row) {
      _childTarget.classList.remove('drop-child');
      _childTarget = null;
    }
  }
  if (row && _hoverStart && !row.classList.contains('sortable-ghost') && Date.now() - _hoverStart >= 500) {
    if (_childTarget !== row) {
      if (_childTarget) _childTarget.classList.remove('drop-child');
      _childTarget = row;
      row.classList.add('drop-child');
    }
  }
  e.preventDefault();
});

document.querySelectorAll('.section-tasks').forEach(function(container) {
  if (typeof Sortable === 'undefined') return;
  Sortable.create(container, {
    group: 'tasks',
    animation: 100,
    ghostClass: 'sortable-ghost',
    onStart: function() { window.isDragging = true; },
    onEnd: function(evt) {
      window.isDragging = false;
      var srcEl = evt.item;
      var srcFile = srcEl.dataset.file;
      var srcLine = parseInt(srcEl.dataset.line);
      var tgtFile, tgtLine, position;

      if (_childTarget) {
        tgtFile = _childTarget.dataset.file;
        tgtLine = parseInt(_childTarget.dataset.line);
        position = 'child';
        _childTarget.classList.remove('drop-child');
        _childTarget = null;
      } else {
        var siblings = Array.from(evt.to.querySelectorAll(':scope > .task-row'));
        var newIdx = siblings.indexOf(srcEl);
        if (newIdx > 0) {
          var prev = siblings[newIdx - 1];
          tgtFile = prev.dataset.file;
          tgtLine = parseInt(prev.dataset.line);
          position = 'after';
        } else if (siblings.length > 1) {
          var next = siblings[1];
          tgtFile = next.dataset.file;
          tgtLine = parseInt(next.dataset.line);
          position = 'before';
        } else {
          location.reload();
          return;
        }
      }
      _lastOver = null;
      post('/move', {src_file: srcFile, src_line: srcLine, target_file: tgtFile, target_line: tgtLine, position: position});
    }
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
<script>{sortable_js}</script>
</head>
<body>
<nav>
  <a href="/" class="{nav_today}">Сегодня</a>
  <a href="/tasks" class="{nav_tasks}">Задачи</a>
  <button class="theme-btn" onclick="toggleTheme()">🌙</button>
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

    left = f"<h1>{title}</h1>\n"
    left += f'<div class="progress"><span class="pct">{done_n}/{total} — {pct}%</span><div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>\n'

    done_all = []
    for sec, items in sections:
        todo = [i for i in items if not i["done"]]
        done_all += [i for i in items if i["done"]]
        if not todo:
            continue
        left += f"<h2>{sec}</h2><ul>\n"
        for item in todo:
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            left += f'<li class="item todo{extra}" data-idx="{item["idx"]}"><span class="chk">·</span><span>{item["text"]}</span></li>\n'
        left += "</ul>\n"

    if done_all:
        left += "<h2>Сделано</h2><ul>\n"
        for item in done_all:
            left += f'<li class="item done-item" data-idx="{item["idx"]}"><span class="chk">✓</span><span>{item["text"]}</span></li>\n'
        left += "</ul>\n"

    right = render_calendar_today()
    return f'<div class="two-col"><div class="col-left">{left}</div><div class="col-right">{right}</div></div>\n'


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
        return [], []
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

    return sections, lines


def count_subtasks(lines, line_no, indent):
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
        sections, file_lines = parse_tasks(proj_file)
        if not sections:
            continue
        key = proj_name.replace(' ', '_')
        b += f'<details data-key="{key}"><summary>{proj_name}</summary>\n'
        for sec_name, items in sections:
            if not items:
                continue
            skey = f"{key}_{sec_name.replace(' ', '_')[:20]}"
            b += f'<details data-key="{skey}"><summary>{sec_name}</summary>\n'
            b += '<div class="section-tasks">\n'
            for item in items:
                indent_cls = f" indent{min(item['indent'], 3)}" if item['indent'] > 0 else ""
                done_cls = " done-task" if item["done"] else ""
                someday_cls = " someday" if item["someday"] else ""
                chk_icon = "✓" if item["done"] else "·"
                s_active = " active" if item["someday"] else ""
                s_label = "S" if not item["someday"] else "✕S"
                deadline_html = f'<span class="deadline">{item["deadline"]}</span>' if item["deadline"] else ""
                subtask_count = count_subtasks(file_lines, item["line"], item["indent"])

                b += f'''<div class="task-row{indent_cls}{done_cls}{someday_cls}" data-file="{item['file']}" data-line="{item['line']}">
  <span class="task-chk" data-file="{item['file']}" data-line="{item['line']}">{chk_icon}</span>
  <span class="task-text" data-file="{item['file']}" data-line="{item['line']}">{item['text']}</span>
  {deadline_html}
  <button class="btn s-btn{s_active}" data-file="{item['file']}" data-line="{item['line']}">{s_label}</button>
  <button class="btn del-btn" data-file="{item['file']}" data-line="{item['line']}" data-count="{subtask_count + 1}">×</button>
</div>\n'''
            b += '</div>\n'
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


def rename_task(file_path, line_no, new_text):
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if line_no >= len(lines):
        return
    line = lines[line_no]
    m = re.match(r'^(\s*- \[.\] (?:\d{4}-\d{2}-\d{2} )?)', line)
    if not m:
        return
    prefix = m.group(1)
    old_rest = line[len(prefix):]
    had_someday = '[someday]' in old_rest
    new_line = prefix + new_text
    if had_someday and '[someday]' not in new_text:
        new_line += ' [someday]'
    lines[line_no] = new_line
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def move_task(src_file, src_line, target_file, target_line, position):
    src_path = Path(src_file)
    tgt_path = Path(target_file)
    same_file = src_file == target_file

    src_lines = src_path.read_text(encoding="utf-8").splitlines()
    if src_line >= len(src_lines):
        return

    src_indent = len(src_lines[src_line]) - len(src_lines[src_line].lstrip())

    # Extract block: task + all subtasks
    block = [src_lines[src_line]]
    i = src_line + 1
    while i < len(src_lines):
        ln = src_lines[i]
        if not re.match(r'\s*- \[.\]', ln):
            break
        cur_ind = len(ln) - len(ln.lstrip())
        if cur_ind > src_indent:
            block.append(ln)
            i += 1
        else:
            break

    del src_lines[src_line:src_line + len(block)]

    if same_file:
        tgt_lines = src_lines
        if target_line > src_line:
            target_line -= len(block)
    else:
        tgt_lines = tgt_path.read_text(encoding="utf-8").splitlines()

    if target_line >= len(tgt_lines):
        insert_at = len(tgt_lines)
        tgt_indent = 0
    else:
        tgt_raw = tgt_lines[target_line]
        tgt_indent_base = len(tgt_raw) - len(tgt_raw.lstrip())

        if position == 'child':
            tgt_indent = tgt_indent_base + 2
            insert_at = target_line + 1
            while insert_at < len(tgt_lines):
                ln = tgt_lines[insert_at]
                if not re.match(r'\s*- \[.\]', ln):
                    break
                if len(ln) - len(ln.lstrip()) > tgt_indent_base:
                    insert_at += 1
                else:
                    break
        elif position == 'before':
            tgt_indent = tgt_indent_base
            insert_at = target_line
        else:  # after
            tgt_indent = tgt_indent_base
            insert_at = target_line + 1
            while insert_at < len(tgt_lines):
                ln = tgt_lines[insert_at]
                if not re.match(r'\s*- \[.\]', ln):
                    break
                if len(ln) - len(ln.lstrip()) > tgt_indent_base:
                    insert_at += 1
                else:
                    break

    indent_diff = tgt_indent - src_indent
    if indent_diff != 0:
        block = [' ' * max(0, (len(ln) - len(ln.lstrip())) + indent_diff) + ln.lstrip() for ln in block]

    for j, ln in enumerate(block):
        tgt_lines.insert(insert_at + j, ln)

    if same_file:
        src_path.write_text("\n".join(tgt_lines) + "\n", encoding="utf-8")
    else:
        tgt_path.write_text("\n".join(tgt_lines) + "\n", encoding="utf-8")
        src_path.write_text("\n".join(src_lines) + "\n", encoding="utf-8")


def done_event_summaries():
    if not TODAY.exists():
        return set()
    done = set()
    for line in TODAY.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\s*- \[x\] (\d{4}-\d{2}-\d{2}) (.+)', line)
        if m:
            done.add((m.group(1), m.group(2).strip()))
    return done


def add_done_event(summary, date=None):
    entry_date = date or today_str()
    text = TODAY.read_text(encoding="utf-8")
    entry = f"- [x] {entry_date} {summary}"
    if entry in text:
        return
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "## Сделано":
            lines.insert(i + 1, entry)
            TODAY.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    lines += ["", "## Сделано", entry]
    TODAY.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── CALENDAR ─────────────────────────────────────────────

def render_calendar_today():
    if not CALENDAR_CACHE.exists():
        return '<div style="color:#444;font-size:0.8rem">Нет данных календаря</div>'
    data = json.loads(CALENDAR_CACHE.read_text(encoding="utf-8"))
    events = data.get("events", [])
    updated = data.get("updated", "")

    stale = ""
    try:
        cache_dt = datetime.fromisoformat(updated)
        age_h = (datetime.now(cache_dt.tzinfo) - cache_dt).total_seconds() / 3600
        if age_h > 24:
            stale = f'<div class="cal-stale">кэш устарел {int(age_h)}ч</div>\n'
    except Exception:
        pass

    today = today_str()
    done = done_event_summaries()
    by_date = {}
    for ev in events:
        by_date.setdefault(ev["date"], []).append(ev)

    b = '<h2 style="margin-top:0">Ближайшие события</h2>\n' + stale
    if not by_date:
        return b + '<div style="color:#444;font-size:0.8rem">Нет событий</div>'

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
        b += f'<div class="cal-day-header{header_cls}">{label}</div>\n'
        for ev in sorted(by_date[day_str], key=lambda x: x.get("start", "")):
            t = ev.get("type", "default")
            time_str = ev.get("start", "")
            end_str = ev.get("end", "")
            time_html = f"{time_str}–{end_str}" if time_str and end_str else (time_str or "весь день")
            summary = ev["summary"]
            is_done = (day_str, summary) in done
            done_cls = " cal-done" if is_done else ""
            if is_today:
                b += f'<div class="cal-event {t}{done_cls}" data-summary="{summary}" data-date="{day_str}"><span class="cal-time">{time_html}</span><span class="cal-title">{summary}</span></div>\n'
            else:
                b += f'<div class="cal-event {t}{done_cls}"><span class="cal-time">{time_html}</span><span class="cal-title">{summary}</span></div>\n'

    return b


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

    try:
        cache_dt = datetime.fromisoformat(updated)
        age_h = (datetime.now(cache_dt.tzinfo) - cache_dt).total_seconds() / 3600
        if age_h > 24:
            b += f'<div class="cal-stale">Кэш устарел ({int(age_h)}ч назад) — попроси Claude обновить</div>\n'
    except Exception:
        pass

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
        refresh='<script>setTimeout(function(){if(!window.isDragging)location.reload()},5000)</script>',
        css=CSS, js=JS, body=body,
        sortable_js=_SORTABLE_JS,
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
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
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
        elif self.path == "/done-event":
            add_done_event(d["summary"], d.get("date"))
        elif self.path == "/rename":
            rename_task(d["file"], d["line"], d["text"])
        elif self.path == "/move":
            move_task(d["src_file"], d["src_line"], d["target_file"], d["target_line"], d["position"])
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


class ThreadingServer(http.server.ThreadingHTTPServer):
    address_family = __import__('socket').AF_INET
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        pass


if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print(f"Открываю {url}  (Ctrl+C чтобы остановить)")
    webbrowser.open(url)
    with ThreadingServer(("127.0.0.1", PORT), Handler) as srv:
        srv.serve_forever()
