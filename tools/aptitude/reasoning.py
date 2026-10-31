"""Logical reasoning: computed where the answer can be worked out by code, written by hand where it needs judgement."""
import itertools
import string

from core import F, Q, T, hand

C = "Verbal Reasoning"
L = string.ascii_uppercase
NAMES = ["Asha", "Bala", "Chitra", "Dev", "Esha", "Farhan", "Gita", "Hari", "Isha", "Jay", "Kiran", "Lata", "Mohan", "Nisha", "Om", "Priya", "Ravi", "Sara", "Tara", "Uma", "Vijay", "Yash", "Zoya", "Arjun", "Meera", "Neel", "Rohan", "Divya", "Kabir", "Anu"]
WORDS = "APPLE BRAIN CHAIR DREAM EAGLE FLAME GRAPE HOUSE IMAGE JUICE KNIFE LEMON MOUSE NIGHT OCEAN PAPER QUEEN RIVER STONE TABLE UNCLE VOICE WATER YOUTH ZEBRA BREAD CLOUD DANCE EARTH FRUIT GLASS HEART LIGHT MONEY NORTH PLANT ROBOT SMILE TRAIN WORLD GARDEN PENCIL BOTTLE WINDOW MARKET SILVER FOREST PLANET SCHOOL BRIDGE".split()


def letter(i):
    return L[i % 26]


# ------------------------------------------------------------------- series
@T(C, "Number & letter series")
def _(r):
    a, d, g = r.randint(1, 20), r.randint(1, 8), r.randint(2, 3)
    seq, x = [], a
    for i in range(6):
        seq.append(x)
        x = x * g if i % 2 == 0 else x + d
    return Q(f"Find the next term: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], f"Alternately multiply by {g} and add {d}.", [seq[-1] + d, seq[-2] * 2 + 1, seq[-1] - 1])


@T(C, "Number & letter series")
def _(r):
    s, d = r.randint(0, 20), r.randint(1, 5)
    seq = [letter(s + i * d) for i in range(6)]
    return Q(f"Find the next letter: {', '.join(seq[:-1])}, ?", seq[-1], f"Move {d} letter{'s' if d > 1 else ''} forward each time (wrapping after Z).", [letter(s + 5 * d + 1), letter(s + 5 * d - 1), letter(s + 5 * d + 2)])


@T(C, "Number & letter series")
def _(r):
    s, d, n = r.randint(0, 15), r.randint(1, 3), r.randint(2, 3)
    terms = ["".join(letter(s + i * d + j * n) for j in range(2)) for i in range(5)]
    wrong = ["".join(letter(s + 4 * d + j * n + k) for j in range(2)) for k in (1, 2, -1)]
    return Q(f"Find the next group: {', '.join(terms[:-1])}, ?", terms[-1], f"Each group moves {d} forward; within a group the letters are {n} apart.", wrong)


@T(C, "Number & letter series")
def _(r):
    a, b = r.randint(1, 9), r.randint(1, 9)
    seq = [a, b]
    for _i in range(5):
        seq.append(seq[-1] + seq[-2])
    return Q(f"Find the next term: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], "Each term is the sum of the previous two.", [seq[-2] * 2, seq[-1] + 1, seq[-1] + seq[-3]])


# ------------------------------------------------------------------- coding
@T(C, "Coding-decoding")
def _(r):
    k = r.randint(1, 6)
    w1, w2 = r.sample(WORDS, 2)
    enc = lambda w: "".join(letter(ord(c) - 65 + k) for c in w)
    return Q(f"In a code, {w1} is written as {enc(w1)}. How is {w2} written?", enc(w2), f"Each letter moves {k} forward.", ["".join(letter(ord(c) - 65 + k + 1) for c in w2), "".join(letter(ord(c) - 65 - k) for c in w2), enc(w2)[::-1]])


@T(C, "Coding-decoding")
def _(r):
    w1, w2 = r.sample(WORDS, 2)
    enc = lambda w: w[::-1]
    return Q(f"In a code, {w1} is written as {enc(w1)}. How is {w2} written?", enc(w2), "The letters are reversed.", [w2[1:] + w2[0], w2[-1] + w2[1:-1] + w2[0], "".join(sorted(w2))])


@T(C, "Coding-decoding")
def _(r):
    w1, w2 = r.sample(WORDS, 2)
    enc = lambda w: "".join(letter(25 - (ord(c) - 65)) for c in w)
    return Q(f"Using the opposite-letter code (A↔Z, B↔Y), {w1} becomes {enc(w1)}. What does {w2} become?", enc(w2), "Each letter is replaced by its opposite in the alphabet.", ["".join(letter(ord(c) - 64) for c in w2), enc(w2)[::-1], "".join(letter(ord(c) - 66) for c in w2)])


@T(C, "Coding-decoding")
def _(r):
    w1, w2 = r.sample(WORDS, 2)
    val = lambda w: sum(ord(c) - 64 for c in w)
    return Q(f"If {w1} is coded as {val(w1)} (the sum of letter positions), what is the code for {w2}?", val(w2), f"Add the alphabet positions of {w2}: {' + '.join(str(ord(c) - 64) for c in w2)} = {val(w2)}.")


# ------------------------------------------------------------------- blood relations
RELATIONS = [
    ("{a} is the father of {b}. {b} is the mother of {c}. How is {a} related to {c}?", "Grandfather", ["Father", "Uncle", "Brother"], "{a} is the father of {c}'s mother."),
    ("{a} is the mother of {b}. {b} is the sister of {c}. How is {a} related to {c}?", "Mother", ["Aunt", "Sister", "Grandmother"], "{b}'s mother is also the mother of {b}'s sibling {c}."),
    ("{a} is the brother of {b}. {b} is the father of {c}. How is {a} related to {c}?", "Uncle", ["Father", "Cousin", "Grandfather"], "A father's brother is an uncle."),
    ("{a} is the sister of {b}. {b} is the mother of {c}. How is {a} related to {c}?", "Aunt", ["Mother", "Sister", "Grandmother"], "A mother's sister is an aunt."),
    ("{a} is the son of {b}. {b} is the brother of {c}. If {c} is a man, how is {c} related to {a}?", "Uncle", ["Father", "Brother", "Nephew"], "{a}'s father's or mother's brother is {a}'s uncle."),
    ("{a} is the wife of {b}. {b} is the son of {c}. {c} is a woman. How is {c} related to {a}?", "Mother-in-law", ["Mother", "Aunt", "Sister-in-law"], "The mother of one's husband is one's mother-in-law."),
    ("{a} is the husband of {b}. {b} is the daughter of {c}. {c} is a man. How is {c} related to {a}?", "Father-in-law", ["Father", "Uncle", "Brother-in-law"], "The father of one's wife is one's father-in-law."),
    ("{a} is the son of {b}, and {c} is the daughter of {b}. How is {a} related to {c}?", "Brother", ["Cousin", "Father", "Uncle"], "They share the parent {b}, and {a} is male."),
    ("{a} is the daughter of {b}. {b} is the son of {c}. {c} is a man. How is {c} related to {a}?", "Grandfather", ["Father", "Uncle", "Great-grandfather"], "{c} is the father of {a}'s father."),
    ("{a} is the sister of {b}. {b} is the son of {c}. {c} is a woman. How is {a} related to {c}?", "Daughter", ["Sister", "Niece", "Mother"], "{a} is a female child of {c}."),
    ("{a} is the brother of {b}. {b} is the mother of {c}. {c} is a boy. How is {c} related to {a}?", "Nephew", ["Son", "Cousin", "Brother"], "A sister's son is a nephew."),
    ("{a} is the sister of {b}. {b} is the father of {c}. {c} is a girl. How is {c} related to {a}?", "Niece", ["Daughter", "Cousin", "Sister"], "A brother's daughter is a niece."),
    ("{a} is the father of {b}. {a} is the brother of {c}. {d} is {c}'s son. How is {b} related to {d}?", "Cousin", ["Brother", "Nephew", "Uncle"], "Their fathers are brothers, so they are cousins."),
    ("Pointing to a photo, {a} says, \"This person is the only son of my mother.\" Who is in the photo, if {a} is a woman?", "{a}'s brother", ["{a}'s father", "{a}'s son", "{a}'s husband"], "A woman's mother's only son is the woman's brother."),
    ("Pointing to a man, {a} (a man) says, \"His mother is the only daughter of my mother.\" How is {a} related to the man?", "Uncle", ["Father", "Brother", "Grandfather"], "The only daughter of {a}'s mother is {a}'s sister. Her son is {a}'s nephew, so {a} is his uncle."),
    ("{a} is married to {b}. {c} is {b}'s brother. {a} is a woman. How is {c} related to {a}?", "Brother-in-law", ["Brother", "Father-in-law", "Cousin"], "A husband's brother is a brother-in-law."),
]


@T(C, "Blood relations")
def _(r):
    q, ans, wrong, why = r.choice(RELATIONS)
    a, b, c, d = r.sample("APQRSTUVWXYZ", 4)  # letters, as tests use: a name would imply a gender
    f = lambda s: s.format(a=a, b=b, c=c, d=d)
    return Q(f(q), f(ans), f(why), [f(w) for w in wrong])


# ------------------------------------------------------------------- direction
DIRS = ["North", "East", "South", "West"]
VEC = {"North": (0, 1), "East": (1, 0), "South": (0, -1), "West": (-1, 0)}


def compass(dx, dy):
    if dx == 0 and dy == 0:
        return "At the starting point"
    ns = "North" if dy > 0 else "South" if dy < 0 else ""
    ew = "East" if dx > 0 else "West" if dx < 0 else ""
    return (ns + ("-" + ew.lower() if ns and ew else ew)) if ns else ew


@T(C, "Direction sense")
def _(r):
    who = r.choice(NAMES)
    h, dx, dy, parts = r.randint(0, 3), 0, 0, []
    for i in range(r.randint(3, 4)):
        d = r.randint(2, 12)
        dx += VEC[DIRS[h]][0] * d
        dy += VEC[DIRS[h]][1] * d
        parts.append(f"walks {d} km" + (f" facing {DIRS[h]}" if i == 0 else ""))
        turn = r.choice([1, 3])
        if i < 3:
            parts.append("turns right" if turn == 1 else "turns left")
            h = (h + turn) % 4
    if parts[-1].startswith("turns"):
        parts.pop()
    # the last walk uses the direction before the final unused turn
    ans = compass(dx, dy)
    all_opts = ["North", "South", "East", "West", "North-east", "North-west", "South-east", "South-west", "At the starting point"]
    wrong = [o for o in all_opts if o != ans]
    r.shuffle(wrong)
    return Q(f"{who} {', then '.join(parts)}. In which direction is {who} now from the start?", ans, f"Net movement: {abs(dx)} km {'east' if dx >= 0 else 'west'} and {abs(dy)} km {'north' if dy >= 0 else 'south'}.", wrong)


@T(C, "Direction sense")
def _(r):
    who = r.choice(NAMES)
    (a, b, c), k = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]), r.randint(1, 4)
    extra = r.randint(2, 9)
    return Q(f"{who} walks {a * k + extra} km north, turns right and walks {b * k} km, then turns right again and walks {extra} km. How far is {who} from the start, in km?", c * k, f"Net: {a * k} km north and {b * k} km east. Distance = √({a * k}² + {b * k}²) = {c * k}.", [(a + b) * k, (a + b) * k + 2 * extra, c * k + extra])


