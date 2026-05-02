# brain — командный центр

## Что это

Экзоскелет мышления + архив решений + командный центр над проектами.

**Разработка кода — НЕ здесь.** Код живёт в отдельных репозиториях (Claude Code). В `brain/` — планирование, стратегия, решения, журнал, паттерны, реестр проектов, задачи, встречи.

## Когнитивный pipeline (папки)

```
00_META       → описание brain/, reading map, текущее состояние
01_RULES      → правила, политики, настройки Cursor/Obsidian
02_CONTEXT    → глоссарий, онтология, ментальные модели
03_RESEARCH   → внешние источники, данные, материалы
04_THINKING   → сессии, дневные заметки, паттерны, открытые вопросы
05_PLANS      → цели, roadmap, mirror задач из SingularityApp
06_DECISIONS  → ADR-лог, записи встреч
07_OUTPUT     → готовые артефакты (эссе, брифы, синтезы)
08_PROJECTS   → реестр внешних Claude Code проектов
99_ARCHIVE    → устаревшее
_templates    → шаблоны для типовых документов
tools         → скрипты синхронизации (SingularityApp, Google Calendar)
```

Структура — адаптация из проекта `vaition`.

## Правила

- Глобальные (стиль, безопасность, когнитивные протоколы): `~/.cursor/rules/`
- Специфичные для brain/: `.cursor/rules/`

Ключевые:
- `~/.cursor/rules/02-thinking-protocols.mdc` — когда expert panel / adversarial review / loop interview
- `~/.cursor/rules/03-knowledge-capture.mdc` — что фиксировать в brain/
- `~/.cursor/rules/04-session-close.mdc` — обязательная сводка в конце сессии
- `.cursor/rules/02-adr-discipline.mdc` — ADR-дисциплина

## Reading order для новой сессии

1. `00_META/project.md` — что происходит прямо сейчас
2. `00_META/reading-map.md` — что читать по теме
3. `08_PROJECTS/_index.md` — статус всех проектов
4. `04_THINKING/open-questions/` — что ждёт решения
5. `06_DECISIONS/adr/` — последние решения (отсортированы по дате)

## Типичные операции

| Ситуация | Действие |
|---|---|
| Нужно принять решение | Expert panel → adversarial review → ADR в `06_DECISIONS/adr/` |
| Размытая идея | Loop interview (AskQuestion пачкой) |
| Встреча прошла | Запись в `06_DECISIONS/meetings/YYYY-MM-DD-<тема>.md` из шаблона |
| Мысль в дороге | `04_THINKING/daily/YYYY-MM-DD.md` (Obsidian Daily Note) |
| Паттерн повторяется | `04_THINKING/patterns/<slug>.md` |
| Работа с внешним проектом | Идёшь в `08_PROJECTS/<slug>/`, смотришь `AGENTS.md`, переходишь в реальный репо |

## Синхронизация (планируется)

- Obsidian Git plugin → auto-commit + push в private GitHub
- `tools/sync_singularity.py` → SingularityApp → `05_PLANS/tasks/`
- `tools/sync_calendar.py` → Google Calendar → `06_DECISIONS/meetings/`
- launchd → `tools/` запускаются по расписанию

## Mobile

- Obsidian Mobile (iOS/Android) — открывает этот же vault
- Working Copy (iOS) — git sync на телефоне
- Voice → Obsidian → transcription (плагин) → `04_THINKING/daily/<today>.md`
