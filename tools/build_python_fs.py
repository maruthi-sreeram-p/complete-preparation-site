"""
Builds the Python Full Stack tree (content/roadmaps/python-fullstack/), the Python counterpart of the Java Full Stack tree.

  tools/python_fs/NN-<name>.md   the parts written for this tree (guide format of tools/guide_source.py; NN-more-*.md extend the part before)
  tools/python_fs/tree.py        stages, the guides shared with the Java tree, and the study order (ROWS)
  tools/python_fs/runner.py      runs the code samples in tools/python_fs/.venv (see tools/python_fs/README.md)

Code is checked while building, so a wrong example or a wrong "output" fails the build:
  ```python Name.py       a program: it is run, and must exit with 0. A fenced block "```output" right after it (before the next program) is
                          REPLACED by the real stdout, so printed results can never be out of date. The output must be the same on two runs.
  ```python Name.py !fail the program must raise: the following "```output" block receives the traceback
  ```python Name.py !skip shown with a .py title but not run (needs a server, a network or a broker); only its syntax is checked
  ```python               any other python block: syntax is checked
  ```pycon                an interactive transcript (">>> "): run as a doctest, every answer compared exactly
Multiple-choice quizzes: tools/python_fs/mcq/<part id>-<name>.txt (format of tools/build_gate.py, plus "# title:" and "# intro:" header lines) become
an MCQ section of that part. `!py` checks run the program in the question (names in tools/python_fs/pyfs_helpers.py), so answer keys cannot be wrong.
Extra directives on top of guide_source.py:
  !qa / question lines / => / answer lines / !end    a practice question whose question and answer span several lines (code, output)

Usage: python -I tools/build_python_fs.py [--strict] [--no-run]
  --strict   fail when a part listed in tools/python_fs/tree.py has not been written yet (without it, missing parts are left out of the tree)
  --no-run   skip running the code samples (structure check only; do not publish the result)
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "python_fs"))
from build_gate import parse_questions  # noqa: E402
from build_roadmap import STAGE_COLORS, nearest_parents  # noqa: E402,F401
from guide_source import build_sections, load_parts  # noqa: E402
import pyfs_helpers  # noqa: E402
import tree  # noqa: E402

SRC = HERE / "python_fs"
OUT = HERE.parent / "content" / "roadmaps" / "python-fullstack"
JAVA_TREE = HERE.parent / "content" / "roadmaps" / tree.JAVA_TREE / "roadmap.json"
DOCUMENT = "Written for this site (November 2026)"
NL = "␤"  # stands for a line break while a multi-line question travels through the one-line "??" syntax of guide_source
DIRECTIVES = ("note", "tip", "warning", "important", "interview", "realworld", "cheat", "keypoints", "end", "qa")


# ------------------------------------------------------------------ the verification interpreter
def verification_python():
    if os.environ.get("PYFS_PYTHON"):
        return os.environ["PYFS_PYTHON"]
    for candidate in (SRC / ".venv" / "Scripts" / "python.exe", SRC / ".venv" / "bin" / "python"):
        if candidate.exists():
            return str(candidate)
    sys.exit("No verification interpreter: create tools/python_fs/.venv (see tools/python_fs/README.md) or set PYFS_PYTHON.")


def run_tasks(tasks, python):
    if not tasks:
        return {}
    with tempfile.TemporaryDirectory(prefix="pyfs-tasks-") as folder:
        path = Path(folder) / "tasks.json"
        path.write_text(json.dumps(tasks), encoding="utf-8")
        done = subprocess.run([python, "-X", "utf8", str(SRC / "runner.py"), str(path)], capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        sys.exit(f"the sample runner crashed:\n{done.stderr}")
    return json.loads(done.stdout)


# ------------------------------------------------------------------ fences
def scan_fences(lines):
    """The code fences of a source file, found exactly as guide_source.py finds them: [(open line, close line, language, title, flags)]."""
    fences, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```") and line.strip() != "```":
            bits = line[3:].split(None, 1)
            lang, rest = bits[0], (bits[1].strip() if len(bits) > 1 else "")
            flags = re.findall(r"(?<!\S)!(\w+)", rest)
            title = re.sub(r"(?<!\S)!\w+", "", rest).strip()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            fences.append((i, j, lang, title, flags))
            i = j + 1
        else:
            i += 1
    return fences


def check_and_rewrite(files, python, run):
    """Runs the samples of every file and returns {path: new text}. Exits with a list of problems if any sample is wrong."""
    plans, tasks, problems = {}, [], []
    for path, text in files.items():
        lines = text.split("\n")
        fences = scan_fences(lines)
        plan, last_run = [], None
        for n, (a, b, lang, title, flags) in enumerate(fences):
            where = f"{path.name}:{a + 1}"
            code = "\n".join(lines[a + 1:b])
            if b >= len(lines):
                problems.append(f"{where}: this code fence is never closed")
                continue
            if lang in ("python", "py"):
                runnable = title.endswith(".py") and "skip" not in flags
                if "fail" in flags and not title.endswith(".py"):
                    problems.append(f"{where}: !fail needs a title ending in .py")
                if runnable:
                    ahead = []
                    for f in fences[n + 1:]:
                        if f[2] in ("python", "py", "pycon"):
                            break
                        ahead.append(f[2])
                    has_output = "output" in ahead
                    tasks.append({"id": where, "kind": "run", "code": code, "stable": has_output, "expect_fail": "fail" in flags})
                    last_run = (n, where, "fail" in flags)
                else:
                    tasks.append({"id": where, "kind": "syntax", "code": code})
                    last_run = None
                plan.append((a, b, lang, title, "code", where))
            elif lang == "pycon":
                if "skip" not in flags:
                    tasks.append({"id": where, "kind": "doctest", "code": code})
                plan.append((a, b, lang, title, "code", where))
            elif lang == "output":
                if last_run is None:
                    problems.append(f"{where}: an ```output block must come right after a program with a .py title")
                else:
                    plan.append((a, b, "output", title, last_run[1:], where))
                    last_run = None
            else:
                plan.append((a, b, lang, title, "code", where))
        plans[path] = (lines, plan)
        # unknown directives would silently become paragraphs
        inside = {k for (a, b, *_rest) in fences for k in range(a, b + 1)}
        for k, line in enumerate(lines):
            if k not in inside and line.startswith("!") and not re.match(rf"!({'|'.join(DIRECTIVES)})(\s|$)", line):
                problems.append(f"{path.name}:{k + 1}: unknown directive {line.split()[0]!r}")
    results = run_tasks(tasks, python) if run else {t["id"]: {"ok": True, "out": "", "err": ""} for t in tasks}
    for t in tasks:
        r = results[t["id"]]
        if not r["ok"]:
            problems.append(f"{t['id']}: {t['kind']} failed\n    " + "\n    ".join((r["err"] or r["out"] or "(no message)").splitlines()[-14:]))
    rewritten = {}
    for path, (lines, plan) in plans.items():
        out = list(lines)
        for a, b, lang, title, extra, where in sorted(plan, key=lambda p: -p[0]):
            if lang == "output":
                run_where, failed = extra
                r = results[run_where]
                body = (r["err"] if failed else r["out"]) if run else "(not run)"
                if not body.strip():
                    problems.append(f"{where}: the program at {run_where} printed nothing to show here")
                    continue
                out[a:b + 1] = ["```text " + ("Traceback" if failed else "Output")] + body.split("\n") + ["```"]
            elif lang in ("python", "py"):
                out[a] = f"```python {title}".rstrip()
        rewritten[path] = "\n".join(out)
    if problems:
        sys.exit(f"{len(problems)} problem(s) in the sources:\n\n" + "\n\n".join(problems))
    return rewritten, sum(1 for t in tasks if t["kind"] == "run")


# ------------------------------------------------------------------ extra directive
def expand_qa(text, path):
    """!qa / question / => / answer / !end  ->  the one-line "?? q" and "=> a" of guide_source.py, with line breaks encoded."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        if lines[i].strip() != "!qa":
            out.append(lines[i])
            i += 1
            continue
        start = i + 1
        question, answer = [], []
        i += 1
        while i < len(lines) and lines[i].strip() != "=>":
            question.append(lines[i])
            i += 1
        i += 1
        while i < len(lines) and lines[i].strip() != "!end":
            answer.append(lines[i])
            i += 1
        if i >= len(lines):
            sys.exit(f"{path.name}:{start}: !qa needs a line '=>' and a closing '!end'")
        i += 1
        out += ["?? " + NL.join(question).strip(), "=> " + NL.join(answer).strip()]
    return "\n".join(out)