@T(C, "Direction sense")
def _(r):
    h, turns = r.randint(0, 3), r.randint(2, 6)
    seq = [r.choice(["right", "left"]) for _ in range(turns)]
    end = h
    for t in seq:
        end = (end + (1 if t == "right" else 3)) % 4
    return Q(f"Facing {DIRS[h]}, a person turns {', then '.join(seq)}, by 90° each time. Which way does the person face now?", DIRS[end], f"Right is +90° and left is −90°. The net result is {DIRS[end]}.", [d for d in DIRS if d != DIRS[end]])


# ------------------------------------------------------------------- ranking
@T(C, "Ranking & order")
def _(r):
    n = r.randint(20, 70)
    a = r.randint(3, n - 3)
    who = r.choice(NAMES)
    return Q(f"{who} is {a}th from the front in a row of {n} people. What is {who}'s position from the back?", n - a + 1, f"Back position = {n} − {a} + 1 = {n - a + 1}.", [n - a, n - a + 2, a])


@T(C, "Ranking & order")
def _(r):
    a, b = r.randint(5, 40), r.randint(5, 40)
    who = r.choice(NAMES)
    return Q(f"{who} is {a}th from the top and {b}th from the bottom of a class. How many students are in the class?", a + b - 1, f"{a} + {b} − 1 = {a + b - 1}, because {who} is counted twice.", [a + b, a + b + 1, a + b - 2])


@T(C, "Ranking & order")
def _(r):
    n = r.randint(25, 70)
    a, b = r.randint(4, 12), r.randint(4, 12)
    gap = n - a - b
    x, y = r.sample(NAMES, 2)
    return Q(f"In a row of {n}, {x} is {a}th from the left and {y} is {b}th from the right. How many people are between them?", gap, f"Between = {n} − {a} − {b} = {gap}.", [gap + 1, gap + 2, gap - 1 if gap > 1 else gap + 3])


@T(C, "Ranking & order")
def _(r):
    who = r.sample(NAMES, 5)
    order = who[:]
    r.shuffle(order)  # tallest to shortest
    facts = [f"{order[i]} is taller than {order[i + 1]}" for i in range(4)]
    r.shuffle(facts)
    k, name = r.choice([("tallest", order[0]), ("shortest", order[-1]), ("second tallest", order[1]), ("exactly in the middle", order[2])])
    return Q(f"{'. '.join(facts)}. Who is {k}?", name, f"The order from tallest is {' > '.join(order)}.", [x for x in who if x != name])


# ------------------------------------------------------------------- seating (brute force)
@T(C, "Seating arrangement")
def _(r):
    for _try in range(400):
        people = r.sample(NAMES, 5)
        target = people[:]
        r.shuffle(target)
        P = {p: i for i, p in enumerate(target)}
        clues = []
        pool = []
        for a, b in itertools.permutations(people, 2):
            if P[a] + 1 == P[b]:
                pool.append((f"{a} sits immediately to the left of {b}", lambda s, a=a, b=b: s[a] + 1 == s[b]))
            if P[a] < P[b]:
                pool.append((f"{a} sits somewhere to the left of {b}", lambda s, a=a, b=b: s[a] < s[b]))
        for a in people:
            if P[a] in (0, 4):
                pool.append((f"{a} sits at an end", lambda s, a=a: s[a] in (0, 4)))
            if P[a] == 2:
                pool.append((f"{a} sits in the middle", lambda s, a=a: s[a] == 2))
        r.shuffle(pool)
        for clue in pool:
            clues.append(clue)
            sols = []
            for perm in itertools.permutations(people):
                s = {p: i for i, p in enumerate(perm)}
                if all(f(s) for _t, f in clues):
                    sols.append(perm)
            if len(sols) == 1:
                k = r.randint(0, 4)
                ask = {0: "at the far left", 1: "second from the left", 2: "in the middle", 3: "second from the right", 4: "at the far right"}[k]
                if len(clues) < 3:
                    break
                return Q(f"Five friends sit in a row facing north. {'. '.join(t for t, _f in clues)}. Who sits {ask}?", target[k], f"The only order that fits, left to right, is {', '.join(target)}.", [p for p in people if p != target[k]])
    raise ValueError("no seating")


