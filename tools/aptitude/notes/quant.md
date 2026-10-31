# Number System
## Types of numbers
| Type | Facts to remember |
|---|---|
| Primes | 25 primes below 100; 2 is the only even prime; every prime above 3 has the form 6k ± 1 |
| Co-primes | HCF is 1, though neither has to be prime |
| Sums | 1 + 2 + ... + n = n(n+1)/2; squares: n(n+1)(2n+1)/6; cubes: [n(n+1)/2]² |

**Harder example.** Find the sum of the squares of the first 10 numbers. 10 × 11 × 21 / 6 = 385.

**Trap:** 1 is neither prime nor composite, and 91 = 7 × 13 and 119 = 7 × 17 look prime but are not.
## Divisibility rules
| By | Rule |
|---|---|
| 4 / 8 | The last 2 / 3 digits are divisible |
| 3 / 9 | The digit sum is divisible |
| 6 / 12 | Divisible by 2 and 3 / by 3 and 4 |
| 11 | Difference of the digit sums at odd and even places is 0 or a multiple of 11 |
| 7, 11, 13 | Any number of the form abcabc is divisible by all three (1001 = 7 × 11 × 13) |

**Harder example.** For which digit x is 7x4 divisible by 11? The alternating sum is 7 + 4 − x = 11 − x, so x = 0 gives 11, and 704 = 11 × 64.

**Trap:** divisibility by 12 needs both 3 and 4: a number divisible by 2 and 6 need not be divisible by 12 (for example 18).
## HCF & LCM
- HCF × LCM = product of two numbers. This works only for two numbers.
- HCF of fractions = HCF of numerators ÷ LCM of denominators; LCM of fractions = LCM of numerators ÷ HCF of denominators.
- Greatest number leaving remainders r₁, r₂ on a, b: HCF(a − r₁, b − r₂).
- Greatest number leaving the same remainder on a, b, c: HCF(a − b, b − c).

**Harder example.** The greatest number dividing 43, 91 and 183 with the same remainder: HCF(91 − 43, 183 − 91) = HCF(48, 92) = 4.

**Trap:** "smallest number that leaves remainder r" uses the LCM plus r. "Greatest divisor" uses the HCF.
## Factors & multiples
For N = aᵖ × b^q × cʳ:

- Number of factors = (p + 1)(q + 1)(r + 1).
- Sum of factors = (aᵖ⁺¹ − 1)/(a − 1) × (b^q⁺¹ − 1)/(b − 1) × ...
- Odd factors: ignore the powers of 2. Even factors = all − odd.
- A number has an odd count of factors only if it is a perfect square.

**Harder example.** How many even factors does 360 have? 360 = 2³ × 3² × 5, so 4 × 3 × 2 = 24 in all. Odd ones are 3 × 2 = 6, so even ones are 18.
## Remainders
- (a × b) mod m = [(a mod m)(b mod m)] mod m. The same holds for + and −.
- Fermat: if p is prime and does not divide a, then a^(p−1) leaves remainder 1 on dividing by p.
- (x − 1) divides xⁿ − 1 always. (x + 1) divides xⁿ + 1 when n is odd.

**Harder example.** Remainder of 2¹⁰⁰ on dividing by 7: 2³ = 8 leaves 1, and 100 = 3 × 33 + 1, so the remainder is 2.

**Trap:** a negative remainder must be converted: −2 mod 7 is 5.
## Unit digit & cyclicity
| Last digit | Cycle | Length |
|---|---|---|
| 0, 1, 5, 6 | Same digit | 1 |
| 2 | 2, 4, 8, 6 | 4 |
| 3 | 3, 9, 7, 1 | 4 |
| 4 | 4, 6 | 2 |
| 7 | 7, 9, 3, 1 | 4 |
| 8 | 8, 4, 2, 6 | 4 |
| 9 | 9, 1 | 2 |

Divide the power by 4 and use the remainder; a remainder of 0 means use power 4.

