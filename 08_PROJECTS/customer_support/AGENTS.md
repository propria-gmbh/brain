---
title: customer_support — brain reference
date: 2026-05-02
type: project-reference
status: draft-only-production
tags: [ecom, support, shopify, gorgias, claude-code]
slug: customer_support
code-path: ~/Projects/customer_support/
---

# customer_support

## Что это

AI-assisted customer-support reply drafting для мульти-стор e-commerce.
**Helpdesk:** Gorgias. **Platform:** Shopify.
**Stores:** Marc & François (CH/DE), Oliver and Alder (UK/EN). Рассчитан на 3-5 магазинов.

## Режим работы

**Draft-only.** Человек вставляет сообщение клиента, агент пишет черновик, человек проверяет и вставляет в Gorgias. Auto-send не включён. Layers 18-20 (tiered/auto-send) написаны, но не активны.

## Где код

`~/Projects/customer_support/`

## Ключевые файлы

- `CLAUDE.md` — главная точка входа для Claude Code
- `__support_setup/README.md` — индекс слоёв + Session Zero checklist
- `__support_setup/funnels/return-resolution.md` — канонический return funnel (Path C)
- `__support_setup/reference/COMPLIANCE_AUDIT.md` — GMC + statutory-rights риски
- `__support_setup/04_HOOKS.md` — H1-H20 hard-block list

## Subagent roster (в проекте)

| Agent | Stage | Model | Role |
|---|---|---|---|
| `flow-designer` | Plan | opus | Sole writer в `funnels/` |
| `reply-drafter` | Draft | sonnet | Composes draft replies |
| `kb-explorer` | Support | haiku | Read-only KB search |
| `qa-reviewer` | Verify | opus | Compliance + tone + GMC check |
| `store-marcfrancois` | Build | sonnet | CH/DE: German, CHF, Swiss law |
| `store-oliverandalder` | Build | sonnet | UK/EN: English, GBP, UK CCRs |

## Текущая цель

Поддерживать draft-only режим стабильно. Подготовить базу для graduate to tiered auto-send (Layers 18-20).

## Стек

- Claude Code с собственным claude-setup
- Shopify + Gorgias (внешние системы — не в репо)
- KB как markdown в `__support_setup/kb/`

## Compliance constraints

- UK CCRs 2013, EU CRD 2011/83, Swiss consumer law = floor
- GMC Annex I + UK/EU UCPD #7 и #19 hard-blocked
- PII sanitization на KB-write

## Где искать больше

- [goals.md](goals.md)
- [open-questions.md](open-questions.md)
