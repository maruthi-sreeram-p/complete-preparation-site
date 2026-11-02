"""
Builds the Cybersecurity for Freshers tree from tools/cyber/: detailed notes with cheat codes, plus MCQs checked at build time.

  tools/cyber/NN-<topic>.md        notes, in the guide format of guide_source.py (use !cheat for cheat codes)
  tools/cyber/mcq/NN-<topic>.txt   multiple-choice questions, same format as the GATE tree (see tools/build_gate.py):
                                   ?1 is a recall question, ?2 is a scenario question
  tools/cyber/cyber_helpers.py     names available to the !py checks (hashes, JWT, CIDR, CVSS, an SQL injection lab ...)

Everything is written for the site for defence and learning. Attacks are explained so you can recognise and prevent them,
and every practical exercise points to a lab you are allowed to attack.

Usage: python -I tools/build_cyber.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "cyber"))
from build_gate import parse_questions  # noqa: E402
from build_roadmap import STAGE_COLORS, nearest_parents  # noqa: E402
from guide_source import build_sections, load_parts  # noqa: E402
import cyber_helpers  # noqa: E402

SRC = HERE / "cyber"
OUT = HERE.parent / "content" / "roadmaps" / "cybersecurity"
DOCUMENT = "Written for this site, for freshers (November 2026)"
NOTICE = {"type": "callout", "variant": "note", "title": "About this page",
          "text": "Written for this site as of November 2026 for a fresher. Standards and tools change (OWASP Top 10 editions, TLS versions, certificate exams), "
                  "so check the official source named in the text before relying on a detail. Practise only on systems you own or have written permission to test."}
LEVEL_TAG = {1: "*(Recall)*", 2: "*(Scenario)*"}

STAGES = [("foundations", "Foundations", "Security thinking, the Linux command line and the networking every attack and defence rests on"),
          ("crypto", "Cryptography", "Hashing, encryption, signatures, TLS and how passwords must be stored"),
          ("appsec", "Application security", "The OWASP Top 10, authentication and access control, and secure coding in Java and Spring"),
          ("defence", "Defence, cloud and DevSecOps", "Logging, detection, incident response, cloud security and securing the pipeline"),
          ("career", "Hands-on and careers", "Legal labs, the pentest method, certificates, a portfolio and interviews")]

# id -> how much a Java fresher needs it
PRIORITY = {
    "cyber-start": "Everyone starts here",
    "cyber-linux-network": "Essential",
    "cyber-crypto": "Essential",
    "cyber-web-attacks": "Core for AppSec",
    "cyber-auth": "Core for AppSec",
    "cyber-secure-java": "Your edge as a Java developer",
    "cyber-defence": "Core for SOC roles",
    "cyber-cloud-devsecops": "Fast-growing",
    "cyber-labs": "Practice",
    "cyber-career": "Job search",
}

# The study order, one row of the tree per line. A row never mixes stages (the tree layout draws a heading wherever a row's stage changes).
ROWS = [["cyber-start"],
        ["cyber-linux-network"],
        ["cyber-crypto"],
        ["cyber-web-attacks"],
        ["cyber-auth", "cyber-secure-java"],
        ["cyber-defence", "cyber-cloud-devsecops"],
        ["cyber-labs"],
        ["cyber-career"]]


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
        questions_file = next(SRC.glob(f"mcq/??-{part['id'].removeprefix('cyber-')}.txt"), None)
        count, spread = 0, ""
        if questions_file:
            items = parse_questions(questions_file, names=cyber_helpers, tag_for=lambda level: LEVEL_TAG[level])
            count = len(items)
            spread = " answers A/B/C/D: " + "/".join(str(sum(1 for i in items if i["a"] == k)) for k in range(4))
            labels = list(dict.fromkeys(i["t"] for i in items))
            subtopics.append({"id": f"{n}-mcq", "title": f"MCQ practice ({count} questions)"})
            sections.append({"id": "mcq", "type": "practice", "title": f"MCQ practice ({count} questions)", "subtopicId": f"{n}-mcq", "blocks": [
                {"type": "markdown", "text": f"{count} original questions on {len(labels)} areas. *Recall* questions test a definition or a rule. *Scenario* questions give you a "
                                             "situation, a log or a snippet and ask what is wrong or what to do. Pick an answer to see why it is right and which trap catches people."},
                {"type": "mcq", "id": part["id"], "items": items}]})
        if written:
            sections.append(written)
        source = {"document": DOCUMENT, **({"questions": count} if count else {})}
        (OUT / "topics" / f"{part['id']}.json").write_text(json.dumps({"source": source, "sections": sections}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total_words += words
        total_questions += count
        topics.append({"id": part["id"], "title": part["title"], "category": part["stage"],
                       "summary": f"{PRIORITY[part['id']]}" + (f" · {count} practice questions" if count else "") + " · cheat codes",
                       "subtopics": subtopics, "source": source, "estimatedMinutes": max(30, round((words / 170 + count * 1.5) / 5) * 5)})
        print(f"{words:6} words {count:4} questions  {part['title']}{spread}")
    by_id = {t["id"]: t for t in topics}
    missing = set(PRIORITY) - set(by_id)
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
        "title": "Cybersecurity for Freshers", "shortTitle": "Cybersecurity", "order": 6,
        "description": f"A path from zero to a job-ready fresher in application security and entry-level SOC work: security thinking, Linux and networking, cryptography, "
                       f"the OWASP Top 10, authentication, secure Java and Spring, detection and response, cloud and DevSecOps, legal labs and interviews. "
                       f"Detailed notes, cheat codes and {total_questions} original questions with explanations. Best started once you can build a Spring Boot API.",
        "layout": "tree", "categories": categories, "topics": topics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total_words, "words,", total_questions, "questions")


if __name__ == "__main__":
    main()
