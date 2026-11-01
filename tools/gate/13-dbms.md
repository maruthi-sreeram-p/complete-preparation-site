@part gate-dbms | Databases | systems
## The ER model and the relational model

### ER modelling

An **entity** is a thing with independent existence; an **entity set** groups similar entities. **Attributes** describe them and can be *simple*, *composite*, *multivalued* or *derived*. A **relationship** associates entities, with **cardinality** one-to-one (1:1), one-to-many (1:N) or many-to-many (M:N), and **participation** that is *total* (every entity must take part) or *partial*. A **weak entity** has no key of its own: it is identified by the key of its **owner** together with its own **partial key**.

### Mapping an ER diagram to tables

| ER element | Relational result |
|---|---|
| Strong entity set | one table with its attributes; key becomes the primary key |
| Weak entity set | one table; primary key = owner's key + partial key |
| Multivalued attribute | a separate table (entity key + the value) |
| **M:N relationship** | **a separate table** holding both keys and the relationship's attributes |
| **1:N relationship** | add the "1" side's key as a **foreign key** on the "N" side (no extra table) |
| 1:1 relationship | foreign key on either side (preferably the side with total participation) |

So two entity sets joined by an M:N relationship give **3 tables**, and joined by a 1:N relationship give **2 tables**.

### Keys

- A **superkey** is a set of attributes that determines all attributes. A **candidate key** is a minimal superkey. The **primary key** is the chosen candidate key. A **foreign key** references the primary key of another table.
- If a relation with n attributes has exactly one candidate key of size k, it has **2^(n−k)** superkeys (any superset of the key). For R(A,B,C,D) with key A there are 2³ = 8.
- With several candidate keys, count the supersets of each and subtract overlaps: R(A,B,C,D,E) with keys {A} and {B,C} has 2⁴ + 2² = 20 superkeys.

### Integrity constraints

**Entity integrity** (no NULL in a primary key), **referential integrity** (a foreign key value must match an existing primary key, or be NULL), **domain** and **key** constraints. Referential actions on delete or update: `CASCADE` (propagate to the referencing rows), `SET NULL`, `SET DEFAULT`, `RESTRICT` / `NO ACTION`.

!cheat ER and key cheat codes ::
- **Count tables:** each strong entity = 1 table, each M:N relationship = 1 table, and 1:N or 1:1 relationships add none.
- **Weak entity key:** owner key + partial key.
- **Superkeys with one candidate key:** 2^(n − |key|).
- **A foreign key may be NULL** unless it is declared NOT NULL.
!end

## Relational algebra and calculus

| Operator | Symbol | Meaning |
|---|---|---|
| Selection | σ_condition(R) | rows satisfying the condition |
| Projection | π_attributes(R) | chosen columns, **duplicates removed** |
| Union, intersection, difference | ∪, ∩, − | need union-compatible relations |
| Cartesian product | R × S | every pair of rows |
| Natural join | R ⋈ S | rows that agree on common attributes, common columns shown once |
| Theta join | R ⋈_θ S | σ_θ(R × S) |
| Outer joins | ⟕, ⟖, ⟗ | keep unmatched rows of the left, right or both sides, padded with NULL |
| Division | R ÷ S | values in R's other attributes paired with **every** row of S |
| Rename | ρ | |

**Size facts:** |R × S| = |R|·|S|, with the attributes of both. |R ∪ S| lies between max(|R|, |S|) and |R| + |S|. If a foreign key of R references the primary key of S and has no NULLs, then |R ⋈ S| = |R|. For R with unique join values {1, 2, 3} and S with {2, 3, 4}: the natural join has 2 rows, left outer 3, full outer 4.

**Division** answers "for all" queries. With R(student, course) = {(s1,c1), (s1,c2), (s2,c1), (s3,c1), (s3,c2), (s3,c3)} and S = {c1, c2}, R ÷ S = {s1, s3}, the students who took *all* the courses of S.

**Equivalences:** σ_{p∧q}(R) = σ_p(σ_q(R)). π_A(R ∪ S) = π_A(R) ∪ π_A(S). But π_A(R ∩ S) ⊆ π_A(R) ∩ π_A(S), **not equal** in general.

