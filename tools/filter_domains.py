#!/usr/bin/env python3
"""
filter_domains.py — фильтрует CSV с аукциона GoDaddy под критерии GMC.

Критерии:
  - .com домен
  - Возраст >= MIN_AGE лет
  - Паттерн: имя+имя (word-and-word, wordandword, word-word) или нейтральный apparel

Запуск:
  python3 tools/filter_domains.py domains.tsv
  python3 tools/filter_domains.py domains.tsv --age 1 --max-price 50 --out results.tsv
"""

import sys
import csv
import re
import argparse

APPAREL_KEYWORDS = [
    "wear", "apparel", "fashion", "outfit", "boutique", "clothing",
    "wardrobe", "couture", "garment",
]

# Имена — популярные короткие (4-8 букв, нет цифр, нет спецсимволов)
NAMES = {
    # Короткие имена
    "adam", "alex", "alice", "amber", "amy", "anna", "anne", "ben", "blake",
    "carl", "cara", "charlie", "chris", "claire", "cole", "dana", "david",
    "diana", "drew", "eli", "ella", "ellie", "emma", "eric", "evan", "eve",
    "faye", "finn", "frank", "fred", "grace", "gray", "grey", "henry",
    "hugo", "iris", "ivan", "jack", "jake", "james", "jane", "jean", "jess",
    "joel", "john", "julia", "kate", "kyle", "laura", "leon", "lily", "lisa",
    "luca", "luke", "luna", "marc", "mark", "matt", "max", "maya", "mia",
    "mike", "milan", "milo", "nora", "noah", "neil", "nina", "noel", "oliver",
    "oscar", "paul", "peter", "phil", "quinn", "rob", "rose", "ross", "ryan",
    "sara", "sean", "sofia", "ted", "theo", "thomas", "tom", "vera", "will",
    "zara", "zoe",
    # Длинные / европейские
    "adler", "bennet", "bennett", "claude", "casa", "giannini",
    "francois", "pierre", "andre", "victor", "eleanor", "charlotte",
    "dominic", "dominique", "florence", "gabriel", "isabelle", "jasmine",
    "julian", "juliette", "leonora", "lorena", "lucien", "margaux",
    "margot", "mathieu", "nicolas", "raphael", "renaud", "sebastian",
    "simone", "sylvie", "valentin", "valerie", "vivienne", "william",
    "colette", "celeste", "aurelie", "bertrand", "camille", "delphine",
    "etienne", "fabrice", "gaston", "gilles", "helene", "jerome",
    "laurent", "mathilde", "maxime", "monique", "nathalie", "philippe",
    "sandrine", "thierry", "vincent", "xavier", "yves",
    # Фамилии-стиль
    "blackwood", "clifton", "dalton", "dawson", "fletcher", "griffin",
    "harlow", "hartley", "hunter", "kingsley", "lawson", "lawton",
    "lennox", "madison", "marlowe", "mercer", "merritt", "morgan",
    "morton", "pemberton", "porter", "prescott", "remington", "sterling",
    "stratton", "sutton", "thornton", "weston", "whitmore", "winston",
}

BLOCKLIST = {
    "swim", "swimwear", "swimsuit", "bikini", "surf", "beach", "pool",
    "kid", "kids", "baby", "toddler", "children", "maternity", "pregnancy",
    "gym", "fitness", "workout", "yoga", "sport", "sports", "athletic",
    "wedding", "bridal", "bride", "prom", "cosplay", "costume", "uniform",
    "plus", "curvy", "lingerie", "underwear", "socks",
    "church", "religious", "christian", "islamic",
    "urban", "ghetto", "trap", "thug", "drip",
    "sex", "adult", "xxx",
}


def looks_like_two_names(name: str) -> bool:
    """Два известных имени: word-and-word, wordandword, word-word."""
    def has_vowel(s):
        return bool(re.search(r'[aeiou]', s))

    candidates = []

    # word-and-word
    m = re.match(r'^([a-z]+)-and-([a-z]+)$', name)
    if m:
        candidates.append((m.group(1), m.group(2)))

    # разделители: and, et (фр), und (нем), y (исп), e (ит), n/n' (рок), de, von, van, le, la
    CONNECTORS = r'(?:and|et|und|von|van|de|le|la|n)'
    m = re.match(rf'^([a-z]{{3,14}})-and-([a-z]{{3,14}})$', name)
    if not m:
        m = re.match(rf'^([a-z]{{3,14}})-n-([a-z]{{3,14}})$', name)
    if m:
        candidates.append((m.group(1), m.group(2)))

    # wordCONNECTORword (слитно)
    m = re.match(rf'^([a-z]{{3,14}})({CONNECTORS})([a-z]{{3,14}})$', name)
    if m:
        candidates.append((m.group(1), m.group(3)))

    # word-word (через дефис без коннектора)
    m = re.match(r'^([a-z]{3,14})-([a-z]{3,14})$', name)
    if m:
        candidates.append((m.group(1), m.group(2)))

    for a, b in candidates:
        if a in NAMES and b in NAMES:
            return True

    # имя+имя слитно: перебираем все точки разбивки
    if re.match(r'^[a-z]{6,20}$', name):
        for i in range(3, len(name) - 2):
            a, b = name[:i], name[i:]
            if a in NAMES and b in NAMES:
                return True

    return False


def is_apparel(name: str) -> bool:
    return any(kw in name for kw in APPAREL_KEYWORDS)


def is_blocked(name: str) -> bool:
    return any(kw in name for kw in BLOCKLIST)


def passes_filter(name: str) -> bool:
    base = name.lower().replace(".com", "")
    if is_blocked(base):
        return False
    return is_apparel(base) or looks_like_two_names(base)


def main():
    parser = argparse.ArgumentParser(description="Filter GoDaddy domain CSV")
    parser.add_argument("input", help="Путь к TSV файлу")
    parser.add_argument("--age", type=int, default=1, help="Минимальный возраст домена (лет)")
    parser.add_argument("--max-price", type=float, default=999, help="Макс цена")
    parser.add_argument("--out", default=None, help="Файл для вывода (по умолчанию stdout)")
    args = parser.parse_args()

    results = []

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Domain Name", "").strip().lower()
            if not name.endswith(".com"):
                continue

            try:
                age = int(row.get("Domain Age", 0) or 0)
            except ValueError:
                age = 0
            if age < args.age:
                continue

            try:
                price = float(row.get("Price", 0) or 0)
            except ValueError:
                price = 0
            if price > args.max_price:
                continue

            # без цифр
            base = name.replace(".com", "")
            if re.search(r'\d', base):
                continue

            if not passes_filter(name):
                continue

            results.append({
                "domain": name,
                "age": age,
                "price": price,
                "tf": row.get("Majestic TF", ""),
                "end": row.get("Auction End Time", ""),
                "sale": row.get("Sale Type", ""),
                "reason": "apparel" if is_apparel(name.replace(".com", "")) else "name+name",
            })

    results.sort(key=lambda x: (-x["age"], -int(x["tf"] or 0)))

    out_fields = ["domain", "age", "price", "tf", "sale", "end", "reason"]

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(results)
        print(f"Сохранено: {len(results)} доменов → {args.out}")
    else:
        header = "\t".join(out_fields)
        print(header)
        print("-" * 80)
        for r in results:
            print("\t".join(str(r[f]) for f in out_fields))
        print(f"\nИтого: {len(results)} доменов")


if __name__ == "__main__":
    main()
