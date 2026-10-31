"""
Builds the "DSA by Topic" tree, laid out like NeetCode's roadmap, and one practice subject per topic.

  tools/dsa/problems.py       the 18 topics, their dependencies and the NeetCode 150 problems (links verified against LeetCode)
  tools/dsa/NN-<topic>.md     the learning page of each topic (format: see guide_source.py)

Writes
  content/roadmaps/dsa-topics/roadmap.json and topics/<topic>.json
  content/practice/dsa-<topic>.json

The page of a topic ends with a generated chapter that lists its problems with links, so the problem lists
live in one place only. Order, dependencies and counts all come from problems.py.

Usage: python -I tools/build_dsa_topics.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "dsa"))
from guide_source import DOCUMENT, build_sections, load_parts  # noqa: E402
from problems import TIERS, TOPICS  # noqa: E402

ROOT = HERE.parent / "content"
ROADMAP_DIR = ROOT / "roadmaps" / "dsa-topics"
PRACTICE_DIR = ROOT / "practice"
LEETCODE = "https://leetcode.com/problems/{}/"

NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "This tree follows the topics and the problem list of NeetCode's roadmap (the NeetCode 150), with a learning page "
                  "written for this site for each topic. The explanations and Java templates are ours; the problems belong to LeetCode, "
                  "and each one links to its LeetCode page."}


def problem_link(p):
    number, title, slug, level, premium = p
    return LEETCODE.format(slug)


def problems_chapter(topic):
    problems = topic["problems"]
    counts = {lv: sum(1 for p in problems if p[3] == lv) for lv in ("Easy", "Medium", "Hard")}
    rows = ["| # | Problem | Level | |", "|---|---|---|---|"]
    for p in problems:
        number, title, slug, level, premium = p
        rows.append(f"| {number} | [{title}]({problem_link(p)}) | {level} | {'LeetCode Premium' if premium else ''} |")
    intro = (f"The NeetCode 150 problems for **{topic['title']}**: {len(problems)} in all "
             f"({counts['Easy']} easy, {counts['Medium']} medium, {counts['Hard']} hard), in the order NeetCode lists them. "
             "Do the easy ones first, then the medium ones. For every problem, write down the idea and the complexity in one sentence "
             "before you look at a solution.")
    blocks = [
        {"type": "markdown", "text": intro},
        {"type": "markdown", "text": "\n".join(rows)},
        {"type": "callout", "variant": "tip", "title": "Practise and track them",
         "text": f"Open **Practice** in the top bar and choose **{topic['title']}** (under DSA by topic) to tick problems off, "
                 "keep notes on each one, and add problems of your own."},
    ]
    if any(p[4] for p in problems):
        blocks.append({"type": "callout", "variant": "note", "title": "Premium problems",
                       "text": "Problems marked LeetCode Premium need a paid LeetCode account. If you do not have one, "
                               "skip them: the free problems of the topic teach the same ideas."})
    return {"title": "Practice: the NeetCode 150 problems", "blocks": blocks, "qa": []}


def main():
    parts = {p["id"]: p for p in load_parts(HERE / "dsa")}
    missing = [t["id"] for t in TOPICS if t["id"] not in parts]
    assert not missing, f"no learning page for: {missing}"
    stray = sorted(set(parts) - {t["id"] for t in TOPICS})
    assert not stray, f"learning pages without a topic: {stray}"

    (ROADMAP_DIR / "topics").mkdir(parents=True, exist_ok=True)
    PRACTICE_DIR.mkdir(parents=True, exist_ok=True)
    for old in (ROADMAP_DIR / "topics").glob("*.json"):
        old.unlink()
    for old in PRACTICE_DIR.glob("dsa-*.json"):
        old.unlink()

    topics_out, total_words = [], 0
    for n, topic in enumerate(TOPICS, 1):
        part = parts[topic["id"]]
        part["chapters"].append(problems_chapter(topic))
        sections, subtopics, words = build_sections(part, n, NOTICE)
        total_words += words
        source = {"document": DOCUMENT}
        (ROADMAP_DIR / "topics" / f"{topic['id']}.json").write_text(
            json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        topics_out.append({
            "id": topic["id"], "title": topic["title"], "category": topic["tier"],
            "summary": f"{len(topic['problems'])} problems · {len(subtopics)} chapters",
            "source": source, "subtopics": subtopics, "requires": topic["requires"],
        })

        levels = sorted({p[3] for p in topic["problems"]}, key=("Easy", "Medium", "Hard").index)
        subject = {
            "id": f"dsa-{topic['id']}", "title": topic["title"], "group": "DSA by topic", "order": 100 + n,
            "description": f"{len(topic['problems'])} NeetCode 150 problems on {topic['title'].lower()} ({', '.join(levels).lower()}). "
                           "Open each on LeetCode, tick it off here and keep notes.",
            "platforms": [
                {"name": "LeetCode: this topic", "url": f"https://leetcode.com/tag/{topic['tag']}/", "note": "More problems tagged with this topic"},
                {"name": "GeeksforGeeks", "url": topic["gfg"], "note": "Tutorial and practice problems"},
                {"name": "NeetCode roadmap", "url": "https://neetcode.io/roadmap", "note": "The roadmap this tree follows"},
            ],
            "questions": [
                {"id": f"dsa-{topic['id']}-{p[0]}", "type": "coding", "title": p[1], "level": p[3],
                 "links": [{"platform": "LeetCode", "label": p[1], "number": p[0], "url": problem_link(p), **({"premium": True} if p[4] else {})}]}
                for p in topic["problems"]
            ],
        }
        (PRACTICE_DIR / f"dsa-{topic['id']}.json").write_text(json.dumps(subject, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{words:6}  {topic['title']}  ({len(topic['problems'])} problems, {len(subtopics)} chapters)")

    categories = [{"id": i, "title": t, "description": d, "color": c} for i, t, d, c in TIERS]
    roadmap = {
        "title": "DSA by Topic: the NeetCode roadmap", "shortTitle": "DSA by Topic", "order": 4,
        "description": "The 18 topics of NeetCode's roadmap in the order it suggests, each with a short Java guide and its NeetCode 150 problems. "
                       "The Java Full Stack tree teaches DSA by pattern; this one goes topic by topic.",
        "layout": "tree", "categories": categories, "topics": topics_out,
    }
    (ROADMAP_DIR / "roadmap.json").write_text(json.dumps(roadmap, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total_words, "words")


if __name__ == "__main__":
    main()
