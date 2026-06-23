# Юридика и операционный минимум

## Статус

Фирма (Propria GmbH) — можно выставлять инвойсы прямо сейчас, шаблон ниже (раздел "Шаблон инвойса").

ИП (Einzelunternehmen) — зарегистрировано 1,5 года назад, ни разу не использовалось, статус неясен. Задача уточнить в Finanzamt и решить, через что выставлять кухни (GmbH/ИП) — см. `tasks.json`.

---

## Текущая ситуация

### Фирма (Propria GmbH)
Можно выставлять инвойсы немедленно. Никаких дополнительных регистраций не нужно.
- Проверить: включена ли Küchenmontage / Handwerk в Unternehmensgegenstand в Satzung
- Если нет — формально стоит добавить, но на практике для первых проектов некритично

### ИП (Einzelunternehmen)
Зарегистрировано ~1,5 года назад, не использовалось.

**Риски бездействия:**
- Finanzamt мог уже послать Fragebogen или напоминания — могут быть штрафы за нулевые декларации
- Steuernummer может быть неактивна

**Действие: позвонить в Finanzamt (или прийти лично)**
Вопросы для налоговой:
1. Активно ли моё ИП, есть ли задолженности по декларациям?
2. Нужно ли подать нулевые EÜR за прошлые годы?
3. Можно ли использовать ИП сейчас или сначала нужно закрыть хвосты?
4. Имеет ли смысл закрыть ИП и работать только через GmbH?

**Финanzamt Берлин:** найти своё по адресу регистрации на finanzamt-finder.de

---

## Шаблон инвойса (Rechnung)

Обязательные поля по немецкому закону:
```
[Твоё имя / Firmenname]
[Адрес]
[Steuernummer: XX/XXX/XXXXX]

Rechnung Nr.: [YYYY-001]
Datum: [дата]

An:
[Имя клиента]
[Адрес клиента]

Leistungsbeschreibung:
- Küchenmontage gemäß Vereinbarung vom [дата]      [сумма] €

Nettobetrag:                                        [сумма] €
19% USt.:                                           [сумма] €
Gesamtbetrag:                                       [сумма] €

Zahlungsziel: 14 Tage
IBAN: [твой IBAN]

Hinweis: Im Zusammenhang mit einem Grundstück erbrachte Leistungen sind nach
§ 14b Abs. 1 Satz 5 UStG vom Kunden zwei Jahre aufzubewahren.
```

**Важно:** строка "Gemäß §19 UStG wird keine Umsatzsteuer berechnet." убрана — Propria GmbH фактически не Kleinunternehmer, в счетах указывается 19% USt (см. Angebot-026 Georgia). Освобождение по §19 UStG зависит от оборота, а не от формы GmbH — это не применимо к текущей практике фирмы.

Строка-Hinweis про 2-летнее хранение обязательна (§14 Abs. 4 Nr. 9 UStG) для Leistungen im Zusammenhang mit einem Grundstück частным клиентам (применимо к монтажу кухни, если работа затрагивает субстанцию здания — навеска на стену, подключение воды/электрики). Не штрафуется отдельно, но формально требуется.

