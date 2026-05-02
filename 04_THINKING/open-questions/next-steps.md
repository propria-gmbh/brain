---
title: Next steps for brain/ setup
date: 2026-05-02
type: open-questions
tags: [setup, infrastructure]
---

# Next steps

Шаг 1 (фундамент) — **готов**. Что дальше:

## Шаг 2 — Когнитивные скиллы Cursor (приоритет)

Создать в `~/.cursor/skills-cursor/`:

- [ ] `expert-panel/SKILL.md` — запускает N subagents через Task tool параллельно, синтезирует расхождения
- [ ] `loop-interview/SKILL.md` — AskQuestion пачкой, итеративное уточнение интента
- [ ] `adversarial-review/SKILL.md` — critic-pass перед важным решением
- [ ] `socratic/SKILL.md` — разбор через сократовские вопросы
- [ ] `brain-capture/SKILL.md` — извлечение ADR/session/pattern из разговора + commit

## Шаг 3 — Инфраструктура хранения

- [ ] Создать private GitHub repo `brain`
- [ ] Добавить remote, push
- [ ] Установить Obsidian (https://obsidian.md) → Open folder as vault → `~/Projects/brain/`
- [ ] Установить плагины: **Obsidian Git** (auto-commit + push), **Templater** (шаблоны из `_templates/`), **Dataview** (запросы по frontmatter), **Daily Notes** (core plugin)
- [ ] Настроить Daily Notes folder: `04_THINKING/daily/`, формат `YYYY-MM-DD`, template — `_templates/daily.md`
- [ ] Settings → Files → `Detect all file extensions` (чтобы видеть .mdc файлы)

## Шаг 4 — Mobile + Voice

- [ ] Obsidian Mobile на iPhone (тот же vault через iCloud Drive или git)
- [ ] Working Copy для git sync на iOS
- [ ] SuperWhisper (macOS, локальный Whisper) ИЛИ Obsidian Whisper плагин
- [ ] Test: мысль с телефона голосом → daily note → git commit → pull на desktop

## Шаг 5 — SingularityApp research

- [ ] Найти документацию REST API SingularityApp
- [ ] Получить API key
- [ ] Решить: pull-only (SA → brain/05_PLANS/tasks/) или two-way
- [ ] Написать `tools/sync_singularity.py`
- [ ] launchd job на запуск раз в час

## Шаг 6 — Google Calendar → meetings

- [ ] Google OAuth credentials для чтения календаря
- [ ] `tools/sync_calendar.py`: события → `06_DECISIONS/meetings/YYYY-MM-DD-<slug>.md` (stub из шаблона)
- [ ] launchd job: раз в утро

## Шаг 7 — Ритуалы и ритм

- [ ] Daily ritual (5-10 мин утром): открыть Daily Note, пробежать open-questions, глянуть _index
- [ ] Weekly review (пятница или воскресенье, 30 мин): `_templates/weekly-review.md` — создать
- [ ] Monthly review (1 час): пересмотреть active ADRs с review trigger, обновить roadmaps
