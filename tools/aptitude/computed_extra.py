"""More computed templates: thin quant and figure types, and computer science worked out by simulation."""
import ipaddress
import sqlite3
from math import comb, factorial, gcd

from core import F, Q, T, fmt, hand
from figures import INK, polygon, strip, svg, choices

# ------------------------------------------------------------------- quant
C = "Profit & Loss"


@T(C, "Dishonest dealings")
def _(r):
    w = r.choice(range(500, 980, 20))
    ans = F((1000 - w) * 100, w)
    return Q(f"A grocer claims no profit but gives {w} g for each kg charged. What is the profit percentage?", f"{float(ans):.2f}%", f"(1000 − {w}) ÷ {w} × 100 = {float(ans):.2f}%.", [f"{(1000 - w) / 10:.2f}%", f"{float(ans) + 2:.2f}%", f"{float(ans) + 5:.2f}%"])


@T(C, "Dishonest dealings")
def _(r):
    p = r.choice([5, 10, 15, 20, 25])
    q = r.choice([5, 10, 15, 20])
    ans = (F(100 + p, 100) * F(100 + q, 100) - 1) * 100
    return Q(f"A trader cheats by {p}% while buying (gets {100 + p} g for each 100 g paid for) and by {q}% while selling (charges for {100 + q} g when giving 100 g). What is the overall profit percentage?", f"{float(ans):.2f}%", f"(1 + {p}/100)(1 + {q}/100) − 1 = {float(ans):.2f}%.", [f"{p + q}%", f"{float(ans) + 3:.2f}%", f"{abs(p - q)}%"])


C = "Permutation & Combination"


@T(C, "Permutations")
def _(r):
    n = r.randint(5, 9)
    v = r.randint(2, n - 2)
    return Q(f"In how many ways can {n} books be arranged on a shelf if {v} particular books stay together?", factorial(n - v + 1) * factorial(v), f"Treat the {v} books as one: ({n - v + 1})! × {v}! = {factorial(n - v + 1) * factorial(v)}.", [factorial(n), factorial(n - v), factorial(n - v + 1)])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(3, 7)
    return Q(f"In how many ways can {n} men and {n} women sit around a round table so that no two men sit together?", factorial(n - 1) * factorial(n), f"Seat the men: ({n} − 1)!. The women fill the {n} gaps: {n}!. Total = {factorial(n - 1) * factorial(n)}.", [factorial(2 * n - 1), factorial(n) ** 2, factorial(n - 1) ** 2])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(5, 12)
    ans = factorial(n - 1) - 2 * factorial(n - 2)
    return Q(f"{n} people sit around a round table. In how many ways can two particular people avoid sitting together?", ans, f"Total ({n} − 1)! minus those together, 2 × ({n} − 2)!: {ans}.", [factorial(n - 1), 2 * factorial(n - 2), factorial(n - 2)])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(11, 16)
    return Q(f"In how many ways can {n} people sit around a round table? Give the answer as a factorial.", f"{n - 1}!", f"Fix one person: ({n} − 1)!.", [f"{n}!", f"{n - 2}!", f"{n + 1}!"])


@T(C, "Circular permutations")
def _(r):
    n, k = r.randint(6, 12), r.randint(3, 5)
    ans = comb(n, k) * factorial(k - 1)
    return Q(f"In how many ways can {k} people be chosen from {n} and seated around a round table?", ans, f"{n}C{k} × ({k} − 1)! = {comb(n, k)} × {factorial(k - 1)} = {ans}.", [comb(n, k), comb(n, k) * factorial(k), factorial(k - 1)])


@T(C, "Circular permutations")
def _(r):
    n, k = r.randint(5, 12), r.randint(2, 4)
    ans = factorial(n - k) * factorial(k)
    return Q(f"{n} people sit around a round table. In how many ways can {k} particular people sit next to each other?", ans, f"Treat them as one: ({n - k + 1} − 1)! × {k}! = {ans}.", [factorial(n - 1), factorial(n - k), ans * 2])


# ------------------------------------------------------------------- figures
C = "Non-Verbal Reasoning"


@T(C, "Paper folding & cutting")
def _(r):
    a, b = r.randint(1, 3), r.randint(1, 3)
    holes = r.randint(1, 4)
    return Q(f"A sheet is folded in half {a} time{'s' if a > 1 else ''} along its length and {b} time{'s' if b > 1 else ''} along its width. It is then punched with {holes} hole{'s' if holes > 1 else ''}. How many holes appear when it is opened?", holes * 2 ** (a + b), f"Layers = 2^{a + b}. Holes = {holes} × {2 ** (a + b)} = {holes * 2 ** (a + b)}.", [holes * (a + b), holes * 2 ** (a + b - 1), holes + 2 ** (a + b)])


