#!/usr/bin/env python3
"""Brain Task Manager — today.md + tasks.json in browser."""

import http.server
import json
import re
import subprocess
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

PORT = 7777
BRAIN = Path(__file__).parent.parent
_SORTABLE_JS = (Path(__file__).parent / "sortable.min.js").read_text(encoding="utf-8")
TODAY = BRAIN / "05_PLANS/today.md"
CALENDAR_CACHE = BRAIN / "tools/calendar_cache.json"
TASKS_FILE = BRAIN / "05_PLANS/tasks/tasks.json"

PROJ_LABELS = {
    "health": "Здоровье",
    "ecom": "Ecom",
    "propria": "Propria",
    "ai-systems": "AI",
    "personal/finance": "Финансы",
    "personal/home": "Дом",
    "personal/purchases": "Покупки",
    "personal/media": "Медиа",
    "personal/family": "Семья",
    "personal/sailing": "Парус",
    "personal/development": "Развитие",
    "projects": "Проекты",
}
PROJ_ORDER = list(PROJ_LABELS.keys())

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
li.item .item-text { flex: 1; }
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
.task-row:not(.someday):not(.done-task) { opacity: .65; }
.task-row.someday { opacity: 1; }
.task-row.sortable-ghost { opacity: .25; background: var(--bg2); }
.task-row.drop-child { border-left: 3px solid #5b8dd9; }
.task-row.red { border-left: 3px solid #e74c3c; }
.task-row.green { border-left: 3px solid #2ecc71; }
.task-row.orange { border-left: 3px solid #f39c12; }
.task-chk { flex-shrink: 0; width: 15px; height: 15px; border-radius: 3px; background: var(--chk); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: .65rem; color: var(--text5); }
.task-chk:hover { background: var(--chk-hov); }
.task-text { flex: 1; }
.task-text[data-id]:hover { text-decoration: underline dotted var(--text4); cursor: text; }
.task-text[contenteditable=true] { outline: 1px solid #5b8dd9; border-radius: 3px; padding: 1px 4px; background: var(--bg2); cursor: text; text-decoration: none !important; }
.deadline { font-size: .75rem; color: var(--text4); flex-shrink: 0; }
.deadline.overdue { color: #e74c3c; }
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
.btn.type-btn { color: #888; font-size: .6rem; padding: 1px 4px; }
li.indent1 { margin-left: 20px; }
li.indent2 { margin-left: 40px; }
li.indent3 { margin-left: 60px; }
.indent1 { margin-left: 20px; }
.indent2 { margin-left: 40px; }
.indent3 { margin-left: 60px; }
.ts { font-size: .7rem; color: var(--bg5); position: fixed; bottom: 12px; right: 16px; }
.section-tasks { padding-left: 16px; }
.area-title[contenteditable=true] { outline: 1px solid #5b8dd9; border-radius: 3px; padding: 1px 4px; background: var(--bg2); cursor: text; }
.area-title:hover { text-decoration: underline dotted var(--text4); cursor: text; }
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

// today.md toggles
document.querySelectorAll('li[data-idx]').forEach(function(li) {
  li.addEventListener('click', function() { post('/toggle', {idx: parseInt(li.dataset.idx)}); });
});

// today.md: remove item
document.querySelectorAll('.del-today[data-idx]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    if (confirm('Убрать из сегодня?')) post('/remove-today', {idx: parseInt(btn.dataset.idx)});
  });
});

// quick add to inbox
window.addInboxTask = function() {
  var inp = document.getElementById('inbox-input');
  var title = (inp.value || '').trim();
  if (!title) return;
  inp.value = '';
  post('/add-task', {title: title});
};
var inboxInp = document.getElementById('inbox-input');
if (inboxInp) inboxInp.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') addInboxTask();
});

// tasks.json: toggle done
document.querySelectorAll('.task-chk[data-id]').forEach(function(el) {
  el.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/toggle-task', {id: el.dataset.id});
  });
});

// tasks.json: toggle someday
document.querySelectorAll('.s-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/someday', {id: btn.dataset.id});
  });
});

