---
title: vaition — brain reference
date: 2026-05-02
type: project-reference
status: active
tags: [protocol, research, licensing, layer0]
slug: vaition
code-path: ~/Projects/vaition/
---

# vaition (VAYDY Layer 0)

## Что это

Теория и спецификация **Layer 0 протокола**: уровень ниже идентификации и аутентификации, который спрашивает не только «кто ты?», а сначала **«ты жив прямо сейчас?»**.

Цели:
- Определить **canonical theory core** (Layer 0, biostream, living session, Split-Streams, ReplaySafe(D))
- Специфицировать, как wearables становятся VAYDY Certified и дают presence proofs без утечки raw biodata
- Описать replay-safety semantics через acceptance domains `D` и federated registries
- Держать чёткий **claims boundary** чтобы публичные материалы не переоценивали теорию
- Дать empirical и deployment checklists для пилотов и измеримых развёртываний

## Текущая стратегия

**Infrastructure licensing-first.** Layer 0 как licensable substrate. End-продукты — от licensees/integrators; in-house device design открывается fallback-ом, если licensee не укладываются в сроки. См. `06_DECISIONS/decision-log.md` §6 и `05_PLANS/backlog.md` в репо.

## Где код / артефакты

`~/Projects/vaition/`

## Структура (cognitive pipeline — прототип для brain/)

```
00_META/      — project state, reading maps
01_RULES/     — claims-boundaries, promotion rules, cursor config
02_CONTEXT/   — glossary, narrative, presentations, briefs
03_RESEARCH/  — theory core, empirics, extensions (EN+RU)
04_THINKING/  — philosophical questions, hypotheses, working resolutions
05_PLANS/     — roadmap, backlog, weekly-review template, release-readiness
06_DECISIONS/ — decision-log, equity, IP-closure, outreach, meetings
07_OUTPUT/    — CTO/Investor/Legal briefs & one-pagers (EN+RU)
99_ARCHIVE/   — old cursor config
```

## Ключевые файлы

- `00_META/project.md` — актуальное описание
- `01_RULES/claims-and-boundaries-en.md` — границы высказываний
- `03_RESEARCH/VAYDY_Device_Agnostic_Framework_EN.md`
- `05_PLANS/strategy-roadmap-6-12-36-months_RU.md`
- `06_DECISIONS/decision-log.md`

## Текущая цель

Довести licensing-first трек до первого контакта с потенциальным licensee. Держать public materials в границах claims.

## Где искать больше

- [goals.md](goals.md)
- [open-questions.md](open-questions.md)
