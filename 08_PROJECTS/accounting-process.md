---
title: Порядок закрытия квартала (бухгалтерия)
date: 2026-06-26
type: process
---

# Порядок закрытия квартала — банк → инвойсы → таблица

Применимо и к Propria GmbH (фирма), и к ecom-магазинам — один и тот же процесс, разные счета/папки.

## Шаги

1. **Скачать банковские выписки.** Официальные Kontoauszug PDF по каждому месяцу квартала. Хранятся в Google Drive: `50. Bank statements/<Банк>/<год>/` (например `Commerzbank/2026/`).
2. **Скачать табличный файл с транзакциями.** Экспорт транзакций (банк/Revolut) — заливается/обновляется в Google Sheet вида `"<год> Propria"` (структурированная таблица: дата, сумма, описание, IBAN, категория, ссылка на инвойс).
3. **Запустить скрипт сопоставления.** Инструмент: `~/Projects/accounting` (FastAPI-сервис "Invoice Processor", `app.py`).
   - **Phase 1** — классифицирует PDF-инвойсы в рабочей папке Drive (например `"<год> Propria docs and transactions"`), переименовывает по шаблону `YYYYMMDD Vendor Amount.pdf` (через OpenAI, с подтверждением пользователя на каждый файл).
   - **Phase 2** — сопоставляет переименованные инвойсы со строками в таблице транзакций, пишет ссылку в колонку (`link_column` в `.env`, по умолчанию `T`), и перемещает привязанный PDF в подпапку **"Linked"** внутри рабочей папки.
   - Конфиг: `.env` в `~/Projects/accounting` — `folder_id`, `sheet_id`, `sheet_tab`, `link_column`.
4. **Проверить незакрытые транзакции.** После Phase 2 — посмотреть в таблице, какие транзакции остались без ссылки на инвойс (обычно: банковские комиссии, переводы в налоговую, зарплата — для них инвойса не существует и это нормально; остальное — донести вручную).

## Если инвойса нет в Drive, но он был переслан по почте

Скрипт `~/Projects/brain/tools/gmail_invoice_dl.py` скачивает PDF-вложения с Gmail-лейбла **"Propria GmbH/Rechnungen"** (только непрочитанные) в локальную папку `0. Inbox Propria` (синхронизированную с Drive). Если письмо уже помечено другим лейблом (например "Processed Invoices") — переставить на "Rechnungen" + пометить unread перед запуском.

Запуск (у скрипта нет своих Python-зависимостей, использовать venv с `googleapiclient`):
```
/Users/dister/Projects/accounting/.venv/bin/python3 /Users/dister/Projects/brain/tools/gmail_invoice_dl.py
```
OAuth-клиент общий с `accounting` (`~/.config/gmail-invoice-dl/client_secret.json` — копия `accounting/credentials/credentials.json`).

После скачивания: переместить файл из `0. Inbox Propria` в рабочую папку квартала, переименовать по конвенции `YYYYMMDD Vendor Amount.pdf`, затем привязать в таблице (см. выше).

**Известный баг:** скрипт фильтрует вложения строго по `mimeType == "application/pdf"`. Некоторые отправители (например MILES Mobility) шлют PDF-вложения с `mimeType: application/octet-stream` — скрипт их не видит и тихо ничего не скачивает (0 downloaded, без ошибки). В этом случае скачивать вручную через Gmail API `messages().attachments().get()` по attachment ID напрямую.

## Категоризация транзакций (столбец Type/L) и заглушка Link (столбец M)

После загрузки нового банковского экспорта в новую вкладку (формат `Buchungstag...Verwendungszweck`, без Type/Link) — добавить два столбца по образцу уже готовых кварталов: **Type** (категория) и **Link** (по умолчанию `"Kein Link"`, заменяется на реальную ссылку при сопоставлении с инвойсом).

Правила категоризации (по тексту операции, регистронезависимо):

