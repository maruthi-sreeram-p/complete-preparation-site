@part gate-digital-logic | Digital Logic | hardware
## Number representation and arithmetic

### Bases and conversions

Binary, octal and hexadecimal are related by grouping bits: 3 bits per octal digit, 4 bits per hex digit. For (3A7)₁₆ = 3·256 + 10·16 + 7 = 935. To convert a fraction to binary, multiply by 2 repeatedly and record the integer parts: 0.625 → 1.25 → 0.5 → 1.0 gives 0.101.

### Signed integers with n bits

| Scheme | Range | Negation | Zero |
|---|---|---|---|
| Sign-magnitude | −(2ⁿ⁻¹ − 1) to 2ⁿ⁻¹ − 1 | flip the sign bit | two zeros |
| 1's complement | −(2ⁿ⁻¹ − 1) to 2ⁿ⁻¹ − 1 | flip all bits | two zeros |
| **2's complement** | **−2ⁿ⁻¹ to 2ⁿ⁻¹ − 1** | flip all bits, add 1 | one zero |
| Excess-K (biased) | −K to 2ⁿ − 1 − K | add K | one zero |

2's complement is what hardware uses because the same adder works for signed and unsigned numbers. The value of a pattern is −b₍ₙ₋₁₎2ⁿ⁻¹ + Σ bᵢ2ⁱ. So 8-bit 11110000 is −128 + 64 + 32 + 16 = −16, and −25 is 11100111 (25 = 00011001, invert 11100110, add 1).

### Addition, subtraction and overflow

