@part gate-calculus | Calculus | math
## Limits

lim f(x) as x → a is the value f(x) approaches. It exists only if the **left-hand and right-hand limits agree**. The value of f at a does not matter, and f need not even be defined there.

### Standard limits to memorise

| Limit (x → 0 unless stated) | Value |
|---|---|
| sin x / x, tan x / x | 1 |
| (1 − cos x) / x² | 1/2 |
| (eˣ − 1) / x, ln(1 + x) / x | 1 |
| (aˣ − 1) / x | ln a |
| (1 + x)^(1/x) | e |
| (1 + a/x)ˣ as x → ∞ | eᵃ |
| x ln x as x → 0⁺ | 0 |
| xⁿ / eˣ as x → ∞ | 0 for any n |
| sin(1/x) | does **not** exist |
| x sin(1/x), x² cos(1/x) | 0 (squeezed between ±\|x\|) |

### Techniques

1. **Direct substitution** whenever it gives a finite number.
2. **Factor and cancel** for 0/0 in rational functions: (x³ − 1)/(x² − 1) = (x² + x + 1)/(x + 1) → 3/2 as x → 1.
3. **L'Hôpital's rule** for 0/0 or ∞/∞: differentiate numerator and denominator separately and try again. Other forms (0·∞, ∞ − ∞, 0⁰, 1^∞, ∞⁰) are first rewritten into a fraction, often by taking the logarithm.
4. **Series expansion** is usually fastest for hard 0/0 limits: replace each function by its first few Maclaurin terms.
5. **Squeeze theorem:** if g ≤ f ≤ h and g, h share a limit L, f has limit L.
6. **Limits at infinity of rational functions:** compare the highest powers. Equal degrees give the ratio of leading coefficients, so (3x² + 2x)/(5x² − 1) → 3/5.

!cheat Limit cheat codes ::
- **Expand, don't differentiate.** For (tan x − sin x)/x³ use tan x ≈ x + x³/3 and sin x ≈ x − x³/6. The difference is x³/2, so the limit is 1/2. Series beat repeated L'Hôpital.
- **(eˣ − 1 − x)/x²** → 1/2, because eˣ = 1 + x + x²/2 + …
- **(sin x − x)/x³** → −1/6, from sin x = x − x³/6 + ….
- **1^∞ form:** if f → 1 and g → ∞, the limit is e^(lim g·(f − 1)). Check: (1 + 2/x)ˣ gives e^(x · 2/x) = e².
- **Absolute value quotient:** |x|/x is +1 from the right and −1 from the left, so the two-sided limit at 0 does not exist.
- **Oscillation without damping** (like sin(1/x)) means no limit. Multiply by x or x² and it dies out.
!end

## Continuity and differentiability

A function is **continuous at a** if lim f(x) = f(a): the limit exists, the value exists, and they are equal. Types of failure:

| Discontinuity | Cause |
|---|---|
| Removable | limit exists but differs from f(a), or f(a) is undefined |
| Jump | left and right limits differ |
| Infinite | the function blows up (like 1/x at 0) |
| Oscillating | no limit (like sin(1/x)) |

**Differentiable at a** means the limit of (f(a + h) − f(a)) / h exists, i.e. the left and right derivatives agree.

- **Differentiable ⇒ continuous.** The converse is false: |x| is continuous at 0 but has a corner there, so no derivative.
- A function is not differentiable at corners, cusps, vertical tangents and discontinuities.

### Examples worth knowing

| Function | At x = 0 |
|---|---|
| \|x\| | continuous, **not** differentiable |
| x\|x\| | differentiable, f′(0) = 0 |
| x² sin(1/x), with f(0) = 0 | differentiable, f′(0) = 0, but f′ is **not** continuous at 0 |
| sin x / x with f(0) = c | continuous exactly when c = 1 |

### Matching a piecewise function