**Harder example.** Unit digit of 7⁹⁵ × 3⁵⁸: 95 mod 4 = 3 gives 3. 58 mod 4 = 2 gives 9. 3 × 9 = 27, so 7.
## Factorials & trailing zeros
Trailing zeros come from pairs of 2 and 5. Fives are rarer, so count them: ⌊n/5⌋ + ⌊n/25⌋ + ⌊n/125⌋ + ...

For a composite base, split it: to find the highest power of 12 in n!, compute the powers of 2 and 3. Then the answer is the smaller of (power of 2) ÷ 2 and (power of 3).

**Harder example.** Power of 12 in 30!. Twos: 15 + 7 + 3 + 1 = 26, which gives 13 fours. Threes: 10 + 3 + 1 = 14. The answer is 13.

**Trap:** 25 contributes two fives, and 125 contributes three, so the higher terms cannot be skipped.
## Number base systems
- To decimal: multiply each digit by its place value. (1101)₂ = 8 + 4 + 0 + 1 = 13.
- From decimal: divide repeatedly and read remainders upward.
- Binary to octal: group 3 bits. Binary to hex: group 4 bits.

**Harder example.** Write (2F)₁₆ in binary: 2 is 0010 and F is 1111, giving 101111. In decimal, it is 2 × 16 + 15 = 47.

**Trap:** digit 8 cannot appear in base 8, and digits above 9 appear in hexadecimal as A to F.
## Surds & indices
| Law | Form |
|---|---|
| Product | aᵐ × aⁿ = aᵐ⁺ⁿ |
| Power | (aᵐ)ⁿ = aᵐⁿ |
| Negative | a⁻ⁿ = 1/aⁿ |
| Fractional | a^(1/n) is the nth root |

To remove a surd from a denominator, multiply by the conjugate: 1/(√3 + √2) = √3 − √2.

**Harder example.** If 4ˣ = 8, then 2²ˣ = 2³, so x = 3/2.

**Trap:** √(a + b) is not √a + √b.
## Logarithms
| Rule | Form |
|---|---|
| Product | log(ab) = log a + log b |
| Quotient | log(a/b) = log a − log b |
| Power | log(aⁿ) = n log a |
| Change of base | logₐ b = log b / log a |

Digits in N = ⌊log₁₀ N⌋ + 1.

**Harder example.** If log 2 = 0.3010, the digits in 2⁵⁰: 50 × 0.3010 = 15.05, so 16 digits.

**Trap:** log(a + b) is not log a + log b, and the log of zero or a negative number is undefined.
# Simplification & Approximation
## BODMAS
Work in order: Brackets, Of, Division and Multiplication (left to right), then Addition and Subtraction (left to right).

**Harder example.** 18 − [6 − {4 − (7 − 3)}] = 18 − [6 − {4 − 4}] = 18 − 6 = 12.

**Trap:** 8 ÷ 2 × 4 is 16, not 1, because division and multiplication go left to right.
## Fractions & decimals
- 0.(ab) recurring = ab/99. 0.a(b) = (ab − a)/90.
- To compare fractions, cross-multiply, or use decimals to two places.
- Useful: 1/7 = 0.142857..., 1/8 = 0.125, 1/9 = 0.111..., 1/11 = 0.0909..., 1/16 = 0.0625.

**Harder example.** 0.2(7) = (27 − 2)/90 = 25/90 = 5/18.
## Squares, cubes & roots
- Memorise squares to 30 and cubes to 15.
- (a + b)² = a² + 2ab + b²; so 103² = 10000 + 600 + 9 = 10609.
- A perfect square never ends in 2, 3, 7 or 8.
- Square of a number ending in 5: 75² = (7 × 8) followed by 25 = 5625.

**Harder example.** √5.76 = 2.4, because √576 = 24, and the decimal halves its places.
## Approximation
Round each number to something easy, then choose the nearest option. Round one number up and another down in a product to keep the error small. Look at how far apart the options are: wide options permit rough rounding.

**Harder example.** 39.8% of 501 is near 40% of 500 = 200.