# ------------------------------------------------------------------ assembling the tree
def shared_topics():
    java = {t["id"]: t for t in json.loads(JAVA_TREE.read_text(encoding="utf-8"))["topics"]}
    out = {}
    for topic_id, stage in tree.SHARED:
        if topic_id not in java:
            sys.exit(f"tools/python_fs/tree.py shares {topic_id!r}, which is not in the Java Full Stack tree")
        src = java[topic_id]
        chapters = len(src.get("subtopics", []))
        topic = {"id": topic_id, "title": src["title"], "category": stage,
                 "summary": (f"{chapters} chapters · " if chapters else "") + "the same guide as in the Java Full Stack tree",
                 "subtopics": src.get("subtopics", []), "contentId": f"{tree.JAVA_TREE}/{topic_id}"}
        if src.get("source"):
            topic["source"] = src["source"]
        if src.get("estimatedMinutes"):
            topic["estimatedMinutes"] = src["estimatedMinutes"]
        out[topic_id] = topic
    return out


LEVEL_TAG = {1: "*(Concept)*", 2: "*(Code)*"}


def mcq_sections(part_id, n):
    """-> (sections, subtopics, number of questions) for the files tools/python_fs/mcq/<part id>-*.txt."""
    sections, subtopics, total = [], [], 0
    for path in sorted((SRC / "mcq").glob(f"{part_id}-*.txt")):
        head = path.read_text(encoding="utf-8")
        title = re.search(r"^# title: (.+)$", head, re.M)
        intro = re.search(r"^# intro: (.+)$", head, re.M)
        if not title or not intro:
            sys.exit(f"{path.name}: needs '# title: ...' and '# intro: ...' header lines")
        items = parse_questions(path, names=pyfs_helpers, tag_for=lambda level: LEVEL_TAG[level])
        slug = path.stem.removeprefix(f"{part_id}-")
        heading = f"{title[1]} ({len(items)} questions)"
        subtopics.append({"id": f"{n}-{slug}", "title": heading})
        labels = len(dict.fromkeys(i["t"] for i in items))
        sections.append({"id": slug, "type": "practice", "title": heading, "subtopicId": f"{n}-{slug}", "blocks": [
            {"type": "markdown", "text": f"{intro[1]} {len(items)} original questions on {labels} areas; pick an answer to see why it is right and which trap catches people."},
            {"type": "mcq", "id": f"pyfs-{path.stem}", "items": items}]})
        total += len(items)
        spread = "/".join(str(sum(1 for i in items if i["a"] == k)) for k in range(4))
        print(f"       {len(items):4} questions  {path.name}  answers A/B/C/D: {spread}")
    return sections, subtopics, total


