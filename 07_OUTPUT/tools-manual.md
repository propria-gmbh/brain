# Tools & Scripts — Справочник

Все скрипты и инструменты, собранные в одном месте.

---

## brain/tools/priority.py

**Что делает:** ранжирует все задачи из task-файлов по формуле P = C×2 + D×3 + S×2 + G×2.

**Запуск:**
```bash
cd ~/Projects/brain
python3 tools/priority.py              # топ 30
python3 tools/priority.py --top 20    # топ 20
python3 tools/priority.py --red       # только 🔴 и 🟧
python3 tools/priority.py --green     # только 🟢 и 🟧
python3 tools/priority.py --someday   # только [someday]
python3 tools/priority.py --all       # все задачи без лимита
python3 tools/priority.py --done --today   # выполнено сегодня
python3 tools/priority.py --done --week    # выполнено за неделю
```

---

## brain/tools/today_server.py

**Что делает:** браузерный дашборд задач. Два таба: Сегодня (today.md) и Задачи (все task-файлы). Чекбоксы, someday-toggle, удаление, коллапс по проектам.

**Запуск:**
```bash
today          # алиас в zshrc
# или
python3 ~/Projects/brain/tools/today_server.py
```
Открывает браузер на `http://localhost:7777`.

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

**Команды:**
| Команда | Что делает |
|---|---|
| `/today` | Показать today.md (мгновенно) |
| `/add <текст>` | Добавить задачу в today.md |
| `/done <задача>` | Отметить задачу выполненной |
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
