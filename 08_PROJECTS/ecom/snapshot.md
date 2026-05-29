---
updated: 2026-05-29
---

# Ecom — контекст

## Активные магазины

| Бренд | Домен | Рынок | GMC статус | Аккаунт GMC |
|---|---|---|---|---|
| Marc et Francois | marcfrancois.ch | CH | ✅ Approved | 3553194@gmail.com |
| Oliver and Alder | oliverandalder.com | UK | Suspended — no more appeals | ? |
| Charlie & Ted | charlieandted.com | US | GMC удалён → ⏳ создать новый | ? |
| Bennet & Gray | bennetandgray.com | ? | ⏳ планируется | bennetandgray.com@gmail.com |
| Oliver and Faye | oliverandfaye.com | ? | ⏳ планируется | ? |
| Casa Giannini | casa-giannini.it | IT | ⏳ планируется | ? |

Закрывается: Havgaard Kobenhavn (havgaard-kobenhavn.dk) — магазин закрывается, верификация не нужна.

## Текущие блокеры

1. **Oliver and Alder** — ScamAdviser 52 (порог 75), возраст домена 4 мес, GMC suspended без апелляций
2. **Bennet & Gray / Oliver and Faye** — возраст домена 4 мес (меньше года), магазины не созданы
3. **Charlie & Ted** — GMC удалён, нужно создать новый; ScamAdviser resolved 27/05/26
4. **Casa Giannini** — .it реестр не позволяет выключить Privacy полностью, RDAP не ответил (возраст неизвестен)
5. **Компания в регистранте** — не проверено ни для одного домена

## Что делается сейчас (2026-05-29)

- Верификация доменов: ScamAdviser, Trustpilot, Privacy OFF, компания в регистранте
- ScamAdviser и Trustpilot проверены для всех 6 доменов (утро 29.05)
- В процессе: Privacy OFF, компания в регистранте

## Следующие шаги

1. Завершить верификацию: компания в регистранте для всех доменов (задачи в tasks.json)
2. Уточнить у Андрея: минимальный возраст домена для GMC + на кого регистрировать GMC
3. Oliver and Alder: разобраться со ScamAdviser 52
4. Charlie & Ted: создать новый GMC
5. Bennet & Gray / Oliver and Faye: создать Shopify магазины, подключить домены
6. Casa Giannini: уточнить возраст домена, проверить Shopify auth
7. Аудит магазинов и GMC — достать задачи из таблицы (Андрей)

## История сессий

| Дата | Что сделано |
|---|---|
| 2026-05-27 | Аудит магазинов и GMC, ScamAdviser фолоуап, google-accounts.md заполнен |
| 2026-05-28 | Реструктуризация ecom областей в tasks.json, задачи верификации по 6 магазинам, хотлист доменов, куплены allspicefashion.com + lilymagsboutique.com |
| 2026-05-29 | Верификация доменов: ScamAdviser/Trustpilot/Privacy/GSB/Shopify auth, создана domain-verification-results.md |

## Ключевые файлы

| Файл | Содержимое |
|---|---|
| `stores-gmc.md` | Мастер-таблица магазинов и GMC статусов |
| `google-accounts.md` | Все Google аккаунты и привязки к магазинам |
| `domain-verification-results.md` | Результаты верификации доменов (ежемесячно) |
| `checklists/andrey-checklist.md` | Полный чеклист настройки магазина |
| `checklists/domain-verification.md` | Чеклист верификации домена |
| `domains-hotlist.md` | Хотлист доменов для GMC + купленные |
| `gmc/` | GMC-специфичные документы |
