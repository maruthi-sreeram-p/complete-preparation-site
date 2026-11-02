@part coa-data | Computer Organisation · Part 2: Data Representation and Computer Arithmetic | coa
## Number systems and text

A computer stores everything as bits, so you must be fluent in the positional number systems that group bits conveniently.

| System | Base | Digits | Why it is used |
|---|---|---|---|
| Binary | 2 | 0, 1 | What the hardware stores |
| Octal | 8 | 0 to 7 | One digit = 3 bits (older systems, Unix permissions) |
| Hexadecimal | 16 | 0 to 9, A to F | One digit = 4 bits (addresses, colours, memory dumps) |
| Decimal | 10 | 0 to 9 | Humans |

### Converting between bases

- **To decimal:** multiply each digit by its place value. 1011₂ = 8 + 0 + 2 + 1 = 11. 2F₁₆ = 2 × 16 + 15 = 47.
- **Decimal to binary (integers):** divide by 2 repeatedly and read the remainders from the last to the first. 37 → remainders 1, 0, 1, 0, 0, 1, so 37 = **100101₂**.
- **Decimal fractions to binary:** multiply the fraction by 2 repeatedly and read the integer parts from the top. 0.625 × 2 = 1.25 → 1; 0.25 × 2 = 0.5 → 0; 0.5 × 2 = 1.0 → 1, so 0.625 = **0.101₂**.
- **Binary ↔ hex:** group bits in fours from the binary point. 1101 0110₂ = D6₁₆. **Binary ↔ octal:** group in threes.

A fraction such as 0.1 has an **infinite** binary expansion (0.000110011001100...₂), exactly as 1/3 has an infinite decimal expansion. This is the root of the floating-point surprises in the third chapter.

!cheat Quick facts ::
- n bits represent 2ⁿ different values. To number N items you need ⌈log₂ N⌉ bits.
- 2¹⁰ = 1024 (Ki), 2²⁰ = Mi, 2³⁰ = Gi, 2⁴⁰ = Ti. A 32-bit address reaches 4 GiB; a 48-bit address reaches 256 TiB.
- Hex digit = 4 bits, so a 32-bit value is 8 hex digits and a byte is 2.
- **Gray code** changes one bit between consecutive values: gray(n) = n XOR (n >> 1). gray(5) = 7 (111).
- **BCD** stores each decimal digit in 4 bits: 59 = 0101 1001. It wastes 6 of the 16 codes per digit.
!end

### Text: ASCII, Unicode, UTF-8

**ASCII** assigns 7-bit codes to 128 characters ('A' = 65, 'a' = 97, '0' = 48; the lowercase code is the uppercase code + 32). **Unicode** gives every character in every script a unique number (a code point). **UTF-8** stores a code point in 1 to 4 bytes: ASCII characters take **1 byte** (so valid ASCII is valid UTF-8), most European letters 2, most Indian scripts 3, emoji 4. Java's `char` is 16 bits (UTF-16), so characters outside the basic plane use two `char`s.

!keypoints n bits give 2ⁿ values, and N values need ⌈log₂ N⌉ bits ;; Group bits by 4 for hex and by 3 for octal ;; Many decimal fractions have infinite binary expansions ;; Gray code changes one bit per step; BCD uses 4 bits per decimal digit ;; UTF-8 is 1 to 4 bytes per character and ASCII-compatible

?? Convert 0.625 to binary and explain why 0.1 cannot be written exactly.
=> 0.625 = 0.101₂ (0.5 + 0.125). A fraction is finite in binary only if its denominator, in lowest terms, is a power of two. 0.1 = 1/10 has the factor 5 in the denominator, so its binary expansion repeats forever and must be rounded when stored.

?? How many bits are needed to give a distinct number to each of 1,000 students?
=> ⌈log₂ 1000⌉ = 10 bits, because 2⁹ = 512 is too few and 2¹⁰ = 1024 is enough.