**Trap:** rounding both numbers up in a division pushes the result in unknown directions, so check against the options.
# Percentages
## Basic percentage
Useful equivalents: 1/8 = 12.5%, 1/6 = 16.67%, 1/3 = 33.33%, 3/8 = 37.5%, 2/3 = 66.67%, 5/6 = 83.33%, 1/7 ≈ 14.29%, 1/9 ≈ 11.11%, 1/11 ≈ 9.09%.

Note that x% of y = y% of x. So 16% of 25 = 25% of 16 = 4.

**Harder example.** If 30% of a number is 90 more than 20% of it, then 10% is 90, and the number is 900.
## Percentage change
- Change % = change ÷ original × 100.
- If A is x% more than B, then B is x/(100 + x) × 100% less than A.
- If a price rises x%, consumption must fall x/(100 + x) × 100% to keep spending the same.

**Harder example.** Salary rises from ₹25,000 to ₹30,000, a 20% rise. Going back needs a 5000/30000 = 16.67% cut.

**Trap:** the base differs in each direction, so a 20% rise is not undone by a 20% fall.
## Successive percentages
Net change for a and b: a + b + ab/100, with decreases taken as negative. A rise and fall of x% gives a net x²/100% loss.

**Harder example.** Three successive 10% rises: multiply 1.1 × 1.1 × 1.1 = 1.331, which is 33.1%.

**Trap:** successive changes do not add. 20% and 30% make 56%, not 50%.
## Population & depreciation
Growth: P(1 + r/100)ⁿ. Depreciation: P(1 − r/100)ⁿ. Different rates each year: multiply each factor.

**Harder example.** Population 10,000 grows 10% then falls 10%: 10,000 × 1.1 × 0.9 = 9,900.

**Trap:** finding the value n years ago means dividing by the factor, rather than multiplying by (1 − r/100).
# Ratio, Proportion & Variation
## Ratio
- Share of A in the ratio a : b : c = a/(a + b + c) × total.
- A : B = 2 : 3 and B : C = 4 : 5 means A : B : C = 8 : 12 : 15. Make B equal.
- Compounded ratio of a : b and c : d is ac : bd.

**Harder example.** Coins of ₹1, 50 p and 25 p in the ratio 1 : 2 : 3 total ₹55. Values are in the ratio 1 : 1 : 0.75 = 4 : 4 : 3. The ₹1 coins are worth 4/11 × 55 = ₹20, so there are 20 of them, with 40 of 50 p and 60 of 25 p.
## Proportion
a : b = c : d means ad = bc. Mean proportional of a, b is √(ab). Third proportional is b²/a. Fourth proportional of a, b, c is bc/a.

**Harder example.** The fourth proportional of 4, 9 and 12 is 9 × 12 ÷ 4 = 27.
## Direct & inverse variation
Direct: y = kx. Inverse: xy = k. Joint: y = kxz. The chain rule combines them: M₁D₁H₁/W₁ = M₂D₂H₂/W₂.

**Harder example.** 8 men working 6 hours a day finish in 10 days. 12 men working 5 hours a day take 8 × 6 × 10 ÷ (12 × 5) = 8 days.
## Componendo & dividendo
If a/b = c/d, then (a + b)/(a − b) = (c + d)/(c − d). Use it when an equation has the form (x + y)/(x − y).

**Harder example.** (x + 3)/(x − 3) = 5/2 gives x/3 = (5 + 2)/(5 − 2) = 7/3, so x = 7.
# Averages
## Simple average
Average = sum ÷ count. For an AP, it equals the middle term, or (first + last) ÷ 2. Use **deviations**: pick a base, average the differences, and add back.

**Harder example.** Average of 52, 56, 49, 53: base 50, deviations 2, 6, −1, 3 average 2.5, so 52.5.
## Weighted average
(n₁a₁ + n₂a₂)/(n₁ + n₂). The combined average lies nearer the larger group. This is the same as alligation.

**Trap:** averaging two averages works only if the groups are equal in size.
## Average speed
Equal distances: 2ab/(a + b). Equal times: (a + b)/2. Otherwise: total distance ÷ total time.

