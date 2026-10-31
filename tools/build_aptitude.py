"""
Builds the Aptitude tree: one step per chapter of the guide, with its notes from the PDF and a large question bank.

Usage: python -I tools/build_aptitude.py "<folder with Aptitude_Mastery_Guide.pdf>"
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "aptitude")]

import pdfplumber  # noqa: E402

from build_roadmap import STAGE_COLORS, load_outline, nearest_parents  # noqa: E402
from core import TEMPLATES, HAND, build_chapter  # noqa: E402
from extract_topic import extract, front_matter  # noqa: E402
import figures, quant, reasoning, technical, verbal  # noqa: E402,F401
import computed_extra, grammar, judgement, verbal_more  # noqa: E402,F401

PDF = "Aptitude_Mastery_Guide.pdf"
OUT = HERE.parent / "content" / "roadmaps" / "aptitude"
ROW_SIZES = [1, 3, 5]
STAGES = {1: ("quant", "Quantitative aptitude", "Numbers, percentages, speed, work, algebra and more"),
          2: ("logical", "Logical reasoning", "Verbal and non-verbal reasoning"),
          3: ("verbal", "Verbal ability", "Grammar, vocabulary and comprehension"),
          4: ("data", "Data interpretation", "Tables, charts and caselets"),
          5: ("technical", "Technical aptitude", "Core computer science and code output")}
MIN_PER_TYPE = 80
WORKED_EXAMPLES = 5
SOURCE_NOTE = "Questions written for this site, not from your PDF. Computed topics have their answers worked out by code."


def split_notes(blocks):
    """One section per numbered sub-topic: the PDF text keeps them in one markdown block."""
    text = "\n\n".join(b["text"] if isinstance(b, dict) and b.get("type") == "markdown" else b if isinstance(b, str) else "" for b in blocks)
    text = re.sub(r"\n*### Part \d+:.*$", "", text, flags=re.S).strip()
    parts = re.split(r"(?m)^#### \d+\.\d+\.\d+ (.+)$", text)
    sections = []
    for i in range(1, len(parts), 2):
        sid = re.sub(r"[^a-z0-9]+", "-", parts[i].lower()).strip("-")
        sections.append({"id": sid, "type": "concept", "title": parts[i].strip(), "blocks": [{"type": "markdown", "text": parts[i + 1].strip()}]})
    return sections or [{"id": "notes", "type": "concept", "title": "Notes", "blocks": [{"type": "markdown", "text": text}]}]


def load_notes():
    """tools/aptitude/notes/*.md: "# Chapter", then "## Sub-topic" with deeper notes written for this site."""
    notes = {}
    for path in sorted((HERE / "aptitude" / "notes").glob("*.md")):
        chapter = topic = None
        for line in path.read_text(encoding="utf-8").split("\n"):
            if line.startswith("# "):
                chapter = line[2:].strip()
            elif line.startswith("## "):
                topic = line[3:].strip()
                notes[(chapter, topic)] = []
            elif topic:
                notes[(chapter, topic)].append(line)
    return {k: "\n".join(v).strip() for k, v in notes.items()}


def deepen(sections, chapter, items, notes):
    """Add the deeper notes and some worked examples to each sub-topic's section of PDF notes."""
    for section in sections:
        if section["id"] in ("practice", "about-this-guide"):
            continue
        title = section["title"]
        text = notes.pop((chapter, title), None)
        if text:
            section["blocks"].append({"type": "markdown", "text": "#### Going deeper\n\n*Written for this site, beyond your PDF.*\n\n" + text})
        examples = [i for i in items if i["t"] == title and "os" not in i and "svg" not in i][:WORKED_EXAMPLES]
        if examples:
            section["blocks"].append({"type": "markdown", "text": "#### Worked examples"})
            section["blocks"].append({"type": "questions", "items": [
                {"question": i["q"], "answer": f"**{i['o'][i['a']]}.** {i['w']}"} for i in examples]})


def main():
    folder = Path(sys.argv[1])
    parts, _ = load_outline(folder / PDF)
    OUT.joinpath("topics").mkdir(parents=True, exist_ok=True)
    categories, topics, report, seen_slugs = [], [], [], set()
    notes = load_notes()
    with pdfplumber.open(folder / PDF) as pdf:
        for number in sorted(parts):
            sid, title, description = STAGES[number]
            categories.append({"id": sid, "title": title, "description": description,
                               "color": STAGE_COLORS[(number - 1) % len(STAGE_COLORS)]})
            for key in sorted(parts[number]["chapters"]):
                ch = parts[number]["chapters"][key]
                name = ch["title"]
                slug = "apt-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                assert slug not in seen_slugs
                seen_slugs.add(slug)
                info = {"subtopics": [{"id": ch["num"].replace(".", "-"), "title": name, "pages": f"{ch['start']}-{ch['end']}"}],
                        "source": {"document": PDF, "pages": f"{ch['start']}-{ch['end']}"}}
                content, missing = extract(pdf, info)
                assert not missing, name
                pdf_notes = next(s for s in content["sections"] if s.get("subtopicId"))["blocks"]
                sections = split_notes(pdf_notes)
                assert name in TEMPLATES or name in HAND, name
                items, counts = build_chapter(name, MIN_PER_TYPE, MIN_PER_TYPE)
                deepen(sections, name, items, notes)
                sections.append({"id": "practice", "type": "practice", "title": f"Practice questions ({len(items)})",
                                 "blocks": [{"type": "callout", "variant": "note", "title": "About these questions", "text": SOURCE_NOTE},
                                            {"type": "mcq", "id": slug, "items": items}]})
                if not topics:
                    intro = front_matter(pdf, ch["start"])
                    if intro:
                        sections.insert(0, {"id": "about-this-guide", "type": "introduction", "title": "About this guide", "blocks": intro})
                (OUT / "topics" / f"{slug}.json").write_text(
                    json.dumps({"source": info["source"], "sections": sections}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
                topics.append({"id": slug, "title": name, "category": sid, "summary": f"{len(items)} practice questions · {description}",
                               "source": {**info["source"], "questions": len(items)}})
                report.append((name, len(items), counts))
    rows = []
    for c in categories:
        members = [t for t in topics if t["category"] == c["id"]]
        i = n = 0
        while i < len(members):
            size = ROW_SIZES[n % 3]
            rows.append(members[i:i + size])
            i += size
            n += 1
    for upper, lower in zip(rows, rows[1:]):
        for j, t in enumerate(lower):
            t["requires"] = nearest_parents(upper, len(lower), j)
    (OUT / "roadmap.json").write_text(json.dumps({
        "title": "Aptitude", "shortTitle": "Aptitude", "order": 3,
        "description": f"Quantitative, logical, verbal, data and technical aptitude, with {sum(r[1] for r in report)} practice questions and instant explanations.",
        "layout": "tree", "categories": categories, "topics": topics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if notes:
        print("NOTES NOT PLACED:", sorted(notes))
    for name, total, counts in report:
        print(f"{total:5}  {name}  |  " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    print(sum(r[1] for r in report), "questions")


if __name__ == "__main__":
    main()