def notice_for(python):
    done = subprocess.run([python, "-X", "utf8", str(SRC / "runner.py"), "--versions"], capture_output=True, text=True, encoding="utf-8")
    v = json.loads(done.stdout)
    libs = ", ".join(f"{name} {v[key]}" for name, key in (("FastAPI", "fastapi"), ("Pydantic", "pydantic"), ("SQLAlchemy", "sqlalchemy"), ("Django", "django")) if key in v)
    return {"type": "callout", "variant": "note", "title": "About this page",
            "text": "Written for this site as of November 2026 for a fresher who wants experienced-level depth, in the style of the Java Full Stack guides. "
                    f"Every example titled `*.py` was run when this page was built, on Python {v['python']} with {libs}, and the output shown is what it really printed. "
                    "Python and its libraries change quickly (and some examples need servers that a build cannot start, so those are only syntax-checked): "
                    "check the official documentation for anything newer before relying on a detail."}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    strict, run = "--strict" in sys.argv, "--no-run" not in sys.argv
    python = verification_python()
    stage_ids = [s[0] for s in tree.STAGES]
    paths = sorted(SRC.glob("*.md"), key=lambda p: (p.name[:2], "-more" in p.name, p.name))
    files = {p: p.read_text(encoding="utf-8") for p in paths}
    rewritten, samples = check_and_rewrite(files, python, run)
    pyfs_helpers.PYTHON, pyfs_helpers.RUN["real"] = python, run
    parts = load_parts(SRC, transform=lambda path, _text: expand_qa(rewritten[path], path))
    for part in parts:
        if part["stage"] not in stage_ids:
            sys.exit(f"{part['id']}: unknown stage {part['stage']!r}")
        for chapter in part["chapters"]:
            chapter["qa"] = [{"question": q["question"].replace(NL, "\n"), "answer": q["answer"].replace(NL, "\n")} for q in chapter["qa"]]
    notice = notice_for(python)
    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "topics").glob("*.json"):
        old.unlink()
    topics = shared_topics()
    total_words = 0
    for n, part in enumerate(parts, 1):
        sections, subtopics, words = build_sections(part, n, notice)
        written = sections.pop() if sections and sections[-1]["id"] == "practice" else None
        quiz_sections, quiz_subtopics, questions = mcq_sections(part["id"], n)
        sections += quiz_sections
        if written:
            sections.append(written)
        source = {"document": DOCUMENT, **({"questions": questions} if questions else {})}
        (OUT / "topics" / f"{part['id']}.json").write_text(json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total_words += words
        topics[part["id"]] = {"id": part["id"], "title": part["title"], "category": part["stage"],
                              "summary": f"{len(subtopics)} chapters · runnable examples" + (f" · {questions} quiz questions" if questions else "") + " · cheat codes",
                              "subtopics": subtopics + quiz_subtopics, "source": source,
                              "estimatedMinutes": max(30, round((words / 170 + questions * 1.5) / 5) * 5)}
        print(f"{words:6} words  {part['title']}  ({len(subtopics)} chapters)")
    listed = [i for row in tree.ROWS for i in row]
    duplicates = {i for i in listed if listed.count(i) > 1}
    unplaced = sorted(set(topics) - set(listed))
    if duplicates or unplaced:
        sys.exit(f"tools/python_fs/tree.py ROWS: listed twice {sorted(duplicates)}; written or shared but not listed {unplaced}")
    missing = [i for i in listed if i not in topics]
    if missing and strict:
        sys.exit(f"{len(missing)} parts are not written yet: {missing}")
    rows = [[i for i in row if i in topics] for row in tree.ROWS]
    rows = [row for row in rows if row]
    stage_of = {i: topics[i]["category"] for row in rows for i in row}
    for row in rows:
        if len({stage_of[i] for i in row}) != 1:
            sys.exit(f"a row mixes stages: {row}")
    for upper, lower in zip(rows, rows[1:]):
        for j, tid in enumerate(lower):
            topics[tid]["requires"] = nearest_parents([topics[i] for i in upper], len(lower), j)
    ordered = [topics[i] for row in rows for i in row]
    used = {t["category"] for t in ordered}
    categories = [{"id": s, "title": t, "description": d, "color": c} for s, t, d, c in tree.STAGES if s in used]
    (OUT / "roadmap.json").write_text(json.dumps({
        "title": "Python Full Stack: Fresher to Experienced Level", "shortTitle": "Python Full Stack", "order": 1.5,
        "description": "The Python counterpart of the Java Full Stack tree, in the same order: the Python language and CPython, DSA, FastAPI, Django and Flask, "
                       "databases and Redis, operating systems and networks, microservices and Kafka, system design, delivery, React and interviews. "
                       "Every code example is run when the site is built. Language-neutral guides (operating systems, networks, databases, Redis, Kafka, high-level design) "
                       "are the same deep guides as in the Java tree.",
        "layout": "tree", "categories": categories, "topics": ordered}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{total_words} words in {len(parts)} written parts, {samples} programs run, {len(ordered)} topics in the tree ({len(missing)} not written yet)")
    if missing:
        print("not written yet:", ", ".join(missing))


if __name__ == "__main__":
    main()
