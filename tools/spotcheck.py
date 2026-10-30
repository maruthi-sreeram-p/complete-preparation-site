"""
Compares a converted topic with the PDF text it came from and reports where they differ.

For every chapter it takes the words of the PDF page range (pdftotext) and the words of the converted section,
and looks for runs of PDF words that are missing from the output ("dropped text") and runs of output words that
are not in the PDF ("extra text"). Runs near the start or end of a page range are usually the neighbouring
chapter and are ignored.

Usage:
  python -I tools/spotcheck.py <folder with the PDFs> <topic-id-prefix>... [--min-run 8]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content" / "roadmaps" / "interview-prep"
N = 4  # n-gram size
SHOW = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 3


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def block_text(b):
    t = b["type"]
    if t == "markdown" or t == "callout":
        return b["text"]
    if t == "code":
        return b.get("title", "") + " " + b["code"]
    if t == "table":
        return " ".join(b["headers"]) + " " + " ".join(" ".join(r) for r in b["rows"]) + " " + b.get("caption", "")
    if t == "questions":
        return " ".join(i["question"] + " " + i.get("answer", "") for i in b["items"])
    if t == "diagram":
        return (b.get("alt", "") + " " + b.get("caption", "")) if b.get("format") == "svg" else b.get("code", "")
    if t == "figure":
        return " ".join(b["labels"]) + " " + b["caption"]
    return ""


def pdf_text(pdf, first, last):
    out = subprocess.run(["pdftotext", "-f", str(first), "-l", str(last), str(pdf), "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    keep = []
    for line in out.splitlines():
        if re.search(r"\bPage \d+\s*$", line) or re.match(r"^\s*PART \d+:", line) or line.strip() == "sreeram":
            continue
        keep.append(line)
    return "\n".join(keep)


def runs(seq, other_grams, min_run):
    """Maximal runs of positions in seq whose n-gram is not in other_grams."""
    found, start = [], None
    for i in range(len(seq) - N + 1):
        gram = tuple(seq[i:i + N])
        if gram not in other_grams:
            start = i if start is None else start
        elif start is not None:
            found.append((start, i + N - 1))
            start = None
    if start is not None:
        found.append((start, len(seq)))
    return [(a, b) for a, b in found if b - a >= min_run]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    min_run = int(sys.argv[sys.argv.index("--min-run") + 1]) if "--min-run" in sys.argv else 8
    if "--min-run" in sys.argv:
        args = [a for a in args if a != str(min_run)]
    if "--show" in sys.argv:
        args = [a for a in args if a != str(SHOW)]
    folder, prefixes = Path(args[0]), args[1:]
    roadmap = json.loads((ROOT / "roadmap.json").read_text(encoding="utf-8"))

    for topic in roadmap["topics"]:
        if not any(topic["id"].startswith(p) for p in prefixes) or not topic.get("subtopics"):
            continue
        content = json.loads((ROOT / "topics" / f"{topic['id']}.json").read_text(encoding="utf-8"))
        sections = {s.get("subtopicId"): s for s in content["sections"]}
        practice = " ".join(block_text(b) for s in content["sections"] if s["id"] == "practice" for b in s["blocks"])
        print(f"\n=== {topic['id']}  ({topic['title']})")
        for sub in topic["subtopics"]:
            first, last = sub["pages"].split("-")
            is_last = sub is topic["subtopics"][-1]
            pdf = tokens(pdf_text(folder / topic["source"]["document"], first, int(last) + (1 if is_last else 0)))
            section = sections.get(sub["id"])
            out = tokens(" ".join(block_text(b) for b in section["blocks"]) if section else "")
            both = out + tokens(practice)  # questions of every chapter live in the topic's Practice section
            out_grams = {tuple(both[i:i + N]) for i in range(len(both) - N + 1)}
            pdf_grams = {tuple(pdf[i:i + N]) for i in range(len(pdf) - N + 1)}
            cover = sum(1 for i in range(len(pdf) - N + 1) if tuple(pdf[i:i + N]) in out_grams) / max(1, len(pdf) - N + 1)

            dropped = [(a, b) for a, b in runs(pdf, out_grams, min_run) if 0.13 < a / len(pdf) and b / len(pdf) < (0.97 if is_last else 0.88)]
            extra = runs(out, pdf_grams, min_run)
            flag = "  <-- CHECK" if cover < 0.9 or dropped or len(extra) > 3 else ""
            print(f"- {sub['id']} {sub['title'][:48]:48} words pdf={len(pdf):5} out={len(out):5} cover={cover:.0%} "
                  f"dropped-runs={len(dropped)} extra-runs={len(extra)}{flag}")
            for a, b in sorted(dropped, key=lambda r: r[0] - r[1])[:SHOW]:
                print(f"    dropped {b - a:3}w @{a * 100 // len(pdf)}%: {' '.join(pdf[a:a + 40])} ...")
            for a, b in sorted(extra, key=lambda r: r[0] - r[1])[:SHOW]:
                print(f"    extra   {b - a:3}w: {' '.join(out[a:a + 40])} ...")


if __name__ == "__main__":
    main()
