"""
Converts one topic (a guide Part) from its PDF into a draft content file for the site.

It reads the PDF's real structure (fonts, positions, filled boxes), not just plain text:
  headings           bold, large         -> markdown headings
  code / terminal    monospace + tag     -> `code` blocks (indentation and blank lines preserved)
  callouts           filled boxes        -> `callout` blocks (note, gotcha, interview angle, key points)
  tables             header band + rows  -> `table` blocks
  check yourself     question + answers  -> `questions` blocks (collected into a Practice section)
  figures            caption + labels    -> `figure` blocks, to be turned into Mermaid diagrams by hand
  everything else    paragraphs, lists   -> markdown, with inline code / bold / italic kept

Only the chapters listed as subtopics of the topic in roadmap.json are extracted.

Usage:
  python -I tools/extract_topic.py <pdf> <roadmap.json> <topic-id> <out.json> [--preview]
Requires: pdfplumber
"""
import colorsys
import json
import math
import re
import sys
from pathlib import Path

import pdfplumber

LANG = {
    "JAVA": "java", "XML": "xml", "TERMINAL": "bash", "BASH": "bash", "SHELL": "bash", "SH": "bash",
    "SQL": "sql", "YAML": "yaml", "YML": "yaml", "JSON": "json", "PROPERTIES": "properties",
    "DOCKERFILE": "dockerfile", "JAVASCRIPT": "javascript", "JS": "javascript", "TYPESCRIPT": "typescript",
    "TS": "typescript", "JSX": "javascript", "TSX": "typescript", "HTML": "xml", "CSS": "css",
    "PYTHON": "python", "GROOVY": "groovy", "KOTLIN": "kotlin", "TEXT": "plaintext", "OUTPUT": "plaintext",
    "CONSOLE": "plaintext", "ASCII": "plaintext", "CONF": "ini", "TOML": "ini", "INI": "ini", "GO": "go",
    "C": "c", "CPP": "cpp", "REDIS": "plaintext", "HTTP": "http", "DIFF": "diff", "MAKEFILE": "makefile",
}
CALLOUT_VARIANT = {
    "NOTE": ("note", "Note"), "TIP": ("tip", "Tip"), "GOTCHA": ("warning", "Gotcha"),
    "WARNING": ("warning", "Warning"), "WATCH OUT": ("warning", "Watch out"),
    "REAL WORLD": ("realworld", "Real world"), "INTERVIEW ANGLE": ("interview", "Interview angle"),
    "KEY POINTS": ("keypoints", "Key points"), "IMPORTANT": ("important", "Important"),
    "DEFINITION": ("note", "Definition"), "REMEMBER": ("important", "Remember"),
    "EXAMPLE": ("note", "Example"), "PITFALL": ("warning", "Pitfall"),
}
MONO_ADVANCE = 0.602  # DejaVu Sans Mono advance width, in em
BULLETS = {"\x7f", "•", "–", "-", "▪"}


# ------------------------------------------------------------------ char helpers
def is_mono(c):
    return "Mono" in c["fontname"]


def is_bold(c):
    return "Bold" in c["fontname"]


def is_italic(c):
    return "Oblique" in c["fontname"] or "Italic" in c["fontname"]


def md_escape(text):
    return re.sub(r"([\\`*_\[\]<>])", r"\\\1", text)


def ctext(c):
    """Character text, normalising the bullet glyph pdfminer reports as '(cid:127)'."""
    t = c["text"]
    return "•" if t in ("", "(cid:127)") else t


def sorted_chars(chars):
    return sorted(chars, key=lambda c: c["x0"])


def gap_before(prev, c):
    return prev is not None and c["text"] != " " and prev["text"] != " " and c["x0"] - prev["x1"] > 0.25 * c["size"]


def chars_text(chars):
    """Plain text of chars, with spaces inferred from gaps."""
    out, prev = [], None
    for c in sorted_chars(chars):
        if gap_before(prev, c):
            out.append(" ")
        out.append(ctext(c))
        prev = c
    return "".join(out)


