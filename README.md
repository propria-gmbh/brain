# brain

Командный центр над проектами. Планирование, решения, контроль выполнения, синтез паттернов.

Разработка проектов — в отдельных репозиториях (Claude Code). Сюда попадают: стратегия, ADR, журнал, шаблоны мышления, статус проектов, задачи, встречи.

## Точка входа

См. [`00_META/project.md`](00_META/project.md) и [`AGENTS.md`](AGENTS.md).

## Когнитивный pipeline

```
00_META       → что это, как устроено, текущее состояние
01_RULES      → границы, политики, настройки инструментов
02_CONTEXT    → глоссарий, онтология, ментальные модели
03_RESEARCH   → внешние источники, факты, данные
04_THINKING   → журнал, сессии мышления, гипотезы, открытые вопросы
05_PLANS      → цели, roadmap, задачи (mirror SingularityApp)
06_DECISIONS  → ADR-лог, записи встреч
07_OUTPUT     → готовые артефакты (эссе, брифы, синтезы)
08_PROJECTS   → реестр внешних Claude Code проектов
99_ARCHIVE    → устаревшее
```

Структура вдохновлена проектом `vaition`.

## Стек

- **Формат**: plain markdown + YAML frontmatter
- **Хранение**: git (private GitHub)
- **Редакторы**: Cursor (desktop), Obsidian (desktop + mobile)
- **Синхронизация**: git (Obsidian Git plugin), SingularityApp → `05_PLANS/tasks/`, Google Calendar → `06_DECISIONS/meetings/`
