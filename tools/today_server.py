#!/usr/bin/env python3
"""Brain Task Manager — today.md + tasks.json in browser."""

import http.server
import json
import re
import subprocess
import sys
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import priority as _priority

PORT = 7777
BRAIN = Path(__file__).parent.parent
_SORTABLE_JS = (Path(__file__).parent / "sortable.min.js").read_text(encoding="utf-8")
TODAY = BRAIN / "05_PLANS/today.md"
CALENDAR_CACHE = BRAIN / "tools/calendar_cache.json"
TASKS_FILE = BRAIN / "05_PLANS/tasks/tasks.json"
SESSION_LOG = BRAIN / "04_THINKING" / "session-log.jsonl"

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
.sess-day { margin-bottom: 24px; }
.sess-day-header { font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; color: var(--text4); margin-bottom: 8px; padding: 4px 0; border-bottom: 1px solid var(--bdr); }
.sess-card { background: var(--bg2); border-radius: 6px; padding: 10px 14px; margin: 4px 0; display: flex; align-items: baseline; gap: 12px; }
.sess-card:hover { background: var(--row-hov); }
.sess-title { flex: 1; font-size: .9rem; color: var(--text2); }
.sess-meta { font-size: .75rem; color: var(--text4); flex-shrink: 0; }
.sess-files { font-size: .72rem; color: var(--text5); margin-top: 4px; }
.sess-tag { display: inline-block; font-size: .65rem; padding: 1px 5px; border-radius: 3px; background: var(--bg4); color: var(--text4); margin-right: 4px; }
.item-text.task-linked { cursor:pointer; }
.item-text.task-linked:hover { text-decoration:underline dotted var(--text4); }
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.6); z-index:200; display:none; align-items:flex-start; justify-content:center; padding-top:80px; }
.modal-overlay.open { display:flex; }
.modal { background:var(--bg2); border-radius:10px; padding:24px 28px; min-width:360px; max-width:600px; width:90%; max-height:75vh; overflow-y:auto; position:relative; }
.modal-close { position:absolute; top:12px; right:14px; background:none; border:none; color:var(--text4); font-size:1.1rem; cursor:pointer; padding:4px 8px; border-radius:4px; }
.modal-close:hover { color:var(--text); background:var(--bg4); }
.modal-title-area { font-size:1.05rem; font-weight:600; color:var(--text); margin-bottom:20px; padding-right:24px; }
.modal-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:16px; }
.modal-field { background:var(--bg3); border-radius:6px; padding:10px 12px; }
.modal-field-label { font-size:.68rem; color:var(--text4); text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px; }
.modal-field-value { font-size:.88rem; color:var(--text2); }
.modal-subtasks-header { font-size:.72rem; color:var(--text4); text-transform:uppercase; letter-spacing:.07em; margin:16px 0 8px; }
.modal-subtask { display:flex; align-items:center; gap:8px; padding:7px 10px; border-radius:5px; background:var(--bg3); margin:3px 0; font-size:.87rem; color:var(--text2); }
.modal-subtask.done-sub { color:var(--text5); text-decoration:line-through; }
.mchk { flex-shrink:0; width:15px; height:15px; border-radius:3px; background:var(--bg4); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:.65rem; color:var(--text5); }
.mchk:hover { background:var(--chk-hov); }
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

// today.md toggles — checkbox only
document.querySelectorAll('li[data-idx]').forEach(function(li) {
  var chk = li.querySelector('.chk');
  if (chk) chk.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/toggle', {idx: parseInt(li.dataset.idx)});
  });
  var txt = li.querySelector('.item-text');
  if (txt) txt.addEventListener('click', function(e) {
    e.stopPropagation();
    var tid = li.dataset.taskId;
    if (tid) openTaskModal(tid);
  });
});

// today tasks from tasks.json (scheduled) — checkbox + modal
document.querySelectorAll('li[data-task-id]:not([data-idx])').forEach(function(li) {
  var tid = li.dataset.taskId;
  if (!tid) return;
  var chk = li.querySelector('.task-chk');
  if (chk) chk.addEventListener('click', function(e) {
    e.stopPropagation();
    li.classList.add('done-item');
    chk.textContent = '✓';
    post('/toggle-task', {id: tid});
  });
  var txt = li.querySelector('.item-text');
  if (txt) txt.addEventListener('click', function(e) {
    e.stopPropagation();
    openTaskModal(tid);
  });
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
  var ctx = (document.getElementById('inbox-context') || {}).value || null;
  var marker = (document.getElementById('inbox-marker') || {}).value || null;
  post('/add-task', {title: title, context: ctx, marker: marker});
};
var inboxInp = document.getElementById('inbox-input');
if (inboxInp) inboxInp.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') addInboxTask();
});

// overdue filter
(function() {
  var btn = document.getElementById('overdue-filter');
  if (!btn) return;
  var today = new Date().toISOString().split('T')[0];
  var on = localStorage.getItem('od-filter') === '1';
  function apply() {
    var rows = document.querySelectorAll('.task-row');
    if (on) {
      var visibleIds = new Set();
      rows.forEach(function(r) {
        var dl = r.querySelector('.deadline');
        if (dl && dl.classList.contains('overdue')) visibleIds.add(r.dataset.id);
      });
      rows.forEach(function(r) {
        if (!r.classList.contains('done-task')) {
          r.style.display = visibleIds.has(r.dataset.id) ? '' : 'none';
        }
      });
      document.querySelectorAll('details').forEach(function(det) {
        var hasVisible = Array.from(det.querySelectorAll('.task-row')).some(function(r) {
          return visibleIds.has(r.dataset.id);
        });
        det.style.display = hasVisible ? '' : 'none';
        if (hasVisible) det.open = true;
      });
    } else {
      rows.forEach(function(r) { r.style.display = ''; });
      document.querySelectorAll('details').forEach(function(det) { det.style.display = ''; });
    }
    btn.style.background = on ? 'var(--s-act)' : '';
    btn.style.color = on ? '#5b8dd9' : '';
  }
  apply();
  btn.addEventListener('click', function() {
    on = !on;
    localStorage.setItem('od-filter', on ? '1' : '0');
    // turn off someday filter if we're turning this on
    if (on) localStorage.setItem('sd-filter', '0');
    apply();
    // re-apply someday off
    var sdBtn = document.getElementById('someday-filter');
    if (sdBtn && on) sdBtn.click && false;
  });
})();

