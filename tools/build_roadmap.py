"""
Builds content/roadmaps/<id>/roadmap.json from Day_By_Day_Plan.xlsx and the PDF bookmark trees.

Mapping (agreed with the user):
  category   = weekly theme from the plan (topics go under the week of their first appearance),
               plus a separate "DSA Patterns" category
  topic      = one guide Part; subtopics = the chapters the plan names (PDF bookmarks give page ranges)
  plan-only  = days with no PDF behind them (build, resume, mocks, final revision)
  requires   = previous Part of the same guide (by part number), Spring Boot Basics Part 1 before
               Beyond Basics Part 1, and each mock/final-revision day requires the Parts it names

Usage (run in isolation so nothing in the data folders is imported):
  python -I tools/build_roadmap.py <folder with the PDFs and xlsx> [--report report.txt]
Requires: pypdf
"""
import difflib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pypdf

ROADMAP_ID = "interview-prep"
PLAN_FILE = "Day_By_Day_Plan.xlsx"

# plan name -> (slug, pdf file)
GUIDES = {
    "Core Java": ("core-java", "Core_Java_In_Depth.pdf"),
    "Spring Boot Basics": ("spring-boot-basics", "Spring_Boot_Basics.pdf"),
    "Spring Boot Beyond Basics": ("spring-boot-beyond-basics", "Spring_Boot_Beyond_Basics.pdf"),
    "Databases": ("databases", "Databases_Guide.pdf"),
    "Redis": ("redis", "Redis_Complete_Guide.pdf"),
    "Operating Systems": ("operating-systems", "Operating_Systems_Guide.pdf"),
    "Computer Networks": ("computer-networks", "Computer_Networks_Guide.pdf"),
    "System Design": ("system-design", "System_Design_Guide.pdf"),
    "Kafka": ("kafka", "Kafka_Complete_Guide.pdf"),
    "Git, Docker and CI/CD": ("git-docker-cicd", "Git_Docker_CICD_Guide.pdf"),
    "DSA Patterns": ("dsa-patterns", "DSA_Patterns.pdf"),
}
GUIDE_RE = "|".join(sorted((re.escape(g) for g in GUIDES), key=len, reverse=True))
MARKER = re.compile(
    rf"(?:(?P<guide>{GUIDE_RE})\s+)?Part\s+(?P<p1>\d+)(?:\s+(?:and|to)\s+(?P<p2>\d+))?(?:\s*\([^)]*\))?\s*:?"
)

WEEK_COLORS = ["violet", "blue", "cyan", "teal", "fuchsia", "amber", "rose", "green"]
PLAN_ONLY_DAYS = {51, 52, 53, 54, 55, 56}

norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# ---------------------------------------------------------------- xlsx
def xlsx_rows(path):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    first = wb.find("m:sheets", ns)[0]
    target = rels[first.get("{%s}id" % ns["r"])].lstrip("/")
    root = ET.fromstring(z.read(target if target.startswith("xl/") else "xl/" + target))
    out = []
    for row in root.iter("{%s}row" % ns["m"]):
        cells = {}
        for c in row.findall("m:c", ns):
            v = c.find("m:v", ns)
            if c.get("t") == "s" and v is not None:
                val = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % ns["m"]))
            else:
                val = v.text if v is not None else ""
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            cells[col - 1] = val
        if cells:
            out.append([cells.get(i, "") for i in range(max(cells) + 1)])
    return out


