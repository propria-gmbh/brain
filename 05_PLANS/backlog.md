---
title: Backlog — не приоритизировано, на потом
date: 2026-05-11
type: backlog
status: active
tags: [operations, procrastination, customer-support, cursor, tooling]
---

# Backlog

Задачи и заметки **вне** текущего фокуского А/B. Не тянут на ADR. Периодически перебрасывать в Singularity / weekly review.

## Операционка и прокрастинация

- [ ] **Customer support (Gorgias / драфты)** — работа с саппортом **постоянно вызывает прокрастинацию**, потому что там надо **возвращать деньги** (рефанды и контекст вокруг них).  
  - **Контекст:** `08_PROJECTS/customer_support/AGENTS.md`  
  - **Идея на потом:** выделенный таймбокс «support slot» (например 2×30 мин в день), отдельно от стратегии; заранее правило «сначала классификация, потом эмоция»; при необходимости — паттерн в `04_THINKING/patterns/`.

## Cursor / единые правила с brain

- [ ] **Распространить symlink `brain/.cursor/rules` на другие репозитории** — по тому же принципу, что для `~/Projects/invertomatic/.cursor/rules → ~/Projects/brain/.cursor/rules`: открываешь только папку проекта, но подхватываются те же `.mdc`, правка в одном месте (`brain/.cursor/rules/`).  
  - **Уже сделано:** `invertomatic` (см. `08_PROJECTS/invertomatic/AGENTS.md` §Cursor).  
  - **Кандидаты:** `customer_support`, `personal-agent`, `vaition`, `listing_automation`, `product_search`, любой проект из `08_PROJECTS/_index.md` с реальным `code-path`.  
  - **Шаги:** `mkdir -p <repo>/.cursor && ln -sfn /Users/dister/Projects/brain/.cursor/rules <repo>/.cursor/rules` → Reload Window → в `08_PROJECTS/<slug>/AGENTS.md` кратко описать (как у invertomatic).  
  - **Осторожно:** если в репо уже есть свой `.cursor/rules/`, не затереть — слить или symlink на уровне отдельных файлов.
