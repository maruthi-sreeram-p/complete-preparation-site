"""
Builds the "Core Subjects" tree: Operating Systems, DBMS, Computer Networks, Computer Organisation and OOP.

  Operating Systems, Databases and Computer Networks are the deep guides of the Java Full Stack tree. They are not copied:
  each topic here points at the page in content/roadmaps/interview-prep/ (contentId "<roadmap>/<topic>"), so one guide is
  stored once and kept in one place. Progress is still tracked separately per tree.

  Computer Organisation and OOP are written for this tree:
    tools/core/NN-<part>.md        notes, in the guide format of guide_source.py (use !cheat for cheat codes)
    tools/core/mcq/NN-<part>.txt   multiple-choice questions, same format as the GATE tree (see tools/build_gate.py);
                                   ?1 is a recall question, ?2 is a problem or scenario question
    tools/core/core_helpers.py     names available to the !py checks, so a wrong answer key fails the build

Usage: python -I tools/build_core.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "core"))
from build_gate import parse_questions  # noqa: E402
from build_roadmap import STAGE_COLORS, nearest_parents  # noqa: E402
from guide_source import build_sections, load_parts  # noqa: E402
import core_helpers  # noqa: E402

SRC = HERE / "core"
OUT = HERE.parent / "content" / "roadmaps" / "core-subjects"
JAVA_TREE = HERE.parent / "content" / "roadmaps" / "interview-prep" / "roadmap.json"
DOCUMENT = "Written for this site (November 2026)"
NOTICE = {"type": "callout", "variant": "note", "title": "About this page",
          "text": "Written for this site as of November 2026 for a computer science student, in the style of the other guides. Examples use Java, with Python and "
                  "C++ where the languages differ. Worked numbers were checked by program. Where a vendor, a standard or a language version matters, "
                  "check the official source before relying on a detail."}
LEVEL_TAG = {1: "*(Recall)*", 2: "*(Problem)*"}

STAGES = [("os", "Operating Systems", "Processes, memory, concurrency, storage and the production playbook"),
          ("dbms", "Database Management Systems", "The relational model, SQL, indexes, transactions and scaling, then NoSQL"),
          ("cn", "Computer Networks", "From the link layer to TCP, HTTP, TLS and troubleshooting"),
          ("coa", "Computer Organisation and Architecture", "Logic, data representation, the CPU, pipelines, memory and I/O"),
          ("oop", "Object-Oriented Programming", "Classes, inheritance, design principles and OOP across languages")]

# Parts reused from the Java Full Stack tree: (id here, topic id there, stage)
REUSED = [(f"os-{n}", f"operating-systems-part-{n}", "os") for n in range(1, 7)] \
    + [(f"dbms-{n}", f"databases-part-{n}", "dbms") for n in (1, 2)] \
    + [(f"cn-{n}", f"computer-networks-part-{n}", "cn") for n in range(1, 7)]

# The study order, one row of the tree per line. A row never mixes stages (the tree layout draws a heading wherever a row's stage changes).
ROWS = [["os-1"], ["os-2"], ["os-3", "os-4"], ["os-5"], ["os-6"],
        ["dbms-1"], ["dbms-2"],
        ["cn-1"], ["cn-2"], ["cn-3"], ["cn-4", "cn-5"], ["cn-6"],
        ["coa-logic"], ["coa-data"], ["coa-cpu"], ["coa-pipeline"], ["coa-memory"], ["coa-io"],
        ["oop-foundations"], ["oop-inheritance"], ["oop-design"], ["oop-languages"]]


def reused_topics():
    java = {t["id"]: t for t in json.loads(JAVA_TREE.read_text(encoding="utf-8"))["topics"]}
    out = []
    for new_id, old_id, stage in REUSED:
        src = java[old_id]
        out.append({"id": new_id, "title": src["title"], "category": stage,
                    "summary": f"{len(src['subtopics'])} chapters · the same guide as in the Java Full Stack tree",
                    "subtopics": src["subtopics"], "source": src["source"], "contentId": f"interview-prep/{old_id}"})
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parts = load_parts(SRC)
    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "topics").glob("*.json"):
        old.unlink()
    categories = [{"id": s, "title": t, "description": d, "color": STAGE_COLORS[i]} for i, (s, t, d) in enumerate(STAGES)]
    topics, total_words, total_questions = reused_topics(), 0, 0
    for n, part in enumerate(parts, 1):
        sections, subtopics, words = build_sections(part, n, NOTICE)
        written = sections.pop() if sections and sections[-1]["id"] == "practice" else None
        questions_file = next(SRC.glob(f"mcq/??-{part['id']}.txt"), None)
        count, spread = 0, ""
        if questions_file:
            items = parse_questions(questions_file, names=core_helpers, tag_for=lambda level: LEVEL_TAG[level])
            count = len(items)
            spread = " answers A/B/C/D: " + "/".join(str(sum(1 for i in items if i["a"] == k)) for k in range(4))
            labels = list(dict.fromkeys(i["t"] for i in items))
            subtopics.append({"id": f"{n}-mcq", "title": f"MCQ practice ({count} questions)"})
            sections.append({"id": "mcq", "type": "practice", "title": f"MCQ practice ({count} questions)", "subtopicId": f"{n}-mcq", "blocks": [
                {"type": "markdown", "text": f"{count} original questions on {len(labels)} areas. *Recall* questions test a definition or a rule. *Problem* questions give you "
                                             "numbers or a short scenario to work out. Pick an answer to see why it is right and which trap catches people."},
                {"type": "mcq", "id": f"core-{part['id']}", "items": items}]})
        if written:
            sections.append(written)
        source = {"document": DOCUMENT, **({"questions": count} if count else {})}
        (OUT / "topics" / f"{part['id']}.json").write_text(json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total_words += words
        total_questions += count
        topics.append({"id": part["id"], "title": part["title"], "category": part["stage"],
                       "summary": f"{len(subtopics) - (1 if count else 0)} chapters" + (f" · {count} practice questions" if count else "") + " · cheat codes",
                       "subtopics": subtopics, "source": source, "estimatedMinutes": max(30, round((words / 170 + count * 1.5) / 5) * 5)})
        print(f"{words:6} words {count:4} questions  {part['title']}{spread}")
    by_id = {t["id"]: t for t in topics}
    if sorted(i for row in ROWS for i in row) != sorted(by_id):
        sys.exit(f"ROWS must list every topic exactly once; difference: {set(i for r in ROWS for i in r) ^ set(by_id)}")
    for row in ROWS:
        if len({by_id[i]["category"] for i in row}) != 1:
            sys.exit(f"a row mixes stages: {row}")
    for upper, lower in zip(ROWS, ROWS[1:]):
        for j, tid in enumerate(lower):
            by_id[tid]["requires"] = nearest_parents([by_id[i] for i in upper], len(lower), j)
    topics = [by_id[i] for row in ROWS for i in row]
    (OUT / "roadmap.json").write_text(json.dumps({
        "title": "Core Subjects", "shortTitle": "Core Subjects", "order": 7,
        "description": "The five subjects every computer science student is tested on: Operating Systems, DBMS, Computer Networks, Computer Organisation and Object-Oriented "
                       "Programming. Detailed guides with diagrams and worked examples, cheat codes and original practice questions with explanations. "
                       "Operating Systems, Databases and Networks are the same deep guides as in the Java Full Stack tree.",
        "layout": "tree", "categories": categories, "topics": topics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total_words, "words,", total_questions, "questions in the new parts,", len(topics), "topics")


if __name__ == "__main__":
    main()
