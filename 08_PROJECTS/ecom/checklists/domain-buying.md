# Чеклист покупки домена

- [ ] 0. Найти домены на площадке (GoDaddy Auctions CSV / Sedo / Afternic)
- [ ] 1. Для GoDaddy CSV: прогнать `filter_domains.py` → сохранить `results.tsv`
- [ ] 2. Маркетинг: звучит по-английски без негатива, легко произносится, нет конкурентов с похожим именем
- [ ] 3. RDAP: дата создания > 1 года, непрерывность (нет gap) — `curl https://rdap.verisign.com/com/v1/domain/ДОМЕН`
- [ ] 4. ScamAdviser: score ≥ 75
- [ ] 5. Google Safe Browsing: нет флага — transparencyreport.google.com/safe-browsing/search?url=ДОМЕН
- [ ] 6. `site:ДОМЕН` в Google: 0 результатов
- [ ] 7. Wayback (при сомнениях): web.archive.org — не было фармы, скама, adult, чужого бренда
- [ ] 8. Дождаться результатов аукциона