**Harder example.** Equal distances at 30, 40 and 60: 3 ÷ (1/30 + 1/40 + 1/60) = 3 ÷ (9/120) = 40 km/h.
## Replacement & addition problems
Replacement: new value = old value + n × change in average. Addition: new value = new average + (old count) × change in average.

**Harder example.** Average age of 8 men rises by 2 when two men aged 20 and 24 are replaced by two women. The women's total is 44 + 16 = 60, so their average is 30.
# Problems on Ages
## Present, past & future ages
Write a single unknown for the present age, and shift everything else to it. Differences between two people's ages never change.

**Harder example.** Ten years ago, A was twice B's age. In 10 years, A will be 1.5 times B's age. A − 10 = 2(B − 10) and A + 10 = 1.5(B + 10). So A = 2B − 10, and 2B = 1.5B + 15, giving B = 30 and A = 50.

**Trap:** "x years hence" applies to both people.
## Ratio-based age problems
Let the ages be ax and bx. Their difference (a − b)x stays fixed, which often gives x directly.

**Harder example.** Ages 3 : 4 now, 5 : 6 in 8 years. (3x + 8)/(4x + 8) = 5/6, so 18x + 48 = 20x + 40 and x = 4. Ages 12 and 16.
# Partnership
## Simple partnership
With equal time, profit follows the ratio of capital.

**Harder example.** A, B and C invest in the ratio 1/2 : 1/3 : 1/4. Multiply by 12: 6 : 4 : 3.

**Trap:** a ratio of fractions must be cleared first. It is not 2 : 3 : 4.
## Compound partnership
Profit follows capital × time. When capital changes, sum each period: A's share = C₁t₁ + C₂t₂.

**Harder example.** A invests ₹10,000 and adds ₹5,000 after 6 months. B invests ₹20,000 throughout the year. A: 60,000 + 90,000 = 150,000. B: 240,000. Ratio 5 : 8.
## Working vs. sleeping partner
Deduct the working partner's salary or commission first, and share the rest by capital × time. A sleeping partner only invests.

**Trap:** do not apply the percentage to the partner's share. Check whether it is on total profit.
# Profit & Loss
## Cost price, selling price, profit & loss
Profit % is on CP unless stated otherwise. SP = CP(100 + P)/100.

If a person sells two items at the same price, one at x% profit and the other at x% loss, there is always a loss of x²/100%.

**Harder example.** Two phones are sold at ₹9,900 each, at 10% profit and 10% loss. The net result is a 1% loss on total CP.
## Discount & marked price
Discount is on the marked price. CP × (100 + P)/100 = MP × (100 − D)/100.

**Harder example.** To make 20% profit after a 10% discount, mark up by 120/90 − 1 = 33.33%.

**Trap:** profit is on CP but discount is on MP, so they cannot be simply added.
## Successive discounts
d₁ and d₂ together are d₁ + d₂ − d₁d₂/100. The order does not matter.

**Harder example.** 20%, 10% and 5%: 0.8 × 0.9 × 0.95 = 0.684, so a 31.6% discount.
## Dishonest dealings
Profit % from a false weight = (true − false)/false × 100. With a markup too: (1 + p/100) × (true/false) − 1.

**Trap:** the base is the false weight rather than 1000 g: 900 g for 1 kg means 100/900 = 11.11%, not 10%.
# Simple & Compound Interest
## Simple interest
SI = PRT/100. A sum multiplies to k times in T years at R = (k − 1) × 100/T.

**Harder example.** Doubles in 8 years: R = 12.5%. It becomes 4 times when interest is 3 times the sum: 3 × 8 = 24 years.
## Compound interest
A = P(1 + R/100)ⁿ. Half-yearly: use R/2 and 2n. Quarterly: use R/4 and 4n. CI for a fraction of a year: apply simple interest to that part in the final period.

**Harder example.** ₹10,000 at 10% for 2.5 years: 10,000 × 1.21 × 1.05 = ₹12,705.

Rule of 72: money doubles in about 72/R years.
## Difference between CI and SI
For 2 years: P(R/100)². For 3 years: P(R/100)²(3 + R/100).

