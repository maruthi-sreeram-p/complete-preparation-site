@part gate-discrete-maths | Discrete Mathematics | math
## Propositional logic

A **proposition** is a statement that is either true or false. Compound propositions are built with connectives, and almost every GATE question in this area reduces to one fact: a formula is just a function from truth assignments to {T, F}, so any claim can be checked on a small truth table.

| Connective | Symbol | True when |
|---|---|---|
| NOT | ¬p | p is false |
| AND | p ∧ q | both true |
| OR | p ∨ q | at least one true |
| XOR | p ⊕ q | exactly one true (the truth values differ) |
| Implication | p → q | **false only when p is true and q is false** |
| Biconditional | p ↔ q | both have the same truth value |
| NAND / NOR | p ↑ q, p ↓ q | ¬(p ∧ q), ¬(p ∨ q) |

### Equivalences you must know cold

| Law | Statement |
|---|---|
| Implication | p → q ≡ ¬p ∨ q ≡ ¬q → ¬p (contrapositive) |
| Not the converse | p → q is **not** equivalent to q → p (converse) or ¬p → ¬q (inverse) |
| Negation of implication | ¬(p → q) ≡ p ∧ ¬q |
| De Morgan | ¬(p ∧ q) ≡ ¬p ∨ ¬q, ¬(p ∨ q) ≡ ¬p ∧ ¬q |
| Biconditional | p ↔ q ≡ (p → q) ∧ (q → p) ≡ ¬(p ⊕ q) |
| Exportation | p → (q → r) ≡ (p ∧ q) → r |
| Distribution | p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r), and the dual |
| Absorption | p ∨ (p ∧ q) ≡ p, p ∧ (p ∨ q) ≡ p |

A formula is a **tautology** if it is true under every assignment, a **contradiction** if false under every assignment, and **satisfiable** if true under at least one. A formula is a tautology exactly when its negation is unsatisfiable.

!cheat Logic cheat codes ::
- **Counting Boolean functions:** n variables give 2ⁿ rows, so 2^(2ⁿ) different functions. For n = 2 that is 16, for n = 3 it is 256.
- **Implication is false in exactly one row** (T → F). To make p → q false, set p = T and q = F. This one fact solves most "find the truth value" puzzles.
- **To test an implication tautology, try to falsify it:** assume the conclusion is false and the premise true, then see if the assignment is consistent. If you cannot, it is a tautology.
- **Functionally complete sets:** {¬, ∧}, {¬, ∨}, {¬, →}, {NAND} alone and {NOR} alone. A set is **not** complete if every function in it keeps T → T (like ∧, ∨, →) or is linear (like ⊕, ↔).
- **CNF and DNF:** a CNF clause is false in exactly one row of its variables; a minterm of a DNF is true in exactly one row. Counting rows is usually faster than algebra.
!end

!warning Common traps :: (1) "p only if q" means p → q, not q → p. (2) "p unless q" is ¬q → p. (3) A vacuous implication (false premise) is **true**. (4) ¬(p → q) is not p → ¬q.

## First-order logic

First-order logic adds variables, predicates and the quantifiers ∀ (for all) and ∃ (there exists) over a domain.

### Translating English

| English | Logic |
|---|---|
| Every student passes | ∀x (Student(x) → Passes(x)) |
| Some student passes | ∃x (Student(x) ∧ Passes(x)) |
| No student passes | ∀x (Student(x) → ¬Passes(x)) ≡ ¬∃x (Student(x) ∧ Passes(x)) |
| Not every student passes | ∃x (Student(x) ∧ ¬Passes(x)) |

The rule that prevents most mistakes: **∀ goes with →, ∃ goes with ∧.** ∀x (S(x) ∧ P(x)) says everything is a student, and ∃x (S(x) → P(x)) is trivially true whenever some x is not a student.

### Negation and order of quantifiers

- ¬∀x P(x) ≡ ∃x ¬P(x), and ¬∃x P(x) ≡ ∀x ¬P(x). Push the negation inwards and flip each quantifier.
- ∀x ∀y and ∃x ∃y can be swapped freely. ∀x ∃y and ∃y ∀x **cannot**: ∃y ∀x P(x, y) is stronger and implies ∀x ∃y P(x, y), but not the other way round.
- ∀ distributes over ∧: ∀x (P ∧ Q) ≡ ∀x P ∧ ∀x Q. ∃ distributes over ∨: ∃x (P ∨ Q) ≡ ∃x P ∨ ∃x Q.
- The other directions fail: ∀x (P ∨ Q) does **not** imply ∀x P ∨ ∀x Q, and ∃x (P ∧ Q) implies, but is not implied by, ∃x P ∧ ∃x Q.