def chars_markdown(chars):
    """Inline markdown (code, bold, italic) from chars; monospace runs become code spans."""
    runs, prev = [], None
    for c in sorted_chars(chars):
        style = "code" if is_mono(c) else "bold" if is_bold(c) else "italic" if is_italic(c) else "plain"
        if c["text"] == " " and runs:
            style = runs[-1][0]  # spaces take the neighbouring style
        if gap_before(prev, c):
            # an inferred space joins neighbours of the same style (so "**two words**" stays one run)
            runs.append([style if runs and runs[-1][0] == style else "plain", " "])
        runs.append([style, ctext(c)])
        prev = c
    merged = []
    for style, text in runs:
        if merged and merged[-1][0] == style:
            merged[-1][1] += text
        else:
            merged.append([style, text])
    out = []
    for style, text in merged:
        core = text.strip()
        if not core:
            out.append(text)
            continue
        lead, trail = text[: len(text) - len(text.lstrip())], text[len(text.rstrip()):]
        if style == "code":
            body = "`" + core.replace("`", "'") + "`"
        elif style == "bold":
            body = "**" + md_escape(core) + "**"
        elif style == "italic":
            body = "*" + md_escape(core) + "*"
        else:
            body = md_escape(core)
        out.append(lead + body + trail)
    return re.sub(r"[ \t]+", " ", "".join(out)).strip()


def lines_of(chars):
    """Group chars into lines by vertical position."""
    groups = []
    for c in sorted(chars, key=lambda c: (round(c["top"]), c["x0"])):
        if groups and abs(groups[-1]["top"] - c["top"]) < 2.5:
            groups[-1]["chars"].append(c)
        else:
            groups.append({"top": c["top"], "chars": [c]})
    for g in groups:
        g["chars"].sort(key=lambda c: c["x0"])
        g["x0"] = g["chars"][0]["x0"]
        g["x1"] = g["chars"][-1]["x1"]
        g["bottom"] = max(c["bottom"] for c in g["chars"])
    return groups


def classify_line(line):
    chars = [c for c in line["chars"] if c["text"].strip()]
    if not chars:
        return None
    n = len(chars)
    return {
        "size": max(c["size"] for c in chars),
        "mono": sum(is_mono(c) for c in chars) / n,
        "bold": sum(is_bold(c) and not is_mono(c) for c in chars) / n,
    }


# ------------------------------------------------------------------ per-page analysis
def find_tables(page, consumed):
    """Tables are a dark header band followed by touching row bands."""
    rects = sorted((r for r in page.rects if r["x1"] - r["x0"] > 400 and r["bottom"] - r["top"] > 8),
                   key=lambda r: r["top"])
    tables, i = [], 0
    while i < len(rects):
        fill = rects[i].get("non_stroking_color") or ()
        dark = isinstance(fill, (tuple, list)) and len(fill) == 3 and sum(fill) < 1.2
        if not dark:
            i += 1
            continue
        bands, j = [rects[i]], i + 1
        while j < len(rects) and abs(rects[j]["top"] - bands[-1]["bottom"]) < 1.5:
            bands.append(rects[j])
            j += 1
        i = j
        if len(bands) < 2:
            continue
        top, bottom = bands[0]["top"], bands[-1]["bottom"]
        in_table = [c for c in page.chars if top - 1 <= c["top"] and c["bottom"] <= bottom + 1 and c["text"].strip()]
        head = sorted_chars(c for c in in_table if c["top"] < bands[0]["bottom"])
        starts, prev = [], None
        for c in head:  # column starts: runs of header chars separated by wide gaps
            if prev is None or c["x0"] - prev["x1"] > 10:
                starts.append(c["x0"])
            prev = c
        rows = []
        for b in bands:
            cells = [[] for _ in starts]
            for c in (c for c in in_table if b["top"] - 1 <= c["top"] and c["bottom"] <= b["bottom"] + 1):
                cells[max((k for k, s in enumerate(starts) if s <= c["x0"] + 3), default=0)].append(c)
            rows.append([" ".join(chars_markdown(g["chars"]) for g in lines_of(chars)) for chars in cells])
        consumed.update(id(c) for c in in_table)
        tables.append({"kind": "table", "top": top, "headers": [h.replace("**", "") for h in rows[0]],
                       "rows": rows[1:], "rects": bands})
    return tables