// tasks.json: toggle done
document.querySelectorAll('.task-chk[data-id]').forEach(function(el) {
  el.addEventListener('click', function(e) {
    e.stopPropagation();
    var row = el.closest('.task-row');
    var isDone = row && row.classList.contains('done-task');
    if (row) {
      if (!isDone) {
        row.classList.add('done-task');
        el.textContent = '✓';
        row.style.transition = 'opacity .15s';
        row.style.opacity = '0.3';
      } else {
        row.classList.remove('done-task');
        el.textContent = '·';
        row.style.opacity = '';
      }
    }
    post('/toggle-task', {id: el.dataset.id});
  });
});

// someday filter
(function() {
  var btn = document.getElementById('someday-filter');
  if (!btn) return;
  var sdCount = parseInt(btn.dataset.count || '0', 10);
  var sdLimit = window.SOMEDAY_LIMIT || 20;
  var on = localStorage.getItem('sd-filter') === '1';
  function apply() {
    var rows = document.querySelectorAll('.task-row');
    if (on) {
      // collect IDs of someday tasks, then expand to include their descendants
      var visibleIds = new Set();
      rows.forEach(function(r) { if (r.classList.contains('someday')) visibleIds.add(r.dataset.id); });
      var changed = true;
      while (changed) {
        changed = false;
        rows.forEach(function(r) {
          var pid = r.dataset.parentId;
          if (pid && visibleIds.has(pid) && !visibleIds.has(r.dataset.id)) {
            visibleIds.add(r.dataset.id);
            changed = true;
          }
        });
      }
      rows.forEach(function(r) {
        if (!r.classList.contains('done-task')) {
          r.style.display = visibleIds.has(r.dataset.id) ? '' : 'none';
        }
      });
      // open all <details> that contain at least one visible someday row
      document.querySelectorAll('details').forEach(function(det) {
        var hasVisible = det.querySelectorAll('.task-row.someday').length > 0;
        if (hasVisible) det.open = true;
      });
    } else {
      rows.forEach(function(r) { r.style.display = ''; });
    }
    btn.textContent = 'Someday (' + sdCount + '/' + sdLimit + ')' + (on ? ' ✓' : '');
    btn.style.background = on ? 'var(--s-act)' : '';
    btn.style.color = sdCount > sdLimit ? '#e74c3c' : (on ? '#5b8dd9' : '');
    btn.style.fontWeight = sdCount > sdLimit ? '600' : '';
  }
  apply();
  btn.addEventListener('click', function() {
    on = !on;
    localStorage.setItem('sd-filter', on ? '1' : '0');
    apply();
  });
})();

// tasks.json: toggle someday
document.querySelectorAll('.s-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    fetch('/someday', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: btn.dataset.id})})
      .then(function(r) { return r.json().catch(function() { return {}; }); })
      .then(function(d) {
        if (d.blocked) { alert(d.warning); return; }
        location.reload();
      });
  });
});

// tasks.json: cycle marker
document.querySelectorAll('.m-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    post('/set-marker', {id: btn.dataset.id});
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
    Array.from(document.querySelectorAll('details')).reverse().forEach(function(det) {
      var summaryText = (det.querySelector('summary') || det).textContent.toLowerCase();
      var summaryMatch = q && summaryText.includes(q);
      if (summaryMatch) {
        det.querySelectorAll('.task-row').forEach(function(r) { r.style.display = ''; });
      }
      var visible = det.querySelectorAll('.task-row:not([style*="none"])').length;
      det.style.display = (!q || visible > 0 || summaryMatch) ? '' : 'none';
      if (q && (visible > 0 || summaryMatch)) det.open = true;
    });
  });
}

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
    var orig = el.dataset.raw || el.textContent;
    el.contentEditable = 'true';
    el.textContent = orig;
    el.focus();
    var range = document.createRange();
    range.selectNodeContents(el);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    function save() {
      el.contentEditable = 'false';
      var txt = el.textContent.trim();
      if (txt && txt !== orig) {
        fetch('/rename', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: el.dataset.id, text: txt})})
          .then(function(r) {
            if (!r.ok) { r.json().then(function(d) { alert(d.error || 'Ошибка'); }); el.textContent = orig; }
          });
      } else el.textContent = orig;
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

// pick main task ("Первая задача")
(function() {
  var btn = document.getElementById('pick-main-task');
  if (!btn) return;
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    fetch('/api/top-priority').then(function(r) { return r.json(); }).then(function(list) {
      var sel = document.createElement('select');
      sel.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.75rem;padding:2px 4px;max-width:320px';
      var none = document.createElement('option');
      none.value = '';
      none.textContent = '— выбрать задачу —';
      sel.appendChild(none);
      list.forEach(function(t) {
        var opt = document.createElement('option');
        opt.value = t.title;
        opt.textContent = 'P' + t.score + ' — ' + t.title;
        sel.appendChild(opt);
      });
      btn.replaceWith(sel);
      sel.focus();
      sel.addEventListener('change', function() {
        if (sel.value) post('/set-main-task', {title: sel.value});
      });
      sel.addEventListener('blur', function() { setTimeout(function() { if (sel.parentNode) sel.replaceWith(btn); }, 200); });
    });
  });
})();

// add subtask inline
document.querySelectorAll('.sub-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var inp = document.createElement('input');
    inp.type = 'text';
    inp.placeholder = 'Текст подзадачи...';
    inp.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.75rem;padding:2px 4px;max-width:220px';
    btn.replaceWith(inp);
    inp.focus();
    function restore() { if (inp.parentNode) inp.replaceWith(btn); }
    function submit() {
      var title = inp.value.trim();
      if (title) {
        post('/add-task', {title: title, parent_id: btn.dataset.id});
      } else {
        restore();
      }
    }
    inp.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); submit(); }
      if (e.key === 'Escape') restore();
    });
    inp.addEventListener('blur', function() { setTimeout(function() { if (inp.parentNode && !inp.value.trim()) restore(); }, 150); });
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
      if (a.id === btn.dataset.id) return;
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
      if (txt && txt !== orig) {
        fetch('/rename', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: el.dataset.id, text: txt})})
          .then(function(r) {
            if (!r.ok) { r.json().then(function(d) { alert(d.error || 'Ошибка'); }); el.textContent = orig; }
          });
      } else el.textContent = orig;
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

