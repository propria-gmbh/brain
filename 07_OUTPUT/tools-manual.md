# Tools & Scripts — Справочник

Все скрипты и инструменты, собранные в одном месте.

---

## brain/tools/priority.py

**Что делает:** ранжирует задачи из `05_PLANS/tasks/tasks.json` по формуле `P = C×2 + D×3 + S×2 + G×2`.
- `C` (цвет/приоритет): orange=4, red=3, green=2, нет=1.
- `D` (срочность дедлайна, с наследованием от родителя через `parent_id`): <1нед=5, 1-2нед=4, 2-4нед=3, 1-3мес=2, просрочено=4, >3мес=0, нет=0. Для задач с тегом `reminder` дедлайн скорится иначе: due today=5, due tomorrow=3, иначе 0.
- `S` (stakes, число `$`, 0-5).
- `G` (`goal_rank`, наследуется вверх по дереву `parent_id`): rank1=5, rank2=3, rank3=1, нет=0.

Без `--done`: по умолчанию берёт только задачи с `someday=true` (если не передан `--all`), типа `task`/`subtask`, не done. Сортировка по `(-P, deadline)`.

**Запуск:**
```bash
cd ~/Projects/brain
python3 tools/priority.py              # топ 30 someday-задач
python3 tools/priority.py --top 20     # топ 20
python3 tools/priority.py --all        # все todo-задачи (не только someday), без лимита --top
python3 tools/priority.py --done --today   # выполнено сегодня
python3 tools/priority.py --done --week    # выполнено за эту неделю
python3 tools/priority.py --done --month   # за этот месяц
python3 tools/priority.py --done --year    # за этот год
python3 tools/priority.py --done           # за всё время
```

---

## brain/tools/add_task.py

**Что делает:** создаёт одну задачу в `05_PLANS/tasks/tasks.json` через CLI (без браузера). Генерирует `id` слагификацией заголовка (кириллица разрешена), проверяет коллизию id (добавляет `-2`, `-3`...). Если переданный `--area` не существует среди area-узлов — fallback на `area-inbox` с warning в stdout.

**Side effect:** после записи файла сразу делает `git add` + `git commit -m "add: <title>"` (не использует общий механизм `save_tasks()` из `today_server.py` — отдельный, более простой коммит).

**Запуск:**
```bash
python3 tools/add_task.py "Текст задачи" --area area-ecom --someday --deadline 2026-07-01 --notes "..."
```
Аргументы: `title` (позиционный), `--area` (default `area-inbox`), `--someday` (флаг), `--notes`, `--deadline` (`YYYY-MM-DD`).

---

## brain/tools/today_server.py

**Что делает:** браузерный дашборд задач, читает/пишет только `05_PLANS/tasks/tasks.json` (нет отдельного файла-плана — `today.md` упразднён, всё живёт в tasks.json). HTTP-сервер на стдлиб (`http.server`), HTML/CSS/JS зашиты в самом файле как строки. Три таба: **Сегодня**, **Задачи**, **Сессии**. Автообновление страницы через polling `/poll` каждые 2 сек (перезагружает, если изменился хэш mtime файлов `tasks.json`/`calendar_cache.json`, но не во время drag/фокуса на input).

**Запуск:**
```bash
today          # алиас в zshrc
# или
python3 ~/Projects/brain/tools/today_server.py
```
Открывает браузер на `http://localhost:7777`.

**Side effect — автокоммит:** каждый `save_tasks()` (любое изменение задачи) делает `git commit -am "server: update tasks"` в репозитории brain. Перед записью бэкапит текущий `tasks.json` в `tools/tasks_undo.json` (используется эндпоинтом `/undo`, не выведен в UI кнопкой — только POST).

### Структура данных tasks.json, которую ожидает сервер

