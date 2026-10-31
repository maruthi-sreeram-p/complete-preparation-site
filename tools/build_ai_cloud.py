"""
Builds the AI and Cloud tree from the guide sources in tools/ai_cloud/*.md: parts, chapters and practice, like the PDF guides.

See guide_source.py for the source format.

These pages are written for the site, not extracted from the user's PDFs, and they say so.

Usage: python -I tools/build_ai_cloud.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_roadmap import STAGE_COLORS, nearest_parents  # noqa: E402
from guide_source import DOCUMENT, build_sections, load_parts  # noqa: E402

SRC = HERE / "ai_cloud"
OUT = HERE.parent / "content" / "roadmaps" / "ai-cloud"
ROW_SIZES = [1, 3, 5]
STAGES = [("cloud", "Cloud: AWS", "From IAM and networking to a production deployment you can defend"),
          ("ai", "AI engineering", "How LLMs behave, Spring AI, RAG, agents, production and one portfolio project")]
NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "No guide of yours covers this subject, so this part was written for the site, as of October 2026. "
                  "Cloud services and AI libraries change quickly: check the official documentation before relying on a detail."}


def main():
    parts = load_parts(SRC)
    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "topics").glob("*.json"):
        old.unlink()
    categories = [{"id": s, "title": t, "description": d, "color": STAGE_COLORS[i]} for i, (s, t, d) in enumerate(STAGES)]
    topics, total = [], 0
    for n, part in enumerate(parts, 1):
        sections, subtopics, words = build_sections(part, n, NOTICE)
        source = {"document": DOCUMENT}
        (OUT / "topics" / f"{part['id']}.json").write_text(json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total += words
        topics.append({"id": part["id"], "title": part["title"], "category": part["stage"], "summary": f"{len(subtopics)} chapters", "subtopics": subtopics, "source": source})
        print(f"{words:6}  {part['title']}  ({len(subtopics)} chapters)")
    rows = []
    for c in categories:
        members = [t for t in topics if t["category"] == c["id"]]
        i = n = 0
        while i < len(members):
            rows.append(members[i:i + ROW_SIZES[n % 3]])
            i += ROW_SIZES[n % 3]
            n += 1
    for upper, lower in zip(rows, rows[1:]):
        for j, t in enumerate(lower):
            t["requires"] = nearest_parents(upper, len(lower), j)
    (OUT / "roadmap.json").write_text(json.dumps({
        "title": "AI and Cloud", "shortTitle": "AI and Cloud", "order": 2,
        "description": "AWS for Java developers, then AI engineering: LLMs, Spring AI, RAG, agents and one portfolio project. Best started once you can build a Spring Boot API.",
        "layout": "tree", "categories": categories, "topics": topics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total, "words")


if __name__ == "__main__":
    main()