// tasks.json: toggle scheduled for today
document.querySelectorAll('.today-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var isScheduled = btn.classList.contains('active');
    var today = new Date().toISOString().split('T')[0];
    post('/set-scheduled-date', {id: btn.dataset.id, scheduled_date: isScheduled ? null : today});
  });
});

// tasks.json: cycle context
document.querySelectorAll('.ctx-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var cycle = ['', 'deep', 'perekur', 'afternoon'];
    var labels = {'': 'ctx', 'deep': '🧠', 'perekur': '🚶', 'afternoon': '🌆'};
    var cur = btn.dataset.context || '';
    var idx = cycle.indexOf(cur);
    var nxt = cycle[(idx + 1) % cycle.length];
    btn.dataset.context = nxt;
    btn.textContent = labels[nxt];
    btn.title = 'Контекст: ' + (nxt || 'нет');
    post('/set-context', {id: btn.dataset.id, context: nxt || null});
  });
});

// tasks.json: set recurring
document.querySelectorAll('.r-btn[data-id]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    var sel = document.createElement('select');
    sel.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.75rem;padding:2px 4px';
    [['', 'нет'], ['weekly', 'еженедельно'], ['monthly', 'ежемесячно'], ['quarterly', 'раз в квартал'], ['yearly', 'ежегодно']].forEach(function(pair) {
      var opt = document.createElement('option');
      opt.value = pair[0];
      opt.textContent = pair[1];
      if (btn.dataset.recurring === pair[0]) opt.selected = true;
      sel.appendChild(opt);
    });
    btn.replaceWith(sel);
    sel.focus();
    sel.addEventListener('change', function() {
      post('/set-recurring', {id: btn.dataset.id, recurring: sel.value || null});
      setTimeout(function() { if (sel.parentNode) sel.replaceWith(btn); }, 100);
    });
    sel.addEventListener('blur', function() { setTimeout(function() { if (sel.parentNode) sel.replaceWith(btn); }, 200); });
    sel.addEventListener('keydown', function(e) { if (e.key === 'Escape') sel.replaceWith(btn); });
  });
});

// task detail modal
function esc(s) { var d = document.createElement('div'); d.textContent = String(s == null ? '' : s); return d.innerHTML; }

function makeField(label, value) {
  var wrap = document.createElement('div');
  wrap.className = 'modal-field';
  var lbl = document.createElement('div');
  lbl.className = 'modal-field-label';
  lbl.textContent = label;
  var val = document.createElement('div');
  val.className = 'modal-field-value';
  val.textContent = value;
  wrap.appendChild(lbl);
  wrap.appendChild(val);
  return wrap;
}

function makeEditableDate(label, value, endpoint, taskId, extraKey) {
  var wrap = document.createElement('div');
  wrap.className = 'modal-field';
  wrap.style.cursor = 'pointer';
  var lbl = document.createElement('div');
  lbl.className = 'modal-field-label';
  lbl.textContent = label;
  var val = document.createElement('div');
  val.className = 'modal-field-value';
  val.textContent = value || '—';
  wrap.appendChild(lbl);
  wrap.appendChild(val);
  wrap.addEventListener('click', function() {
    var inp = document.createElement('input');
    inp.type = 'date';
    inp.value = value || '';
    inp.style.cssText = 'background:var(--bg2);color:var(--text);border:1px solid #5b8dd9;border-radius:3px;font-size:.85rem;padding:2px 6px;width:100%';
    val.replaceWith(inp);
    inp.focus();
    function save() {
      var body = {id: taskId};
      body[extraKey] = inp.value || null;
      post(endpoint, body);
      val.textContent = inp.value || '—';
      value = inp.value;
      inp.replaceWith(val);
    }
    inp.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); save(); }
      if (e.key === 'Escape') { inp.replaceWith(val); }
    });
    inp.addEventListener('blur', function() { setTimeout(function() { if (inp.parentNode) save(); }, 200); });
  });
  return wrap;
}

