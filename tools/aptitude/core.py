"""
Shared helpers for the aptitude question generators.

A template is a function taking a seeded random.Random and returning one Q. Answers are computed in the
template, never typed, so a numeric answer is right as long as the template's working is right.
"""
import math
import random
import re
from fractions import Fraction as F

TEMPLATES = {}  # chapter -> {sub-topic: [functions]}
HAND = {}       # chapter -> {sub-topic: [question dicts]}


def T(chapter, topic):
    def register(fn):
        TEMPLATES.setdefault(chapter, {}).setdefault(topic, []).append(fn)
        return fn
    return register


def hand(chapter, topic, rows):
    """rows: (question, answer, wrong, wrong, wrong, why): the answer is shuffled in later."""
    bucket = HAND.setdefault(chapter, {}).setdefault(topic, [])
    for q, a, w1, w2, w3, why in rows:
        bucket.append(Q(q, a, why, [w1, w2, w3]))


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x, float):
        return f"{x:.2f}".rstrip("0").rstrip(".")
    return str(x)


def near(answer, r):
    """Plausible wrong numbers: common slips rather than random values."""
    if isinstance(answer, F) and answer.denominator != 1:
        n, d = answer.numerator, answer.denominator
        pool = [F(n + 1, d), F(max(n - 1, 1), d), F(n, d + 1), F(n, d + 2), F(d, n), answer * 2, answer / 2, F(n + 2, d + 1)]
    else:
        a = int(answer)
        step = max(1, abs(a) // 10)
        pool = [a + step, a - step, a + 2 * step, a - 2 * step, a + 1, a - 1, a * 2, a + 5 * step, a + 3 * step]
        if a > 0:
            pool = [p for p in pool if p > 0] or [a + 1, a + 2, a + 3]
    r.shuffle(pool)
    return pool


def near_text(answer, r):
    """Wrong options for answers like "25%", "₹300" or "3 : 4": vary the first number and keep the form."""
    m = re.search(r"\d+(\.\d+)?", answer)
    if not m:
        if " " in answer or len(answer) < 4:
            raise ValueError(f"cannot make options for: {answer}")
        return ["".join(r.sample(answer, len(answer))) for _ in range(8)]  # a coded word: other letter orders
    value = float(m.group())
    digits = len(m.group(1)) - 1 if m.group(1) else 0
    step = max(10 ** -digits, round(abs(value) * .1, digits))
    pool = [value + k * step for k in (1, 2, 3, 4, 5)] + [value - k * step for k in (1, 2) if value - k * step > 0]
    r.shuffle(pool)
    return [answer[:m.start()] + f"{v:.{digits}f}" + answer[m.end():] for v in pool]


def tidy(text):
    """Text that templates cannot avoid on their own: ordinals, singular units, and 200/7% as a decimal."""
    def ordinal(m):
        n = int(m.group(1))
        suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
    text = re.sub(r"\b(\d+)th\b", ordinal, text)
    text = re.sub(r"\b1 steps/s", "1 step/s", text)
    text = re.sub(r"\b1 years'", "1 year's", text)
    return re.sub(r"\b(\d+)/(\d+)%", lambda m: f"{int(m.group(1)) / int(m.group(2)):.2f}%", text)


class Q:
    def __init__(self, text, answer, why, wrong=None, svg=None, option_svgs=None):
        self.text, self.why = tidy(text), tidy(why)
        self.answer = tidy(answer) if isinstance(answer, str) else answer
        self.wrong = [tidy(w) if isinstance(w, str) else w for w in wrong] if wrong is not None else None
        self.svg, self.option_svgs = svg, option_svgs

    def key(self):
        return (self.text, fmt(self.answer), self.svg, tuple(self.option_svgs[:1] + sorted(self.option_svgs[1:])) if self.option_svgs else ())

    def build(self, topic, r):
        if self.option_svgs:  # option_svgs[0] is the answer's figure; options are labelled by letter only
            order = list(range(4))
            r.shuffle(order)
            item = {"t": topic, "q": self.text, "o": [str(i) for i in order], "a": order.index(0),
                    "w": self.why, "os": [self.option_svgs[i] for i in order]}
        else:
            answer = fmt(self.answer)
            pool = list(self.wrong) if self.wrong is not None else []
            if len({fmt(w) for w in pool} - {answer}) < 3:
                pool += near_text(self.answer, r) if isinstance(self.answer, str) else near(self.answer, r)
            options, seen = [], {answer}
            for w in pool:
                text = fmt(w)
                if text not in seen:
                    seen.add(text)
                    options.append(text)
                if len(options) == 3:
                    break
            options.append(answer)
            r.shuffle(options)
            item = {"t": topic, "q": self.text, "o": options, "a": options.index(answer), "w": self.why}
        if self.svg:
            item["svg"] = self.svg
        return item


def quota(chapter, n_topics, minimum=30, chapter_floor=100):
    return max(minimum, math.ceil(chapter_floor / n_topics))


def build_chapter(chapter, minimum=30, chapter_floor=100, seed=2026):
    """-> (items shuffled so that types mix, {topic: count}). Raises nothing: thin topics show up in the counts."""
    r = random.Random(f"{seed}:{chapter}")
    items, counts = [], {}
    generated = TEMPLATES.get(chapter, {})
    written = HAND.get(chapter, {})
    topics = list(dict.fromkeys([*written, *generated]))
    per = quota(chapter, len(topics), minimum, chapter_floor)
    for topic in topics:
        seen, got = set(), []
        for q in written.get(topic, []):
            if q.key() not in seen:
                seen.add(q.key())
                got.append(q.build(topic, r))
        fns = generated.get(topic, [])
        attempts = 0
        while fns and len(got) < per and attempts < per * 60:
            q = fns[attempts % len(fns)](r)
            attempts += 1
            if q.key() in seen:
                continue
            seen.add(q.key())
            got.append(q.build(topic, r))
        items += got
        counts[topic] = len(got)
    r.shuffle(items)
    return items, counts
