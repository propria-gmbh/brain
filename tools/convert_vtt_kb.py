#!/usr/bin/env python3
"""
Convert AB Inner Circle VTT transcripts to markdown knowledge base.
Groups by section number → one MD file per section.
Output: 08_PROJECTS/ecom/ab-inner-circle/
"""

import re
from pathlib import Path
from collections import defaultdict

VTT_DIR = Path("/Users/dister/Library/CloudStorage/GoogleDrive-ilja.disterheft@gmail.com/Shared drives/Propria/Dropshipping/Google Ads Masterclass")
OUT_DIR = Path(__file__).parent.parent / "08_PROJECTS/ecom/ab-inner-circle"

SECTION_NAMES = {
    "1": "Intro — What is Google Ads",
    "2": "Niches + Markets",
    "3": "Store Setup",
    "4": "Google Merchant Center",
    "5": "Launch Campaign",
    "6": "GMC Suspensions",
    "7": "Product Research + Import",
    "8": "Ads + Scaling",
    "9": "Advanced",
    "10": "Accounting + Banking",
    "11": "CNY + Seasonal",
}


def parse_vtt(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    seen = set()
    result = []
    for line in lines:
        line = line.strip()
        # Skip headers, timestamps, cue numbers, empty lines
        if not line:
            continue
        if line == "WEBVTT":
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        # Skip duplicate lines (VTT often repeats segments)
        if line in seen:
            continue
        seen.add(line)
        result.append(line)
    # Join and clean up spaces
    raw = " ".join(result)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def video_title(filename: str) -> str:
    # "4.5 How to delete a Google Merchant Center - Google Ads Masterclass · AB Inner Circle"
    name = Path(filename).stem
    name = re.sub(r"_en_English CC$", "", name)
    name = re.sub(r" - Google Ads Masterclass.*", "", name)
    return name.strip()


def section_num(filename: str) -> str:
    m = re.match(r"^(\d+)\.", Path(filename).name)
    return m.group(1) if m else "0"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    vtt_files = sorted(VTT_DIR.glob("*.vtt"))
    if not vtt_files:
        print("No VTT files found.")
        return

    sections = defaultdict(list)
    for f in vtt_files:
        sections[section_num(f.name)].append(f)

    index_lines = ["# AB Inner Circle — Google Ads Masterclass\n",
                   "База знаний из транскриптов видеокурса AB Inner Circle.\n",
                   "| Файл | Секция |\n|---|---|"]

    for sec in sorted(sections, key=lambda x: int(x)):
        files = sorted(sections[sec])
        sec_name = SECTION_NAMES.get(sec, f"Section {sec}")
        out_file = OUT_DIR / f"section-{sec.zfill(2)}-{sec_name.lower().replace(' ', '-').replace('+', 'and')[:40]}.md"

        lines = [f"# Section {sec}: {sec_name}\n"]
        for f in files:
            title = video_title(f.name)
            transcript = parse_vtt(f)
            lines.append(f"## {title}\n")
            lines.append(transcript + "\n")

        out_file.write_text("\n".join(lines), encoding="utf-8")
        index_lines.append(f"| [{out_file.name}]({out_file.name}) | {sec_name} |")
        print(f"  Section {sec}: {len(files)} videos → {out_file.name}")

    index_file = OUT_DIR / "README.md"
    index_file.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"\nDone. {len(vtt_files)} transcripts → {len(sections)} sections → {OUT_DIR}")


if __name__ == "__main__":
    main()