function makeContextSelect(label, value, taskId) {
  var wrap = document.createElement('div');
  wrap.className = 'modal-field';
  var lbl = document.createElement('div');
  lbl.className = 'modal-field-label';
  lbl.textContent = label;
  var sel = document.createElement('select');
  sel.style.cssText = 'background:var(--bg3);color:var(--text);border:none;font-size:.85rem;width:100%;padding:2px 0;cursor:pointer';
  [['', '— нет —'], ['deep', '🧠 Задачи (утро)'], ['perekur', '🚶 Перекур'], ['afternoon', '🌆 2-я половина']].forEach(function(pair) {
    var opt = document.createElement('option');
    opt.value = pair[0];
    opt.textContent = pair[1];
    if (value === pair[0]) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.addEventListener('change', function() {
    post('/set-context', {id: taskId, context: sel.value || null});
  });
  wrap.appendChild(lbl);
  wrap.appendChild(sel);
  return wrap;
}

function openTaskModal(taskId) {
  fetch('/api/task?id=' + encodeURIComponent(taskId))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      document.getElementById('modal-title-text').textContent = d.title || '';
      var grid = document.createElement('div');
      grid.className = 'modal-grid';
      grid.appendChild(makeEditableDate('Запланировано', d.scheduled_date, '/set-scheduled-date', d.id, 'scheduled_date'));
      grid.appendChild(makeEditableDate('Дедлайн', d.deadline, '/set-deadline', d.id, 'deadline'));
      grid.appendChild(makeContextSelect('Контекст', d.context || '', d.id));
      grid.appendChild(makeField('Someday', d.someday ? '✓' : '—'));
      grid.appendChild(makeField('Маркер', d.marker || '—'));
      grid.appendChild(makeField('Область', d.parent_title || '—'));
      var fieldsEl = document.getElementById('modal-fields');
      fieldsEl.innerHTML = '';
      fieldsEl.appendChild(grid);
      var sub = document.getElementById('modal-subtasks');
      var subSec = document.getElementById('modal-subtasks-section');
      sub.innerHTML = '';
      if (d.subtasks && d.subtasks.length > 0) {
        d.subtasks.forEach(function(s) {
          var row = document.createElement('div');
          row.className = 'modal-subtask' + (s.done ? ' done-sub' : '');
          var chk = document.createElement('span');
          chk.className = 'mchk';
          chk.textContent = s.done ? '✓' : '·';
          chk.dataset.id = s.id;
          chk.addEventListener('click', function(e) {
            e.stopPropagation();
            post('/toggle-task', {id: s.id});
            chk.textContent = chk.textContent === '·' ? '✓' : '·';
          });
          var title = document.createElement('span');
          title.textContent = s.title;
          row.appendChild(chk);
          row.appendChild(title);
          sub.appendChild(row);
        });
        subSec.style.display = '';
      } else {
        subSec.style.display = 'none';
      }
      document.getElementById('task-modal').classList.add('open');
    });
}
function closeTaskModal() {
  document.getElementById('task-modal').classList.remove('open');
}
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeTaskModal();
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
  <a href="/sessions" class="{nav_sessions}">Сессии</a>
  <div style="display:flex;gap:6px;align-items:center;margin-left:16px;flex:1">
    <input id="inbox-input" type="text" placeholder="Быстрая задача в Inbox..." style="flex:1;max-width:280px;padding:6px 10px;border-radius:6px;border:none;background:var(--bg2);color:var(--text);font-size:.85rem;outline:1px solid var(--bdr)">
    <select id="inbox-context" style="padding:5px 6px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.82rem" title="Контекст">
      <option value="">ctx</option>
      <option value="deep">🧠 утро</option>
      <option value="perekur">🚶 перекур</option>
      <option value="afternoon">🌆 вечер</option>
    </select>
    <select id="inbox-marker" style="padding:5px 6px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.82rem" title="Маркер">
      <option value="">—</option>
      <option value="🔴">🔴</option>
      <option value="🟢">🟢</option>
      <option value="🟧">🟧</option>
    </select>
    <button onclick="addInboxTask()" style="padding:6px 12px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.85rem">+</button>
  </div>
  <button class="undo-btn" onclick="post('/undo',null);setTimeout(function(){{location.reload()}},300)" title="Отменить последнее действие" style="padding:6px 10px;border-radius:6px;border:none;background:var(--bg2);color:var(--text3);cursor:pointer;font-size:.85rem;margin-left:4px">↩</button>
  <button class="theme-btn" onclick="toggleTheme()">🌙</button>
</nav>

{body}

<div id="task-modal" class="modal-overlay" onclick="if(event.target===this)closeTaskModal()">
  <div class="modal">
    <button class="modal-close" onclick="closeTaskModal()">✕</button>
    <div class="modal-title-area" id="modal-title-text"></div>
    <div id="modal-fields"></div>
    <div id="modal-subtasks-section">
      <div class="modal-subtasks-header">Подзадачи</div>
      <div id="modal-subtasks"></div>
    </div>
  </div>
</div>

<div class="ts">live</div>
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


CONTEXT_SECTIONS = [
    ("deep",      "Задачи"),
    ("perekur",   "Перекур / На улице"),
    ("afternoon", "2-я половина дня"),
]


def _render_scheduled_item(task):
    """Render a tasks.json task as a today-style list item."""
    task_id = task["id"]
    title = task.get("title", "")
    priority = task.get("priority")
    extra = {"red": " red", "green": " green", "orange": " orange"}.get(priority, "")
    deadline = task.get("deadline", "")
    dl_html = f' <span class="deadline{" overdue" if deadline and (date.fromisoformat(deadline) - date.today()).days < 0 else ""}" style="font-size:.72rem;color:var(--text4)">{deadline}</span>' if deadline else ""
    return (
        f'<li class="item todo{extra}" data-task-id="{task_id}">'
        f'<span class="task-chk" data-id="{task_id}" style="flex-shrink:0;width:15px;height:15px;border-radius:3px;background:var(--chk);display:inline-flex;align-items:center;justify-content:center;font-size:.65rem;color:var(--text5);cursor:pointer">·</span>'
        f'<span class="item-text task-linked" style="flex:1">{linkify(title)}</span>'
        f'{dl_html}'
        f'</li>\n'
    )