| Паттерн в тексте | Категория |
|---|---|
| HECHT VON LUXBURG | FiBu |
| MILES Mobility | MILES |
| Finanzamt / Berlin für Körperschaften / Berliner Finanzämter / ZAHLUNGSVERKEHR BERLINER FINANZAEMT | Finanzamt |
| AllStar Gym / Pink Frauen Fitness / Sports Club Berlin | Fitness Umsatz |
| FIREFLIES.AI (любой знак — списание или возврат) | **Subscription** |
| Hale.Now Studios | **доход (+) → Fitness Umsatz; расход (−) → Фитнес расходы** |
| AOK Nordost | SV |
| Anna Disterheft | Gehalt |
| Kontoführung / Rechnungsabschluss | Bank |
| PayPal Europe | PayPal |
| IHK Berlin | IHK |
| всё остальное (Slack, OWU, Volbak, Zoho, Google Cloud, Anthropic, GitHub, BGHW и т.д.) | без категории (пусто) |

**Правило `Kein Link` — критично, не путать:**
`Kein Link` пишется в столбец Link **только** для категорий, где по природе операции инвойса не бывает: **Finanzamt, Bank, Gehalt, SV, PayPal**. Это финальное, навсегда верное значение.

Для всех остальных категорий (FiBu, MILES, Fitness Umsatz, Subscription, Фитнес расходы, IHK, без категории) столбец Link оставлять **пустым** — документ либо ещё не найден, либо будет привязан позже. Никогда не писать туда `Kein Link` — это означало бы "документа не будет", что неверно для этих категорий.

Скрипты: `/tmp/categorize_q2.py`, `/tmp/apply_main.py` (one-off, не сохранены в репозитории — пересоздать по этим правилам при необходимости для следующего квартала).

## Правила записи ссылок в таблицу Revolut EUR

**КРИТИЧНО — нарушение вызвало массовую перезапись строк (2026-07-01):**

1. **Всегда нормализовать порядок строк: oldest-first.** Revolut CSV скачивается в порядке newest-first (новые сверху), а Google Sheet хранит oldest-first (старые сверху). Перед записью CSV должен быть отсортирован по дате по возрастанию — или номера строк должны вычисляться динамически (см. правило 2).

2. **Никогда не записывать по номеру строки из CSV.** Вместо csv_row → ячейка K{csv_row}: найти строку по дате и сумме (`date == X AND amount == Y`), взять её row_index из таблицы, только тогда писать. Пример правильного подхода:
   ```python
   # НЕПРАВИЛЬНО:
   client.write_link(sheet_id, csv_row - 1, 10, url, tab)
   
   # ПРАВИЛЬНО:
   sheet_rows = load_all_rows(sheet_id, tab)  # oldest-first
   target = next(r for r in sheet_rows if r['date'] == date and r['amount'] == amount)
   client.write_link(sheet_id, target['row_index'], 10, url, tab)
   ```

3. **Перед записью проверить: правильный ли тип строки?** TOPUP → payment_transactions ссылка. CARD_PAYMENT Shopify* → billing invoice URL. TRANSFER к Shopify → payment_transactions. Другие строки — соответствующий инвойс или пусто.

## Drive API — обязательные параметры

**Папка "2026 Propria docs and transactions" находится в Shared Drive.** При любом прямом вызове Drive API (вне `DriveClient`) обязательны:

```python
supportsAllDrives=True          # для get, update, delete, create
includeItemsFromAllDrives=True  # для list
```

Без этих параметров — `404 File not found` даже для существующих файлов.

- `DriveClient` в `services/drive.py` уже содержит эти параметры везде.
- Одноразовые скрипты (fix_*.py, cleanup_*.py) — добавлять явно.
- `delete` не работает в Shared Drive при роли `writer`/`fileOrganizer`. Использовать `update(body={'trashed': True})` вместо `delete()`.

## Файловая структура Google Drive

### Propria GmbH — основная папка

