"""
Reads guides written for the site as Markdown: parts with chapters and practice, shaped like the PDF guides.

Source format (one file per part):
  @part <id> | <title> | <stage id>
  @more                       instead of @part: a file named NN-more-*.md adds chapters to part NN
  ## Chapter title            starts a chapter; ### and markdown tables work as usual
  ```mermaid Title            a diagram; ```java Title is a titled code block
  !tip Title :: text          a callout (note, tip, warning, important, interview, realworld)
  !keypoints a ;; b ;; c      a key points list
  ?? question                 a practice question; the next line is "=> answer"
"""
import re
from pathlib import Path

DOCUMENT = "Written for this site (not from your PDFs)"


def parse(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines[0].strip() == "@more":
        part = {"id": None, "chapters": []}
    else:
        head = lines[0].removeprefix("@part ").split("|")
        part = {"id": head[0].strip(), "title": head[1].strip(), "stage": head[2].strip(), "chapters": []}
    chapter, para, i = None, [], 1

    def flush():
        text = "\n".join(para).strip()
        para.clear()
        if text:
            chapter["blocks"].append({"type": "markdown", "text": text})

    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith("## "):
            if chapter:
                flush()
            chapter = {"title": line[3:].strip(), "blocks": [], "qa": []}
            part["chapters"].append(chapter)
        elif line.startswith("```") and line.strip() != "```":
            flush()
            bits = line[3:].split(None, 1)
            lang, title = bits[0], bits[1].strip() if len(bits) > 1 else None
            code = []
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            body = "\n".join(code)
            if lang == "mermaid":
                block = {"type": "diagram", "format": "mermaid", "code": body}
            else:
                block = {"type": "code", "language": lang, "code": body}
            if title:
                block["title"] = title
            chapter["blocks"].append(block)
        elif line.startswith("!keypoints "):
            flush()
            points = [p.strip() for p in line[len("!keypoints "):].split(";;")]
            chapter["blocks"].append({"type": "callout", "variant": "keypoints", "title": "Key points", "text": "\n".join(f"- {p}" for p in points)})
        elif re.match(r"!(note|tip|warning|important|interview|realworld) ", line):
            flush()
            variant, rest = line[1:].split(" ", 1)
            title, text = rest.split(" :: ", 1) if " :: " in rest else (None, rest)
            block = {"type": "callout", "variant": variant, "text": text.strip()}
            if title:
                block["title"] = title.strip()
            chapter["blocks"].append(block)
        elif line.startswith("?? "):
            flush()
            assert lines[i].startswith("=> "), line
            chapter["qa"].append({"question": line[3:].strip(), "answer": lines[i][3:].strip()})
            i += 1
        else:
            para.append(line)
    flush()
    return part


def load_parts(folder):
    """All parts of a guide folder, in file order; NN-more-*.md files extend the part before them."""
    parts = []
    # by number, the part itself first: "07-more-x" would otherwise sort before "07-routing"
    for path in sorted(Path(folder).glob("*.md"), key=lambda p: (p.name[:2], "-more" in p.name, p.name)):
        part = parse(path)
        if part["id"] is None:
            parts[-1]["chapters"] += part["chapters"]
        else:
            parts.append(part)
    return parts


def build_sections(part, n, notice):
    """-> (sections for the topic file, subtopics for the roadmap, word count)."""
    sections, practice, subtopics = [], [], []
    for k, ch in enumerate(part["chapters"], 1):
        sid = f"{n}-{k}"
        subtopics.append({"id": sid, "title": ch["title"]})
        blocks = ([notice] if k == 1 else []) + ch["blocks"]
        sections.append({"id": f"ch-{sid}", "type": "concept", "title": ch["title"], "subtopicId": sid, "blocks": blocks})
        if ch["qa"]:
            practice.append({"type": "markdown", "text": f"#### {ch['title']}"})
            practice.append({"type": "questions", "items": ch["qa"]})
    if practice:
        sections.append({"id": "practice", "type": "practice", "title": "Practice questions", "blocks": practice})
    words = sum(len(b.get("text", b.get("code", "")).split()) for c in part["chapters"] for b in c["blocks"])
    words += sum(len((q["question"] + q["answer"]).split()) for c in part["chapters"] for q in c["qa"])
    return sections, subtopics, words