def render_today(path):
    title, sections, all_items = parse_today(path)
    tasks = load_tasks()
    task_by_norm = {normalize_title(t.get("title", "")): t["id"] for t in tasks if t.get("type") != "area"}
    today = today_str()

    # Tasks scheduled for today (scheduled_date == today OR deadline == today, not done)
    scheduled = [
        t for t in tasks
        if t.get("type") != "area"
        and t.get("status") != "done"
        and (t.get("scheduled_date") == today or t.get("deadline") == today)
    ]

    # Count total items: today.md checklist + scheduled tasks
    checklist_items = [i for sec, items in sections for i in items if sec == "Утренний чеклист"]
    total = len(checklist_items) + len(scheduled)
    done_checklist = sum(1 for i in checklist_items if i["done"])
    done_scheduled = sum(1 for t in tasks
                         if t.get("status") == "done" and t.get("scheduled_date") == today)
    done_n = done_checklist + done_scheduled
    pct = int(done_n / total * 100) if total else 0

    left = f"<h1>{title}</h1>\n"
    left += f'<div class="progress"><span class="pct">{done_n}/{total} — {pct}%</span><div class="bar"><div class="fill" style="width:{pct}%"></div></div></div>\n'

    # Первая задача — rendered first, above Утренний чеклист
    main_task_found = False
    for sec, items in sections:
        if sec != "Первая задача":
            continue
        main_task_found = True
        items_html = ""
        for item in items:
            done_cls = " done-item" if item["done"] else ""
            chk_icon = "✓" if item["done"] else "·"
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            task_id = task_by_norm.get(normalize_title(item["text"]), "")
            task_id_attr = f' data-task-id="{task_id}"' if task_id else ""
            link_cls = " task-linked" if task_id else ""
            items_html += (
                f'<li class="item{done_cls}{extra}" data-idx="{item["idx"]}"{task_id_attr} style="font-size:1.02rem;font-weight:600">'
                f'<span class="chk">{chk_icon}</span><span class="item-text{link_cls}">{linkify(item["text"])}</span>'
                f'<button class="btn del-today" data-idx="{item["idx"]}">×</button></li>\n'
            )
        left += (
            f'<h2 style="color:#5b8dd9;display:flex;align-items:center;gap:8px">Первая задача'
            f'<button class="btn" id="pick-main-task" style="font-size:.65rem;text-transform:none;letter-spacing:0">выбрать</button></h2>'
            f'<ul class="today-section">\n{items_html}</ul>\n'
        )
    if not main_task_found:
        left += (
            '<h2 style="color:#5b8dd9;display:flex;align-items:center;gap:8px">Первая задача'
            '<button class="btn" id="pick-main-task" style="font-size:.65rem;text-transform:none;letter-spacing:0">выбрать</button></h2>'
        )

    def section_is_future(sec):
        m = re.search(r'(\d{1,2})\.(\d{2})', sec)
        if not m:
            return False
        try:
            d = date(date.today().year, int(m.group(2)), int(m.group(1)))
            return d > date.today()
        except ValueError:
            return False

    # Render Утренний чеклист from today.md
    for sec, items in sections:
        if sec != "Утренний чеклист":
            continue
        todo = [i for i in items if not i["done"]]
        done_sec = [i for i in items if i["done"]]
        items_html = ""
        for item in todo:
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            task_id = task_by_norm.get(normalize_title(item["text"]), "")
            task_id_attr = f' data-task-id="{task_id}"' if task_id else ""
            link_cls = " task-linked" if task_id else ""
            items_html += f'<li class="item todo{extra}" data-idx="{item["idx"]}"{task_id_attr}><span class="chk">·</span><span class="item-text{link_cls}">{linkify(item["text"])}</span><button class="btn del-today" data-idx="{item["idx"]}">×</button></li>\n'
        for item in done_sec:
            items_html += f'<li class="item done-item" data-idx="{item["idx"]}"><span class="chk">✓</span><span>{linkify(item["text"])}</span></li>\n'
        sec_key = "Утренний_чеклист"
        left += f'<details data-key="today_{sec_key}"><summary style="font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text4);padding:4px 0;list-style:none;cursor:pointer">Утренний чеклист</summary><ul class="today-section">\n{items_html}</ul></details>\n'

    # Render task sections from tasks.json grouped by context
    for ctx_key, ctx_label in CONTEXT_SECTIONS:
        if ctx_key == "deep":
            ctx_tasks = [t for t in scheduled if t.get("context") in ("deep", None, "")]
        elif ctx_key == "perekur":
            ctx_tasks = [t for t in scheduled if t.get("context") in ("perekur", "phone", "email")]
        else:
            ctx_tasks = [t for t in scheduled if t.get("context") == ctx_key]
        if not ctx_tasks:
            continue
        items_html = "".join(_render_scheduled_item(t) for t in ctx_tasks)
        left += f'<h2>{ctx_label}</h2><ul class="today-section">\n{items_html}</ul>\n'

    # Render non-checklist, non-task sections from today.md (Завтра, Сегодня в календаре, etc.)
    task_section_names = {"Задачи", "Перекур / На улице", "2-я половина дня", "Утренний чеклист", "Первая задача", "Сделано"}
    for sec, items in sections:
        if section_is_future(sec):
            continue
        if sec in task_section_names:
            continue
        todo = [i for i in items if not i["done"]]
        if not todo:
            continue
        items_html = ""
        for item in todo:
            extra = " red" if "🔴" in item["text"] else (" green" if "🟢" in item["text"] else (" orange" if "🟧" in item["text"] else ""))
            task_id = task_by_norm.get(normalize_title(item["text"]), "")
            task_id_attr = f' data-task-id="{task_id}"' if task_id else ""
            link_cls = " task-linked" if task_id else ""
            items_html += f'<li class="item todo{extra}" data-idx="{item["idx"]}"{task_id_attr}><span class="chk">·</span><span class="item-text{link_cls}">{linkify(item["text"])}</span><button class="btn del-today" data-idx="{item["idx"]}">×</button></li>\n'
        left += f'<h2>{sec}</h2><ul class="today-section">\n{items_html}</ul>\n'

    # Done section from today.md
    done_all = [i for sec, items in sections for i in items if i["done"] and sec != "Утренний чеклист"]
    if done_all:
        left += "<h2>Сделано</h2><ul>\n"
        for item in done_all:
            left += f'<li class="item done-item" data-idx="{item["idx"]}"><span class="chk">✓</span><span>{linkify(item["text"])}</span></li>\n'
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


import html as _html
from urllib.parse import urlparse as _urlparse

_URL_RE = re.compile(r'(https?://\S+)')