**Harder example.** ₹8,000 at 5% for 3 years: 8000 × 0.0025 × 3.05 = ₹61.
## Installments
Under compound interest, each installment is discounted back: P = x/(1 + r) + x/(1 + r)² + ...

**Harder example.** A loan at 10% repaid in 2 equal installments of ₹1,210: 1100 + 1000 = ₹2,100.
## Effective rate of interest
Effective rate = (1 + r/n)ⁿ − 1. It exceeds the nominal rate when n is above 1.

**Harder example.** 12% compounded quarterly: 1.03⁴ − 1 = 12.55%.
# Mixtures & Alligations
## Alligation rule
(Costlier − mean) : (mean − cheaper) gives the ratio cheaper : costlier.

```text
 cheaper c          costlier d
        \           /
           mean m
        /           \
    d − m           m − c
```

**Harder example.** A dealer mixes rice at ₹30 and ₹45, and sells at ₹42 for a 20% profit. Mean cost = 42/1.2 = ₹35. Ratio = 10 : 5 = 2 : 1.

**Trap:** first turn selling price into cost price before alligating.
## Replacement of a mixture
After taking out x from V and refilling, n times: Remaining = V(1 − x/V)ⁿ.

**Harder example.** A 40 l can of milk. Remove 4 l and refill with water, three times: 40 × 0.9³ = 29.16 l.

**Trap:** the formula applies to the quantity being diluted, and needs equal removals.
# Time & Work
## Work-rate
Rate = 1/days. Rates add when people work together. Choose total work as the LCM of the days, to avoid fractions.

**Harder example.** A takes 12 days, B 15 and C 20. Work = 60 units, rates 5, 4 and 3. Together 12 a day: 5 days.
## Efficiency method
Time varies inversely with efficiency. If A is 25% more efficient than B, then time ratio A : B is 4 : 5.

**Harder example.** A takes 20 days. B is 25% more efficient. B takes 16 days.
## Work & wages
Wages follow the amount of work done, not the time spent. Rates give the ratio.

**Harder example.** A, B take 10 and 15 days and earn ₹5,000 together, with C helping to finish in 5 days. Work shares: A 1/2, B 1/3, C 1/6. C gets ₹833.33.
## Pipes & cisterns
Filling rates are positive, and leaks are negative. A leak's time: if a pipe takes a hours, and b hours with the leak, the leak alone empties in ab/(b − a).

**Harder example.** A pipe takes 8 h; with a leak it takes 10 h. The leak alone takes 8 × 10 ÷ 2 = 40 h.
# Time, Speed & Distance
## Basic formula
km/h to m/s: × 5/18. If the speed ratio is a : b for equal distance, then the time ratio is b : a.

**Harder example.** Walking at 3/4 of usual speed, a man is 20 min late. Time ratio is 4 : 3, so 1 part = 20 min and usual time = 60 min.
## Relative speed
Same direction: subtract. Opposite directions: add.

**Harder example.** A leaves at 40 km/h. B leaves 2 hours later, at 60 km/h. The gap is 80 km, closing at 20 km/h: 4 hours.
## Trains
Passing a pole or person: distance = train length. Passing a bridge or platform: length + its length. Passing a train: sum of lengths with relative speed.

**Harder example.** A train passes a man in 10 s and a 200 m platform in 20 s. In 10 extra seconds, it covers 200 m, so speed = 20 m/s and length = 200 m.
## Boats & streams
Downstream = b + s, upstream = b − s. b = (D + U)/2, s = (D − U)/2.

**Harder example.** 30 km downstream in 2 h and upstream in 3 h: D = 15, U = 10, so boat 12.5 and stream 2.5.
## Races & games
"A beats B by x m" means that when A has run the full distance, B has run x less. For a race of d m with leads a and b, A beats C by a + b − ab/d.

**Harder example.** 100 m: A beats B by 10 and B beats C by 10. A beats C by 10 + 10 − 1 = 19 m.
## Circular tracks
Opposite directions: first meet after L/(a + b). Same direction: L/|a − b|. At the start again: the LCM of lap times.

