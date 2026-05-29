# Gmail сортировка

Анализ ~300 из ~1000 писем. Дата: 2026-05-19. Обновлено: 2026-05-24.

## Система классификации (логика триажа)

| Действие | Когда |
|---|---|
| **0. Payments** | нужно оплатить и/или сохранить инвойс |
| **1. Attention** | важная задача, требует действия сейчас |
| **3. Reading Later** | задача, но не срочно — можно подождать |
| **→ Folder** | явно относится к папке (MILES, Propria, Yachting...) — архивировать туда |
| **Archive** | может пригодиться, но действий не требует (подтверждения заказов, уведомления) |
| **Trash** | не нужно совсем (маркетинг, newsletters, legal notices) |

## Правила по отправителям

| Отправитель | Действие | Примечание |
|---|---|---|
| `invoice+statements@mail.anthropic.com` | 0. Payments | |
| `no-reply@revolut.com` | 0. Payments | |
| `billing@hetzner.com` | 0. Payments | |
| `payments-noreply@google.com` | 0. Payments | Google Ads |
| `support@nordaccount.com` | 0. Payments | NordVPN |
| `noreply@service.easybank.de` | Trash | транзакционные уведомления |
| `rueckgabe@amazon.de` | Trash | подтверждения возвратов |
| `noreply@lovable.dev` | Trash | маркетинг |
| `*@getorca.com` | Trash | newsletter |
| `support@predictwind.com` | Trash | marketing |
| `no-reply@traderepublic.com` | Trash | |
| `no-reply@accounts.google.com` | Trash | security alerts — показать, убедиться что это ты |
| Коды доступа, верификация устройств (любой отправитель) | Trash | проверить срок в тексте; если истёк или письмо старше 30 мин — Trash |
| `notify@mail.notion.so` | Trash | уведомления |
| `no-reply@legal.spotify.com` | Trash | legal notices |
| `*@deals.boataround.com` | Trash | отписан 2026-05-24 |
| `*@brevosend.com` | Trash | отписан 2026-05-24 |
| `abo@miles-mobility.com` | → Propria GmbH/MILES Abo | |
| `newsletter@deutscheoperberlin.de` | 3. Reading Later | |
| Leasing-офферы от автодилеров | 3. Reading Later | |
| `fred@fireflies.ai` | Archive | bot notifications |
| `noreply@notify.cloudflare.com` | Archive | invoices $0 |
| Подтверждения заказов (Amazon, H&M) | Archive | |
| PayPal уведомления об оплате | Archive | |

---


## Стратегия

Удалить глобальный фильтр `to:3553194@gmail.com → add label Forwarding/3553194`.
Заменить на 5 специфичных фильтров — тогда Ryanair → только Travels, easybank → только Payments, без дублирования лейблов.

---

## Фильтр 1: Travels

**Условие:**
```
to:3553194@gmail.com from:(*ryanairemail.com OR thy@mail.turkishairlines.com OR ajet@mail.ajet.com)
```
**Действие:** +Misc/Travels, Skip Inbox

Отправители:
- `service@service.ryanairemail.com` / `marketing@marketing.ryanairemail.com`
- `thy@mail.turkishairlines.com`
- `ajet@mail.ajet.com`

---

## Фильтр 2: Yachting

**Условие:**
```
to:3553194@gmail.com from:(boataround.com OR booking-manager.com OR euroyacht.hr OR orvas.eu OR sailsquare.com OR skippercheck.net OR brevosend.com OR phantomcharter.com OR nausys.com OR thraceyachting.com OR yolo-charters.com OR houseboat.it OR horizonyachtcharters.com OR flaka.nl OR sailway.es OR exclusive-yachtcharter.com OR alquilercatamaran.es OR kanalcharter.se OR pitter-yachting.com OR moanacharter.com OR predictwind.com OR mailchimpapp.com)
```
**Действие:** +Yachting, Skip Inbox

Отправители:
- `info@deals.boataround.com` — ежедневно
- `info@booking-manager.com`, `info@euroyacht.hr`, `newsletter@orvas.eu`
- `francescaellisse@sailsquare.com`, `info@skippercheck.net`
- `info@10637704.brevosend.com` (Sailing in Italy)
- `info@phantomcharter.com`, `info@nausys.com`
- `charters@thraceyachting.com`, `info@yolo-charters.com`
- `info@houseboat.it`, `marketing@horizonyachtcharters.com`
- `info@flaka.nl`, `info@sailway.es`
- `charter@exclusive-yachtcharter.com`, `info@alquilercatamaran.es`
- `boka@kanalcharter.se`, `info@pitter-yachting.com`
- `booking@moanacharter.com`, `support@predictwind.com`
- Mailchimp чартеры: `*athenablu*mailchimpapp.com`, `*oceandrift54*mailchimpapp.com`