def find_callouts(page, consumed):
    out = []
    for r in page.rects:
        if r["x1"] - r["x0"] < 400 or r["bottom"] - r["top"] < 25:
            continue
        inside = [c for c in page.chars if r["top"] - 1 <= c["top"] and c["bottom"] <= r["bottom"] + 1
                  and id(c) not in consumed and c["text"].strip()]
        if not inside:
            continue
        first_top = min(c["top"] for c in inside)
        label_chars = [c for c in inside if abs(c["top"] - first_top) < 2]
        label = chars_text(label_chars).strip().upper()
        if label not in CALLOUT_VARIANT or not all(is_bold(c) for c in label_chars):
            continue
        consumed.update(id(c) for c in inside)
        out.append({"kind": "callout", "top": r["top"], "label": label, "rect": r,
                    "chars": [c for c in inside if c["top"] - first_top >= 2]})
    return out


# ------------------------------------------------------------------ figures as dark-themed SVG
def color_rgb(c):
    if c is None:
        return None
    if isinstance(c, (int, float)):
        c = (c,)
    c = tuple(c)
    if len(c) == 1:
        return (c[0],) * 3
    if len(c) == 3:
        return c
    if len(c) == 4:
        cc, m, y, k = c
        return ((1 - cc) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))
    return None


def hex_color(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * 255))) for v in rgb)


def theme_color(color, role):
    """Map a colour drawn for white paper to one that works on the site's dark background."""
    rgb = color_rgb(color)
    if rgb is None:
        return "none"
    h, l, sat = colorsys.rgb_to_hls(*rgb)
    if role == "fill":
        if l >= 0.6:
            if sat < 0.12:
                return "#1c1c1c" if l >= 0.93 else "#242424"
            return hex_color(colorsys.hls_to_rgb(h, min(0.4, max(0.16, 1 - l)), sat * 0.8))
        return hex_color(rgb)
    if role == "stroke":
        if sat < 0.15:
            return "#9a9a9a" if l < 0.7 else "#3a3a3a"
        return hex_color(colorsys.hls_to_rgb(h, max(l, 0.6), sat))
    # text
    if l < 0.55:
        return "#e7e9f3" if sat < 0.25 else hex_color(colorsys.hls_to_rgb(h, 0.78, sat))
    return hex_color(rgb)


def xml_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def drawing_path(obj, ox, oy):
    parts = []
    for op in obj["path"]:
        kind = op[0]
        pts = " ".join(f"{x - ox:.1f} {y - oy:.1f}" for x, y in op[1:])
        parts.append({"m": "M", "l": "L", "c": "C", "h": "Z"}[kind] + pts if kind != "h" else "Z")
    return " ".join(parts)


def svg_for_region(drawings, chars, box):
    """Render drawings and text inside box=(x0, top, x1, bottom) to an SVG string."""
    x0, top, x1, bottom = box
    width, height = x1 - x0, bottom - top
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
           f'font-family="Inter Variable, ui-sans-serif, system-ui, sans-serif">']
    for obj in drawings:
        fill = theme_color(obj.get("non_stroking_color"), "fill") if obj.get("fill") else "none"
        stroke = theme_color(obj.get("stroking_color"), "stroke") if obj.get("stroke") else "none"
        attrs = f'fill="{fill}" stroke="{stroke}"'
        if stroke != "none":
            attrs += f' stroke-width="{max(obj.get("linewidth") or 0.5, 0.5):.2f}" stroke-linejoin="round"'
            dash = obj.get("dash")
            if dash and dash[0]:
                attrs += f' stroke-dasharray="{" ".join(f"{d:.1f}" for d in dash[0])}"'
        if obj.get("evenodd"):
            attrs += ' fill-rule="evenodd"'
        out.append(f'<path d="{drawing_path(obj, x0, top)}" {attrs}/>')
    # rotated labels (axes, vertical annotations): one text element per column of characters
    columns = {}
    for c in chars:
        if not c.get("upright", True):
            columns.setdefault(round(c["x0"]), []).append(c)
    for col in columns.values():
        m = col[0]["matrix"]
        fs = math.hypot(m[0], m[1]) or col[0]["size"]
        upward = m[1] > 0
        col.sort(key=lambda c: -c["top"] if upward else c["top"])
        text, prev = "", None
        for c in col:
            gap = 0 if prev is None else (prev["top"] - c["bottom"] if upward else c["top"] - prev["bottom"])
            text += (" " if gap > 0.25 * fs else "") + ctext(c)
            prev = c
        length = abs((col[0]["bottom"] if upward else col[0]["top"]) - (col[-1]["top"] if upward else col[-1]["bottom"]))
        px = (col[0]["x1"] - 0.236 * fs) if upward else (col[0]["x0"] + 0.236 * fs)
        py = col[0]["bottom"] if upward else col[0]["top"]
        out.append(
            f'<text transform="translate({px - x0:.1f} {py - top:.1f}) rotate({-90 if upward else 90})" '
            f'font-size="{fs:.1f}" fill="{theme_color(col[0].get("non_stroking_color"), "text")}" '
            f'textLength="{length:.1f}" lengthAdjust="spacingAndGlyphs">{xml_escape(text.strip())}</text>')

    for line in lines_of([c for c in chars if c.get("upright", True)]):
        # split a line into runs: a wide gap or a style change starts a new text element
        runs, prev = [], None
        for c in line["chars"]:
            style = (is_mono(c), is_bold(c), is_italic(c), round(c["size"], 1))
            if prev is None or style != runs[-1]["style"] or c["x0"] - prev["x1"] > 0.9 * c["size"]:
                runs.append({"style": style, "chars": []})
            runs[-1]["chars"].append(c)
            prev = c
        for run in runs:
            cs = run["chars"]
            text = chars_text(cs).strip()
            if not text:
                continue
            mono, bold, italic, size = run["style"]
            start = next(c for c in cs if c["text"].strip())
            end = cs[-1]
            length = end["x1"] - start["x0"]
            attrs = (f'x="{start["x0"] - x0:.1f}" y="{start["bottom"] - 0.236 * start["size"] - top:.1f}" '
                     f'font-size="{size}" fill="{theme_color(start.get("non_stroking_color"), "text")}"')
            if mono:
                attrs += ' font-family="JetBrains Mono Variable, ui-monospace, monospace"'
            if bold:
                attrs += ' font-weight="700"'
            if italic:
                attrs += ' font-style="italic"'
            if len(text) > 1 and length > 0:
                attrs += f' textLength="{length:.1f}" lengthAdjust="spacingAndGlyphs"'
            out.append(f"<text {attrs}>{xml_escape(text)}</text>")
    out.append("</svg>")
    return "".join(out)


