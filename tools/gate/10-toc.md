@part gate-toc | Theory of Computation | software
## The big picture: the Chomsky hierarchy

Every GATE question in this subject sits somewhere on this ladder. Learn what each level can and cannot do.

| Type | Language class | Grammar | Machine | Example it can do | Example it cannot do |
|---|---|---|---|---|---|
| 3 | Regular | right/left linear | DFA, NFA | strings ending in 01 | aⁿbⁿ |
| 2 | Context-free (CFL) | A → α (one non-terminal on the left) | PDA | aⁿbⁿ, palindromes | aⁿbⁿcⁿ, ww |
| 1 | Context-sensitive (CSL) | αAβ → αγβ | linear bounded automaton (LBA) | aⁿbⁿcⁿ, ww | the halting problem |
| 0 | Recursively enumerable (RE) | unrestricted | Turing machine | halting (semi-decidable) | co-halting |

Regular ⊂ CFL ⊂ CSL ⊂ Recursive ⊂ RE. Deterministic and non-deterministic machines have the same power for finite automata, and for Turing machines, but **not** for pushdown automata.

## Finite automata

A **DFA** is (Q, Σ, δ, q₀, F) with exactly one transition per state and symbol. An **NFA** may have several or none, and may use ε-moves. They accept exactly the same languages (the regular languages). Converting an NFA with n states to a DFA by the **subset construction** gives at most **2ⁿ** states, and this bound can be reached.

### Building and counting states

| Language over {a, b} or {0, 1} | States of the minimal complete DFA |
|---|---|
| ends with 01 | 3 |
| ends with abb | 4 (substring length + 1) |
| contains 101 as a substring | 4 |
| does not contain 11 | 3 (including a dead state) |
| (number of a's) mod 3 = 0 **and** (number of b's) mod 2 = 0 | 3 × 2 = 6 (product) |
| number of a's even **or** number of b's even | 4 |
| the 3rd symbol from the end is a | **2³ = 8** (an NFA needs only 4) |
| binary number (MSB first) divisible by 5 | 5 (the remainder is the state) |
| length divisible by 3 **or** by 5 | 15 (the length modulo 15) |

Rules of thumb:

- **"Ends with a string of length k":** k + 1 states.
- **"k-th symbol from the end":** 2ᵏ DFA states, k + 1 NFA states.
- **Modular counters** need one state per residue, and independent conditions multiply.
- **Complement:** swap the accepting and non-accepting states of a **complete** DFA. Does not work directly on an NFA.
- **Product construction:** a DFA for L₁ ∩ L₂ or L₁ ∪ L₂ needs at most m × n states (m and n are the sizes of the two DFAs).
- **Myhill–Nerode theorem:** the minimal DFA for L has exactly as many states as there are equivalence classes of the relation "x ~ y if xz ∈ L ⇔ yz ∈ L for every z". If this number is infinite, L is not regular.

Counting strings: the number of binary strings of length n with no two consecutive 1s is the Fibonacci number F(n + 2): 21 for n = 6.

!cheat DFA cheat codes ::
- **Draw the states as "what I still need to remember".** For "ends with abb" remember the longest suffix that is a prefix of abb.
- **Count the classes with the Myhill–Nerode idea:** two prefixes are the same state if every future suffix treats them alike.
- **Dead state:** a complete DFA needs one. "Contains 101" has none (the accepting state absorbs everything), but "does not contain 11" does.
- **A DFA for "divisible by k"** has k states, with δ(r, bit) = (2r + bit) mod k for binary input.
- **Closure under the three basic operations** (union, concatenation, star) plus complement, intersection, reversal, difference and homomorphism.
!end

## Regular expressions and regular languages

A regular expression is built from ∅, ε, symbols, union (+), concatenation and star (*). Useful identities:

| Identity | |
|---|---|
| R + R = R, R + ∅ = R | |
| Rε = R, R∅ = ∅ | |
| (R*)* = R*, ε + RR* = R* | |
| **(a + b)\* = (a\*b\*)\* = (a\* + b\*)\* = (a + b\*)\*** | all generate every string over {a, b} |
| (a + b)\* ≠ a\*b\* | a\*b\* cannot produce "ba" |
| a(ba)\* = (ab)\*a | |

