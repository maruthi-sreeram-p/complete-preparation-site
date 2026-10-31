"""
Builds the Frontend stage's pages from tools/frontend/*.md (see guide_source.py for the format).

These pages are written for the site, not extracted from the user's PDFs, and they say so.
build_roadmap.py reads the same sources to list each part's chapters.

Usage: python -I tools/build_frontend_guide.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from guide_source import DOCUMENT, build_sections, load_parts  # noqa: E402

OUT = HERE.parent / "content" / "roadmaps" / "interview-prep" / "topics"
NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "No guide of yours covers this subject, so this part was written for the site, as of October 2026. "
                  "Frontend libraries change quickly: check the official documentation before relying on a detail."}


def main():
    total = 0
    for n, part in enumerate(load_parts(HERE / "frontend"), 1):
        sections, subtopics, words = build_sections(part, n, NOTICE)
        (OUT / f"{part['id']}.json").write_text(
            json.dumps({"source": {"document": DOCUMENT}, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total += words
        print(f"{words:6}  {part['title']}  ({len(subtopics)} chapters)")
    print(total, "words")


if __name__ == "__main__":
    main()