# ---------------------------------------------------------------- pdf outlines
def load_outline(pdf_path):
    reader = pypdf.PdfReader(str(pdf_path))
    flat = []

    def walk(items, depth=0):
        for it in items:
            if isinstance(it, list):
                walk(it, depth + 1)
            else:
                flat.append((depth, it.title.strip(), reader.get_destination_page_number(it) + 1))

    walk(reader.outline)
    total = len(reader.pages)
    parts, order = {}, []
    for i, (depth, title, page) in enumerate(flat):
        if depth > 1:
            continue
        nxt = next(((p) for d, _, p in flat[i + 1:] if d <= 1), total + 1)
        end = max(page, nxt - 1)
        if depth == 0:
            m = re.match(r"Part\s+(\d+):\s*(.+)", title)
            if not m:
                continue
            parts[int(m.group(1))] = {"title": m.group(2).strip(), "start": page, "chapters": {}}
            current = parts[int(m.group(1))]
        else:
            m = re.match(r"(\d+)\.(\d+)\s+(.+)", title)
            if not m:
                continue
            number = (int(m.group(1)), int(m.group(2)))
            parts[number[0]]["chapters"][number[1]] = {
                "num": f"{number[0]}.{number[1]}", "title": m.group(3).strip(), "start": page, "end": end}
    return parts, total


# ---------------------------------------------------------------- parsing the plan text
def clean_item(text):
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"^(and|then)\s+", "", text.strip(), flags=re.I)
    return text.strip(" .,:")


def split_items(text):
    return [clean_item(x) for x in re.split(r";|\.\s+|\.$", text) if clean_item(x)]


def parse_study(text):
    """-> list of (guide, [part numbers], [items]) in text order."""
    marks = list(MARKER.finditer(text))
    out, guide = [], None
    for i, m in enumerate(marks):
        guide = m.group("guide") or guide
        p1 = int(m.group("p1"))
        p2 = int(m.group("p2")) if m.group("p2") else None
        parts = [p1] if not p2 else (list(range(p1, p2 + 1)) if " to " in m.group(0) else [p1, p2])
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((guide, parts, split_items(text[m.end():end])))
    return out


def match_chapter(item, candidates):
    """candidates: list of (part_no, chapter dict). Returns (part_no, chapter, how) or None."""
    n = norm(item)
    if not n:
        return None
    for p, c in candidates:
        if norm(c["title"]) == n:
            return p, c, "exact"
    for p, c in candidates:
        t = norm(c["title"])
        if len(n) > 6 and (n in t or (len(t) > 8 and t in n)):
            return p, c, "contains"
    best = max(candidates, key=lambda pc: difflib.SequenceMatcher(None, n, norm(pc[1]["title"])).ratio(), default=None)
    if best and difflib.SequenceMatcher(None, n, norm(best[1]["title"])).ratio() >= 0.78:
        return best[0], best[1], "fuzzy"
    return None


def day_ranges(days):
    days = sorted(set(days))
    runs, start = [], days[0]
    for a, b in zip(days, days[1:] + [None]):
        if b != a + 1:
            runs.append((start, a))
            start = b
    return ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b in runs)


def page_range(chapters):
    lo = min(c["start"] for c in chapters)
    hi = max(c["end"] for c in chapters)
    return f"{lo}-{hi}"