def figure_region(page, drawings, caption_top, label_top=None):
    """The drawings that form the figure just above a caption, or None.

    label_top is the top of the small-print text block above the caption (titles, descriptions, notes):
    the drawings may sit well above the caption when there is such text between them.
    """
    above = [d for d in drawings if d["bottom"] <= caption_top + 1]
    reach = caption_top - 100 if label_top is None else min(caption_top - 100, label_top - 70)
    near = [d for d in above if d["bottom"] >= reach]
    if not near:
        return None
    cluster = [max(near, key=lambda d: d["bottom"])]
    changed = True
    while changed:
        changed = False
        top = min(d["top"] for d in cluster)
        for d in above:
            if d not in cluster and d["bottom"] >= top - 20:
                cluster.append(d)
                changed = True
    return cluster


def is_code_like(line):
    info = classify_line(line)
    if not info:
        return False
    tiny = [c for c in line["chars"] if c["size"] <= 6.9 and c["text"].strip()]
    return (info["mono"] >= 0.85 and line["x0"] >= 59) or (bool(tiny) and line["x1"] > 470 and info["size"] <= 7.0)


def page_elements(page):
    # the PDFs carry a huge, faint background watermark made of oversized characters: ignore it
    page = page.filter(lambda o: o.get("object_type") != "char" or o["size"] <= 30)
    consumed = set()
    tables, callouts = find_tables(page, consumed), find_callouts(page, consumed)
    elements = tables + callouts
    skip = {id(r) for t in tables for r in t["rects"]} | {id(c["rect"]) for c in callouts}
    lines = lines_of([c for c in page.chars if id(c) not in consumed and c["text"].strip() and 40 <= c["top"] <= 800])
    code_boxes = [(l["x0"], l["top"], l["x1"], l["bottom"]) for l in lines if is_code_like(l)]

    def usable(d):
        w, h = d["x1"] - d["x0"], d["bottom"] - d["top"]
        if id(d) in skip or d["top"] < 40 or d["bottom"] > 800:
            return False
        if w > 440 and h < 4:  # section rules
            return False
        if w <= 4.5 and 8 <= h <= 24:  # the little accent bar beside a sub-heading
            return False
        if d["x0"] == d["x1"] and d["x0"] < 51 and (d.get("linewidth") or 0) >= 2.5:  # callout accent bar
            return False
        if w > 440 and h > 60:  # code boxes and panels
            return False
        if w > 440 and any(not (d["x1"] < bx0 or d["x0"] > bx1 or d["bottom"] < bt or d["top"] > bb)
                           for bx0, bt, bx1, bb in code_boxes):
            return False
        return True

    drawings = [d for d in page.rects + page.lines + page.curves if usable(d)]

    def inside_drawing(line):
        """True when most of the line's characters sit inside a drawn shape (a label in a box)."""
        chars = [c for c in line["chars"] if c["text"].strip()]
        inside = sum(1 for c in chars if any(
            d["x0"] - 2 <= c["x0"] and c["x1"] <= d["x1"] + 2 and d["top"] - 2 <= c["top"] and c["bottom"] <= d["bottom"] + 2
            for d in drawings))
        return bool(chars) and inside / len(chars) >= 0.6
    chars_free = [c for c in page.chars if id(c) not in consumed and c["text"].strip() and 40 <= c["top"] <= 800]

    used = set()
    for idx, ln in enumerate(lines):
        text = chars_text(ln["chars"])
        if not (re.match(r"Figure \d+\.\d+\.", text) and all(is_italic(c) for c in ln["chars"] if c["text"].strip())):
            continue
        caption, k = [text], idx + 1
        while (k < len(lines) and lines[k]["top"] - lines[k - 1]["bottom"] < 6
               and max(c["size"] for c in lines[k]["chars"]) <= 8.4
               and all(is_italic(c) for c in lines[k]["chars"] if c["text"].strip())):
            caption.append(chars_text(lines[k]["chars"]))
            used.add(k)
            k += 1
        used.add(idx)

        label_top, j = None, idx - 1  # small-print text block directly above the caption
        while j >= 0:
            info = classify_line(lines[j])
            if not info or info["size"] >= 8.6 or j in used:
                break
            if info["mono"] > 0.5 and not inside_drawing(lines[j]):
                break  # a code listing, not a label inside a box
            label_top = lines[j]["top"]
            j -= 1
        cluster = figure_region(page, drawings, ln["top"], label_top)
        if cluster:
            top = min(d["top"] for d in cluster) - 2
            if label_top is not None:
                top = min(top, label_top - 1)
            box = (min(d["x0"] for d in cluster) - 2, top, max(d["x1"] for d in cluster) + 2, ln["top"] - 1)
            box = (box[0], box[1], box[2], max(box[3], max(d["bottom"] for d in cluster) + 2))
            # small text just above the drawings is part of the figure (group titles and the like)
            for other in lines:
                info = classify_line(other)
                if (info and info["size"] <= 8.6 and info["mono"] < 0.5 and box[1] - 45 <= other["bottom"] <= box[1] + 1
                        and not is_code_like(other) and box[0] - 2 <= other["x0"] <= box[2]):
                    box = (box[0], min(box[1], other["top"] - 1), box[2], box[3])
            inside = [c for c in chars_free if box[1] <= c["top"] and c["bottom"] <= box[3] + 1]
            if inside:  # labels may stick out past the drawings (annotations beside a diagram)
                box = (min(box[0], min(c["x0"] for c in inside) - 2), box[1],
                       max(box[2], max(c["x1"] for c in inside) + 2), box[3])
            labels = [chars_text(l["chars"]) for l in lines_of([c for c in inside if c.get("upright", True)])]
            for j, other in enumerate(lines):
                if j != idx and box[1] <= other["top"] and other["bottom"] <= box[3] + 1:
                    used.add(j)
            elements.append({"kind": "figure", "top": box[1], "caption": " ".join(caption), "labels": labels,
                             "svg": svg_for_region(cluster, inside, box), "width": round(box[2] - box[0])})
            continue

        labels, j = [], idx - 1  # no drawing found: keep the text labels only
        while j >= 0:
            info = classify_line(lines[j])
            if not info or info["mono"] > 0.5 or info["size"] >= 8.6 or j in used:
                break
            labels.append(chars_text(lines[j]["chars"]))
            used.add(j)
            j -= 1
        elements.append({"kind": "figure", "top": lines[j + 1]["top"] if labels else ln["top"],
                         "caption": " ".join(caption), "labels": list(reversed(labels))})
    elements += [{"kind": "line", "top": ln["top"], "line": ln} for idx, ln in enumerate(lines) if idx not in used]
    return sorted(elements, key=lambda e: e["top"])