**Trap:** meeting anywhere is different from meeting at the starting point.
## Escalators
Steps = (walker's speed ± escalator's speed) × time. With two trips at different speeds, solve for escalator speed and steps.

**Harder example.** Walking 1 step/s up takes 30 s; 2 steps/s takes 20 s. (1 + e)30 = (2 + e)20 gives e = 1, so 60 steps.
# Algebra
## Linear equations
Consistency of a₁x + b₁y = c₁ and a₂x + b₂y = c₂: unique if a₁/a₂ ≠ b₁/b₂; none if a₁/a₂ = b₁/b₂ ≠ c₁/c₂; infinite if all three are equal.

**Harder example.** For what k do x + 2y = 3 and 2x + ky = 7 have no solution? 1/2 = 2/k gives k = 4, and 3/7 differs.
## Quadratic equations
Roots: (−b ± √D)/2a, with D = b² − 4ac. Sum = −b/a; product = c/a.

**Harder example.** If the roots are α and β of x² − 5x + 6, then α² + β² = (α + β)² − 2αβ = 25 − 12 = 13.
## Inequalities
Multiplying or dividing by a negative flips the sign. For (x − a)(x − b) < 0 with a < b, x is between a and b. For > 0, x is outside.

**Trap:** do not multiply by an unknown whose sign you don't know.
## Progressions (AP, GP, HP)
| | nth term | Sum |
|---|---|---|
| AP | a + (n − 1)d | n/2 × (2a + (n − 1)d) |
| GP | arⁿ⁻¹ | a(rⁿ − 1)/(r − 1); infinite: a/(1 − r) for \|r\| < 1 |

AM ≥ GM ≥ HM, and for two numbers, GM² = AM × HM.

**Harder example.** The infinite sum of 1 + 1/2 + 1/4 + ... = 2.
## Functions
f(g(x)) means apply g first. The inverse undoes f. Even function: f(−x) = f(x). Odd: f(−x) = −f(x).

**Harder example.** f(x) = 2x + 3, then f⁻¹(x) = (x − 3)/2, so f⁻¹(11) = 4.
# Permutation & Combination
## Fundamental counting principle
"And" multiplies, "or" adds. Fill the most restricted position first.

**Harder example.** 4-digit even numbers from 1 to 6, no repeats: last digit 3 ways, then 5 × 4 × 3 = 180.
## Permutations
nPr = n!/(n − r)!. With repeats: n!/(p! q! ...). Vowels together: treat them as one unit. Then multiply by their internal arrangements.

**Harder example.** LEADER: 6!/2! = 360 in all. Vowels E, A, E together: units L, D, R and the block make 4! = 24, times 3!/2! = 3, giving 72.
## Combinations
nCr = n!/(r!(n − r)!). nCr = nC(n − r). "At least one" = total − none.

**Harder example.** Committees of 3 from 5 men and 4 women, with at least one woman: 9C3 − 5C3 = 84 − 10 = 74.
## Circular permutations
(n − 1)! around a table; (n − 1)!/2 if clockwise and anticlockwise count as one, as with a necklace.

**Trap:** a fixed reference, such as numbered seats, turns it back into a line, and n! applies.
## Distribution problems
| Items | Boxes | Ways |
|---|---|---|
| Identical | Different, empty allowed | C(n + k − 1, k − 1) |
| Identical | Different, none empty | C(n − 1, k − 1) |
| Different | Different | kⁿ |
| Different, groups of a, b, c | Unlabelled sizes differ | n!/(a! b! c!) |

**Harder example.** x + y + z = 10, with non-negative integers: C(12, 2) = 66.
# Probability
## Basic probability
P = favourable ÷ total. P(not A) = 1 − P(A). Use complements for "at least".

**Harder example.** At least one head in 3 tosses: 1 − 1/8 = 7/8.

**Trap:** outcomes must be equally likely. "2 heads, 1 head or 0 heads" are not.
## Independent & dependent events
Independent: P(A and B) = P(A)P(B). Mutually exclusive: P(A or B) = P(A) + P(B). In general: P(A or B) = P(A) + P(B) − P(A and B). Without replacement, the second draw's total falls.