- **Subtraction:** A − B = A + (2's complement of B).
- **Sign extension:** copy the sign bit leftwards to widen a 2's complement number without changing its value.
- **Overflow in signed addition** happens only when two numbers of the **same sign** give a result of the **opposite sign**. Equivalent test: carry into the sign bit ≠ carry out of the sign bit. Adding 01100100 + 01100100 (100 + 100) gives 11001000, which reads as −56, with overflow.
- **Carry out** (not overflow) signals overflow for unsigned numbers.
- To hold the integers −N to +N you need the smallest n with 2ⁿ⁻¹ > N. For ±500 that is n = 10 bits (range −512 to 511).

### Other codes

| Code | Idea |
|---|---|
| BCD | each decimal digit in 4 bits: 93 → 1001 0011 |
| Gray | adjacent values differ in one bit: g = b ⊕ (b >> 1). 1011 → 1110 |
| Parity | one extra bit makes the number of 1s even (even parity) or odd |

### IEEE 754 floating point

| Format | Sign | Exponent | Fraction | Bias |
|---|---|---|---|---|
| Single (32 bit) | 1 | 8 | 23 | 127 |
| Double (64 bit) | 1 | 11 | 52 | 1023 |

For a normal number, **value = (−1)ˢ × 1.fraction × 2^(exponent − bias)**. The leading 1 is implied.

| Exponent field | Fraction | Meaning |
|---|---|---|
| all 0s | 0 | ±0 |
| all 0s | non-zero | denormal (no implied 1, exponent −126) |
| all 1s | 0 | ±∞ |
| all 1s | non-zero | NaN |

Worked example: −6.25 = −110.01₂ = −1.1001 × 2². Sign 1, exponent 2 + 127 = 129 = 10000001, fraction 1001 followed by zeros. The pattern is 1 10000001 1001000… = **0xC0C80000**.

The smallest positive normal single is 2⁻¹²⁶, and the smallest positive denormal is 2⁻¹⁴⁹.

!cheat Number-system cheat codes ::
- **Range of n-bit 2's complement:** −2ⁿ⁻¹ … 2ⁿ⁻¹ − 1. It has one more negative value than positive.
- **Quick negative:** read the number from the right, copy bits up to and including the first 1, then flip everything to the left.
- **Overflow trick:** only same-sign operands can overflow, and then only if the result sign differs. Opposite-sign operands never overflow.
- **Two zeros:** sign-magnitude and 1's complement have them. 2's complement does not.
- **Float to hex:** write the number as 1.f × 2ᵉ, add the bias to e, then group the bits in fours.
- **Exponent 0 or all 1s are special.** Normal numbers use exponents 1 to 254 (single) or 1 to 2046 (double).
- **Fraction bits are the precision:** more exponent bits give range, more fraction bits give accuracy.
!end

## Boolean algebra and minimization

### Laws

| Law | Form |
|---|---|
| Identity / null | A + 0 = A, A·1 = A, A + 1 = 1, A·0 = 0 |
| Idempotent | A + A = A, A·A = A |
| Complement | A + A′ = 1, A·A′ = 0 |
| Absorption | A + AB = A, A(A + B) = A |
| Redundancy | A + A′B = A + B |
| Distribution | A + BC = (A + B)(A + C) |
| De Morgan | (AB)′ = A′ + B′, (A + B)′ = A′B′ |
| **Consensus** | AB + A′C + BC = AB + A′C |
| XOR | A ⊕ B = AB′ + A′B, A ⊕ A = 0, A ⊕ 1 = A′ |

**Duality:** swap AND with OR and 0 with 1 to get the dual of an identity, which is also true.

### Canonical forms

A **minterm** is a product of all variables (each complemented or not) that is 1 for exactly one input row. A **maxterm** is a sum that is 0 for exactly one row. A function with n variables has 2ⁿ minterms. f = Σm(…) lists the rows where f = 1, and f = ΠM(…) lists the rows where f = 0. The two lists together cover all 2ⁿ rows, so **ΠM(0, 2, 5) over 3 variables has 8 − 3 = 5 minterms**.

### Karnaugh maps

A K-map writes the truth table in Gray-code order so that neighbouring cells differ in one variable. Group 1s in rectangles of size 1, 2, 4, 8, 16 (powers of 2). The map **wraps around** the edges, so the four corners of a 4-variable map form a group.

- A bigger group means fewer literals: a group of 2ᵏ cells in n variables gives a product term of n − k literals.
- A **prime implicant** (PI) is a group that cannot be enlarged. An **essential** PI covers a 1 that no other PI covers.
- Don't-care cells (X) may be used in groups to make them bigger, but need not be covered.
- Take all essential PIs, then add the fewest PIs to cover the rest.

Example. f(A, B, C, D) = Σm(0, 1, 2, 5, 6, 7, 8, 9, 10, 14) has six prime implicants. The essential ones are B′C′ (cells 0, 1, 8, 9) and CD′ (cells 2, 6, 10, 14), and A′BD (cells 5, 7) completes the cover. The minimum SOP is **B′C′ + CD′ + A′BD**, with 7 literals.

### Quine–McCluskey (tabular method)

1. List all minterms (and don't-cares) in binary and group by the number of 1s.
2. Combine two terms from adjacent groups if they differ in **exactly one bit**, replacing that bit by a dash.
3. Repeat until nothing combines. The terms left behind are the prime implicants.
4. Build the PI table and choose the essential PIs, then a minimum cover for the rest.

### Self-dual functions, hazards and universality

- A function is **self-dual** if f(x) = (f(x′))′. There are 2^(2ⁿ⁻¹) self-dual functions of n variables: 16 for n = 3.
- A **static-1 hazard** is a brief 0 glitch when a single input changes and the output should stay 1. Cure it by adding the consensus term. AB + A′C needs **BC**.
- **NAND and NOR are universal.** A two-level AND-OR network converts directly into two levels of NAND: AB + CD = ((AB)′ (CD)′)′ uses 3 two-input NANDs. XOR needs 4 NANDs.

!cheat Minimization cheat codes ::
- **Literal count:** a group of 2ᵏ cells loses k variables. Group the biggest rectangles first.
- **Corners and edges wrap.** Check for the four-corner group in a 4-variable map.
- **Count minterms from maxterms:** 2ⁿ minus the number of maxterms.
- **XOR of n variables** is 1 for exactly half the rows (2ⁿ⁻¹), and its K-map is a checkerboard that cannot be simplified.
- **f = A + B on 3 variables (A, B, C):** minterms are all rows except A = B = 0, so 8 − 2 = 6.
- **Redundancy trick:** A + A′B = A + B. If you can create a variable and its complement, you can often drop the complement.
- **Consensus term** is redundant in logic, but removes a hazard in hardware.
!end

## Combinational circuits

A combinational circuit's outputs depend only on the present inputs.

### Adders and subtractors

| Circuit | Outputs |
|---|---|
| Half adder | Sum = A ⊕ B, Carry = AB |
| Full adder | Sum = A ⊕ B ⊕ Cᵢₙ, Carry = AB + Cᵢₙ(A ⊕ B) (two half adders + one OR) |
| Half subtractor | Difference = A ⊕ B, Borrow = A′B |
| Ripple-carry adder | n full adders chained; worst-case delay ≈ n × (carry delay) |
| Carry-lookahead | G = AB (generate), P = A ⊕ B (propagate): C₁ = G₀ + P₀C₀, computed in parallel, so delay does not grow linearly |

A 32-bit ripple-carry adder with 2 ns per carry stage has a worst-case carry delay of 64 ns.

### Multiplexers, decoders and ROMs

| Block | Size rule |
|---|---|
| MUX 2ⁿ : 1 | n select lines, 2ⁿ data inputs, 1 output |
| DEMUX 1 : 2ⁿ | n select lines |
| Decoder n → 2ⁿ | one output high for each input code; outputs are the minterms |
| Encoder 2ⁿ → n | inverse; a priority encoder reports the highest-priority active input |

- **Any function of n variables fits a 2ⁿ⁻¹ : 1 MUX:** use n − 1 variables as selects and connect each data input to 0, 1, the last variable or its complement.
- **Building a 2ⁿ : 1 MUX from 2 : 1 MUXes** needs 2ⁿ − 1 of them (7 for 8 : 1).
- **Decoder + OR gate** implements any function: OR the minterm outputs for which f = 1. Σm(1, 2, 4, 7) needs a 3 → 8 decoder and a 4-input OR.
- **Cascading decoders:** a 4 → 16 decoder from 2 → 4 decoders with enable uses 4 + 1 = 5 of them.
- **ROM as a lookup table:** an 8-bit adder (two 8-bit inputs, 9-bit sum) needs 2¹⁶ words of 9 bits.
- **Parity of n bits** takes n − 1 two-input XOR gates.

!cheat Combinational cheat codes ::
- **MUX as function generator:** for f(A, B, C) = Σm(1, 2, 6, 7) with A, B as selects, the data inputs for AB = 00, 01, 10, 11 are C, C′, 0, 1. For each select combination, ask what f is in terms of the remaining variable.
- **Full adder = 2 half adders + 1 OR.** Gate delay of Sum is 2 XORs.
- **Carry out of a full adder** is the majority function of A, B, Cᵢₙ.
- **Sizes:** n select lines for 2ⁿ inputs, always.
- **Priority encoder 0110 with D₃ highest:** D₂ is the highest active input, so the output is 10.
!end

## Sequential circuits

A sequential circuit has memory: its output depends on the inputs **and** the stored state.

### Latches and flip-flops

A **latch** is level-sensitive and a **flip-flop** is edge-triggered. The NOR-based SR latch has S = R = 1 as the forbidden input, whereas a NAND-based one forbids S = R = 0.

| Flip-flop | Characteristic equation | Notes |
|---|---|---|
| SR | Q⁺ = S + R′Q | S = R = 1 not allowed; S = R = 0 holds |
| D | Q⁺ = D | copies D on the clock edge |
| JK | Q⁺ = JQ′ + K′Q | J = K = 1 toggles |
| T | Q⁺ = T ⊕ Q | T = 1 toggles |

**Conversions:** JK as D: J = D, K = D′. D as T: D = T ⊕ Q. JK as T: J = K = T.

**Race-around:** a level-triggered JK flip-flop with J = K = 1 keeps toggling for as long as the clock is high. It is cured with edge triggering or a master–slave design.

### Registers and counters

- An n-bit **shift register** moves data one position per clock. Serial-in/serial-out needs n clocks to move a bit through.
- A **ring counter** of n flip-flops cycles through **n** states (one hot). A **Johnson (twisted-ring) counter** cycles through **2n** states.
- An **asynchronous (ripple) counter** clocks each stage from the previous one. An n-bit counter divides the input frequency by 2ⁿ at its last output, and the maximum clock rate is limited by the total ripple delay, about 1 / (n · t_pd). Four stages at 20 ns each allow at most 1 / 80 ns = 12.5 MHz.
- A **mod-N counter** needs ⌈log₂ N⌉ flip-flops. A mod-12 counter needs 4. Cascaded counters multiply: mod-5 followed by mod-8 is mod-40.
- **Synchronous counters** clock every flip-flop together, so all outputs change at the same time and are faster but need more logic.

### Finite state machines and timing

- **Moore:** outputs depend only on the current state. **Mealy:** outputs depend on the current state **and** the input (so they react in the same cycle).
- A machine with S states needs ⌈log₂ S⌉ flip-flops. 17 states need 5.
- An overlapping "101" sequence detector needs **3 states in Mealy** form and **4 in Moore** form.
- **Setup time:** data must be stable before the clock edge. **Hold time:** stable after it.
- **Minimum clock period** = t_clk→Q + t_combinational + t_setup. With 1 ns, 6 ns, 1 ns that is 8 ns, i.e. a maximum frequency of 125 MHz.
- A **setup violation** is fixed by slowing the clock or shortening the logic. A **hold violation** cannot be fixed by changing the clock frequency; add delay in the data path.

!cheat Sequential cheat codes ::
- **Memorise the four characteristic equations** (SR, D, JK, T). Every conversion or "next state" question starts there.
- **Counters:** states = 2ⁿ for a binary counter, n for a ring, 2n for a Johnson counter.
- **Frequency division:** an n-bit counter's MSB runs at f / 2ⁿ. 16 kHz into 3 bits gives 2 kHz.
- **Moore vs Mealy states:** Moore usually needs one more state than Mealy for the same detector.
- **Timing:** T_clk ≥ t_clk→Q + t_comb + t_setup. Frequency is the inverse. Hold issues ignore frequency.
- **Flip-flop count:** ⌈log₂ states⌉, always rounded up.
!end

## Cheat sheet: Digital Logic on one page

| Topic | Fact |
|---|---|
| 2's complement range | −2ⁿ⁻¹ to 2ⁿ⁻¹ − 1 |
| Signed overflow | same-sign operands, opposite-sign result |
| IEEE single | 1 + 8 + 23 bits, bias 127; double 1 + 11 + 52, bias 1023 |
| Boolean functions of n variables | 2^(2ⁿ) |
| Redundancy | A + A′B = A + B |
| Consensus | AB + A′C + BC = AB + A′C |
| K-map group of 2ᵏ cells | n − k literals |
| Minterms from maxterms | 2ⁿ minus the count |
| Full adder | Sum = A ⊕ B ⊕ C; Carry = AB + C(A ⊕ B) |
| MUX / decoder | n select lines for 2ⁿ inputs; n → 2ⁿ |
| 2ⁿ : 1 MUX from 2 : 1 | 2ⁿ − 1 |
| Any n-variable function | 2ⁿ⁻¹ : 1 MUX |
| JK, T, D, SR | Q⁺ = JQ′ + K′Q, T ⊕ Q, D, S + R′Q |
| Ring / Johnson counter | n states / 2n states |
| Clock period | t_clk→Q + t_comb + t_setup |
| FSM flip-flops | ⌈log₂ states⌉ |

??  Why is 2's complement preferred to sign-magnitude in hardware?
=> The same binary adder performs signed and unsigned addition, subtraction is addition of the complement, and there is only one representation of zero.
??  How do you detect overflow when adding two 2's complement numbers?
=> Overflow occurs when both operands have the same sign and the result has the opposite sign, which is also when the carry into the sign bit differs from the carry out of it. Operands with different signs can never overflow.
??  Express f = AB + A′C + BC in its simplest form and explain why a designer may keep the third term.
=> By the consensus theorem f = AB + A′C. A designer may keep BC to avoid a static-1 hazard when A switches while B = C = 1.
??  How many states does an overlapping "101" detector need in Mealy and Moore form?
=> 3 for Mealy (nothing, seen 1, seen 10) and 4 for Moore, because Moore needs an extra state whose output is the detection.