# ------------------------------------------------------------------ flow assembly
class Flow:
    """Accumulates the blocks of the current chapter."""

    def __init__(self):
        self.blocks, self.text = [], []  # text: pending markdown fragments
        self.para, self.para_bottom = [], None
        self.list_items, self.list_x = [], 0
        self.code = None
        self.pending_table = None
        self.qa = {"mode": None, "q": [], "a": []}

    def flush_para(self):
        if self.para:
            self.text.append(" ".join(self.para))
        self.para, self.para_bottom = [], None

    def flush_list(self):
        if self.list_items:
            ordered = self.list_items[0][0] == "ol"
            self.text.append("\n".join(
                f"{i}. {item}" if ordered else f"- {item}" for i, (_, item) in enumerate(self.list_items, 1)))
        self.list_items = []

    def flush_text(self):
        self.flush_para()
        self.flush_list()
        if self.text:
            self.blocks.append({"type": "markdown", "text": "\n\n".join(self.text)})
        self.text = []

    def flush_code(self):
        code, self.code = self.code, None
        if not code or not code["lines"]:
            return
        lines = code["lines"]
        origin = min(l["x0"] for l in lines)
        pitches = sorted(b["top"] - a["top"] for a, b in zip(lines, lines[1:]) if b["top"] > a["top"])
        pitch = pitches[len(pitches) // 2] if pitches else 10
        out = []
        for i, l in enumerate(lines):
            if i:
                out.extend([""] * max(0, round((l["top"] - lines[i - 1]["top"]) / pitch) - 1))
            width = next(c["size"] for c in l["chars"] if c["text"].strip()) * MONO_ADVANCE
            text = ""
            for c in l["chars"]:
                text = text.ljust(round((c["x0"] - origin) / width)) + c["text"]
            out.append(text.rstrip())
        body = "\n".join(out)
        if code.get("append_to") is not None:
            code["append_to"]["code"] += "\n" + body
            return
        block = {"type": "code", "language": code["language"], "code": body}
        if code["caption"]:
            block["title"] = code["caption"]
        self.blocks.append(block)

    def flush_all(self):
        self.flush_code()
        self.flush_text()

    def finish_qa(self):
        q, a = self.qa["q"], self.qa["a"]
        if q and len(q) == len(a):
            return [{"question": x, "answer": y} for x, y in zip(q, a)]
        return [{"question": x} for x in q]


def convert(pdf, wanted, page_range):
    """-> [{num, title, blocks, qa}] for the wanted chapters, in document order."""
    chapters, current, flow = [], None, Flow()

    def close_chapter():
        nonlocal current
        if current is not None:
            flow.flush_all()
            current.update(blocks=flow.blocks, qa=flow.finish_qa())
            chapters.append(current)
        current = None

    for pno in range(page_range[0], page_range[1] + 1):
        for el in page_elements(pdf.pages[pno - 1]):
            if el["kind"] == "line":
                info = classify_line(el["line"])
                if not info:
                    continue
                text = chars_text(el["line"]["chars"]).strip()
                if re.fullmatch(r"PART \d+", text):  # the next part's cover page ends this chapter
                    close_chapter()
                    flow = Flow()
                    continue
                m = re.match(r"(\d+\.\d+)\s+(.+)$", text)
                if info["bold"] > 0.8 and info["size"] >= 14 and m:
                    close_chapter()
                    flow = Flow()
                    if m.group(1) in wanted:
                        current = {"num": m.group(1), "title": m.group(2).strip()}
                elif current is not None:
                    handle_line(flow, el["line"], info, text)
            elif current is not None:
                handle_element(flow, el)
    close_chapter()
    return chapters


def handle_element(flow, el):
    flow.flush_code()
    flow.flush_text()
    flow.pending_table = None
    flow.qa["mode"] = None
    if el["kind"] == "table":
        flow.pending_table = {"type": "table", "headers": el["headers"], "rows": el["rows"]}
        flow.blocks.append(flow.pending_table)
    elif el["kind"] == "callout":
        variant, title = CALLOUT_VARIANT[el["label"]]
        flow.blocks.append({"type": "callout", "variant": variant, "title": title,
                            "text": callout_markdown(el["chars"])})
    elif el["kind"] == "figure":
        caption = re.sub(r"^Figure \d+\.\d+\.\s*", "", el["caption"]).strip()
        if el.get("svg"):
            flow.blocks.append({"type": "diagram", "format": "svg", "svg": el["svg"], "width": el["width"],
                                "caption": caption, "alt": " | ".join(el["labels"])})
        else:
            flow.blocks.append({"type": "figure", "caption": caption, "labels": el["labels"]})


def callout_markdown(chars):
    parts, para, items, last = [], [], [], None
    for ln in lines_of(chars):
        text = chars_text(ln["chars"]).strip()
        md = chars_markdown(ln["chars"])
        if text[:1] in BULLETS and text[1:2] == " ":
            if para:
                parts.append(" ".join(para))
                para = []
            items.append("- " + re.sub(r"^•\s*", "", md).strip())
        elif items and ln["x0"] > last["x0"] + 4:
            items[-1] += " " + md
        else:
            if items:
                parts.append("\n".join(items))
                items = []
            if para and ln["top"] - last["bottom"] > 5:
                parts.append(" ".join(para))
                para = []
            para.append(md)
        last = ln
    if para:
        parts.append(" ".join(para))
    if items:
        parts.append("\n".join(items))
    return "\n\n".join(parts)


def handle_line(flow, ln, info, text):
    chars = [c for c in ln["chars"] if c["text"].strip()]
    qa = flow.qa

    # caption under a table
    if flow.pending_table is not None:
        table, flow.pending_table = flow.pending_table, None
        if all(is_italic(c) or is_mono(c) for c in chars) and any(is_italic(c) for c in chars) and len(text) < 90:
            table["caption"] = text
            return

    # code tag line: small caps language at the right, optional bold caption on the left
    small = [c for c in chars if c["size"] <= 6.9 and not is_mono(c)]
    tag = chars_text([c for c in small if not is_bold(c)]).strip()
    if small and re.fullmatch(r"[A-Z][A-Z0-9+#]*", tag) and ln["x1"] > 470 and info["size"] <= 7.0:
        caption = chars_text([c for c in small if is_bold(c)]).strip()
        flow.flush_code()
        flow.flush_text()
        last = flow.blocks[-1] if flow.blocks else None
        if re.search(r"\(continued\)", caption, re.I) and last and last["type"] == "code":
            flow.code = {"language": last["language"], "caption": "", "lines": [], "append_to": last}
        else:
            flow.code = {"language": LANG.get(tag, tag.lower()), "caption": caption, "lines": []}
        return

    # an indented, mostly-monospace line right after a list item or a question continues that item
    continues_item = flow.code is None and (qa["mode"] or (flow.list_items and ln["x0"] > flow.list_x + 4))

    # code lines
    if info["mono"] >= 0.85 and not continues_item and (flow.code is not None or ln["x0"] >= 59):
        if flow.code is None:
            flow.flush_text()
            flow.code = {"language": "plaintext", "caption": "", "lines": []}
        flow.code["lines"].append(ln)
        return
    flow.flush_code()

    md = chars_markdown(ln["chars"])

    # headings
    if info["bold"] > 0.8 and info["size"] >= 11:
        flow.flush_para()
        flow.flush_list()
        qa["mode"] = None
        flow.text.append("### " + re.sub(r"^\d+(\.\d+)+\s+", "", text))
        return
    if info["bold"] > 0.8 and info["size"] >= 9.4 and len(text) < 90:
        flow.flush_para()
        flow.flush_list()
        low = text.lower()
        qa["mode"] = "q" if low == "check yourself" else "a" if low == "answers" else None
        if qa["mode"] is None:
            flow.text.append("#### " + text)
        return

    bullet = text[:1] in BULLETS and text[1:2] == " "
    numbered = re.match(r"\d+\.\s", text)

    # "Check yourself" questions and their answers
    if qa["mode"]:
        target = qa["q"] if qa["mode"] == "q" else qa["a"]
        if numbered:
            target.append(re.sub(r"^\d+\.\s+", "", md))
        elif target:
            target[-1] += " " + md
        return

    # lists
    if bullet or numbered:
        flow.flush_para()
        kind = "ul" if bullet else "ol"
        if flow.list_items and flow.list_items[0][0] != kind:
            flow.flush_list()
        flow.list_items.append((kind, re.sub(r"^(•|\d+\.)\s*", "", md).strip()))
        flow.list_x = ln["x0"]
        return
    if flow.list_items and ln["x0"] > flow.list_x + 4:
        kind, item = flow.list_items[-1]
        flow.list_items[-1] = (kind, item + " " + md)
        return
    flow.flush_list()

    # paragraphs
    if flow.para and flow.para_bottom is not None and ln["top"] - flow.para_bottom > 5.5:
        flow.flush_para()
    flow.para.append(md)
    flow.para_bottom = ln["bottom"]


def extract(pdf, topic):
    """Extract one topic from an open pdfplumber PDF -> (content dict, set of chapters not found)."""
    wanted = {}
    for s in topic["subtopics"]:
        a, b = s["pages"].split("-")
        wanted[s["id"].replace("-", ".")] = {"sub": s, "start": int(a), "end": int(b)}
    # the page after the last chapter is included too: the next chapter often starts mid-page,
    # after this chapter's last answers and key points
    page_range = (min(w["start"] for w in wanted.values()),
                  min(max(w["end"] for w in wanted.values()) + 1, len(pdf.pages)))
    chapters = convert(pdf, wanted, page_range)

    sections, practice = [], []
    for ch in chapters:
        sub = wanted[ch["num"]]["sub"]
        sections.append({"id": "ch-" + sub["id"], "type": "concept", "title": sub["title"],
                         "subtopicId": sub["id"], "blocks": ch["blocks"]})
        if ch["qa"]:
            practice.append({"type": "markdown", "text": f"#### {sub['title']}"})
            practice.append({"type": "questions", "items": ch["qa"]})
    if practice:
        sections.append({"id": "practice", "type": "practice", "title": "Practice questions", "blocks": practice})
    missing = set(wanted) - {c["num"] for c in chapters}
    return {"source": topic["source"], "sections": sections}, missing


def front_matter(pdf, first_page):
    """The guide's opening pages ("How to use this guide" and similar), up to its table of contents."""
    flow = Flow()
    for pno in range(2, first_page):
        for el in page_elements(pdf.pages[pno - 1]):
            if el["kind"] != "line":
                handle_element(flow, el)
                continue
            info = classify_line(el["line"])
            if not info:
                continue
            text = chars_text(el["line"]["chars"]).strip()
            if text.lower() in ("contents", "table of contents"):
                flow.flush_all()
                return flow.blocks
            handle_line(flow, el["line"], info, text)
    flow.flush_all()
    return flow.blocks


def summary(content):
    kinds = {}
    for s in content["sections"]:
        for b in s["blocks"]:
            kinds[b["type"]] = kinds.get(b["type"], 0) + 1
    return kinds


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--doc" in flags:
        # batch mode: <pdf folder> <roadmap.json> <pdf file name> <topics out dir> [--force]
        folder, roadmap_path, doc, out_dir = args[:4]
        roadmap = json.loads(Path(roadmap_path).read_text(encoding="utf-8"))
        topics = [t for t in roadmap["topics"] if t.get("source", {}).get("document") == doc]
        with pdfplumber.open(Path(folder) / doc) as pdf:
            for topic in topics:
                target = Path(out_dir) / f"{topic['id']}.json"
                if target.exists() and "--force" not in flags:
                    print(f"{topic['id']}: exists, skipped", flush=True)
                    continue
                content, missing = extract(pdf, topic)
                if topic["id"].endswith("-part-1"):
                    blocks = front_matter(pdf, int(topic["source"]["pages"].split("-")[0]))
                    if blocks:
                        content["sections"].insert(0, {"id": "about-this-guide", "type": "introduction",
                                                       "title": "About this guide", "blocks": blocks})
                target.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"{topic['id']}: {summary(content)}"
                      + (f"  CHAPTERS NOT FOUND: {sorted(missing)}" if missing else ""), flush=True)
        return

    pdf_path, roadmap_path, topic_id, out_path = args[:4]
    roadmap = json.loads(Path(roadmap_path).read_text(encoding="utf-8"))
    topic = next(t for t in roadmap["topics"] if t["id"] == topic_id)
    with pdfplumber.open(pdf_path) as pdf:
        content, missing = extract(pdf, topic)
    Path(out_path).write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(content['sections'])} sections, {summary(content)}"
          + (f"; chapters not found: {sorted(missing)}" if missing else ""))
    if "--preview" in flags:
        for s in content["sections"]:
            print("\n##", s["title"])
            for b in s["blocks"]:
                body = b.get("text") or b.get("code") or b.get("caption") or ""
                if b["type"] == "questions":
                    body = f"{len(b['items'])} questions"
                print(f"  [{b['type']}] {str(body)[:110]!r}")


if __name__ == "__main__":
    main()