**"2026 Propria docs and transactions"** (`1n2wOMMwx73mkvziaC5Xu5PTlCaljM_RU`)
- `2026 Propria` (Google Sheet) — мастер-таблица транзакций (вкладки: Commerzbank EUR, Revolut EUR)
- `Linked/` — инвойсы, привязанные к транзакциям (после Phase 2)
- Инвойсы PDF в корне — ещё не привязаны
- `Revolut EUR transaction-statement_*.csv` — CSV выгрузка Revolut EUR
- `Revolut USD transaction-statement_*.csv` — CSV выгрузка Revolut USD

**Правила для инвойсов:**
- Новый инвойс → в корень "2026 Propria docs and transactions/"
- После привязки скриптом → перемещается в "Linked/" автоматически (Phase 2)
- Название файла по конвенции: `YYYYMMDD Vendor InvoiceNumber Amount.pdf`

**50. Bank statements** (`154HnvAT7UlkoHxd3B2gIcViPj4YRBNGy`)
- `Commerzbank/2026/` — официальные Kontoauszug PDF по месяцам
- `Revolut EUR/2026/` — PDF выписки Revolut EUR по месяцам

### Ecom магазины — Shopify файлы

**Shopify магазинов папка** (`1rSG2X-dQA0dEzyUTUeZeDGGNCZEuqlD6`)
- `Charlie & Ted/` (`1ZLDv7i2wF2X6X48xRIvFbuwrs1P0ZJ1l`)
- `Marc&François/` (`1exosWZS1ZcwU5zUrqAjCjAPVBOUcaVmi`)
- `Casa Giannini/` (`1G8kbL-4Aj633YLhJm2SvQeGCrSD4naPU`)
- `Oliver and Alder/` (`1Q1SKu4Bz2WGJooJw2mVAXscqFBvsYtEM`)

**Правила для Shopify файлов:**
- Тип файла: `payment_transactions_export`, `payouts_export`, `orders_export`
- Название Google Sheet: `[Тип] [Период]` — например "Orders Q1 2026" (payment_transactions)
- Каждый магазин — в свою подпапку
- Если файл скачан через Playwright → сразу Upload в Drive через MCP, не хранить локально

**Shopify Inbox** (устаревшее, только 2025): `1XQEqLx2mvaQ4xbqhEIucDTTnkmmLhdek` — не использовать для 2026

### Локальный scratchpad

`.playwright-mcp/` в brain — только временно. После скачивания файла:
- Если нужен в Drive → Upload через MCP → удалить локально
- Если одноразовый → удалить сразу после использования

## Данные Q1+Q2 2026 — где что лежит

Аудит проведён 2026-07-03. Обновлять при изменениях.

### Расчётные счета (банковские выписки)

| Счёт | Тип | Путь | Период | Статус |
|---|---|---|---|---|
| Commerzbank EUR (DE74...800) | CSV | `~/Downloads/DE74120400000463223800_EUR_27-06-2026_1612.csv` | Q1 2026 (02.01–31.03) | ✓ есть |
| Commerzbank EUR (DE74...800) | CSV | `~/Downloads/DE74120400000463223800_EUR_27-06-2026_1610.csv` | Q2 2026 (02.04–26.06) | ✓ есть |
| Revolut EUR | CSV | Google Drive: `1n2wOMMwx73mkvziaC5Xu5PTlCaljM_RU` → `Revolut EUR transaction-statement_*.csv` | нужно уточнить диапазон | ⚠ проверить |
| Revolut EUR | PDF | `~/Downloads/Revolut_account-statement_2025-05-01_2026-02-18_en_*.pdf` | до 18.02.2026 | ⚠ неполное |

Revolut CSV за Q1+Q2 2026 скачивать: Revolut Business → Transactions → Export → EUR → 01.01.2026–30.06.2026.

### Shopify — квартальный отчёт (правила формирования)

**Результат:** HTML-отчёт `brain/07_OUTPUT/qXqY-YYYY-propria-report-v2.html`, по образцу `q1q2-2026-propria-report-v2.html`.

**Шаг 1 — Список пейаутов по каждому магазину**

