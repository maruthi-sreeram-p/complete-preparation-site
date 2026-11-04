"""Dev helper: print the verified outputs of a built part, to compare them with the prose.  python -I tools/python_fs/show_outputs.py py-core-2"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
path = Path(__file__).resolve().parent.parent.parent / "content" / "roadmaps" / "python-fullstack" / "topics" / f"{sys.argv[1]}.json"
data = json.loads(path.read_text(encoding="utf-8"))
last = None
for section in data["sections"]:
    for block in section["blocks"]:
        if isinstance(block, dict) and block["type"] == "code":
            if block.get("title") in ("Output", "Traceback"):
                print(f"=== {last} -> {block['title']}\n{block['code']}")
            else:
                last = block.get("title")
        elif isinstance(block, dict) and block["type"] == "questions":
            for q in block["items"]:
                for text in (q["question"], q["answer"]):
                    if "```text Output" in text or "```text Traceback" in text:
                        pass
                a = q["answer"]
                if "```text" in a:
                    print(f"=== QA: {q['question'].splitlines()[0][:70]}\n" + a.split("```text", 1)[1].split("```")[0])