// calendar event done
document.querySelectorAll('.cal-event[data-summary]').forEach(function(el) {
  el.addEventListener('click', function() {
    post('/done-event', {summary: el.dataset.summary, date: el.dataset.date});
  });
});

// task search filter
var searchInput = document.getElementById('task-search');
if (searchInput) {
  searchInput.addEventListener('input', function() {
    var q = this.value.toLowerCase().trim();
    document.querySelectorAll('.task-row').forEach(function(row) {
      var text = (row.querySelector('.task-text') || row).textContent.toLowerCase();
      row.style.display = (!q || text.includes(q)) ? '' : 'none';
    });
    document.querySelectorAll('details').forEach(function(det) {
      var visible = det.querySelectorAll('.task-row:not([style*="none"])').length;
      det.style.display = (!q || visible > 0) ? '' : 'none';
      if (q && visible > 0) det.open = true;
    });
  });
}

// tasks.json: move up/down
document.querySelectorAll('.mv-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/move-order', {id: btn.dataset.id, direction: btn.dataset.dir});
  });
});

// tasks.json: delete
document.querySelectorAll('.del-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    if (confirm('Удалить?')) post('/delete', {id: btn.dataset.id});
  });
});

// tasks.json: rename (double-click)
document.querySelectorAll('.task-text[data-id]').forEach(function(el) {
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
      if (txt && txt !== orig) post('/rename', {id: el.dataset.id, text: txt});
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

// parent selector
document.querySelectorAll('.p-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var sel = document.createElement('select');
    sel.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.75rem;padding:2px 4px;max-width:200px';
    var none = document.createElement('option');
    none.value = '';
    none.textContent = '— нет родителя —';
    sel.appendChild(none);
    (window.AREAS || []).forEach(function(a) {
      var opt = document.createElement('option');
      opt.value = a.id;
      opt.textContent = a.title;
      sel.appendChild(opt);
    });
    btn.replaceWith(sel);
    sel.focus();
    sel.addEventListener('change', function() {
      post('/set-parent', {id: btn.dataset.id, parent_id: sel.value || null});
      setTimeout(function() { if (sel.parentNode) sel.replaceWith(btn); }, 100);
    });
    sel.addEventListener('blur', function() { setTimeout(function() { if (sel.parentNode) sel.replaceWith(btn); }, 200); });
    sel.addEventListener('keydown', function(e) { if (e.key === 'Escape') sel.replaceWith(btn); });
  });
});

// deadline editor
document.querySelectorAll('.d-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var inp = document.createElement('input');
    inp.type = 'date';
    inp.value = btn.dataset.deadline || '';
    inp.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.75rem;padding:2px 4px;width:130px';
    btn.replaceWith(inp);
    inp.focus();
    function save() {
      post('/set-deadline', {id: btn.dataset.id, deadline: inp.value || null});
      setTimeout(function() { location.reload(); }, 150);
    }
    inp.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); save(); }
      if (e.key === 'Escape') inp.replaceWith(btn);
    });
    inp.addEventListener('blur', function(e) {
      setTimeout(function() {
        if (document.activeElement === inp) return;
        if (inp.parentNode) { if (inp.value) save(); else inp.replaceWith(btn); }
      }, 300);
    });
  });
});

// type toggle
document.querySelectorAll('.type-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var cur = btn.dataset.current;
    var next = cur === 'area' ? 'task' : 'area';
    if (!confirm('Сменить тип с ' + cur.toUpperCase() + ' на ' + next.toUpperCase() + '?')) return;
    post('/set-type', {id: btn.dataset.id, type: next});
  });
});