@T(C, "Embedded figures")
def _(r):
    a, b, c = r.sample(range(3, 9), 3)
    fig = polygon(a, False, 32, 32, 28) + polygon(b, False, 32, 32, 18) + polygon(c, False, 32, 32, 9)
    wrong = [x for x in range(3, 10) if x not in (a, b, c)]
    r.shuffle(wrong)
    ans = r.choice([a, b, c])
    return Q("Three shapes are drawn one inside another. Which shape is part of this figure?", "", f"The figure contains shapes with {a}, {b} and {c} sides, so the {ans}-sided shape is in it.", [], strip([fig], False), choices(polygon(ans), [polygon(x) for x in wrong[:3]]))


@T(C, "Counting figures")
def _(r):
    n = r.randint(2, 20)
    return Q(f"A straight line has {n} points marked on it. How many line segments do these points define?", comb(n, 2), f"Pick any 2 of the {n} points: {comb(n, 2)}.", [n - 1, n, n * n])


@T(C, "Counting figures")
def _(r):
    n = r.randint(3, 20)
    return Q(f"In a convex polygon with {n} sides, how many triangles can be formed using its corners?", comb(n, 3), f"Choose 3 of the {n} corners: {comb(n, 3)}.", [comb(n, 2), n - 2, comb(n, 3) + n])


@T(C, "Counting figures")
def _(r):
    m, n = r.randint(1, 8), r.randint(1, 8)
    return Q(f"A rectangle is crossed by {m} line{'s' if m > 1 else ''} parallel to its length and {n} parallel to its width. How many rectangles does the figure contain?", comb(m + 2, 2) * comb(n + 2, 2), f"Choose 2 of {m + 2} horizontal and 2 of {n + 2} vertical lines: {comb(m + 2, 2)} × {comb(n + 2, 2)}.", [(m + 1) * (n + 1), m * n, comb(m + 2, 2) + comb(n + 2, 2)])


# ------------------------------------------------------------------- computer fundamentals
C = "Core Computer Science"


@T(C, "Computer fundamentals")
def _(r):
    n = r.randint(2, 512)
    u, f = r.choice([("KB", 1024), ("MB", 1024)])
    return Q(f"Using 1 {u} = 1024 of the smaller unit, how many {'bytes' if u == 'KB' else 'KB'} are in {n} {u}?", n * f, f"{n} × 1024 = {n * f}.", [n * 1000, n * 512, n * f + 24])


@T(C, "Computer fundamentals")
def _(r):
    n = r.randint(4, 32)
    return Q(f"How many different values can {n} bits represent?", f"2^{n}", f"Each bit doubles the count: 2^{n}.", [f"{n}^2", f"2^{n + 1}", f"2^{n - 1}", f"{2 * n}"])


@T(C, "Computer fundamentals")
def _(r):
    n = r.randint(3, 16)
    return Q(f"What is the largest unsigned integer that fits in {n} bits?", 2 ** n - 1, f"2^{n} − 1 = {2 ** n - 1}.", [2 ** n, 2 ** (n - 1), 2 ** (n - 1) - 1])


@T(C, "Computer fundamentals")
def _(r):
    n = r.randint(3, 16)
    return Q(f"What range does a {n}-bit two's complement integer hold?", f"−{2 ** (n - 1)} to {2 ** (n - 1) - 1}", f"From −2^{n - 1} to 2^{n - 1} − 1.", [f"−{2 ** (n - 1) - 1} to {2 ** (n - 1)}", f"0 to {2 ** n - 1}", f"−{2 ** n} to {2 ** n}"])


@T(C, "Computer fundamentals")
def _(r):
    a, b = r.randint(1, 255), r.randint(1, 255)
    op, f = r.choice([("AND", lambda x, y: x & y), ("OR", lambda x, y: x | y), ("XOR", lambda x, y: x ^ y)])
    return Q(f"What is {a} {op} {b}, as a decimal number, applied bit by bit?", f(a, b), f"{a:08b} {op} {b:08b} = {f(a, b):08b} = {f(a, b)}.", [a + b, abs(a - b) + 1, f(a, b) + 1])