### Tuple and domain calculus

Tuple relational calculus (TRC) writes queries as {t | P(t)}, where P is a first-order formula over tuple variables. For example {t | Student(t) ∧ t.age > 20} is σ_{age>20}(Student). An expression is **safe** if it returns a finite relation; {t | ¬Student(t)} is **unsafe**. Safe TRC, safe DRC and relational algebra have the same expressive power.

!cheat Relational-algebra cheat codes ::
- **"For all" = division,** or double negation: "no course exists that the student did not take".
- **Projection removes duplicates,** so |π(R)| ≤ |R|.
- **Join sizes:** FK → PK join has exactly the size of the FK relation; a join with no common attributes is a Cartesian product.
- **π does not distribute over ∩ or −.**
- **Count attributes and tuples separately:** |R × S| rows and attributes(R) + attributes(S) columns.
!end

## SQL

```sql Sample data used in the examples
CREATE TABLE Emp(eid INT, name TEXT, dept TEXT, salary INT);
-- (1,'Asha','CS',50) (2,'Ben','CS',60) (3,'Chitra','EE',55)
-- (4,'Dev','EE',NULL) (5,'Esha','ME',70) (6,'Farid','CS',60)
CREATE TABLE Dept(did INT, dname TEXT);
-- (1,'CS') (2,'EE') (3,'ME') (4,'CE')
```

### Core syntax

`SELECT [DISTINCT] columns FROM tables [WHERE condition] [GROUP BY cols [HAVING condition]] [ORDER BY cols]`. WHERE filters rows **before** grouping; HAVING filters **groups** after aggregation. Aggregates are COUNT, SUM, AVG, MIN and MAX. Set operators UNION, INTERSECT and EXCEPT remove duplicates (UNION ALL keeps them).

### NULL: three-valued logic

Any comparison with NULL is **unknown**, and WHERE keeps only rows where the condition is **true**.

| Query on the sample data | Result | Why |
|---|---|---|
| `COUNT(*)` / `COUNT(salary)` | 6 / 5 | COUNT(column) skips NULL |
| `AVG(salary)` | 59 | the NULL is ignored (295 / 5), not treated as 0 |
| `COUNT(DISTINCT salary)` | 4 | 50, 55, 60, 70 |
| `WHERE salary > 55 OR salary <= 55` | 5 rows | the NULL row satisfies neither |
| `WHERE salary NOT IN (SELECT salary FROM Emp WHERE dept='EE')` | **0 rows** | the subquery returns {55, NULL}, and x NOT IN (…, NULL) is never true |
| `MAX(salary) WHERE salary < (SELECT MAX(salary) FROM Emp)` | 60 | second highest |
| departments with `HAVING COUNT(*) > 1` | CS and EE (2 rows) | |
| `MAX(c)` over `SELECT COUNT(*) c … GROUP BY dept` | 3 | CS has 3 employees |
| employees earning more than their department's average (correlated) | 2 | Ben and Farid in CS (average 56.67) |
| `Dept LEFT JOIN Emp ON dept = dname` | 7 rows | CS 3 + EE 2 + ME 1 + CE with NULLs |
| `SELECT dept FROM Emp UNION SELECT dname FROM Dept` | 4 rows | CS, EE, ME, CE |

!warning NOT IN and NULL :: `x NOT IN (subquery)` returns no rows at all if the subquery produces a NULL. Use `NOT EXISTS` or filter the NULLs out of the subquery.

### Other SQL features

- **Joins:** INNER, LEFT / RIGHT / FULL OUTER, CROSS (Cartesian product), NATURAL.
- **Subqueries:** `IN`, `EXISTS`, `ANY`, `ALL`; a *correlated* subquery refers to the outer query and is evaluated per row.
- **Views** are stored queries. **Constraints:** PRIMARY KEY, UNIQUE, FOREIGN KEY, CHECK, NOT NULL. **Triggers** run on INSERT, UPDATE or DELETE.