// area rename (double-click)
document.querySelectorAll('.area-title[data-id]').forEach(function(el) {
  el.addEventListener('dblclick', function(e) {
    e.stopPropagation();
    e.preventDefault();
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
      if (txt && txt !== orig) post('/rename', {id: el.dataset.id, text: txt});
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

// drag & drop
window.isDragging = false;
var _childTarget = null;
var _lastOver = null;
var _hoverStart = null;

document.addEventListener('dragover', function(e) {
  var row = e.target.closest ? e.target.closest('.task-row[data-id]') : null;
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

var topAreas = document.getElementById('top-areas');
if (topAreas && typeof Sortable !== 'undefined') {
  Sortable.create(topAreas, {
    animation: 100,
    ghostClass: 'sortable-ghost',
    handle: 'summary',
    onEnd: function(evt) {
      var srcId = evt.item.dataset.id;
      var siblings = Array.from(topAreas.querySelectorAll(':scope > [data-id]'));
      var newIdx = siblings.indexOf(evt.item);
      var tgtId, position;
      if (newIdx > 0) {
        tgtId = siblings[newIdx - 1].dataset.id;
        position = 'after';
      } else if (siblings.length > 1) {
        tgtId = siblings[1].dataset.id;
        position = 'before';
      } else { return; }
      post('/move', {src_id: srcId, target_id: tgtId, position: position});
    }
  });
}

document.querySelectorAll('.today-section').forEach(function(ul) {
  if (typeof Sortable === 'undefined') return;
  Sortable.create(ul, {
    animation: 100,
    ghostClass: 'sortable-ghost',
    onEnd: function() {
      var indices = Array.from(ul.querySelectorAll('li[data-idx]')).map(function(li) {
        return parseInt(li.dataset.idx);
      });
      post('/reorder-today', {indices: indices});
    }
  });
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
      var srcId = srcEl.dataset.id;
      var tgtId, position;

      if (_childTarget) {
        tgtId = _childTarget.dataset.id;
        position = 'child';
        _childTarget.classList.remove('drop-child');
        _childTarget = null;
      } else {
        var siblings = Array.from(evt.to.querySelectorAll(':scope > .task-row'));
        var newIdx = siblings.indexOf(srcEl);
        if (newIdx > 0) {
          tgtId = siblings[newIdx - 1].dataset.id;
          position = 'after';
        } else if (siblings.length > 1) {
          tgtId = siblings[1].dataset.id;
          position = 'before';
        } else {
          location.reload();
          return;
        }
      }
      _lastOver = null;
      post('/move', {src_id: srcId, target_id: tgtId, position: position});
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
  <div style="display:flex;gap:6px;align-items:center;margin-left:16px;flex:1">
    <input id="inbox-input" type="text" placeholder="Быстрая задача в Inbox..." style="flex:1;max-width:320px;padding:6px 10px;border-radius:6px;border:none;background:var(--bg2);color:var(--text);font-size:.85rem;outline:1px solid var(--bdr)">
    <button onclick="addInboxTask()" style="padding:6px 12px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.85rem">+</button>
  </div>
  <button class="theme-btn" onclick="post('/undo',null);setTimeout(function(){{location.reload()}},300)" title="Отменить последнее действие" style="padding:6px 10px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.85rem;margin-left:4px">↩</button>
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
            indent = (len(line) - len(line.lstrip())) // 2
            text = re.sub(r'\s*- \[.\] ', '', line).strip()
            text = clean_text(text)
            item = {"done": done, "text": text, "line": i, "idx": idx, "indent": indent}
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

    def section_is_future(sec):
        m = re.search(r'(\d{1,2})\.(\d{2})', sec)
        if not m:
            return False
        try:
            d = date(date.today().year, int(m.group(2)), int(m.group(1)))
            return d > date.today()
        except ValueError:
            return False

    done_all = []
    for sec, items in sections:
        if section_is_future(sec):
            continue
        todo = [i for i in items if not i["done"]]
        done_all += [i for i in items if i["done"]]
        if not todo:
            continue
        sec_key = sec.replace(" ", "_")[:30]
        items_html = ""
        for item in todo:
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            indent_cls = f" indent{min(item['indent'], 3)}" if item.get("indent", 0) > 0 else ""
            items_html += f'<li class="item todo{extra}{indent_cls}" data-idx="{item["idx"]}"><span class="chk">·</span><span class="item-text">{item["text"]}</span><button class="btn del-today" data-idx="{item["idx"]}">×</button></li>\n'
        if sec == "Утренний чеклист":
            left += f'<details data-key="today_{sec_key}"><summary style="font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text4);padding:4px 0;list-style:none;cursor:pointer">{sec}</summary><ul class="today-section">\n{items_html}</ul></details>\n'
        else:
            left += f'<h2>{sec}</h2><ul class="today-section">\n{items_html}</ul>\n'

    if done_all:
        left += "<h2>Сделано</h2><ul>\n"
        for item in done_all:
            left += f'<li class="item done-item" data-idx="{item["idx"]}"><span class="chk">✓</span><span>{item["text"]}</span></li>\n'
        left += "</ul>\n"

    right = render_calendar_today()
    return f'<div class="two-col"><div class="col-left">{left}</div><div class="col-right">{right}</div></div>\n'


def normalize_title(text):
    text = re.sub(r'[🔴🟢🟧⏳]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return re.sub(r'\s+', ' ', text).strip().lower()


def sync_today_to_tasks(item_text, done):
    norm = normalize_title(item_text)
    if not norm:
        return
    tasks = load_tasks()
    changed = False
    for t in tasks:
        if t.get("type") == "area":
            continue
        if normalize_title(t.get("title", "")) == norm:
            t["status"] = "done" if done else "todo"
            t["done_at"] = today_str() if done else None
            changed = True
            break
    if changed:
        save_tasks(tasks)


def sync_tasks_to_today(task_title, done):
    if not TODAY.exists():
        return
    norm = normalize_title(task_title)
    lines = TODAY.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not re.match(r'\s*- \[.\]', line):
            continue
        raw = re.sub(r'\s*- \[.\] (\d{4}-\d{2}-\d{2} )?', '', line).strip()
        if normalize_title(raw) == norm:
            if done:
                lines[i] = re.sub(r'- \[ \] ', f'- [x] {today_str()} ', line)
            else:
                lines[i] = re.sub(r'- \[x\] \d{4}-\d{2}-\d{2} ', '- [ ] ', line, flags=re.I)
                lines[i] = re.sub(r'- \[x\] ', '- [ ] ', lines[i], flags=re.I)
            break
    TODAY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def toggle_today(path, idx):
    lines = path.read_text(encoding="utf-8").splitlines()
    _, _, all_items = parse_today(path)
    item = next((i for i in all_items if i["idx"] == idx), None)
    if not item:
        return
    line = lines[item["line"]]
    now_done = item["done"]
    if now_done:
        line = re.sub(r'- \[x\] \d{4}-\d{2}-\d{2} ', '- [ ] ', line, flags=re.I)
        line = re.sub(r'- \[x\] ', '- [ ] ', line, flags=re.I)
    else:
        line = re.sub(r'- \[ \] ', f'- [x] {today_str()} ', line)
    lines[item["line"]] = line
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sync_today_to_tasks(item["text"], not now_done)


# ── TASKS JSON ───────────────────────────────────────────

def load_tasks():
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    for t in tasks:
        if t.get("order") is None:
            t["order"] = 0.0
    return tasks


UNDO_FILE = BRAIN / "tools/tasks_undo.json"

def save_tasks(tasks):
    # save undo backup before writing
    if TASKS_FILE.exists():
        UNDO_FILE.write_text(TASKS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    TASKS_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        ["git", "commit", "-am", "server: update tasks"],
        cwd=BRAIN, capture_output=True
    )

def undo_tasks():
    if UNDO_FILE.exists():
        TASKS_FILE.write_text(UNDO_FILE.read_text(encoding="utf-8"), encoding="utf-8")


def render_task_row(task, all_tasks, depth=0):
    task_id = task["id"]
    title = task.get("title", "")
    priority = task.get("priority")
    someday = task.get("someday", False)
    deadline = task.get("deadline")
    done = task.get("status") == "done"

    children = sorted(
        [t for t in all_tasks if t.get("parent_id") == task_id and t.get("status") != "done"],
        key=lambda t: t.get("order", 0),
    )

    indent_cls = f" indent{min(depth, 3)}" if depth > 0 else ""
    done_cls = " done-task" if done else ""
    someday_cls = " someday" if someday else ""
    prio_cls = {"red": " red", "green": " green", "orange": " orange"}.get(priority, "")
    chk_icon = "✓" if done else "·"
    s_active = " active" if someday else ""
    s_label = "✕S" if someday else "S"

    dl_html = ""
    if deadline:
        try:
            days = (date.fromisoformat(deadline) - date.today()).days
            overdue = " overdue" if days < 0 else ""
        except Exception:
            overdue = ""
        dl_html = f'<span class="deadline{overdue}">{deadline}</span>'

    dl_val = deadline or ""
    html = (
        f'<div class="task-row{indent_cls}{done_cls}{someday_cls}{prio_cls}" data-id="{task_id}">\n'
        f'  <span class="task-chk" data-id="{task_id}">{chk_icon}</span>\n'
        f'  <span class="task-text" data-id="{task_id}">{title}</span>\n'
        f'  {dl_html}\n'
        f'  <button class="btn type-btn" data-id="{task_id}" data-current="task">T</button>\n'
        f'  <button class="btn p-btn" data-id="{task_id}">P</button>\n'
        f'  <button class="btn d-btn" data-id="{task_id}" data-deadline="{dl_val}">D</button>\n'
        f'  <button class="btn s-btn{s_active}" data-id="{task_id}">{s_label}</button>\n'
        f'  <button class="btn mv-btn" data-id="{task_id}" data-dir="up" title="Вверх">▲</button>\n'
        f'  <button class="btn mv-btn" data-id="{task_id}" data-dir="down" title="Вниз">▼</button>\n'
        f'  <button class="btn del-btn" data-id="{task_id}">×</button>\n'
        f'</div>\n'
    )
    for child in children:
        html += render_task_row(child, all_tasks, depth + 1)
    return html


def render_area(area, all_nodes):
    area_id = area["id"]
    title = area.get("title", "")
    children = sorted(
        [t for t in all_nodes if t.get("parent_id") == area_id],
        key=lambda t: t.get("order", 0),
    )
    if not children:
        return (
            f'<div class="task-row" data-id="{area_id}">\n'
            f'  <span class="task-text">{title}'
            f'<span style="font-size:.7rem;color:var(--text4);margin-left:6px">area</span></span>\n'
            f'  <button class="btn del-btn" data-id="{area_id}">×</button>\n'
            f'</div>\n'
        )
    b = f'<details data-key="{area_id}" data-id="{area_id}"><summary><span class="area-title" data-id="{area_id}">{title}</span><button class="btn type-btn" data-id="{area_id}" data-current="area" onclick="event.stopPropagation()">A</button></summary>\n'
    b += '<div class="section-tasks">\n'
    for child in children:
        if child.get("type") == "area":
            b += render_area(child, all_nodes)
        else:
            b += render_task_row(child, all_nodes)
    b += "</div>\n</details>\n"
    return b


def build_area_options(areas, all_nodes, prefix=""):
    opts = []
    for a in sorted(areas, key=lambda t: t.get("order", 0)):
        path = prefix + a.get("title", "")
        opts.append({"id": a["id"], "title": path})
        sub = [t for t in all_nodes if t.get("parent_id") == a["id"] and t.get("type") == "area"]
        opts.extend(build_area_options(sub, all_nodes, path + " › "))
    return opts


def render_tasks():
    tasks = load_tasks()
    active = [t for t in tasks if t.get("status") != "done"]
    top_areas = sorted(
        [t for t in active if t.get("type") == "area" and not t.get("parent_id")],
        key=lambda t: t.get("order", 0),
    )
    areas_json = json.dumps(build_area_options(top_areas, active), ensure_ascii=False)
    search_style = "width:100%;max-width:500px;padding:8px 12px;border-radius:6px;border:none;background:var(--bg2);color:var(--text);font-size:.88rem;outline:1px solid var(--bdr);margin-bottom:16px;display:block"
    b = (f"<h1>Задачи</h1>\n<script>window.AREAS={areas_json};</script>\n"
         f'<input id="task-search" type="text" placeholder="Поиск по задачам..." style="{search_style}">\n'
         f"<div id=\"top-areas\">\n")
    for area in top_areas:
        b += render_area(area, active)
    b += "</div>\n"
    return b


def toggle_task(task_id):
    tasks = load_tasks()
    title = ""
    done = False
    for t in tasks:
        if t["id"] == task_id:
            if t.get("status") == "done":
                t["status"] = "todo"
                t["done_at"] = None
                done = False
            else:
                t["status"] = "done"
                t["done_at"] = today_str()
                done = True
            title = t.get("title", "")
            break
    save_tasks(tasks)
    if title:
        sync_tasks_to_today(title, done)


def toggle_someday(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["someday"] = not t.get("someday", False)
            break
    save_tasks(tasks)


def delete_task(task_id):
    tasks = load_tasks()
    ids_to_delete = {task_id}
    changed = True
    while changed:
        changed = False
        for t in tasks:
            if t.get("parent_id") in ids_to_delete and t["id"] not in ids_to_delete:
                ids_to_delete.add(t["id"])
                changed = True
    save_tasks([t for t in tasks if t["id"] not in ids_to_delete])


def set_task_parent(task_id, parent_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if parent_id:
                t["parent_id"] = parent_id
            else:
                t.pop("parent_id", None)
            break
    save_tasks(tasks)


def set_task_deadline(task_id, deadline):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if deadline:
                t["deadline"] = deadline
            else:
                t["deadline"] = None
            break
    save_tasks(tasks)


def set_task_type(task_id, new_type):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["type"] = new_type
            break
    save_tasks(tasks)


def rename_task(task_id, new_text):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["title"] = new_text
            break
    save_tasks(tasks)


def reorder_today(path, ordered_indices):
    _, _, all_items = parse_today(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    by_idx = {item["idx"]: item for item in all_items}
    items_in_order = [by_idx[i] for i in ordered_indices if i in by_idx]
    if len(items_in_order) < 2:
        return
    original_line_nums = sorted(item["line"] for item in items_in_order)
    # capture content before any writes to avoid overwrite-then-read bug
    contents = [lines[item["line"]] for item in items_in_order]
    for line_num, content in zip(original_line_nums, contents):
        lines[line_num] = content
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_today_line(path, idx):
    _, _, all_items = parse_today(path)
    item = next((i for i in all_items if i["idx"] == idx), None)
    if not item:
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    del lines[item["line"]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_task_inbox(title):
    tasks = load_tasks()
    if not any(t["id"] == "area-inbox" for t in tasks):
        tasks.insert(0, {"id": "area-inbox", "title": "Inbox", "type": "area", "order": -1})
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)[:50]
    task_id = f"inbox-{slug}"
    existing_ids = {t["id"] for t in tasks}
    if task_id in existing_ids:
        import time
        task_id = f"inbox-{slug}-{int(time.time()) % 10000}"
    tasks.append({
        "id": task_id,
        "title": title,
        "parent_id": "area-inbox",
        "status": "todo",
        "someday": True,
        "created_at": today_str()
    })
    save_tasks(tasks)


def move_task(src_id, target_id, position):
    tasks = load_tasks()
    by_id = {t["id"]: t for t in tasks}
    src = by_id.get(src_id)
    target = by_id.get(target_id)
    if not src or not target:
        return

    if position == "child":
        src["parent_id"] = target_id
        siblings = [t for t in tasks if t.get("parent_id") == target_id]
        src["order"] = max((t.get("order", 0) for t in siblings), default=0) + 1.0
    else:
        src["parent_id"] = target.get("parent_id")
        parent_id = target.get("parent_id")
        siblings = sorted(
            [t for t in tasks if t.get("parent_id") == parent_id and t["id"] != src_id],
            key=lambda t: t.get("order", 0),
        )
        target_order = target.get("order", 0)
        target_idx = next((i for i, t in enumerate(siblings) if t["id"] == target_id), 0)
        if position == "after":
            if target_idx + 1 < len(siblings):
                nxt = siblings[target_idx + 1].get("order", target_order + 2)
                src["order"] = (target_order + nxt) / 2
            else:
                src["order"] = target_order + 1.0
        else:  # before
            if target_idx > 0:
                prv = siblings[target_idx - 1].get("order", target_order - 2)
                src["order"] = (prv + target_order) / 2
            else:
                src["order"] = target_order - 1.0

    save_tasks(tasks)


def move_task_order(task_id, direction):
    tasks = load_tasks()
    by_id = {t["id"]: t for t in tasks}
    task = by_id.get(task_id)
    if not task:
        return
    parent_id = task.get("parent_id")
    siblings = sorted(
        [t for t in tasks if t.get("parent_id") == parent_id and t.get("status") != "done"],
        key=lambda t: t.get("order", 0),
    )
    idx = next((i for i, t in enumerate(siblings) if t["id"] == task_id), None)
    if idx is None:
        return
    if direction == "up" and idx > 0:
        a, b = siblings[idx - 1], siblings[idx]
        a["order"], b["order"] = b.get("order", 0), a.get("order", 0)
    elif direction == "down" and idx < len(siblings) - 1:
        a, b = siblings[idx], siblings[idx + 1]
        a["order"], b["order"] = b.get("order", 0), a.get("order", 0)
    save_tasks(tasks)


# ── CALENDAR ─────────────────────────────────────────────

def done_event_summaries():
    if not TODAY.exists():
        return set()
    done = set()
    for line in TODAY.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\s*- \[x\] (\d{4}-\d{2}-\d{2}) (.+)', line)
        if m:
            done.add((m.group(1), m.group(2).strip()))
    return done


def add_done_event(summary, date_str=None):
    entry_date = date_str or today_str()
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
        if day_str < today:
            continue
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


DAY_NAMES = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTH_NAMES = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


# ── SERVER ───────────────────────────────────────────────

def make_page(body, page):
    return HTML.format(
        title="Сегодня" if page == "today" else "Задачи",
        refresh='<script>setTimeout(function(){var a=document.activeElement,tag=a?a.tagName:"";if(!window.isDragging&&tag!=="INPUT"&&tag!=="SELECT"&&tag!=="TEXTAREA"&&!a.isContentEditable)location.reload()},5000)</script>',
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
            toggle_task(d["id"])
        elif self.path == "/someday":
            toggle_someday(d["id"])
        elif self.path == "/delete":
            delete_task(d["id"])
        elif self.path == "/done-event":
            add_done_event(d["summary"], d.get("date"))
        elif self.path == "/rename":
            rename_task(d["id"], d["text"])
        elif self.path == "/set-type":
            set_task_type(d["id"], d["type"])
        elif self.path == "/set-parent":
            set_task_parent(d["id"], d.get("parent_id"))
        elif self.path == "/set-deadline":
            set_task_deadline(d["id"], d.get("deadline"))
        elif self.path == "/remove-today":
            remove_today_line(TODAY, d["idx"])
        elif self.path == "/reorder-today":
            reorder_today(TODAY, d["indices"])
        elif self.path == "/add-task":
            add_task_inbox(d["title"])
        elif self.path == "/move":
            move_task(d["src_id"], d["target_id"], d["position"])
        elif self.path == "/undo":
            undo_tasks()
        elif self.path == "/move-order":
            move_task_order(d["id"], d["direction"])
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


class ThreadingServer(http.server.ThreadingHTTPServer):
    address_family = __import__("socket").AF_INET
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        pass


if __name__ == "__main__":
    url = f"http://localhost:{PORT}"
    print(f"Открываю {url}  (Ctrl+C чтобы остановить)")
    webbrowser.open(url)
    with ThreadingServer(("127.0.0.1", PORT), Handler) as srv:
        srv.serve_forever()
