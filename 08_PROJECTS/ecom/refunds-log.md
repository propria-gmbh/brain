---
title: Refunds log (ecom)
date: 2026-05-04
type: ledger
status: active
tags: [ecom, refunds, finance, shopify]
---

# Refunds log

Журнал **внешних** возвратов денег клиентам (partial / full). **Кто** — через **номер заказа** в Shopify (`#…`); ФИО и email сюда не дублируем. Сумма и факт возврата сверяются с **Shopify** и выпиской PSP.

## Конвенции колонок

| Колонка | Значение |
|---|---|
| Дата | дата фактического возврата (ISO `YYYY-MM-DD`) |
| Магазин | slug или бренд, например marc-francois |
| Store id | routing id витрины, напр. `qff1md-0e` |
| Заказ | `#1015` — единственный идентификатор клиента в этой таблице |
| Валюта | ISO 4217 |
| Сумма | число, точка как десятичный разделитель |
| Причина | delay, damage, withdrawal, goodwill, dup, другой код |
| Канал | Shopify refund, Stripe reversal, др. |
| Ref / txn | id транзакции в PSP или примечание из Shopify |
| Проверено | дата сверки с банком/Stripe |

## Стоимость несвоевременной обработки тикетов

| Период | Сумма | Валюта | Примечание |
|--------|-------|--------|------------|
| 2026-05 | 63.95 | CHF | #1013 withdrawal |
| 2026-05 | 54.95 | CHF | #1009 withdrawal |
| 2026-05 | 127.50 | CHF | CH Store delay |
| 2026-05 | 85.90 | GBP | UK Store delay |

## Таблица

| Дата | Магазин | Store id | Заказ | Валюта | Сумма | Причина | Канал | Ref / txn | Проверено |
|------|---------|----------|-------|--------|-------|---------|-------|-----------|-----------|
| 2026-05-11 | CH Store | qff1md-0e | #1013 | CHF | 63.95 | withdrawal (client wants refund) | Shopify | — | |
| 2026-05-11 | CH Store | qff1md-0e | #1009 | CHF | 54.95 | withdrawal (client wants refund) | Shopify | — | |
| 2026-05-04 | UK Store | — | #STID20261010-UK | GBP | 85.90 | delay (supplier not shipped) | Gorgias/Shopify | — | |
| 2026-05-05 | CH Store | — | — | CHF | 127.50 | delay (no supplier response) | Shopify | — | |

<!-- Добавляйте строки сверху под заголовком (новые сверху) или снизу — выберите один стиль и держитесь его. -->