hand(C, "Computer fundamentals", [
    ("Which memory is non-volatile?", "SSD", "RAM", "CPU cache", "CPU register", "It keeps data without power."),
    ("Which translates and runs code line by line?", "Interpreter", "Linker", "Assembler", "Loader", "No separate output file is needed."),
    ("Which combines object files into one executable?", "Linker", "Compiler", "Debugger", "Editor", "It resolves references."),
    ("Which converts assembly into machine code?", "Assembler", "Linker", "Browser", "Loader", "One step below a compiler."),
    ("What is firmware?", "Software stored on a hardware device", "A type of monitor", "A virus", "A network cable", "It controls the device."),
    ("GPU stands for", "Graphics Processing Unit", "General Program Unit", "Global Power Unit", "Graph Parsing Utility", "Built for parallel work."),
    ("Which is an output device?", "Monitor", "Mouse", "Scanner", "Microphone", "It shows information."),
    ("One nibble has how many bits?", "4", "2", "8", "16", "Half a byte."),
    ("Unicode was created to", "Represent characters of the world's languages", "Compress video", "Encrypt files", "Speed up disks", "ASCII covers little beyond English."),
    ("UTF-8 uses how many bytes for an ASCII character?", "1", "2", "3", "4", "It stays compatible with ASCII."),
    ("Which is open-source?", "Linux", "Windows", "macOS", "Microsoft Word", "Its source code is public."),
    ("What does a bus do in a computer?", "Carries data between components", "Stores files permanently", "Cools the CPU", "Prints pages", "Address, data and control buses."),
    ("Moore's law observed that", "Transistor counts roughly double about every two years", "Disks fail every two years", "RAM prices never change", "CPUs need no cooling", "An observation, now slowing."),
    ("Which number is hexadecimal F in decimal?", "15", "16", "14", "10", "A to F mean 10 to 15."),
    ("What does the fetch-decode-execute cycle describe?", "How a CPU runs instructions", "How a printer prints", "How a disk is formatted", "How a network routes", "The basic CPU loop."),
])


# ------------------------------------------------------------------- data structures, by simulation
@T(C, "Data structures & algorithms")
def _(r):
    ops, stack, popped = [], [], None
    for x in r.sample(range(1, 60), 6):
        ops.append(f"push {x}")
        stack.append(x)
        if r.random() < .4 and stack:
            ops.append("pop")
            popped = stack.pop()
    if not stack:
        ops.append("push 7")
        stack.append(7)
    return Q(f"After these operations on an empty stack, what is on top?\n\n{', '.join(ops)}", stack[-1], f"The stack holds {stack}, so the top is {stack[-1]}.", [x for x in stack[:-1]] + [popped or 99, stack[-1] + 1, stack[-1] + 2])


@T(C, "Data structures & algorithms")
def _(r):
    ops, q = [], []
    for x in r.sample(range(1, 60), 6):
        ops.append(f"enqueue {x}")
        q.append(x)
        if r.random() < .4 and q:
            ops.append("dequeue")
            q.pop(0)
    if not q:
        ops.append("enqueue 7")
        q.append(7)
    return Q(f"After these operations on an empty queue, what is at the front?\n\n{', '.join(ops)}", q[0], f"The queue holds {q}, so the front is {q[0]}.", q[1:] + [q[0] + 1, q[0] + 2, q[-1] + 3])


@T(C, "Data structures & algorithms")
def _(r):
    keys = r.sample(range(1, 99), r.randint(5, 8))
    tree = None

    def insert(t, k):
        if t is None:
            return [k, None, None]
        t[1 if k < t[0] else 2] = insert(t[1 if k < t[0] else 2], k)
        return t

    def height(t):
        return 0 if t is None else 1 + max(height(t[1]), height(t[2]))

    def pre(t):
        return [] if t is None else [t[0]] + pre(t[1]) + pre(t[2])
    for k in keys:
        tree = insert(tree, k)
    if r.random() < .5:
        return Q(f"Keys {', '.join(map(str, keys))} are inserted in order into an empty BST. What is its height, counted in nodes on the longest path?", height(tree), f"Building the tree gives a longest root-to-leaf path of {height(tree)} nodes.", [height(tree) + 1, max(height(tree) - 1, 1), len(keys)])
    ans = " ".join(map(str, pre(tree)))
    return Q(f"Keys {', '.join(map(str, keys))} are inserted in order into an empty BST. What is the preorder traversal?", ans, "Preorder visits node, left subtree, right subtree.", [" ".join(map(str, sorted(keys))), " ".join(map(str, keys[::-1])), " ".join(map(str, sorted(keys, reverse=True)))])


@T(C, "Data structures & algorithms")
def _(r):
    a = sorted(r.sample(range(1, 200), r.randint(7, 15)))
    x = r.choice(a)
    lo, hi, n = 0, len(a) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        n += 1
        if a[mid] == x:
            break
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return Q(f"Binary search looks for {x} in {a}, using mid = (lo + hi) / 2 rounded down. How many elements are compared?", n, f"The search halves the range and finds it on comparison {n}.", [x2 for x2 in range(1, 8) if x2 != n][:5])


