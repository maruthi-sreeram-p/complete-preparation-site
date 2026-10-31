"""Helpers for the mock-interview question sets (days 53-55). Written for this site, not taken from the PDFs."""

WRITTEN_FOR_SITE = (
    "*Written for this site (not from your PDFs).* The answers are model answers: read the question, "
    "say your own answer out loud, then press **Show answer** and compare. Do not memorise the wording."
)


def q(level, question, answer, hint=None):
    item = {"question": question, "answer": answer.strip(), "difficulty": level}
    if hint:
        item["hint"] = hint
    return item


def section(sid, title, intro, items, kind="practice"):
    return {
        "id": sid,
        "type": kind,
        "title": title,
        "blocks": [
            {"type": "markdown", "text": intro},
            {"type": "questions", "items": items},
        ],
    }


def info(sid, title, text, kind="introduction"):
    return {"id": sid, "type": kind, "title": title, "blocks": [{"type": "markdown", "text": text}]}
