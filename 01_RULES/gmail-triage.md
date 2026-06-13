---
type: rules
topic: gmail-triage
updated: 2026-05-21
---

# Gmail Triage Rules

Self-learning rules based on observed user actions. Update after each inbox session.

## Search rules

- Always use `in:inbox` — no time filters like `newer_than:Xd` (they silently miss emails).
- Use label names in searches (e.g. `label:"1. Attention"`), not label IDs.
- Do NOT declare inbox empty until `in:inbox` returns zero threads.
- Convert Attention emails to tasks ONLY when user says "давай разберём почту". Never auto-insert tasks at session start.
- If Attention / Payments are empty — say nothing. Report only when there is something actionable.

## Working with messages vs threads

- Use `label_message` / `unlabel_message` for individual messages when a thread mixes old (trashed) and new (inbox) emails.
- Use `label_thread` only when all messages in the thread need the same treatment.
- Emails in TRASH: do not review or mention unless user asks.

## Auto-routing (no confirmation needed)

| Sender / Pattern | Action |
|---|---|
| `noreply@service.easybank.de` | Search `from:noreply@service.easybank.de in:inbox` separately. Use `label_message` → 0. Payments + remove INBOX. Never touch messages already in TRASH. |
| Amazon order confirmations (`bestellbestaetigung@amazon.de`) | Delete |
| Amazon Spar-Abo delivery reminders (`no-reply@amazon.de`) | 3. Reading Later |
| Google location sharing reminders | Archive |
| Auto-reply confirmation (subject "Vielen Dank für Ihre E-Mail") | Archive |
| nausys.com sailing newsletters | Yachting + archive |
| Revolut "Your expenses are missing some info" | Delete |
| Revolut "Your weekly expenses summary" | Delete |
| newsletter@deutscheoperberlin.de | Always read and summarize content to user |
| Ryanair / travel reminders | Archive after calendar event is created |
| AliExpress tracking notifications | Delete after informing user |

## Attention triggers

| Pattern | Action |
|---|---|
| Google subscription / billing changes | 1. Attention |
| Financial: missing payment, pension, Riester | 1. Attention |

## Marketing / newsletters — unsubscribe + delete

Cannot click unsubscribe links via MCP. Tell user to unsubscribe manually first, then delete.

- info@skippercheck.net (unsubscribed 2026-05-21)

## Spam watch list — flag immediately if appears in inbox again

Unsubscribed 2026-05-20 (still sending as of 2026-06-11 — flag + delete):
- info@skippercheck.net

Unsubscribed 2026-05-20:
- noreply@gelato.com
- kampagnen@news.innn.it
- sail.athenablu@227608066.mailchimpapp.com
- booking@uth-sailing.com
- marketing@marketing.ryanairemail.com

Unsubscribed 2026-05-27 (yacht newsletters — keep worldcruising.com):
- charter@hermesyachting.com
- info@seafarerholidays.com
- hi@katamaran-sonea.de
- Boataround (any sender)

## Propria GmbH — обработка счетов (Rechnungen)

Новые письма со счетами попадают в `Propria GmbH` (корневая метка).
После скачивания вложения — переместить письмо в `Propria GmbH/Rechnungen`.
Старые письма в Rechnungen (50 шт.) не трогать.

Поисковые ключевые слова для инвойсов: receipt, invoice, rechnung, счет, счета

## Правило: метка = убрать INBOX

Когда любая метка присваивается треду из inbox (label_thread или label_message) — **всегда** сразу вызывать unlabel_thread/unlabel_message с INBOX. Без исключений.

## After creating a task from an email

Immediately archive or delete the email.

## Outgoing email formatting

Always add empty line before closing salutation:

```
...last sentence.

Mit freundlichen Grüßen,
Ilja Disterheft
```