Каждый элемент массива — словарь с полями (не все обязательны):
| Поле | Значение |
|---|---|
| `id` | уникальный строковый id |
| `type` | `"area"` (узел-папка) или `"task"` (обычная задача); area без `type` тоже считается area если есть дети-area |
| `title` | текст |
| `parent_id` | id родителя (area или task — задачи можно вкладывать друг в друга как подзадачи) |
| `status` | `"todo"` \| `"done"` \| `"active"` (area по умолчанию active) |
| `someday` | bool, лимит 20 одновременно (`SOMEDAY_LIMIT`) |
| `deadline` | `YYYY-MM-DD` или `null` |
| `scheduled_date` | `YYYY-MM-DD` — задача показывается в табе "Сегодня", если равна сегодняшней дате (или `deadline` == сегодня) |
| `context` | `"deep"` (Задачи), `"perekur"`/`"phone"`/`"email"` (Перекур), `"afternoon"` (2-я половина дня), `null`/`""` |
| `priority` | `"red"`/`"green"`/`"orange"`/`null` — синхронизирован с `marker` |
| `marker` | `"🔴"`/`"🟢"`/`"🟧"`/`""` — цикличная кнопка M на task-row, при смене обновляет `priority` |
| `recurring` | `"daily"` (сбрасывается на `todo` каждый день на месте, см. `reset_daily_recurring`) \| `"weekly"`/`"monthly"`/`"quarterly"`/`"yearly"` (при выполнении клонирует задачу с новым id `<id>-next` и пересчитанным дедлайном) \| `null` |
| `last_reset_date`, `missed_count` | только у `recurring: "daily"` — дата последнего сброса и счётчик пропусков (инкрементируется, если на момент сброса задача не была done) |
| `main_task_date` | `YYYY-MM-DD` — задача с этим полем равным сегодня рендерится в секции "Первая задача" (максимум одна такая задача одновременно) |
| `assignee` | `"claude"` \| `null` — переключается кнопкой "Клод" в модалке задачи |
| `type: "event"` + `event_summary` + `event_date` | связка календарного события (из `calendar_cache.json`) с задачей — так у события появляется done/todo состояние и запись в дейлог |
| `order` | float, порядок среди siblings (drag&drop пересчитывает как среднее между соседями) |
| `done_at` | `YYYY-MM-DD`, когда задача закрыта |
| `stakes`, `goal_rank`, `tags`, `notes`, `waiting_for`, `created_at` | используются `priority.py` для скоринга или как метаданные, сервер их не рендерит напрямую (кроме как в модалке через `/api/task`) |

**Инвариант:** у задачи `type: "task"` не может быть дочерних элементов (детей по `parent_id`) — если у неё появляется ребёнок (через `/add-task` с `parent_id`, `/set-parent` или drag&drop "в родители"), сервер автоматически переключает её в `type: "area"` (`ensure_area()`). «Проект» — это просто верхний `area` без `parent_id`, отдельного типа для него нет.

### Таб "Сегодня" (`/`)

Рендерится целиком из `tasks.json`, живого файла-плана нет.

- При каждом открытии страницы сначала вызывается `reset_daily_recurring(tasks)`: для всех задач с `recurring == "daily"`, у которых `last_reset_date != сегодня` — если `status != "done"`, `missed_count += 1`; затем `status = "todo"`, `done_at = None`, `last_reset_date = сегодня`.
- Секция **"Первая задача"** — задача с `main_task_date == сегодня` (максимум одна), рендерится первой крупным шрифтом. Кнопка "выбрать" (`#pick-main-task`) открывает `<select>` с топ-5 задач из `/api/top-priority` (только someday-задачи с `priority == "green"`), выбор пишет `main_task_date` через `/set-main-task` (`set_main_task_date` — снимает поле с любой другой задачи, у которой оно было на сегодня, прежде чем поставить на выбранную).
- Секция **"Утренний чеклист"** (сворачиваемый `<details>`) — задачи с `recurring == "daily"`, todo сверху, done снизу.
- Секции по контексту из tasks.json (`CONTEXT_SECTIONS`): "Задачи" (context=deep/None), "Перекур / На улице" (context=perekur/phone/email), "2-я половина дня" (context=afternoon) — показывают задачи с `scheduled_date == сегодня` или `deadline == сегодня`, не done.
- Секция "Сделано" — задачи с `status=="done" and done_at==сегодня`.
- Правый столбец — календарь на сегодня+будущее из `calendar_cache.json` (предупреждение "кэш устарел Nч" если старше 24ч); клик по событию сегодняшнего дня помечает done (`/done-event` → `mark_event_done`, создаёт/переключает связанную задачу `type: "event"`, событие остаётся видимым в календаре, но блёклым/зачёркнутым — `cal-done`).
- Quick-add инпут (`#inbox-input`) с опциональным контекстом/маркером — Enter создаёт задачу в `area-inbox` (`/add-task` → `add_task_inbox`).

