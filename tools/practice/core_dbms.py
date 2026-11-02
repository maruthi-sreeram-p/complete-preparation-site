"""Extra DBMS theory questions for the Databases subject. Keys, schedules and index sizes are computed here."""
import itertools

from common import written

# ---- functional dependencies: R(A,B,C,D,E) with A->B, BC->D, D->E, E->B  (attributes as letters)
ATTRS = "ABCDE"
FDS = [("A", "B"), ("BC", "D"), ("D", "E"), ("E", "B")]


def closure(attrs, fds=FDS):
    result = set(attrs)
    changed = True
    while changed:
        changed = False
        for left, right in fds:
            if set(left) <= result and not set(right) <= result:
                result |= set(right)
                changed = True
    return result


def candidate_keys(attrs=ATTRS, fds=FDS):
    keys = []
    for size in range(1, len(attrs) + 1):
        for combo in itertools.combinations(attrs, size):
            if closure(combo, fds) == set(attrs) and not any(set(k) <= set(combo) for k in keys):
                keys.append("".join(combo))
    return keys


KEYS = candidate_keys()
assert KEYS == ["AC"], KEYS
CLOSURE_A = "".join(sorted(closure("A")))
CLOSURE_BC = "".join(sorted(closure("BC")))
assert (CLOSURE_A, CLOSURE_BC) == ("AB", "BCDE")


# ---- conflict serializability: a schedule is a list of (transaction, operation, item)
def precedence_edges(schedule):
    edges = set()
    for i, (t1, op1, x1) in enumerate(schedule):
        for t2, op2, x2 in schedule[i + 1:]:
            if t1 != t2 and x1 == x2 and "W" in (op1, op2):
                edges.add((t1, t2))
    return edges


def has_cycle(edges):
    nodes = {n for e in edges for n in e}
    for start in nodes:
        stack, seen = [start], set()
        while stack:
            n = stack.pop()
            for a, b in edges:
                if a == n:
                    if b == start:
                        return True
                    if b not in seen:
                        seen.add(b)
                        stack.append(b)
    return False


S1 = [(1, "R", "A"), (1, "W", "A"), (2, "R", "A"), (2, "W", "A"), (1, "R", "B"), (1, "W", "B"), (2, "R", "B"), (2, "W", "B")]
S2 = [(1, "R", "A"), (2, "R", "A"), (1, "W", "A"), (2, "W", "A")]
assert not has_cycle(precedence_edges(S1)) and has_cycle(precedence_edges(S2))
assert precedence_edges(S1) == {(1, 2)} and precedence_edges(S2) == {(1, 2), (2, 1)}