@T(C, "Data structures & algorithms")
def _(r):
    a = r.sample(range(1, 99), 6)
    b = a[:]
    for i in range(len(b) - 1):
        if b[i] > b[i + 1]:
            b[i], b[i + 1] = b[i + 1], b[i]
    return Q(f"What is the array {a} after one full pass of bubble sort (ascending)?", " ".join(map(str, b)), "Each adjacent pair is swapped if out of order, so the largest moves to the end.", [" ".join(map(str, sorted(a))), " ".join(map(str, a[::-1])), " ".join(map(str, a[1:] + a[:1]))])


@T(C, "Data structures & algorithms")
def _(r):
    n = r.randint(1, 12)
    k = r.choice(["height", "leaves", "edges"])
    if k == "height":
        return Q(f"What is the most nodes a binary tree of height {n} can have (height counted in levels)?", 2 ** n - 1, f"2^{n} − 1 = {2 ** n - 1}.", [2 ** n, 2 ** (n - 1), n * 2])
    if k == "leaves":
        return Q(f"How many leaves does a full binary tree with {n + 1} levels have?", 2 ** n, f"The last level holds 2^{n} = {2 ** n} nodes.", [2 ** n - 1, 2 ** (n + 1), n])
    m = 5 * n
    return Q(f"How many edges does a complete undirected graph on {m} vertices have?", comb(m, 2), f"{m}C2 = {comb(m, 2)}.", [m, m * m, m * (m - 1)])


hand(C, "Data structures & algorithms", [
    ("Which sort is stable by default?", "Merge sort", "Quicksort", "Heap sort", "Selection sort", "Equal keys keep their order."),
    ("Which sort uses no extra array and has O(n log n) worst case?", "Heap sort", "Merge sort", "Bubble sort", "Quicksort", "In-place with guaranteed bound."),
    ("A balanced BST lookup takes", "O(log n)", "O(1)", "O(n²)", "O(n log n)", "Height stays logarithmic."),
    ("An unbalanced BST lookup can take", "O(n)", "O(1)", "O(log log n)", "O(n²)", "It can degrade to a list."),
    ("Dynamic programming relies on", "Overlapping subproblems and optimal substructure", "Random choices", "Sorting only", "Recursion without memory", "Results are reused."),
    ("Topological sort applies to", "Directed acyclic graphs", "Any undirected graph", "Only trees of height 1", "Arrays of strings", "It orders dependencies."),
    ("Which structure backs a priority queue?", "Heap", "Stack", "Linked list only", "Trie", "Fast min or max."),
    ("A trie is best for", "Prefix search on strings", "Sorting numbers", "Shortest paths", "Memory allocation", "Characters along paths."),
    ("What is hash collision?", "Two keys map to one bucket", "A key is deleted", "The table is empty", "A hash has two values", "Handled by chaining or probing."),
    ("Kruskal's algorithm finds", "A minimum spanning tree", "Shortest paths from a source", "A topological order", "The longest path", "It adds cheap edges without cycles."),
    ("A doubly linked list node holds", "Data and two pointers", "Only data", "Three data fields and no pointers", "Only one pointer", "Previous and next."),
    ("Space used by recursion depends on", "The call stack depth", "The screen size", "The number of files", "The clock speed", "Each call adds a frame."),
])


# ------------------------------------------------------------------- OOP, computed by following dispatch rules
CLS = [("Animal", "Dog"), ("Vehicle", "Car"), ("Shape", "Circle"), ("Account", "Savings"), ("Employee", "Manager"), ("Device", "Phone")]


@T(C, "OOP concepts")
def _(r):
    p, c = r.choice(CLS)
    a, b = r.sample(range(1, 99), 2)
    return Q(f"What does this Java code print?\n\n```java\nclass {p} {{ int f() {{ return {a}; }} }}\nclass {c} extends {p} {{ int f() {{ return {b}; }} }}\n// ...\n{p} x = new {c}();\nSystem.out.println(x.f());\n```", b, "Overriding is chosen at run time from the object's real type.", [a, a + b, 0])


@T(C, "OOP concepts")
def _(r):
    p, c = r.choice(CLS)
    a, b = r.sample(range(1, 99), 2)
    return Q(f"What does this Java code print?\n\n```java\nclass {p} {{ static int f() {{ return {a}; }} }}\nclass {c} extends {p} {{ static int f() {{ return {b}; }} }}\n// ...\n{p} x = new {c}();\nSystem.out.println(x.f());\n```", a, "Static methods are hidden, not overridden: the declared type decides.", [b, a + b, 0])


@T(C, "OOP concepts")
def _(r):
    p, c = r.choice(CLS)
    a, b = r.sample(range(1, 99), 2)
    return Q(f"What does this Java code print?\n\n```java\nclass {p} {{ int v = {a}; }}\nclass {c} extends {p} {{ int v = {b}; }}\n// ...\n{p} x = new {c}();\nSystem.out.println(x.v);\n```", a, "Fields are not polymorphic: the declared type decides.", [b, a + b, 0])