!cheat SQL cheat codes ::
- **Evaluate in this order:** FROM / JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.
- **NULL checklist:** NULL = NULL is unknown; use IS NULL; COUNT(*) counts rows, COUNT(col) counts non-NULLs; aggregates skip NULLs.
- **Counting join rows:** list the matches per group of keys and multiply.
- **UNION removes duplicates,** UNION ALL does not.
- **Second-highest:** `SELECT MAX(x) FROM T WHERE x < (SELECT MAX(x) FROM T)`.
!end

## Functional dependencies and normal forms

A **functional dependency** X → Y says that two rows agreeing on X must agree on Y. The **closure** X⁺ is the set of attributes determined by X. X is a **superkey** when X⁺ contains all attributes, and a **candidate key** when it is also minimal.

**Armstrong's axioms:** reflexivity (if Y ⊆ X then X → Y), augmentation (X → Y gives XZ → YZ) and transitivity. **Union**, **decomposition** and **pseudotransitivity** follow from them. They are sound and complete.

### Finding candidate keys

Attributes that never appear on a right-hand side must be in every key. Attributes that appear only on right-hand sides are in no key. Compute the closure of the forced attributes and add more if the closure is short. Example: R(A,B,C,D,E) with A → B, BC → D, D → E. A and C never appear on a right side, and (AC)⁺ = ABCDE, so **AC is the only key**. For R(A,B,C,D) with AB → C, C → D, D → A, the keys are **AB, BC and BD**.

### Normal forms

| Form | Condition (for every non-trivial FD X → A) |
|---|---|
| 1NF | attributes are atomic |
| **2NF** | no non-prime attribute depends on a **proper part** of a candidate key |
| **3NF** | X is a superkey, **or** A is a prime attribute |
| **BCNF** | X is a superkey |
| 4NF | for every non-trivial multivalued dependency X →→ Y, X is a superkey |

BCNF ⊂ 3NF ⊂ 2NF ⊂ 1NF. Examples:

- R(A,B,C) with AB → C and C → B: keys AB and AC, so every attribute is prime. It is in 3NF, but C → B has a non-superkey left side, so it is **not BCNF**.
- R(A,B,C,D) with A → B, B → C, C → D: key A. B → C is a transitive dependency, so it is in **2NF** but not 3NF.
- R(A,B,C,D) with AB → CD and B → C: key AB. B → C is a partial dependency, so only **1NF**.
- Course–teacher–book with independent multivalued dependencies course →→ teacher and course →→ book is in BCNF but not **4NF**.

### Decomposition

- **Lossless join:** a decomposition into R₁ and R₂ is lossless if (R₁ ∩ R₂) → R₁ or (R₁ ∩ R₂) → R₂. For larger decompositions use the chase (tableau) algorithm. R(A,B,C) with A → B splits losslessly into {AB, AC} but not into {AB, BC}.
- **Dependency preserving:** every FD can be derived from the FDs that fit inside a single fragment. R(A,B,C) with AB → C, C → B decomposes into {AC, BC} losslessly (C determines B), but AB → C is lost.
- **Every relation has a lossless, dependency-preserving 3NF decomposition. BCNF decompositions are always lossless but may lose dependencies.**

### Minimal (canonical) cover

Split right-hand sides to single attributes, remove extraneous left-side attributes, remove redundant FDs. For {A → BC, B → C, A → B, AB → C} the minimal cover is **{A → B, B → C}**. Two FD sets are **equivalent** if each is implied by the other, such as {A → B, B → C} and {A → B, B → C, A → C}.

!cheat Normalisation cheat codes ::
- **Keys first:** always find all candidate keys before judging a normal form. Prime = in some candidate key.
- **Quick tests:** 3NF fails when a non-prime attribute depends on a non-superkey; BCNF fails when *any* attribute depends on a non-superkey.
- **If every attribute is prime, the relation is in 3NF.**
- **Lossless binary test:** the common attributes must be a key of one of the parts.
- **A cyclic set** A → B → C → D → A makes each attribute a key (4 candidate keys).
- **Union is not an axiom,** it is derived.
!end

## Transactions and concurrency control

### ACID

