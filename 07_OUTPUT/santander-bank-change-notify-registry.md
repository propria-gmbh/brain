# Реестр для смены реквизитов (Santander → Sparkasse)

Источник данных: [santander-recurring-payments.md](santander-recurring-payments.md). Здесь — только actionable список: кому и как сообщать новые реквизиты.

## A. Прямые SEPA-мандаты — нужно отправить новый IBAN получателю напрямую

| Получатель | Договор/референс | Сумма | Статус |
|---|---|---|---|
| Generali Krankenversicherung | Versicherungsnr. 0807402 04 | €73.11/мес | вручную через портал (GesundheitsApp/Web-Postfach, нужен логин Ильи) |
| FitX Deutschland GmbH (мандат 1) | MLREF2906959 | €24.00/мес | не начато |
| FitX Deutschland GmbH (мандат 2) | MLREF2906960 | €24.00/мес | не начато |
| DB Vertrieb GmbH | Abo 6443 4752 3 | €63.00/мес | не начато |
| Telefonica Germany / O2 | Kd-Nr. 6071 7693 45 | €50–56/мес | не начато |
| Dialog Versicherung AG | Vertrag 227403 2150 | €8.92/мес | не начато |
| sim.de (Drillisch Online GmbH) ×2 | CRED DE40ZZZ0000020926 | €9.99 ×2/мес | не начато |
| ACE-Wirtschaftsdienst GmbH | MREF SEPA-W0016 77065 | €82.00/год | не начато — см. отдельную задачу ниже (сначала выяснить статус договора) |
| Rundfunkbeitrag (ARD, ZDF, DRadio) | Beitragsnr. 68673 7615 | €55.08/квартал | не начато |
| Die Haftpflichtkasse VVaG | Vertrag/MREF HK-MN-60858591-02 | €68.31/год (?) | не начато — уточнить у Ильи, актуальный ли это страховщик (см. заметку про VOLKSWOHL BUND/Ammerländer) |

## B. Через PayPal — реквизиты менять не у получателя, а в PayPal (привязанный счёт)

Один раз обновить привязанный банковский счёт в PayPal — закрывает все три позиции:

| Получатель | Сумма | Комментарий |
|---|---|---|
| Spotify AB | €12–22/мес (нестабильно) | Списывается через PayPal (PP.4523.PP) |
| Paddle.net | €3.10–3.90/мес | Списывается через PayPal (PP.4523.PP) |
| PayPal *Rivertygmbh | переменная | Рассрочки за покупки, тоже через PayPal |

## C. Карточные платежи — реквизиты меняются через провайдера сервиса, не через получателя

| Получатель | Сумма | Комментарий |
|---|---|---|
| Slack | €9.82/мес | Оплата картой (не SEPA), обновить карту в billing Slack |
| Apple.com/bill (iTunes/App Store) | €0.99/мес | Оплата картой, обновить в Apple ID billing |

## Не включено (расторгнуто / неактивно)

- **ADVOCARD Rechtsschutzversicherung** — не встречается в выписках с апреля 2025, похоже расторгнут
- **Allianz Versicherungs-AG (KFZ)** — подтверждён квартально только за 2025 год, в выписках 2026 года (янв–июнь) не найден
- **VOLKSWOHL BUND / Ammerländer Versicherung** — последнее списание декабрь 2025, возможно заменён на Die Haftpflichtkasse VVaG (см. пункт A)

## Разово / вне подписок

- **Gabriela Heyman** (аренда) — не входит в этот реестр, отдельная тема, см. [gabriela-heyman-payments.md](gabriela-heyman-payments.md)