To make f continuous at the join, equate the two formulas there. To make it differentiable, **also equate their derivatives** there. For f(x) = x² (x ≤ 1), ax + b (x > 1): continuity gives a + b = 1, differentiability gives a = 2, so b = −1.

### Standard differentiation

| f | f′ |
|---|---|
| xⁿ | n xⁿ⁻¹ |
| eˣ, aˣ | eˣ, aˣ ln a |
| ln x | 1/x |
| sin x, cos x, tan x | cos x, −sin x, sec² x |
| uv | u′v + uv′ |
| u/v | (u′v − uv′) / v² |
| f(g(x)) | f′(g(x)) g′(x) |
| xˣ | xˣ (1 + ln x), by logarithmic differentiation |

For implicit curves, differentiate both sides with respect to x. x² + y² = 25 gives 2x + 2y y′ = 0, so y′ = −x/y, which is −3/4 at (3, 4).

!cheat Continuity and differentiability cheat codes ::
- **Continuity needs one equation; differentiability needs two** (value and slope).
- **IVT:** a function continuous on [a, b] takes every value between f(a) and f(b). Use it to prove a root exists when the signs differ.
- **Corner test:** compute the left and right derivative separately. If they differ, it is a corner.
- **Power of |x|:** |x|ⁿ with n > 1 is differentiable at 0; |x| (n = 1) is not.
- **Derivative of a^x type:** take ln first. y = xˣ gives ln y = x ln x, so y′/y = ln x + 1.
!end

## Maxima and minima

A **critical point** of f is a point where f′ = 0 or f′ does not exist. Local extrema occur only at critical points.

### Tests

- **First derivative test:** if f′ changes from + to − at c, it is a local **maximum**; from − to +, a local **minimum**; no sign change, neither.
- **Second derivative test** (when f′(c) = 0): f″(c) > 0 gives a minimum, f″(c) < 0 a maximum, and f″(c) = 0 is **inconclusive** (x³ has an inflection point, x⁴ has a minimum, both at 0).
- A **point of inflection** is where the curvature changes sign (f″ changes sign).

### Absolute extrema on a closed interval [a, b]

By the extreme value theorem a continuous function has an absolute maximum and minimum there. Evaluate f at the endpoints and at every critical point inside, then compare. Example: f(x) = 2x³ − 9x² + 12x on [0, 3]. f′ = 6(x − 1)(x − 2). Values: f(0) = 0, f(1) = 5, f(2) = 4, f(3) = 9. The maximum is 9 at the endpoint x = 3.

### Functions of two variables

Set both partial derivatives to zero. For f(x, y) = x² + y² − 2x − 4y + 10, fₓ = 2x − 2 = 0 and f_y = 2y − 4 = 0 give (1, 2), where f = 5. With r = fₓₓ, s = fₓᵧ, t = f_yy: if rt − s² > 0 and r > 0 it is a minimum; if rt − s² > 0 and r < 0 a maximum; if rt − s² < 0 a saddle point.

!cheat Optimisation cheat codes ::
- **Check endpoints.** The maximum on a closed interval is often at an endpoint, not at the critical point.
- **Rectangle with a fixed perimeter** has its largest area when it is a square. Perimeter 20 → area 25.
- **AM–GM:** for x > 0, x + 1/x ≥ 2 with equality at x = 1. sin x + cos x has maximum √2 (it equals √2 sin(x + π/4)).
- **f′ ≥ 0 everywhere (like (x − 1)²·3)** means no local extremum at all, even where f′ = 0. A touch of zero slope that does not change sign is not an extremum.
- **Even power at a zero of f′:** (x − 1)² keeps the same sign, so it gives no extremum; an odd power changes sign.
!end

## Mean value theorems and Taylor series

### Rolle's theorem

If f is continuous on [a, b], differentiable on (a, b) and f(a) = f(b), then f′(c) = 0 for some c in (a, b). It fails if any condition fails: |x| on [−1, 1] is not differentiable at 0, and 1/x on [−1, 1] is not even continuous.

### Lagrange's mean value theorem (MVT)

