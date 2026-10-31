"""
Builds the pages of the Kafka parts written for the site, from tools/kafka/*.md (see guide_source.py for the format).

The Kafka PDF has no chapters on the plain Java consumer, on consuming with Spring Kafka, or on testing and monitoring
Kafka applications. These parts fill that gap, and they say so. build_roadmap.py reads the same sources to list each
part's chapters and learning_path.json places each part among the PDF parts.

Usage: python -I tools/build_kafka_guide.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from guide_source import DOCUMENT, build_sections, load_parts  # noqa: E402

OUT = HERE.parent / "content" / "roadmaps" / "interview-prep" / "topics"
NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "Your Kafka guide has no chapters on this subject, so this part was written for the site, as of October 2026. "
                  "It follows the versions used in the rest of the Kafka guide (Kafka 4.x, Spring Boot 4.1, Spring for Apache Kafka 4.1) "
                  "and refers to its chapters by name. Defaults and class names change between releases: check the official "
                  "documentation of the version you run before relying on a detail."}


def main():
    total = 0
    for n, part in enumerate(load_parts(HERE / "kafka"), 1):
        sections, subtopics, words = build_sections(part, n, NOTICE)
        (OUT / f"{part['id']}.json").write_text(
            json.dumps({"source": {"document": DOCUMENT}, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total += words
        print(f"{words:6}  {part['title']}  ({len(subtopics)} chapters)")
    print(total, "words")


if __name__ == "__main__":
    main()
