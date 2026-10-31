"""
Helpers for writing pages in Python, used by build_experience_topics.py.
The Frontend pages themselves now come from tools/frontend/ (see build_frontend_guide.py).
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "roadmaps" / "interview-prep" / "topics"
SOURCE = {"document": "Written for this site (not from your PDFs)"}
NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "Your PDFs do not cover this topic, so this page was written for the site. Your 12-week plan lists "
                  "React, hooks, rendering, performance, state management and TypeScript. Check it against the "
                  "official documentation, or give me a PDF to replace it."}


def code(language, text, title=None, walkthrough=None):
    block = {"type": "code", "language": language, "code": text.strip("\n")}
    if title:
        block["title"] = title
    if walkthrough:
        block["walkthrough"] = walkthrough
    return block


def note(variant, title, text):
    return {"type": "callout", "variant": variant, "title": title, "text": text}


def interview(text):
    return note("interview", "Interview angle", text)


def keypoints(*points):
    return note("keypoints", "Key points", "\n".join(f"- {p}" for p in points))


def table(headers, rows, caption=None):
    block = {"type": "table", "headers": headers, "rows": rows}
    if caption:
        block["caption"] = caption
    return block


def diagram(title, source, caption=None, components=None):
    block = {"type": "diagram", "format": "mermaid", "title": title, "code": source.strip("\n")}
    if caption:
        block["caption"] = caption
    if components:
        block["components"] = components
    return block


def practice(*pairs):
    return {"id": "practice", "type": "practice", "title": "Practice questions",
            "blocks": [{"type": "questions", "items": [{"question": q, "answer": a} for q, a in pairs]}]}


def section(sid, kind, title, *blocks):
    return {"id": sid, "type": kind, "title": title, "blocks": list(blocks)}