If f is continuous on [a, b] and differentiable on (a, b), there is c with

**f′(c) = (f(b) − f(a)) / (b − a).**

Geometrically, some tangent is parallel to the chord. For f(x) = x² on [1, 3] the slope is (9 − 1)/2 = 4, and f′(c) = 2c = 4 gives c = 2. For x³ on [0, 2], 3c² = 4 gives c = 2/√3.

Consequences: if f′ = 0 on an interval, f is constant. If f′ > 0, f is increasing. Cauchy's MVT is the ratio form (f(b) − f(a)) / (g(b) − g(a)) = f′(c) / g′(c).

### Maclaurin series

| Function | Series |
|---|---|
| eˣ | 1 + x + x²/2! + x³/3! + … |
| sin x | x − x³/3! + x⁵/5! − … |
| cos x | 1 − x²/2! + x⁴/4! − … |
| ln(1 + x) | x − x²/2 + x³/3 − … (for \|x\| < 1) |
| 1/(1 − x) | 1 + x + x² + … (for \|x\| < 1) |
| (1 + x)ⁿ | 1 + nx + n(n − 1)x²/2! + … |

The coefficient of xᵏ in a Maclaurin series is f⁽ᵏ⁾(0) / k!. So e²ˣ has x³ coefficient 2³ / 3! = 4/3.

!cheat MVT and series cheat codes ::
- **Rolle check list:** continuous, differentiable inside, equal end values. If any fails, Rolle's theorem cannot be applied (the conclusion may still happen to be true).
- **MVT point:** solve f′(c) = (f(b) − f(a))/(b − a) and keep only roots inside (a, b).
- **Series substitute:** to expand e²ˣ, replace x by 2x in the series for eˣ. To expand x² eˣ, multiply the series by x².
- **Coefficient of x² in ln(1 + x)** is −1/2. The signs alternate.
- **Sign of f′ = (x − 1)²(x − 2):** negative for x < 2 (except at 1), positive for x > 2. So only x = 2 is a local minimum; x = 1 is not an extremum.
!end

## Integration

### Basic antiderivatives

| ∫ f dx | Result (+ C) |
|---|---|
| xⁿ (n ≠ −1) | xⁿ⁺¹ / (n + 1) |
| 1/x | ln \|x\| |
| eˣ, aˣ | eˣ, aˣ / ln a |
| sin x, cos x | −cos x, sin x |
| sec² x | tan x |
| 1/(1 + x²) | tan⁻¹ x |
| 1/√(1 − x²) | sin⁻¹ x |

### Methods

- **Substitution:** let u = g(x) and replace g′(x) dx by du. Change the limits too in a definite integral.
- **By parts:** ∫ u dv = uv − ∫ v du. Choose u in the order Logarithm, Inverse trig, Algebraic, Trig, Exponential. Example: ∫₀¹ x eˣ dx = [x eˣ − eˣ]₀¹ = 1.
- **Standard parts result:** ∫ ln x dx = x ln x − x.

### Definite integrals: properties and shortcuts

| Property | Statement |
|---|---|
| Odd function | ∫ from −a to a of f = 0 |
| Even function | ∫ from −a to a of f = 2 ∫ from 0 to a of f |
| Reflection ("King") | ∫ₐᵇ f(x) dx = ∫ₐᵇ f(a + b − x) dx |
| Wallis | ∫₀^(π/2) sinⁿ x dx = ∫₀^(π/2) cosⁿ x dx: 1 (n=1), π/4 (n=2), 2/3 (n=3), 3π/16 (n=4) |
| Gamma | ∫₀^∞ xⁿ e⁻ˣ dx = n! |
| Beta | ∫₀¹ xᵐ (1 − x)ⁿ dx = m! n! / (m + n + 1)! |
| Average value | (1/(b − a)) ∫ₐᵇ f |
| Area between curves | ∫ (top − bottom) |
| Leibniz | d/dx ∫ from a to g(x) of f(t) dt = f(g(x)) g′(x) |