def linkify(text):
    def replace(m):
        url = m.group(1).rstrip('.,)')
        parsed = _urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return _html.escape(url)
        safe_url = _html.escape(url, quote=True)
        safe_domain = _html.escape(parsed.hostname or '', quote=True)
        return f'<a href="{safe_url}" target="_blank" onclick="event.stopPropagation()" style="color:#5b8dd9;font-size:.75rem;margin-left:4px;text-decoration:none" title="{safe_url}">↗{safe_domain}</a>'
    return _URL_RE.sub(lambda m: replace(m), _html.escape(text))


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

    marker = task.get("marker", "")
    marker_label = marker if marker else "M"
    marker_style = ""
    if marker == "🔴":
        marker_style = " style=\"color:#e74c3c\""
    elif marker == "🟢":
        marker_style = " style=\"color:#2ecc71\""
    elif marker == "🟧":
        marker_style = " style=\"color:#f39c12\""

    recurring = task.get("recurring")
    recurring_badge = ""
    if recurring:
        badge_letter = {"weekly": "W", "monthly": "M", "quarterly": "Q", "yearly": "Y"}.get(recurring, "R")
        recurring_badge = f'<span style="font-size:.65rem;color:var(--text4);margin-left:4px">↻{badge_letter}</span>'
    r_label = recurring if recurring else "R"

    dl_val = deadline or ""
    parent_id = task.get("parent_id", "")
    parent_attr = f' data-parent-id="{_html.escape(parent_id, quote=True)}"' if parent_id else ""

    scheduled_date = task.get("scheduled_date", "")
    is_today = scheduled_date == today_str()
    today_active = " active" if is_today else ""
    today_label = "✕↗" if is_today else "↗"
    today_title = "Убрать из сегодня" if is_today else "Добавить в сегодня"

    ctx = task.get("context", "")
    ctx_labels = {"deep": "🧠", "perekur": "🚶", "afternoon": "🌆", "": "ctx"}
    ctx_label_btn = ctx_labels.get(ctx, "ctx")

    html = (
        f'<div class="task-row{indent_cls}{done_cls}{someday_cls}{prio_cls}" data-id="{task_id}"{parent_attr}>\n'
        f'  <span class="task-chk" data-id="{task_id}">{chk_icon}</span>\n'
        f'  <span class="task-text" data-id="{task_id}" data-raw="{_html.escape(title, quote=True)}">{linkify(title)}{recurring_badge}</span>\n'
        f'  {dl_html}\n'
        f'  <button class="btn today-btn{today_active}" data-id="{task_id}" data-scheduled="{scheduled_date}" title="{today_title}">{today_label}</button>\n'
        f'  <button class="btn ctx-btn" data-id="{task_id}" data-context="{ctx}" title="Контекст: {ctx or "нет"}">{ctx_label_btn}</button>\n'
        f'  <button class="btn type-btn" data-id="{task_id}" data-current="task">T</button>\n'
        f'  <button class="btn p-btn" data-id="{task_id}">P</button>\n'
        f'  <button class="btn d-btn" data-id="{task_id}" data-deadline="{dl_val}">D</button>\n'
        f'  <button class="btn s-btn{s_active}" data-id="{task_id}">{s_label}</button>\n'
        f'  <button class="btn m-btn" data-id="{task_id}"{marker_style}>{marker_label}</button>\n'
        f'  <button class="btn r-btn" data-id="{task_id}" data-recurring="{recurring or ""}">{r_label}</button>\n'
        f'  <button class="btn sub-btn" data-id="{task_id}" title="Добавить подзадачу">+</button>\n'
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
        [t for t in all_nodes if t.get("parent_id") == area_id and t.get("status") != "done"],
        key=lambda t: t.get("order", 0),
    )
    if not children:
        return (
            f'<div class="task-row" data-id="{area_id}">\n'
            f'  <span class="task-text">{title}'
            f'<span style="font-size:.7rem;color:var(--text4);margin-left:6px">area</span></span>\n'
            f'  <button class="btn sub-btn" data-id="{area_id}" title="Добавить задачу">+</button>\n'
            f'  <button class="btn del-btn" data-id="{area_id}">×</button>\n'
            f'</div>\n'
        )
    b = f'<details data-key="{area_id}" data-id="{area_id}"><summary><span class="area-title" data-id="{area_id}">{title}</span><button class="btn type-btn" data-id="{area_id}" data-current="area" onclick="event.stopPropagation()">A</button><button class="btn sub-btn" data-id="{area_id}" title="Добавить задачу" onclick="event.stopPropagation()">+</button></summary>\n'
    b += '<div class="section-tasks">\n'
    for child in children:
        if child.get("type") == "area":
            b += render_area(child, all_nodes)
        else:
            b += render_task_row(child, all_nodes)
    b += "</div>\n</details>\n"
    return b


def build_area_options(nodes, all_nodes, prefix=""):
    opts = []
    for a in sorted(nodes, key=lambda t: t.get("order", 0)):
        path = prefix + a.get("title", "")
        opts.append({"id": a["id"], "title": path})
        sub = [t for t in all_nodes if t.get("parent_id") == a["id"]]
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
    someday_count = sum(1 for t in active if t.get("someday") and t.get("type") != "area")
    sd_limit = 20
    today_iso = date.today().isoformat()
    overdue_count = sum(
        1 for t in active
        if t.get("type") != "area" and t.get("deadline") and t["deadline"] not in ("-", "None")
        and t["deadline"] <= today_iso
    )
    sd_warn_style = ";color:#e74c3c;font-weight:600" if someday_count > sd_limit else ""
    overdue_warn_style = ";color:#e74c3c;font-weight:600" if overdue_count > 0 else ""
    b = (f"<h1>Задачи</h1>\n<script>window.AREAS={areas_json};window.SOMEDAY_LIMIT={sd_limit};</script>\n"
         f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:12px">'
         f'<input id="task-search" type="text" placeholder="Поиск по задачам..." style="flex:1;max-width:500px;padding:8px 12px;border-radius:6px;border:none;background:var(--bg2);color:var(--text);font-size:.88rem;outline:1px solid var(--bdr)">'
         f'<button id="someday-filter" class="btn" style="padding:6px 12px;font-size:.82rem;border-radius:6px;flex-shrink:0" data-count="{someday_count}">Someday</button>'
         f'<button id="overdue-filter" class="btn" style="padding:6px 12px;font-size:.82rem;border-radius:6px;flex-shrink:0{overdue_warn_style}" data-count="{overdue_count}">Просрочено ({overdue_count})</button>'
         f'</div>\n'
         f"<div id=\"top-areas\">\n")
    for area in top_areas:
        b += render_area(area, active)
    b += "</div>\n"
    return b


def toggle_task(task_id):
    tasks = load_tasks()
    title = ""
    done = False
    cloned = None
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
                recurring = t.get("recurring")
                if recurring:
                    import time as _time
                    base_id = task_id + "-next"
                    existing_ids = {x["id"] for x in tasks}
                    new_id = base_id if base_id not in existing_ids else f"{base_id}-{int(_time.time()) % 100000}"
                    skip_keys = {"id", "status", "done_at"}
                    cloned = {k: v for k, v in t.items() if k not in skip_keys}
                    cloned["id"] = new_id
                    cloned["status"] = "todo"
                    dl = next_deadline(recurring)
                    if dl:
                        cloned["deadline"] = dl
            title = t.get("title", "")
            break
    if cloned:
        tasks.append(cloned)
    save_tasks(tasks)
    if title:
        sync_tasks_to_today(title, done)