**A**tomicity (all or nothing), **C**onsistency (valid state to valid state), **I**solation (concurrent transactions behave as if serial), **D**urability (committed results survive failures).

### Schedules and serializability

A **schedule** interleaves the operations of several transactions. Two operations **conflict** if they belong to different transactions, access the same item and at least one is a write. A schedule is **conflict serializable** if its **precedence graph** (an edge Tᵢ → Tⱼ whenever an operation of Tᵢ conflicts with and precedes one of Tⱼ) has **no cycle**. Any topological order of that graph gives an equivalent serial schedule.

- r1(x) r2(x) w1(x) w2(x): T2 → T1 (r2 before w1) and T1 → T2 (r1 before w2) form a cycle, so it is not conflict serializable.
- r1(x) r2(y) w2(y) w1(x) r2(x): the only edge is T1 → T2, so it is conflict serializable.
- Two transactions with 3 and 2 operations can be interleaved in C(5, 2) = 10 ways.

### Recoverability

| Class | Condition |
|---|---|
| Recoverable | a transaction commits only after every transaction whose data it read has committed |
| Cascadeless (ACA) | transactions read only committed data |
| Strict | no read or write of an item until the last writer commits or aborts |

Strict ⊂ cascadeless ⊂ recoverable. The schedule w1(x) r2(x) c2 c1 is **not recoverable**: T2 read uncommitted data and committed first.

### Concurrency-control protocols

- **Two-phase locking (2PL):** a growing phase (acquire locks) then a shrinking phase (release). Guarantees conflict serializability but **can deadlock**. **Strict 2PL** holds all exclusive locks until commit, which also gives strict (cascadeless) schedules.
- **Timestamp ordering:** each transaction T gets a timestamp TS(T). T's write(X) is rejected (T rolled back) if RTS(X) > TS(T) or WTS(X) > TS(T). With TS(T) = 5, RTS(X) = 7 the write is rejected.
- **Deadlock prevention:** *wait-die* (an older transaction requesting a lock held by a younger one **waits**; a younger one requesting from an older one dies) and *wound-wait* (older preempts the younger).
- **Isolation levels:** READ UNCOMMITTED (allows dirty reads), READ COMMITTED, REPEATABLE READ (phantoms still possible), SERIALIZABLE.
- **Recovery:** *write-ahead logging* requires log records on stable storage before the corresponding data pages. Undo for uncommitted transactions, redo for committed ones, with checkpoints to bound the work.

!cheat Transaction cheat codes ::
- **Precedence graph recipe:** list every pair of conflicting operations in schedule order, add an edge from the earlier to the later transaction, then look for a cycle.
- **Same item, different transactions, at least one write** = conflict. Read–read never conflicts.
- **Strict 2PL ⇒ conflict serializable and strict. Basic 2PL ⇒ conflict serializable only.**
- **Wait-die:** old waits, young dies.
- **Dirty read** needs READ UNCOMMITTED.
!end

## File organisation and indexing

### Blocks and records

With block size B and record size R, the **blocking factor** is bf = ⌊B/R⌋ and a file of r records needs ⌈r / bf⌉ blocks. For B = 1024, R = 100 and r = 10 000: bf = 10, so 1000 blocks.

| Access | Block accesses |
|---|---|
| Heap file, linear search | b / 2 on average, b worst case |
| Sorted file, binary search on blocks | ⌈log₂ b⌉ |
| Hashed file (no overflow) | about 1 |

### Single-level indexes

- A **dense index** has an entry for every record; a **sparse index** has one for every block and needs the data file to be **sorted** on the indexed field. A **primary index** is on the ordering key field, a **clustering index** on an ordering non-key field, and a **secondary index** on a non-ordering field (it must be dense).
- Index size: entries × (key + pointer) bytes, so index blocks = ⌈entries / index bf⌉. With 1000 data blocks and index bf = 64, a sparse index has 1000 entries in ⌈1000/64⌉ = 16 blocks. A search costs ⌈log₂ 16⌉ + 1 (data block) = 5 accesses. A dense secondary index on 10 000 records needs ⌈10 000/64⌉ = 157 blocks.

### B-trees and B+ trees

