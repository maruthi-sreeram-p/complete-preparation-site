"""
Builds the GATE CS 2027 tree from tools/gate/: detailed notes with cheat codes, plus MCQs checked at build time.

  tools/gate/NN-<topic>.md        notes, in the guide format of guide_source.py (use !cheat for cheat codes)
  tools/gate/mcq/NN-<topic>.txt   multiple-choice questions, format below
  tools/gate/helpers.py           names available to the !py checks

Question format (one block per question, blank line between blocks):

  ?2 [Cache mapping] Stem in markdown; fenced code and tables work, so do several lines.
  (a) a wrong option
  (b)* the correct option          exactly one option carries the *
  (c) another wrong option
  (d) another wrong option
  => Why it is right, and the trap in the others. May continue on the next lines.
  !fixed                           optional: keep the written order of the options (statements I/II, "both")
  !py assert num(ans) == 128      optional check run at build time; `ans` is the correct option, `opts` all four.
                                   Lines after "!py" continue the code until the next blank line.

?1 / ?2 is the marks the question would carry in GATE. [Label] groups questions under a chip in the page.
Options are shuffled (deterministically) unless !fixed is given, so the right answer is not always in the same place.
These questions are written for the site in the style of GATE. They are not copies of past papers.

Usage: python -I tools/build_gate.py
"""
import json
import random
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "gate"))
from build_roadmap import STAGE_COLORS, nearest_parents  # noqa: E402
from guide_source import build_sections, load_parts  # noqa: E402
import helpers  # noqa: E402

SRC = HERE / "gate"
OUT = HERE.parent / "content" / "roadmaps" / "gate-cs"
DOCUMENT = "Written for this site against the official GATE 2027 CS syllabus (IIT Madras)"
NOTICE = {"type": "callout", "variant": "note", "title": "About this page",
          "text": "Written for this site against the official GATE 2027 CS syllabus from IIT Madras. The questions are original and in the style of GATE: "
                  "they drill the concepts GATE repeats, they are not copies of past papers. If the official syllabus changes, the official PDF wins."}

STAGES = [("start", "Start here", "Exam pattern, marking scheme, strategy and General Aptitude"),
          ("math", "Engineering Mathematics", "Discrete maths, probability, linear algebra and calculus (about 13 marks)"),
          ("hardware", "Digital Logic and Architecture", "Boolean logic, circuits, caches, pipelines"),
          ("software", "Programming, Algorithms and Theory", "C, data structures, algorithms, automata, compilers"),
          ("systems", "Systems", "Operating systems, databases and computer networks")]

# id -> weightage shown on the node (rough averages of recent papers)
WEIGHT = {
    "gate-start": "15 marks (General Aptitude)",
    "gate-discrete-maths": "about 5 marks",
    "gate-probability": "about 3 marks",
    "gate-linear-algebra": "about 3 marks",
    "gate-calculus": "about 2 marks",
    "gate-digital-logic": "about 6 marks",
    "gate-coa": "about 9 marks",
    "gate-programming-ds": "about 10 marks",
    "gate-algorithms": "about 7 marks",
    "gate-toc": "about 8 marks",
    "gate-compiler": "about 6 marks",
    "gate-os": "about 8 marks",
    "gate-dbms": "about 7 marks",
    "gate-networks": "about 8 marks",
}

# The study order, one row of the tree per line. A row never mixes stages, and each row follows the one above it
# (the tree layout puts a heading wherever a row's stage changes, so the stages must stay contiguous).
ROWS = [["gate-start"],
        ["gate-discrete-maths"],
        ["gate-probability", "gate-linear-algebra", "gate-calculus"],
        ["gate-digital-logic"],
        ["gate-coa"],
        ["gate-programming-ds"],
        ["gate-algorithms", "gate-toc", "gate-compiler"],
        ["gate-os"],
        ["gate-dbms", "gate-networks"]]

QUESTION = re.compile(r"^\?([12]) \[([^\]]+)\] ?(.*)$")
OPTION = re.compile(r"^\(([a-d])\)(\*?) (.*)$")


def fail(path, line, message):
    sys.exit(f"{path.name}:{line}: {message}")


