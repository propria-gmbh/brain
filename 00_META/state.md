---
title: Current state
date: 2026-05-02
type: meta
status: active
---

# Текущее состояние brain/

## Фаза

**Setup.** Только что создан скелет. Экзоскелет мышления ещё не собран (нужны скиллы expert-panel, adversarial-review, loop-interview, brain-capture). Синхронизация SingularityApp / Calendar не настроена.

## Что работает

- [x] Структура папок по vaition-паттерну
- [x] Глобальные правила Cursor (`~/.cursor/rules/`)
- [x] Проектные правила (`brain/.cursor/rules/`)
- [x] Шаблоны документов (`_templates/`)
- [x] Реестр проектов (5 начальных референсов)
- [x] Первый ADR — архитектура brain
- [x] Git repo локально

## Что НЕ работает / не настроено

- [ ] Obsidian не установлен / vault не открыт
- [ ] GitHub private remote не создан
- [ ] Obsidian Git plugin не настроен (auto-commit + push)
- [ ] Voice capture (SuperWhisper или Obsidian Whisper)
- [ ] SingularityApp sync (нужно research — REST API, API key, формат)
- [ ] Google Calendar sync (нужен OAuth flow)
- [ ] Скиллы: expert-panel, adversarial-review, loop-interview, brain-capture, pattern-detector, project-status
- [ ] launchd jobs для tools/

## Главная цель

**Преодоление прокрастинации и правильная приоритизация.** Инфраструктура brain/ — средство, а не цель. См. [ADR 2026-05-02-prioritization-policy](../06_DECISIONS/adr/2026-05-02-prioritization-policy.md).

## Следующий шаг

**Не продолжать строить brain/.** Текущий блокирующий контекст — GMC:
- Проанализировать имеющиеся ресурсы в `~/Projects/GMC/`
- Довести до решения вопрос с магазином (oliverandalder / новый)
- Зарегистрировать новый магазин

Возврат к «Шаг 2: скиллы мышления» — только после того, как GMC-блок разрешён. См. `04_THINKING/open-questions/next-steps.md`.