**Дейлог:** при любой отметке задачи выполненной (`/toggle-task`, а также создание done-задачи через `/done-event`) сервер дописывает `04_THINKING/daylogs/YYYY-MM-DD.md` через `tools/daylog.py` (`write_daylog_entries`) и коммитит файл отдельным git-коммитом `"daylog: YYYY-MM-DD"`.

### Таб "Задачи" (`/tasks`)

Рендерит дерево area → area/task рекурсивно (`render_area`, `render_task_row`), без done-задач.

- **Поиск** (`#task-search`) — фильтрует по тексту `.task-text` всех task-row на странице (client-side, без запроса на сервер), также раскрывает area с совпадением в заголовке.
- **Кнопка Someday (N/20)** — фильтр, показывает только someday-задачи и их потомков (наследование вверх по дереву раскрывает родительские area). Подсвечивается красным, если `N > 20` (лимит см. `SOMEDAY_LIMIT`/`sd_limit`).
- **Кнопка "Просрочено (N)"** — фильтр по задачам с `deadline <= сегодня`, не area. Взаимоисключающий с Someday-фильтром (включение одного выключает другой через localStorage `od-filter`/`sd-filter`).
- **Каждый area-узел** (`<details>`): заголовок с инлайн-rename (двойной клик → contenteditable, Enter/blur сохраняет через `/rename`, Escape отменяет), кнопка **`A`** (`type-btn`) — переключает тип area↔task с подтверждением `confirm()` (`/set-type`; блокируется на сервере если переименование в area создаёт дубликат имени среди area), кнопка **`+`** (`sub-btn`) — открывает inline `<input>` для создания новой задачи прямо в этой area (`/add-task` с `parent_id` = id area, Enter создаёт, Escape/blur без текста отменяет). Area без детей рендерится одной строкой (без `<details>`) с тем же `+` и кнопкой `×` удаления.
- **Каждая задача** (`task-row`) — разгружена до 4 элементов: чекбокс done (`task-chk`, `/toggle-task` — если у задачи `recurring` и это не `daily`, при выполнении клонирует со сдвинутым дедлайном; `daily` сбрасывается отдельно через `reset_daily_recurring`), текст (одиночный клик с debounce 250мс открывает модалку `openTaskModal`/`/api/task`, двойной клик — inline rename, оба обработчика не конфликтуют благодаря таймеру), дедлайн (если есть, только отображение, красным если просрочен), кнопка **↗/✕↗** (`today-btn`) — добавляет/убирает `scheduled_date=сегодня`, кнопка **маркер** (`m-btn`, цикл `''→🔴→🟢→🟧→''`, синхронизирует `priority`). Остальные поля (контекст, тип, область/родитель, someday, повтор, assignee, дедлайн-редактирование, добавление подзадачи, удаление) — только через модалку, на строке больше не отображаются.
- **Drag&drop** (через `sortable.min.js`, бандл лежит в `tools/sortable.min.js`): top-level area можно переставлять между собой (только за `summary`, группа `top-areas`). Задачи можно перетаскивать между area (общая drag-группа `tasks`) — обычное перетаскивание переставляет порядок (`/move` с `position: before/after`), удержание над строкой ≥500мс делает её родителем (`position: child`, подсветка класса `drop-child`; переводит целевую задачу в `area`, если она ещё не была).
- **Модалка карточки задачи** (`openTaskModal`, `/api/task?id=`): "Запланировано"/"Дедлайн" (клик → `<input type=date>`), select "Контекст", select "Тип" (task/area, `/set-type`), select "Область" (родитель из `window.AREAS`, `/set-parent` — переводит новый родитель в area автоматически), select "Повтор" (нет/ежедневно/еженедельно/ежемесячно/раз в квартал/ежегодно, `/set-recurring`), toggle "Someday" (`/someday`, показывает `alert()` при блокировке лимита), toggle "Клод" (`/set-assignee`), read-only "Маркер", кнопка "Удалить задачу" (с `confirm()`, `/delete`), список подзадач с чекбоксами + инпут добавления новой подзадачи по Enter (`/add-task` с `parent_id`).

### Таб "Сессии" (`/sessions`)

Читает `04_THINKING/session-log.jsonl` (пишет туда `session_indexer.py`, см. ниже), группирует по дате, дедуп по `session_id`, показывает заголовок/первое сообщение, длительность, число реплик, изменённые файлы, проект (последний компонент `cwd`). Только просмотр, без интерактива.

### Эндпоинты (HTTP)