def parse_questions(path, names=helpers, tag_for=lambda marks: f"*({marks} mark{'s' if marks == 2 else ''})*"):
    """-> list of question dicts, checked and with the options in their final order.

    `names` is the module whose names the !py checks can use; `tag_for(marks)` is the italic prefix of the stem
    (build_cyber.py reuses this parser with its own checks and levels instead of marks)."""
    raw, cur, mode = [], None, None

    def finish():
        if cur:
            raw.append(cur)

    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        m = QUESTION.match(line)
        if m:
            finish()
            cur = {"line": number, "marks": int(m[1]), "label": m[2].strip(), "stem": [m[3]], "opts": [], "right": None,
                   "why": [], "py": [], "fixed": False}
            mode = "stem"
            continue
        if cur is None:
            if line.strip() and not line.startswith("#"):
                fail(path, number, "text before the first question")
            continue
        opt = OPTION.match(line)
        if opt and mode in ("stem", "opts"):
            mode = "opts"
            if opt[2]:
                if cur["right"] is not None:
                    fail(path, number, "two options are marked correct")
                cur["right"] = len(cur["opts"])
            cur["opts"].append(opt[3].strip())
        elif line.startswith("=> ") and mode == "opts":
            mode = "why"
            cur["why"].append(line[3:])
        elif line.strip() == "!fixed":
            cur["fixed"] = True
            mode = None
        elif line.startswith("!py"):
            mode = "py"
            if line[3:].strip():
                cur["py"].append(line[3:].strip())
        elif mode == "py" and line.strip():
            cur["py"].append(line)
        elif not line.strip():
            if mode in ("why", "py"):
                mode = None
        elif mode == "stem":
            cur["stem"].append(line)
        elif mode == "why":
            cur["why"].append(line)
        else:
            fail(path, number, f"unexpected line: {line[:60]!r}")
    finish()

    # Right answers are spread evenly over A-D: a shuffled, repeating schedule of target positions per file.
    slots = [i % 4 for i in range(sum(1 for q in raw if not q["fixed"]))]
    random.Random(zlib.crc32(path.name.encode())).shuffle(slots)
    out = []
    for q in raw:
        where = q["line"]
        if len(q["opts"]) != 4 or len(set(q["opts"])) != 4:
            fail(path, where, "needs four different options")
        if q["right"] is None:
            fail(path, where, "no option is marked with *")
        if not q["why"]:
            fail(path, where, "no explanation (=>)")
        right_text = q["opts"][q["right"]]
        if q["py"]:
            namespace = dict(vars(names), ans=right_text, opts=list(q["opts"]))
            try:
                exec("\n".join(q["py"]), namespace)
            except Exception as error:  # noqa: BLE001 - report which question failed
                fail(path, where, f"check failed ({type(error).__name__}: {error})")
        options = list(q["opts"])
        if not q["fixed"]:  # shuffled, so the position of the right answer gives nothing away
            others = [o for o in options if o != right_text]
            random.Random(zlib.crc32("\n".join(q["stem"]).encode())).shuffle(others)
            options = others[:]
            options.insert(slots.pop(), right_text)
        stem = "\n".join(q["stem"]).strip()
        tag = tag_for(q["marks"])
        out.append({"t": q["label"], "q": f"{tag}\n\n{stem}" if stem.startswith("```") else f"{tag} {stem}",
                    "o": options, "a": options.index(right_text), "w": "\n".join(q["why"]).strip()})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parts = load_parts(SRC)
    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "topics").glob("*.json"):
        old.unlink()
    categories = [{"id": s, "title": t, "description": d, "color": STAGE_COLORS[i]} for i, (s, t, d) in enumerate(STAGES)]
    topics, total_words, total_questions = [], 0, 0
    for n, part in enumerate(parts, 1):
        sections, subtopics, words = build_sections(part, n, NOTICE)
        written = sections.pop() if sections and sections[-1]["id"] == "practice" else None
        questions_file = next(SRC.glob(f"mcq/??-{part['id'].removeprefix('gate-')}.txt"), None)
        count, spread = 0, ""
        if questions_file:
            items = parse_questions(questions_file)
            count = len(items)
            spread = " answers A/B/C/D: " + "/".join(str(sum(1 for i in items if i["a"] == k)) for k in range(4))
            labels = list(dict.fromkeys(i["t"] for i in items))
            subtopics.append({"id": f"{n}-mcq", "title": f"MCQ practice ({count} questions)"})
            sections.append({"id": "mcq", "type": "practice", "title": f"MCQ practice ({count} questions)", "subtopicId": f"{n}-mcq", "blocks": [
                {"type": "markdown", "text": f"{count} original GATE-style questions on {len(labels)} areas. Pick an answer to see why it is right and which trap catches people. "
                                             "The marks shown are what a question like this would carry in GATE; in the real exam a wrong 1-mark MCQ costs 1/3 mark and a wrong 2-mark MCQ costs 2/3."},
                {"type": "mcq", "id": part["id"], "items": items}]})
        if written:
            sections.append(written)
        source ={"document": DOCUMENT, **({"questions": count} if count else {})}
        (OUT / "topics" / f"{part['id']}.json").write_text(json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total_words += words
        total_questions += count
        topics.append({"id": part["id"], "title": part["title"], "category": part["stage"],
                       "summary": f"{WEIGHT[part['id']]}" + (f" · {count} practice questions" if count else "") + " · cheat codes",
                       "subtopics": subtopics, "source": source, "estimatedMinutes": max(30, round((words / 170 + count * 1.5) / 5) * 5)})
        print(f"{words:6} words {count:4} questions  {part['title']}{spread}")
    by_id = {t["id"]: t for t in topics}
    missing = set(WEIGHT) - set(by_id)
    if missing:
        sys.exit(f"no notes file for {sorted(missing)}")
    if sorted(i for row in ROWS for i in row) != sorted(by_id):
        sys.exit("ROWS must list every topic exactly once")
    for row in ROWS:
        if len({by_id[i]["category"] for i in row}) != 1:
            sys.exit(f"a row mixes stages: {row}")
    for upper, lower in zip(ROWS, ROWS[1:]):
        for j, tid in enumerate(lower):
            by_id[tid]["requires"] = nearest_parents([by_id[i] for i in upper], len(lower), j)
    topics = [by_id[i] for row in ROWS for i in row]
    (OUT / "roadmap.json").write_text(json.dumps({
        "title": "GATE CSE 2027", "shortTitle": "GATE CSE", "order": 5,
        "description": f"Every section of the GATE 2027 Computer Science and Information Technology syllabus: detailed notes, cheat codes for quick solving "
                       f"and {total_questions} original GATE-style questions with explanations. Follows the official syllabus from IIT Madras.",
        "layout": "tree", "categories": categories, "topics": topics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total_words, "words,", total_questions, "questions")


if __name__ == "__main__":
    main()