Инструмент: использовать [Debitoor](https://debitoor.de), [Sevdesk](https://sevdesk.de) или просто Word/Google Docs с шаблоном.

---

## Для яхтенного направления (международные клиенты)

- Если клиент из другой страны ЕС: укажи его VAT-номер, применяй reverse charge
- Если клиент вне ЕС: НДС не применяется
- Договор на PM: составить простой 1-страничный contract (scope, payment terms, liability limit)
- Платежи: принимать через банковский перевод (IBAN) или Wise для удобства международных клиентов

---

## Страховка

- Для кухонного направления: Haftpflichtversicherung für Handwerker (~150–300 €/год)
- Для яхтенного PM: Professional Indemnity Insurance (если берёшь ответственность за проект)
- Провайдеры: Hiscox, AXA, Allianz

---

## Банковский счёт

- Для старта: личный счёт допустим, но лучше отдельный
- Рекомендации: N26 Business / Qonto / Penta (бесплатно или дёшево, онлайн)

---

## Rechtliche Angaben для Kleinanzeigen-Gewerbeaccount (минимально необходимые документы)

**Статус:** требуется для Kleinanzeigen Gewerbeaccount (раздел "Rechtliche Angaben" — 0 из 3 полей, отмечено "Fehlt"). Связано с задачей в tasks.json (`подготовить-agb-и-datenschutzerklärung-для-propria-gmbh-mont`).

**Важно (не юридическая консультация):** Widerrufsbelehrung и Muster-Widerrufsformular ниже — официальный текст закона (Anlage 1 и Anlage 2 zu Art. 246a EGBGB, проверено напрямую на gesetze-im-internet.de 22.06.2026), заполненный данными Propria GmbH. Используется без изменений формулировок закона — это даёт "Gesetzlichkeitsfiktion" (защиту от ошибок в содержании). AGB и Datenschutzerklärung — черновик не от юриста, перед публикацией рекомендуется быстрая проверка у Steuerberater/Anwalt (особенно разделы Haftung и Gerichtsstand).

### Применимость Widerrufsrecht к бизнесу Propria

Договоры заключаются через переписку (Kleinanzeigen/WhatsApp) без личной встречи в момент заключения сделки → Fernabsatzvertrag (§312c BGB), либо переговоры частично на территории клиента → außerhalb von Geschäftsräumen (§312b BGB). В обоих случаях действует gesetzliches Widerrufsrecht (§312g BGB). Подписание документов на месте у клиента **не избегает** этого — наоборот, это классический случай "außerhalb von Geschäftsräumen".

Решение для горящих сроков (типично у нас: кухня привезена, монтаж нужен через 1 день) — пункт о явном согласии клиента на немедленное начало работ, см. ниже.

---

### 1. Widerrufsbelehrung (Dienstleistungsvertrag, Propria GmbH)

```
Widerrufsbelehrung

Widerrufsrecht

Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.

Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsabschlusses.

Um Ihr Widerrufsrecht auszuüben, müssen Sie uns

Propria GmbH
Potsdamer Straße 92
10785 Berlin
Telefon: 0177 8192313
E-Mail: info@propria.gmbh

mittels einer eindeutigen Erklärung (z. B. ein mit der Post versandter Brief oder eine E-Mail) über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren. Sie können dafür das beigefügte Muster-Widerrufsformular verwenden, das jedoch nicht vorgeschrieben ist.

Zur Wahrung der Widerrufsfrist reicht es aus, dass Sie die Mitteilung über die Ausübung des Widerrufsrechts vor Ablauf der Widerrufsfrist absenden.

Folgen des Widerrufs

Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf dieses Vertrags bei uns eingegangen ist. Für diese Rückzahlung verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen wurde ausdrücklich etwas anderes vereinbart; in keinem Fall werden Ihnen wegen dieser Rückzahlung Entgelte berechnet.

Haben Sie verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen soll, so haben Sie uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu dem Sie uns von der Ausübung des Widerrufsrechts hinsichtlich dieses Vertrags unterrichten, bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen Dienstleistungen entspricht.

Ende der Widerrufsbelehrung
```

Источник: Anlage 1 zu Art. 246a § 1 Abs. 2 Satz 2 EGBGB, https://www.gesetze-im-internet.de/bgbeg/art_253anlage_1.html (Variante a — Dienstleistungsvertrag, Fristbeginn = Vertragsabschluss).

---

### 2. Muster-Widerrufsformular

```
Muster-Widerrufsformular

(Wenn Sie den Vertrag widerrufen wollen, dann füllen Sie bitte dieses Formular aus und senden Sie es zurück.)

An:
Propria GmbH
Potsdamer Straße 92
10785 Berlin
E-Mail: info@propria.gmbh

Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über die Erbringung der folgenden Dienstleistung:

_____________________________________________

Bestellt am (*): _______________

Name des/der Verbraucher(s): _______________

Anschrift des/der Verbraucher(s): _______________

Unterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier): _______________

Datum: _______________

(*) Unzutreffendes streichen.
```

Источник: Anlage 2 zu Art. 246a § 1 Abs. 2 Satz 1 Nr. 1 und § 2 Abs. 2 Nr. 2 EGBGB, https://www.gesetze-im-internet.de/bgbeg/art_253anlage_2.html

---

### 3. Klausel: Ausdrückliche Zustimmung zum vorzeitigen Beginn (für Angebot/Auftragsbestätigung)

Не официальный Muster-текст (закон не предусматривает готовую формулировку для этого пункта), но содержание точно соответствует требованиям § 356 Abs. 4 BGB: явное согласие на начало работ + подтверждение знания об утрате права на отказ при полном завершении. Добавлять в Angebot/Auftragsbestätigung, когда сроки горящие (типичный случай: доставка кухни → монтаж на следующий день):

```
Ausdrückliche Zustimmung zum vorzeitigen Vertragsbeginn

Ich stimme ausdrücklich zu, dass Propria GmbH mit der Ausführung der beauftragten Dienstleistung bereits vor Ablauf der 14-tägigen Widerrufsfrist beginnt.

Mir ist bekannt, dass ich mein Widerrufsrecht verliere, sobald die Dienstleistung durch Propria GmbH vollständig erbracht wurde.

Datum, Unterschrift Kunde: _______________
```

**Применение:** клиент подписывает/подтверждает это явно (бумага на месте или явное "Ja, ich stimme zu" в переписке) до начала монтажа — устного согласия недостаточно. По судебной практике это согласие должно быть обособленным, не "спрятанным" среди прочих пунктов — оформлять отдельной строкой с собственной подписью/явным "Ja", не как один из пунктов общего текста.

**Привязка AGB к договору:** AGB становятся частью договора только при явной отсылке + предоставлении текста клиенту. Наличия AGB в профиле Kleinanzeigen недостаточно. В каждое Angebot (как у Georgia, угебот-026) добавлять строку: "Es gelten die beigefügten AGB" и прикладывать PDF/текст AGB к Angebot.

---

### 6. Klausel: Haftung bei Schäden (для Angebot, между "Gewährleistung" и "Datenschutz")

Повод: клиент (Georgia, 21.06.2026) спросил в WhatsApp, что будет, если что-то пойдёт не так — придётся ли самой заказывать и платить за детали заново. Ответ был дан вручную ("если ошибка с нашей стороны — мы покрываем расходы"). Эта формулировка ничего не добавляет к уже существующей ответственности по AGB п.9 (Haftung) и п.12 (verborgene Mängel) — просто делает её видимой в Angebot заранее, что снимает главный страх клиента и работает на конверсию без расширения обязательств.

```
Haftung bei Schäden
Sollte während der Montage ein Schaden durch einen Fehler unsererseits entstehen,
übernehmen wir die Kosten für Ersatzteile und deren Nachbestellung. Ausgenommen
sind Schäden durch verborgene Mängel der vorhandenen Bausubstanz (siehe AGB Punkt 12).
```

**Важно:** не обещать больше, чем AGB п.9/12 — ответственность только за собственный Fehler (Verschulden), не за скрытые дефекты стены/проводки.

---

### 4. AGB (Allgemeine Geschäftsbedingungen) — минимальная версия, Propria GmbH

```
Allgemeine Geschäftsbedingungen (AGB) der Propria GmbH

1. Geltungsbereich
Diese AGB gelten für alle Verträge zwischen der Propria GmbH (Potsdamer Straße 92, 10785 Berlin) und ihren Kunden über die Erbringung von Montage- und Handwerksleistungen (insbesondere Küchen- und Möbelmontage).

2. Vertragsschluss
Der Vertrag kommt durch Annahme des von Propria GmbH übermittelten Angebots zustande, spätestens mit Zahlung der vereinbarten Anzahlung durch den Kunden.

3. Leistungsumfang
Der Leistungsumfang ergibt sich aus dem jeweiligen Angebot. Nicht im Leistungsumfang enthalten sind, sofern nicht ausdrücklich im Angebot vereinbart:
- Elektroarbeiten, die eine Elektrofachkraft erfordern (Festanschluss von Geräten, Arbeiten am Sicherungskasten, Einrichten neuer Steckdosen)
- Gasarbeiten, die eine zugelassene Fachkraft erfordern
- Bauliche Veränderungen (Versetzen von Wänden, Fenstern, Türen)
- Sanitärarbeiten außer dem Anschluss an bereits vorhandene Wasseranschlüsse
- Dekorative Arbeiten (Fliesen, Verputzen, Streichen, Bodenverlegung)
- Demontage und Entsorgung der Altküche, sofern nicht separat vereinbart

4. Preise und Zahlung
Es gilt der im Angebot genannte Festpreis. Bei Auftragsbestätigung ist eine Anzahlung von 20 % fällig, der Restbetrag nach Fertigstellung der Arbeiten.

5. Mitwirkungspflichten des Kunden
Der Kunde stellt sicher, dass der Arbeitsbereich am vereinbarten Termin zugänglich, beräumt und mit den notwendigen Anschlüssen (Strom, Wasser) versehen ist. Verzögerungen aufgrund fehlender Mitwirkung gehen nicht zu Lasten von Propria GmbH.

6. Termine
Vereinbarte Termine sind verbindlich. Eine feste Terminreservierung erfolgt erst nach Eingang der Anzahlung.

7. Stornierung
Bei Stornierung weniger als 48 Stunden vor dem vereinbarten Termin verbleibt die Anzahlung als Entschädigung für die Terminblockade. Bei Stornierung mehr als 48 Stunden vor dem Termin wird die Anzahlung vollständig zurückerstattet. Verschiebt sich der Termin nach Eingang der Anzahlung aus Gründen, die der Kunde nicht zu vertreten hat (z. B. Lieferverzögerung), erhält der Kunde ein Vorrangrecht auf die nächstmöglichen freien Termine.

8. Gewährleistung
Es gilt die gesetzliche Gewährleistung gemäß § 634a BGB (2 Jahre auf Werkleistungen).

9. Haftung
Propria GmbH haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit sowie bei Verletzung des Lebens, des Körpers oder der Gesundheit. Bei leichter Fahrlässigkeit haftet Propria GmbH nur bei Verletzung wesentlicher Vertragspflichten, begrenzt auf den nach Art des Vertrags vorhersehbaren, typischen Schaden.

10. Widerrufsrecht
Verbrauchern steht ein gesetzliches Widerrufsrecht gemäß der gesondert mitgeteilten Widerrufsbelehrung zu.

11. Material und Werkzeug
Sofern im Angebot nicht anders vereinbart, stellt der Kunde die zu montierenden Möbel/Küchenteile sowie ggf. Verbrauchsmaterial (z. B. Silikon) bereit. Werkzeug wird, sofern nicht anders vereinbart, von Propria GmbH gestellt.

12. Verborgene Mängel der Bausubstanz
Propria GmbH haftet nicht für Schäden, die auf nicht erkennbare, verborgene Mängel der vorhandenen Bausubstanz zurückzuführen sind (z. B. unbekannte Leitungsführung in der Wand), sofern diese bei sachgerechter Ausführung der Arbeiten nicht erkennbar waren.

13. Schlussbestimmungen
Sollte eine Bestimmung dieser AGB unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt. Es gilt deutsches Recht. Zwingende gesetzliche Verbraucherschutzvorschriften, insbesondere zum Gerichtsstand, bleiben unberührt.
```

---

### 5. Datenschutzerklärung — минимальная версия, Propria GmbH

```
Datenschutzerklärung

1. Verantwortlicher
Propria GmbH
Potsdamer Straße 92, 10785 Berlin
E-Mail: info@propria.gmbh
Telefon: 0177 8192313

2. Welche Daten wir verarbeiten
Im Rahmen der Auftragsabwicklung verarbeiten wir: Name, Adresse, Telefonnummer, E-Mail-Adresse, von Ihnen übermittelte Fotos und Planungsunterlagen zu Ihrer Küche/Wohnung, sowie Zahlungsdaten (Rechnungsdaten, keine Kartendaten).

3. Zweck und Rechtsgrundlage
Die Verarbeitung erfolgt zur Erfüllung des mit Ihnen geschlossenen Vertrags bzw. zur Vorbereitung eines Angebots (Art. 6 Abs. 1 lit. b DSGVO) sowie zur Erfüllung gesetzlicher Aufbewahrungspflichten, insbesondere im Steuer- und Handelsrecht (Art. 6 Abs. 1 lit. c DSGVO).

4. Speicherdauer
Vertrags- und Rechnungsdaten werden gemäß gesetzlicher Aufbewahrungsfristen (i. d. R. 6–10 Jahre nach HGB/AO) gespeichert. Fotos und Planungsunterlagen werden nach Abschluss des Auftrags gelöscht, sofern keine Aufbewahrungspflicht besteht.

5. Weitergabe an Dritte
Ihre Daten werden ausschließlich zur Bearbeitung des Auftrags verwendet. Eine Weitergabe erfolgt nur an unseren Steuerberater zur Buchhaltung sowie, soweit gesetzlich vorgeschrieben, an Behörden. Eine darüber hinausgehende Weitergabe an Dritte findet nicht statt.

6. Kommunikation über Kleinanzeigen
Soweit die Kommunikation über die Plattform Kleinanzeigen erfolgt, gilt zusätzlich die Datenschutzerklärung von Kleinanzeigen für die Nutzung der Plattform selbst.

7. Kommunikation über WhatsApp
Für die Kommunikation mit Kunden nutzen wir WhatsApp Business (Anbieter: WhatsApp Ireland Limited, eine Tochtergesellschaft der Meta Platforms, Inc.). Wenn Sie uns über WhatsApp kontaktieren, werden Ihre Nachrichten und die dabei übermittelten Daten (z. B. Telefonnummer, Name, Fotos) zur Bearbeitung Ihrer Anfrage verarbeitet. Dabei kann es zu einer Datenübermittlung in die USA kommen. Die Nutzung erfolgt auf Grundlage Ihrer Einwilligung durch Kontaktaufnahme (Art. 6 Abs. 1 lit. a DSGVO) bzw. zur Vertragsanbahnung (Art. 6 Abs. 1 lit. b DSGVO). Es gelten zusätzlich die Datenschutzhinweise von WhatsApp/Meta.

8. Ihre Rechte
Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit sowie Widerspruch gegen die Verarbeitung Ihrer Daten. Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren, z. B. bei der Berliner Beauftragten für Datenschutz und Informationsfreiheit.

9. Automatisierte Entscheidungsfindung
Eine automatisierte Entscheidungsfindung einschließlich Profiling findet nicht statt.

10. Kontakt
Bei Fragen zum Datenschutz wenden Sie sich an: info@propria.gmbh
```

**Открытый вопрос:** AGB-раздел Haftung и Gerichtsstand, а также Datenschutz-Aufsichtsbehörde — рекомендуется проверить у Steuerberater/Anwalt перед публикацией, особенно если объём заказов вырастет.
