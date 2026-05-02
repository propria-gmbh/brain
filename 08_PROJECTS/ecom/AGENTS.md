---
title: ecom — brain reference (umbrella)
date: 2026-05-02
type: project-reference
status: active
tags: [ecom, shopify, multi-store]
slug: ecom
---

# ecom

## Что это

Зонтичный подпроект для всего e-commerce. Под ним — магазины по брендам/странам, а также сквозные темы (GMC, платежи, реклама).

## Бренды и магазины

| Бренд | Страны | Магазин | Папка |
|---|---|---|---|
| Marc & François | CH, DE | ch-marcfrancois | [stores/ch-marcfrancois](stores/ch-marcfrancois/) |
| Oliver and Alder | UK | uk-oliverandalder | [stores/uk-oliverandalder](stores/uk-oliverandalder/) |
| _(TBD)_ | US | us-new | [stores/us-new](stores/us-new/) |

## Сквозные темы

- [gmc/](gmc/) — Google Merchant Center (аккаунты, фиды, ревью, appeal)
- [payments/](payments/) — платёжные системы (Stripe, TWINT, локальные)
- _(позже)_ ads/, inventory/

## Платформа

Shopify (rollout 3-5 магазинов). AI-assisted customer support = отдельный tool-проект `customer_support/`, обслуживает эти магазины.

## Где искать больше

- [stores/_index.md](stores/_index.md) — статус всех магазинов
- `08_PROJECTS/customer_support/AGENTS.md` — AI-инструмент поверх ecom