### Improper integrals

- ∫₁^∞ x⁻ᵖ dx converges exactly when **p > 1** (value 1/(p − 1)).
- ∫₀¹ x⁻ᵖ dx converges exactly when **p < 1**.
- So ∫₁^∞ 1/x diverges (p = 1), ∫₁^∞ 1/√x diverges, ∫₁^∞ 1/x² = 1, and ∫₀¹ 1/x diverges.

!cheat Integration cheat codes ::
- **Spot symmetry first:** ∫ from −π to π of x³ cos x or sin⁵ x is 0 because the integrand is odd.
- **King's property:** ∫₀^(π/2) sin x / (sin x + cos x) dx equals the same integral with sin and cos swapped. Adding gives π/2, so each is π/4. Use it whenever the integrand has a sum of "partner" functions in the denominator.
- **Wallis in seconds:** for even n multiply (n−1)/n · (n−3)/(n−2) … by π/2; for odd n multiply by 1 at the end. ∫₀^(π/2) sin³ x = (2/3)·1 = 2/3.
- **Gamma shortcut:** ∫₀^∞ x³ e⁻ˣ dx = 3! = 6. Replace x by ax and divide by aⁿ⁺¹.
- **|x − c| integrals:** split at c. ∫₀² |x − 1| dx = 1/2 + 1/2 = 1.
- **Area:** find the intersection points first. y = x² and y = x meet at 0 and 1, and the area is ∫₀¹ (x − x²) dx = 1/6.
- **Average of x² over [0, 3]** = (1/3) · (27/3) = 3.
!end

## Cheat sheet: Calculus on one page

| Topic | Fact |
|---|---|
| Standard limits | sin x/x → 1, (1 − cos x)/x² → 1/2, (eˣ − 1)/x → 1, (1 + 1/x)ˣ → e |
| 1^∞ | exp(lim g·(f − 1)) |
| Continuity | one equation: equal at the join |
| Differentiability | two equations: value and slope equal |
| Differentiable ⇒ continuous | converse false (\|x\|) |
| Local extremum | f′ changes sign (first test), f″ ≠ 0 (second test) |
| Closed interval | compare endpoints and critical points |
| Rolle | f(a) = f(b) ⇒ f′(c) = 0 |
| MVT | f′(c) = (f(b) − f(a)) / (b − a) |
| Maclaurin | eˣ, sin x, cos x, ln(1 + x), 1/(1 − x) |
| Odd / even integrals | 0 / 2 ∫₀ᵃ |
| Wallis | ∫₀^(π/2) sin² = π/4, sin³ = 2/3 |
| Gamma | ∫₀^∞ xⁿ e⁻ˣ = n! |
| p-test | ∫₁^∞ x⁻ᵖ converges iff p > 1 |

??  Why is f(x) = |x| continuous but not differentiable at 0?
=> lim |x| = 0 = f(0), so it is continuous. The right derivative is +1 and the left derivative is −1; they differ, so the derivative does not exist (a corner).
??  State the conditions of Rolle's theorem and say why it fails for f(x) = |x| on [−1, 1].
=> f must be continuous on [a, b], differentiable on (a, b) and f(a) = f(b). For |x| on [−1, 1] the end values are equal and f is continuous, but f is not differentiable at 0, so the conclusion f′(c) = 0 cannot be guaranteed (and there is no such c).
??  Evaluate ∫₀^(π/2) sin x / (sin x + cos x) dx.
=> Let I be the integral. Replacing x by π/2 − x gives I = ∫ cos x / (sin x + cos x) dx. Adding the two gives 2I = ∫₀^(π/2) 1 dx = π/2, so I = π/4.
??  Does ∫₁^∞ 1/x^1.5 dx converge?
=> Yes: p = 1.5 > 1, and the value is 1/(p − 1) = 2. The integral ∫₁^∞ 1/x dx (p = 1) diverges.