!cheat FOL cheat codes ::
- **"Every A is B"** → ∀x (A → B). **"Some A is B"** → ∃x (A ∧ B). Never swap the connectives.
- **Check an FOL claim on a 2-element domain.** If the claim fails there, it is not valid. A claim that is true on every tiny domain is usually valid.
- **For ∀x ∃y statements,** read it as "pick any x, then find a y". For ∃y ∀x, read it as "one y that works for every x".
- **Valid inferences:** modus ponens (p → q, p ⊢ q), modus tollens (p → q, ¬q ⊢ ¬p), hypothetical syllogism, disjunctive syllogism. **Invalid:** affirming the consequent (p → q, q ⊢ p) and denying the antecedent (p → q, ¬p ⊢ ¬q).
!end

## Sets, relations and functions

### Relations

A relation R on a set A is a subset of A × A. If |A| = n:

| Property | Condition | Count on n elements |
|---|---|---|
| All relations | any subset of A × A | 2^(n²) |
| Reflexive | (a, a) ∈ R for all a | 2^(n² − n) |
| Irreflexive | no (a, a) | 2^(n² − n) |
| Symmetric | (a, b) ∈ R ⇒ (b, a) ∈ R | 2^(n(n+1)/2) |
| Antisymmetric | (a, b), (b, a) ∈ R ⇒ a = b | 2ⁿ · 3^(n(n−1)/2) |
| Asymmetric | never both (a, b) and (b, a) | 3^(n(n−1)/2) |
| Reflexive and symmetric | | 2^(n(n−1)/2) |
| Equivalence relations | reflexive, symmetric, transitive | Bell number Bₙ |

Bell numbers: B₁ = 1, B₂ = 2, B₃ = 5, B₄ = 15, B₅ = 52, B₆ = 203. An equivalence relation is the same thing as a **partition** of the set, so the number of equivalence relations with exactly k classes is the Stirling number S(n, k).

A **partial order** is reflexive, antisymmetric and transitive. A **total order** is a partial order in which every two elements are comparable. A **preorder** is reflexive and transitive only.

!warning Transitive closure :: R ∪ R² ∪ … ∪ Rⁿ. If R = {(1,2), (2,3), (3,4)} the closure adds (1,3), (2,4) and (1,4), giving 6 pairs. Closing a relation can add the reflexive pairs only if you ask for the reflexive-transitive closure.

### Functions

For f : A → B with |A| = n and |B| = m:

| Type | Meaning | Count |
|---|---|---|
| All functions | | mⁿ |
| One-to-one (injective) | different inputs give different outputs | m(m−1)…(m−n+1) = P(m, n) |
| Onto (surjective) | every element of B is hit | Σₖ (−1)ᵏ C(m, k) (m−k)ⁿ |
| Bijective | both, needs n = m | n! |

Composition facts that GATE asks directly:

- If g ∘ f is injective, then **f** is injective. If g ∘ f is surjective, then **g** is surjective.
- The composition of injective functions is injective, and of surjective functions is surjective.
- A function has an inverse exactly when it is a bijection.

!cheat Relations and functions cheat codes ::
- **Onto count for small sizes:** onto functions from n to 2 elements = 2ⁿ − 2. From n to 3 = 3ⁿ − 3·2ⁿ + 3.
- **Equivalence classes of "a ≡ b (mod k)" on the integers:** exactly k classes.
- **|a − b| ≤ 1 on the integers** is reflexive and symmetric but **not transitive**, a favourite trap.
- **Check transitivity** by searching for a chain (a, b), (b, c) and confirming (a, c). One missing pair is enough to fail it.
- **Antisymmetric does not mean "not symmetric".** The identity relation is both.
!end

## Partial orders and lattices

A **poset** (P, ≤) is drawn as a **Hasse diagram**: only covering edges are shown, with larger elements higher. x **covers** y if y < x and nothing lies strictly between.