@T(C, "OOP concepts")
def _(r):
    p, c = r.choice(CLS)
    a, b = r.sample("ABCDEFGHJKLMNPQR", 2)
    return Q(f"What does this Java code print?\n\n```java\nclass {p} {{ {p}() {{ System.out.print(\"{a}\"); }} }}\nclass {c} extends {p} {{ {c}() {{ System.out.print(\"{b}\"); }} }}\n// ...\nnew {c}();\n```", a + b, "The parent constructor runs first.", [b + a, b, a])


@T(C, "OOP concepts")
def _(r):
    a, b = r.sample(range(1, 50), 2)
    return Q(f"What does this Java code print?\n\n```java\nint f(int x) {{ return {a}; }}\nint f(long x) {{ return {b}; }}\n// ...\nSystem.out.println(f(5));\n```", a, "An int argument matches f(int) exactly at compile time.", [b, a + b, 5])


@T(C, "OOP concepts")
def _(r):
    n = r.randint(2, 30)
    return Q(f"What does this Java code print?\n\n```java\nclass C {{ static int n = 0; C() {{ n++; }} }}\n// create {n} objects with new C(), then:\nSystem.out.println(C.n);\n```", n, f"A static field is shared, so each of the {n} constructors adds 1.", [1, 0, n + 1])


hand(C, "OOP concepts", [
    ("An interface in Java can contain", "Abstract and default methods", "Only private fields", "Constructors", "Instance variables that change", "Fields are constants."),
    ("The Liskov substitution principle says", "A subclass must be usable wherever its parent is", "Classes must be small", "Interfaces must be big", "Use only static methods", "SOLID's \"L\"."),
    ("The single responsibility principle says", "A class should have one reason to change", "A project has one class", "A method has one line", "One developer owns a class", "SOLID's \"S\"."),
    ("The open/closed principle says", "Open for extension, closed for modification", "Always use public fields", "Close all files", "Never add classes", "SOLID's \"O\"."),
    ("Dependency inversion means depending on", "Abstractions", "Concrete classes", "Global variables", "File paths", "SOLID's \"D\"."),
    ("A private member is visible in", "Its own class only", "All subclasses", "The whole package", "Everywhere", "The strictest access."),
    ("A protected member is visible in", "Its package and subclasses", "Only its own method", "Everywhere", "No other class", "Java's rule."),
    ("Which relationship is weakest?", "Association", "Composition", "Inheritance", "Aggregation", "Objects just use each other."),
    ("An abstract method has", "No body", "Only a return statement", "A private modifier", "Two bodies", "A subclass implements it."),
    ("Can a static method be overridden?", "No, it can only be hidden", "Yes, always", "Only if final", "Only in interfaces", "Static binding applies."),
    ("Can a constructor be inherited?", "No", "Yes", "Only if public", "Only if static", "Each class declares its own."),
    ("The diamond problem concerns", "Multiple inheritance of implementation", "Deep recursion", "Hash collisions", "Null pointers", "Two parents share an ancestor."),
])


# ------------------------------------------------------------------- SQL, run on a real database
NAMES = ["Asha", "Bala", "Chitra", "Dev", "Esha", "Farhan", "Gita", "Hari", "Isha", "Jay"]
DEPTS = ["HR", "IT", "Sales"]


def employees(r):
    rows = [(i + 1, n, r.choice(DEPTS), 10 * r.randint(2, 9)) for i, n in enumerate(r.sample(NAMES, r.randint(5, 7)))]
    db = sqlite3.connect(":memory:")
    db.execute("create table emp(id int, name text, dept text, pay int)")
    db.executemany("insert into emp values(?,?,?,?)", rows)
    table = "| id | name | dept | pay |\n|---|---|---|---|\n" + "\n".join("| " + " | ".join(map(str, x)) + " |" for x in rows)
    return db, table, rows


def one(db, sql):
    return db.execute(sql).fetchone()[0]


@T(C, "DBMS & SQL")
def _(r):
    db, table, rows = employees(r)
    p = 10 * r.randint(3, 8)
    d = r.choice(DEPTS)
    sql, why = r.choice([
        (f"SELECT COUNT(*) FROM emp WHERE pay > {p}", f"Count rows with pay above {p}."),
        (f"SELECT COUNT(*) FROM emp WHERE dept = '{d}' OR pay >= {p}", "OR keeps a row if either side is true."),
        (f"SELECT COUNT(*) FROM emp WHERE dept = '{d}' AND pay < {p}", "AND needs both sides to be true."),
        ("SELECT COUNT(DISTINCT dept) FROM emp", "It counts unique departments."),
    ])
    ans = one(db, sql)
    return Q(f"{table}\n\nWhat does this return?\n\n```sql\n{sql};\n```", ans, why, [x for x in range(0, 8) if x != ans][:5])