**Trap:** mutually exclusive events are not independent: if one occurs, the other cannot.
## Conditional probability
P(A | B) = P(A and B)/P(B). Restrict the sample space to B. Bayes: P(A | B) = P(B | A)P(A)/P(B).

**Harder example.** A test is 90% accurate, and 1% of people have the disease. A positive result: 0.009 true, 0.099 false. So P(disease | positive) ≈ 8.3%.
## Cards, dice & coins
52 cards: 26 red, 26 black, 13 per suit, 12 face cards (6 red), 4 aces. Two dice: 36 outcomes. Sums peak at 7 (6 ways). n coins: 2ⁿ outcomes.

**Trap:** kings are also face cards, so "a king or a face card" means 12, not 16.
# Geometry
## Lines & angles
Vertically opposite angles are equal. On parallel lines, corresponding and alternate angles are equal, and co-interior ones add to 180°.

**Harder example.** Angle bisectors of co-interior angles meet at 90°, since half of 180° is 90°.
## Triangles
Sum of two sides exceeds the third. Pythagorean triples: 3-4-5, 5-12-13, 8-15-17, 7-24-25. The median to the hypotenuse is half of it. Similar triangles: areas go as the square of sides. Exterior angle = sum of the two remote interior angles.

| Centre | Meets at | Note |
|---|---|---|
| Centroid | Medians | Divides each 2 : 1 |
| Incentre | Angle bisectors | Inside always |
| Circumcentre | Perpendicular bisectors | Midpoint of hypotenuse in a right triangle |
| Orthocentre | Altitudes | At the right-angle vertex in a right triangle |

Equilateral: area √3a²/4, height √3a/2.
## Circles
Angle at centre = 2 × angle at circumference. Angle in a semicircle = 90°. Tangent ⟂ radius. Tangents from one point are equal. Cyclic quadrilateral: opposite angles add to 180°. Chords: PA × PB = PC × PD.

**Harder example.** Two circles of radius 5 and 3, with centres 10 apart: direct common tangent = √(100 − 4) = √96.
## Quadrilaterals & polygons
Interior sum: (n − 2) × 180°. Exterior sum: 360°. Diagonals: n(n − 3)/2.

| Shape | Area |
|---|---|
| Parallelogram | base × height |
| Rhombus | ½ d₁d₂ |
| Trapezium | ½(a + b)h |

**Harder example.** A regular polygon with interior angle 150° has exterior angle 30°, so 12 sides.
## Coordinate geometry
Distance: √(Δx² + Δy²). Slope: Δy/Δx. Parallel lines: equal slopes. Perpendicular: slopes multiply to −1. Section: (mx₂ + nx₁)/(m + n). Triangle centroid: average of vertices. Line: y = mx + c.

**Harder example.** Line through (1, 2) and (3, 8): slope 3, so y = 3x − 1.
# Mensuration
## 2D figures: area & perimeter
| Figure | Area | Perimeter |
|---|---|---|
| Rectangle | lb | 2(l + b) |
| Square | a² or d²/2 | 4a |
| Triangle (Heron) | √(s(s−a)(s−b)(s−c)) | a + b + c |
| Circle | πr² | 2πr |
| Sector | θ/360 × πr² | Arc: θ/360 × 2πr |

**Harder example.** A path 2 m wide runs around a 20 × 10 m garden. Area = 24 × 14 − 200 = 136 m².

**Trap:** if each side grows x%, area grows by 2x + x²/100 %.
## 3D figures: surface area & volume
| Solid | Volume | Surface |
|---|---|---|
| Cuboid | lbh | 2(lb + bh + hl) |
| Cube | a³ | 6a² |
| Cylinder | πr²h | Curved 2πrh; total 2πr(r + h) |
| Cone | ⅓πr²h | Curved πrl; l = √(r² + h²) |
| Sphere | 4/3 πr³ | 4πr² |
| Hemisphere | 2/3 πr³ | Total 3πr² |