Conversions: RE → NFA (Thompson construction; the NFA has O(|r|) states), NFA → RE (state elimination or Arden's theorem), RE ↔ regular grammar. For the right-linear grammar S → aS | bA, A → aA | ε, the language is a\*ba\*.

Examples of REs:

- Ends in ab: (a + b)\*ab.
- Even number of 0s: 1\*(01\*01\*)\*.
- First and last symbols differ: a(a + b)\*b + b(a + b)\*a.
- Number of strings of length 3 in (ab + a)\*: aaa, aab, aba, so 3.

### The pumping lemma (to prove a language is NOT regular)

If L is regular there is a length p such that every w in L with |w| ≥ p can be written w = xyz with **|xy| ≤ p, |y| ≥ 1 and xyⁱz ∈ L for all i ≥ 0.** To show L is not regular: pick an adversary-proof string w, show that **every** valid split (y lies within the first p symbols) pumps out of L.

| Not regular | Why |
|---|---|
| {aⁿbⁿ} | pumping y (all a's) unbalances the counts |
| {aⁱbʲ : i > j} | pump down (i = 0) to violate i > j |
| {ww}, {wwᴿ} | needs unbounded memory |
| {aᵖ : p prime}, {a^(n²) : n ≥ 0} | gaps between members grow |

| Regular, despite appearances | Why |
|---|---|
| {w : #01 = #10 in w} | equivalent to "empty, or first symbol = last symbol" |
| {aⁱbʲ : i + j is even} | just a parity condition |
| {w : |w| divisible by 3} | a counter modulo 3 |

!warning The pumping lemma only proves non-regularity :: Passing the pumping test does not show a language is regular. And counting "equal numbers" of single symbols is non-regular, but counting equal numbers of substrings such as 01 and 10 is regular.

**Decision problems for regular languages** (emptiness, finiteness, membership, equivalence, containment) are all **decidable**.

!cheat Regular-language cheat codes ::
- **Closure:** complement, union, intersection, difference, concatenation, star, reversal, homomorphism, inverse homomorphism. **A subset of a regular language need not be regular.**
- **Test equivalence of REs** by trying all strings up to length 3 or 4. A failing string is a counterexample.
- **Non-regular suspects:** anything that compares two unbounded counts (aⁿbⁿ), copies a string (ww) or tests primality.
- **Regular suspects:** any condition that needs only bounded memory: parity, residues, "starts with", "ends with", "contains".
- **Pumping proof template:** assume p, choose w = aᵖbᵖ (or similar), note y ⊆ aˢ, pump to get a string outside L.
!end

## Context-free grammars and pushdown automata

A **CFG** has productions A → α, with a single non-terminal on the left. A derivation is **leftmost** or **rightmost** depending on which non-terminal is expanded first, and the same parse tree can correspond to many derivations. A grammar is **ambiguous** if some string has two different parse trees (equivalently, two leftmost derivations).

| Grammar | Language |
|---|---|
| S → aSb \| ε | {aⁿbⁿ : n ≥ 0} |
| S → aSa \| bSb \| a \| b \| ε | all palindromes over {a, b} |
| S → aSb \| bSa \| SS \| ε | strings with equal numbers of a's and b's |
| S → aSb \| SS \| ε | balanced brackets with a = "(" and b = ")" (2 strings of length 4: aabb, abab) |
| S → SS \| a | a⁺, **ambiguous** (aaa has two parse trees) |
| S → aS \| b | a\*b, unambiguous |

Some languages are **inherently ambiguous**: every grammar for them is ambiguous, for example {aⁱbʲcᵏ : i = j or j = k}.

### Normal forms

- **Chomsky normal form (CNF):** every production is A → BC or A → a. A string of length n has a derivation of exactly **2n − 1** steps.
- **Greibach normal form (GNF):** every production is A → aα with α a string of non-terminals. A string of length n takes exactly **n** steps.
- Conversion removes ε-productions, unit productions and useless symbols first.
- The **CYK algorithm** decides membership for a CNF grammar in **O(n³ · |G|)** time.

### Pushdown automata

A PDA is a finite automaton plus a stack. It can be accepted **by final state or by empty stack**, and the two give the same class of languages for non-deterministic PDAs.

- **NPDA ⊋ DPDA.** The deterministic CFLs (DCFLs) are a **proper** subset of the CFLs.
- A DPDA accepts {aⁿbⁿ}, {wcwᴿ} and {aⁿbᵐcⁿ}, but **no DPDA** accepts {wwᴿ}, because the machine cannot know where the middle is.
- A PDA can accept {aⁿbⁿ}, but not {aⁿbⁿcⁿ}, which needs two comparisons from one stack.

!cheat CFG and PDA cheat codes ::
- **Find the language of a grammar** by listing the shortest strings it derives, then guess the pattern and check a longer string.
- **Ambiguity test:** find one string with two parse trees. Left-recursive and right-recursive rules in the same non-terminal (S → SS) are a hint.
- **CNF steps:** 2n − 1. **GNF steps:** n. For n = 7 that is 13 and 7.
- **Stack counts one thing.** Equal counts of two symbols → PDA. Three counts, or a copy (ww) → not a PDA.
- **wcwᴿ → DPDA. wwᴿ → NPDA only.** The marker c is what makes it deterministic.
!end

## Properties and pumping lemma for context-free languages

| Operation | Regular | CFL | DCFL |
|---|---|---|---|
| Union | yes | yes | no |
| Concatenation | yes | yes | no |
| Kleene star | yes | yes | no |
| Reversal | yes | yes | no |
| **Intersection** | yes | **no** | no |
| **Complement** | yes | **no** | **yes** |
| Intersection with a regular language | yes | **yes** | yes |
| Homomorphism | yes | yes | no |

Proof that CFLs are not closed under intersection: {aⁿbⁿcᵐ} and {aᵐbⁿcⁿ} are both context-free, and their intersection {aⁿbⁿcⁿ} is not.

The complement of {aⁿbⁿ} **is** context-free (a union of "wrong order" and "wrong counts" parts), which shows that a CFL's complement is sometimes a CFL.

### The pumping lemma for CFLs

If L is context-free there is a p such that every w in L with |w| ≥ p can be written **w = uvxyz** with **|vxy| ≤ p, |vy| ≥ 1 and uvⁱxyⁱz ∈ L for all i ≥ 0.** Use it to show a language is not context-free.

| Not context-free | Context-free |
|---|---|
| {aⁿbⁿcⁿ} | {aⁿbⁿcᵐ}, {aⁿbᵐcᵐ} |
| {ww : w ∈ {a, b}\*} | {wwᴿ}, {wcwᴿ} |
| {aⁿbᵐcⁿdᵐ} | {aⁱbʲcᵏ : i = j or j = k} |
| {aⁱbʲcᵏ : k = i·j} | complement of {aⁿbⁿ}, complement of {ww} |

**Decision problems for CFGs.** *Decidable:* is L(G) empty? is L(G) finite? is w ∈ L(G)? (CYK). *Undecidable:* is G ambiguous? is L(G) = Σ\*? is L(G₁) = L(G₂)? is L(G₁) ∩ L(G₂) = ∅? is L(G) regular?

!cheat CFL cheat codes ::
- **Intersection and complement:** CFLs fail both, DCFLs have complement, and a regular language is always safe to intersect with.
- **CFL vs not:** one stack can compare two quantities in a nested order (aⁿbⁿ, wwᴿ), but not three (aⁿbⁿcⁿ) or crossing pairs (aⁿbᵐcⁿdᵐ, ww).
- **"i = j or j = k"** is a union of two CFLs, hence a CFL, and it is not deterministic.
- **Pumping bookkeeping:** v and y are pumped together, and they can touch at most two of the three symbol blocks.
- **Decidable for CFG:** emptiness, finiteness, membership. **Undecidable:** ambiguity, equivalence, universality.
!end

## Turing machines and decidability

A **Turing machine** has an infinite tape, a head that reads, writes and moves left or right, and a finite control. Multi-tape, non-deterministic and two-way-infinite-tape machines accept **exactly the same languages** as the basic TM (they only change the running time).

| Class | Meaning |
|---|---|
| **Recursive (decidable)** | a TM that halts on every input accepts or rejects |
| **Recursively enumerable (semi-decidable)** | a TM accepts exactly the strings of L but may loop on others |
| Not RE | no TM can even semi-decide it |

### Closure and relationships

- Recursive languages are closed under complement, union, intersection and concatenation.
- RE languages are closed under union, intersection, concatenation and star, but **not** under complement.
- **L and its complement are both RE ⇔ L is recursive.**
- So the halting language HALT is RE but not recursive, and its complement is **not RE**.
- A universal Turing machine simulates any TM from a description of the machine plus its input.
- Context-sensitive languages are decidable (an LBA has finitely many configurations), so membership for context-sensitive grammars is **decidable**.

### Undecidability

- **The halting problem** ("does M halt on w?") is undecidable.
- **Rice's theorem:** every non-trivial property of the *language* of a TM is undecidable. Examples: is L(M) empty? is L(M) finite? is L(M) regular? is L(M) = Σ\*? do two TMs accept the same language?
- **Syntactic properties** of the machine's description are decidable: "does M have at least 10 states?", "does M ever move left on its first step?".
- If A reduces to B (A ≤ₘ B) and A is undecidable, then B is undecidable. If B is decidable, so is A.
- **Post correspondence problem (PCP)** is undecidable and is used to prove undecidability for CFG problems.
- "Does a TM accept at least one string?" is undecidable but semi-decidable (RE): dovetail over all inputs.

!cheat Decidability cheat codes ::
- **Ask: is the property about the language or about the machine's description?** Language property → Rice → undecidable. Description property (state count) → decidable.
- **RE vs recursive:** if you can only confirm "yes" answers, it is RE. If you can answer both, it is recursive.
- **Complement trick:** a language is recursive exactly when it and its complement are RE.
- **Reduction direction:** to prove B undecidable, reduce a known undecidable problem **to** B.
- **Everything about DFAs is decidable** (emptiness, equivalence, membership). The first undecidable problems appear with CFGs (ambiguity, equivalence) and TMs.
!end

## Cheat sheet: Theory of Computation on one page

| Topic | Fact |
|---|---|
| Hierarchy | Regular ⊂ CFL ⊂ CSL ⊂ Recursive ⊂ RE |
| NFA → DFA | ≤ 2ⁿ states |
| Ends with a string of length k | k + 1 DFA states |
| k-th symbol from the end | 2ᵏ DFA states |
| Product construction | m × n |
| Myhill–Nerode | classes = states of the minimal DFA |
| Regular closure | everything (but not arbitrary subsets) |
| Pumping (regular) | \|xy\| ≤ p, \|y\| ≥ 1, xyⁱz ∈ L |
| Pumping (CFL) | \|vxy\| ≤ p, \|vy\| ≥ 1, uvⁱxyⁱz ∈ L |
| CNF / GNF | 2n − 1 steps / n steps |
| CYK | O(n³ \|G\|) |
| DPDA vs NPDA | wcwᴿ vs wwᴿ |
| CFL not closed | intersection, complement |
| DCFL | closed under complement |
| RE not closed | complement |
| Undecidable CFG problems | ambiguity, equivalence, universality |
| Rice's theorem | non-trivial language properties of TMs |
| L and complement both RE | L is recursive |

??  Why does the language {aⁿbⁿ} need a stack but {a*b*} does not?
=> {a*b*} only requires remembering that the a's are finished, which is a constant amount of information. {aⁿbⁿ} requires remembering an unbounded count n, which a finite automaton cannot do but a stack can (push an a per a, pop one per b).
??  How many states does the minimal DFA for "the third symbol from the end is a" have, and why?
=> 8. The DFA must remember the last three symbols, and each of the 2³ combinations leads to a different future behaviour. An NFA can guess the position and needs only 4 states.
??  Is "does a Turing machine halt on input w?" decidable? What about "does it have more than 5 states?"
=> The halting problem is undecidable (and only semi-decidable). Counting states is decidable: read the machine's description and count, because it is a property of the description, not of the language.
??  Why is the intersection of two context-free languages not necessarily context-free?
=> {aⁿbⁿcᵐ} and {aᵐbⁿcⁿ} are both context-free (each compares one pair of counts), but their intersection is {aⁿbⁿcⁿ}, which needs two comparisons at once and is not context-free by the pumping lemma.