Shopify Admin → Finance → Payouts → фильтр по периоду. По каждому пейауту записать:
- Payout ID, дата, статус (Deposited / Withdrawn), сумма
- Withdrawn = Chargeback/Dispute, требует отдельной документации

**Шаг 2 — Сопоставление с Revolut EUR**

Каждый Deposited-пейаут появляется в Revolut EUR как `TOPUP` (тип) с суммой пейаута.
Каждая Shopify billing (подписка / threshold) — строка `CARD_PAYMENT` с описанием `Shopify*`.
Для каждой CARD_PAYMENT Shopify: в Shopify Admin → Settings → Billing → Invoice History — скачать PDF по номеру счёта (ID в описании строки Revolut).

**Шаг 3 — Детализация транзакций** (опционально, не блокирует отчёт)

Finance → Payouts → открыть пейаут → Export order transactions (CSV будет отправлен на email).
В отчёте показывается как раскрывающийся блок per-payout.

**Структура HTML-отчёта:**
- На каждый магазин: итог Q1 / Q2 / общий, список пейаутов с суммами
- Отдельная таблица Shopify billing (CARD_PAYMENT) с ссылками на инвойсы
- Раздел "Offene Punkte" — несоответствия Revolut, Chargeback-документация, незакрытые детали

**Итоги Q1+Q2 2026:**

| Магазин | Q1 | Q2 | Итого |
|---|---|---|---|
| Charlie & Ted | €107,99 | €56,90 | €164,89 |
| Marc&François | €380,57 | €1.042,24 | €1.422,81 |
| Casa Giannini | −€2,29 | €0,00 | −€2,29 |
| Oliver and Alder | €236,21 | €309,42 | €545,63 |
| **Gesamt** | **€722,48** | **€1.408,56** | **€2.131,04** |

Всего 43 пейаута, 4 магазина. Отчёт создан 02.07.2026, Drive: пока локально `brain/07_OUTPUT/`.

### Инвойсы поставщиков

| Поставщик | Период | Где | Кол-во | Статус |
|---|---|---|---|---|
| Youlu International Dev. (Alibaba/Kungfubuy) | май–июн 2026 | Google Drive → `accounting/invoice_store.json` (file_id → Drive) | 5 инвойсов | ✓ есть |
| Cursor IDE | авг 2025–май 2026 | Google Drive → `accounting/invoice_store.json` | 7 инвойсов | ✓ есть |
| Неизвестный поставщик | 15.01.2026 | Google Drive → `accounting/invoice_store.json` | 1 инвойс (€200) | ⚠ уточнить |
| Инвойсы Q1 (если были закупки до мая) | янв–апр 2026 | Gmail "Propria GmbH/Rechnungen" или Drive | ? | ⚠ проверить |

Локальный индекс: `~/Projects/accounting/invoice_store.json` — 14 записей, структура: `file_id`, `vendor`, `invoice_date`, `amount`, `renamed_to`.

### Google Ads

Инвойсы Google Ads за Q1+Q2 2026 не найдены. Скачивать: Google Ads → Billing → Documents → фильтр Jan–Jun 2026 → Download PDF/CSV.

## Реестр недостающих документов — Commerzbank EUR Q1+Q2 2026

Аудит проведён 2026-07-05.

| Дата | Сумма | Контрагент | Тип | Статус | Примечание |
|---|---|---|---|---|---|
| 20.04.2026 | −€25,02 | FIREFLIES.AI | Subscription | ⚠ нет инвойса | Возврат от Fireflies — инвойс не высылают при возвратах. Закрыть как "Kein Link" после подтверждения у бухгалтера. |
| 19.05.2026 | −€25,33 | FIREFLIES.AI | Subscription | ⚠ нет инвойса | Аналогично апрелю — возврат, инвойса нет. |
| 26.05.2026 | −€1.050,00 | MILES Mobility GmbH | MILES | ❌ нет | Нестандартная сумма, инвойс в почте |
| 02.06.2026 | −€238,00 | HECHT VON LUXBURG | FiBu | ❌ нет | Инвойс FiBu июнь, в почте |
| 03.06.2026 | −€439,00 | MILES Mobility GmbH | MILES | ❌ нет | Инвойс MILES июнь, в почте |
| 29.06.2026 | −€47,60 | Hale.Now Studios GmbH | Фитнес расходы | ❌ нет | ReNr 202600156, запросить у Hale.Now |
| 14.04.2026 | +€90,83 | PayPal Europe | Fitness Umsatz | ❓ уточнить | Доход неизвестного происхождения — выяснить какой Rechnung |