## Signed integers

An n-bit unsigned integer covers 0 to 2ⁿ − 1. To store negative numbers there are three schemes:

| Scheme | How −x is formed | Range (n bits) | Problems |
|---|---|---|---|
| **Sign-magnitude** | flip the leftmost (sign) bit | −(2ⁿ⁻¹ − 1) to +(2ⁿ⁻¹ − 1) | two zeros (+0, −0); addition needs sign logic |
| **One's complement** | flip **all** bits | −(2ⁿ⁻¹ − 1) to +(2ⁿ⁻¹ − 1) | two zeros; needs an end-around carry |
| **Two's complement** | flip all bits, **add 1** | **−2ⁿ⁻¹ to +(2ⁿ⁻¹ − 1)** | one extra negative number |

**Two's complement is what every modern CPU uses**, and what Java's `int` and `long` use. Reasons: one representation of zero, and the *same adder* works for signed and unsigned numbers.

### Working in two's complement

- **Negate:** invert the bits, add 1. +37 = 00100101, so −37 = 11011010 + 1 = **11011011**.
- **Meaning of the bits:** the sign bit has weight −2ⁿ⁻¹. 11011011 = −128 + 64 + 16 + 8 + 2 + 1 = −37.
- **Range of 8 bits:** −128 to +127. The most negative number, 10000000, **has no positive partner**: negating it gives itself. This is why `Math.abs(Integer.MIN_VALUE)` is negative in Java.
- **Sign extension:** to widen a number, copy the sign bit into the new upper bits. 8-bit 11111011 (−5) becomes 16-bit 1111111111111011 (−5). Zero-extending a signed value gives a wrong answer.
- **Subtraction:** A − B = A + (two's complement of B). The adder and a row of XOR gates are enough.

### Overflow

Overflow happens when the true result does not fit in n bits.

- **Unsigned:** overflow if there is a **carry out** of the leftmost bit.
- **Signed (two's complement):** overflow if two numbers of the **same sign** give a result of the **opposite sign**. Equivalently, the carry **into** the sign bit differs from the carry **out of** it. Adding numbers of different signs can never overflow.

**Example (8 bits):** 100 + 50 = 150 > 127, so 01100100 + 00110010 = 10010110, which reads as −106. Two positives gave a negative: overflow. Java does not warn you: `Integer.MAX_VALUE + 1` silently becomes `Integer.MIN_VALUE`.

!cheat Signed number cheat sheet ::
- Two's complement range: **−2ⁿ⁻¹ to 2ⁿ⁻¹ − 1** (8 bits: −128..127, 16 bits: −32768..32767, 32 bits: about ±2.1 × 10⁹).
- −x = ~x + 1. The bit pattern of −1 is all ones.
- Sign-magnitude and one's complement both have **±0**.
- Sign overflow rule: carry into the sign bit ≠ carry out of the sign bit.
- Sign-extend signed values, zero-extend unsigned values. In Java `>>` keeps the sign and `>>>` fills with zeros.
!end

!keypoints Two's complement: invert and add 1; range −2ⁿ⁻¹ to 2ⁿ⁻¹ − 1 with one zero ;; The most negative number has no positive counterpart ;; Signed overflow: same-sign operands, opposite-sign result ;; Sign-extend when widening a signed value ;; One adder serves both signed and unsigned arithmetic

?? Why do computers use two's complement instead of sign-magnitude?
=> Two's complement has a single representation of zero, and the same binary adder produces correct results for both signed and unsigned operands, so no extra sign-handling hardware is needed. Subtraction becomes addition of the complement.

?? How do you detect overflow when adding two signed numbers?
=> Overflow occurs when both operands have the same sign and the result has the opposite sign (equivalently, the carry into the sign bit differs from the carry out of it). Operands of different signs cannot overflow.

?? What is the 8-bit two's complement representation of −37?
=> +37 = 00100101; inverting gives 11011010 and adding 1 gives 11011011.

## Floating-point numbers (IEEE 754)

Integers cannot represent 3.14 or 6.02 × 10²³. **Floating point** stores a number as **sign, exponent and fraction**, like scientific notation in binary: **(−1)^s × 1.fraction × 2^(exponent − bias)**.

| | Single (Java `float`) | Double (Java `double`) |
|---|---|---|
| Total bits | 32 | 64 |
| Sign | 1 | 1 |
| Exponent | 8 | 11 |
| Fraction (mantissa) | 23 | 52 |
| Bias | 127 | 1023 |
| Precision | about 7 decimal digits | about 15 to 16 decimal digits |
| Largest finite value | about 3.4 × 10³⁸ | about 1.8 × 10³⁰⁸ |

The leading 1 of a **normalised** number is **implied** (the "hidden bit"), so 23 stored bits give 24 bits of precision.

### Encoding a number step by step

**Encode −118.625 as a 32-bit float.**

1. Sign: negative, so s = 1.
2. Convert to binary: 118.625 = 1110110.101₂.
3. Normalise: 1.110110101 × 2⁶.
4. Exponent: 6 + 127 = 133 = 10000101₂.
5. Fraction (drop the leading 1, pad with zeros): 11011010100000000000000.
6. Result: 1 | 10000101 | 11011010100000000000000 = **0xC2ED4000**.

**Decode 0x40B00000:** 0 | 10000001 | 01100000000000000000000. The exponent is 129 − 127 = 2 and the mantissa is 1.011₂ = 1.375, so the value is 1.375 × 4 = **5.5**.

### Special values

| Exponent | Fraction | Meaning |
|---|---|---|
| all 0 | 0 | **±0** |
| all 0 | not 0 | **denormal** (subnormal): no hidden 1, fills the gap around zero |
| all 1 | 0 | **±infinity** |
| all 1 | not 0 | **NaN** (not a number), e.g. 0/0 |

### The surprises

- **0.1 + 0.2 ≠ 0.3** in Java, Python and JavaScript: both operands are rounded, and the sum prints as `0.30000000000000004`. Never compare floating-point values with `==`; compare with a tolerance. Use `BigDecimal` for money.
- **Precision shrinks with magnitude.** Near 2²⁴ = 16,777,216 a `float` can no longer represent every integer: `16777216f + 1f == 16777216f`.
- **Addition is not associative** with rounding: (a + b) + c can differ from a + (b + c). Adding a tiny number to a huge one loses it.
- **NaN is not equal to itself:** `Double.NaN == Double.NaN` is false; use `Double.isNaN`.

!cheat IEEE 754 single precision ::
- Value = (−1)^s × 1.f × 2^(E − 127), with E the stored exponent (1..254 for normal numbers).
- 1.0 = 0x3F800000. 0.15625 = 0x3E200000. −0.75 = 0xBF400000. 5.5 = 0x40B00000.
- Exponent range for normal numbers: −126 to +127 (stored 1 to 254).
- Smallest step near 1.0 is 2⁻²³ (about 1.2 × 10⁻⁷); for `double`, 2⁻⁵² (about 2.2 × 10⁻¹⁶).
- Compare floats with `Math.abs(a - b) < epsilon`, never `==`.
!end

!interview Interview angle: Why does 0.1 + 0.2 not equal 0.3, and what do you do about it? :: 0.1 and 0.2 have no exact binary representation, so each is stored as the nearest double; their sum is rounded again and lands one step away from the double nearest 0.3. Compare with a tolerance (`Math.abs(a - b) < 1e-9`), or avoid floating point: use integers (store cents as a `long`) or `BigDecimal` for money.

!keypoints Floating point = sign, biased exponent, fraction with a hidden leading 1 ;; Single: 1+8+23 bits, bias 127; double: 1+11+52 bits, bias 1023 ;; Exponent all ones means infinity or NaN; all zeros means zero or denormal ;; Most decimal fractions are not exact, so never compare floats with == ;; Large values lose integer precision (float beyond 2²⁴)

?? What are the field sizes and bias of IEEE 754 single precision?
=> 1 sign bit, 8 exponent bits with bias 127, and 23 fraction bits, with an implied leading 1 giving 24 bits of precision.

?? Why do financial programs avoid float and double?
=> Decimal fractions like 0.10 are not exactly representable, and rounding errors accumulate and make totals differ by tiny amounts. Money is stored as an integer count of the smallest unit (cents) or in `BigDecimal`.

## Arithmetic algorithms and error detection

### Addition and subtraction

Addition in two's complement is plain binary addition, ignoring the final carry out. Subtraction A − B = A + ~B + 1: the subtractor is the adder with the B inputs inverted (XOR gates controlled by a "subtract" line) and the carry-in set to 1.

### Multiplication

**Shift-and-add:** for each bit of the multiplier, from the least significant end, add the multiplicand to the partial product if the bit is 1, and shift. An n × n multiplication produces a **2n-bit** product and takes n add steps.

**Booth's algorithm** handles signed multipliers and skips runs of ones. It scans the multiplier bits in pairs (the current bit and the one to its right, with an implicit 0 beyond the end):

| Bit pair (current, right) | Action |
|---|---|
| 00 or 11 | do nothing (inside a run) |
| 10 | **subtract** the multiplicand (start of a run of 1s) |
| 01 | **add** the multiplicand (end of a run of 1s) |

A run of ones like 0111100 is worth 2⁶ − 2² = 60, so it needs only **one subtraction and one addition** instead of four additions: Booth is fast on multipliers with long runs, and the same for positive and negative numbers. The worst case is an alternating pattern such as 01010101, which needs n operations.

### Division

**Restoring division** shifts the remainder left, subtracts the divisor, and if the result is negative, adds the divisor back (restores) and the quotient bit is 0. **Non-restoring division** avoids the restore step by adding instead of subtracting in the next step, so it is faster. For an n-bit quotient, both take n steps.

### Detecting and correcting bit errors

| Code | Detects | Corrects | Idea |
|---|---|---|---|
| **Parity bit** | any odd number of bit flips | nothing | one extra bit makes the count of 1s even (or odd) |
| **Hamming code** | up to 2 bit errors | **1 bit** | check bits at positions 1, 2, 4, 8, ...; the syndrome gives the error position |
| **CRC** | burst errors | nothing | polynomial division remainder, used by Ethernet, disks |

A Hamming code needs r check bits for m data bits where **2ʳ ≥ m + r + 1**: 4 data bits need 3 check bits (the classic (7,4) code), 8 data bits need 4, and 64 data bits need 7. Adding one **overall parity bit** gives **SECDED** (single-error correction, double-error detection), the scheme used in ECC memory.

!keypoints Subtraction = add the complement; one adder with XOR gates does both ;; Shift-and-add multiplies in n steps with a 2n-bit result ;; Booth recodes runs of 1s: 10 subtract, 01 add, 00 and 11 skip ;; Restoring and non-restoring division take n steps for n quotient bits ;; Hamming needs 2^r ≥ m + r + 1 check bits and corrects 1 bit; SECDED adds one parity bit

?? How many check bits does a single-error-correcting Hamming code need for 8 data bits?
=> r such that 2ʳ ≥ 8 + r + 1: r = 3 gives 8 ≥ 12 (false), r = 4 gives 16 ≥ 13 (true). So 4 check bits, giving a 12-bit codeword.

?? Why is Booth's algorithm faster than plain shift-and-add on some multipliers?
=> It replaces a run of consecutive 1s by one subtraction at the start and one addition after the end, so a multiplier like 0111100 needs 2 operations instead of 4. For a multiplier with alternating bits it gives no benefit.
