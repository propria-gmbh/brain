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
