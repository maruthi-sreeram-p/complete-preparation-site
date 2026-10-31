"""
Writes the hand-written practice subjects to content/practice/<id>.json from tools/practice/*.py.

The DSA subjects (one per topic of the "DSA by topic" tree) are written by build_dsa_topics.py, not here.
A check at the end makes sure no question id is used twice, because answers are saved under the id.

Usage: python -I tools/build_practice.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "practice"))
import core_java  # noqa: E402
import databases  # noqa: E402
import kafka_design  # noqa: E402
import spring_boot  # noqa: E402

OUT = HERE.parent / "content" / "practice"
SUBJECTS = [databases.SUBJECT, core_java.SUBJECT, spring_boot.SUBJECT, *kafka_design.SUBJECTS]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    seen = set()
    for s in SUBJECTS:
        for q in s["questions"]:
            assert q["id"] not in seen, f"duplicate question id {q['id']}"
            seen.add(q["id"])
        (OUT / f"{s['id']}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        kinds = {}
        for q in s["questions"]:
            kinds[q["type"]] = kinds.get(q["type"], 0) + 1
        print(f"{s['id']:14} {len(s['questions']):3} questions  {kinds}")


if __name__ == "__main__":
    main()
