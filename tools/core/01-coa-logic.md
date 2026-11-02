@part coa-logic | Computer Organisation · Part 1: Digital Logic Foundations | coa
## From transistors to Boolean algebra

A computer is built from circuits that have only two meaningful voltage levels, read as **0** and **1**. A **logic gate** takes bits in and produces a bit out. Everything the CPU does, from adding numbers to running your Java program, is a very large arrangement of a handful of gate types.

There are two families of circuit, and the rest of this guide keeps coming back to the difference:

| | Combinational circuit | Sequential circuit |
|---|---|---|
| Output depends on | the **current inputs** only | the current inputs **and the stored state** |
| Has memory | no | yes (flip-flops, latches) |
| Needs a clock | no | usually yes |
| Examples | adder, multiplexer, decoder, ALU | register, counter, finite state machine, memory cell |

### The basic gates

| Gate | Expression | Output is 1 when |
|---|---|---|
| AND | A · B | both inputs are 1 |
| OR | A + B | at least one input is 1 |
| NOT | A' | the input is 0 |
| NAND | (A · B)' | not both inputs are 1 |
| NOR | (A + B)' | both inputs are 0 |
| XOR | A ⊕ B = A'B + AB' | the inputs differ (odd number of 1s) |
| XNOR | (A ⊕ B)' | the inputs are equal |

**NAND and NOR are universal gates**: any Boolean function can be built from NAND gates alone (or NOR gates alone). That is why real chips are often built from one gate type. For example NOT A = NAND(A, A), and AND = NOT(NAND). An XOR needs **4 NAND gates**.

### Boolean algebra laws you will use every day

| Law | AND form | OR form |
|---|---|---|
| Identity | A · 1 = A | A + 0 = A |
| Null | A · 0 = 0 | A + 1 = 1 |
| Idempotent | A · A = A | A + A = A |
| Complement | A · A' = 0 | A + A' = 1 |
| Absorption | A · (A + B) = A | A + A · B = A |
| Distributive | A · (B + C) = AB + AC | A + BC = (A + B)(A + C) |

**De Morgan's laws** (the most tested identities in the subject): (A + B)' = A' · B' and (A · B)' = A' + B'. In words: *break the bar, change the sign*. They let you convert between AND-OR and NAND-NAND forms.