GET: `/` (Сегодня), `/tasks` (Задачи), `/sessions` (Сессии), `/poll` (хэш mtime для автообновления), `/api/top-priority` (топ-5 someday по приоритету), `/api/task?id=` (детали задачи + subtasks + parent_title).

POST (читают JSON body, возвращают 200 без тела, кроме отмеченных): `/toggle-task` (done/todo по id, клонирует recurring кроме daily, пишет дейлог при переходе в done), `/someday` (toggle, **возвращает JSON** при блокировке лимита), `/delete` (рекурсивное удаление), `/done-event` (отметить/снять событие календаря выполненным через связанную задачу `type: event`), `/rename` (**возвращает 409 JSON** при дубликате имени area), `/set-type`, `/set-parent` (переводит нового родителя в area), `/set-deadline`, `/add-task` (создание в area-inbox или указанный parent_id, переводит parent в area), `/set-main-task` (принимает `{id}`, эксклюзивно выставляет `main_task_date`), `/move` (drag&drop), `/set-marker`, `/set-assignee` (toggle `assignee: "claude"`), `/undo` (откат последнего `save_tasks` из бэкапа `tools/tasks_undo.json`, не привязан к кнопке UI), `/move-order` (сдвиг up/down по соседям, не привязан к видимой кнопке UI), `/set-recurring`, `/set-scheduled-date`, `/set-context`.

---

## brain/tools/gmail_invoice_dl.py

**Что делает:** скачивает PDF-вложения из Gmail лейбла `Propria GmbH/Rechnungen` (только непрочитанные). После скачивания помечает письмо прочитанным. Дедупликация по SHA256.

**Куда кладёт:** `Shared drives/Propria/Propria GmbH/0. Inbox Propria`

**Имя файла:** `YYYY-MM-DD_domain_originalname.pdf`

**Запуск:**
```bash
python3 ~/Projects/brain/tools/gmail_invoice_dl.py
# или в другую папку:
python3 ~/Projects/brain/tools/gmail_invoice_dl.py --dest ~/другая/папка
```

**Первый запуск — настройка OAuth (один раз):**
1. Установить зависимости: `pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2`
2. [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) → OAuth client ID → Desktop app → скачать JSON
3. Сохранить как `~/.config/gmail-invoice-dl/client_secret.json`
4. Добавить `ilja.disterheft@gmail.com` как test user в OAuth consent screen
5. Запустить — откроется браузер для авторизации, токен сохранится автоматически

**Конфиг файлы:**
| Файл | Назначение |
|---|---|
| `~/.config/gmail-invoice-dl/client_secret.json` | OAuth credentials (создать вручную) |
| `~/.config/gmail-invoice-dl/token.json` | OAuth token (автоматически) |
| `~/.config/gmail-invoice-dl/state.json` | Хеши скачанных PDF |

**Расписание:** запускать 2 раза в неделю (через `/schedule` или вручную).

---

## ~/.claude/hooks/rule-enforcer.py

**Что делает:** надсмотрщик-хук. Перехватывает вызовы инструментов Claude до выполнения и блокирует нарушения правил. При нарушении выводит сообщение и отменяет вызов (exit 2).

**Правила** описаны в `~/.claude/hooks/rules.json`. Формат:
```json
{
  "rules": [
    {
      "id": "rule-id",
      "tool": "mcp__claude_ai_Gmail__search_threads",
      "checks": [
        { "field": "query", "contains": "label:Label_", "message": "Сообщение об ошибке" }
      ]
    }
  ]
}
```

**Активные правила:**
| Правило | Инструмент | Что блокирует |
|---|---|---|
| `gmail-label-format` | Gmail search | label ID (`Label_XXX`) и временные фильтры (`newer_than:`, `after:`, `before:`, `older_than:`) |

---

## Gmail MCP — инструменты Claude Code

Сервер настроен в `~/.claude/settings.json` как `httpUrl`: `https://gmailmcp.googleapis.com/mcp/v1`, имя сервера `gmail`.

**Инструменты НЕ видны через ToolSearch** — вызывать напрямую по имени.

| Инструмент | Что делает |
|---|---|
| `mcp__gmail__search_threads` | поиск писем (как в поиске Gmail) |
| `mcp__gmail__get_thread` | читать полное содержимое треда |
| `mcp__gmail__label_thread` | поставить метку |
| `mcp__gmail__unlabel_thread` | снять метку |
| `mcp__gmail__create_draft` | создать черновик |
| `mcp__gmail__list_labels` | список меток с их ID |