---

## Фильтр 3: Payments

**Условие:**
```
to:3553194@gmail.com from:(noreply@service.easybank.de OR billing@hetzner.com OR payments-noreply@google.com OR support@nordaccount.com OR feedback@slack.com OR no-reply@easypark.net)
```
**Действие:** +0. Payments, Skip Inbox

Отправители:
- `noreply@service.easybank.de` — транзакционные уведомления (несколько в день)
- `billing@hetzner.com` — счета Hetzner
- `payments-noreply@google.com` — Google Ads invoice
- `support@nordaccount.com` — NordVPN receipts
- `feedback@slack.com` — subscription renewal
- `no-reply@easypark.net` — парковка

---

## Фильтр 4: Ecom / Business (оставить в Forwarding)

**Условие:**
```
to:3553194@gmail.com from:(noreply@skool.com OR fireflies.ai OR googlebase-noreply@google.com OR mailer@shopify.com OR email@email.shopify.com OR noreply@github.com OR scamadviser.com OR info@chancetobrand.de OR noreply@lovable.dev OR no-reply@email.slackhq.com OR no-reply@slack.com)
```
**Действие:** +Forwarding/3553194, Skip Inbox

Отправители:
- `noreply@skool.com` — GMC Help, AB Inner Circle, GAds Lab (много в день)
- `fred@fireflies.ai` — meeting recaps
- `googlebase-noreply@google.com` — Google Merchant Center
- `mailer@shopify.com` / `email@email.shopify.com` — Shopify login alerts + updates
- `noreply@github.com` — GitHub
- `report@scamadviser.com`, `noreply@scamadviser.com` — важно
- `info@chancetobrand.de` — поставщик

---

## Фильтр 5: Catch-all (остальное на 3553194)

**Условие:**
```
to:3553194@gmail.com
```
**Действие:** +Forwarding/3553194 (без Skip Inbox — оставлять видимым)

Сюда попадают: Google security alerts, Bitwarden 2FA, Doctolib, Instagram login, Starlink, O2, Amazon orders, Easybank info, Volvo, Rechnungen, личная переписка.

---

## Unsubscribe — список

Отписаться перед настройкой фильтров:

| Сервис | Адрес |
|--------|-------|
| Oscar Karem (спам) | `oscar@post.oscarkarem.com` |
| Coursiv (навязчивый спам) | `*@*updates.coursiv.co` |
| MyFoodBook (австралийские рецепты) | `newsletter@myfoodbook.com.au` |
| NordVPN upsell | `no-reply@mail.nordvpn.com` |
| Eventim | `*@*service.eventim.de` |
| Deutsche Oper Berlin | `newsletter@deutscheoperberlin.de` |
| Wakeboard Berlin | `newsletter@wakeboard-berlin.de` |
| CineStar | `card@news.reply.cinestar.de` |
| Planetarium Berlin | `newsletter@planetarium.berlin` |
| Lieferando | `newsletter@update.lieferando.de` |
| Vodafone | `info@enews.vodafone.de` |
| XING Jobs | `jobs@mail.xing.com` |
| Gelato | `noreply@gelato.com` |
| italki | `hello@e.italki.com` |
| TED | `recommends@ted.com` |
| Artlist | `team@newsletter.artlist.io` |
| Ozon (все) | `*@*news.ozon.ru` |
| Biohacking Academy (RU спам) | `info@biohacking-academy.pro` |
| BMW | `bmw@mail.bmw.de` |
| IKEA | `ikea@hej.news.email.ikea.de` |
| Deutschland startet | `redaktion@deutschland-startet.de` |
| innn.it (петиции) | `kampagnen@innn.it` |
| BerLINK | `BerLINK@user.luma-mail.com` |

---

## Порядок действий

1. [ ] Отписаться от сервисов из таблицы выше
2. [ ] Удалить глобальный фильтр `to:3553194@gmail.com`
3. [ ] Создать фильтр 1 (Travels)
4. [ ] Создать фильтр 2 (Yachting)
5. [ ] Создать фильтр 3 (Payments)
6. [ ] Создать фильтр 4 (Ecom/Business)
7. [ ] Создать фильтр 5 (Catch-all)
8. [ ] Очистить старые письма от ненужных лейблов (bulk)