# ---- B+ tree: 4096-byte blocks, 8-byte keys, 8-byte pointers, 100 million records
BLOCK, KEY, PTR, RECORDS = 4096, 8, 8, 100_000_000
FANOUT = max(n for n in range(2, 1000) if n * PTR + (n - 1) * KEY <= BLOCK)
LEAF = (BLOCK - PTR) // (KEY + PTR)  # entries per leaf; one pointer to the next leaf
assert (FANOUT, LEAF) == (256, 255)
leaves = -(-RECORDS // LEAF)
LEVEL_SIZES, nodes = [leaves], leaves  # number of nodes on each level, from the leaves up to the root
while nodes > 1:
    nodes = -(-nodes // FANOUT)
    LEVEL_SIZES.append(nodes)
height = len(LEVEL_SIZES)
assert LEVEL_SIZES == [392157, 1532, 6, 1] and height == 4, LEVEL_SIZES

QUESTIONS = [
    written("db-theory-keys", "Candidate keys from functional dependencies", "Hard",
        f"R(A, B, C, D, E) has the functional dependencies A → B, BC → D, D → E and E → B. Find the closure of A, the closure of BC and all candidate keys.",
        f"- **A⁺** = {{{', '.join(CLOSURE_A)}}} (A → B, and nothing else starts from A or B alone).\n"
        f"- **(BC)⁺** = {{{', '.join(CLOSURE_BC)}}} (BC → D, D → E).\n"
        f"- Attributes that appear on no right-hand side must be in every key: **A** and **C** (nothing determines them). **(AC)⁺** = A, C, B (from A), D (from BC), E (from D) = all attributes, so the only candidate key is **{KEYS[0]}**.\n\n"
        "To find keys: start from the attributes that are never on a right-hand side, compute the closure, and add attributes only if the closure is still incomplete. A relation is in **3NF** if every dependency's left side is a superkey or its right side is part of a candidate key; here BC → D violates it (BC is not a superkey and D is not prime), so R is not even in 3NF.",
        hint="Which attributes never appear on a right-hand side?"),
    written("db-theory-bcnf", "BCNF and 3NF", "Hard",
        "What is the difference between 3NF and BCNF? Why is BCNF decomposition not always dependency-preserving?",
        "A relation is in **BCNF** if for every non-trivial dependency X → Y, **X is a superkey**. **3NF** relaxes this: X → Y is also allowed if **Y is part of some candidate key** (a prime attribute). Every BCNF relation is in 3NF, not vice versa.\n\n"
        "Decomposing into BCNF always gives a **lossless join** but cannot always preserve every functional dependency (the classic example is R(Street, City, Zip) with {Street, City} → Zip and Zip → City: decomposing on Zip → City loses the ability to enforce the first dependency within one table). 3NF decomposition can always be both lossless and dependency-preserving, which is why 3NF is the practical target and BCNF is applied when no dependency is lost."),
    written("db-theory-serializability", "Conflict serializability", "Hard",
        "Are the schedules S1 = R1(A) W1(A) R2(A) W2(A) R1(B) W1(B) R2(B) W2(B) and S2 = R1(A) R2(A) W1(A) W2(A) conflict serializable? Show how you decide.",
        "Build the **precedence graph**: add an edge Ti → Tj when an operation of Ti conflicts with a **later** operation of Tj (same item, different transactions, at least one write). A schedule is conflict serializable **iff the graph has no cycle**; a topological order gives an equivalent serial schedule.\n\n"
        f"- **S1:** every conflict goes from T1 to T2 (R1(A) before W2(A), W1(A) before R2(A) and W2(A), and the same for B): edges {sorted(precedence_edges(S1))}, **no cycle**, so it is serializable and equivalent to T1 then T2.\n"
        f"- **S2:** R2(A) precedes W1(A) (T2 → T1) and R1(A) precedes W2(A) (T1 → T2): edges {sorted(precedence_edges(S2))} form a **cycle**, so it is **not** conflict serializable (it is the classic lost-update pattern).\n\n"
        "**Two-phase locking** guarantees conflict-serializable schedules: a transaction acquires all its locks before releasing any."),
    written("db-theory-bplus", "B+ tree height", "Hard",
        f"A B+ tree index has {BLOCK}-byte blocks, {KEY}-byte keys and {PTR}-byte pointers. How many keys fit in an internal node, and how many levels does the tree need for {RECORDS:,} records? Why are B+ trees used instead of binary trees on disk?",
        f"An internal node with n pointers has n − 1 keys: n × {PTR} + (n − 1) × {KEY} ≤ {BLOCK} gives a **fan-out of {FANOUT}**. A leaf holds about ({BLOCK} − {PTR}) / ({KEY} + {PTR}) = **{LEAF}** entries. {RECORDS:,} records need ⌈{RECORDS:,} / {LEAF}⌉ = {leaves:,} leaves; each level above divides by {FANOUT}: {' → '.join(f'{n:,}' for n in LEVEL_SIZES)} nodes per level, so the tree has **{height} levels**: a lookup reads about {height} blocks even for 100 million rows.\n\n"
        "B+ trees are wide and shallow because **each node is one disk block**, minimising disk reads (a binary tree on 100 million keys would need about 27 levels). All data pointers are in the **linked leaves**, so range scans and `ORDER BY` just follow the leaf chain, and internal nodes hold only keys, giving a higher fan-out than a plain B-tree."),
    written("db-theory-joins-algos", "Join algorithms", "Hard",
        "Describe nested loop, hash and sort-merge joins. When does the optimiser choose each?",
        "- **Nested loop:** for each row of the outer table, look for matches in the inner table. O(n·m) without an index; with an **index on the inner join column** each probe is O(log m), the best choice when the outer side is small.\n"
        "- **Hash join:** build an in-memory **hash table** on the smaller input and probe it with each row of the larger. About O(n + m); best for large, unsorted inputs with an **equality** condition and enough memory (it spills to disk otherwise).\n"
        "- **Sort-merge join:** sort both inputs on the join key (or read them sorted from an index) and merge in one pass. Good when the inputs are **already sorted** or the result must be ordered, and it handles range conditions.\n\n"
        "The optimiser estimates the cost of each from **table statistics** (row counts, value distributions); stale statistics are a common cause of a bad plan. `EXPLAIN` shows the choice."),
    written("db-theory-wal", "Write-ahead logging and recovery", "Hard",
        "How does a database guarantee durability and atomicity after a crash? Explain write-ahead logging.",
        "**Write-ahead logging (WAL):** before a changed data page may be written to disk, the log record describing the change must be **flushed to the log on disk**, and a transaction is committed only after its commit record is in the durable log. Data pages themselves can be written lazily, because the log is sequential and cheap to force.\n\n"
        "After a crash, **recovery** reads the log: **redo** the changes of committed transactions that never reached the data files (durability) and **undo** the changes of uncommitted transactions that did (atomicity). **Checkpoints** record a point from which recovery can start, so the log does not need to be replayed from the beginning. This is the ARIES approach used by most relational databases; PostgreSQL's WAL also feeds replication and point-in-time recovery."),
    written("db-theory-view-mv", "View, materialized view, trigger, stored procedure", "Medium",
        "Differentiate a view, a materialized view, a trigger and a stored procedure.",
        "- **View:** a **saved query** presented as a virtual table; no data stored, it runs each time. It simplifies queries and restricts access to columns.\n"
        "- **Materialized view:** the query result is **stored** and refreshed on demand or on a schedule: fast reads for expensive aggregations, but possibly stale.\n"
        "- **Trigger:** code that runs **automatically** on an `INSERT`, `UPDATE` or `DELETE` (audit logs, derived columns, enforcing a rule). Hidden side effects make triggers hard to debug and test.\n"
        "- **Stored procedure:** named, reusable code stored in the database that you **call explicitly** with parameters, running close to the data (fewer round trips) but harder to version, test and port than application code."),
]