@T(C, "DBMS & SQL")
def _(r):
    db, table, rows = employees(r)
    d = r.choice(sorted({x[2] for x in rows}))
    sql, why = r.choice([
        (f"SELECT SUM(pay) FROM emp WHERE dept = '{d}'", "Add pay for that department."),
        ("SELECT MAX(pay) - MIN(pay) FROM emp", "Highest minus lowest pay."),
        ("SELECT MIN(pay) FROM emp", "The lowest pay."),
        ("SELECT pay FROM emp ORDER BY pay DESC LIMIT 1 OFFSET 1", "Sort high to low, then skip one row: the second row in that order."),
    ])
    ans = one(db, sql)
    if ans is None:
        ans = 0
    return Q(f"{table}\n\nWhat does this return?\n\n```sql\n{sql};\n```", ans, why, [ans + 10, ans + 20, abs(ans - 10) or 30, ans + 30])


@T(C, "DBMS & SQL")
def _(r):
    db, table, rows = employees(r)
    n = r.randint(1, 3)
    ans = db.execute(f"SELECT COUNT(*) FROM (SELECT dept FROM emp GROUP BY dept HAVING COUNT(*) > {n})").fetchone()[0]
    return Q(f"{table}\n\nHow many rows does this return?\n\n```sql\nSELECT dept FROM emp GROUP BY dept HAVING COUNT(*) > {n};\n```", ans, f"Only departments with more than {n} people remain: {ans}.", [x for x in range(0, 5) if x != ans])


@T(C, "DBMS & SQL")
def _(r):
    a, b = r.randint(2, 9), r.randint(2, 9)
    m = r.randint(0, min(a, b))
    k, ans, why = r.choice([("CROSS JOIN", a * b, "Every pair of rows."), ("INNER JOIN", m, "Only matching rows."), ("LEFT JOIN", a, "All left rows are kept, whether matched or not.")])
    return Q(f"Table A has {a} rows and B has {b}, with unique join keys in each. {m} keys match. How many rows does A {k} B return?", ans, why, [a * b, m, a, b, a + b - m, a + b])


hand(C, "DBMS & SQL", [
    ("A candidate key is", "A minimal set of columns that identifies a row", "Any column with text", "A foreign key always", "A sorted column", "A primary key is chosen from these."),
    ("First normal form requires", "Atomic column values", "No primary key", "Many values in one column", "Only one table", "No repeating groups."),
    ("Second normal form removes", "Partial dependency on a composite key", "All foreign keys", "Atomic values", "All indexes", "Non-key columns need the whole key."),
    ("Which isolation level allows dirty reads?", "Read uncommitted", "Read committed", "Repeatable read", "Serializable", "The weakest level."),
    ("Which isolation level is strictest?", "Serializable", "Read committed", "Read uncommitted", "Repeatable read", "As if transactions ran one by one."),
    ("A phantom read is", "New rows appearing in a repeated query", "Reading a deleted database", "A slow disk", "A locked table", "Range results change."),
    ("A view is", "A stored query that acts like a table", "A backup", "An index", "A physical copy always", "Virtual by default."),
    ("Which command undoes a transaction?", "ROLLBACK", "COMMIT", "SAVE", "GRANT", "It reverts uncommitted changes."),
    ("A clustered index", "Decides the physical order of rows", "Stores no data", "Is always on a text column", "Can exist many times per table", "At most one per table."),
    ("DELETE differs from TRUNCATE because DELETE", "Can filter rows with WHERE", "Removes the table definition", "Can never be rolled back", "Works on one row only", "TRUNCATE removes all rows."),
    ("What does the D in ACID mean?", "Durability", "Distribution", "Dependency", "Deletion", "Committed data survives failures."),
    ("What does the C in ACID mean?", "Consistency", "Concurrency", "Commit", "Cache", "Rules hold before and after."),
    ("An N+1 query problem means", "One query followed by one more per result row", "A query returns N+1 columns", "A table has N+1 keys", "An index has one extra level", "Common in ORMs."),
])


# ------------------------------------------------------------------- operating systems, by simulation
@T(C, "Operating systems")
def _(r):
    bursts = [r.randint(1, 15) for _ in range(r.randint(3, 5))]
    wait, t = [], 0
    for b in bursts:
        wait.append(t)
        t += b
    ans = F(sum(wait), len(bursts))
    return Q(f"Processes arrive together with CPU bursts {bursts}, run first-come, first-served in this order. What is the average waiting time?", ans, f"Waiting times are {wait}. Average = {fmt(ans)}.", [F(sum(bursts), len(bursts)), ans + 1, ans + 2])


