"""
Builds the topic pages for the plan-only days (build, resume, mock interviews, final revision) from the
spreadsheets themselves: nothing is written that is not in the plan.

Usage:
  python -I tools/build_plan_topics.py <folder with the xlsx files>
Reads Day_By_Day_Plan.xlsx and Java_FullStack_12Week_Plan.xlsx (its "Resume Fixes" and
"Project Interview Prep" tabs, which day 52 points to) and writes topics/plan-day-*.json.
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROADMAP_ID = "interview-prep"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def sheet_rows(path, sheet_name=None):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = list(wb.find("m:sheets", NS))
    sheet = next((s for s in sheets if sheet_name is None or s.get("name") == sheet_name), None)
    if sheet is None:
        return []
    target = rels[sheet.get("{%s}id" % NS["r"])].lstrip("/")
    root = ET.fromstring(z.read(target if target.startswith("xl/") else "xl/" + target))
    rows = []
    for row in root.iter("{%s}row" % NS["m"]):
        cells = {}
        for c in row.findall("m:c", NS):
            v = c.find("m:v", NS)
            if c.get("t") == "s" and v is not None:
                val = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            else:
                val = v.text if v is not None else ""
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            cells[col - 1] = val
        if cells:
            rows.append([cells.get(i, "") for i in range(max(cells) + 1)])
    return rows


def minutes(value):
    try:
        return f"{int(float(value))} min"
    except ValueError:
        return value or ""


def main():
    folder = Path(sys.argv[1])
    out_dir = Path(__file__).resolve().parent.parent / "content" / "roadmaps" / ROADMAP_ID / "topics"
    out_dir.mkdir(parents=True, exist_ok=True)
    roadmap = json.loads((out_dir.parent / "roadmap.json").read_text(encoding="utf-8"))
    plan_topics = {t["source"]["planDays"]: t for t in roadmap["topics"]
                   if t.get("source", {}).get("document") == "Day_By_Day_Plan.xlsx"}

    days = {}
    for r in sheet_rows(folder / "Day_By_Day_Plan.xlsx"):
        if r and r[0].isdigit() and len(r) >= 14:
            days[r[0]] = r

    twelve = folder / "Java_FullStack_12Week_Plan.xlsx"
    resume = [r for r in sheet_rows(twelve, "Resume Fixes") if r and r[0].isdigit()]
    projects = [r for r in sheet_rows(twelve, "Project Interview Prep") if r and r[0] and r[0] != "Project" and len(r) > 2 and r[2]]

    for day, topic in plan_topics.items():
        r = days[day]
        study, hours, study_min, build_min, dsa, dsa_min, review_min, done, total = (
            r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13])
        blocks = [
            {"type": "markdown", "text": study},
            {"type": "table", "caption": "Time plan for the day (from the plan; minutes are a planning assumption)",
             "headers": ["Activity", "Planned"],
             "rows": [["Study", minutes(study_min)], ["Build or hands-on", minutes(build_min)],
                      ["DSA", f"{minutes(dsa_min)}: {dsa}" if dsa else minutes(dsa_min)],
                      ["Review or output", minutes(review_min)], ["Total", minutes(total)]]},
            {"type": "callout", "variant": "important", "title": "Done when", "text": done},
        ]
        sections = [{"id": "plan", "type": "introduction", "title": f"Plan for day {day}", "blocks": blocks}]

        if day == "52" and resume:
            sections.append({"id": "resume-fixes", "type": "notes", "title": "Resume fixes", "blocks": [
                {"type": "markdown", "text": "From the *Resume Fixes* tab of `Java_FullStack_12Week_Plan.xlsx`."},
                {"type": "table", "headers": ["#", "Issue", "Fix", "Priority"],
                 "rows": [[x[0], x[1], x[2], x[3] if len(x) > 3 else ""] for x in resume]}]})
        if day == "52" and projects:
            sections.append({"id": "project-prep", "type": "practice", "title": "Project interview prep", "blocks": [
                {"type": "markdown", "text": "From the *Project Interview Prep* tab of `Java_FullStack_12Week_Plan.xlsx`."},
                {"type": "table", "headers": ["Project", "Topic to defend", "Questions to be ready for"],
                 "rows": [[x[0], x[1], x[2]] for x in projects]}]})

        content = {"source": topic["source"], "sections": sections}
        (out_dir / f"{topic['id']}.json").write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
        print(topic["id"], [s["title"] for s in sections])


if __name__ == "__main__":
    main()
