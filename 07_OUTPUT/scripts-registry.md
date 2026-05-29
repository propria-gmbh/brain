# Scripts Registry

Все скрипты и сервисы на компе. Обновлено: 2026-05-25.

## brain/tools/

| Скрипт | Что делает | Запуск |
|---|---|---|
| `today_server.py` | Браузерный дашборд задач (today.md + tasks.json). Чекбоксы, someday, drag & drop. | `today` или `python3 ~/Projects/brain/tools/today_server.py` → :7777 |
| `priority.py` | Ранжирует задачи из tasks.json по P = C×2+D×3+S×2+G×2 | `python3 tools/priority.py [--top N] [--red] [--green] [--someday] [--all] [--done --today/--week]` |
| `gmail_invoice_dl.py` | Скачивает PDF-вложения из Gmail лейбла Propria GmbH/Rechnungen → Google Drive. Дедупликация по SHA256. | `python3 ~/Projects/brain/tools/gmail_invoice_dl.py` |
| `migrate_tasks.py` | Разовый скрипт миграции задач из .md файлов в tasks.json (выполнен 2026-05-25). | — |
| `convert_vtt_kb.py` | Конвертирует VTT-транскрипты в KB-документы (использовался для Inner Circle). | `python3 tools/convert_vtt_kb.py <file.vtt>` |
| `filter_domains.py` | Фильтрует TSV с аукциона GoDaddy: .com, возраст 1+ год, паттерн имя+имя или apparel-ключевые слова. | `python3 tools/filter_domains.py domains.tsv [--age 1] [--max-price 50] [--out results.tsv]` |

## accounting/ (бухгалтерия Propria)

Сервис автоматической обработки инвойсов: Gmail → PDF → классификация → Google Sheets.

| Скрипт | Что делает |
|---|---|
| `__main__.py` / `app.py` | Точка входа приложения |
| `rename_invoices.py` | Переименование инвойсов по шаблону (Фаза 1 задачи Аллы) |
| `gmail_attachments.py` | Скачивание вложений из Gmail |
| `services/pipeline.py` | Пайплайн: PDF → классификация → матчинг транзакций → Sheets |
| `services/classifier.py` | AI-классификатор документов |
| `services/pdf_extractor.py` | Извлечение данных из PDF |
| `services/sheets.py` | Запись результатов в Google Sheets |
| `services/matcher.py` | Матчинг инвойсов с банковскими транзакциями |
| `scripts/integration_audit.py` | Аудит интеграций |

## listing_automation/keywords/

| Скрипт | Что делает |
|---|---|
| `analyze_trends.py` | Анализ трендов ключевых слов |
| `import_keywords.py` | Импорт ключевых слов |

## product_search/scripts/ (пайплайн поиска товаров)

| Скрипт | Этап | Что делает |
|---|---|---|
| `stage1_generate_keywords.py` | 1 | Генерация ключевых слов |
| `stage2_build_report_html.py` | 2 | Сборка HTML-отчёта |
| `stage2_classify_volume_growth.py` | 2 | Классификация по объёму и росту |
| `stage2_filter_growth_keywords.py` | 2 | Фильтрация растущих ключевых слов |
| `stage2_google_trends.py` | 2 | Данные Google Trends |
| `stage2_merge_keyword_export.py` | 2 | Объединение экспортов |
| `stage2_merge_trends.py` | 2 | Объединение трендов |
| `stage2_trends_12m_visual.py` | 2 | Визуализация трендов 12 мес. |
| `stage3_browser_google_search.py` | 3 | Браузерный поиск конкурентов |
| `stage3_prepare_searches.py` | 3 | Подготовка поисковых запросов |
| `stage4_check_stores.py` | 4 | Проверка магазинов конкурентов |
| `keyword_planner_browser.py` | — | Google Keyword Planner через браузер |
| `seasonality.py` | — | Анализ сезонности |

## shopify_assistant/scripts/

| Скрипт | Что делает |
|---|---|
| `sot_docgen.py` | Генерация документации SOT (Source of Truth) |
| `sot_index_build.py` | Сборка индекса SOT |

## personal-agent/ (Hetzner VPS)

| Скрипт | Что делает |
|---|---|
| `health/health.py` | Healthcheck сервиса (эндпоинт для мониторинга) |
| `health/deploy.sh` | Деплой агента на Hetzner VPS |

## GMC/

| Скрипт | Что делает |
|---|---|
| `googlebot-check.py` | Проверка доступности сайта для Googlebot |

## VAYDY/scripts/

| Скрипт | Что делает |
|---|---|
| `export_markdown_to_html.py` | Экспорт Markdown → HTML |
| `export_markdown_to_pdf.py` | Экспорт Markdown → PDF |

## ~/.claude/hooks/

| Скрипт | Что делает |
|---|---|
| `rule-enforcer.py` | Pre-tool хук Claude Code. Блокирует нарушения правил (напр. label ID в Gmail-запросах). Конфиг: `rules.json`. |