SOMEDAY_LIMIT = 20

def toggle_someday(task_id):
    tasks = load_tasks()
    result = {"warning": None, "blocked": False}
    for t in tasks:
        if t["id"] == task_id:
            enabling = not t.get("someday", False)
            if enabling:
                count = sum(1 for x in tasks if x.get("someday") and x.get("status") != "done" and x.get("type") != "area")
                if count >= SOMEDAY_LIMIT:
                    result["blocked"] = True
                    result["warning"] = f"Лимит someday достигнут: {count}/{SOMEDAY_LIMIT}. Снимите someday с другой задачи."
                    return result
            t["someday"] = not t.get("someday", False)
            break
    save_tasks(tasks)
    return result


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
    if new_type == "area":
        target_title = next((t.get("title", "").strip().lower() for t in tasks if t["id"] == task_id), None)
        duplicate = any(
            t["id"] != task_id and t.get("type") == "area"
            and t.get("title", "").strip().lower() == target_title
            for t in tasks
        )
        if duplicate:
            return False
    for t in tasks:
        if t["id"] == task_id:
            t["type"] = new_type
            break
    save_tasks(tasks)
    return True


def next_deadline(recurring):
    today = date.today()
    if recurring == "weekly":
        return (today + timedelta(days=7)).isoformat()
    elif recurring == "monthly":
        m = today.month + 1
        y = today.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        import calendar
        d = min(today.day, calendar.monthrange(y, m)[1])
        return date(y, m, d).isoformat()
    elif recurring == "quarterly":
        m = today.month + 3
        y = today.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        import calendar
        d = min(today.day, calendar.monthrange(y, m)[1])
        return date(y, m, d).isoformat()
    elif recurring == "yearly":
        import calendar
        y = today.year + 1
        d = min(today.day, calendar.monthrange(y, today.month)[1])
        return date(y, today.month, d).isoformat()
    return None


def set_task_marker(task_id):
    tasks = load_tasks()
    cycle = ["", "🔴", "🟢", "🟧"]
    priority_map = {"🔴": "red", "🟢": "green", "🟧": "orange", "": None}
    for t in tasks:
        if t["id"] == task_id:
            cur = t.get("marker", "")
            idx = cycle.index(cur) if cur in cycle else 0
            nxt = cycle[(idx + 1) % len(cycle)]
            t["marker"] = nxt
            t["priority"] = priority_map[nxt]
            break
    save_tasks(tasks)


def set_task_recurring(task_id, recurring):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if recurring:
                t["recurring"] = recurring
            else:
                t.pop("recurring", None)
            break
    save_tasks(tasks)


def set_task_scheduled_date(task_id, scheduled_date):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if scheduled_date:
                t["scheduled_date"] = scheduled_date
            else:
                t.pop("scheduled_date", None)
            break
    save_tasks(tasks)


def set_task_context(task_id, context):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if context:
                t["context"] = context
            else:
                t.pop("context", None)
            break
    save_tasks(tasks)


def rename_task(task_id, new_text):
    tasks = load_tasks()
    target = next((t for t in tasks if t["id"] == task_id), None)
    if target and target.get("type") == "area":
        duplicate = any(
            t["id"] != task_id and t.get("type") == "area"
            and t.get("title", "").strip().lower() == new_text.strip().lower()
            for t in tasks
        )
        if duplicate:
            return False
    for t in tasks:
        if t["id"] == task_id:
            t["title"] = new_text
            break
    save_tasks(tasks)
    return True


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


def get_top_priority(n=5):
    data = _priority.load_tasks()
    task_map = _priority.build_task_map(data)
    today = date.today()
    candidates = [
        t for t in data
        if isinstance(t, dict) and t.get("type") != "area"
        and t.get("status") != "done" and t.get("someday")
        and t.get("priority") == "green"
    ]
    scored = []
    for t in candidates:
        p, *_ = _priority.score_task(t, task_map, today)
        scored.append((p, t))
    scored.sort(key=lambda x: -x[0])
    return [{"id": t["id"], "title": t.get("title", ""), "score": p} for p, t in scored[:n]]


def set_main_task(title):
    lines = TODAY.read_text(encoding="utf-8").splitlines()
    out = []
    i = 0
    found = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if line.strip() == "## Первая задача":
            found = True
            i += 1
            # skip existing content of this section until next "## " heading
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            out.append("")
            out.append(f"- [ ] {title}")
            out.append("")
            continue
        i += 1
    if not found:
        # insert right after the "# " title line
        new_out = []
        inserted = False
        for line in out:
            new_out.append(line)
            if line.startswith("# ") and not inserted:
                new_out.append("")
                new_out.append("## Первая задача")
                new_out.append("")
                new_out.append(f"- [ ] {title}")
                inserted = True
        out = new_out
    TODAY.write_text("\n".join(out) + "\n", encoding="utf-8")


def add_task_inbox(title, context=None, marker=None, parent_id=None):
    tasks = load_tasks()
    if not any(t["id"] == "area-inbox" for t in tasks):
        tasks.insert(0, {"id": "area-inbox", "title": "Inbox", "type": "area", "order": -1})
    if parent_id and not any(t["id"] == parent_id for t in tasks):
        parent_id = None
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)[:50]
    task_id = f"inbox-{slug}"
    existing_ids = {t["id"] for t in tasks}
    if task_id in existing_ids:
        import time
        task_id = f"inbox-{slug}-{int(time.time()) % 10000}"
    priority_map = {"🔴": "red", "🟢": "green", "🟧": "orange"}
    task = {
        "id": task_id,
        "title": title,
        "parent_id": parent_id or "area-inbox",
        "status": "todo",
        "someday": True,
        "created_at": today_str()
    }
    if context:
        task["context"] = context
    if marker:
        task["marker"] = marker
        task["priority"] = priority_map.get(marker)
    tasks.append(task)
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
        by_date.setdefault(ev.get("date", ev.get("start", "")[:10]), []).append(ev)

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
            def _fmt_time(s):
                if not s:
                    return ""
                try:
                    return datetime.fromisoformat(s).strftime("%H:%M")
                except Exception:
                    return s[11:16] if len(s) > 15 else s
            time_str = _fmt_time(ev.get("start", ""))
            end_str = _fmt_time(ev.get("end", ""))
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