**Важно:** метки искать по имени, не по ID (`Label_XXX` заблокированы rule-enforcer).

**Подключён в:** `~/.claude/settings.json` → `hooks.PreToolUse`

**Как добавить новое правило:** добавить объект в массив `rules` в `rules.json`. Поддерживаются любые инструменты Claude и любые поля их input.

---

## brain/tools/telegram_bot.py

**Что делает:** Telegram-бот, даёт доступ к brain из телефона. Команды работают напрямую с файлами (без Claude). Свободный текст — через Claude Code CLI.

**Запуск:** автоматически через launchd (`com.dister.telegram-bot`), стартует при входе в систему.

**⚠️ Сломано (2026-07-06):** `/today`, `/add`, `/done` читают/пишут `05_PLANS/today.md` напрямую — файл удалён при переходе дашборда на tasks.json-only. Задача на починку в tasks.json (area-inbox). До починки эти три команды не работают, свободный текст (через Claude CLI) работает как обычно.

**Команды:**
| Команда | Что делает |
|---|---|
| `/today` | Показать today.md (мгновенно) — сломано, см. выше |
| `/add <текст>` | Добавить задачу в today.md — сломано, см. выше |
| `/done <задача>` | Отметить задачу выполненной — сломано, см. выше |
| Любой текст | Claude отвечает с контекстом brain/ |

**Push из скриптов:**
```bash
python3 ~/Projects/brain/tools/telegram_bot.py --send "текст сообщения"
```

**Конфиг:** `~/.config/telegram-bot/config.json` — токен и chat_id
**Логи:** `~/.config/telegram-bot/bot.log`

**Ограничения:** MCP инструменты (Gmail, Calendar) недоступны — бот работает только с локальными файлами.

**Управление:**
```bash
launchctl kickstart -k gui/$UID/com.dister.telegram-bot  # перезапуск
launchctl list | grep telegram-bot                        # статус
```

---

## brain/tools/filter_domains.py

**Что делает:** фильтрует TSV/CSV с аукциона GoDaddy под критерии GMC (apparel-магазин). Критерии (`passes_filter`): `.com`, без цифр в имени, не в блоклисте (swim/kids/bridal/adult и т.п.), и подходит под один из паттернов — apparel-keyword, имя+имя (`looks_like_two_names`, по словарю `NAMES`), prefix+слово (`is_prefix_word`, словарь `FASHION_PREFIXES`), слово+suffix (`is_word_suffix`, `FASHION_SUFFIXES`), два слова через дефис (`is_two_hyphenated_words`), одно элегантное слово 5-10 букв (`is_single_elegant_word`). Также фильтрует по `--age` (мин. возраст домена) и `--max-price`. Сортирует результат по `(-возраст, -Majestic TF)`.

**Запуск:**
```bash
python3 tools/filter_domains.py domains.tsv
python3 tools/filter_domains.py domains.tsv --age 1 --max-price 50 --out domains_filtered.tsv
# без --out печатает TSV в stdout
```

**Файл shortlist:** `tools/domains_shortlist.tsv` — финальный список кандидатов из сессии 2026-05-28 (не генерируется этим скриптом автоматически, отдельный артефакт).

---

## brain/tools/convert_vtt_kb.py

**Что делает:** конвертирует VTT-субтитры видео AB Inner Circle (Google Ads Masterclass) в markdown knowledge base. Источник захардкожен — папка на Google Drive (`Shared drives/Propria/Dropshipping/Google Ads Masterclass`). Группирует файлы по номеру секции (префикс `N.` в имени файла, маппинг названий секций в `SECTION_NAMES`), чистит VTT (убирает заголовок WEBVTT, таймкоды, номера cue, дублирующиеся строки), один markdown-файл на секцию + `README.md`-индекс со списком файлов.

**Куда кладёт:** `08_PROJECTS/ecom/ab-inner-circle/` (создаёт папку при необходимости).

**Запуск:**
```bash
python3 tools/convert_vtt_kb.py
```
Без аргументов — сам сканирует папку VTT-файлов на Drive.

---

## brain/tools/migrate_to_areas.py / migrate_tasks.py

**Что делают:** одноразовые скрипты миграции `tasks.json` (переход с project+section на area-иерархию с `parent_id`, 2026-05). Миграция завершена, повторный запуск не нужен — `migrate_to_areas.py` пишет бэкап в `tasks.json.bak2` перед перезаписью; `migrate_tasks.py` парсит старые `.md`-файлы задач (`ecom.md`, `propria.md`, `health.md` и др.) в `tasks.json` с нуля (перетирает файл).