!cheat Ten-second Boolean tricks ::
- A + A'B = A + B (the complement vanishes: `A + A'B = (A + A')(A + B) = A + B`).
- A ⊕ 0 = A, A ⊕ 1 = A', A ⊕ A = 0, A ⊕ A' = 1.
- The number of Boolean functions of n variables is **2^(2^n)**: 16 for 2 variables, 256 for 3.
- n variables have 2^n minterms, numbered by the binary value of the inputs.
- A function with k minterms among 2^n has an SOP form of at most k product terms before simplification.
!end

### Standard forms: minterms and maxterms

A **minterm** is an AND of all variables, each in true or complemented form, that is 1 for exactly one input combination. A **maxterm** is an OR of all variables that is 0 for exactly one combination.

- **Sum of products (SOP)**: OR together the minterms where f = 1. f(A,B,C) = Σm(1,3,5,6) means f is 1 for inputs 001, 011, 101 and 110.
- **Product of sums (POS)**: AND together the maxterms where f = 0. The two forms describe the same function: the minterms missing from the SOP are the maxterms of the POS.

!keypoints Combinational circuits have no memory: output depends on current inputs only ;; NAND and NOR are universal; XOR needs 4 NAND gates ;; De Morgan: break the bar, change the sign ;; n variables give 2^(2^n) Boolean functions and 2^n minterms ;; SOP lists where f is 1 (minterms), POS lists where f is 0 (maxterms)

?? Why are NAND and NOR called universal gates?
=> Every Boolean function can be built from NAND gates alone, or from NOR gates alone: NOT, AND and OR can each be made from them (NOT A = NAND(A, A); AND = NOT of NAND; OR by De Morgan). A chip designer can therefore manufacture one gate type.

?? How many different Boolean functions can be defined on 3 variables?
=> 2^(2^3) = 256. There are 2^3 = 8 input combinations and each can independently produce 0 or 1.

?? State De Morgan's laws.
=> (A + B)' = A'·B' and (A·B)' = A' + B'. Complementing an OR gives an AND of complements, and complementing an AND gives an OR of complements.

## Simplifying with Karnaugh maps

Fewer gates mean a cheaper, faster, lower-power circuit. A **Karnaugh map** (K-map) is a grid arranged so that cells that differ in one variable are neighbours; grouping neighbouring 1s removes variables.

The rules:

1. Axes use **Gray code** order (00, 01, 11, 10), so adjacent cells differ in exactly one bit. The map **wraps around**: the left and right edges touch, and so do the top and bottom.
2. Group the 1s into rectangles whose size is a **power of two** (1, 2, 4, 8, 16).
3. Make the groups **as large as possible**, and use as **few groups** as possible, but cover every 1.
4. A group of 2^k cells removes k variables. A group of 8 cells on a 4-variable map leaves a single literal.
5. **Don't-care** cells (X) may be used as 1 to make a group bigger, but need not be covered.

**Example.** f(A,B,C) = Σm(0,1,2,3,6,7) = A' + B. The four cells with A = 0 form one group that eliminates B and C, giving A'. The cells m2, m3, m6, m7 (B = 1) form a group that eliminates A and C, giving B. Result: **f = A' + B**.

| | BC = 00 | 01 | 11 | 10 |
|---|---|---|---|---|
| A = 0 | 1 | 1 | 1 | 1 |
| A = 1 | 0 | 0 | 1 | 1 |

### Terms you must be able to name

- **Implicant**: any product term that implies f.
- **Prime implicant**: an implicant that cannot be made larger (a maximal group).
- **Essential prime implicant**: a prime implicant that covers a 1 no other prime implicant covers. It must appear in every minimal SOP.
- **Hazard**: a brief unwanted glitch caused by unequal gate delays when one input changes. A **static-1 hazard** appears when a function that should stay at 1 dips to 0 for a moment; adding the redundant (consensus) term covering the two adjacent groups removes it.

!cheat K-map checklist ::
1. Mark every minterm (and don't care) on a Gray-coded grid.
2. Start with the 1s that have only one possible group: they give the essential prime implicants.
3. Cover the remaining 1s with the fewest, biggest groups.
4. Write each group as the variables that do not change.
5. OR the groups. For POS, group the 0s instead, then complement the result.
!end

!interview Interview angle: What is a hazard, and when does it matter? :: A hazard is a glitch at a gate's output caused by different propagation delays on different paths, for example a function that should stay at 1 while one input changes. In a purely combinational circuit that only feeds a flip-flop, the glitch usually settles before the clock edge and is harmless. It matters when the output drives an asynchronous input, such as a clock or reset line. It is removed by adding the redundant consensus term.

!keypoints Group 1s in power-of-two rectangles, as large as possible, wrapping around the edges ;; A group of 2^k cells removes k variables ;; Use Gray code order on the axes ;; Essential prime implicants cover a 1 that nothing else covers ;; Don't cares help make groups bigger but need not be covered

?? What is the Gray code order of the K-map axes for?
=> It makes neighbouring cells differ in exactly one variable. That is the property that lets a group of cells drop a variable: the cells in the group agree on all the other variables.

?? What is the difference between a prime implicant and an essential prime implicant?
=> A prime implicant is a group that cannot be enlarged. It is essential if it covers at least one 1 that no other prime implicant covers, so every minimal expression must include it.

## Combinational building blocks

Combinational circuits are assembled from a small set of standard blocks. Knowing each block's **size and delay** answers most numerical questions.

### Adders

A **half adder** adds two bits: **Sum = A ⊕ B**, **Carry = A · B**. It cannot accept a carry from the previous column.

A **full adder** adds A, B and a carry-in:

- **Sum = A ⊕ B ⊕ Cin**
- **Cout = A·B + Cin·(A ⊕ B)**

A full adder can be built from two half adders and an OR gate.

An n-bit **ripple-carry adder** chains n full adders: the carry-out of each stage feeds the next. It is cheap and simple but **slow**: the carry must travel through all n stages, so the worst-case delay grows linearly with n. A 32-bit ripple adder with 2 ns per carry stage needs about 64 ns for the carry to settle.

A **carry-lookahead adder (CLA)** computes carries in parallel from two signals per bit: **generate G = A·B** (this column makes a carry by itself) and **propagate P = A ⊕ B** (this column passes a carry along). Then C(i+1) = G(i) + P(i)·C(i), expanded so that every carry depends only on the inputs and C0. The delay is roughly constant in n (or grows with log n for a hierarchy of look-ahead units) at the cost of more gates.

### Multiplexers, demultiplexers, decoders, encoders

| Block | Inputs → outputs | What it does |
|---|---|---|
| **Multiplexer (MUX) 2^n : 1** | 2^n data + n select → 1 | Picks one of 2^n inputs |
| **Demultiplexer 1 : 2^n** | 1 data + n select → 2^n | Routes one input to one of 2^n outputs |
| **Decoder n : 2^n** | n inputs → 2^n outputs | Exactly one output is 1: it produces every minterm |
| **Encoder 2^n : n** | 2^n inputs → n outputs | Reverse of a decoder; a **priority encoder** handles several active inputs |
| **Comparator** | two n-bit numbers → <, =, > | Compares magnitudes |

**Implementing functions:**

- A **decoder plus an OR gate** implements any function: OR together the outputs for the minterms where f = 1.
- A **2^n : 1 MUX implements any function of n + 1 variables**: use n variables as select lines and connect each data input to 0, 1, the remaining variable or its complement. So an 8:1 MUX realises any 4-variable function.
- A bigger MUX can be built from smaller ones: one 8:1 MUX needs two 4:1 MUXes plus one 2:1 MUX.

!cheat Block sizes to remember ::
- n select lines → 2^n inputs (4:1 MUX has 2 select lines, 8:1 has 3, 16:1 has 4).
- A 3-to-8 decoder has 8 AND-type outputs; a 4-to-16 decoder is built from two 3-to-8 decoders using the enable input.
- A 4:1 MUX = three 2:1 MUXes. A 2^n : 1 MUX = 2^n − 1 two-to-one MUXes.
- Full adder: 2 XOR + 2 AND + 1 OR (or 9 NAND gates).
- n-bit ripple-carry delay ≈ n × (carry delay per stage).
!end

!keypoints Full adder: Sum = A⊕B⊕Cin, Cout = AB + Cin(A⊕B) ;; Ripple carry delay grows linearly with n; carry lookahead uses generate and propagate to compute carries in parallel ;; A decoder produces all minterms; decoder plus OR implements any function ;; A 2^n:1 MUX can implement any function of n+1 variables ;; A 2^n:1 MUX needs 2^n − 1 two-to-one MUXes

?? Why is a ripple-carry adder slow, and how does carry lookahead fix it?
=> The carry out of each stage depends on the previous stage's carry, so the carry ripples through all n stages one after another. Carry lookahead computes every carry directly from the generate (A·B) and propagate (A⊕B) signals and the first carry-in, so the carries are available in parallel after a constant (or logarithmic) number of gate delays, at the price of more hardware.

?? What function can an 8:1 multiplexer implement without extra gates?
=> Any Boolean function of 4 variables. Three variables drive the select lines and each data input is tied to 0, 1, the fourth variable or its complement.

## Sequential circuits: memory, registers and counters

Sequential circuits remember. The basic memory element is a **latch** (level-sensitive) or **flip-flop** (edge-triggered): a circuit with two stable states that stores one bit.

### Latches and flip-flops

| Element | Behaviour | Characteristic equation |
|---|---|---|
| **SR latch** | S = set, R = reset; S = R = 1 is forbidden (invalid) | Q⁺ = S + R'·Q |
| **D flip-flop** | Copies D to Q on the clock edge | Q⁺ = D |
| **JK flip-flop** | J = K = 0 hold, J = 1 K = 0 set, J = 0 K = 1 reset, J = K = 1 **toggle** | Q⁺ = JQ' + K'Q |
| **T flip-flop** | T = 0 hold, T = 1 toggle | Q⁺ = T ⊕ Q |

A **latch** changes whenever its enable is high (level-triggered); a **flip-flop** changes only on a clock **edge**, which makes synchronous design predictable. A JK flip-flop becomes a T flip-flop by tying J and K together, and a D flip-flop by connecting J = D, K = D'.

### Registers and counters

- An n-bit **register** is n D flip-flops sharing a clock. A **shift register** passes each bit to its neighbour on every clock: serial-in/parallel-out converts a serial line to a parallel word.
- A **ripple (asynchronous) counter** chains T flip-flops, each clocked by the previous output. It is simple, but the delays add up: n flip-flops with a propagation delay t each can take **n × t** to settle, which limits the clock speed.
- A **synchronous counter** clocks all flip-flops together and uses logic to decide which toggle, so the delay does not accumulate.
- A **mod-N counter** counts 0 to N − 1 and repeats. It needs **⌈log₂ N⌉ flip-flops**. A mod-10 (decade) counter needs 4. A **ring counter** with n flip-flops has n states; a **Johnson (twisted ring) counter** with n flip-flops has **2n** states.

### Timing: how fast can the clock run?

Between two flip-flops, a signal must leave the first (clock-to-Q delay), travel through logic, and arrive at the second early enough to meet its **setup time**:

**T_clock ≥ t_clk→Q + t_logic(max) + t_setup**, and the maximum frequency is **1 / T_clock**.

The **hold time** is the interval after the edge during which the data must stay stable; a hold violation cannot be fixed by slowing the clock.

**Example.** t_clk→Q = 1 ns, longest logic path = 6 ns, setup = 1 ns: T ≥ 8 ns, so f_max = 125 MHz.

### Finite state machines

A **finite state machine (FSM)** is a state register plus combinational logic for the next state and the output. In a **Moore machine** the output depends only on the **state**; in a **Mealy machine** it depends on the state and the **current input**, so it can react one cycle earlier and often needs fewer states. A machine with N states needs ⌈log₂ N⌉ flip-flops (binary encoding).

!cheat Sequential circuit quick answers ::
- Flip-flops for N states or a mod-N counter: ⌈log₂ N⌉.
- Johnson counter: 2n states from n flip-flops. Ring counter: n states.
- T flip-flop from JK: J = K = T. D flip-flop from JK: J = D, K = D'.
- Ripple counter worst-case settling time: n × (flip-flop delay).
- f_max = 1 / (t_clk→Q + t_logic + t_setup).
- Moore output = f(state); Mealy output = f(state, input).
!end

!interview Interview angle: Latch versus flip-flop? :: A latch is level-sensitive: while its enable is active its output follows the input, so changes can race through several latches in one phase. A flip-flop samples its input only on the clock edge (a master-slave pair of latches), so each stage changes once per cycle. Synchronous design with flip-flops is easy to reason about and to time.

!keypoints Latches are level-triggered, flip-flops are edge-triggered ;; JK with J=K=1 and T with T=1 toggle ;; Mod-N counters need ⌈log₂ N⌉ flip-flops; a Johnson counter has 2n states ;; Ripple counters accumulate delay; synchronous counters do not ;; Clock period ≥ clock-to-Q + logic delay + setup time ;; Moore output depends on state only, Mealy output also on input

?? How many flip-flops does a mod-12 counter need?
=> ⌈log₂ 12⌉ = 4 flip-flops, since 3 flip-flops give only 8 states and 4 give 16.

?? What is the maximum clock frequency if clock-to-Q is 1 ns, the longest logic path is 6 ns and setup time is 1 ns?
=> The period must be at least 1 + 6 + 1 = 8 ns, so the frequency is at most 1 / 8 ns = 125 MHz.

?? What is the difference between a Moore and a Mealy machine?
=> In a Moore machine the output is a function of the current state only. In a Mealy machine the output is a function of the state and the current input, so it can change as soon as the input changes and usually needs fewer states.