### Что нужно сделать для полного отчёта

- [ ] Скачать Revolut CSV за Jan–Jun 2026 (Revolut Business → Export)
- [ ] Скачать Shopify payment_transactions для всех 4 магазинов за Q1+Q2 2026
- [ ] Скачать инвойсы Google Ads за Q1+Q2 2026
- [ ] Проверить инвойсы от поставщиков за Q1 (если были закупки в Jan–Apr)
- [ ] Уточнить "Vendor €200" от 15.01.2026 (что за поставщик)

## Реестр порталов для скачивания инвойсов

Обходить как чеклист при каждом закрытии квартала. Обновлять логины при смене аккаунтов.

| Поставщик | Портал | Аккаунт/логин | Что в Rechnungen | Примечание |
|---|---|---|---|---|
| Google Ads | ads.google.com/aw/billing | 3553194@gmail.com (+ другие?) | 4 инвойса Q1–Q2 2026 | Раздел Billing → Documents → PDF |
| OpenAI API | platform.openai.com/billing | ilja.disterheft@gmail.com | 1 инвойс (май 2026) | Usage → Invoice PDF |
| NordVPN | nordvpn.com/account | 3553194@gmail.com | 7 квитанций — проверить есть ли PDF | My Nord → Billing → Invoices |
| Cloud Starter (n8n) | app.n8n.cloud/billing | ? | 7 квитанций Paddle — проверить PDF | или через paddle.com если direct |
| Denote | — | ilja.disterheft@gmail.com | 6 квитанций KodePay | проверить есть ли PDF на сайте |
| MILES Mobility | miles-mobility.com | info@propria.gmbh | 5 писем "Zahlung war erfolgreich" | Mein Konto → Rechnungen |
| Hetzner | console.hetzner.cloud/billing | 3553194@gmail.com (K1214966824) | 6 "Minimum not reached" — архив | инвойс не выставлялся |
| Anthropic | console.anthropic.com/billing | ilja.disterheft@gmail.com | — (обработано) | |
| Slack | app.slack.com/billing | info@propria.gmbh | — (обработано) | |
| Fireflies | fireflies.ai/billing | ? | — (обработано) | |
| Hecht v. Luxburg | email (a.dudnichenko@) | — | — (инвойс в письме) | |

## Где смотреть

- Скрипт: `~/Projects/accounting/app.py` (`routers/processing.py`, `services/sheets.py`, `services/pipeline.py`)
- Запуск: `uvicorn app:app` в `~/Projects/accounting`, дефолтный порт 5000, UI в браузере
- Рабочая папка (Propria 2026): Drive id `1n2wOMMwx73mkvziaC5Xu5PTlCaljM_RU`
- Таблица транзакций (Propria 2026): Drive id `1CLagSWym_Z_qFeC_BUb6nro0CjGchoJ6GgoYTjnCb5k`
- Shopify payment_transactions 2026:
  - Charlie & Ted: `1u33wtTs4K7e7vtlsdrT5ysHRD3LB4dCmdlI5__tLjPA`
  - Marc&François: `1AKOKpDw3_nWTWZt4KBHLLHtoOJqyUAnxp3bpqj5nLp4`
  - Casa Giannini: `1Tmk1Q7wQsQTSCNeZI1Z0uuWnkCijrhtJRte8YvoQnqo`
  - Oliver and Alder: `19ufKcu9bQ1wcMU04jYkIJypSFXZCGtJeIwONTSxgKXM`
