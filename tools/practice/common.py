"""Helpers shared by the practice subject files."""


def written(id_, title, level, prompt, answer, hint=None):
    q = {"id": id_, "type": "written", "title": title, "level": level, "prompt": prompt, "answer": answer}
    if hint:
        q["hint"] = hint
    return q


def subject(id_, title, group, order, description, questions, platforms=()):
    return {"id": id_, "title": title, "group": group, "order": order, "description": description,
            "platforms": list(platforms), "questions": list(questions)}