| Term | Meaning |
|---|---|
| Maximal element | nothing is strictly above it (there can be several) |
| Greatest element | above everything (at most one) |
| Upper bound, lub | element above a set, the least such bound |
| Lower bound, glb | element below a set, the greatest such bound |
| Chain | a subset that is totally ordered |
| Antichain | a subset in which no two elements are comparable |

A **lattice** is a poset in which every pair has both a lub (join, ∨) and a glb (meet, ∧). A lattice is **distributive** if ∧ and ∨ distribute over each other, **bounded** if it has a least (0) and greatest (1) element, and **complemented** if every element has a complement x′ with x ∧ x′ = 0 and x ∨ x′ = 1. A distributive complemented lattice is a **Boolean algebra**.

### The divisor lattice Dₙ

Under divisibility, a ∧ b = gcd and a ∨ b = lcm. Dₙ is always distributive. It is complemented, and so a Boolean algebra, **exactly when n is square-free** (no repeated prime factor). With k distinct primes it has 2ᵏ elements.

```text Hasse diagram of D12 (covering pairs)
12 covers 4 and 6
 4 covers 2
 6 covers 2 and 3
 2 and 3 cover 1
```

!cheat Poset and lattice cheat codes ::
- **Counting Hasse edges:** count covering pairs. In D12 there are 7: (1,2), (1,3), (2,4), (2,6), (3,6), (4,12), (6,12).
- **Boolean algebra sizes** are always powers of 2. A lattice with 6 elements is never a Boolean algebra.
- **Dilworth:** the minimum number of chains needed to cover a poset equals the size of the largest antichain. For {1,…,n} under divisibility the largest antichain has ⌈n/2⌉ elements.
- **Non-distributive lattices contain N5 (pentagon) or M3 (diamond).** If you see one, you can stop checking.
- **Complement in Dₙ:** x′ = n / x only when gcd(x, n / x) = 1.
- **Subsets of an n-set under ⊆:** a Boolean lattice with n! maximal chains, 2ⁿ elements, and the largest antichain of size C(n, ⌊n/2⌋).
!end

## Monoids and groups

| Structure | Required properties |
|---|---|
| Semigroup | closure, associativity |
| Monoid | semigroup + identity |
| Group | monoid + every element has an inverse |
| Abelian group | group + commutativity |

Examples: (ℕ, +) with 0 is a monoid but not a group. (ℤ, +) is an abelian group. Matrices under multiplication are a monoid, and the invertible ones form a group.

### Facts GATE uses

- **Lagrange's theorem:** the order of a subgroup divides the order of the group. So the order of every element divides |G|, and a group of prime order is cyclic.
- **Cyclic group of order n:** it has exactly φ(n) generators and one subgroup for every divisor d of n, of order d. The number of elements of order d is φ(d).
- **Order of an element** a in ℤₙ (additive) is n / gcd(a, n).
- **ℤₙ\* (multiplication mod n)** is a group of order φ(n) made of the numbers coprime to n. It is cyclic only for n = 1, 2, 4, pᵏ and 2pᵏ (p an odd prime).
- **Subgroup test:** a non-empty subset H is a subgroup if a·b⁻¹ ∈ H for all a, b ∈ H.
- **Orders of permutations:** an element of Sₙ has order equal to the lcm of its cycle lengths. S₃ has 3 elements of order 2 and 2 of order 3.
- The **Klein four-group** ℤ₂ × ℤ₂ is the smallest non-cyclic group. Every element has order 1 or 2.

!cheat Group cheat codes ::
- **Closure first:** for "is this a group?" questions check closure first. {1, 2, 3} under multiplication mod 4 fails because 2 × 2 = 0.
- **A group fails quickly:** no identity, a non-invertible element (such as 0 in multiplication), or failing associativity (like subtraction).
- **Element order divides group order.** In a group of order 18 there is no element of order 4, 5 or 7.
- **Number of subgroups of cyclic ℤₙ** = number of divisors of n.
- **Number of elements of order 2 in S₄** = 6 transpositions + 3 double transpositions = 9.
- **|HK| = |H||K| / |H ∩ K|** counts the product set of two subgroups.
!end

## Graph theory

### Basics

A graph G = (V, E) with v vertices and e edges. In a simple graph:

- **Handshake lemma:** the sum of all degrees is 2e, so the number of odd-degree vertices is even.
- **Complete graph Kₙ:** n(n−1)/2 edges, every degree n − 1. **Complete bipartite K_{m,n}:** mn edges.
- **Maximum edges** in a simple graph on n vertices: n(n−1)/2. In a bipartite graph: ⌊n²/4⌋.
- A graph is **bipartite** exactly when it has **no odd cycle**.

### Trees

A tree is a connected acyclic graph. Equivalent facts: v − 1 edges and connected; v − 1 edges and acyclic; a unique path between any two vertices.

- A forest with v vertices, e edges has **v − e components**.
- A tree has at least 2 leaves, and **L = 2 + Σ (dᵢ − 2)** over vertices of degree ≥ 3.
- **Cayley's formula:** Kₙ has n^(n−2) labelled spanning trees. Cₙ has n spanning trees.

### Euler and Hamilton

| | Condition | Remember |
|---|---|---|
| Euler circuit | connected, every degree even | uses every **edge** once |
| Euler path | connected, 0 or 2 odd-degree vertices | |
| Hamiltonian cycle | no exact rule | visits every **vertex** once. Dirac: if every degree ≥ n/2, then Hamiltonian |

### Planar graphs

For a connected planar graph: **v − e + f = 2**. For simple planar graphs with v ≥ 3, e ≤ 3v − 6. If the graph has no triangles, e ≤ 2v − 4. **K₅ and K₃,₃ are not planar**, and Kuratowski's theorem says a graph is non-planar exactly when it has a subdivision of K₅ or K₃,₃.

### Colouring and matching

- χ(Kₙ) = n. A bipartite graph has χ = 2. An odd cycle has χ = 3, an even cycle 2. Every planar graph is 4-colourable. The Petersen graph has χ = 3.
- Brooks: χ ≤ Δ except for complete graphs and odd cycles.
- **Hall's theorem:** a bipartite graph has a matching saturating X exactly when |N(S)| ≥ |S| for every S ⊆ X.
- **König:** in a bipartite graph, maximum matching = minimum vertex cover. Also |vertex cover| + |independent set| = v.
- A perfect matching of Kₙ (n even) can be done in (n−1)!! = (n−1)(n−3)…1 ways. K₆ has 15, K₄,₄ has 4! = 24.

!cheat Graph cheat codes ::
- **Planar edge count:** quote e ≤ 3v − 6. For a 10-vertex connected planar graph with 15 edges, f = 2 − v + e = 7.
- **Odd vertices test:** Euler circuit for Kₙ exists only for odd n. K₅ has one; K₄ does not.
- **Always check connectivity** before applying any Euler condition.
- **Tree leaves:** L = 2 + Σ (d − 2) over internal vertices. One degree-4 and two degree-3 vertices give 2 + 2 + 1 + 1 = 6 leaves.
- **Counting trees:** labelled trees on n vertices = n^(n−2); the number of ways to attach vertex degrees dᵢ is (n − 2)! / Π (dᵢ − 1)! (Prüfer sequence).
!end

## Combinatorics: counting, recurrences and generating functions

### Counting

| Task | Formula |
|---|---|
| Arrangements of r from n, order matters | P(n, r) = n! / (n − r)! |
| Choose r from n | C(n, r) |
| Arrange n with repeats a, b, c | n! / (a! b! c!) |
| Circular arrangements of n | (n − 1)! |
| Non-negative solutions of x₁ + … + x_k = n | C(n + k − 1, k − 1) |
| Positive solutions | C(n − 1, k − 1) |
| Derangements Dₙ | n! Σ (−1)ʲ / j! : 0, 1, 2, 9, 44, 265 for n = 1…6 |
| Catalan Cₙ | C(2n, n) / (n + 1) : 1, 1, 2, 5, 14, 42, 132 |

**Inclusion–exclusion:** |A ∪ B ∪ C| = Σ|A| − Σ|A ∩ B| + |A ∩ B ∩ C|. **Pigeonhole:** with N objects in k boxes, some box has at least ⌈N / k⌉.

The Catalan number Cₙ counts: balanced bracket sequences of n pairs, binary trees with n nodes, ways to parenthesise a product of n + 1 factors, and triangulations of an (n + 2)-gon.