---

## brain/tools/daylog.py

**Что делает:** модуль (не хук — импортируется напрямую `today_server.py`), функция `write_daylog_entries(date_str, titles)`. Вызывается из `toggle_task()` и `mark_event_done()` при переходе задачи в `done` (заголовки в tasks.json уже чистые, доп. нормализация не нужна — в отличие от старого today.md-хука). Создаёт/дополняет дейлог `04_THINKING/daylogs/YYYY-MM-DD.md` (секция "## Задачи выполнены", без дублей), коммитит файл отдельным git-коммитом `"daylog: YYYY-MM-DD"`. Раньше это делал внешний PostToolUse-хук `sync_today_done.py`, реагировавший на правки `today.md` — упразднён вместе с самим файлом.

**Запуск:** не запускается вручную — подключён как hook (`PostToolUse`) в `~/.claude/settings.json`, получает данные хука через stdin (JSON с `tool_input.file_path`).

---

## brain/tools/session_indexer.py

**Что делает:** Stop-хук Claude Code. По завершении сессии читает JSONL-транскрипт (путь из stdin hook-данных), извлекает: заголовок сессии (последний `ai-title`), первое сообщение пользователя, тайминги (старт/конец/длительность в минутах), число реплик пользователя, счётчики использованных инструментов, список изменённых файлов (Write/Edit) и прочитанных (Read, до 20). Добавляет одну JSON-строку в `04_THINKING/session-log.jsonl` (append, не перезаписывает). При ошибке логирует traceback в `04_THINKING/session-indexer-errors.log`.

**Запуск:** не запускается вручную — подключён как hook (`Stop`) в `~/.claude/settings.json`, читает JSON из stdin.

**Потребитель:** таб "Сессии" в `today_server.py` читает этот же `session-log.jsonl`.

---

## brain/tools/transcribe_andrey.sh

**Что делает:** одноразовый bash-скрипт транскрипции конкретного видео-созвона с Андреем (GMC, 23.04.2026). Шаги: 1) `ffmpeg` извлекает аудио из захардкоженного `.mp4` на Google Drive в `/tmp/andrey_transcribe.mp3` (16kHz mono); 2) транскрибирует через **OpenAI Whisper API** (`whisper-1`, ключ из `~/Projects/accounting/.env`, python-окружение `accounting/.venv`); 3) пишет результат в `03_RESEARCH/andrey-call-gmc-transcript.md` и коммитит в git.

**Запуск:** только из терминала напрямую (не из Claude Code, по комментарию в самом файле):
```bash
bash tools/transcribe_andrey.sh
```

**Важно:** использует OpenAI Whisper API — платный вызов. Существует общее правило не использовать Whisper API без необходимости (см. `feedback_no_whisper` в памяти) — этот скрипт привязан к конкретному разовому видео, не шаблон для повторного использования.

---

## brain/tools/build_propria_report.py

**Что делает:** строит самодостаточный HTML-отчёт `07_OUTPUT/q1q2-2026-propria-report-v5.html` для бухгалтерии Propria GmbH за Q1+Q2 2026. Читает Revolut JSON (`/private/tmp/revolut_clean.json`) и Shopify CSV-экспорты (Payouts, Transactions, Orders) для 4 магазинов (Marc&François, Oliver & Alder, Charlie & Ted, Casa Giannini). Вкладки: Revolut EUR, Payouts, Orders, Transactions, Lieferanten, P&L. Ссылки инвойс-ордер хранятся в `localStorage` браузера; East Baite (Kungfu Buy) линки заполняются автоматически из `kfb_auto_links` в Revolut JSON.

**Запуск:**
```bash
cd ~/Projects/brain
python3 tools/build_propria_report.py
# Открыть: http://localhost:8868/q1q2-2026-propria-report-v5.html
# Сервер: python3 -m http.server 8868 (из 07_OUTPUT/)
```

---

## Flow: обработка инвойсов

```
Получил инвойс → оплатил → переносишь письмо в Propria GmbH/Rechnungen
                                        ↓
             python3 tools/gmail_invoice_dl.py
                                        ↓
             PDF в 0. Inbox Propria (Google Drive)
             письмо помечено прочитанным
                                        ↓
             раскладываешь PDF по банковским выпискам
```