def main():
    folder = Path(sys.argv[1])
    report_path = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    report = []

    rows = [r for r in xlsx_rows(folder / PLAN_FILE) if r and r[0].isdigit() and len(r) >= 14]
    days = {int(r[0]): {"week": int(r[3]), "theme": r[4], "study": r[5], "dsa": r[9], "output": r[12],
                        "minutes": int(float(r[13])) if r[13] else None} for r in rows}

    outlines = {g: load_outline(folder / pdf) for g, (_, pdf) in GUIDES.items()}

    # (guide, part) -> {"chapters": {num: chapter}, "days": set, "first": (day, order)}
    topics, mentions, order_counter = {}, [], 0

    def topic_for(guide, part, day):
        nonlocal order_counter
        key = (guide, part)
        if key not in topics:
            topics[key] = {"chapters": {}, "days": set(), "first": (day, order_counter)}
            order_counter += 1
        topics[key]["days"].add(day)
        return topics[key]

    for day, info in sorted(days.items()):
        for guide, parts, items in parse_study(info["study"]):
            if guide not in GUIDES:
                report.append(f"day {day}: part marker without a known guide: {parts} {items}")
                continue
            part_map = outlines[guide][0]
            valid = [p for p in parts if p in part_map]
            for p in set(parts) - set(valid):
                report.append(f"day {day}: {guide} Part {p} does not exist in the PDF outline")
            candidates_in = [(p, c) for p in valid for c in part_map[p]["chapters"].values()]
            candidates_all = [(p, c) for p in part_map for c in part_map[p]["chapters"].values()]
            matched_any = False
            for item in items:
                if re.fullmatch(r"all .* chapters", item, re.I):
                    for p in valid:
                        t = topic_for(guide, p, day)
                        for num, c in part_map[p]["chapters"].items():
                            t["chapters"][(p, num)] = c
                    matched_any = True
                    continue
                if item.lower() in ("and", "or", ""):
                    continue
                hit = match_chapter(item, candidates_in) or match_chapter(item, candidates_all)
                if hit:
                    p, c, how = hit
                    t = topic_for(guide, p, day)
                    t["chapters"][(p, int(c["num"].split(".")[1]))] = c
                    matched_any = True
                    if how != "exact":
                        report.append(f"day {day}: {how} match  '{item}'  ->  {guide} {c['num']} '{c['title']}'")
                elif any(norm(item) == norm(part_map[p]["title"]) for p in valid):
                    pass  # names the part itself: a reference only
                elif day in PLAN_ONLY_DAYS or re.search(r"\b(chapter|tab|problems?)\b", item, re.I):
                    pass
                else:
                    report.append(f"day {day}: UNMATCHED  {guide} {valid}: '{item}'")
            for p in valid:
                mentions.append((guide, p, day, matched_any))

    # DSA column
    dsa_parts, dsa_cands = outlines["DSA Patterns"][0], None
    dsa_cands = [(p, c) for p in dsa_parts for c in dsa_parts[p]["chapters"].values()]
    for day, info in sorted(days.items()):
        text = info["dsa"]
        if "DSA" not in text and not re.search(r"Pattern recognition|Mixed interview", text):
            continue
        text = re.sub(r"^DSA Patterns( Part \d+)?:?\s*", "", text)
        text = re.sub(r"\b(Part \d+:)\s*", "", text)
        for item in split_items(re.sub(r"\.\s*\d+ problems?.*$|, then \d+ problems?.*$|\(read both.*$", "", text)):
            hit = match_chapter(item, dsa_cands)
            if hit:
                p, c, how = hit
                topic_for("DSA Patterns", p, day)["chapters"][(p, int(c["num"].split(".")[1]))] = c
                if how != "exact":
                    report.append(f"day {day}: DSA {how} match  '{item}'  ->  {c['num']} '{c['title']}'")
            elif not re.search(r"problems?|redo|timed", item, re.I):
                report.append(f"day {day}: DSA UNMATCHED '{item}'")

    # reference-only parts (no chapters matched anywhere): include the whole part
    for guide, p, day, matched in mentions:
        if (guide, p) not in topics:
            t = topic_for(guide, p, day)
            for num, c in outlines[guide][0][p]["chapters"].items():
                t["chapters"][(p, num)] = c
            report.append(f"day {day}: {guide} Part {p} was only referenced by name; whole part included "
                          f"({len(t['chapters'])} chapters)")

    # ------------------------------------------------------------ categories
    weeks = {}
    for d, info in sorted(days.items()):
        w = weeks.setdefault(info["week"], {"theme": info["theme"], "days": []})
        w["days"].append(d)
    categories = []
    for i, (w, info) in enumerate(sorted(weeks.items())):
        categories.append({"id": f"week-{w}", "title": info["theme"],
                           "description": f"Week {w} · days {min(info['days'])}–{max(info['days'])}",
                           "color": WEEK_COLORS[i % len(WEEK_COLORS)]})
    categories.append({"id": "dsa-patterns", "title": "DSA Patterns",
                       "description": "Parallel daily track from DSA_Patterns.pdf", "color": "slate"})

    # ------------------------------------------------------------ topics
    def topic_id(guide, part):
        return f"{GUIDES[guide][0]}-part-{part}"

    built = []
    for (guide, part), t in topics.items():
        info = outlines[guide][0][part]
        chapters = [t["chapters"][k] for k in sorted(t["chapters"])]
        first_day = min(t["days"])
        category = "dsa-patterns" if guide == "DSA Patterns" else f"week-{days[first_day]['week']}"
        built.append({
            "sort": (first_day, 1 if guide == "DSA Patterns" else 0, t["first"][1]),
            "topic": {
                "id": topic_id(guide, part),
                "title": f"{guide} · Part {part}: {info['title']}",
                "category": category,
                "summary": f"{guide}, Part {part} · plan days {day_ranges(t['days'])}",
                "requires": [],
                "subtopics": [{"id": c["num"].replace(".", "-"), "title": c["title"],
                               "pages": f"{c['start']}-{c['end']}"} for c in chapters],
                "source": {"document": GUIDES[guide][1], "pages": page_range(chapters),
                           "planDays": day_ranges(t["days"])},
            },
        })

    plan_only = {
        51: ("plan-day-51-deploy-careerflux", "Build day: deploy CareerFlux", ("Git, Docker and CI/CD", 4)),
        52: ("plan-day-52-resume-walkthroughs", "Resume and project walkthroughs", None),
        53: ("plan-day-53-mock-core-java-spring", "Mock interview 1: Core Java and Spring Boot",
             [("Core Java", 14), ("Spring Boot Beyond Basics", 6)]),
        54: ("plan-day-54-mock-databases-design", "Mock interview 2: Databases and System Design",
             [("Databases", 2), ("System Design", 4)]),
        55: ("plan-day-55-mock-dsa-lld", "Mock interview 3: DSA and LLD",
             [("DSA Patterns", 7), ("System Design", 3)]),
        56: ("plan-day-56-final-revision", "Final revision from the cheat sheets",
             [("System Design", 4), ("Databases", 2), ("Spring Boot Beyond Basics", 6),
              ("Git, Docker and CI/CD", 4)]),
    }
    for day, (tid, title, reqs) in plan_only.items():
        if reqs is None:
            reqs = []
        elif isinstance(reqs, tuple):
            reqs = [reqs]
        req_ids = [topic_id(g, p) for g, p in reqs if (g, p) in topics]
        for g, p in reqs:
            if (g, p) not in topics:
                report.append(f"day {day}: required part {g} Part {p} is not a topic")
        built.append({"sort": (day, 2, 0), "topic": {
            "id": tid, "title": title, "category": f"week-{days[day]['week']}",
            "summary": days[day]["output"], "requires": req_ids,
            "estimatedMinutes": days[day]["minutes"],
            "source": {"document": PLAN_FILE, "planDays": str(day)},
        }})

    built.sort(key=lambda b: b["sort"])
    result = [b["topic"] for b in built]
    by_id = {t["id"]: t for t in result}

    # dependencies: previous existing Part of the same guide, by part number
    per_guide = {}
    for guide, part in topics:
        per_guide.setdefault(guide, []).append(part)
    for guide, parts in per_guide.items():
        parts.sort()
        for prev, cur in zip(parts, parts[1:]):
            by_id[topic_id(guide, cur)]["requires"].append(topic_id(guide, prev))
    extra = (("Spring Boot Beyond Basics", 1), ("Spring Boot Basics", 1))
    if (extra[0] in topics) and (extra[1] in topics):
        by_id[topic_id(*extra[0])]["requires"].append(topic_id(*extra[1]))

    for t in result:
        if not t["requires"]:
            del t["requires"]

    out = {
        "title": "Interview Prep: 8-Week Day-by-Day Plan",
        "description": "Built from Day_By_Day_Plan.xlsx: each node is a Part of one of your guides, with the chapters "
                       "the plan names as subtopics. Categories are the plan's weekly themes.",
        "categories": categories,
        "topics": result,
    }
    target = Path(__file__).resolve().parent.parent / "content" / "roadmaps" / ROADMAP_ID / "roadmap.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_sub = sum(len(t.get("subtopics", [])) for t in result)
    report.insert(0, f"{len(result)} topics, {n_sub} subtopics, {len(categories)} categories -> {target}")
    text = "\n".join(report)
    if report_path:
        Path(report_path).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