def render_sessions():
    records = []
    if SESSION_LOG.exists():
        seen = set()
        for line in SESSION_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = r.get("session_id", "")
            if sid and sid in seen:
                continue
            if sid:
                seen.add(sid)
            records.append(r)

    records.sort(key=lambda r: r.get("started_at") or r.get("date") or "", reverse=True)

    by_date = {}
    for r in records:
        day = (r.get("started_at") or r.get("date") or "")[:10]
        by_date.setdefault(day, []).append(r)

    if not records:
        return "<h1>Сессии</h1><p style='color:var(--text4);margin-top:24px'>Нет записей в session-log.jsonl</p>"

    html = "<h1>Сессии</h1>\n"
    for day in sorted(by_date.keys(), reverse=True):
        day_recs = by_date[day]
        html += f'<div class="sess-day">\n<div class="sess-day-header">{day}</div>\n'
        for r in day_recs:
            title = _html.escape(r.get("title") or r.get("first_msg") or "—")
            dur = r.get("duration_min", 0)
            turns = r.get("turns", 0)
            cwd = r.get("cwd", "")
            proj = cwd.split("/")[-1] if cwd else ""
            files = r.get("files_modified", [])
            file_names = [f.split("/")[-1] for f in files[:5]]
            files_html = ""
            if file_names:
                files_html = f'<div class="sess-files">{_html.escape(", ".join(file_names))}</div>'
            proj_tag = f'<span class="sess-tag">{_html.escape(proj)}</span>' if proj else ""
            html += (
                f'<div class="sess-card">'
                f'<div><div class="sess-title">{proj_tag}{title}</div>{files_html}</div>'
                f'<div class="sess-meta">{dur}мин · {turns}↔</div>'
                f'</div>\n'
            )
        html += "</div>\n"
    return html


_PAGE_TITLES = {"today": "Сегодня", "tasks": "Задачи", "sessions": "Сессии"}

def make_page(body, page):
    return HTML.format(
        title=_PAGE_TITLES.get(page, "Brain"),
        refresh='<script>(function(){var h=null;function poll(){fetch("/poll").then(function(r){return r.json()}).then(function(d){if(h===null){h=d.hash}else if(d.hash!==h){var a=document.activeElement,tag=a?a.tagName:"";if(!window.isDragging&&tag!=="INPUT"&&tag!=="SELECT"&&tag!=="TEXTAREA"&&!a.isContentEditable)location.reload()}}).catch(function(){});setTimeout(poll,2000)}poll()})()</script>',
        css=CSS, js=JS, body=body,
        sortable_js=_SORTABLE_JS,
        nav_today="active" if page == "today" else "",
        nav_tasks="active" if page == "tasks" else "",
        nav_sessions="active" if page == "sessions" else "",
    ).encode("utf-8")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/poll":
            import hashlib
            mtimes = ""
            for f in [TODAY, TASKS_FILE, CALENDAR_CACHE]:
                try:
                    mtimes += str(f.stat().st_mtime)
                except Exception:
                    pass
            h = hashlib.md5(mtimes.encode()).hexdigest()[:12]
            data = json.dumps({"hash": h}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(data))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
            return
        elif self.path == "/":
            body = render_today(TODAY)
            data = make_page(body, "today")
        elif self.path == "/tasks":
            body = render_tasks()
            data = make_page(body, "tasks")
        elif self.path == "/sessions":
            body = render_sessions()
            data = make_page(body, "sessions")
        elif self.path == "/api/top-priority":
            data = json.dumps(get_top_priority(5), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
            return
        elif self.path.startswith("/api/task"):
            from urllib.parse import urlparse as _up, parse_qs as _pqs
            qs = _pqs(_up(self.path).query)
            task_id = qs.get("id", [None])[0]
            tasks = load_tasks()
            task = next((t for t in tasks if t["id"] == task_id), None)
            if not task:
                self.send_error(404)
                return
            subtasks = [t for t in tasks if t.get("parent_id") == task_id]
            parent = next((t for t in tasks if t["id"] == task.get("parent_id")), None)
            result = dict(task)
            result["parent_title"] = parent["title"] if parent else None
            result["subtasks"] = [
                {"id": s["id"], "title": s["title"], "done": s.get("status") == "done"}
                for s in subtasks
            ]
            data = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(data))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
            return
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
            result = toggle_someday(d["id"])
            if result.get("blocked") or result.get("warning"):
                resp = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", len(resp))
                self.end_headers()
                self.wfile.write(resp)
                return
        elif self.path == "/delete":
            delete_task(d["id"])
        elif self.path == "/done-event":
            add_done_event(d["summary"], d.get("date"))
        elif self.path == "/rename":
            ok = rename_task(d["id"], d["text"])
            if ok is False:
                err = json.dumps({"error": "Area с таким именем уже существует"}).encode("utf-8")
                self.send_response(409)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", len(err))
                self.end_headers()
                self.wfile.write(err)
                return
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
            add_task_inbox(d["title"], d.get("context"), d.get("marker"), d.get("parent_id"))
        elif self.path == "/set-main-task":
            set_main_task(d["title"])
        elif self.path == "/move":
            move_task(d["src_id"], d["target_id"], d["position"])
        elif self.path == "/set-marker":
            set_task_marker(d["id"])
        elif self.path == "/undo":
            undo_tasks()
        elif self.path == "/move-order":
            move_task_order(d["id"], d["direction"])
        elif self.path == "/set-recurring":
            set_task_recurring(d["id"], d.get("recurring") or None)
        elif self.path == "/set-scheduled-date":
            set_task_scheduled_date(d["id"], d.get("scheduled_date") or None)
        elif self.path == "/set-context":
            set_task_context(d["id"], d.get("context") or None)
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