In a **B+ tree of order p** each internal node has at most **p child pointers and p − 1 keys**, and at least ⌈p/2⌉ children (the root at least 2). The keys and record pointers are in the **leaves**, which are linked for range scans. In a **B-tree** keys (with record pointers) also appear in internal nodes.

- **Choosing the order from the block size:** p·(pointer size) + (p − 1)·(key size) ≤ B. With B = 1024, key 8 bytes, pointer 4 bytes: 12p ≤ 1032, so **p = 86**.
- **Capacity:** with order 100 and leaves holding 99 keys, three levels hold up to 100² · 99 = **990 000** keys.
- **Search cost** = height + 1 block accesses (one per level, plus the data block).
- **B-tree of order m** (max m children): a non-root node has at least ⌈m/2⌉ children, so at least ⌈m/2⌉ − 1 keys: for m = 5 that is 2 keys, and the maximum is 4.
- Insertion into a full node **splits** it and pushes a key up. Deletion may borrow from a sibling or merge.

### Hashing

**Static hashing** maps a key to one of M buckets, with overflow chains when a bucket fills. For 1000 records, bucket capacity 10 and an 80% load, M = 1000 / (10 × 0.8) = 125 buckets. **Extendible hashing** uses a directory of 2^d entries (d = global depth) that doubles when a bucket with local depth equal to the global depth splits. **Linear hashing** splits buckets in order without a directory.

!cheat Indexing cheat codes ::
- **Compute bf and block counts first,** then index sizes.
- **Binary search needs ⌈log₂ b⌉ block reads;** a sparse index search adds one data-block read.
- **B+ tree order from block size:** solve p·P + (p − 1)·K ≤ B for the largest integer p.
- **Records in a full B+ tree** = (internal fan-out)^(levels − 1) × (keys per leaf).
- **Dense is needed when the file is not sorted** on the indexed field.
- **Extendible hashing:** a directory of global depth d has 2^d entries.
!end

## Cheat sheet: Databases on one page

| Topic | Fact |
|---|---|
| Tables from ER | M:N = own table; 1:N = foreign key on the N side |
| Superkeys, one key of size k | 2^(n − k) |
| Division | "for all" queries |
| Join sizes | FK → PK: \|R\|; no common attributes: \|R\|·\|S\| |
| NULL | COUNT(col) and AVG skip it; NOT IN with NULL gives nothing |
| WHERE / HAVING | rows / groups |
| 3NF | X superkey or A prime |
| BCNF | X superkey |
| Lossless binary split | common attributes form a key of one part |
| 3NF | always lossless and dependency preserving |
| BCNF | lossless, maybe not dependency preserving |
| Conflict serializable | precedence graph has no cycle |
| Strict 2PL | conflict serializable and strict |
| Timestamp rule | reject write if RTS or WTS exceeds TS(T) |
| Blocking factor | ⌊B/R⌋ |
| B+ tree order | p·P + (p − 1)·K ≤ B |
| Search in a B+ tree | height + 1 |

??  Why does `SELECT COUNT(*) FROM T WHERE x NOT IN (SELECT x FROM U)` return 0 when U.x contains a NULL?
=> For a value v, v NOT IN (…, NULL) is (v ≠ a) AND … AND (v ≠ NULL). The last comparison is unknown, so the whole condition is never true, and WHERE discards every row. Use NOT EXISTS or remove the NULLs.
??  Is every BCNF decomposition dependency preserving? Give an example where it is not.
=> No. For R(A,B,C) with AB → C and C → B, the BCNF decomposition {AC, BC} is lossless, but AB → C cannot be checked inside either fragment, so it is lost.
??  How do you decide whether a schedule is conflict serializable?
=> Build the precedence graph with a node per transaction and an edge Ti → Tj for each pair of conflicting operations where Ti's comes first. The schedule is conflict serializable if and only if the graph has no cycle, and a topological order gives an equivalent serial schedule.
??  What is the difference between a dense and a sparse index?
=> A dense index has an entry for every record (so works on unsorted files, needed for secondary indexes). A sparse index has one entry per block, is much smaller, and requires the file to be sorted on the indexed field.