### Recurrence relations

For aₙ = c₁aₙ₋₁ + c₂aₙ₋₂, solve the **characteristic equation** r² = c₁r + c₂:

| Roots | Solution |
|---|---|
| Distinct r₁, r₂ | aₙ = A r₁ⁿ + B r₂ⁿ |
| Repeated r | aₙ = (A + Bn) rⁿ |
| Complex | rⁿ (A cos nθ + B sin nθ) |

Use the initial values to find A and B. For a non-homogeneous recurrence, add a particular solution of the same form as the extra term. If that form is already a solution of the homogeneous equation, multiply it by n.

### Generating functions

The generating function of (aₙ) is Σ aₙ xⁿ. Useful series:

- 1 / (1 − x) = 1 + x + x² + …
- 1 / (1 − ax) = Σ aⁿ xⁿ
- 1 / (1 − x)ᵏ = Σ C(n + k − 1, k − 1) xⁿ
- (1 + x)ⁿ = Σ C(n, j) xʲ

Multiplying generating functions **convolves** coefficients, so the coefficient of xⁿ in a product counts the ways to split n between the factors. For example, 1 / ((1 − x)(1 − x²)) counts the ways to write n = a + 2b.

!cheat Counting and recurrence cheat codes ::
- **Stars and bars first:** any "distribute identical objects into distinct boxes" question is C(n + k − 1, k − 1), with minimums handled by subtracting them first.
- **"At least one" → complement.** Total minus none is almost always shorter.
- **Recurrence with a root 1** (like aₙ = aₙ₋₁ + 2) grows linearly or polynomially, not exponentially.
- **Check your closed form on a₀ and a₁** before trusting it.
- **Pigeonhole "guarantee" questions:** the answer is (boxes × (k − 1)) + 1.
- **Catalan check:** C₄ = 14, which counts ways to parenthesise 5 factors.
!end

## Cheat sheet: Discrete Mathematics on one page

| Topic | Formula or fact |
|---|---|
| Boolean functions of n variables | 2^(2ⁿ) |
| p → q | ¬p ∨ q ≡ ¬q → ¬p, false only for T → F |
| ¬(p → q) | p ∧ ¬q |
| FOL pairing | ∀ with →, ∃ with ∧ |
| Relations on n elements | all 2^(n²), reflexive 2^(n²−n), symmetric 2^(n(n+1)/2), antisymmetric 2ⁿ3^(n(n−1)/2) |
| Equivalence relations | Bell: 1, 2, 5, 15, 52, 203 |
| Functions n → m | mⁿ, injective P(m, n), onto by inclusion–exclusion |
| Dₙ Boolean algebra | n square-free |
| Lagrange | subgroup and element orders divide \|G\| |
| Cyclic group of order n | φ(n) generators, τ(n) subgroups |
| Handshake | Σ deg = 2e |
| Planar | v − e + f = 2, e ≤ 3v − 6 (e ≤ 2v − 4 triangle-free) |
| Euler circuit | connected, all degrees even |
| Labelled trees on n | n^(n−2) |
| Stars and bars | C(n + k − 1, k − 1) |
| Derangements | 0, 1, 2, 9, 44, 265 |
| Catalan | 1, 1, 2, 5, 14, 42, 132 |

??  How many binary relations on a 4-element set are reflexive and symmetric?
=> 2^(n(n−1)/2) = 2⁶ = 64. The diagonal is forced and each of the 6 unordered pairs is in or out.
??  Why is ∀x (P(x) ∨ Q(x)) not equivalent to ∀x P(x) ∨ ∀x Q(x)?
=> Take the domain {1, 2} with P true only at 1 and Q true only at 2. Every element satisfies P or Q, but neither P nor Q holds everywhere. The reverse direction (right implies left) does hold.
??  A tree has one vertex of degree 4, two of degree 3 and none of degree 2. How many leaves?
=> Leaves L = 2 + Σ (d − 2) = 2 + 2 + 1 + 1 = 6. Check: n = 9 vertices, degree sum = 4 + 6 + 6 = 16 = 2(n − 1).
??  How many generators does a cyclic group of order 12 have, and how many subgroups?
=> φ(12) = 4 generators and τ(12) = 6 subgroups (orders 1, 2, 3, 4, 6, 12).
