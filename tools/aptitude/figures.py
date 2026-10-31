"""Non-verbal reasoning and data interpretation: figures are drawn as SVG, and answers come from the same data."""
import math
from math import comb

from core import F, Q, T, fmt

C = "Non-Verbal Reasoning"
INK = "#1f2937"
ACCENT = "#6366f1"


def svg(body, w=64, h=64):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def arrow(angle, cx=32, cy=32):
    """An arrow with a side flag, so rotations and mirror images all look different."""
    return (f'<g transform="rotate({angle} {cx} {cy})" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round">'
            f'<path d="M{cx} {cy + 22}V{cy - 22}M{cx} {cy - 22}l-9 10M{cx} {cy - 22}l9 10M{cx} {cy + 6}h13"/></g>')


def polygon(sides, fill=False, cx=32, cy=32, rad=23):
    pts = " ".join(f"{cx + rad * math.sin(2 * math.pi * i / sides):.1f},{cy - rad * math.cos(2 * math.pi * i / sides):.1f}" for i in range(sides))
    return f'<polygon points="{pts}" fill="{ACCENT if fill else "none"}" stroke="{INK}" stroke-width="3"/>'


def dots(n, cx=32, cy=32):
    pos = [(i % 3, i // 3) for i in range(n)]
    return "".join(f'<circle cx="{cx - 13 + 13 * a}" cy="{cy - 13 + 13 * b}" r="4.5" fill="{INK}"/>' for a, b in pos)


def strip(figures, slot=True):
    """Figures in a row; the last place is a question mark."""
    w = 70
    body = ""
    for i, fig in enumerate(figures):
        body += f'<g transform="translate({i * w + 3} 3)"><rect x="0" y="0" width="64" height="64" fill="none" stroke="#cbd5e1"/>{fig}</g>'
    if slot:
        i = len(figures)
        body += f'<g transform="translate({i * w + 3} 3)"><rect x="0" y="0" width="64" height="64" fill="none" stroke="#cbd5e1" stroke-dasharray="4"/><text x="32" y="43" text-anchor="middle" font-size="30" font-family="sans-serif" fill="{INK}">?</text></g>'
    return svg(body, w * (len(figures) + (1 if slot else 0)) + 3, 70)


def choices(right, wrong):
    return [svg(right)] + [svg(x) for x in wrong[:3]]


@T(C, "Series (figures)")
def _(r):
    step = r.choice([45, 90, 135])
    start = r.choice(range(0, 360, 45))
    seq = [(start + i * step) % 360 for i in range(5)]
    wrong = [(seq[4] + d) % 360 for d in (45, 90, 180, 270, 315) if d != step]
    r.shuffle(wrong)
    return Q(f"Each figure rotates by the same angle. Which figure comes next?", "", f"The arrow turns {step}° clockwise each time, so the next is at {seq[4]}°.", [], strip([arrow(a) for a in seq[:4]]), choices(arrow(seq[4]), [arrow(a) for a in wrong]))


@T(C, "Series (figures)")
def _(r):
    s = r.randint(1, 4)
    n = [s + i for i in range(5)]
    wrong = [n[4] + 1, n[4] - 1, n[4] + 2]
    return Q(f"The dots follow a pattern. Which figure comes next?", "", f"One dot is added each time, giving {n[4]}.", [], strip([dots(x) for x in n[:4]]), choices(dots(n[4]), [dots(x) for x in wrong]))


@T(C, "Series (figures)")
def _(r):
    s = r.randint(3, 5)
    fill = r.choice([True, False])
    seq = [polygon(s + i, fill) for i in range(4)]
    return Q(f"Which figure comes next?", "", f"Each figure has one more side, so the next has {s + 4}.", [], strip(seq), choices(polygon(s + 4, fill), [polygon(s + 3, fill), polygon(s + 5, fill), polygon(s + 4, not fill)]))


@T(C, "Analogy (figures)")
def _(r):
    a, d = r.choice(range(0, 360, 45)), r.choice([90, 180, 45])
    c = (a + r.choice([45, 90, 135, 225])) % 360
    ans = (c + d) % 360
    wrong = [(ans + x) % 360 for x in (45, 90, 180)]
    return Q(f"First pair: figure 1 becomes figure 2. Apply the same change to figure 3. Which figure completes the analogy?", "", f"The change is a clockwise turn of {d}°.", [], strip([arrow(a), arrow((a + d) % 360), arrow(c)]), choices(arrow(ans), [arrow(x) for x in wrong]))


@T(C, "Analogy (figures)")
def _(r):
    a, c = r.sample(range(3, 9), 2)
    return Q(f"Figure 1 becomes figure 2. Apply the same change to figure 3. Which figure completes the analogy?", "", "The change fills the shape, keeping the same number of sides.", [], strip([polygon(a), polygon(a, True), polygon(c)]), choices(polygon(c, True), [polygon(c), polygon(c + 1, True), polygon(a if a != c + 1 else c + 2, True)]))


@T(C, "Analogy (figures)")
def _(r):
    a, k, c = r.randint(1, 3), r.randint(1, 2), r.randint(1, 4)
    return Q(f"Figure 1 becomes figure 2. Apply the same change to figure 3. Which figure completes the analogy?", "", f"The change adds {k} dot{'s' if k > 1 else ''}.", [], strip([dots(a), dots(a + k), dots(c)]), choices(dots(c + k), [dots(c), dots(c + k + 1), dots(c + k + 2)]))


@T(C, "Odd one out (figures)")
def _(r):
    sides = r.choice([3, 4, 5, 6, 7, 8])
    other = r.choice([x for x in (3, 4, 5, 6, 7, 8) if x != sides])
    fills = [r.choice([True, False]) for _ in range(3)]
    sizes = r.sample([14, 17, 20, 23, 26], 3)
    return Q("Which figure is the odd one out?", "", f"Three figures have {sides} sides; the odd one has {other}.", [], None, choices(polygon(other, r.choice([True, False]), rad=r.choice([14, 20, 26])), [polygon(sides, f, rad=s) for f, s in zip(fills, sizes)]))


@T(C, "Odd one out (figures)")
def _(r):
    # three rotations of the same arrow and one mirror image
    a, b, c = r.sample(range(0, 360, 45), 3)
    m = r.choice(range(0, 360, 45))
    mirrored = f'<g transform="translate(64 0) scale(-1 1)">{arrow(m)}</g>'
    return Q(f"Three figures are rotations of one figure, and one is its mirror image. Which is the mirror image?", "", "The side flag lies on the opposite side in the mirror image, however you rotate it.", [], None, choices(mirrored, [arrow(a), arrow(b), arrow(c)]))


@T(C, "Odd one out (figures)")
def _(r):
    n = r.randint(2, 6)
    odd = r.choice([x for x in range(1, 9) if x % 2 != n % 2])
    others = r.sample([x for x in range(1, 9) if x % 2 == n % 2], 3)
    word = "odd" if odd % 2 else "even"
    return Q(f"Which figure is the odd one out?", "", f"It alone has an {word} number of dots.", [], None, choices(dots(odd), [dots(x) for x in others]))


MIRROR_LETTERS = "AHIMOTUVWXY"
NOT_SAME = "BCDEFGJKLNPQRSZ"
WATER_SAME = "BCDEHIKOX"


@T(C, "Mirror & water images")
def _(r):
    h, m = r.randint(1, 12), r.choice(range(0, 60, 5))
    total = (720 - (h % 12) * 60 - m) % 720
    hh, mm = total // 60 or 12, total % 60
    ans = f"{hh}:{mm:02d}"
    return Q(f"A clock shows {h}:{m:02d}. What time does its mirror image appear to show?", ans, "Subtract the time from 12:00 (the mirror time plus the actual time equals 12:00).", [f"{h}:{(60 - m) % 60:02d}", f"{(hh % 12) + 1}:{mm:02d}", f"{hh}:{(mm + 5) % 60:02d}", f"{(h % 12) + 1}:{m:02d}"])


@T(C, "Mirror & water images")
def _(r):
    good = r.choice(MIRROR_LETTERS)
    bad = r.sample(NOT_SAME, 4)
    return Q("Which capital letter looks the same in a vertical mirror (one standing beside it)?", good, f"{good} is symmetric about a vertical line.", bad)


@T(C, "Mirror & water images")
def _(r):
    good = r.choice(WATER_SAME)
    bad = r.sample("AFGJLMNPQRSTUVWYZ", 4)
    return Q("Which capital letter looks the same in water (a horizontal mirror below it)?", good, f"{good} is symmetric about a horizontal line.", bad)


@T(C, "Mirror & water images")
def _(r):
    a = r.choice(range(0, 360, 45))
    mirrored = f'<g transform="translate(64 0) scale(-1 1)">{arrow(a)}</g>'
    flip = f'<g transform="translate(0 64) scale(1 -1)">{arrow(a)}</g>'
    return Q(f"Which option is the mirror image of this figure, with the mirror on its right?", "", "A vertical mirror swaps left and right but keeps top and bottom.", [], strip([arrow(a)], False), choices(mirrored, [arrow(a), arrow((a + 90) % 360), flip]))


@T(C, "Paper folding & cutting")
def _(r):
    folds, holes = r.randint(1, 5), r.randint(1, 6)
    return Q(f"A square sheet is folded in half {folds} time{'s' if folds > 1 else ''}, each fold doubling the thickness. {holes} hole{'s are' if holes > 1 else ' is'} punched through all layers. How many holes appear when it is unfolded?", holes * 2 ** folds, f"Each fold doubles the holes: {holes} × 2^{folds} = {holes * 2 ** folds}.", [holes * folds, holes + 2 ** folds, holes * 2 ** (folds + 1)])


@T(C, "Paper folding & cutting")
def _(r):
    n = r.randint(1, 4)
    k = 2 ** n
    s = r.choice([8, 12, 16, 20, 24, 32, 40, 48])
    return Q(f"A {s} cm square is folded in half {n} time{'s' if n > 1 else ''}, each time along lines parallel to the same side. What is the width of the folded strip?", fmt(F(s, k)) + " cm", f"Each fold halves the width: {s} ÷ {k} = {fmt(F(s, k))}.", [fmt(F(s, k) * 2) + " cm", fmt(F(s, k) + 1) + " cm", fmt(F(s, k) / 2) + " cm", f"{s} cm"])


@T(C, "Paper folding & cutting")
def _(r):
    cuts = r.randint(1, 6)
    return Q(f"A folded paper strip is cut straight across {cuts} time{'s' if cuts > 1 else ''}, while folded once in half at one end. How many separate pieces result when it is unfolded?", cuts + 1, f"The fold keeps the piece at the folded end joined: {cuts} cuts give {cuts + 1} pieces.", [2 * cuts + 1, 2 * cuts, cuts])


@T(C, "Embedded figures")
def _(r):
    a = r.randint(3, 8)
    target = polygon(a)
    outer = polygon(a) + f'<circle cx="32" cy="32" r="28" fill="none" stroke="{INK}" stroke-width="2"/>'
    return Q(f"This figure hides a simple shape inside a circle. Which shape is embedded in it?", "", f"The shape inside has {a} sides.", [], strip([outer], False), choices(target, [polygon(x) for x in (a + 1, a + 2, a + 3)]))


@T(C, "Embedded figures")
def _(r):
    a, b = r.sample(range(3, 9), 2)
    fig = polygon(a, False, 32, 32, 26) + polygon(b, False, 32, 32, 12)
    return Q(f"Which shape appears in this figure?", "", f"It holds shapes with {a} and {b} sides.", [], strip([fig], False), choices(polygon(b), [polygon(x) for x in range(3, 10) if x not in (a, b)][:3]))


def tile(a, b, c, d, hide=None):
    def cell(col, row, kind):
        x, y = 2 + col * 30, 2 + row * 30
        if (col, row) == hide:
            return f'<rect x="{x}" y="{y}" width="30" height="30" fill="#e2e8f0" stroke="{INK}" stroke-dasharray="3"/><text x="{x + 15}" y="{y + 22}" text-anchor="middle" font-size="20" font-family="sans-serif">?</text>'
        return f'<rect x="{x}" y="{y}" width="30" height="30" fill="none" stroke="{INK}"/>' + kind(x, y)
    return cell(0, 0, a) + cell(1, 0, b) + cell(0, 1, c) + cell(1, 1, d)


MARKS = {
    "diag": lambda x, y: f'<path d="M{x} {y}L{x + 30} {y + 30}" stroke="{INK}" stroke-width="3"/>',
    "anti": lambda x, y: f'<path d="M{x + 30} {y}L{x} {y + 30}" stroke="{INK}" stroke-width="3"/>',
    "dot": lambda x, y: f'<circle cx="{x + 15}" cy="{y + 15}" r="7" fill="{INK}"/>',
    "ring": lambda x, y: f'<circle cx="{x + 15}" cy="{y + 15}" r="8" fill="none" stroke="{INK}" stroke-width="3"/>',
    "bar": lambda x, y: f'<path d="M{x} {y + 15}H{x + 30}" stroke="{INK}" stroke-width="3"/>',
    "post": lambda x, y: f'<path d="M{x + 15} {y}V{y + 30}" stroke="{INK}" stroke-width="3"/>',
    "fill": lambda x, y: f'<rect x="{x + 6}" y="{y + 6}" width="18" height="18" fill="{ACCENT}"/>',
    "cross": lambda x, y: f'<path d="M{x + 6} {y + 6}L{x + 24} {y + 24}M{x + 24} {y + 6}L{x + 6} {y + 24}" stroke="{INK}" stroke-width="3"/>',
}


@T(C, "Pattern completion")
def _(r):
    a, b = r.sample(list(MARKS), 2)
    hide = r.choice([(0, 0), (1, 0), (0, 1), (1, 1)])
    ans = a if hide in ((0, 0), (1, 1)) else b
    wrong = [k for k in MARKS if k != ans]
    r.shuffle(wrong)
    single = lambda k: f'<rect x="17" y="17" width="30" height="30" fill="none" stroke="{INK}"/>' + MARKS[k](17, 17)
    return Q(f"The diagonal tiles of this square match. Which tile fills the blank?", "", "Tiles on the same diagonal are identical.", [], strip([tile(MARKS[a], MARKS[b], MARKS[b], MARKS[a], hide)], False), choices(single(ans), [single(w) for w in wrong]))


@T(C, "Counting figures")
def _(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    body = "".join(f'<rect x="{4 + 16 * i}" y="{4 + 16 * j}" width="16" height="16" fill="none" stroke="{INK}" stroke-width="2"/>' for i in range(m) for j in range(n))
    return Q(f"How many rectangles, including squares, does this {m} × {n} grid contain?", comb(m + 1, 2) * comb(n + 1, 2), f"Choose 2 of {m + 1} vertical lines and 2 of {n + 1} horizontal lines: {comb(m + 1, 2)} × {comb(n + 1, 2)}.", [m * n, m * n + m + n, comb(m + 1, 2) + comb(n + 1, 2)], svg(body, 16 * m + 8, 16 * n + 8))


@T(C, "Counting figures")
def _(r):
    n = r.randint(2, 7)
    ans = sum((n - k) ** 2 for k in range(n))
    body = "".join(f'<rect x="{4 + 14 * i}" y="{4 + 14 * j}" width="14" height="14" fill="none" stroke="{INK}" stroke-width="2"/>' for i in range(n) for j in range(n))
    return Q(f"How many squares of all sizes are in this {n} × {n} grid?", ans, f"1² + 2² + ... + {n}² = {ans}.", [n * n, 2 * n * n, ans + n], svg(body, 14 * n + 8, 14 * n + 8))


@T(C, "Counting figures")
def _(r):
    n = r.randint(1, 8)
    lines = "".join(f'<path d="M50 6L{6 + i * 88 / n:.1f} 70" stroke="{INK}" stroke-width="2"/>' for i in range(n + 1))
    return Q(f"{n + 1} lines from the top point of a triangle reach its base, as shown. How many triangles are there?", comb(n + 1, 2), f"Pick any 2 of the {n + 1} lines: {comb(n + 1, 2)}.", [n, n + 1, n * n], svg(lines + f'<path d="M6 70H94" stroke="{INK}" stroke-width="2"/>', 100, 76))


@T(C, "Cubes & dice")
def _(r):
    n = r.randint(3, 12)
    k, ans = r.choice([("exactly 3 faces", 8), ("exactly 2 faces", 12 * (n - 2)), ("exactly 1 face", 6 * (n - 2) ** 2), ("no faces", (n - 2) ** 3)])
    return Q(f"A painted cube is cut into {n ** 3} equal small cubes. How many small cubes have paint on {k}?", ans, "Corners have 3 painted faces (always 8); edges have 2: 12(n − 2); faces have 1: 6(n − 2)²; the inside has none: (n − 2)³.", [12 * (n - 2) if k != "exactly 2 faces" else 8, 6 * (n - 2) ** 2 if k != "exactly 1 face" else (n - 2) ** 3 + 1, ans + 4])


@T(C, "Cubes & dice")
def _(r):
    a = r.randint(1, 6)
    return Q(f"On a standard die, opposite faces add up to 7. Which number is opposite {a}?", 7 - a, f"7 − {a} = {7 - a}.", [x for x in range(1, 7) if x != 7 - a])


@T(C, "Cubes & dice")
def _(r):
    k = r.randint(1, 5)
    return Q(f"How many faces of a cube meet at one corner, and how many edges does a cube have in total?", "3 faces and 12 edges", "A cube has 8 corners, 12 edges and 6 faces, with 3 faces at each corner.", ["4 faces and 8 edges", "3 faces and 8 edges", "6 faces and 12 edges"])


@T(C, "Cubes & dice")
def _(r):
    n, m = r.randint(2, 8), r.randint(2, 8)
    h = r.randint(1, 6)
    return Q(f"How many unit cubes are needed to build a solid block {n} × {m} × {h}?", n * m * h, f"{n} × {m} × {h} = {n * m * h}.", [n + m + h, 2 * (n * m + m * h + h * n), n * m])


@T(C, "Figure matrix")
def _(r):
    a = r.randint(1, 3)
    grid = [[a + i + j for j in range(3)] for i in range(3)]
    ans = grid[2][2]
    cells = "".join(f'<g transform="translate({j * 66 + 2} {i * 66 + 2})"><rect width="64" height="64" fill="none" stroke="#cbd5e1"/>{dots(grid[i][j]) if (i, j) != (2, 2) else ""}</g>' for i in range(3) for j in range(3))
    return Q(f"Which figure fills the empty cell of this matrix?", "", f"Dots rise by one across each row and down each column, so the last has {ans}.", [], svg(cells + f'<text x="165" y="175" text-anchor="middle" font-size="30" font-family="sans-serif">?</text>', 200, 200), choices(dots(ans), [dots(ans + d) for d in (-1, 1, -2)]))


@T(C, "Figure matrix")
def _(r):
    shapes = r.sample(range(3, 8), 3)
    grid = [[shapes[(i + j) % 3] for j in range(3)] for i in range(3)]
    ans = grid[2][2]
    cells = "".join(f'<g transform="translate({j * 66 + 2} {i * 66 + 2})"><rect width="64" height="64" fill="none" stroke="#cbd5e1"/>{polygon(grid[i][j]) if (i, j) != (2, 2) else ""}</g>' for i in range(3) for j in range(3))
    wrong = [x for x in range(3, 9) if x != ans]
    r.shuffle(wrong)
    return Q(f"Each shape appears once in every row and column. Which figure fills the empty cell?", "", "A Latin-square rule: the missing shape is the one absent from its row.", [], svg(cells + '<text x="165" y="175" text-anchor="middle" font-size="30" font-family="sans-serif">?</text>', 200, 200), choices(polygon(ans), [polygon(x) for x in wrong]))


@T(C, "Figure matrix")
def _(r):
    a, b = r.randint(2, 9), r.randint(2, 9)
    rows = [[x, y, x + y] for x, y in ((a, b), (b + 1, a + 2), (a + 3, b + 4))]
    ans = rows[2][2]
    table = "| Column 1 | Column 2 | Column 3 |\n|---|---|---|\n" + "\n".join("| " + " | ".join(str(v) if not (i == 2 and j == 2) else "?" for j, v in enumerate(row)) + " |" for i, row in enumerate(rows))
    return Q(f"Find the missing number:\n\n{table}", ans, "In each row, the third number is the sum of the first two.", [ans + 1, ans - 1, rows[2][0] * rows[2][1]])


# =================================================================== Data Interpretation
C = "Reading & Analysing Data"
BRANDS = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Sigma"]
YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
PALETTE = ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#a855f7"]


def text(x, y, s, anchor="middle", size=11):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-family="sans-serif" fill="{INK}">{s}</text>'


def bar_chart(labels, values):
    top = max(values) * 1.15
    w = 46
    body = f'<path d="M36 10V170H{40 + w * len(values)}" fill="none" stroke="{INK}"/>'
    for i, v in enumerate(values):
        h = 160 * v / top
        body += f'<rect x="{44 + i * w}" y="{170 - h:.1f}" width="30" height="{h:.1f}" fill="{PALETTE[i % 6]}"/>' + text(59 + i * w, 165 - h, v) + text(59 + i * w, 184, labels[i], size=10)
    return svg(body, 50 + w * len(values), 192)


def line_chart(labels, values):
    top = max(values) * 1.15
    w = 52
    pts = [(50 + i * w, 170 - 160 * v / top) for i, v in enumerate(values)]
    body = f'<path d="M36 10V170H{44 + w * len(values)}" fill="none" stroke="{INK}"/><polyline fill="none" stroke="{PALETTE[0]}" stroke-width="2.5" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>'
    for (x, y), v, l in zip(pts, values, labels):
        body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{PALETTE[0]}"/>' + text(x, y - 7, v) + text(x, 184, l, size=10)
    return svg(body, 60 + w * len(values), 192)


def pie_chart(labels, shares):
    cx, cy, rad = 90, 90, 80
    a, body = -math.pi / 2, ""
    for i, s in enumerate(shares):
        b = a + 2 * math.pi * s / 100
        large = 1 if s > 50 else 0
        body += f'<path d="M{cx} {cy}L{cx + rad * math.cos(a):.1f} {cy + rad * math.sin(a):.1f}A{rad} {rad} 0 {large} 1 {cx + rad * math.cos(b):.1f} {cy + rad * math.sin(b):.1f}Z" fill="{PALETTE[i % 6]}" stroke="#fff"/>'
        body += f'<rect x="185" y="{14 + i * 20}" width="12" height="12" fill="{PALETTE[i % 6]}"/>' + text(202, 25 + i * 20, f"{labels[i]}: {s}%", "start")
        a = b
    return svg(body, 300, 185)


def radar_chart(labels, values):
    cx, cy, rad = 95, 95, 70
    n = len(labels)
    p = lambda i, f: (cx + rad * f * math.sin(2 * math.pi * i / n), cy - rad * f * math.cos(2 * math.pi * i / n))
    body = ""
    for f in (.25, .5, .75, 1):
        body += f'<polygon fill="none" stroke="#cbd5e1" points="{" ".join("%.1f,%.1f" % p(i, f) for i in range(n))}"/>'
    body += f'<polygon fill="{PALETTE[0]}" fill-opacity=".35" stroke="{PALETTE[0]}" stroke-width="2" points="{" ".join("%.1f,%.1f" % p(i, values[i] / 100) for i in range(n))}"/>'
    for i in range(n):
        x, y = p(i, 1.2)
        body += text(x, y + 4, f"{labels[i]} ({values[i]})", size=10)
    return svg(body, 200, 190)


def md_table(headers, rows):
    return "| " + " | ".join(headers) + " |\n|" + "---|" * len(headers) + "\n" + "\n".join("| " + " | ".join(str(c) for c in row) + " |" for row in rows)


def series_questions(r, labels, values, unit="units"):
    """Questions that any list of labelled values supports."""
    i, j = r.sample(range(len(values)), 2)
    kind = r.choice(["total", "avg", "max", "ratio", "share", "diff", "pct"])
    if kind == "total":
        return f"What is the total, in {unit}?", sum(values), f"Add all the values: {sum(values)}.", [sum(values) + values[i], sum(values) - values[j], sum(values) + 10]
    if kind == "avg":
        a = F(sum(values), len(values))
        return f"What is the average, in {unit}?", f"{float(a):.2f}", f"{sum(values)} ÷ {len(values)} = {float(a):.2f}.", [f"{float(a) + 2:.2f}", f"{float(a) - 3:.2f}", f"{float(a) + 5:.2f}"]
    if kind == "max":
        m = labels[values.index(max(values))]
        if values.count(max(values)) > 1:
            return f"What is the highest value, in {unit}?", max(values), f"The highest value is {max(values)}.", [min(values), max(values) - 5, max(values) + 5]
        return "Which has the highest value?", m, f"{m} has {max(values)}.", [str(x) for x in labels if x != m]
    if kind == "ratio":
        g = math.gcd(values[i], values[j])
        return f"What is the ratio of {labels[i]} to {labels[j]}?", f"{values[i] // g} : {values[j] // g}", f"{values[i]} : {values[j]} = {values[i] // g} : {values[j] // g}.", [f"{values[j] // g} : {values[i] // g}", f"{values[i] // g + 1} : {values[j] // g}", f"{values[i] // g} : {values[j] // g + 1}"]
    if kind == "share":
        s = F(values[i] * 100, sum(values))
        return f"What percentage of the total is {labels[i]}?", f"{float(s):.2f}%", f"{values[i]} ÷ {sum(values)} × 100 = {float(s):.2f}%.", [f"{float(s) + 3:.2f}%", f"{float(F(values[j] * 100, sum(values))) + .01:.2f}%", f"{float(s) + 7:.2f}%"]
    if kind == "diff":
        return f"What is the difference between {labels[i]} and {labels[j]}, in {unit}?", abs(values[i] - values[j]), f"|{values[i]} − {values[j]}| = {abs(values[i] - values[j])}.", [values[i] + values[j], abs(values[i] - values[j]) + 5, abs(values[i] - values[j]) + 10]
    p = F((values[j] - values[i]) * 100, values[i])
    return f"By what percentage does {labels[j]} differ from {labels[i]}, relative to {labels[i]}?", f"{float(p):.2f}%", f"({values[j]} − {values[i]}) ÷ {values[i]} × 100 = {float(p):.2f}%.", [f"{float(p) + 5:.2f}%", f"{float(F((values[j] - values[i]) * 100, values[j])):.2f}%", f"{float(-p):.2f}%"]


@T(C, "Tables")
def _(r):
    labels = r.sample(BRANDS, 5)
    v = [10 * r.randint(4, 40) for _ in labels]
    q, a, why, wrong = series_questions(r, labels, v)
    return Q(f"{md_table(['Brand', 'Units sold'], list(zip(labels, v)))}\n\n{q}", a, why, wrong)


@T(C, "Bar graphs")
def _(r):
    labels = YEARS[:5]
    v = [10 * r.randint(3, 30) for _ in labels]
    q, a, why, wrong = series_questions(r, labels, v, "thousand units")
    return Q(f"The chart shows production by year. {q}", a, why, wrong, bar_chart(labels, v))


@T(C, "Line graphs")
def _(r):
    labels = YEARS[:6]
    v = [10 * r.randint(4, 30) for _ in labels]
    i = r.randint(0, 4)
    if r.random() < .3:
        d = [v[k + 1] - v[k] for k in range(5)]
        m = max(d)
        y = labels[d.index(m)]
        if d.count(m) == 1 and m > 0:
            return Q(f"The line shows profit by year. After which year was the rise largest?", y, f"The largest rise is {m}, from {y} to {y + 1}.", [str(l) for l in labels[:5] if l != y], line_chart(labels, v))
    q, a, why, wrong = series_questions(r, labels, v, "₹ lakh")
    return Q(f"The line shows profit by year. {q}", a, why, wrong, line_chart(labels, v))


@T(C, "Pie charts")
def _(r):
    labels = r.sample(["Rent", "Food", "Travel", "Savings", "Fees", "Other"], 5)
    cuts = sorted(r.sample(range(1, 19), 4))
    shares = [5 * (b - a) for a, b in zip([0] + cuts, cuts + [20])]
    total = 1000 * r.randint(2, 30)
    i, j = r.sample(range(5), 2)
    kind = r.choice(["amount", "angle", "ratio", "sum"])
    fig = pie_chart(labels, shares)
    if kind == "amount":
        a = total * shares[i] // 100
        return Q(f"A family spends ₹{total} a month, as shown. How much is spent on {labels[i]}?", f"₹{a}", f"{shares[i]}% of {total} = {a}.", [f"₹{total * shares[j] // 100 + 1}", f"₹{a + 500}", f"₹{a + 1000}"], fig)
    if kind == "angle":
        return Q(f"What angle does {labels[i]} take up in the pie chart?", f"{shares[i] * 18 // 5}°", f"{shares[i]}% of 360 = {shares[i] * 18 // 5}.", [f"{shares[i]}°", f"{shares[i] * 18 // 5 + 18}°", f"{shares[i] * 18 // 5 + 36}°"], fig)
    if kind == "ratio":
        g = math.gcd(shares[i], shares[j])
        return Q(f"What is the ratio of spending on {labels[i]} to {labels[j]}?", f"{shares[i] // g} : {shares[j] // g}", f"{shares[i]} : {shares[j]}.", [f"{shares[j] // g} : {shares[i] // g}", f"{shares[i] // g + 1} : {shares[j] // g}", f"{shares[i] // g} : {shares[j] // g + 1}"], fig)
    a = total * (shares[i] + shares[j]) // 100
    return Q(f"A family spends ₹{total} a month, as shown. How much goes on {labels[i]} and {labels[j]} together?", f"₹{a}", f"{shares[i] + shares[j]}% of {total} = {a}.", [f"₹{a + 500}", f"₹{a + 1500}", f"₹{total - a + 1}"], fig)


@T(C, "Mixed or combined graphs")
def _(r):
    labels = YEARS[:5]
    rev = [100 * r.randint(2, 12) for _ in labels]
    pct = [5 * r.randint(2, 8) for _ in labels]
    i = r.randint(0, 4)
    p = rev[i] * pct[i] // 100
    return Q(f"The bars show revenue (₹ lakh), and the table below gives the profit percentage.\n\n{md_table(['Year'] + [str(y) for y in labels], [['Profit %'] + pct])}\n\nWhat is the profit in {labels[i]}, in ₹ lakh?", p, f"{pct[i]}% of {rev[i]} = {p}.", [rev[i] - p, p + 10, p + 25], bar_chart(labels, rev))


@T(C, "Radar or web charts")
def _(r):
    labels = ["Java", "SQL", "DSA", "React", "AWS"]
    v = [10 * r.randint(3, 10) for _ in labels]
    q, a, why, wrong = series_questions(r, labels, v, "marks")
    return Q(f"The web chart shows one student's marks out of 100. {q}", a, why, wrong, radar_chart(labels, v))


@T(C, "Caselets")
def _(r):
    t = 10 * r.randint(10, 80)
    a, b = r.choice([20, 25, 30, 40, 50]), r.choice([10, 20, 30, 40])
    m = t * a // 100
    q = (t - m) * b // 100
    kind = r.choice([0, 1, 2])
    text_ = f"A company has {t} employees. {a}% work in engineering. Of the rest, {b}% work in sales, and all others work in support."
    if kind == 0:
        return Q(f"{text_} How many work in sales?", q, f"Non-engineering = {t - m}. Sales = {b}% of that = {q}.", [t * b // 100 + 1, q + 10, q + 5])
    if kind == 1:
        return Q(f"{text_} How many work in support?", t - m - q, f"{t} − {m} − {q} = {t - m - q}.", [t - m, t - q, t - m - q + 10])
    return Q(f"{text_} How many work in engineering?", m, f"{a}% of {t} = {m}.", [t - m, m + 10, m + 20])


@T(C, "Venn-based data interpretation")
def _(r):
    t = 10 * r.randint(10, 40)
    a, b = t * r.randint(4, 7) // 10, t * r.randint(3, 6) // 10
    both = r.randint(max(1, a + b - t + 1), min(a, b) - 1)
    neither = t - (a + b - both)
    kind = r.choice([0, 1, 2])
    base = f"Of {t} people surveyed, {a} use Android apps, {b} use iOS apps and {both} use both."
    if kind == 0:
        return Q(f"{base} How many use neither?", neither, f"{t} − ({a} + {b} − {both}) = {neither}.", [t - a - b + 2 * both, neither + both, neither + 5])
    if kind == 1:
        return Q(f"{base} How many use only Android apps?", a - both, f"{a} − {both} = {a - both}.", [a, both, a - both + 5])
    return Q(f"{base} What percentage use both?", f"{float(F(both * 100, t)):.2f}%", f"{both} ÷ {t} × 100.", [f"{float(F(a * 100, t)):.2f}%", f"{float(F(both * 100, t)) + 5:.2f}%", f"{float(F(b * 100, t)):.2f}%"])


@T(C, "Missing data")
def _(r):
    labels = r.sample(BRANDS, 4)
    v = [10 * r.randint(4, 40) for _ in labels]
    k = r.randint(0, 3)
    shown = [str(x) if i != k else "?" for i, x in enumerate(v)]
    return Q(f"{md_table(['Brand', 'Sales'], list(zip(labels, shown)))}\n\nThe total sales are {sum(v)}. What is the missing value?", v[k], f"{sum(v)} − the known values = {v[k]}.", [v[k] + 10, v[k] - 10 if v[k] > 10 else v[k] + 20, v[k] + 30])


@T(C, "Missing data")
def _(r):
    labels = r.sample(BRANDS, 5)
    v = [10 * r.randint(4, 40) for _ in labels]
    a = sum(v)
    while a % 5:
        v[0] += 10
        a = sum(v)
    k = r.randint(0, 4)
    shown = [str(x) if i != k else "?" for i, x in enumerate(v)]
    return Q(f"{md_table(['Brand', 'Sales'], list(zip(labels, shown)))}\n\nThe average sales are {a // 5}. What is the missing value?", v[k], f"Total = 5 × {a // 5} = {a}. Missing = {a} − the known values = {v[k]}.", [v[k] + 10, abs(v[k] - 20) or 15, v[k] + 40])


DS2 = ["Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are needed", "Neither is sufficient, even together"]


@T(C, "Data sufficiency (data interpretation)")
def _(r):
    t, p = 100 * r.randint(2, 30), r.choice([10, 20, 25, 40])
    return Q(f"What were the company's sales of product A? (1) Total sales were {t}. (2) Product A made up {p}% of total sales.", DS2[2], f"Together: {p}% of {t}. Neither alone gives the amount.", [DS2[0], DS2[1], DS2[3]])


@T(C, "Data sufficiency (data interpretation)")
def _(r):
    t = 100 * r.randint(2, 30)
    return Q(f"What were the company's sales in 2024? (1) 2024 sales were {t} units. (2) Sales grew in 2023.", DS2[0], "Statement 1 states the value directly.", [DS2[1], DS2[2], DS2[3]])


@T(C, "Data sufficiency (data interpretation)")
def _(r):
    p = r.choice([10, 20, 25, 40])
    return Q(f"What was the profit in 2024? (1) Profit rose by {p}% over 2023. (2) Costs also rose in 2024.", DS2[3], "No base figure is given for profit in either statement.", [DS2[0], DS2[1], DS2[2]])


@T(C, "Core calculation skills")
def _(r):
    n = 10 * r.randint(20, 900)
    p = r.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 60, 75])
    ans = F(n * p, 100)
    return Q(f"Quickly: what is {p}% of {n}?", ans, f"Split into easy parts: {fmt(ans)}.")


@T(C, "Core calculation skills")
def _(r):
    a, b = r.randint(100, 900), r.randint(100, 900)
    if a == b:
        b += 13
    ans = F((b - a) * 100, a)
    return Q(f"What is the percentage change from {a} to {b}, correct to 2 decimal places?", f"{float(ans):.2f}%", f"({b} − {a}) ÷ {a} × 100 = {float(ans):.2f}%.", [f"{float(ans) + 2:.2f}%", f"{float(F((b - a) * 100, b)):.2f}%", f"{float(-ans):.2f}%"])


@T(C, "Core calculation skills")
def _(r):
    fr = [F(r.randint(1, 9), r.randint(2, 12)) for _ in range(2)]
    while fr[0] == fr[1]:
        fr[1] = F(r.randint(1, 9), r.randint(2, 12))
    big = max(fr)
    small = min(fr)
    return Q(f"Which is greater: {fmt(fr[0])} or {fmt(fr[1])}?", fmt(big), "Compare by cross-multiplying.", [fmt(small), "They are equal", "Cannot be compared"])