@T(C, "Operating systems")
def _(r):
    bursts = [r.randint(1, 15) for _ in range(r.randint(3, 5))]
    s = sorted(bursts)
    wait, t = [], 0
    for b in s:
        wait.append(t)
        t += b
    ans = F(sum(wait), len(s))
    return Q(f"Processes arrive together with CPU bursts {bursts}. What is the average waiting time under non-preemptive shortest job first?", ans, f"Run in order {s}. Waiting times {wait}. Average = {fmt(ans)}.", [F(sum(bursts), len(bursts)), ans + 1, ans + 2])


@T(C, "Operating systems")
def _(r):
    bursts = [r.randint(2, 12) for _ in range(3)]
    q = r.randint(1, 4)
    left = bursts[:]
    t, finish = 0, [0, 0, 0]
    while any(left):
        for i in range(3):
            if left[i]:
                run = min(q, left[i])
                t += run
                left[i] -= run
                if not left[i]:
                    finish[i] = t
    return Q(f"Processes P1, P2 and P3 arrive together with bursts {bursts}. Under round robin with quantum {q}, at what time does P1 finish?", finish[0], f"Simulating the rotation, the finish times are {finish}.", [sum(bursts), bursts[0], finish[1] if finish[1] != finish[0] else finish[0] + 1, finish[2] if finish[2] != finish[0] else finish[0] + 2, finish[0] + 3])


def faults(refs, frames, lru):
    mem, n = [], 0
    for p in refs:
        if p in mem:
            if lru:
                mem.remove(p)
                mem.append(p)
            continue
        n += 1
        if len(mem) == frames:
            mem.pop(0)
        mem.append(p)
    return n


@T(C, "Operating systems")
def _(r):
    refs = [r.randint(1, 5) for _ in range(r.randint(8, 12))]
    frames = r.randint(2, 4)
    lru = r.random() < .5
    ans = faults(refs, frames, lru)
    return Q(f"Pages {' '.join(map(str, refs))} are requested with {frames} frames, initially empty. How many page faults occur under {'LRU' if lru else 'FIFO'}?", ans, f"Simulating {'LRU' if lru else 'FIFO'} gives {ans} faults.", [faults(refs, frames, not lru) if faults(refs, frames, not lru) != ans else ans + 1, ans + 1, ans + 2, max(ans - 1, 1)])


@T(C, "Operating systems")
def _(r):
    va, off = r.randint(16, 48), r.randint(10, 16)
    return Q(f"A system has {va}-bit virtual addresses and pages of 2^{off} bytes. How many bits make up the virtual page number?", va - off, f"{va} − {off} = {va - off}.", [va, off, va + off])


@T(C, "Operating systems")
def _(r):
    n = r.randint(2, 16)
    return Q(f"A parent process calls fork() {n} times in sequence, and every child continues the same code. How many processes exist at the end?", 2 ** n, f"Each fork doubles the count: 2^{n} = {2 ** n}.", [n + 1, 2 * n, 2 ** n - 1])


hand(C, "Operating systems", [
    ("Which is NOT a deadlock condition?", "Preemption of resources", "Mutual exclusion", "Hold and wait", "Circular wait", "The condition is no preemption."),
    ("Banker's algorithm is used for", "Deadlock avoidance", "Disk scheduling", "Page replacement", "Compilation", "It checks safe states."),
    ("Which needs a dirty bit?", "Writing changed pages back to disk", "Reading the BIOS", "Sorting files", "Opening a browser", "Clean pages can be dropped."),
    ("A TLB is", "A cache of page table entries", "A disk type", "A scheduler", "A file format", "It speeds up translation."),
    ("Internal fragmentation is", "Wasted space inside an allocated block", "Free space between blocks", "A broken disk", "Too many users", "Fixed-size blocks cause it."),
    ("External fragmentation is", "Free memory split into unusable gaps", "Waste inside blocks", "A full disk only", "A network fault", "Compaction or paging helps."),
    ("A race condition happens when", "The result depends on thread timing", "One thread runs alone", "A loop ends", "A file closes", "Shared data without coordination."),
    ("Which call creates a process on Unix?", "fork", "open", "read", "kill", "exec then loads a program."),
    ("An orphan process is", "One whose parent has exited", "One with no memory", "A paused thread", "A kernel module", "init adopts it."),
    ("A system call", "Requests a service from the kernel", "Calls a phone", "Restarts the system", "Compiles a program", "It crosses into kernel mode."),
    ("Which is a preemptive schedule?", "Round Robin", "First-come, first-served", "Non-preemptive SJF", "A batch queue", "The timer interrupts a task."),
    ("Belady's anomaly can occur in", "FIFO", "LRU", "Optimal", "None of these policies", "More frames can mean more faults."),
])