@T(C, "Seating arrangement")
def _(r):
    n = r.choice([6, 8, 10, 12])
    people = r.sample(NAMES, n)
    i, k = r.randint(0, n - 1), r.randint(1, n // 2 - 1)
    side = r.choice(["right", "left"])
    j = (i - k) % n if side == "right" else (i + k) % n
    return Q(f"{n} people sit around a circle facing the centre, listed clockwise: {', '.join(people)}. Who is {k} place{'s' if k > 1 else ''} to the {side} of {people[i]}?", people[j], "When facing the centre, moving to the right is counter-clockwise; moving to the left is clockwise. Count from the name.", [p for p in people if p != people[j]][:6])


@T(C, "Seating arrangement")
def _(r):
    n = r.choice([6, 8, 10, 12])
    people = r.sample(NAMES, n)
    i = r.randint(0, n - 1)
    return Q(f"{n} people sit evenly around a table in this order: {', '.join(people)}. Who sits directly opposite {people[i]}?", people[(i + n // 2) % n], f"Opposite means {n // 2} places away.", [people[(i + 1) % n], people[(i - 1) % n], people[(i + n // 2 + 1) % n]])


# ------------------------------------------------------------------- puzzles
@T(C, "Puzzles")
def _(r):
    who = r.sample(NAMES, 3)
    items = r.choice([("Java", "Python", "C++"), ("red", "blue", "green"), ("tea", "coffee", "milk"), ("Delhi", "Pune", "Chennai"), ("maths", "physics", "history"), ("cricket", "tennis", "chess")])
    for _try in range(200):
        truth = list(items)
        r.shuffle(truth)
        A = dict(zip(who, truth))
        clues = []
        cands = [(f"{p} did not choose {it}", lambda m, p=p, it=it: m[p] != it) for p in who for it in items if A[p] != it]
        r.shuffle(cands)
        sols = list(itertools.permutations(items))
        for c in cands:
            clues.append(c)
            good = [s for s in sols if all(f(dict(zip(who, s))) for _t, f in clues)]
            if len(good) == 1:
                p = r.choice(who)
                return Q(f"{', '.join(who)} each chose a different one of {', '.join(items)}. {'. '.join(t for t, _f in clues)}. Which did {p} choose?", A[p], "Eliminate: the clues leave only one assignment, " + ", ".join(f"{k} chose {v}" for k, v in A.items()) + ".", [x for x in items if x != A[p]] + ["Cannot be determined"])
    raise ValueError


@T(C, "Puzzles")
def _(r):
    who = r.sample(NAMES, 4)
    ages = r.sample(range(18, 40), 4)
    A = dict(sorted(zip(who, ages), key=lambda x: x[1]))
    order = list(A)
    return Q(f"Ages: {who[0]} is {ages[0]}, {who[1]} is {ages[1]}, {who[2]} is {ages[2]} and {who[3]} is {ages[3]}. Who is second youngest?", order[1], f"From youngest: {', '.join(order)}.", [p for p in who if p != order[1]])


@T(C, "Puzzles")
def _(r):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    who = r.sample(NAMES, 5)
    for _try in range(200):
        truth = who[:]
        r.shuffle(truth)
        d = {p: i for i, p in enumerate(truth)}
        pool = []
        for a, b in itertools.permutations(who, 2):
            if d[a] + 1 == d[b]:
                pool.append((f"{b} presents the day after {a}", lambda s, a=a, b=b: s[a] + 1 == s[b]))
            elif d[a] < d[b]:
                pool.append((f"{a} presents before {b}", lambda s, a=a, b=b: s[a] < s[b]))
        for p in who:
            pool.append((f"{p} presents on {days[d[p]]}", lambda s, p=p, v=d[p]: s[p] == v))
        r.shuffle(pool)
        clues = []
        for c in pool:
            clues.append(c)
            n = sum(1 for perm in itertools.permutations(who) if all(f({p: i for i, p in enumerate(perm)}) for _t, f in clues))
            if n == 1:
                k = r.randint(0, 4)
                if len(clues) < 3:
                    break
                return Q(f"Five people present on different weekdays, Monday to Friday. {'. '.join(t for t, _f in clues)}. Who presents on {days[k]}?", truth[k], f"The order is {', '.join(truth)}.", [p for p in who if p != truth[k]])
    raise ValueError


# ------------------------------------------------------------------- syllogisms
SYL = [
    ("All {a} are {b}. All {b} are {c}.", "All {a} are {c}", ["No {a} are {c}", "All {c} are {a}", "Some {c} are not {b}"], "Chain the two: every {a} is a {b}, and every {b} is a {c}."),
    ("All {a} are {b}. No {b} are {c}.", "No {a} are {c}", ["All {a} are {c}", "Some {a} are {c}", "All {c} are {a}"], "Every {a} is a {b}, and no {b} is a {c}."),
    ("Some {a} are {b}. All {b} are {c}.", "Some {a} are {c}", ["All {a} are {c}", "No {a} are {c}", "All {c} are {a}"], "The {a} that are {b} must also be {c}."),
    ("All {a} are {b}. Some {c} are {a}.", "Some {c} are {b}", ["All {c} are {b}", "No {c} are {b}", "All {b} are {c}"], "The {c} that are {a} are also {b}."),
    ("No {a} are {b}. Some {c} are {a}.", "Some {c} are not {b}", ["No {c} are {b}", "All {c} are {b}", "Some {b} are {a}"], "The {c} that are {a} cannot be {b}."),
    ("All {a} are {b}. All {a} are {c}.", "Some {b} are {c}", ["All {b} are {c}", "No {b} are {c}", "All {c} are {b}"], "Every {a} is both, so at least some {b} are {c} (if {a} exist)."),
    ("Some {a} are {b}. Some {b} are {c}.", "No definite conclusion follows", ["Some {a} are {c}", "No {a} are {c}", "All {a} are {c}"], "Two \"some\" premises give no definite link between {a} and {c}."),
    ("All {a} are {b}. All {c} are {b}.", "No definite conclusion follows", ["All {a} are {c}", "Some {a} are {c}", "No {a} are {c}"], "Sharing a larger group says nothing about how {a} and {c} overlap."),
    ("No {a} are {b}. No {b} are {c}.", "No definite conclusion follows", ["No {a} are {c}", "All {a} are {c}", "Some {a} are {c}"], "Two negative premises give no conclusion."),
]
GROUPS = "pens books cats dogs tables doctors singers rivers phones cars birds trees teachers players stars chairs lamps coins keys boxes pilots painters kings clouds apples".split()


@T(C, "Syllogisms")
def _(r):
    p, ans, wrong, why = r.choice(SYL)
    a, b, c = r.sample(GROUPS, 3)
    f = lambda s: s.format(a=a, b=b, c=c)
    return Q(f"Statements: {f(p)} Which conclusion follows?", f(ans), f(why), [f(w) for w in wrong])


# ------------------------------------------------------------------- analogy and classification
@T(C, "Analogy")
def _(r):
    k = r.randint(2, 9)
    f, name = r.choice([(lambda x: x * x, "square"), (lambda x: x ** 3, "cube"), (lambda x: x * 2, "double"), (lambda x: x * 3, "triple"), (lambda x: x + 7, "plus 7"), (lambda x: x * x + 1, "square plus 1"), (lambda x: x * x - 1, "square minus 1")])
    b = r.randint(2, 15)
    while b == k:
        b = r.randint(2, 15)
    return Q(f"{k} : {f(k)} :: {b} : ?", f(b), f"The rule is {name}.", [f(b) + 1, f(b) - 1, f(b) + b])


@T(C, "Analogy")
def _(r):
    d = r.randint(1, 5)
    a, c = r.sample(range(0, 20), 2)
    pair = lambda s: letter(s) + letter(s + d)
    return Q(f"{pair(a)} : {pair(a + d + 1)} :: {pair(c)} : ?", pair(c + d + 1), f"Each pair of letters is {d} apart; the second group starts {d + 1} letters later.", [pair(c + d), pair(c + d + 2), letter(c + d + 1) + letter(c + d + 1)])


ANALOGY = [("Doctor", "Hospital", "Teacher", "School", ["Book", "Student", "Board"], "A workplace."), ("Pen", "Write", "Knife", "Cut", ["Sharp", "Kitchen", "Steel"], "A tool and its use."), ("Bird", "Nest", "Bee", "Hive", ["Honey", "Flower", "Tree"], "An animal and its home."), ("Puppy", "Dog", "Kitten", "Cat", ["Milk", "Tiger", "Pet"], "Young one and adult."), ("Hot", "Cold", "Tall", "Short", ["High", "Big", "Long"], "Opposites."), ("Eye", "See", "Ear", "Hear", ["Sound", "Head", "Listen to music"], "Organ and function."), ("Car", "Road", "Train", "Track", ["Station", "Engine", "Coach"], "Vehicle and path."), ("Author", "Book", "Composer", "Music", ["Piano", "Song", "Singer"], "Creator and creation."), ("Water", "Thirst", "Food", "Hunger", ["Plate", "Cook", "Eat"], "What relieves what."), ("Foot", "Shoe", "Hand", "Glove", ["Ring", "Finger", "Watch"], "Part and its covering."), ("Day", "Night", "Summer", "Winter", ["Hot", "Sun", "Rain"], "Opposite periods."), ("Lion", "Roar", "Dog", "Bark", ["Tail", "Bite", "Bone"], "Animal and sound."), ("Fish", "Water", "Camel", "Desert", ["Hump", "Sand", "Oasis"], "Animal and habitat."), ("Clock", "Time", "Thermometer", "Temperature", ["Fever", "Mercury", "Doctor"], "Instrument and measure."), ("Cow", "Milk", "Hen", "Egg", ["Feather", "Farm", "Chick"], "Animal and product."), ("Tree", "Forest", "Soldier", "Army", ["Gun", "War", "Uniform"], "Member and group."), ("Tailor", "Clothes", "Baker", "Bread", ["Oven", "Flour", "Shop"], "Maker and product."), ("Page", "Book", "Brick", "Wall", ["Cement", "Mason", "Red"], "Part and whole."), ("Rain", "Umbrella", "Sun", "Sunglasses", ["Sky", "Heat", "Shadow"], "Protection."), ("Kilogram", "Weight", "Metre", "Length", ["Road", "Ruler", "Height of a man"], "Unit and quantity.")]


@T(C, "Analogy")
def _(r):
    a, b, c, d, wrong, why = r.choice(ANALOGY)
    return Q(f"{a} : {b} :: {c} : ?", d, f"Relation: {why}", wrong)


@T(C, "Classification (odd one out)")
def _(r):
    kind = r.choice(["prime", "even", "square", "mult"])
    if kind == "prime":
        good = r.sample([x for x in range(11, 100) if all(x % d for d in range(2, 10) if x != d)], 3)
        bad = r.choice([x for x in range(21, 100, 2) if x % 3 == 0 or x % 7 == 0])
        return Q(f"Which is the odd one out: {', '.join(map(str, sorted(good + [bad])))}?", bad, f"{bad} is composite; the others are prime.", good)
    if kind == "even":
        good = [2 * x for x in r.sample(range(5, 60), 3)]
        bad = 2 * r.randint(5, 60) + 1
        return Q(f"Which is the odd one out: {', '.join(map(str, sorted(good + [bad])))}?", bad, f"{bad} is odd; the others are even.", good)
    if kind == "square":
        good = [x * x for x in r.sample(range(3, 25), 3)]
        bad = r.randint(3, 24) ** 2 + r.randint(2, 6)
        return Q(f"Which is the odd one out: {', '.join(map(str, sorted(good + [bad])))}?", bad, f"The others are perfect squares; {bad} is not.", good)
    d = r.choice([3, 4, 6, 7, 8, 9])
    good = [d * x for x in r.sample(range(2, 30), 3)]
    bad = d * r.randint(2, 30) + 1
    return Q(f"Which is the odd one out: {', '.join(map(str, sorted(good + [bad])))}?", bad, f"The others are multiples of {d}; {bad} is not.", good)


ODD = [("Rose Lily Lotus Mango", "Mango", "A fruit; the others are flowers."), ("Delhi Mumbai Paris Chennai", "Paris", "Not in India."), ("Dog Cat Cow Sparrow", "Sparrow", "A bird; the others are mammals."), ("Java Python Oracle Rust", "Oracle", "A company and database product; the others are programming languages."), ("Mars Venus Moon Saturn", "Moon", "A satellite; the others are planets."), ("Copper Iron Silver Wood", "Wood", "Not a metal."), ("Triangle Square Circle Cube", "Cube", "A 3D solid; the others are 2D."), ("Hammer Saw Spanner Pillow", "Pillow", "Not a tool."), ("Red Green Blue Round", "Round", "A shape word; the others are colours."), ("Monday Friday June Sunday", "June", "A month; the others are days."), ("Violin Flute Sitar Guitar", "Flute", "A wind instrument; the others have strings."), ("Carrot Potato Radish Tomato", "Tomato", "Grows above ground; the others are root vegetables."), ("Shark Whale Salmon Trout", "Whale", "A mammal; the others are fish."), ("MySQL PostgreSQL Redis Linux", "Linux", "An operating system; the others are databases."), ("Ganga Yamuna Godavari Himalaya", "Himalaya", "A mountain range; the others are rivers."), ("Eagle Ostrich Crow Parrot", "Ostrich", "A flightless bird."), ("Chair Table Sofa Spoon", "Spoon", "Cutlery; the others are furniture."), ("Hindi Tamil French Telugu", "French", "Not an Indian language."), ("Doctor Nurse Surgeon Lawyer", "Lawyer", "Not a medical profession."), ("Oxygen Hydrogen Nitrogen Sodium", "Sodium", "A metal; the others are gases at room temperature.")]


@T(C, "Classification (odd one out)")
def _(r):
    s, ans, why = r.choice(ODD)
    opts = s.split()
    return Q(f"Which word does not belong: {', '.join(opts)}?", ans, why, [o for o in opts if o != ans])


@T(C, "Classification (odd one out)")
def _(r):
    d = r.randint(1, 4)
    starts = r.sample(range(0, 20), 4)
    good = [letter(s) + letter(s + d) + letter(s + 2 * d) for s in starts[:3]]
    s = starts[3]
    bad = letter(s) + letter(s + d + 1) + letter(s + 2 * d + 3)
    return Q(f"Which letter group is the odd one out: {', '.join(sorted(good + [bad]))}?", bad, f"The others have letters evenly spaced by {d}.", good)


# ------------------------------------------------------------------- inequalities
@T(C, "Inequalities (reasoning)")
def _(r):
    a, b, c, d = r.sample("ABCDEFGHJKLMPQRSTUVWXYZ", 4)
    op = r.choice([(">", "≥", ">"), ("≥", ">", ">"), ("≥", "≥", "≥"), (">", ">", ">"), ("<", "≤", "<"), ("≤", "≤", "≤")])
    big = op[0] in (">", "≥")
    return Q(f"Given {a} {op[0]} {b} {op[1]} {c} {op[2]} {d}, what follows about {a} and {d}?", f"{a} {'≥' if op == ('≥', '≥', '≥') else '≤' if op == ('≤', '≤', '≤') else '>' if big else '<'} {d}", "Chain the signs: if any sign in the chain is strict, the result is strict.", [f"{a} = {d}", f"{a} {'<' if big else '>'} {d}", f"No relation can be found between {a} and {d}"])


@T(C, "Inequalities (reasoning)")
def _(r):
    a, b, c = r.sample("ABCDEFGHJKLMPQRSTUVWXYZ", 3)
    return Q(f"Given {a} > {b} and {c} > {b}, what is the relation between {a} and {c}?", f"No relation can be determined", f"Both exceed {b}, but that does not compare them.", [f"{a} > {c}", f"{a} < {c}", f"{a} = {c}"])


@T(C, "Inequalities (reasoning)")
def _(r):
    a, b, c, d = r.sample("ABCDEFGHJKLMPQRSTUVWXYZ", 4)
    return Q(f"Given {a} ≥ {b} = {c} > {d}, which statement must be true?", f"{a} > {d}", f"{a} ≥ {c} and {c} > {d} make {a} > {d}. {a} and {b} may be equal.", [f"{a} > {b}", f"{d} > {c}", f"{a} = {c}"])


# ------------------------------------------------------------------- input-output
@T(C, "Input-output")
def _(r):
    nums = r.sample(range(10, 99), 5)
    k = r.randint(1, 3)
    cur = nums[:]
    for i in range(k):
        rest = cur[i:]
        m = min(rest)
        rest.remove(m)
        cur = cur[:i] + [m] + rest
    wrong = []
    for j in (1, 2, 3):
        w = cur[:]
        w[-1], w[-1 - j] = w[-1 - j], w[-1]
        wrong.append(" ".join(map(str, w)))
    return Q(f"A machine takes the input {' '.join(map(str, nums))}. In each step it moves the smallest unmoved number to the left end of the unmoved part. What is the output after step {k}?", " ".join(map(str, cur)), "Each step fixes the next smallest number in place from the left.", wrong + [" ".join(map(str, sorted(nums, reverse=True)))])


@T(C, "Input-output")
def _(r):
    words = r.sample(WORDS, 5)
    k = r.randint(1, 3)
    cur = words[:]
    for i in range(k):
        rest = cur[i:]
        m = min(rest)
        rest.remove(m)
        cur = cur[:i] + [m] + rest
    wrong = [" ".join(reversed(cur)), " ".join(sorted(words, reverse=True)), " ".join(words[::-1][1:] + words[::-1][:1])]
    return Q(f"Input: {' '.join(words)}. In each step, the word that comes first alphabetically among the unmoved words moves to the left end of them. What is the output after step {k}?", " ".join(cur), "Each step fixes one more word in alphabetical order from the left.", wrong + [" ".join(words[1:] + words[:1])] + [" ".join(r.sample(words, 5)) for _i in range(4)])


@T(C, "Input-output")
def _(r):
    nums = r.sample(range(2, 40), 4)
    d = r.randint(1, 9)
    ans = " ".join(str(x + d) if x % 2 == 0 else str(x - d) for x in nums)
    return Q(f"A machine adds {d} to each even number and subtracts {d} from each odd number. What is the output for {' '.join(map(str, nums))}?", ans, "Apply the rule to each number by whether it is even or odd.", [" ".join(str(x + d) for x in nums), " ".join(str(x - d) for x in nums), " ".join(str(x - d) if x % 2 == 0 else str(x + d) for x in nums)])


# ------------------------------------------------------------------- mathematical operations
@T(C, "Mathematical operations")
def _(r):
    a, b, c = r.randint(2, 20), r.randint(2, 12), r.randint(2, 9)
    d = c * r.randint(1, 8)
    mapping = r.sample(["+", "−", "×", "÷"], 4)
    sym = dict(zip(["@", "%", "&", "#"], mapping))
    rev = {v: k for k, v in sym.items()}
    ans = a + b * c - d // c
    return Q(f"If {rev['+']} means +, {rev['−']} means −, {rev['×']} means × and {rev['÷']} means ÷, find {a} {rev['+']} {b} {rev['×']} {c} {rev['−']} {d} {rev['÷']} {c}.", ans, f"Follow BODMAS after replacing symbols: {a} + {b} × {c} − {d} ÷ {c} = {ans}.", [(a + b) * c - d // c, a + b * c - d, ans + c])


@T(C, "Mathematical operations")
def _(r):
    a, b = r.randint(2, 15), r.randint(2, 15)
    s = r.choice(["@", "&", "%"])
    p, q = r.randint(2, 12), r.randint(2, 12)
    k = r.choice([("a² + b", lambda x, y: x * x + y), ("2a + 3b", lambda x, y: 2 * x + 3 * y), ("a × b − a", lambda x, y: x * y - x), ("(a + b)²", lambda x, y: (x + y) ** 2), ("a² − b²", lambda x, y: x * x - y * y)])
    return Q(f"If a {s} b = {k[0]}, find {p} {s} {q}.", k[1](p, q), f"Substitute a = {p}, b = {q}: {k[1](p, q)}.", [k[1](q, p), k[1](p, q) + 1, k[1](p, q) + p + 1])


# ------------------------------------------------------------------- alphanumeric
@T(C, "Alphanumeric series")
def _(r):
    chars = r.sample(list("ABCDEFGHJKLMNPQRTUVWXY") * 2 + list("23456789@#$%&"), 18)
    k, side = r.randint(3, 12), r.choice(["left", "right"])
    s = chars if side == "left" else chars[::-1]
    ans = s[k - 1]
    pool = [x for x in dict.fromkeys(chars) if x != ans]
    return Q(f"In the series {' '.join(chars)}, which is the {k}th element from the {side}?", ans, f"Count {k} from the {side}.", pool[:6])


@T(C, "Alphanumeric series")
def _(r):
    chars = r.sample(list("ABCDEFGHJKLMNPQRTUVWXY") + list("23456789") + list("@#$%&"), 20)
    n = sum(1 for i in range(1, len(chars)) if chars[i].isdigit() and chars[i - 1].isalpha())
    return Q(f"In the series {' '.join(chars)}, how many digits come immediately after a letter?", n, f"Check each digit's left neighbour. The count is {n}.", [x for x in range(0, 10) if x != n][:6])


@T(C, "Alphanumeric series")
def _(r):
    chars = r.sample(list("ABCDEFGHJKLMNPQRTUVWXY") + list("23456789") + list("@#$%&"), 18)
    n = sum(1 for c in chars if not c.isalnum())
    return Q(f"How many symbols (not letters or digits) are in {' '.join(chars)}?", n, f"Count the symbols: {n}.", [x for x in range(0, 8) if x != n][:6])


# ------------------------------------------------------------------- truth and lies (brute force)
@T(C, "Truth & lie puzzles")
def _(r):
    who = r.sample(NAMES, 3)
    while True:
        stm = {}
        for p in who:
            o = r.choice([x for x in who if x != p])
            kind = r.choice(["liar", "truth"])
            stm[p] = (o, kind)
        sols = []
        for vals in itertools.product([True, False], repeat=3):
            v = dict(zip(who, vals))
            ok = all(v[p] == ((not v[o]) if kind == "liar" else v[o]) for p, (o, kind) in stm.items())
            if ok and sum(vals) == 1:
                sols.append(v)
        if len(sols) == 1:
            honest = next(p for p in who if sols[0][p])
            text = ". ".join(f"{p} says, \"{o} is a {'liar' if k == 'liar' else 'truth-teller'}\"" for p, (o, k) in stm.items())
            return Q(f"Exactly one of three people tells the truth, and the others always lie. {text}. Who tells the truth?", honest, "Test each person as the one truth-teller. Only this case makes all three statements consistent.", [p for p in who if p != honest] + ["Cannot be determined"])


@T(C, "Truth & lie puzzles")
def _(r):
    who = r.sample(NAMES, 4)
    culprit = r.choice(who)
    a, b, c, d = who
    stm = {a: (b, True), b: (d, True), c: (c, False), d: (b, False)}  # (x, True) "x did it"; (x, False) "x did not"
    for cand in who:
        n = sum((cand == x) == flag for x, flag in stm.values())
        if n == 1:
            return Q(f"One of four took a pen, and exactly one of them speaks the truth. {a}: \"{b} took it.\" {b}: \"{d} took it.\" {c}: \"I did not take it.\" {d}: \"{b} did not take it.\" Who took it?", cand, f"If {cand} took it, exactly one statement is true. No other person gives exactly one true statement.", [x for x in who if x != cand])
    raise ValueError


@T(C, "Truth & lie puzzles")
def _(r):
    who = r.sample(NAMES, 2)
    return Q(f"{who[0]} says, \"{who[1]} and I are both liars.\" Each person is either a truth-teller or a liar. What are they?", f"{who[0]} is a liar and {who[1]} is a truth-teller", f"A truth-teller could not claim to be a liar, so {who[0]} lies. The claim is then false, so they are not both liars: {who[1]} tells the truth.", [f"Both are liars", f"Both are truth-tellers", f"{who[0]} is a truth-teller and {who[1]} is a liar"])


# ------------------------------------------------------------------- data sufficiency
DS = ["Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are needed", "Neither is sufficient, even together"]


@T(C, "Data sufficiency (reasoning)")
def _(r):
    a, b, c = r.sample(NAMES, 3)
    return Q(f"Who is the tallest of {a}, {b} and {c}? (1) {a} is taller than {b}. (2) {c} is taller than {a}.", DS[2], f"Together: {c} > {a} > {b}. Alone, each leaves a person unplaced.", [DS[0], DS[1], DS[3]])


@T(C, "Data sufficiency (reasoning)")
def _(r):
    a, b, c = r.sample(NAMES, 3)
    return Q(f"Who is the tallest of {a}, {b} and {c}? (1) {a} is taller than {b}. (2) {c} is taller than {b}.", DS[3], f"{a} and {c} are never compared.", [DS[0], DS[1], DS[2]])


@T(C, "Data sufficiency (reasoning)")
def _(r):
    a, b, c = r.sample(NAMES, 3)
    k = r.randint(2, 9)
    return Q(f"What is {a}'s rank in a class? (1) {a} is {k}th from the top. (2) {b} is just above {c}.", DS[0], "Statement 1 states the rank directly; statement 2 does not mention it.", [DS[1], DS[2], DS[3]])


@T(C, "Data sufficiency (reasoning)")
def _(r):
    a, b = r.sample(NAMES, 2)
    d, k = r.choice(["North", "South", "East", "West"]), r.randint(2, 15)
    return Q(f"In which direction is {a}'s house from the school? (1) {b}'s house is north of the school. (2) {a}'s house is {k} km {d} of the school.", DS[1], "Statement 2 gives it directly; statement 1 is about someone else.", [DS[0], DS[2], DS[3]])


# ------------------------------------------------------------------- questions that need judgement
hand(C, "Statement & conclusion", [
    ("Statement: All engineers at the firm must complete security training. Rahul is an engineer at the firm. Conclusion: Rahul must complete security training. Does it follow?", "Yes, it definitely follows", "No, it does not follow", "It follows only if Rahul agrees", "Data is contradictory", "A general rule applied directly to a member."),
    ("Statement: Sales rose after the discount campaign. Conclusion: The campaign caused the rise. Does it definitely follow?", "No, it does not definitely follow", "Yes, it definitely follows", "It follows only for discounts", "The statement is false", "Timing alone does not prove the cause."),
    ("Statement: Most students in this college live in hostels. Conclusion: Some students of this college live in hostels. Does it follow?", "Yes", "No", "Only if the college is large", "Cannot be judged", "If most do, then at least some do."),
    ("Statement: The train is late only when it rains. It did not rain today. Conclusion: The train was not late today. Does it follow?", "Yes", "No", "Only in summer", "Cannot be judged", "\"Only when it rains\" makes rain necessary for lateness."),
    ("Statement: No member of the team knows Spanish. Priya is on the team. Conclusion: Priya does not know Spanish. Does it follow?", "Yes", "No", "Only if she says so", "Cannot be judged", "\"No member\" includes Priya."),
    ("Statement: The shop sells some imported phones. Conclusion: Every phone in the shop is imported. Does it follow?", "No", "Yes", "Yes, if the shop is big", "Cannot be judged", "\"Some\" does not mean \"every\"."),
    ("Statement: Exercise improves health. Conclusion: People who do not exercise are always unhealthy. Does it follow?", "No", "Yes", "Only for adults", "Cannot be judged", "The statement does not say exercise is the only route to health."),
    ("Statement: The office opens at 9 a.m. on weekdays. Today is Wednesday. Conclusion: The office opens at 9 a.m. today. Does it follow?", "Yes", "No", "Only in winter", "Cannot be judged", "Wednesday is a weekday."),
    ("Statement: All the bulbs in this box are new. Conclusion: At least one bulb in the box might be used. Does it follow?", "No", "Yes", "Only if the box is opened", "Cannot be judged", "It contradicts \"all are new\"."),
    ("Statement: Fuel prices have increased by 15%. Conclusion: Everyone will stop driving. Does it follow?", "No", "Yes", "Yes, within a month", "Cannot be judged", "An extreme conclusion that the statement does not support."),
    ("Statement: Only registered users can post. Asha posted a comment. Conclusion: Asha is a registered user. Does it follow?", "Yes", "No", "Only if she paid", "Cannot be judged", "Posting requires registration."),
    ("Statement: Some cars in the lot are electric. All electric cars are charged overnight. Conclusion: Some cars in the lot are charged overnight. Does it follow?", "Yes", "No", "Only the new ones", "Cannot be judged", "The electric ones in the lot are those cars."),
])
hand(C, "Statement & assumption", [
    ("Statement: \"Hire more support staff to reduce waiting times.\" What is assumed?", "More staff can reduce waiting times", "Customers enjoy waiting", "Staff are paid too much", "Waiting times do not matter", "The advice only makes sense if staffing affects waiting."),
    ("Statement: \"Advertise on television to increase sales.\" What is assumed?", "Viewers can be influenced by the advertisement", "Television is free", "Sales cannot increase", "Everyone owns a television", "Advertising is pointless unless it can influence buyers; it need not reach everyone."),
    ("Statement: \"Carry an umbrella; it may rain.\" What is assumed?", "An umbrella helps if it rains", "It will certainly rain", "It never rains here", "Umbrellas are cheap", "\"May\" does not assume certainty."),
    ("Statement: \"Use this app to learn English in 30 days.\" What is assumed?", "Some people want to learn English", "Everyone already knows English", "No other app exists", "English takes years", "The offer presumes demand; exclusivity is not assumed."),
    ("Statement: \"Please do not park here; the road is narrow.\" What is assumed?", "People will generally heed the request", "The road will be widened", "Nobody owns a car", "Parking is illegal everywhere", "A request presumes it may be followed."),
    ("Statement: \"Our new policy will reduce employee turnover.\" What is assumed?", "Turnover can be affected by company policy", "Turnover is zero", "Employees dislike all policies", "Pay does not matter", "Otherwise a policy could not reduce it."),
    ("Statement: \"Book your tickets early to avoid disappointment.\" What is assumed?", "Tickets may run out", "Tickets are free", "Everyone will attend", "The show will be cancelled", "Early booking only helps if supply is limited."),
    ("Statement: \"Add an index to speed up this query.\" What is assumed?", "The query can use such an index", "All queries are slow", "Indexes never cost anything", "The table is empty", "An index helps only if the query can use it."),
    ("Statement: \"Train your staff, and errors will fall.\" What is assumed?", "Some errors result from lack of training", "Staff make no errors", "Training is free", "All errors will end", "Otherwise training could not reduce errors."),
    ("Statement: \"Take this medicine after food.\" What is assumed?", "The patient will have food", "The patient dislikes the medicine", "Food is harmful", "The medicine is a food", "The instruction presumes the patient eats."),
    ("Statement: \"Reduce the price and more people will buy.\" What is assumed?", "Demand responds to price", "The product is free", "Nobody buys it today", "Quality is falling", "The claim relies on price sensitivity."),
    ("Statement: \"Keep your password secret.\" What is assumed?", "Sharing a password can cause harm", "Passwords are unnecessary", "Everyone knows your password", "Accounts cannot be hacked", "Secrecy matters only if disclosure carries a risk."),
])
hand(C, "Statement & argument", [
    ("Should college attendance be compulsory? Argument: Yes, because attending classes helps students learn from teachers and peers. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "It gives a relevant reason linked to the outcome."),
    ("Should the city ban plastic bags? Argument: No, because my uncle sells plastic bags. Is this strong?", "Weak", "Strong", "Strong for the seller", "Cannot be judged", "A personal case is not a general reason."),
    ("Should employees be allowed to work from home? Argument: Yes, because it saves commute time and many roles can be done remotely. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "It gives relevant, general benefits."),
    ("Should the voting age be lowered? Argument: No, because all other countries do it differently. Is this strong?", "Weak", "Strong", "Strong if true", "Cannot be judged", "It rests on an unsupported generalisation, and copying others is not itself a reason."),
    ("Should school uniforms be mandatory? Argument: Yes, because uniforms reduce visible differences between students. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "A relevant effect on the school environment."),
    ("Should the company adopt code reviews? Argument: Yes, because reviews catch defects earlier, when they are cheaper to fix. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "A direct, relevant benefit."),
    ("Should the company adopt code reviews? Argument: No, because reviews are boring. Is this strong?", "Weak", "Strong", "Strong for juniors", "Cannot be judged", "Personal taste is not a reason about outcomes."),
    ("Should smoking in public places be banned? Argument: Yes, because second-hand smoke harms others. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "A relevant public-health reason."),
    ("Should cities build more metro lines? Argument: No, because trains are noisy for those who ride them. Is this strong?", "Weak", "Strong", "Strong for riders", "Cannot be judged", "A minor issue, not weighed against the main goals."),
    ("Should exams be held online? Argument: Yes, because everything modern is better. Is this strong?", "Weak", "Strong", "Strong if cheap", "Cannot be judged", "A sweeping claim with no real reason."),
    ("Should the government subsidise vaccines? Argument: Yes, because wider vaccination reduces disease for everyone. Is this strong?", "Strong", "Weak", "Irrelevant", "Cannot be judged", "A relevant benefit at the level of the decision."),
    ("Should banks be open on Sundays? Argument: No, because Sunday comes after Saturday. Is this strong?", "Weak", "Strong", "Strong in some regions", "Cannot be judged", "A true fact, but irrelevant."),
])
hand(C, "Course of action", [
    ("A city's main bridge has developed cracks. What is the best immediate action?", "Close or restrict the bridge and inspect it", "Ignore it until it fails", "Hold a public celebration", "Build a new city", "Safety comes first, and inspection is proportionate."),
    ("A production service has started returning errors after a release. What should the team do first?", "Roll back the release and investigate", "Delete the database", "Wait until next week", "Fire the developer", "Restore service first, then find the cause."),
    ("Many students failed a new exam. What is the most sensible action?", "Review the teaching and the exam, and offer support", "Close the college", "Abolish all exams forever", "Do nothing", "It addresses possible causes proportionately."),
    ("A food stall is found selling spoiled food. What is the most suitable action?", "Inspect, stop the sale and penalise under the rules", "Ban all food in the city", "Ignore it", "Publicly attack the owner's family", "Targeted and proportionate."),
    ("A team keeps missing deadlines. What should the manager do first?", "Find out the causes with the team", "Replace everyone", "Cancel all meetings forever", "Remove all testing", "Diagnosis must come before a remedy."),
    ("Heavy rain is forecast, and low areas may flood. What should authorities do?", "Warn residents and prepare evacuation", "Stop weather forecasts", "Ask people to ignore the rain", "Close all schools for a year", "Timely and proportionate."),
    ("A customer's data may have leaked. What should the company do first?", "Contain the leak, assess it and follow its notification duties", "Hide it", "Delete all logs", "Blame the customer", "Containment and duty to report; hiding worsens it."),
    ("Road accidents have risen at one junction. What is the best action?", "Study the junction and improve signals or signs", "Ban all vehicles", "Remove all traffic police", "Ignore the data", "Fixes the location's specific problem."),
    ("A key employee has resigned with a month's notice. What should the team do?", "Arrange a handover and document their knowledge", "Refuse the resignation", "Stop the project at once", "Do nothing until they leave", "Practical and timely."),
    ("A school's drinking water is found contaminated. What is the right action?", "Stop its use, provide safe water and find the source", "Tell students to drink less", "Close the school forever", "Ignore the test", "Immediate safety, then the root cause."),
    ("A website is very slow during sales. What is the sensible long-term action?", "Load test it, then fix bottlenecks and scale", "Cancel all sales", "Remove the website", "Ask customers to come back another year", "Addresses the actual cause."),
    ("An employee is repeatedly late. What is the sensible first action?", "Talk to the employee and understand why", "Dismiss them at once", "Announce it publicly", "Ignore it forever", "Proportionate first step."),
])
hand(C, "Cause & effect", [
    ("A: Prices of vegetables rose sharply. B: Heavy rains destroyed crops. How are they related?", "B is the cause and A is its effect", "A is the cause and B is its effect", "Both are independent", "Both are effects of a common cause", "Crop loss reduces supply, raising prices."),
    ("A: The factory closed. B: Hundreds of workers lost their jobs. How are they related?", "A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "Closure leads to job loss."),
    ("A: Schools were closed. B: Offices were closed. Both happened during a major storm. How are A and B related?", "Both are effects of a common cause", "A is the cause of B", "B is the cause of A", "They are unrelated", "The storm caused both."),
    ("A: The server ran out of memory. B: The service crashed. How are they related?", "A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "Out-of-memory conditions crash a process."),
    ("A: The cricket team won the match. B: A train arrived late in another city. How are they related?", "They are independent", "A causes B", "B causes A", "Both have a common cause", "No connection."),
    ("A: The government reduced fuel tax. B: Fuel became cheaper. How are they related?", "A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "Lower tax lowers the price."),
    ("A: Sales of umbrellas rose. B: Sales of raincoats rose. How are they related?", "Both are effects of a common cause", "A is the cause of B", "B is the cause of A", "They are unrelated", "Rainy weather likely drives both."),
    ("A: Many students scored full marks. B: The exam paper was unusually easy. How are they related?", "B is the cause and A is its effect", "A is the cause and B is its effect", "Both are independent", "Both are effects of a common cause", "An easy paper raises scores."),
    ("A: The river overflowed. B: Nearby villages were flooded. How are they related?", "A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "Overflow floods nearby land."),
    ("A: The database query lacked an index. B: The page took 8 seconds to load. How are they related?", "A is the likely cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "A full scan slows the response."),
    ("A: There was a power cut in the town. B: Street lights went off. How are they related?", "A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause", "No power means no lights."),
    ("A: The company hired more people. B: A new moon was seen. How are they related?", "They are independent", "A causes B", "B causes A", "Both have a common cause", "No connection."),
])
hand(C, "Critical reasoning", [
    ("A company says its new tool saved time because tasks finished faster after launch. Which fact most weakens this?", "Task sizes were also cut at the same time", "The tool has a blue logo", "The company is 10 years old", "Staff use laptops", "Smaller tasks offer another explanation."),
    ("\"Students who attend extra classes score higher, so extra classes raise scores.\" What most weakens this?", "Only already strong students chose to attend", "Classes are held on Saturdays", "Scores are given out of 100", "The school has a library", "Selection could explain the gap."),
    ("\"Our app's users are happy: 95% of the survey replies were positive.\" What is the main flaw?", "Unhappy users may not have replied", "95 is a large number", "Surveys use questions", "Apps have users", "Response bias."),
    ("A town installed cameras and burglaries fell by 20%. Which fact most strengthens the idea that cameras helped?", "Burglaries did not fall in similar towns without cameras", "Cameras are expensive", "The town has many shops", "Burglars dislike rain", "It provides a comparison group."),
    ("\"All my friends like this film, so everybody will.\" What is the flaw?", "It generalises from a small, unrepresentative sample", "It uses the word film", "Friends cannot watch films", "It is about friends", "Hasty generalisation."),
    ("\"Ice-cream sales and drowning both rise in summer, so ice-cream causes drowning.\" What is the flaw?", "Correlation is mistaken for causation", "Ice-cream is cold", "Summer is short", "Nobody drowns", "Hot weather explains both."),
    ("\"Sir, this bug cannot be in my code, as I am a good programmer.\" What is the flaw?", "It relies on the person rather than on evidence", "It is too short", "It mentions code", "It is polite", "An appeal to self, with no evidence."),
    ("\"We must either use microservices or fail.\" What is the flaw?", "It presents a false choice", "Microservices do not exist", "It uses a modal verb", "It mentions failure", "Other options exist, such as a modular monolith."),
    ("Conclusion: The new policy reduced absences. Which assumption does this need?", "Nothing else changed that could have reduced absences", "Everyone likes the policy", "Absences were zero before", "The policy was long", "Otherwise another cause might be responsible."),
    ("\"Sales fell after we changed the logo, so the logo caused it.\" Which question is most useful?", "What else changed in the same period?", "What colour is the logo?", "Who designed the old logo?", "Do customers own phones?", "It checks for other causes."),
    ("A study of 10 people found that a diet works. Why be cautious?", "The sample is very small", "Diets involve food", "Ten is an even number", "People eat daily", "Small samples are unreliable."),
    ("\"A famous actor uses this bank, so it is the safest.\" What is the flaw?", "It appeals to an irrelevant authority", "Actors have money", "Banks are buildings", "It uses the word safe", "Fame does not show banking expertise."),
])
hand(C, "Decision making", [
    ("Rule: Candidates need a 60% degree score and 2 years of experience. Ravi has 72% and 3 years. What is the decision?", "Select", "Reject", "Refer to the manager", "Data is inadequate", "Meets both conditions."),
    ("Rule: Candidates need a 60% degree score and 2 years of experience. Sara has 58% and 5 years. What is the decision?", "Reject", "Select", "Refer to the manager", "Data is inadequate", "Fails the score condition, and no exception is stated."),
    ("Rule: Candidates need 60%, and those with less than 60% but over 5 years' experience are referred to the manager. Om has 55% and 6 years. What is the decision?", "Refer to the manager", "Select", "Reject", "Data is inadequate", "The exception applies."),
    ("Rule: A loan needs salary over ₹30,000 and a credit score over 700. Lata earns ₹45,000, and her credit score is not given. What is the decision?", "Data is inadequate", "Approve", "Reject", "Refer to the manager", "The credit score is missing."),
    ("Rule: Leave over 5 days needs a director's approval. Jay asks for 3 days. Who can decide?", "It does not need the director", "Only the director", "The CEO", "Data is inadequate", "It is below the threshold."),
    ("Rule: Refund if returned within 30 days with a receipt. Uma returns an item on day 20, with a receipt. What is the decision?", "Refund", "Refuse", "Refer to the manager", "Data is inadequate", "Both conditions hold."),
    ("Rule: Refund if returned within 30 days with a receipt. Hari returns an item on day 40, with a receipt. What is the decision?", "Refuse", "Refund", "Refer to the manager", "Data is inadequate", "Past the limit."),
    ("Rule: Admit if age is 18 to 25 and the entrance score is above 70. Tara is 24 and scored 70. What is the decision?", "Do not admit", "Admit", "Refer to the manager", "Data is inadequate", "The score must be above 70."),
    ("Rule: Admit if age is 18 to 25 and the entrance score is above 70. Neel is 25 and scored 85. What is the decision?", "Admit", "Do not admit", "Refer to the manager", "Data is inadequate", "Both conditions hold, as 25 is within the range."),
    ("Rule: Bonus for those rated above 4 with over a year of service. Kabir is rated 4.5 and has 8 months' service. What is the decision?", "No bonus", "Bonus", "Refer to the manager", "Data is inadequate", "Service is under a year."),
    ("Rule: Deploy on Friday only with a director's approval. A team has no approval, and it is Friday. What should it do?", "Do not deploy", "Deploy", "Deploy half of it", "Data is inadequate", "The condition is not met."),
    ("Rule: Candidates must speak Hindi or Tamil. Anu speaks Tamil only. What is the decision?", "Eligible", "Not eligible", "Refer to the manager", "Data is inadequate", "\"Or\" needs only one."),
])