**Harder example.** A sphere of radius 6 is melted into cones of radius 3 and height 4. 288π ÷ 12π = 24 cones.

**Trap:** melting keeps the volume, not the surface area.
# Trigonometry
## Ratios & identities
| | 0° | 30° | 45° | 60° | 90° |
|---|---|---|---|---|---|
| sin | 0 | 1/2 | 1/√2 | √3/2 | 1 |
| cos | 1 | √3/2 | 1/√2 | 1/2 | 0 |
| tan | 0 | 1/√3 | 1 | √3 | undefined |

sin²θ + cos²θ = 1; 1 + tan²θ = sec²θ; 1 + cot²θ = cosec²θ. sin(90° − θ) = cos θ.

**Harder example.** If sin θ + cos θ = √2, squaring gives 1 + 2 sin θ cos θ = 2, so sin θ cos θ = 1/2.
## Heights & distances
Elevation looks up, and depression looks down, and they are equal for two points across a horizontal. Draw the right triangle, and use tan for height and distance.

**Harder example.** The elevation of a tower's top changes from 30° to 60° after walking 20 m closer. h = 20 × tan 30° × tan 60° ÷ (tan 60° − tan 30°) = 20 ÷ (2/√3) = 10√3 m.
# Calendar & Clock
## Calendar
Odd days: an ordinary year has 1, a leap year 2. 100 years = 5; 200 = 3; 300 = 1; 400 = 0. Months: Jan 3, Feb 0 or 1, Mar 3, Apr 2, May 3, Jun 2, Jul 3, Aug 3, Sep 2, Oct 3, Nov 2, Dec 3.

The calendar repeats after 6 or 11 years for most years, and after 28 for leap years.

**Trap:** century years are leap years only if divisible by 400: 1900 is not.
## Clock angles
Angle = |30H − 5.5M|; take 360 minus this if it's over 180. Hands coincide every 65 5/11 minutes, 11 times in 12 hours and 22 times in a day. They are at right angles 44 times a day, and straight 22 times.

**Harder example.** At 3:40: |90 − 220| = 130°.
## Fast & slow clocks
A clock gaining g minutes in T hours shows T + g/60 hours in T true hours. Work out the proportion. To show the right time again, a clock must gain or lose 12 hours in total.

**Harder example.** A clock gains 5 min per hour. If it shows 1 p.m. correctly, then at 4 p.m. true time, it shows 4:15.
# Set Theory & Venn Diagrams
## Union, intersection & complement
n(A ∪ B) = n(A) + n(B) − n(A ∩ B). De Morgan: (A ∪ B)′ = A′ ∩ B′. Subsets: 2ⁿ; proper subsets: 2ⁿ − 1.

**Trap:** the empty set is a subset of every set.
## Overlapping sets
Three sets: n(A ∪ B ∪ C) = sum of singles − sum of pairs + all three. **Exactly two** = sum of pairs − 3 × all three. **Exactly one** = singles − 2 × pairs + 3 × all three.

**Harder example.** Maximum overlap of 70% and 60% is 60%; the minimum is 70 + 60 − 100 = 30%.
# Other Quantitative Topics
## Number series
Test in order: differences, second differences, ratios, squares and cubes, primes, alternate terms, then combinations such as ×2 + 1.

**Harder example.** 2, 6, 12, 20, 30: differences go 4, 6, 8, 10. The terms equal n(n + 1), so the next is 42.
## Stocks, shares & banker's discount
Dividend is on face value. Yield = dividend ÷ market price. Banker's discount is SI on the face value. True discount: FV × RT/(100 + RT). BD − TD = SI on TD.

**Harder example.** A ₹1,300 bill due in 2 years at 15%: TD = 1300 × 30/130 = ₹300; BD = 1300 × 30/100 = ₹390.
## Data sufficiency
You don't need the answer, only whether one could be found. Test each statement alone first, and then together. Look for a hidden fact: "x is an integer" or "both are positive" can decide it.

**Trap:** don't use outside assumptions: unless it is said, a number need not be an integer or positive.