# ------------------------------------------------------------------- networks, computed
@T(C, "Computer networks")
def _(r):
    p = r.randint(8, 30)
    return Q(f"How many usable host addresses does a /{p} IPv4 network have?", 2 ** (32 - p) - 2, f"2^{32 - p} − 2 = {2 ** (32 - p) - 2}, excluding network and broadcast addresses.", [2 ** (32 - p), 2 ** (32 - p) - 1, 2 ** (31 - p)])


@T(C, "Computer networks")
def _(r):
    p = r.randint(8, 30)
    m = str(ipaddress.ip_network(f"0.0.0.0/{p}").netmask)
    return Q(f"What is the subnet mask for a /{p} network?", m, f"{p} ones followed by zeros is {m}.", [str(ipaddress.ip_network(f"0.0.0.0/{x}").netmask) for x in (p - 1, p + 1, p - 2) if 0 < x <= 32] + ["255.255.255.255"])


@T(C, "Computer networks")
def _(r):
    p = r.randint(16, 28)
    ip = ".".join(str(r.randint(1, 254)) for _ in range(4))
    net = ipaddress.ip_interface(f"{ip}/{p}").network
    return Q(f"What is the network address of {ip}/{p}?", str(net.network_address), f"Keep the first {p} bits and set the rest to 0.", [ip, str(net.broadcast_address), str(net.network_address + 1)])


@T(C, "Computer networks")
def _(r):
    size, rate = r.choice([10, 20, 50, 100, 200, 500, 1000]), r.choice([10, 20, 50, 100, 1000])
    ans = F(size * 8, rate)
    return Q(f"How many seconds does a {size} MB file take to send over a {rate} Mbps link, ignoring overheads?", ans, f"{size} MB = {size * 8} megabits. {size * 8} ÷ {rate} = {fmt(ans)}.", [F(size, rate), ans + 1, ans * 2])


@T(C, "Computer networks")
def _(r):
    first = r.randint(1, 223)
    if first == 127:
        first = 128
    cls = "A" if first < 127 else "B" if first < 192 else "C"
    return Q(f"Under classful addressing, which class does {first}.{r.randint(0, 255)}.{r.randint(0, 255)}.{r.randint(1, 254)} belong to?", cls, "A: 1 to 126, B: 128 to 191, C: 192 to 223.", [x for x in "ABCD" if x != cls])


PORTS = {"HTTP": 80, "HTTPS": 443, "SSH": 22, "FTP": 21, "SMTP": 25, "DNS": 53, "MySQL": 3306, "PostgreSQL": 5432, "Redis": 6379, "Telnet": 23}


@T(C, "Computer networks")
def _(r):
    k = r.choice(list(PORTS))
    other = [v for n, v in PORTS.items() if n != k]
    r.shuffle(other)
    return Q(f"What is the default port for {k}?", PORTS[k], "A standard default port.", other)


hand(C, "Computer networks", [
    ("Which layer does HTTP belong to?", "Application", "Transport", "Network", "Data link", "Top of the stack."),
    ("Which layer does TCP belong to?", "Transport", "Application", "Network", "Physical", "End-to-end delivery."),
    ("Which layer does IP belong to?", "Network", "Transport", "Session", "Application", "Routing between networks."),
    ("ARP maps", "IP addresses to MAC addresses", "Names to IPs", "Ports to processes", "Files to disks", "On a local network."),
    ("NAT lets", "Many private hosts share a public IP", "Disks share files", "A CPU run faster", "Browsers run offline", "Translation at the router."),
    ("What does a CDN do?", "Serves content from locations near users", "Creates domain names", "Encrypts disks", "Assigns IP addresses", "It lowers latency."),
    ("A load balancer", "Spreads traffic across servers", "Stores files", "Compiles code", "Assigns MAC addresses", "It improves availability."),
    ("WebSocket gives", "A two-way persistent connection", "One-way email", "A file system", "A DNS record", "Full duplex over one connection."),
    ("HTTP is", "Stateless", "Always encrypted", "A routing protocol", "A database", "Each request stands alone."),
    ("HTTP status 301 means", "Moved permanently", "Not found", "Forbidden", "OK", "3xx is a redirect."),
    ("HTTP status 401 means", "Unauthenticated", "Moved", "Created", "Server error", "Credentials are needed."),
    ("HTTP status 403 means", "Forbidden", "Not found", "Bad gateway", "OK", "Known user, not allowed."),
    ("Which DNS record maps a name to an IPv4 address?", "A", "MX", "CNAME", "TXT", "MX is for mail."),
    ("MAC addresses are how long?", "48 bits", "32 bits", "128 bits", "16 bits", "Six bytes."),
])
