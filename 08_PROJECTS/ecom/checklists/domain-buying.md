# Чеклист покупки домена

## Шаг 1 — Поиск и фильтрация

- [ ] Скачать CSV с GoDaddy Auctions (или Sedo / Afternic)
- [ ] Прогнать `filter_domains.py` → сохранить `results.tsv`

```bash
python3 tools/filter_domains.py domains.tsv --age 1 --max-price 50 --out results.tsv
```

### Паттерны отбора (скрипт)

| Паттерн | Примеры | Метка |
|---|---|---|
| имя + союз + имя | soofandbloom, oliver-and-alder | `name+name` |
| нейтральный apparel-keyword | wearvestra, drylinewear | `apparel` |
| prefix + слово | bymayberry, theboden, maisonrose | `prefix+word` |
| слово + suffix | emblemboutique, almondmuse | `word+suffix` |
| два слова через дефис | ever-pretty, silk-bloom | `hyphen-pair` |
| одно слово 5-10 букв | azazie, boden, lunera | `single-word*` |

Домены с меткой `single-word*` — финальный отбор глазами (скрипт не может оценить "звучание").

## Шаг 2 — Проверка кандидатов

- [ ] RDAP: дата создания > 1 года, непрерывность (нет gap) — `curl https://rdap.verisign.com/com/v1/domain/ДОМЕН`
- [ ] ScamAdviser: score ≥ 75
- [ ] Google Safe Browsing: нет флага — transparencyreport.google.com/safe-browsing/search?url=ДОМЕН
- [ ] `site:ДОМЕН` в Google: 0 результатов
- [ ] Маркетинг: звучит по-английски без негатива, легко произносится, нет конкурентов с похожим именем
- [ ] Wayback (при сомнениях): web.archive.org — не было фармы, скама, adult, чужого бренда

## Шаг 3 — Покупка

- [ ] Дождаться результатов аукциона / купить напрямую
- [ ] Добавить в `domains-hotlist.md`
