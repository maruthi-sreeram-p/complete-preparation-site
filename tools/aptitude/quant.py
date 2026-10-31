"""Quantitative aptitude: templates for every sub-topic of the guide's Part 1."""
import math
from math import comb, factorial, gcd, perm

from core import F, Q, T, fmt


def lcm(a, b):
    return a * b // gcd(a, b)


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def n_factors(n):
    return sum(1 for d in range(1, n + 1) if n % d == 0)


# =================================================================== Number System
C = "Number System"


@T(C, "Types of numbers")
def _(r):
    a = r.randint(2, 90)
    b = a + r.randint(10, 40)
    n = sum(is_prime(x) for x in range(a, b + 1))
    return Q(f"How many prime numbers are there from {a} to {b}, both included?", n,
             f"The primes are {', '.join(str(x) for x in range(a, b + 1) if is_prime(x)) or 'none'}, so the count is {n}.")


@T(C, "Types of numbers")
def _(r):
    n = r.randint(5, 150)
    kind = r.choice(["natural", "odd", "even"])
    ans = {"natural": n * (n + 1) // 2, "odd": n * n, "even": n * (n + 1)}[kind]
    rule = {"natural": "n(n+1)/2", "odd": "n²", "even": "n(n+1)"}[kind]
    return Q(f"What is the sum of the first {n} {kind} numbers?", ans, f"Use {rule} with n = {n}, which gives {ans}.",
             [n * n, n * (n + 1), n * (n + 1) // 2, n * (n - 1)])


@T(C, "Types of numbers")
def _(r):
    p = r.choice([x for x in range(30, 400) if is_prime(x)])
    bad = []
    while len(bad) < 3:
        x = r.randint(30, 400) | 1
        if not is_prime(x) and x % 5 and x not in bad:
            bad.append(x)
    return Q("Which of these is a prime number?", p, f"{p} has no divisor up to √{p}. Each other option is composite.", bad)


@T(C, "Divisibility rules")
def _(r):
    d = r.choice([3, 9])
    a, b, c = r.randint(1, 9), r.randint(0, 9), r.randint(0, 9)
    s = a + b + c
    ans = (d - s % d) % d
    return Q(f"Find the smallest digit x for which the number {a}{b}x{c} is divisible by {d}.", ans,
             f"The digit sum is {s} + x. The smallest x making it a multiple of {d} is {ans}.", [(ans + i) % 10 for i in (1, 2, 4, 5, 7)])


@T(C, "Divisibility rules")
def _(r):
    q = r.randint(100, 899)
    n = q * 11
    wrong = []
    while len(wrong) < 3:
        x = n + r.randint(1, 10)
        if x % 11 and x not in wrong:
            wrong.append(x)
    return Q("Which of these numbers is divisible by 11?", n,
             f"{n} = 11 × {q}. For 11, the difference of the digit sums at odd and even places must be 0 or a multiple of 11.", wrong)


@T(C, "Divisibility rules")
def _(r):
    d = r.choice([4, 8, 6, 7, 12, 13])
    n = r.randint(100, 9999) * d + r.randint(1, d - 1)
    ans = d - n % d
    return Q(f"What is the smallest number that must be added to {n} to make it exactly divisible by {d}?", ans,
             f"{n} leaves remainder {n % d} when divided by {d}, so add {ans}" + ".")


@T(C, "HCF & LCM")
def _(r):
    h = r.randint(2, 30)
    a, b = r.randint(2, 15), r.randint(2, 15)
    while gcd(a, b) != 1:
        b = r.randint(2, 15)
    return Q(f"Find the HCF of {h * a} and {h * b}.", h, f"{h * a} = {h} × {a} and {h * b} = {h} × {b}, and {a}, {b} share no factor, so the HCF is {h}.")


@T(C, "HCF & LCM")
def _(r):
    a, b, c = r.sample(range(4, 40), 3)
    ans = lcm(lcm(a, b), c)
    return Q(f"Find the LCM of {a}, {b} and {c}.", ans, f"LCM({a}, {b}) = {lcm(a, b)}, and the LCM of that with {c} is {ans}.")


@T(C, "HCF & LCM")
def _(r):
    h = r.randint(2, 20)
    a, b = r.randint(2, 20), r.randint(2, 20)
    while gcd(a, b) != 1 or a == b:
        b = r.randint(2, 20)
    x, y, l = h * a, h * b, h * a * b
    return Q(f"The HCF of two numbers is {h} and their LCM is {l}. If one number is {x}, what is the other?", y,
             f"HCF × LCM = product of the numbers. Other = {h} × {l} ÷ {x} = {y}.")


@T(C, "HCF & LCM")
def _(r):
    a, b, c = r.sample([6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 30], 3)
    k = r.randint(1, 5)
    ans = lcm(lcm(a, b), c) + k
    return Q(f"What is the smallest number that leaves remainder {k} when divided by each of {a}, {b} and {c}?", ans,
             f"LCM({a}, {b}, {c}) = {ans - k}. Add the common remainder: {ans - k} + {k} = {ans}.", [ans - k, ans + k, ans - 1 if k != 1 else ans + 2 * k])


@T(C, "Factors & multiples")
def _(r):
    a, b, c = r.randint(1, 6), r.randint(1, 5), r.randint(0, 3)
    n = 2 ** a * 3 ** b * 5 ** c
    ans = (a + 1) * (b + 1) * (c + 1)
    return Q(f"How many factors does {n} have?", ans,
             f"{n} = 2^{a} × 3^{b} × 5^{c}. The count is ({a}+1)({b}+1)({c}+1) = {ans}.")


@T(C, "Factors & multiples")
def _(r):
    n = r.choice([12, 18, 20, 24, 28, 30, 36, 40, 42, 45, 48, 50, 54, 56, 60, 63, 64, 70, 72, 75, 80, 84, 90, 96, 98, 100, 108, 112, 120, 126, 135, 144, 150, 180, 200, 210, 240, 252, 300, 360])
    ans = sum(d for d in range(1, n + 1) if n % d == 0)
    return Q(f"What is the sum of all the factors of {n}, including 1 and {n}?", ans, f"Adding every divisor of {n} gives {ans}.", [ans - n, ans + n, ans - 1])


@T(C, "Factors & multiples")
def _(r):
    d = r.randint(3, 19)
    lo = r.randint(10, 300)
    hi = lo + r.randint(100, 900)
    ans = hi // d - (lo - 1) // d
    return Q(f"How many multiples of {d} are there from {lo} to {hi}, both included?", ans,
             f"⌊{hi}/{d}⌋ − ⌊{lo - 1}/{d}⌋ = {hi // d} − {(lo - 1) // d} = {ans}.")


@T(C, "Remainders")
def _(r):
    a, n, m = r.randint(2, 19), r.randint(5, 60), r.choice([3, 5, 7, 9, 11, 13])
    while a % m == 0:
        a = r.randint(2, 19)
    ans = pow(a, n, m)
    return Q(f"Find the remainder when {a}^{n} is divided by {m}.", ans, f"Remainders of powers of {a} modulo {m} repeat; computing gives {a}^{n} mod {m} = {ans}.",
             [x for x in range(m) if x != ans])


@T(C, "Remainders")
def _(r):
    m = r.choice([12, 15, 18, 20, 24, 28, 30, 36, 42, 45, 48, 60])
    d = r.choice([x for x in range(2, m) if m % x == 0 and x > 2])
    k = r.randint(5, 80)
    rem = r.randint(1, m - 1)
    ans = rem % d
    return Q(f"A number leaves remainder {rem} when divided by {m}. What is the remainder when the same number is divided by {d}?", ans,
             f"{d} divides {m}, so the remainder is {rem} mod {d} = {ans}.", [x for x in range(d + 3) if x != ans])


@T(C, "Remainders")
def _(r):
    m = r.randint(4, 17)
    xs = r.sample(range(11, 99), 3)
    ans = (xs[0] * xs[1] * xs[2]) % m
    return Q(f"Find the remainder when {xs[0]} × {xs[1]} × {xs[2]} is divided by {m}.", ans,
             f"Reduce each: {xs[0] % m} × {xs[1] % m} × {xs[2] % m}, then take the remainder modulo {m}: {ans}.", [x for x in range(m + 2) if x != ans])


@T(C, "Unit digit & cyclicity")
def _(r):
    a, n = r.randint(2, 99), r.randint(11, 999)
    ans = pow(a, n, 10)
    return Q(f"What is the unit digit of {a}^{n}?", ans, f"Unit digit depends only on {a % 10} and the power cycle (at most 4). {a % 10}^{n} ends in {ans}.", [x for x in range(10) if x != ans])


@T(C, "Unit digit & cyclicity")
def _(r):
    a, b, m, n = r.randint(2, 99), r.randint(2, 99), r.randint(11, 200), r.randint(11, 200)
    ans = pow(a, m, 10) * pow(b, n, 10) % 10
    return Q(f"What is the unit digit of {a}^{m} × {b}^{n}?", ans, f"{a}^{m} ends in {pow(a, m, 10)} and {b}^{n} ends in {pow(b, n, 10)}. Their product ends in {ans}.", [x for x in range(10) if x != ans])


@T(C, "Factorials & trailing zeros")
def _(r):
    n = r.randint(20, 2000)
    ans, p = 0, 5
    while p <= n:
        ans += n // p
        p *= 5
    return Q(f"How many trailing zeros does {n}! have?", ans, f"Count factors of 5: ⌊{n}/5⌋ + ⌊{n}/25⌋ + ⌊{n}/125⌋ + ... = {ans}.")


@T(C, "Factorials & trailing zeros")
def _(r):
    n, p = r.randint(20, 300), r.choice([2, 3, 5, 7])
    ans, q = 0, p
    while q <= n:
        ans += n // q
        q *= p
    return Q(f"What is the highest power of {p} that divides {n}!?", ans, f"Legendre's formula: add ⌊{n}/{p}⌋, ⌊{n}/{p}²⌋ and so on, which gives {ans}.")


@T(C, "Number base systems")
def _(r):
    n = r.randint(9, 255)
    return Q(f"Convert the binary number {bin(n)[2:]} to decimal.", n, f"Add the place values of the 1 bits: the value is {n}.")


@T(C, "Number base systems")
def _(r):
    n, b = r.randint(9, 500), r.choice([2, 3, 4, 5, 8])
    def to_base(x):
        s = ""
        while x:
            s = str(x % b) + s
            x //= b
        return s
    ans = to_base(n)
    wrong = [to_base(n + i) for i in (1, 2, 3, -1) if n + i > 0]
    return Q(f"Write the decimal number {n} in base {b}.", ans, f"Divide repeatedly by {b} and read the remainders upward: {ans}.", wrong)


@T(C, "Number base systems")
def _(r):
    n = r.randint(16, 4000)
    ans = hex(n)[2:].upper()
    return Q(f"Write the decimal number {n} in hexadecimal.", ans, f"Divide repeatedly by 16: {n} = {ans} in base 16.",
             [hex(n + i)[2:].upper() for i in (1, 16, -1, 2)])


@T(C, "Surds & indices")
def _(r):
    a, m, n, p = r.choice([2, 3, 5, 7]), r.randint(2, 12), r.randint(2, 12), r.randint(1, 9)
    ans = m + n - p
    return Q(f"If {a}^{m} × {a}^{n} ÷ {a}^{p} = {a}^x, find x.", ans, f"Add and subtract exponents: {m} + {n} − {p} = {ans}.", [m + n + p, m * n - p, m - n + p])


@T(C, "Surds & indices")
def _(r):
    s, k = r.choice([2, 3, 5, 6, 7, 10]), r.randint(2, 20)
    return Q(f"Simplify √{k * k * s}.", f"{k}√{s}", f"{k * k * s} = {k}² × {s}, so the root is {k}√{s}.", [f"{k + 1}√{s}", f"{k}√{s + 1}", f"{s}√{k}", f"{k - 1}√{s}"])


@T(C, "Surds & indices")
def _(r):
    a, b = r.randint(2, 15), r.choice([2, 3, 5, 6, 7])
    ans = a * a - b
    return Q(f"Find the value of ({a} + √{b})({a} − √{b}).", ans, f"(x + y)(x − y) = x² − y² = {a * a} − {b} = {ans}.", [a * a + b, a * a - 2 * b, a * a - b * b])


@T(C, "Logarithms")
def _(r):
    b, n = r.choice([2, 3, 4, 5, 7, 10]), r.randint(2, 6)
    return Q(f"Find log base {b} of {b ** n}.", n, f"{b}^{n} = {b ** n}, so the logarithm is {n}.", [n + 1, n - 1, b, n * b])


@T(C, "Logarithms")
def _(r):
    b, m, n = r.choice([2, 3, 5]), r.randint(1, 5), r.randint(1, 5)
    return Q(f"Find log{b}({b ** m}) + log{b}({b ** n}), where log{b} is the logarithm to base {b}.", m + n, f"The values are {m} and {n}. Their sum is {m + n}, which is also log{b}({b ** (m + n)}).", [m * n, abs(m - n), m + n + 1])


@T(C, "Logarithms")
def _(r):
    a, n = r.randint(2, 30), r.randint(5, 60)
    log2 = {2: 0.30103, 3: 0.47712, 5: 0.69897, 7: 0.8451}
    b = r.choice(list(log2))
    ans = math.floor(n * log2[b]) + 1
    return Q(f"Using log 2 = 0.30103, log 3 = 0.47712, log 5 = 0.69897 and log 7 = 0.8451, how many digits does {b}^{n} have?", ans, f"Digits = ⌊{n} × log {b}⌋ + 1 = ⌊{n * log2[b]:.3f}⌋ + 1 = {ans}.", [ans + 1, ans - 1, ans + 2])


# =================================================================== Simplification
C = "Simplification & Approximation"


@T(C, "BODMAS")
def _(r):
    b, c = r.randint(2, 12), r.randint(2, 9)
    a = b * r.randint(2, 12)
    d, e = r.randint(1, 9), r.randint(10, 30)
    f = r.randint(1, 9)
    ans = a // b * c + d * d - (e - f)
    return Q(f"Evaluate {a} ÷ {b} × {c} + {d}² − ({e} − {f}).", ans, f"Brackets {e - f}; power {d * d}; left to right {a // b} × {c} = {a // b * c}. Then {a // b * c} + {d * d} − {e - f} = {ans}.")


@T(C, "BODMAS")
def _(r):
    a, b, c, d = r.randint(20, 90), r.randint(2, 9), r.randint(2, 9), r.randint(2, 9)
    ans = a - b * c + d
    return Q(f"Evaluate {a} − {b} × {c} + {d}.", ans, f"Multiply first: {b * c}. Then {a} − {b * c} + {d} = {ans}.", [(a - b) * c + d, a - b * (c + d), ans + 2 * d])


@T(C, "BODMAS")
def _(r):
    den, num = r.choice([2, 3, 4, 5, 8, 10]), r.randint(1, 3)
    while gcd(den, num) != 1:
        num = r.randint(1, 3)
    n = den * r.randint(4, 40)
    k = r.randint(2, 6)
    ans = n * num // den * k
    return Q(f"Find {num}/{den} of {n} × {k}.", ans, f"\"Of\" means multiply: {num}/{den} × {n} = {n * num // den}, then × {k} = {ans}.")


@T(C, "Fractions & decimals")
def _(r):
    a, b, c, d = r.randint(1, 9), r.randint(2, 12), r.randint(1, 9), r.randint(2, 12)
    ans = F(a, b) + F(c, d)
    return Q(f"Find {a}/{b} + {c}/{d}.", ans, f"With a common denominator, the sum in lowest terms is {fmt(ans)}.", [F(a + c, b + d), F(a * c, b * d), F(a * d, b * c)])


@T(C, "Fractions & decimals")
def _(r):
    n = r.randint(1, 98)
    if n % 11 == 0 or n % 10 == 0:
        n += 1
    ans = F(n, 99)
    return Q(f"Write the recurring decimal 0.{n:02d}{n:02d}{n:02d}... as a fraction in lowest terms.", ans, f"A two-digit repeat over 99: {n}/99 = {fmt(ans)}.", [F(n, 100), F(n, 90), F(n + 1, 99)])


@T(C, "Fractions & decimals")
def _(r):
    vals = r.sample([F(a, b) for b in (3, 4, 5, 6, 7, 8, 9, 11) for a in range(1, b) if gcd(a, b) == 1], 4)
    big = max(vals)
    return Q("Which of these fractions is the largest?", big, f"As decimals: {', '.join(f'{fmt(v)} ≈ {float(v):.3f}' for v in vals)}.", [v for v in vals if v != big])


@T(C, "Squares, cubes & roots")
def _(r):
    n = r.randint(11, 99)
    return Q(f"Find the square root of {n * n}.", n, f"{n} × {n} = {n * n}.")


@T(C, "Squares, cubes & roots")
def _(r):
    n = r.randint(11, 50)
    return Q(f"Find the cube root of {n ** 3}.", n, f"{n}³ = {n ** 3}. The last digit and the size of the leading part identify it quickly.")


@T(C, "Squares, cubes & roots")
def _(r):
    n = r.randint(21, 150)
    if n % 10 == 0:
        n += 1
    return Q(f"Find the value of {n}².", n * n, f"Split it: ({n // 10 * 10} + {n % 10})² = {(n // 10 * 10) ** 2} + {2 * (n // 10 * 10) * (n % 10)} + {(n % 10) ** 2} = {n * n}.")


@T(C, "Approximation")
def _(r):
    a, b = r.randint(20, 99), r.randint(11, 49)
    x, y = a + r.choice([-.1, .1, .05, -.05]), b + r.choice([-.1, .1, .05, -.05])
    ans = a * b
    step = 10 ** (len(str(ans)) - 2)
    return Q(f"What is the closest value of {x:.2f} × {y:.2f}?", ans, f"Round to {a} × {b} = {ans}.", [ans + step * 3, ans - step * 2, ans + step * 6])


@T(C, "Approximation")
def _(r):
    a, b = r.randint(100, 900), r.choice([5, 10, 20, 25, 50])
    pct = r.choice([9.98, 10.02, 19.97, 20.04, 24.96, 25.03, 49.95, 50.02])
    base = round(pct)
    ans = a * b // 100 if a * b % 100 == 0 else a * base // 100
    ans = a * base // 100
    return Q(f"Approximately, what is {pct}% of {a}?", ans, f"Round to {base}% of {a}, which is about {ans}.")


# =================================================================== Percentages
C = "Percentages"


@T(C, "Basic percentage")
def _(r):
    p = r.choice([5, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 80])
    n = 20 * r.randint(3, 80)
    return Q(f"What is {p}% of {n}?", p * n // 100, f"{p}/100 × {n} = {p * n // 100}.")


@T(C, "Basic percentage")
def _(r):
    p = r.choice([4, 5, 8, 10, 12, 15, 16, 20, 24, 25, 30, 40, 50, 60])
    total = 25 * r.randint(2, 60)
    part = p * total // 100
    return Q(f"{part} is {p}% of which number?", total, f"Number = {part} × 100 ÷ {p} = {total}.", [part * p, total + 25, total - 25])


@T(C, "Basic percentage")
def _(r):
    total = r.choice([40, 50, 80, 120, 160, 200, 250, 400, 500, 800])
    p = r.choice([5, 10, 15, 20, 25, 30, 40, 45, 60, 65, 70, 75, 80])
    part = p * total // 100
    return Q(f"{part} is what percent of {total}?", f"{p}%", f"{part} ÷ {total} × 100 = {p}%.", [f"{p + 5}%", f"{p - 5 if p > 5 else p + 10}%", f"{p + 10}%", f"{p * 2}%"])


@T(C, "Basic percentage")
def _(r):
    total = 100 * r.randint(2, 20)
    fail = r.choice([10, 15, 20, 25, 30, 35, 40])
    return Q(f"In an exam, {fail}% of {total} students failed. How many passed?", total * (100 - fail) // 100, f"Passed = {100 - fail}% of {total} = {total * (100 - fail) // 100}.", [total * fail // 100])


@T(C, "Percentage change")
def _(r):
    old = 20 * r.randint(2, 40)
    p = r.choice([5, 10, 15, 20, 25, 30, 40, 50])
    up = r.choice([True, False])
    new = old * (100 + p) // 100 if up else old * (100 - p) // 100
    return Q(f"A value changes from {old} to {new}. What is the percentage {'increase' if up else 'decrease'}?", f"{p}%", f"Change {abs(new - old)} ÷ original {old} × 100 = {p}%.", [f"{p + 5}%", f"{p + 10}%", f"{abs(p - 3)}%", f"{p * 2}%"])


@T(C, "Percentage change")
def _(r):
    p = r.choice([10, 20, 25, 50, 100, 60, 150, 11, 12])
    ans = F(p * 100, 100 + p)
    return Q(f"Price of an item rises by {p}%. By what percent must consumption fall to keep the spending the same?", f"{fmt(ans)}%", f"Fall = {p} ÷ (100 + {p}) × 100 = {fmt(ans)}%.", [f"{p}%", f"{fmt(F(p * 100, 100 - p)) if p < 100 else p + 20}%", f"{fmt(F(p, 2))}%"])


@T(C, "Percentage change")
def _(r):
    a = r.choice([10, 20, 25, 40, 50, 60])
    k = r.randint(2, 40) * 100
    ans = F(a * 100, 100 + a)
    return Q(f"A's salary ({k * (100 + a) // 100}) is {a}% more than B's ({k}). By what percent is B's salary less than A's?", f"{fmt(ans)}%", f"Difference ÷ A's salary = {a}/{100 + a} = {fmt(ans)}%.", [f"{a}%", f"{a + 5}%", f"{fmt(F(a, 2))}%"])


@T(C, "Successive percentages")
def _(r):
    a, b = r.choice([5, 10, 15, 20, 25, 30, 40, 50]), r.choice([5, 10, 15, 20, 25, 30, 40])
    s = r.choice([1, -1])
    net = F(a + s * b) + F(a * s * b, 100)
    word = "decrease" if s < 0 else "increase"
    return Q(f"A value increases by {a}% and then has a further {word} of {b}%. What is the net percentage change?", f"{fmt(net)}%", f"a + b + ab/100 = {a} {'+' if s > 0 else '−'} {b} {'+' if s > 0 else '−'} {fmt(F(a * b, 100))} = {fmt(net)}%.", [f"{a + s * b}%", f"{fmt(net + 2)}%", f"{fmt(net - 3)}%", f"{a + b}%"])


@T(C, "Successive percentages")
def _(r):
    x = r.choice([10, 20, 30, 40, 50, 25, 5, 15])
    ans = F(x * x, 100)
    return Q(f"A price is raised by {x}% and then lowered by {x}%. What is the overall result?", f"{fmt(ans)}% loss", f"−x²/100 = −{x}²/100 = −{fmt(ans)}%.", ["No change", f"{fmt(ans)}% gain", f"{x}% loss", f"{2 * x}% loss"])


@T(C, "Population & depreciation")
def _(r):
    p = 1000 * r.randint(2, 40)
    g, n = r.choice([5, 10, 20, 25, 50]), r.choice([1, 2, 3])
    ans = F(p) * F(100 + g, 100) ** n
    return Q(f"A town's population of {p} grows at {g}% a year. What will it be after {n} year{'s' if n > 1 else ''}?", ans, f"{p} × (1 + {g}/100)^{n} = {fmt(ans)}.", [p + p * g * n // 100 + 7 * g if n == 1 else p + p * g * n // 100, ans + 500, ans - 300])


@T(C, "Population & depreciation")
def _(r):
    p = 1000 * r.randint(10, 400)
    g, n = r.choice([5, 10, 20, 25]), r.choice([1, 2, 3])
    ans = F(p) * F(100 - g, 100) ** n
    return Q(f"A machine worth ₹{p} depreciates by {g}% each year. What is its value after {n} year{'s' if n > 1 else ''}?", f"₹{fmt(ans)}", f"{p} × (1 − {g}/100)^{n} = {fmt(ans)}.", [f"₹{p - p * g * n // 100 - (500 if n == 1 else 0)}", f"₹{fmt(ans + 800)}", f"₹{fmt(ans - 600)}"])


@T(C, "Population & depreciation")
def _(r):
    now = 1000 * r.randint(2, 50)
    g = r.choice([10, 20, 25, 50])
    ago = F(now) * F(100 + g, 100)
    return Q(f"A town has {fmt(ago)} people now, after growing {g}% in the last year. What was the population a year ago?", now, f"Divide by 1 + {g}/100: {fmt(ago)} ÷ {fmt(F(100 + g, 100))} = {now}.", [ago - ago * g // 100, now + 500, now - 400])


# =================================================================== Ratio
C = "Ratio, Proportion & Variation"


@T(C, "Ratio")
def _(r):
    a, b = r.randint(1, 12), r.randint(1, 12)
    while gcd(a, b) != 1:
        b = r.randint(1, 12)
    k = r.randint(5, 60)
    return Q(f"Divide ₹{(a + b) * k} between A and B in the ratio {a} : {b}. What is A's share?", a * k, f"One part = {(a + b) * k} ÷ {a + b} = {k}. A = {a} × {k} = {a * k}.", [b * k])


@T(C, "Ratio")
def _(r):
    a, b, c, d = r.randint(1, 9), r.randint(2, 9), r.randint(2, 9), r.randint(1, 9)
    ans = F(a * c, b * d)
    return Q(f"If A : B = {a} : {b} and B : C = {c} : {d}, what is A : C?", f"{ans.numerator} : {ans.denominator}", f"A/C = (A/B)(B/C) = ({a}/{b})({c}/{d}) = {fmt(ans)}.", [f"{a * d} : {b * c}", f"{a + c} : {b + d}", f"{ans.denominator} : {ans.numerator}", f"{ans.numerator + 1} : {ans.denominator}"])


@T(C, "Ratio")
def _(r):
    a, b = r.randint(2, 9), r.randint(2, 9)
    while a == b or gcd(a, b) != 1:
        b = r.randint(2, 9)
    k = r.randint(3, 20)
    add = r.randint(1, 8) * (a + b)
    x = (a * k + add)
    y = (b * k + add)
    g = gcd(x, y)
    return Q(f"Two numbers, {a * k} and {b * k}, are in the ratio {a} : {b}. If {add} is added to each, what is the new ratio?", f"{x // g} : {y // g}", f"({a * k} + {add}) : ({b * k} + {add}) = {x} : {y} = {x // g} : {y // g}.", [f"{a} : {b}", f"{y // g} : {x // g}", f"{x // g + 1} : {y // g}", f"{x // g} : {y // g + 1}"])


@T(C, "Proportion")
def _(r):
    a, b, k = r.randint(2, 15), r.randint(2, 15), r.randint(2, 12)
    c = a * k
    return Q(f"Find x if {a} : {b} = {c} : x.", b * k, f"Product of means = product of extremes: x = {b} × {c} ÷ {a} = {b * k}.")


@T(C, "Proportion")
def _(r):
    a, k = r.randint(2, 12), r.randint(2, 6)
    b, c = a * k, a * k * k
    return Q(f"Find the mean proportional between {a} and {c}.", b, f"Mean proportional = √({a} × {c}) = √{a * c} = {b}.")


@T(C, "Proportion")
def _(r):
    a, k = r.randint(2, 12), r.randint(2, 5)
    b = a * k
    return Q(f"Find the third proportional to {a} and {b}.", b * k, f"{a} : {b} = {b} : x, so x = {b}² ÷ {a} = {b * k}.")


@T(C, "Direct & inverse variation")
def _(r):
    x1, k, x2 = r.randint(2, 20), r.randint(2, 15), r.randint(2, 30)
    return Q(f"y varies directly as x. If y = {x1 * k} when x = {x1}, find y when x = {x2}.", k * x2, f"y = {k}x, so y = {k} × {x2} = {k * x2}.")


@T(C, "Direct & inverse variation")
def _(r):
    p = r.choice([60, 72, 84, 90, 96, 120, 144, 180, 240, 360])
    x1, x2 = r.sample([x for x in range(2, 25) if p % x == 0], 2)
    return Q(f"y varies inversely as x. If y = {p // x1} when x = {x1}, find y when x = {x2}.", p // x2, f"xy is constant = {p}, so y = {p} ÷ {x2} = {p // x2}.")


@T(C, "Direct & inverse variation")
def _(r):
    m, d = r.choice([6, 8, 10, 12, 15, 20, 24]), r.choice([6, 8, 10, 12, 15, 18, 20, 30])
    m2 = r.choice([x for x in (2, 3, 4, 5, 6, 8, 10, 12, 15, 16, 20, 24, 30, 40) if m * d % x == 0 and x != m])
    return Q(f"{m} workers finish a job in {d} days. How many days would {m2} workers take, at the same rate?", m * d // m2, f"Workers × days is constant = {m * d}. Days = {m * d} ÷ {m2} = {m * d // m2}.")


@T(C, "Componendo & dividendo")
def _(r):
    a, b = r.randint(2, 15), r.randint(1, 14)
    while a <= b:
        a = r.randint(2, 15)
    ans = F(a + b, a - b)
    return Q(f"If x/y = {a}/{b}, find (x + y)/(x − y).", ans, f"Componendo and dividendo: ({a} + {b})/({a} − {b}) = {fmt(ans)}.", [F(a - b, a + b), F(a, b), F(a + b, a)])


@T(C, "Componendo & dividendo")
def _(r):
    p, q = r.randint(3, 15), r.randint(1, 12)
    while p <= q:
        p = r.randint(3, 15)
    ans = F(p + q, p - q)
    return Q(f"If (x + y)/(x − y) = {p}/{q}, find x/y.", ans, f"Apply it in reverse: x/y = ({p} + {q})/({p} − {q}) = {fmt(ans)}.", [F(p - q, p + q), F(p, q), F(p + q, q)])


# =================================================================== Averages
C = "Averages"


@T(C, "Simple average")
def _(r):
    n = r.randint(4, 7)
    avg = r.randint(15, 90)
    xs = [avg + r.randint(-12, 12) for _ in range(n - 1)]
    xs.append(avg * n - sum(xs))
    return Q(f"Find the average of {', '.join(map(str, xs))}.", avg, f"Sum = {avg * n}, count = {n}, average = {avg}.")


@T(C, "Simple average")
def _(r):
    n = r.randint(5, 40)
    a = r.randint(10, 80)
    return Q(f"The average of {n} numbers is {a}. What is their sum?", n * a, f"Sum = {n} × {a} = {n * a}.")


@T(C, "Simple average")
def _(r):
    n = r.choice([5, 7, 9, 11, 15, 21, 25, 51])
    start = r.randint(1, 60)
    return Q(f"Find the average of {n} consecutive numbers starting from {start}.", start + (n - 1) // 2, f"Consecutive numbers: average is the middle term, {start} + {(n - 1) // 2} = {start + (n - 1) // 2}.")


@T(C, "Weighted average")
def _(r):
    n1, n2 = r.randint(10, 40), r.randint(10, 40)
    a1, a2 = r.randint(30, 70), r.randint(30, 70)
    ans = F(n1 * a1 + n2 * a2, n1 + n2)
    return Q(f"A class of {n1} students averages {a1} marks and another of {n2} averages {a2}. What is the combined average?", ans if ans.denominator == 1 else f"{float(ans):.2f}", f"({n1} × {a1} + {n2} × {a2}) ÷ {n1 + n2} = {n1 * a1 + n2 * a2} ÷ {n1 + n2} = {float(ans):.2f}.", [f"{(a1 + a2) / 2:.2f}", f"{float(ans) + 2:.2f}", f"{float(ans) - 3:.2f}"])


@T(C, "Weighted average")
def _(r):
    b = 5 * r.randint(4, 12)
    g = b + 5 * r.randint(2, 6)
    m = r.randint(1, 3) * 5 if False else 5
    n1, n2 = r.randint(1, 5), r.randint(1, 5)
    avg = F(n1 * b + n2 * g, n1 + n2)
    return Q(f"Boys average {b} and girls average {g} in a test. If boys and girls are in the ratio {n1} : {n2}, find the class average.", f"{float(avg):.2f}", f"Weights: ({n1} × {b} + {n2} × {g}) ÷ {n1 + n2} = {float(avg):.2f}.", [f"{(b + g) / 2 + 1.5:.2f}", f"{float(avg) + 2.5:.2f}", f"{float(avg) - 2.5:.2f}"])


@T(C, "Average speed")
def _(r):
    a, b = r.choice([(20, 30), (30, 60), (40, 60), (30, 50), (36, 45), (60, 90), (10, 40), (25, 75), (24, 40), (45, 90), (20, 60), (28, 35), (60, 120), (15, 30), (18, 36), (40, 120), (50, 150)])
    s = 2 * a * b // (a + b) if 2 * a * b % (a + b) == 0 else None
    ans = F(2 * a * b, a + b)
    return Q(f"A car goes from P to Q at {a} km/h and returns at {b} km/h. What is the average speed for the round trip, in km/h?", ans, f"Equal distances: 2ab/(a + b) = 2 × {a} × {b} ÷ {a + b} = {fmt(ans)}.", [F(a + b, 2), F(a + b, 2) + 2, ans + 3])


@T(C, "Average speed")
def _(r):
    t1, t2, s1, s2 = r.randint(1, 5), r.randint(1, 5), 10 * r.randint(2, 8), 10 * r.randint(2, 8)
    ans = F(t1 * s1 + t2 * s2, t1 + t2)
    return Q(f"A bus travels {t1} h at {s1} km/h and then {t2} h at {s2} km/h. What is its average speed in km/h?", ans, f"Total distance {t1 * s1 + t2 * s2} ÷ total time {t1 + t2} = {fmt(ans)}.", [F(s1 + s2, 2) + 3, ans + 4, ans + 7 if ans > 8 else ans + 9])


@T(C, "Replacement & addition problems")
def _(r):
    n, a = r.randint(5, 40), r.randint(20, 70)
    inc = r.randint(1, 4)
    out = r.randint(30, 80)
    ans = out + n * inc
    return Q(f"The average weight of {n} people rises by {inc} kg when one person of {out} kg is replaced by a new person. What is the new person's weight, in kg?", ans, f"New = old + n × rise = {out} + {n} × {inc} = {ans}.", [out + inc, out - n * inc if out > n * inc else out + 2 * inc, ans + n])


@T(C, "Replacement & addition problems")
def _(r):
    n, a, d = r.randint(5, 30), r.randint(20, 70), r.randint(1, 3)
    ans = a + d * (n + 1)
    return Q(f"The average of {n} numbers is {a}. Adding one number raises the average by {d}. What is the added number?", ans, f"New sum = {n + 1} × {a + d} = {(n + 1) * (a + d)}; old sum = {n * a}. Added = {ans}.", [a + d, a + d * n, ans + 1])


@T(C, "Replacement & addition problems")
def _(r):
    n, a = r.randint(5, 30), r.randint(20, 70)
    x = a + r.randint(5, 40)
    new_sum = n * a - x
    ans = F(new_sum, n - 1)
    return Q(f"The average of {n} numbers is {a}. If one number, {x}, is removed, what is the new average?", f"{float(ans):.2f}", f"({n} × {a} − {x}) ÷ {n - 1} = {new_sum} ÷ {n - 1} = {float(ans):.2f}.", [f"{float(ans) + 1:.2f}", f"{float(ans) - 1.5:.2f}", f"{a + 1:.2f}"])


# =================================================================== Ages
C = "Problems on Ages"


@T(C, "Present, past & future ages")
def _(r):
    c = r.randint(5, 20)
    k = r.randint(2, 5)
    y = r.randint(2, 8)
    return Q(f"A father is {k} times as old as his son. {y} years ago, their total age was {(k + 1) * c - 2 * y}. How old is the son now?", c, f"Now total = {(k + 1) * c - 2 * y} + {2 * y} = {(k + 1) * c}. Son = {(k + 1) * c} ÷ {k + 1} = {c}.")


@T(C, "Present, past & future ages")
def _(r):
    s = r.randint(6, 25)
    d = r.randint(18, 35)
    a = s + d
    return Q(f"A mother is {d} years older than her son. In {r.randint(2, 2)} years the sum of their ages will be {a + s + 4}. How old is the son now?", s, f"Let son = x. x + 2 + x + {d} + 2 = {a + s + 4}, so 2x = {2 * s}, x = {s}.")


@T(C, "Present, past & future ages")
def _(r):
    s = r.randint(5, 20)
    m = r.randint(2, 5)
    y = r.randint(2, 15)
    f = m * (s + y) - y
    return Q(f"A man is now {f} and his son is {s}. In how many years will the man be {m} times as old as the son?", y, f"{f} + y = {m}({s} + y), so y = ({f} − {m * s}) ÷ {m - 1} = {y}.")


@T(C, "Ratio-based age problems")
def _(r):
    a, b = r.randint(2, 7), r.randint(2, 9)
    while a == b or gcd(a, b) != 1:
        b = r.randint(2, 9)
    k = r.randint(2, 12)
    y = r.randint(2, 12)
    x1, x2 = a * k + y, b * k + y
    g = gcd(x1, x2)
    return Q(f"The present ages of A and B are in the ratio {a} : {b}. After {y} years the ratio will be {x1 // g} : {x2 // g}. What is A's present age?", a * k, f"Let the ages be {a}x and {b}x. ({a}x + {y}) ÷ ({b}x + {y}) = {x1 // g}/{x2 // g} gives x = {k}. A = {a * k}.", [b * k])


@T(C, "Ratio-based age problems")
def _(r):
    a, b = r.randint(2, 9), r.randint(2, 9)
    while a == b or gcd(a, b) != 1:
        b = r.randint(2, 9)
    k = r.randint(2, 12)
    return Q(f"The ages of two sisters are in the ratio {a} : {b}, and the sum of their ages is {(a + b) * k}. How old is the younger sister?", min(a, b) * k, f"One part = {(a + b) * k} ÷ {a + b} = {k}. Younger = {min(a, b)} × {k} = {min(a, b) * k}.", [max(a, b) * k])


@T(C, "Ratio-based age problems")
def _(r):
    a, b = r.randint(2, 7), r.randint(3, 9)
    while a >= b or gcd(a, b) != 1:
        a, b = r.randint(2, 7), r.randint(3, 9)
    k = r.randint(3, 12)
    return Q(f"Ages of two friends are in the ratio {a} : {b}. If their ages differ by {(b - a) * k} years, what is the elder friend's age?", b * k, f"{b - a} parts = {(b - a) * k}, so one part = {k}. Elder = {b} × {k} = {b * k}.", [a * k])


# =================================================================== Partnership
C = "Partnership"


@T(C, "Simple partnership")
def _(r):
    a, b = 1000 * r.randint(2, 12), 1000 * r.randint(2, 12)
    while a == b:
        b = 1000 * r.randint(2, 12)
    g = gcd(a, b)
    profit = (a + b) // g * r.randint(100, 900)
    return Q(f"A invests ₹{a} and B invests ₹{b} for the same period. The profit is ₹{profit}. What is A's share?", f"₹{profit * a // (a + b)}", f"Ratio {a // g} : {b // g}. A gets {a // g}/{(a + b) // g} of {profit} = {profit * a // (a + b)}.", [f"₹{profit * b // (a + b)}", f"₹{profit // 2 + 11}", f"₹{profit * a // (a + b) + 100}"])


@T(C, "Simple partnership")
def _(r):
    a, b, c = r.randint(1, 7), r.randint(1, 7), r.randint(1, 7)
    t = a + b + c
    k = r.randint(100, 900)
    return Q(f"A, B and C share profit in the ratio {a} : {b} : {c}. If the total profit is ₹{t * k}, what is C's share?", f"₹{c * k}", f"One part = {t * k} ÷ {t} = {k}. C = {c} × {k} = {c * k}.", [f"₹{a * k + 5}", f"₹{b * k + 15}", f"₹{c * k + k}"])


@T(C, "Compound partnership")
def _(r):
    a, b = 1000 * r.randint(2, 10), 1000 * r.randint(2, 10)
    m1, m2 = r.choice([4, 6, 8, 9, 12]), r.choice([3, 4, 6, 8, 9, 12])
    x, y = a * m1, b * m2
    g = gcd(x, y)
    profit = (x + y) // g * r.randint(100, 800)
    return Q(f"A invests ₹{a} for {m1} months and B invests ₹{b} for {m2} months. Of a profit of ₹{profit}, how much does B get?", f"₹{profit * y // (x + y)}", f"Capital × time: {x} : {y} = {x // g} : {y // g}. B = {y // g}/{(x + y) // g} × {profit} = {profit * y // (x + y)}.", [f"₹{profit * x // (x + y)}", f"₹{profit // 2 + 13}", f"₹{profit * y // (x + y) + 200}"])


@T(C, "Compound partnership")
def _(r):
    a, b = 1000 * r.randint(2, 10), 1000 * r.randint(2, 10)
    m = r.choice([2, 3, 4, 5, 6, 8, 9, 10])
    x, y = a * 12, b * (12 - m)
    g = gcd(x, y)
    return Q(f"A starts a business with ₹{a}. B joins {m} months later with ₹{b}. In what ratio should the first year's profit be shared (A : B)?", f"{x // g} : {y // g}", f"A: {a} × 12 = {x}. B: {b} × {12 - m} = {y}. Ratio {x // g} : {y // g}.", [f"{a // gcd(a, b)} : {b // gcd(a, b)}", f"{y // g} : {x // g}", f"{x // g + 1} : {y // g}", f"{x // g} : {y // g + 1}"])


@T(C, "Working vs. sleeping partner")
def _(r):
    a, b = 1000 * r.choice([4, 6, 8, 10]), 1000 * r.choice([2, 3, 5, 6])
    p = r.choice([10, 20, 25])
    k = (a + b) // 1000
    profit = k * 100 * r.randint(2, 30)
    salary = profit * p // 100
    rest = profit - salary
    ans = salary + rest * a // (a + b)
    return Q(f"A (working partner) invests ₹{a} and B (sleeping partner) invests ₹{b}. A first gets {p}% of the profit for managing, and the rest is shared by capital. What does A get in total from a profit of ₹{profit}?", f"₹{ans}", f"Management share {salary}. Rest {rest} split {a} : {b}, so A gets {rest * a // (a + b)}. Total {ans}.", [f"₹{profit * a // (a + b)}", f"₹{salary}", f"₹{profit - ans}"])


@T(C, "Working vs. sleeping partner")
def _(r):
    a, b = 1000 * r.choice([4, 6, 8, 10, 12]), 1000 * r.choice([2, 3, 4, 5, 6])
    salary = 100 * r.randint(3, 20)
    k = (a + b) // gcd(a, b)
    rest = k * 100 * r.randint(2, 12)
    profit = rest + salary
    ans = rest * b // (a + b)
    return Q(f"Sleeping partner B invests ₹{b} and working partner A invests ₹{a}. A also draws ₹{salary} as salary from a profit of ₹{profit}. What does B receive?", f"₹{ans}", f"After salary, {rest} is left. B's share is {b}/{a + b} of it = {ans}.", [f"₹{profit * b // (a + b)}", f"₹{rest * a // (a + b)}", f"₹{ans + salary}"])


# =================================================================== Profit & Loss
C = "Profit & Loss"


@T(C, "Cost price, selling price, profit & loss")
def _(r):
    cp, p = 20 * r.randint(5, 80), r.choice([5, 10, 15, 20, 25, 30, 40, 50])
    return Q(f"An article bought for ₹{cp} is sold at a {p}% profit. What is the selling price?", f"₹{cp * (100 + p) // 100}", f"SP = {cp} × {100 + p}/100 = {cp * (100 + p) // 100}.", [f"₹{cp * (100 - p) // 100}", f"₹{cp + p}", f"₹{cp * (100 + p) // 100 + 20}"])


@T(C, "Cost price, selling price, profit & loss")
def _(r):
    cp, p = 20 * r.randint(5, 80), r.choice([5, 10, 15, 20, 25, 30, 40, 50])
    sp = cp * (100 - p) // 100
    return Q(f"An article bought for ₹{cp} is sold for ₹{sp}. What is the loss percentage?", f"{p}%", f"Loss {cp - sp} ÷ {cp} × 100 = {p}%.", [f"{p + 5}%", f"{p + 2}%", f"{fmt(F((cp - sp) * 100, sp))}%" if (cp - sp) * 100 % sp == 0 else f"{p + 10}%"])


@T(C, "Cost price, selling price, profit & loss")
def _(r):
    cp, p = 100 * r.randint(2, 30), r.choice([10, 20, 25, 50])
    sp = cp * (100 + p) // 100
    return Q(f"A trader sells a phone for ₹{sp}, making a {p}% profit. What did the phone cost?", f"₹{cp}", f"CP = {sp} × 100 ÷ {100 + p} = {cp}.", [f"₹{sp * (100 - p) // 100}", f"₹{cp + 100}", f"₹{cp - 50}"])


@T(C, "Cost price, selling price, profit & loss")
def _(r):
    x = r.choice([8, 10, 12, 15, 16, 18, 20, 24, 25, 30])
    y = r.choice([v for v in (5, 6, 8, 9, 10, 12, 15, 16, 18, 20) if v < x])
    ans = F((x - y) * 100, y)
    return Q(f"The cost price of {x} articles equals the selling price of {y} articles. What is the profit percentage?", f"{fmt(ans)}%", f"Profit % = ({x} − {y}) ÷ {y} × 100 = {fmt(ans)}%.", [f"{fmt(F((x - y) * 100, x))}%", f"{x - y}%", f"{fmt(ans + 5)}%"])


@T(C, "Discount & marked price")
def _(r):
    m, d = 100 * r.randint(2, 40), r.choice([5, 10, 15, 20, 25, 30, 40, 50])
    return Q(f"An item marked ₹{m} is sold at a {d}% discount. What is the selling price?", f"₹{m * (100 - d) // 100}", f"SP = {m} × {100 - d}/100 = {m * (100 - d) // 100}.", [f"₹{m * d // 100}", f"₹{m - d}", f"₹{m * (100 - d) // 100 + 50}"])


@T(C, "Discount & marked price")
def _(r):
    cp, up, d = 100 * r.randint(2, 20), r.choice([20, 25, 30, 40, 50, 60]), r.choice([5, 10, 20, 25])
    ans = F((100 + up) * (100 - d), 100) - 100
    return Q(f"A shopkeeper marks goods {up}% above cost and gives a {d}% discount. What is the profit percentage?", f"{fmt(ans)}%", f"(1 + {up}/100)(1 − {d}/100) − 1 gives {fmt(ans)}%.", [f"{up - d}%", f"{fmt(ans + 2)}%", f"{fmt(ans + 5)}%", f"{up}%"])


@T(C, "Successive discounts")
def _(r):
    a, b = r.choice([5, 10, 15, 20, 25, 30, 40]), r.choice([5, 10, 15, 20, 25, 30])
    ans = a + b - F(a * b, 100)
    return Q(f"What single discount equals successive discounts of {a}% and {b}%?", f"{fmt(ans)}%", f"a + b − ab/100 = {a} + {b} − {fmt(F(a * b, 100))} = {fmt(ans)}%.", [f"{a + b}%", f"{fmt(ans + 2)}%", f"{fmt(ans - 2)}%"])


@T(C, "Successive discounts")
def _(r):
    m, a, b = 1000 * r.randint(1, 20), r.choice([10, 20, 25, 50]), r.choice([10, 20, 25, 50])
    ans = F(m) * F(100 - a, 100) * F(100 - b, 100)
    return Q(f"A TV marked ₹{m} gets discounts of {a}% and then {b}%. What is the final price?", f"₹{fmt(ans)}", f"{m} × {fmt(F(100 - a, 100))} × {fmt(F(100 - b, 100))} = {fmt(ans)}.", [f"₹{m * (100 - a - b) // 100 if a + b < 100 else m // 5}", f"₹{fmt(ans + 100)}", f"₹{fmt(ans + 250)}"])


@T(C, "Dishonest dealings")
def _(r):
    w = r.choice([800, 900, 950, 750, 960, 875, 500, 600, 400, 625])
    ans = F((1000 - w) * 100, w)
    return Q(f"A dealer claims to sell at cost price but uses a {w} g weight for 1 kg. What is the profit percentage?", f"{fmt(ans)}%", f"Profit % = (1000 − {w}) ÷ {w} × 100 = {fmt(ans)}%.", [f"{fmt(F(1000 - w, 10))}%", f"{fmt(ans + 2)}%", f"{fmt(ans + 5)}%"])


@T(C, "Dishonest dealings")
def _(r):
    p = r.choice([10, 20, 25, 50])
    w = r.choice([800, 900, 750, 500, 960, 625, 400])
    ans = F(100 + p, 100) * F(1000, w) * 100 - 100
    return Q(f"A dealer marks up by {p}% over cost and also gives only {w} g for each kg. What is the actual profit percentage?", f"{fmt(ans)}%", f"(1 + {p}/100) × (1000/{w}) − 1 = {fmt(ans)}%.", [f"{fmt(p + F(1000 - w, 10))}%", f"{p}%", f"{fmt(ans + 3)}%"])


# =================================================================== Interest
C = "Simple & Compound Interest"


@T(C, "Simple interest")
def _(r):
    p, t, rate = 100 * r.randint(5, 200), r.randint(2, 10), r.randint(2, 15)
    return Q(f"Find the simple interest on ₹{p} at {rate}% per year for {t} years.", f"₹{p * rate * t // 100}", f"SI = PRT/100 = {p} × {rate} × {t} ÷ 100 = {p * rate * t // 100}.", [f"₹{p * rate // 100}", f"₹{p + p * rate * t // 100}", f"₹{p * rate * (t + 1) // 100}"])


@T(C, "Simple interest")
def _(r):
    p, t, rate = 100 * r.randint(5, 200), r.randint(2, 10), r.randint(2, 15)
    a = p + p * rate * t // 100
    return Q(f"A sum becomes ₹{a} in {t} years at {rate}% simple interest. What was the sum?", f"₹{p}", f"A = P(1 + RT/100). P = {a} ÷ {fmt(F(100 + rate * t, 100))} = {p}.", [f"₹{a - p * rate // 100}", f"₹{p + 100}", f"₹{p - 100}"])


@T(C, "Simple interest")
def _(r):
    k = r.randint(2, 6)
    t = r.choice([2, 4, 5, 8, 10, 12, 15, 20, 25])
    ans = F((k - 1) * 100, t)
    return Q(f"A sum becomes {k} times itself in {t} years at simple interest. What is the rate per year?", f"{fmt(ans)}%", f"Interest is {k - 1} times the sum: R = {k - 1} × 100 ÷ {t} = {fmt(ans)}%.", [f"{fmt(F(k * 100, t))}%", f"{fmt(ans + 2)}%", f"{fmt(ans + 5)}%"])


@T(C, "Compound interest")
def _(r):
    p, rate, n = 1000 * r.randint(1, 30), r.choice([5, 10, 20, 25, 50]), r.choice([2, 3])
    a = F(p) * F(100 + rate, 100) ** n
    return Q(f"Find the amount on ₹{p} at {rate}% compounded yearly for {n} years.", f"₹{fmt(a)}", f"A = {p} × (1 + {rate}/100)^{n} = {fmt(a)}.", [f"₹{p + p * rate * n // 100}", f"₹{fmt(a + 200)}", f"₹{fmt(a - 150)}"])


@T(C, "Compound interest")
def _(r):
    p, rate, n = 1000 * r.randint(1, 30), r.choice([10, 20, 5, 25]), 2
    ci = F(p) * F(100 + rate, 100) ** n - p
    return Q(f"Find the compound interest on ₹{p} at {rate}% per year for {n} years, compounded yearly.", f"₹{fmt(ci)}", f"Amount − principal = {fmt(ci + p)} − {p} = {fmt(ci)}.", [f"₹{p * rate * n // 100}", f"₹{fmt(ci + p)}", f"₹{fmt(ci + 50)}"])


@T(C, "Compound interest")
def _(r):
    k = r.choice([2, 3, 4, 5])
    y = r.randint(2, 12)
    m = r.choice([2, 3, 4])
    return Q(f"A sum becomes {k} times itself in {y} years at compound interest. In how many years does it become {k ** m} times itself?", y * m, f"{k ** m} = {k}^{m}, so the time is {m} × {y} = {y * m} years.", [y * (k ** m) // k, y * (m + 1), y * m + y // 2 + 1])


@T(C, "Difference between CI and SI")
def _(r):
    p, rate = 1000 * r.randint(1, 50), r.choice([5, 10, 20, 15, 25, 4, 8, 12])
    d = F(p * rate * rate, 10000)
    return Q(f"Find the difference between compound and simple interest on ₹{p} at {rate}% for 2 years.", f"₹{fmt(d)}", f"For 2 years: P(R/100)² = {p} × ({rate}/100)² = {fmt(d)}.", [f"₹{fmt(d * 2)}", f"₹{fmt(d + 10)}", f"₹{p * rate // 100}"])


@T(C, "Difference between CI and SI")
def _(r):
    rate = r.choice([5, 10, 20, 4, 8, 25])
    p = 1000 * r.randint(1, 50)
    d = F(p * rate * rate, 10000)
    return Q(f"The difference between compound and simple interest on a sum for 2 years at {rate}% is ₹{fmt(d)}. What is the sum?", f"₹{p}", f"P = D × (100/R)² = {fmt(d)} × (100/{rate})² = {p}.", [f"₹{p + 1000}", f"₹{p * 2}", f"₹{p // 2 + 500}"])


@T(C, "Installments")
def _(r):
    x = 100 * r.randint(2, 40)
    rate, n = r.choice([5, 10, 20, 25, 50]), 2
    g = F(100 + rate, 100)
    debt = x / g + x / (g * g)
    return Q(f"A loan is repaid in 2 equal yearly installments of ₹{x} at {rate}% compound interest. What was the loan?", f"₹{float(debt):.2f}", f"Present value = {x}/{fmt(g)} + {x}/{fmt(g)}² = {float(debt):.2f}.", [f"₹{2 * x}", f"₹{float(debt) + 100:.2f}", f"₹{float(debt) - 75:.2f}"])


@T(C, "Installments")
def _(r):
    rate, n = r.choice([5, 10, 20, 15, 8, 12]), r.choice([2, 3, 4, 5])
    x = 100 * r.randint(2, 30)
    ans = x * n + x * rate * n * (n - 1) // 200
    return Q(f"At {rate}% simple interest, a debt is cleared by {n} equal yearly installments of ₹{x}. What is the debt due at the end of {n} years?", f"₹{ans}", f"Each installment earns SI until the end: {n} × {x} + {x} × {rate}/100 × (0 + 1 + ... + {n - 1}) = {ans}.", [f"₹{x * n}", f"₹{ans + x}", f"₹{ans + 100}"])


@T(C, "Effective rate of interest")
def _(r):
    rate = r.choice([4, 6, 8, 10, 12, 16, 20, 24])
    ans = (F(100 + F(rate, 2), 100) ** 2 - 1) * 100
    return Q(f"What is the effective annual rate of {rate}% per year compounded half-yearly?", f"{float(ans):.2f}%", f"(1 + {rate / 2:g}/100)² − 1 = {float(ans):.2f}%.", [f"{rate}%", f"{float(ans) + .5:.2f}%", f"{rate + 1}%"])


@T(C, "Effective rate of interest")
def _(r):
    rate = r.choice([4, 8, 12, 16, 20, 24, 28, 32])
    ans = (F(100 + F(rate, 4), 100) ** 4 - 1) * 100
    return Q(f"What is the effective annual rate of {rate}% per year compounded quarterly?", f"{float(ans):.2f}%", f"(1 + {rate / 4:g}/100)⁴ − 1 = {float(ans):.2f}%.", [f"{rate}%", f"{float(ans) + .4:.2f}%", f"{float(ans) - .25:.2f}%"])


@T(C, "Effective rate of interest")
def _(r):
    p, rate = 1000 * r.randint(1, 40), r.choice([10, 20, 8, 4, 12, 16])
    half = F(rate, 2)
    a = F(p) * F(100 + half, 100) ** 2
    return Q(f"Find the amount on ₹{p} after 1 year at {rate}% compounded half-yearly.", f"₹{float(a):.2f}", f"{p} × (1 + {fmt(half)}/100)² = {float(a):.2f}.", [f"₹{p + p * rate // 100}", f"₹{float(a) + 50:.2f}", f"₹{float(a) - 30:.2f}"])


# =================================================================== Mixtures
C = "Mixtures & Alligations"


@T(C, "Alligation rule")
def _(r):
    a = r.randint(20, 60)
    b = a + r.randint(10, 60)
    m = r.randint(a + 1, b - 1)
    x, y = b - m, m - a
    g = gcd(x, y)
    return Q(f"In what ratio must rice at ₹{a}/kg be mixed with rice at ₹{b}/kg to get a mixture worth ₹{m}/kg?", f"{x // g} : {y // g}", f"Alligation: ({b} − {m}) : ({m} − {a}) = {x} : {y} = {x // g} : {y // g}.", [f"{y // g} : {x // g}", f"{x // g + 1} : {y // g}", f"{a} : {b}", f"{x // g} : {y // g + 1}"])


@T(C, "Alligation rule")
def _(r):
    a, b = r.randint(1, 5), r.randint(1, 5)
    ca, cb = 10 * r.randint(2, 6), 10 * r.randint(2, 8)
    m = F(a * ca + b * cb, a + b)
    return Q(f"Milk at ₹{ca}/litre and milk at ₹{cb}/litre are mixed in the ratio {a} : {b}. What is the mixture's price per litre, in ₹?", f"{float(m):.2f}", f"({a} × {ca} + {b} × {cb}) ÷ {a + b} = {float(m):.2f}.", [f"{(ca + cb) / 2 + 1.5:.2f}", f"{float(m) + 2:.2f}", f"{float(m) - 3:.2f}"])


@T(C, "Alligation rule")
def _(r):
    w, m, y = r.choice([1, 2, 3, 4]), r.choice([3, 4, 5, 6, 7, 9]), 0
    total = (w + m) * r.randint(3, 15)
    water = total * w // (w + m)
    add = r.randint(1, 10) * (w + m)
    return Q(f"A {total}-litre mixture has milk and water in the ratio {m} : {w}. How many litres of water are in it?", water, f"Water = {w}/{m + w} × {total} = {water}.", [total - water])


@T(C, "Replacement of a mixture")
def _(r):
    v, t = r.choice([20, 40, 50, 60, 80, 100, 120]), r.choice([2, 3])
    x = r.choice([d for d in (2, 4, 5, 8, 10, 12, 15, 16, 20) if d < v])
    ans = F(v) * F(v - x, v) ** t
    return Q(f"From a {v}-litre can of pure milk, {x} litres are taken out and replaced by water, and this is done {t} times in all. How many litres of milk remain?", f"{float(ans):.2f}", f"Milk left = {v} × (1 − {x}/{v})^{t} = {float(ans):.2f}.", [f"{v - x * t}", f"{float(ans) + 1.5:.2f}", f"{float(ans) - 2:.2f}"])


@T(C, "Replacement of a mixture")
def _(r):
    v = r.choice([40, 50, 60, 80, 100, 120, 200])
    m, w = r.randint(3, 9), r.randint(1, 4)
    while gcd(m, w) != 1:
        w = r.randint(1, 4)
    total = (m + w) * r.randint(2, 12)
    add = w * r.randint(1, 4)
    milk, water = total * m // (m + w), total * w // (m + w) + add
    g = gcd(milk, water)
    return Q(f"A {total}-litre mixture has milk and water in the ratio {m} : {w}. If {add} litres of water are added, what is the new ratio of milk to water?", f"{milk // g} : {water // g}", f"Milk {milk}, water {water - add} + {add} = {water}. Ratio {milk // g} : {water // g}.", [f"{m} : {w}", f"{water // g} : {milk // g}", f"{milk // g + 1} : {water // g}", f"{milk // g} : {water // g + 1}"])


@T(C, "Replacement of a mixture")
def _(r):
    v = r.choice([20, 30, 40, 50, 60, 80, 100])
    x = r.choice([d for d in (2, 4, 5, 6, 8, 10, 12, 15, 20) if d < v])
    ans = F(x * 100, v)
    return Q(f"A {v}-litre tank of petrol has {x} litres removed and replaced by kerosene. What percent of the tank is now kerosene?", f"{fmt(ans)}%", f"Kerosene share = {x}/{v} = {fmt(ans)}%.", [f"{fmt(F(100 - ans))}%", f"{fmt(ans + 5)}%", f"{fmt(ans * 2)}%"])


# =================================================================== Time & Work
C = "Time & Work"


@T(C, "Work-rate")
def _(r):
    a, b = r.sample([6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 30, 36, 40, 45, 60], 2)
    ans = F(a * b, a + b)
    return Q(f"A can do a job in {a} days and B in {b} days. How many days do they take working together?", ans, f"Rates add: 1/{a} + 1/{b}. Time = {a} × {b} ÷ {a + b} = {fmt(ans)}.", [F(a + b, 2), ans + 1, ans + 2])


@T(C, "Work-rate")
def _(r):
    t, a = r.choice([(6, 10), (6, 15), (8, 12), (8, 24), (10, 15), (12, 20), (12, 18), (10, 30), (15, 20), (20, 30), (9, 18), (4, 12), (5, 20), (6, 9), (4, 6), (10, 40), (15, 60), (18, 45), (12, 28), (14, 35), (20, 60), (24, 40), (30, 45), (9, 36), (8, 40), (6, 42), (10, 14), (15, 40), (16, 48), (21, 28)])
    ans = F(t * a, a - t)
    return Q(f"A and B together finish a job in {t} days. A alone needs {a} days. How long does B alone take, in days?", ans, f"B's rate = 1/{t} − 1/{a}. Time = {t} × {a} ÷ ({a} − {t}) = {fmt(ans)}.", [a - t, ans + 2, ans + 5])


@T(C, "Work-rate")
def _(r):
    a, b, k = r.choice([10, 12, 15, 20, 24, 30]), r.choice([12, 15, 18, 20, 30, 36, 40]), r.randint(2, 5)
    left = 1 - F(k, a)
    ans = left * b
    return Q(f"A can finish a job in {a} days and B in {b} days. A works alone for {k} days and then B finishes the job. How many days does B work?", ans, f"Left after A: 1 − {k}/{a} = {fmt(left)}. B takes {fmt(left)} × {b} = {fmt(ans)}.", [b - k, ans + 2, ans + 1])


@T(C, "Efficiency method")
def _(r):
    p = r.choice([10, 20, 25, 50, 60, 100])
    d = r.choice([x for x in (12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 75) if True])
    ans = F(d * 100, 100 + p)
    return Q(f"B takes {d} days to do a job. A is {p}% more efficient than B. How many days does A take?", ans, f"Time scales inversely: {d} × 100 ÷ {100 + p} = {fmt(ans)}.", [d - d * p // 100 if d * p // 100 < d else d - 1, ans + 2, ans + 3])


@T(C, "Efficiency method")
def _(r):
    k = r.randint(2, 4)
    t = r.choice([x for x in range(4, 30)])
    ans = F(k * t * 1 * (k + 1), k) / (k + 1) * (k + 1) / (k + 1)
    a_alone = F(t * (k + 1), k)
    return Q(f"A is {k} times as efficient as B. Together they finish a job in {t} days. How many days does A alone take?", a_alone, f"Rates {k} : 1. Total work = {t} × {k + 1} units. A alone: {t * (k + 1)} ÷ {k} = {fmt(a_alone)}.", [t * (k + 1), a_alone + 2, a_alone + 3])


@T(C, "Efficiency method")
def _(r):
    m1, d1 = r.randint(4, 30), r.randint(4, 40)
    m2 = r.randint(2, 40)
    ans = F(m1 * d1, m2)
    return Q(f"{m1} men finish a job in {d1} days. How many days do {m2} men take?", ans, f"Man-days = {m1 * d1}. Days = {m1 * d1} ÷ {m2} = {fmt(ans)}.", [ans + 2, ans + 1, F(m2 * d1, m1)])


@T(C, "Work & wages")
def _(r):
    a, b = r.sample([6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40], 2)
    k = a + b
    total = k * 100 * r.randint(1, 6)
    return Q(f"A can do a job in {a} days and B in {b} days. They work together and earn ₹{total}. What is A's share?", f"₹{total * b // (a + b)}", f"Wages follow rates, {b} : {a}. A gets {b}/{a + b} × {total} = {total * b // (a + b)}.", [f"₹{total * a // (a + b)}", f"₹{total // 2 + 10}", f"₹{total * b // (a + b) + 100}"])


@T(C, "Work & wages")
def _(r):
    a, b, w = r.randint(2, 15), r.randint(10, 40), r.randint(100, 900)
    return Q(f"{a} workers earn ₹{a * b * w} in {b} days. What is one worker's daily wage?", f"₹{w}", f"{a * b * w} ÷ ({a} × {b}) = {w}.", [f"₹{w + 50}", f"₹{w * 2}", f"₹{w + 25}"])


@T(C, "Work & wages")
def _(r):
    m, d, w = r.randint(3, 20), r.randint(3, 20), r.randint(100, 800)
    m2, d2 = r.randint(3, 20), r.randint(3, 20)
    return Q(f"{m} men earn ₹{m * d * w} in {d} days. At the same rate, what do {m2} men earn in {d2} days?", f"₹{m2 * d2 * w}", f"Daily wage = {w}. Total = {m2} × {d2} × {w} = {m2 * d2 * w}.", [f"₹{m2 * d2 * w + w}", f"₹{m2 * d * w}", f"₹{m * d2 * w + 1}"])


@T(C, "Pipes & cisterns")
def _(r):
    a, b = r.sample([6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60], 2)
    ans = F(a * b, a + b)
    return Q(f"Pipe A fills a tank in {a} hours and pipe B in {b} hours. How long do they take together, in hours?", ans, f"Time = {a} × {b} ÷ {a + b} = {fmt(ans)}.", [F(a + b, 2), ans + 1, ans + 2])


@T(C, "Pipes & cisterns")
def _(r):
    a, b = r.sample(range(4, 40), 2)
    a, b = min(a, b), max(a, b)
    ans = F(a * b, b - a)
    return Q(f"A pipe fills a tank in {a} hours and a leak empties it in {b} hours. With both open, how long does the tank take to fill, in hours?", ans, f"Net rate = 1/{a} − 1/{b}. Time = {a} × {b} ÷ {b - a} = {fmt(ans)}.", [F(a * b, a + b), ans + 2, ans + 1])


@T(C, "Pipes & cisterns")
def _(r):
    a, b, c = r.randint(6, 30), r.randint(6, 30), r.randint(8, 40)
    net = F(1, a) + F(1, b) - F(1, c)
    if net <= 0:
        c = c + 40
        net = F(1, a) + F(1, b) - F(1, c)
    ans = 1 / net
    return Q(f"Pipes A and B fill a tank in {a} and {b} hours, and pipe C empties it in {c} hours. With all three open, how long does it take to fill, in hours?", ans, f"Net rate = 1/{a} + 1/{b} − 1/{c} = {fmt(net)}. Time = {fmt(ans)}.", [1 / (F(1, a) + F(1, b) + F(1, c)), ans + 1, ans + 2])


# =================================================================== Speed
C = "Time, Speed & Distance"


@T(C, "Basic formula")
def _(r):
    s, t = r.randint(10, 120), r.randint(2, 12)
    return Q(f"A car travels {s * t} km in {t} hours. What is its speed in km/h?", s, f"Speed = {s * t} ÷ {t} = {s}.")


@T(C, "Basic formula")
def _(r):
    s = 18 * r.randint(1, 15)
    return Q(f"Convert {s} km/h to m/s.", s * 5 // 18, f"Multiply by 5/18: {s} × 5/18 = {s * 5 // 18}.")


@T(C, "Basic formula")
def _(r):
    s = 5 * r.randint(1, 40)
    return Q(f"Convert {s} m/s to km/h.", s * 18 // 5, f"Multiply by 18/5: {s} × 18/5 = {s * 18 // 5}.")


@T(C, "Basic formula")
def _(r):
    s1 = r.choice([20, 24, 30, 36, 40, 45, 48, 50, 60, 72])
    s2 = s1 + r.choice([4, 5, 6, 10, 12, 15])
    late = r.choice([10, 15, 20, 30])
    d = F(s1 * s2 * late, (s2 - s1) * 60)
    return Q(f"A man reaches {late} minutes late at {s1} km/h and on time at {s2} km/h. What is the distance in km?", d, f"d/{s1} − d/{s2} = {late}/60, so d = {s1} × {s2} × {late} ÷ ({s2 - s1} × 60) = {fmt(d)}.", [d + 5, d + 10, d + 2])


@T(C, "Relative speed")
def _(r):
    a, b, d = 10 * r.randint(2, 8), 10 * r.randint(2, 8), 10 * r.randint(5, 80)
    ans = F(d, a + b)
    return Q(f"Two cars {d} km apart drive towards each other at {a} and {b} km/h. After how many hours do they meet?", ans, f"Closing speed {a + b}. Time = {d} ÷ {a + b} = {fmt(ans)}.", [F(d, abs(a - b) or 7), ans + 1, ans + 2])


@T(C, "Relative speed")
def _(r):
    b = 10 * r.randint(2, 7)
    a = b + 5 * r.randint(1, 6)
    gap = (a - b) * r.randint(1, 8)
    return Q(f"A police car at {a} km/h chases a thief {gap} km ahead moving at {b} km/h. How many hours until it catches up?", gap // (a - b), f"Relative speed {a - b}. Time = {gap} ÷ {a - b} = {gap // (a - b)}.", [F(gap, a + b) + 1, gap // (a - b) + 1, gap // (a - b) + 2])


@T(C, "Trains")
def _(r):
    s = 18 * r.randint(2, 7)
    t = r.randint(6, 40)
    length = s * 5 // 18 * t
    return Q(f"A train running at {s} km/h passes a pole in {t} seconds. How long is the train, in metres?", length, f"{s} km/h = {s * 5 // 18} m/s. Length = {s * 5 // 18} × {t} = {length}.", [s * t, length + 50, length - 20])


@T(C, "Trains")
def _(r):
    s = 18 * r.randint(2, 7)
    t = r.randint(8, 40)
    l = 10 * r.randint(5, 30)
    total = s * 5 // 18 * t
    bridge = total - l
    if bridge <= 0:
        bridge = 50
        total = l + bridge
    ans = F(total, s * 5 // 18)
    return Q(f"A {l} m train at {s} km/h crosses a {bridge} m bridge. How many seconds does it take?", ans, f"Distance = {l} + {bridge} = {total} m; speed = {s * 5 // 18} m/s. Time = {fmt(ans)}.", [F(l, s * 5 // 18), ans + 5, ans + 2])


@T(C, "Trains")
def _(r):
    s1, s2 = 18 * r.randint(2, 5), 18 * r.randint(2, 5)
    l1, l2 = 10 * r.randint(8, 30), 10 * r.randint(8, 30)
    rel = (s1 + s2) * 5 // 18
    ans = F(l1 + l2, rel)
    return Q(f"Trains of {l1} m and {l2} m run towards each other at {s1} and {s2} km/h. How many seconds do they take to cross each other?", ans, f"Relative speed = {rel} m/s. Time = ({l1} + {l2}) ÷ {rel} = {fmt(ans)}.", [F(l1 + l2, abs(s1 - s2) * 5 // 18 or 7), ans + 3, ans + 1])


@T(C, "Boats & streams")
def _(r):
    b, s = r.randint(6, 30), r.randint(1, 5)
    t = r.randint(2, 8)
    return Q(f"A boat's speed in still water is {b} km/h and the stream flows at {s} km/h. How far does it go downstream in {t} hours?", (b + s) * t, f"Downstream speed {b + s}. Distance = {(b + s) * t}.", [(b - s) * t, b * t])


@T(C, "Boats & streams")
def _(r):
    b, s = r.randint(6, 30), r.randint(1, 5)
    return Q(f"A boat goes downstream at {b + s} km/h and upstream at {b - s} km/h. What is the stream's speed?", s, f"Stream = (down − up) ÷ 2 = ({b + s} − {b - s}) ÷ 2 = {s}.", [b, s + 1, s + 2])


@T(C, "Boats & streams")
def _(r):
    b, s = r.randint(8, 30), r.randint(1, 6)
    return Q(f"A boat goes downstream at {b + s} km/h and upstream at {b - s} km/h. What is its speed in still water?", b, f"Boat = (down + up) ÷ 2 = {b}.", [s, b + 1, b - 1])


@T(C, "Races & games")
def _(r):
    race = 100 * r.randint(1, 10)
    lead = 10 * r.randint(1, 9)
    b_run = race - lead
    ans = F(race, b_run)
    x = 100 * r.randint(1, 5)
    return Q(f"In a {race} m race, A beats B by {lead} m. In the same race, how far has B run when A finishes?", f"{b_run} m", f"B has covered {race} − {lead} = {b_run} m when A reaches the line.", [f"{race} m", f"{lead} m", f"{b_run + 10} m"])


@T(C, "Races & games")
def _(r):
    n = r.choice([100, 200, 400, 500, 1000])
    a, b = r.choice([(n // 10, n // 20), (n // 10, n // 5), (n // 20, n // 10), (n // 5, n // 10), (n // 4, n // 5), (n // 20, n // 25)])
    ans = F(n * (a + b) - a * b, n)
    ab, bc = n - a, n - b
    ac = F(ab * bc, n)
    return Q(f"In a {n} m race, A beats B by {a} m, and B beats C by {b} m. By how many metres does A beat C?", fmt(n - ac), f"When A runs {n}, B runs {ab}, and C runs {ab} × {bc}/{n} = {fmt(ac)}. A wins by {fmt(n - ac)} m.", [a + b, fmt(n - ac + 5), abs(a - b) + 1])


@T(C, "Races & games")
def _(r):
    n = r.choice([100, 200, 300, 400, 500, 1000])
    s = r.choice([(3, 2), (4, 3), (5, 4), (5, 3), (2, 1), (7, 5)])
    if n % s[0]:
        n = s[0] * 100
    start = n - n * s[1] // s[0]
    return Q(f"A runs {s[0]}/{s[1]} times as fast as B. In a {n} m race, what head start should A give B so that both finish together?", f"{start} m", f"B can run {s[1]}/{s[0]} of the distance in the same time, i.e. {n * s[1] // s[0]} m. Head start = {start} m.", [f"{start + 10} m", f"{n - start} m", f"{start + 25} m"])


@T(C, "Circular tracks")
def _(r):
    a, b = r.sample([10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 90], 2)
    return Q(f"Two runners take {a} s and {b} s to complete one lap. If they start together, after how many seconds do they first meet at the start?", lcm(a, b), f"LCM of {a} and {b} = {lcm(a, b)}.", [a + b, a * b, lcm(a, b) + a])


@T(C, "Circular tracks")
def _(r):
    l = 100 * r.randint(2, 15)
    a, b = 5 * r.randint(1, 5), 5 * r.randint(1, 5)
    while a == b:
        b = 5 * r.randint(1, 5)
    ans = F(l, a + b)
    return Q(f"On a {l} m circular track, two runners start together in opposite directions at {a} and {b} m/s. When do they first meet, in seconds?", ans, f"Opposite directions: {l} ÷ ({a} + {b}) = {fmt(ans)}.", [F(l, abs(a - b)), ans + 5, ans + 2])


@T(C, "Circular tracks")
def _(r):
    l = 100 * r.randint(2, 15)
    a, b = 5 * r.randint(1, 5), 5 * r.randint(1, 5)
    while a == b:
        b = 5 * r.randint(1, 5)
    ans = F(l, abs(a - b))
    return Q(f"On a {l} m circular track, two runners start together in the same direction at {a} and {b} m/s. When does the faster first lap the slower, in seconds?", ans, f"Same direction: {l} ÷ |{a} − {b}| = {fmt(ans)}.", [F(l, a + b), ans + 5, ans + 10])


@T(C, "Escalators")
def _(r):
    w, e, t = r.randint(1, 3), r.randint(1, 3), 5 * r.randint(2, 12)
    return Q(f"A man walks up a moving escalator at {w} steps/s while it moves at {e} steps/s, reaching the top in {t} s. How many steps are visible on the escalator?", (w + e) * t, f"Same direction: speeds add. Steps = ({w} + {e}) × {t} = {(w + e) * t}.", [w * t, e * t, abs(w - e) * t + 3])


@T(C, "Escalators")
def _(r):
    w, e = r.randint(3, 6), r.randint(1, 2)
    t = 5 * r.randint(2, 12)
    return Q(f"A boy walks down an up-moving escalator at {w} steps/s while it moves up at {e} steps/s, taking {t} s. How many steps are visible?", (w - e) * t, f"Opposite directions: ({w} − {e}) × {t} = {(w - e) * t}.", [(w + e) * t, w * t, e * t + 5])


@T(C, "Escalators")
def _(r):
    n = r.choice([40, 60, 80, 90, 100, 120, 150])
    t = r.choice([x for x in (10, 15, 20, 30) if n % x == 0])
    s = n // t
    e = r.randint(1, s - 1) if s > 1 else 1
    w = s - e
    if w <= 0:
        w, e = 1, 1
    return Q(f"An escalator with {n} visible steps carries a person walking up at {w} steps/s, and it moves at {e} steps/s. How long does the trip take, in seconds?", F(n, w + e), f"Combined speed {w + e} steps/s. Time = {n} ÷ {w + e} = {fmt(F(n, w + e))}.", [F(n, w), F(n, e), F(n, w + e) + 5])


# =================================================================== Algebra
C = "Algebra"


@T(C, "Linear equations")
def _(r):
    a, x, b = r.randint(2, 12), r.randint(-15, 25), r.randint(-30, 30)
    sign = "+" if b >= 0 else "−"
    return Q(f"Solve {a}x {sign} {abs(b)} = {a * x + b}.", x, f"{a}x = {a * x}, so x = {x}.", [x + 1, x - 2, -x if x else 4])


@T(C, "Linear equations")
def _(r):
    x, y = r.randint(1, 20), r.randint(1, 20)
    return Q(f"If x + y = {x + y} and x − y = {x - y}, find x.", x, f"Add the equations: 2x = {2 * x}, so x = {x}.", [y if y != x else x + 2, x + 1, x + 2])


@T(C, "Linear equations")
def _(r):
    a, b, x, y = r.randint(2, 5), r.randint(2, 5), r.randint(1, 15), r.randint(1, 15)
    c, d = r.randint(2, 7), r.randint(1, 4)
    while a * d == b * c:
        c = r.randint(2, 7)
    return Q(f"If {a}x + {b}y = {a * x + b * y} and {c}x + {d}y = {c * x + d * y}, find y.", y, f"Solving by elimination gives x = {x}, y = {y}.", [x if x != y else y + 1, y + 1, y + 2])


@T(C, "Quadratic equations")
def _(r):
    a, b = r.randint(-12, 15), r.randint(-12, 15)
    s, p = a + b, a * b
    t2 = f"{'+' if -s >= 0 else '−'} {abs(s)}x"
    t3 = f"{'+' if p >= 0 else '−'} {abs(p)}"
    return Q(f"What are the roots of x² {t2} {t3} = 0?", f"{a} and {b}", f"Two numbers with sum {s} and product {p} are {a} and {b}.", [f"{-a} and {-b}", f"{a + 1} and {b - 1}", f"{a} and {-b}" if b else f"{a} and 1", f"{a + 2} and {b + 2}"])


@T(C, "Quadratic equations")
def _(r):
    a, b, c = r.randint(1, 9), r.randint(-20, 20), r.randint(-20, 20)
    ans = F(-b, a)
    return Q(f"What is the sum of the roots of {a}x² {'+' if b >= 0 else '−'} {abs(b)}x {'+' if c >= 0 else '−'} {abs(c)} = 0?", ans, f"Sum = −b/a = {fmt(ans)}.", [F(b, a), F(c, a), ans + 1])


@T(C, "Quadratic equations")
def _(r):
    b, c = r.randint(-12, 12), r.randint(-20, 20)
    d = b * b - 4 * c
    ans = "Two distinct real roots" if d > 0 else "Equal real roots" if d == 0 else "No real roots"
    return Q(f"What is the nature of the roots of x² {'+' if b >= 0 else '−'} {abs(b)}x {'+' if c >= 0 else '−'} {abs(c)} = 0?", ans, f"Discriminant b² − 4ac = {b * b} − {4 * c} = {d}.", ["Two distinct real roots", "Equal real roots", "No real roots", "One positive root only"])


@T(C, "Inequalities")
def _(r):
    a, x, b = r.randint(2, 9), r.randint(-9, 15), r.randint(1, 20)
    return Q(f"Solve {a}x + {b} > {a * x + b}.", f"x > {x}", f"Subtract {b}, then divide by {a}: x > {x}.", [f"x < {x}", f"x > {x + 1}", f"x ≥ {x}", f"x > {x - 1}"])


@T(C, "Inequalities")
def _(r):
    a, x, b = r.randint(2, 9), r.randint(-9, 15), r.randint(1, 20)
    return Q(f"Solve {b} − {a}x < {b - a * x}.", f"x > {x}", f"Dividing by a negative number flips the sign: −{a}x < {-a * x} gives x > {x}.", [f"x < {x}", f"x > {-x if x else 3}", f"x ≤ {x}", f"x < {-x if x else 3}"])


@T(C, "Inequalities")
def _(r):
    a, b = r.randint(1, 12), r.randint(1, 15)
    return Q(f"How many integers satisfy |x − {a}| ≤ {b}?", 2 * b + 1, f"x runs from {a - b} to {a + b}, which is {2 * b + 1} integers.", [2 * b, 2 * b - 1, b + 1])


@T(C, "Progressions (AP, GP, HP)")
def _(r):
    a, d, n = r.randint(-5, 20), r.randint(2, 12), r.randint(8, 60)
    return Q(f"In an AP with first term {a} and common difference {d}, find term number {n}.", a + (n - 1) * d, f"a + (n − 1)d = {a} + {n - 1} × {d} = {a + (n - 1) * d}.", [a + n * d, a + (n - 2) * d, n * d])


@T(C, "Progressions (AP, GP, HP)")
def _(r):
    a, d, n = r.randint(1, 20), r.randint(1, 10), r.randint(6, 50)
    ans = n * (2 * a + (n - 1) * d) // 2
    return Q(f"Find the sum of the first {n} terms of the AP {a}, {a + d}, {a + 2 * d}, ...", ans, f"n/2 × (2a + (n − 1)d) = {n}/2 × ({2 * a} + {(n - 1) * d}) = {ans}.", [n * (a + (n - 1) * d), ans + d, ans - n])


@T(C, "Progressions (AP, GP, HP)")
def _(r):
    a, g, n = r.randint(1, 5), r.choice([2, 3]), r.randint(4, 10)
    return Q(f"Find the sum of the first {n} terms of the GP {a}, {a * g}, {a * g * g}, ...", a * (g ** n - 1) // (g - 1), f"a(rⁿ − 1)/(r − 1) = {a} × ({g}^{n} − 1) ÷ {g - 1} = {a * (g ** n - 1) // (g - 1)}.", [a * g ** n, a * g ** (n - 1), a * (g ** n - 1)])


@T(C, "Progressions (AP, GP, HP)")
def _(r):
    a, b = r.randint(1, 15), r.randint(2, 20)
    while a == b:
        b = r.randint(2, 20)
    ans = F(2 * a * b, a + b)
    return Q(f"Find the harmonic mean of {a} and {b}.", ans, f"HM = 2ab/(a + b) = {2 * a * b} ÷ {a + b} = {fmt(ans)}.", [F(a + b, 2), ans + 1, ans + 2])


@T(C, "Functions")
def _(r):
    a, b, x = r.randint(2, 9), r.randint(-9, 9), r.randint(-6, 9)
    return Q(f"If f(x) = {a}x {'+' if b >= 0 else '−'} {abs(b)}, find f({x}).", a * x + b, f"{a} × {x} {'+' if b >= 0 else '−'} {abs(b)} = {a * x + b}.")


@T(C, "Functions")
def _(r):
    a, b, c, d, x = r.randint(2, 5), r.randint(1, 7), r.randint(2, 5), r.randint(1, 7), r.randint(-4, 6)
    return Q(f"If f(x) = {a}x + {b} and g(x) = {c}x + {d}, find f(g({x})).", a * (c * x + d) + b, f"g({x}) = {c * x + d}; f of that = {a * (c * x + d) + b}.", [c * (a * x + b) + d, a * x + b + c * x + d, a * (c * x + d)])


@T(C, "Functions")
def _(r):
    a, b, c, x = r.randint(1, 4), r.randint(-6, 6), r.randint(-9, 9), r.randint(-5, 6)
    return Q(f"If f(x) = {a}x² {'+' if b >= 0 else '−'} {abs(b)}x {'+' if c >= 0 else '−'} {abs(c)}, find f({x}).", a * x * x + b * x + c, f"{a} × {x * x} + ({b}) × ({x}) + ({c}) = {a * x * x + b * x + c}.")


# =================================================================== Permutation & Combination
C = "Permutation & Combination"
WORDS = ["APPLE", "BANANA", "LEVEL", "MANGO", "TIGER", "ORANGE", "SCHOOL", "LETTER", "COFFEE", "PEPPER", "MOTHER", "BALLOON", "SUCCESS", "COMPUTER", "TEACHER", "STUDENT", "JAVA", "SPRING", "GARDEN", "SILENT", "ENGINE", "PRINCE", "BOTTLE", "WINDOW", "SUMMER", "KITTEN", "MIRROR", "PEOPLE", "LITTLE", "PURPLE", "RABBIT", "MEMBER", "MONKEY", "ARMY", "NATION", "RATIO", "DATA", "STACK", "QUEUE", "GRAPH", "MATRIX", "PUZZLE", "SYSTEM", "NETWORK", "PROCESS"]


@T(C, "Fundamental counting principle")
def _(r):
    s, p, c = r.randint(2, 9), r.randint(2, 9), r.randint(2, 7)
    return Q(f"A person owns {s} shirts, {p} trousers and {c} pairs of shoes. How many different outfits are possible?", s * p * c, f"Multiply the choices: {s} × {p} × {c} = {s * p * c}.", [s + p + c, s * p + c, s * c + p])


@T(C, "Fundamental counting principle")
def _(r):
    n = r.randint(2, 6)
    rep = r.choice([True, False])
    if rep:
        return Q(f"How many {n + 1}-digit PIN codes can be made from the digits 1 to {n + 3}, with repetition allowed?", (n + 3) ** (n + 1), f"Each of {n + 1} places has {n + 3} choices: {(n + 3) ** (n + 1)}.", [perm(n + 3, n + 1), (n + 1) ** (n + 3), (n + 3) * (n + 1)])
    return Q(f"How many {n + 1}-digit numbers can be made from the digits 1 to {n + 3}, without repetition?", perm(n + 3, n + 1), f"{n + 3} × {n + 2} × ... for {n + 1} places = {perm(n + 3, n + 1)}.", [(n + 3) ** (n + 1), comb(n + 3, n + 1), perm(n + 3, n)])


@T(C, "Fundamental counting principle")
def _(r):
    a, b = r.randint(2, 15), r.randint(2, 15)
    c = r.randint(2, 15)
    return Q(f"A menu has {a} starters, {b} mains and {c} desserts. A diner picks exactly one dish from any one section. How many choices are there?", a + b + c, f"\"Or\" means add: {a} + {b} + {c} = {a + b + c}.", [a * b * c, a * b + c, a + b * c])


@T(C, "Permutations")
def _(r):
    w = r.choice(WORDS)
    tot = factorial(len(w))
    for ch in set(w):
        tot //= factorial(w.count(ch))
    rep = {ch: w.count(ch) for ch in sorted(set(w)) if w.count(ch) > 1}
    note = f" Divide by the repeats: {', '.join(f'{k} × {v}' for k, v in rep.items())}." if rep else " All letters are different."
    return Q(f"In how many ways can the letters of the word {w} be arranged?", tot, f"{len(w)}! = {factorial(len(w))}.{note} The result is {tot}.", [factorial(len(w)), tot * 2 if rep else tot // 2, tot + len(w)])


@T(C, "Permutations")
def _(r):
    n, k = r.randint(5, 12), r.randint(2, 4)
    return Q(f"In how many ways can {k} students be seated in a row of {n} chairs?", perm(n, k), f"{n}P{k} = {perm(n, k)}.", [comb(n, k), n ** k, perm(n, k - 1)])


@T(C, "Permutations")
def _(r):
    n = r.randint(4, 8)
    return Q(f"{n} friends stand in a line. In how many arrangements do two particular friends stand next to each other?", 2 * factorial(n - 1), f"Treat the pair as one: {n - 1}! × 2 = {2 * factorial(n - 1)}.", [factorial(n), factorial(n - 1), factorial(n) - 2 * factorial(n - 1)])


@T(C, "Combinations")
def _(r):
    n, k = r.randint(5, 20), r.randint(2, 5)
    return Q(f"How many teams of {k} can be chosen from {n} players?", comb(n, k), f"Order does not matter: {n}C{k} = {comb(n, k)}.", [perm(n, k), comb(n, k - 1), comb(n, k + 1)])


@T(C, "Combinations")
def _(r):
    m, w, a, b = r.randint(4, 9), r.randint(3, 8), r.randint(1, 3), r.randint(1, 3)
    return Q(f"A committee has {a} men from {m} and {b} women from {w}. How many committees are possible?", comb(m, a) * comb(w, b), f"{m}C{a} × {w}C{b} = {comb(m, a)} × {comb(w, b)} = {comb(m, a) * comb(w, b)}.", [comb(m + w, a + b), comb(m, a) + comb(w, b), comb(m, b) * comb(w, a) + 1])


@T(C, "Combinations")
def _(r):
    n = r.randint(5, 25)
    k = r.choice(["handshakes", "diagonals", "lines"])
    if k == "handshakes":
        return Q(f"{n} people at a meeting each shake hands with every other person once. How many handshakes happen?", comb(n, 2), f"{n}C2 = {comb(n, 2)}.", [n * (n - 1), n * n, comb(n, 2) + n])
    if k == "diagonals":
        return Q(f"How many diagonals does a {n}-sided polygon have?", n * (n - 3) // 2, f"n(n − 3)/2 = {n * (n - 3) // 2}.", [comb(n, 2), n * (n - 3), n * (n - 2) // 2])
    return Q(f"How many straight lines can be drawn through {n} points, no three of which lie on a line?", comb(n, 2), f"Each pair gives one line: {n}C2 = {comb(n, 2)}.", [n * (n - 1), comb(n, 3), n * n // 2 + 1])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(4, 10)
    return Q(f"In how many ways can {n} people sit around a round table?", factorial(n - 1), f"Fix one person: ({n} − 1)! = {factorial(n - 1)}.", [factorial(n), factorial(n - 2), factorial(n - 1) // 2])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(4, 10)
    return Q(f"In how many different ways can {n} beads be arranged on a necklace, if flipping it gives the same necklace?", factorial(n - 1) // 2, f"(n − 1)!/2 = {factorial(n - 1) // 2}.", [factorial(n - 1), factorial(n) // 2, factorial(n - 1) // 2 + n])


@T(C, "Circular permutations")
def _(r):
    n = r.randint(4, 9)
    return Q(f"{n} people sit around a round table. In how many ways can two particular people sit together?", 2 * factorial(n - 2), f"Pair as one: ({n} − 2)! × 2 = {2 * factorial(n - 2)}.", [factorial(n - 1), factorial(n - 2), factorial(n - 1) - 2 * factorial(n - 2) + 1])


@T(C, "Distribution problems")
def _(r):
    n, k = r.randint(3, 12), r.randint(2, 5)
    return Q(f"In how many ways can {n} identical sweets be given to {k} children, if a child may get none?", comb(n + k - 1, k - 1), f"Stars and bars: C({n + k - 1}, {k - 1}) = {comb(n + k - 1, k - 1)}.", [k ** n, comb(n - 1, k - 1), n ** k])


@T(C, "Distribution problems")
def _(r):
    n, k = r.randint(5, 14), r.randint(2, 5)
    return Q(f"In how many ways can {n} identical sweets be given to {k} children so that each child gets at least one?", comb(n - 1, k - 1), f"C({n - 1}, {k - 1}) = {comb(n - 1, k - 1)}.", [comb(n + k - 1, k - 1), k ** n, comb(n, k)])


@T(C, "Distribution problems")
def _(r):
    n, k = r.randint(3, 8), r.randint(2, 5)
    return Q(f"In how many ways can {n} different letters be posted in {k} letter boxes?", k ** n, f"Each letter has {k} choices: {k}^{n} = {k ** n}.", [n ** k, comb(n + k - 1, k - 1), n * k])


# =================================================================== Probability
C = "Probability"
SUITS = {"a king": 4, "a heart": 13, "a red card": 26, "a face card": 12, "an ace": 4, "a spade": 13, "a black king": 2, "a red ace": 2, "the queen of spades": 1, "a black card": 26, "a 7": 4, "a number card from 2 to 10": 36, "a king or a queen": 8, "a heart or a spade": 26, "an ace or a king or a queen": 12, "a red face card": 6, "a diamond": 13, "a club": 13}


@T(C, "Basic probability")
def _(r):
    a, b, c = r.randint(2, 12), r.randint(2, 12), r.randint(2, 12)
    ans = F(a, a + b + c)
    return Q(f"A bag has {a} red, {b} blue and {c} green balls. What is the probability that one ball drawn at random is red?", ans, f"{a} ÷ {a + b + c} = {fmt(ans)}.", [F(b, a + b + c), F(a, b + c), F(c + 1, a + b + c + 1)])


@T(C, "Basic probability")
def _(r):
    n = r.randint(10, 100)
    d = r.choice([2, 3, 4, 5, 6, 7])
    ans = F(n // d, n)
    return Q(f"A number is picked at random from 1 to {n}. What is the probability that it is divisible by {d}?", ans, f"{n // d} multiples of {d} out of {n}: {fmt(ans)}.", [F(1, d + 1), ans + F(1, n), F(n // d + 2, n)])


@T(C, "Basic probability")
def _(r):
    a, b = r.randint(3, 10), r.randint(3, 10)
    ans = F(comb(a, 2), comb(a + b, 2))
    return Q(f"A box has {a} black and {b} white balls. Two are drawn together. What is the probability that both are black?", ans, f"{a}C2 ÷ {a + b}C2 = {comb(a, 2)} ÷ {comb(a + b, 2)} = {fmt(ans)}.", [F(a, a + b) ** 2, F(a, a + b), F(comb(b, 2), comb(a + b, 2)) + F(1, 50)])


@T(C, "Independent & dependent events")
def _(r):
    a, b = r.choice([F(1, 2), F(1, 3), F(2, 3), F(1, 4), F(3, 4), F(2, 5), F(3, 5), F(1, 5), F(4, 5), F(1, 6), F(5, 6)]), r.choice([F(1, 2), F(1, 3), F(2, 3), F(1, 4), F(3, 4), F(2, 5), F(3, 5), F(1, 5), F(4, 5), F(5, 7), F(2, 7), F(3, 8)])
    return Q(f"A hits a target with probability {fmt(a)} and B with probability {fmt(b)}, independently. What is the probability that both hit?", a * b, f"Independent events multiply: {fmt(a)} × {fmt(b)} = {fmt(a * b)}.", [a + b - a * b, (a + b) / 2, 1 - a * b])


@T(C, "Independent & dependent events")
def _(r):
    a, b = r.choice([F(1, 2), F(1, 3), F(2, 3), F(1, 4), F(3, 4), F(2, 5), F(3, 5), F(1, 5), F(5, 6)]), r.choice([F(1, 2), F(1, 3), F(2, 3), F(1, 4), F(3, 4), F(2, 5), F(3, 5), F(1, 5), F(3, 7), F(5, 8)])
    ans = 1 - (1 - a) * (1 - b)
    return Q(f"A solves a problem with probability {fmt(a)} and B with probability {fmt(b)}, independently. What is the probability that the problem gets solved?", ans, f"1 − P(both fail) = 1 − {fmt(1 - a)} × {fmt(1 - b)} = {fmt(ans)}.", [a * b, 1 - a * b, (1 - a) * (1 - b)])


@T(C, "Independent & dependent events")
def _(r):
    a, b = r.randint(3, 12), r.randint(3, 12)
    ans = F(a, a + b) * F(a - 1, a + b - 1)
    return Q(f"A bag has {a} red and {b} blue balls. Two are drawn one after the other without replacement. What is the probability that both are red?", ans, f"{a}/{a + b} × {a - 1}/{a + b - 1} = {fmt(ans)}.", [F(a, a + b) ** 2, F(a, a + b), F(a * b, (a + b) * (a + b - 1))])


@T(C, "Conditional probability")
def _(r):
    n = r.choice([12, 20, 24, 30, 36, 40, 48, 60, 72, 100, 120])
    d1, d2 = r.sample([2, 3, 4, 5, 6], 2)
    given = n // d1
    both = n // lcm(d1, d2)
    ans = F(both, given)
    return Q(f"A number from 1 to {n} is chosen, and it is known to be a multiple of {d1}. What is the probability that it is also a multiple of {d2}?", ans, f"Multiples of {d1}: {given}. Of both: {both}. So {both}/{given} = {fmt(ans)}.", [F(n // d2, n), F(both, n), ans + F(1, 12)])


@T(C, "Conditional probability")
def _(r):
    a = r.choice([F(1, 2), F(2, 5), F(3, 5), F(3, 10), F(1, 4), F(3, 4), F(7, 10), F(4, 5), F(9, 20), F(11, 20)])
    p = r.choice([F(1, 5), F(1, 4), F(3, 20), F(1, 10), F(3, 25), F(2, 25), F(7, 50)])
    if p >= a:
        p = a / 2
    ans = p / a
    return Q(f"P(A) = {fmt(a)} and P(A and B) = {fmt(p)}. Find P(B given A).", ans, f"P(B | A) = P(A and B) ÷ P(A) = {fmt(ans)}.", [p * a, a - p, ans + F(1, 10)])


@T(C, "Conditional probability")
def _(r):
    b, g = r.randint(10, 40), r.randint(10, 40)
    x, y = r.randint(2, b - 1), r.randint(2, g - 1)
    ans = F(y, x + y)
    return Q(f"A class has {b} boys and {g} girls. {x} boys and {y} girls wear glasses. A student wearing glasses is chosen. What is the probability that it is a girl?", ans, f"Restrict to the {x + y} with glasses: {y}/{x + y} = {fmt(ans)}.", [F(y, g), F(g, b + g), F(y, b + g)])


@T(C, "Cards, dice & coins")
def _(r):
    e, n = r.choice(list(SUITS.items()))
    ans = F(n, 52)
    return Q(f"One card is drawn from a standard pack of 52. What is the probability of getting {e}?", ans, f"{n} favourable of 52: {fmt(ans)}.", [F(n + 1, 52), F(n, 26) if n <= 13 else F(n - 2, 52), F(max(n - 1, 1), 52)])


@T(C, "Cards, dice & coins")
def _(r):
    s = r.randint(2, 12)
    w = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == s)
    kind = r.choice(["equal", "at least", "at most"])
    if kind == "equal":
        return Q(f"Two dice are thrown. What is the probability that the sum is {s}?", F(w, 36), f"{w} of 36 outcomes: {fmt(F(w, 36))}.", [F(w + 1, 36), F(1, 6) if F(w, 36) != F(1, 6) else F(1, 12), F(s, 36) if s != w else F(s + 1, 36)])
    if kind == "at least":
        c = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b >= s)
        return Q(f"Two dice are thrown. What is the probability that the sum is at least {s}?", F(c, 36), f"{c} of 36 outcomes: {fmt(F(c, 36))}.", [F(36 - c + 1, 36), F(c + 2, 37), F(max(c - 1, 1), 36)])
    c = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b <= s)
    return Q(f"Two dice are thrown. What is the probability that the sum is at most {s}?", F(c, 36), f"{c} of 36 outcomes: {fmt(F(c, 36))}.", [F(36 - c + 1, 36), F(c + 2, 37), F(max(c - 1, 1), 36)])


@T(C, "Cards, dice & coins")
def _(r):
    n, k = r.randint(2, 8), None
    k = r.randint(0, n)
    kind = r.choice(["exactly", "at least"])
    if kind == "exactly":
        ans = F(comb(n, k), 2 ** n)
        return Q(f"{n} fair coins are tossed. What is the probability of exactly {k} heads?", ans, f"{n}C{k} ÷ 2^{n} = {comb(n, k)}/{2 ** n} = {fmt(ans)}.", [F(1, 2 ** n) if ans != F(1, 2 ** n) else F(1, n + 1), F(k + 1, n + 2), F(comb(n, k) + 1, 2 ** n)])
    ans = F(sum(comb(n, i) for i in range(k, n + 1)), 2 ** n)
    return Q(f"{n} fair coins are tossed. What is the probability of at least {k} heads?", ans, f"Add {n}Ci for i = {k} to {n}, then divide by {2 ** n}: {fmt(ans)}.", [F(comb(n, k), 2 ** n) if F(comb(n, k), 2 ** n) != ans else F(1, n + 1), F(1, 2 ** n) if ans != F(1, 2 ** n) else F(1, n + 2), F(k + 1, n + 3)])


# =================================================================== Geometry
C = "Geometry"


@T(C, "Lines & angles")
def _(r):
    a = r.randint(10, 170)
    return Q(f"Two angles form a straight line. One is {a}°. What is the other?", f"{180 - a}°", f"Supplementary: 180 − {a} = {180 - a}.", [f"{abs(90 - a) + 3}°", f"{360 - a}°", f"{a}°"])


@T(C, "Lines & angles")
def _(r):
    a = r.randint(5, 85)
    return Q(f"What is the complement of {a}°?", f"{90 - a}°", f"Complementary angles add to 90: {90 - a}.", [f"{180 - a}°", f"{a}°", f"{90 + a}°"])


@T(C, "Lines & angles")
def _(r):
    a = r.randint(20, 160)
    ans, why = r.choice([(a, "Corresponding angles on parallel lines are equal."), (a, "Alternate interior angles on parallel lines are equal."), (180 - a, "Co-interior angles on parallel lines add to 180.")])
    name = "co-interior" if ans != a else ("corresponding" if "Corr" in why else "alternate interior")
    return Q(f"A line crosses two parallel lines. One angle is {a}°. What is its {name} angle?", f"{ans}°", why, [f"{180 - ans}°" if ans != 90 else "45°", f"{(ans + 10) % 180 or 15}°", f"{(ans + 30) % 180 or 25}°"])


@T(C, "Triangles")
def _(r):
    a, b = r.randint(20, 90), r.randint(20, 60)
    return Q(f"Two angles of a triangle are {a}° and {b}°. What is the third?", f"{180 - a - b}°", f"Angles add to 180: {180 - a - b}.", [f"{90 - b if b != a else 40}°", f"{180 - a}°", f"{a + b}°"])


@T(C, "Triangles")
def _(r):
    (x, y, z), k = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41)]), r.randint(1, 8)
    return Q(f"A right triangle has legs {x * k} and {y * k}. What is the hypotenuse?", z * k, f"√({x * k}² + {y * k}²) = {z * k}.", [(x + y) * k, (z + 1) * k, z * k + 2])


@T(C, "Triangles")
def _(r):
    b, h = 2 * r.randint(3, 40), r.randint(3, 40)
    return Q(f"Find the area of a triangle with base {b} and height {h}.", b * h // 2, f"½ × {b} × {h} = {b * h // 2}.", [b * h, b + h, b * h // 2 + b])


@T(C, "Triangles")
def _(r):
    k = r.randint(2, 9)
    a, b, c = k * 3, k * 4, k * 5
    k2 = r.randint(2, 6)
    return Q(f"Two similar triangles have corresponding sides in the ratio {k2} : {k2 + 1}. What is the ratio of their areas?", f"{k2 ** 2} : {(k2 + 1) ** 2}", "Areas are in the ratio of the squares of corresponding sides.", [f"{k2} : {k2 + 1}", f"{k2 ** 3} : {(k2 + 1) ** 3}", f"{2 * k2} : {k2 + 1}"])


@T(C, "Circles")
def _(r):
    a = 2 * r.randint(10, 85)
    return Q(f"An arc subtends {a}° at the centre of a circle. What angle does it subtend at a point on the remaining part of the circle?", f"{a // 2}°", f"Angle at circumference is half the angle at the centre: {a // 2}.", [f"{a}°", f"{180 - a // 2}°", f"{a // 2 + 10}°"])


@T(C, "Circles")
def _(r):
    (x, y, z), k = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17)]), r.randint(1, 5)
    rad, d, half = z * k, x * k, y * k
    return Q(f"A chord is {d} from the centre of a circle of radius {rad}. How long is the chord?", 2 * half, f"Half chord = √({rad}² − {d}²) = {half}. Chord = {2 * half}.", [half, 2 * d, 2 * half + 2])


@T(C, "Circles")
def _(r):
    (x, y, z), k = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]), r.randint(1, 5)
    return Q(f"A tangent is drawn from a point {z * k} away from the centre of a circle of radius {x * k}. How long is the tangent?", y * k, f"Tangent ⟂ radius: √({z * k}² − {x * k}²) = {y * k}.", [z * k + x * k, (z - x) * k, y * k + 2])


@T(C, "Quadrilaterals & polygons")
def _(r):
    n = r.randint(5, 20)
    return Q(f"What is the sum of the interior angles of a {n}-sided polygon?", f"{(n - 2) * 180}°", f"(n − 2) × 180 = {(n - 2) * 180}.", [f"{n * 180}°", f"{(n - 1) * 180}°", f"{(n - 3) * 180}°"])


@T(C, "Quadrilaterals & polygons")
def _(r):
    n = r.choice([3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 72, 90])
    k = r.choice(["exterior", "interior"])
    ans = 360 // n if k == "exterior" else 180 - 360 // n
    return Q(f"What is each {k} angle of a regular polygon with {n} sides?", f"{ans}°", f"Each exterior angle = 360/{n} = {360 // n}. Interior = 180 − exterior.", [f"{180 - ans}°", f"{ans + 5}°", f"{ans + 10}°"])


@T(C, "Quadrilaterals & polygons")
def _(r):
    a, b, h = r.randint(5, 30), r.randint(5, 30), 2 * r.randint(2, 15)
    return Q(f"A trapezium has parallel sides {a} and {b} and height {h}. What is its area?", (a + b) * h // 2, f"½({a} + {b}) × {h} = {(a + b) * h // 2}.", [(a + b) * h, a * b, (a + b) * h // 2 + h])


@T(C, "Quadrilaterals & polygons")
def _(r):
    d1, d2 = 2 * r.randint(3, 25), 2 * r.randint(3, 25)
    return Q(f"A rhombus has diagonals {d1} and {d2}. What is its area?", d1 * d2 // 2, f"½ × {d1} × {d2} = {d1 * d2 // 2}.", [d1 * d2, d1 + d2, d1 * d2 // 4])


@T(C, "Coordinate geometry")
def _(r):
    x, y = r.randint(-10, 10), r.randint(-10, 10)
    (a, b, c), k = r.choice([(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)]), r.choice([1, 2])
    return Q(f"Find the distance between ({x}, {y}) and ({x + a * k}, {y + b * k}).", c * k, f"√({a * k}² + {b * k}²) = {c * k}.", [(a + b) * k, c * k + 1, c * k + 2])


@T(C, "Coordinate geometry")
def _(r):
    x1, y1, x2, y2 = [2 * r.randint(-8, 8) for _ in range(4)]
    return Q(f"Find the midpoint of ({x1}, {y1}) and ({x2}, {y2}).", f"({(x1 + x2) // 2}, {(y1 + y2) // 2})", "Average the coordinates.", [f"({x1 + x2}, {y1 + y2})", f"({(x2 - x1) // 2}, {(y2 - y1) // 2})", f"({(x1 + x2) // 2 + 1}, {(y1 + y2) // 2})", f"({(y1 + y2) // 2}, {(x1 + x2) // 2 + 2})"])


@T(C, "Coordinate geometry")
def _(r):
    x1, y1 = r.randint(-9, 9), r.randint(-9, 9)
    dx, dy = r.randint(1, 9), r.randint(-9, 9)
    ans = F(dy, dx)
    return Q(f"Find the slope of the line through ({x1}, {y1}) and ({x1 + dx}, {y1 + dy}).", ans, f"Rise over run: {dy}/{dx} = {fmt(ans)}.", [F(dx, dy) if dy else F(1, 2), ans + 1, -ans if ans else F(1, 3)])


# =================================================================== Mensuration
C = "Mensuration"


@T(C, "2D figures: area & perimeter")
def _(r):
    l, b = r.randint(5, 80), r.randint(3, 60)
    k = r.choice(["area", "perimeter"])
    ans = l * b if k == "area" else 2 * (l + b)
    return Q(f"Find the {k} of a rectangle {l} m long and {b} m wide.", ans, f"{'l × b' if k == 'area' else '2(l + b)'} = {ans}.", [l * b if k != "area" else 2 * (l + b), l + b, ans + l])


@T(C, "2D figures: area & perimeter")
def _(r):
    rad = 7 * r.randint(1, 15)
    k = r.choice(["area", "circumference"])
    ans = 22 * rad * rad // 7 if k == "area" else 44 * rad // 7
    return Q(f"Using π = 22/7, find the {k} of a circle of radius {rad}.", ans, f"{'πr²' if k == 'area' else '2πr'} = {ans}.", [44 * rad // 7 if k == "area" else 22 * rad * rad // 7, ans + 22, ans * 2])


@T(C, "2D figures: area & perimeter")
def _(r):
    (a, b, c), k = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25), (6, 8, 10)]), r.randint(1, 8)
    s = (a + b + c) * k // 2
    return Q(f"Find the area of a triangle with sides {a * k}, {b * k} and {c * k}.", a * b * k * k // 2, f"It is right-angled, so ½ × {a * k} × {b * k} = {a * b * k * k // 2}. Heron's formula with s = {s} gives the same.", [a * b * k * k, s * k, a * b * k * k // 2 + k])


@T(C, "2D figures: area & perimeter")
def _(r):
    a = r.randint(4, 60)
    k = r.choice([2, 3, 4])
    return Q(f"If each side of a square is multiplied by {k}, by what factor does its area grow?", k * k, f"Area scales with the square: {k}² = {k * k}.", [k, 2 * k, k * k * k], ) if a < 12 else Q(f"A square has side {a}. What is the length of its diagonal, written with √2?", f"{a}√2", f"Diagonal = side × √2.", [f"{a}√3", f"{2 * a}", f"{a * 2}√2", f"{a + 2}√2"])


@T(C, "3D figures: surface area & volume")
def _(r):
    l, b, h = r.randint(2, 30), r.randint(2, 25), r.randint(2, 20)
    k = r.choice(["volume", "total surface area"])
    ans = l * b * h if k == "volume" else 2 * (l * b + b * h + h * l)
    return Q(f"Find the {k} of a cuboid {l} × {b} × {h}.", ans, f"{'l × b × h' if k == 'volume' else '2(lb + bh + hl)'} = {ans}.", [2 * (l * b + b * h + h * l) if k == "volume" else l * b * h, ans + l, l * b + b * h + h * l])


@T(C, "3D figures: surface area & volume")
def _(r):
    a = r.randint(2, 40)
    k = r.choice(["volume", "total surface area", "longest diagonal"])
    if k == "volume":
        return Q(f"Find the volume of a cube of edge {a}.", a ** 3, f"a³ = {a ** 3}.", [6 * a * a, a * a, a ** 3 + a])
    if k == "total surface area":
        return Q(f"Find the total surface area of a cube of edge {a}.", 6 * a * a, f"6a² = {6 * a * a}.", [a ** 3 if a != 6 else 200, 4 * a * a, 6 * a * a + a])
    return Q(f"Find the longest diagonal of a cube of edge {a}.", f"{a}√3", "Diagonal = a√3.", [f"{a}√2", f"{a * 3}", f"{a + 3}√3", f"{a + 1}√2"])


@T(C, "3D figures: surface area & volume")
def _(r):
    rad, h = 7 * r.randint(1, 5), r.randint(3, 30)
    k = r.choice(["volume", "curved surface area"])
    ans = 22 * rad * rad * h // 7 if k == "volume" else 44 * rad * h // 7
    return Q(f"Using π = 22/7, find the {k} of a cylinder of radius {rad} and height {h}.", ans, f"{'πr²h' if k == 'volume' else '2πrh'} = {ans}.", [44 * rad * h // 7 if k == "volume" else 22 * rad * rad * h // 7, ans * 2, ans + 22])


@T(C, "3D figures: surface area & volume")
def _(r):
    rad, h = 7 * r.randint(1, 5), 3 * r.randint(1, 10)
    return Q(f"Using π = 22/7, find the volume of a cone of radius {rad} and height {h}.", 22 * rad * rad * h // 21, f"⅓πr²h = {22 * rad * rad * h // 21}.", [22 * rad * rad * h // 7, 22 * rad * h // 7, 22 * rad * rad * h // 21 + 22])


@T(C, "3D figures: surface area & volume")
def _(r):
    rad = 21 * r.randint(1, 6)
    k = r.choice(["volume", "surface area"])
    ans = 88 * rad ** 3 // 21 if k == "volume" else 88 * rad * rad // 7
    return Q(f"Using π = 22/7, find the {k} of a sphere of radius {rad}.", ans, f"{'4/3 πr³' if k == 'volume' else '4πr²'} = {ans}.", [88 * rad * rad // 7 if k == "volume" else 88 * rad ** 3 // 21, ans + 88, ans // 2])


# =================================================================== Trigonometry
C = "Trigonometry"
TABLE = {("sin", 0): "0", ("sin", 30): "1/2", ("sin", 45): "1/√2", ("sin", 60): "√3/2", ("sin", 90): "1",
         ("cos", 0): "1", ("cos", 30): "√3/2", ("cos", 45): "1/√2", ("cos", 60): "1/2", ("cos", 90): "0",
         ("tan", 0): "0", ("tan", 30): "1/√3", ("tan", 45): "1", ("tan", 60): "√3"}
VALUES = {("sin", 0): F(0), ("sin", 30): F(1, 2), ("cos", 60): F(1, 2), ("cos", 0): F(1), ("sin", 90): F(1), ("tan", 45): F(1), ("tan", 0): F(0), ("cos", 90): F(0)}
SQ = {("sin", 0): F(0), ("sin", 30): F(1, 4), ("sin", 45): F(1, 2), ("sin", 60): F(3, 4), ("sin", 90): F(1), ("cos", 0): F(1), ("cos", 30): F(3, 4), ("cos", 45): F(1, 2), ("cos", 60): F(1, 4), ("cos", 90): F(0), ("tan", 0): F(0), ("tan", 30): F(1, 3), ("tan", 45): F(1), ("tan", 60): F(3)}


@T(C, "Ratios & identities")
def _(r):
    f, a = r.choice(list(TABLE))
    wrong = [v for v in dict.fromkeys(TABLE.values()) if v != TABLE[(f, a)]]
    r.shuffle(wrong)
    return Q(f"What is the value of {f} {a}°?", TABLE[(f, a)], f"Standard table value: {f} {a}° = {TABLE[(f, a)]}.", wrong)


@T(C, "Ratios & identities")
def _(r):
    k1, k2 = r.sample(list(SQ), 2)
    a, b = r.randint(1, 4), r.randint(1, 4)
    ans = a * SQ[k1] + b * SQ[k2]
    return Q(f"Find the value of {a} {k1[0]}²{k1[1]}° + {b} {k2[0]}²{k2[1]}°.", ans, f"{a} × {fmt(SQ[k1])} + {b} × {fmt(SQ[k2])} = {fmt(ans)}.", [ans + 1, ans + F(1, 2), ans + F(1, 4)])


@T(C, "Ratios & identities")
def _(r):
    x, y, z = r.choice([(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (4, 3, 5), (12, 5, 13), (15, 8, 17), (24, 7, 25), (21, 20, 29), (40, 9, 41)])
    f = r.choice(["cos", "tan", "cosec", "sec", "cot"])
    ans = {"cos": F(y, z), "tan": F(x, y), "cosec": F(z, x), "sec": F(z, y), "cot": F(y, x)}[f]
    return Q(f"If sin θ = {x}/{z}, with θ acute, find {f} θ.", ans, f"The sides are {x}, {y}, {z}. So {f} θ = {fmt(ans)}.", [F(x, z), F(z, y) if f != "sec" else F(y, x), F(y, x) if f != "cot" else F(x, y), F(z, x) if f != "cosec" else F(y, z)])


@T(C, "Ratios & identities")
def _(r):
    a = r.randint(1, 89)
    k = r.choice([1, 2, 3, 4, 5, 6, 7])
    f = r.choice(["sin", "tan", "sec"])
    g = {"sin": "cos", "tan": "cot", "sec": "cosec"}[f]
    return Q(f"Find the value of {k} × {f} {a}° ÷ {g} {90 - a}°.", k, f"{f} A = {g} (90° − A), so the ratio is 1 and the answer is {k}.", [k + 1, 0, k * 2])


@T(C, "Heights & distances")
def _(r):
    h = r.randint(5, 150)
    ang = r.choice([45, 30, 60])
    d = {45: str(h), 30: f"{h}√3", 60: f"{h}/√3"}[ang]
    return Q(f"The angle of elevation of the top of a {h} m tower from a point on the ground is {ang}°. How far is the point from the tower?", f"{d} m", f"Distance = height ÷ tan {ang}° = {d}.", [f"{h}√2 m", f"{2 * h} m", f"{h + 10} m", f"{h}√3 m", f"{h}/√3 m", f"{h} m"])


@T(C, "Heights & distances")
def _(r):
    d = r.randint(5, 150)
    ang = r.choice([45, 30, 60])
    h = {45: str(d), 30: f"{d}/√3", 60: f"{d}√3"}[ang]
    return Q(f"From a point {d} m from the foot of a tower, the angle of elevation of the top is {ang}°. How tall is the tower?", f"{h} m", f"Height = distance × tan {ang}° = {h}.", [f"{2 * d} m", f"{d}√2 m", f"{d + 10} m", f"{d}√3 m", f"{d}/√3 m", f"{d} m"])


@T(C, "Heights & distances")
def _(r):
    l = 2 * r.randint(3, 40)
    return Q(f"A ladder {l} m long leans against a wall at 60° to the ground. How far is its foot from the wall?", f"{l // 2} m", f"Distance = {l} × cos 60° = {l // 2}.", [f"{l} m", f"{l // 2}√3 m", f"{l // 2 + 2} m"])


# =================================================================== Calendar & Clock
C = "Calendar & Clock"
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


@T(C, "Calendar")
def _(r):
    import datetime
    y, m, d = r.randint(1950, 2045), r.randint(1, 12), r.randint(1, 28)
    day = datetime.date(y, m, d)
    ans = day.strftime("%A")
    return Q(f"What day of the week was or will be {day.strftime('%d %B %Y')}?", ans, f"Count odd days from a known date. {day.strftime('%d %B %Y')} falls on a {ans}.", [x for x in DAYS if x != ans][:3] if False else r.sample([x for x in DAYS if x != ans], 3))


@T(C, "Calendar")
def _(r):
    i, n = r.randint(0, 6), r.randint(10, 500)
    ans = DAYS[(i + n) % 7]
    return Q(f"Today is {DAYS[i]}. What day will it be after {n} days?", ans, f"{n} mod 7 = {n % 7}. Move {n % 7} days ahead of {DAYS[i]}: {ans}.", r.sample([x for x in DAYS if x != ans], 3))


@T(C, "Calendar")
def _(r):
    y = r.randint(1600, 2400)
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    return Q(f"Is {y} a leap year?", "Yes" if leap else "No", f"{y} {'is' if leap else 'is not'} a leap year: a year divisible by 4 is a leap year unless it is a century year not divisible by 400.", ["Yes" if not leap else "No", "Only in the Julian calendar", "Cannot be determined"])


@T(C, "Calendar")
def _(r):
    i = r.randint(0, 6)
    y = r.randint(1901, 2099)
    leap = (y + 1) % 4 == 0
    shift = 2 if leap else 1
    ans = DAYS[(i + shift) % 7]
    return Q(f"1 March {y} is a {DAYS[i]}. What day is 1 March {y + 1}?", ans, f"From 1 March {y} to 1 March {y + 1} is {365 + (1 if leap else 0)} days, which is {shift} odd day{'s' if shift > 1 else ''}. So it is {ans}.", r.sample([x for x in DAYS if x != ans], 3))


@T(C, "Clock angles")
def _(r):
    h, m = r.randint(1, 12), r.choice(range(0, 60, 2))
    a = abs(30 * (h % 12) + F(m, 2) - 6 * m)
    a = min(a, 360 - a)
    return Q(f"What is the smaller angle between the hands of a clock at {h}:{m:02d}?", f"{fmt(a)}°", f"|30 × {h % 12} − 5.5 × {m}| = {fmt(a)}, taking the smaller side.", [f"{fmt(a + 15)}°", f"{fmt(abs(a - 12) if a != 12 else 40)}°", f"{fmt(360 - a)}°"])


@T(C, "Clock angles")
def _(r):
    h = r.randint(1, 11)
    ans = F(60 * h, 11)
    return Q(f"At what time after {h} o'clock do the hands first coincide, in minutes past {h}?", ans, f"Minute hand gains 5.5° per minute. Minutes = {30 * h} ÷ 5.5 = {fmt(ans)}.", [5 * h, ans + 1, F(60 * h, 12)])


@T(C, "Clock angles")
def _(r):
    n = r.choice([12, 24, 36, 48, 60, 72, 6, 18, 30])
    return Q(f"How many times do the hands of a clock coincide in {n} hours?", n * 11 // 12 if n % 12 == 0 else fmt(F(n * 11, 12)), "They coincide 11 times in every 12 hours.", [n, n * 2, n - 2]) if n % 12 == 0 else Q(f"Through how many degrees does the hour hand turn in {n} hours?", f"{n * 30}°", "The hour hand turns 30° each hour.", [f"{n * 6}°", f"{n * 60}°", f"{n * 15}°"])


@T(C, "Fast & slow clocks")
def _(r):
    g, n = r.randint(1, 12), r.randint(2, 30)
    return Q(f"A clock gains {g} minutes every day. How many minutes will it be ahead after {n} days?", g * n, f"{g} × {n} = {g * n}.", [g + n, g * n + g, g * n - g])


@T(C, "Fast & slow clocks")
def _(r):
    g = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15])
    h = r.choice([x for x in range(2, 49) if x % 2 == 0])
    return Q(f"A clock loses {g} minutes every hour. It shows the right time at 12 noon. By how many minutes is it behind after {h} hours?", g * h, f"{g} × {h} = {g * h}.", [g + h, g * h + g, g * (h - 1)])


@T(C, "Fast & slow clocks")
def _(r):
    g = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30])
    return Q(f"A clock gains {g} minutes a day. After how many days will it again show the correct time (12 hours ahead)?", 720 // g, f"It must gain 720 minutes. 720 ÷ {g} = {720 // g}.", [1440 // g, 360 // g, 720 // g + 2])


# =================================================================== Sets
C = "Set Theory & Venn Diagrams"


@T(C, "Union, intersection & complement")
def _(r):
    a, b = r.randint(10, 80), r.randint(10, 80)
    i = r.randint(1, min(a, b) - 1)
    return Q(f"n(A) = {a}, n(B) = {b} and n(A ∩ B) = {i}. Find n(A ∪ B).", a + b - i, f"{a} + {b} − {i} = {a + b - i}.", [a + b, a + b + i, a + b - 2 * i])


@T(C, "Union, intersection & complement")
def _(r):
    u = r.randint(50, 200)
    a = r.randint(10, u - 5)
    return Q(f"A universal set has {u} elements and n(A) = {a}. Find the number of elements in the complement of A.", u - a, f"{u} − {a} = {u - a}.", [a, u + a, u - a + 1])


@T(C, "Union, intersection & complement")
def _(r):
    n = r.randint(2, 10)
    return Q(f"How many subsets does a set with {n} elements have?", 2 ** n, f"2^{n} = {2 ** n}.", [2 ** n - 1, n * n, 2 * n])


@T(C, "Union, intersection & complement")
def _(r):
    a, b = set(r.sample(range(1, 25), 7)), set(r.sample(range(1, 25), 7))
    k = r.choice(["∩", "∪", "−"])
    res = a & b if k == "∩" else a | b if k == "∪" else a - b
    return Q(f"A = {{{', '.join(map(str, sorted(a)))}}} and B = {{{', '.join(map(str, sorted(b)))}}}. How many elements are in A {k} B?", len(res), f"A {k} B has {len(res)} elements: {sorted(res)}.", [len(a & b) + 1 if k != "∩" else len(a | b), len(a | b) if k != "∪" else len(a - b), len(a - b) + 2 if k != "−" else len(b - a) + 3])


@T(C, "Overlapping sets")
def _(r):
    t = r.randint(60, 200)
    a, b = r.randint(20, 80), r.randint(20, 80)
    n = r.randint(1, 20)
    i = a + b + n - t
    while i < 0 or i > min(a, b):
        t, a, b = r.randint(60, 200), r.randint(30, 100), r.randint(30, 100)
        i = a + b + n - t
    return Q(f"Of {t} students, {a} like tea, {b} like coffee and {n} like neither. How many like both?", i, f"Tea or coffee = {t} − {n} = {t - n}. Both = {a} + {b} − {t - n} = {i}.", [a + b - t, n, i + n])


@T(C, "Overlapping sets")
def _(r):
    a, b, c = r.randint(20, 60), r.randint(20, 60), r.randint(20, 60)
    ab, bc, ca = r.randint(5, 15), r.randint(5, 15), r.randint(5, 15)
    abc = r.randint(1, 4)
    ans = a + b + c - ab - bc - ca + abc
    return Q(f"In a group, {a} play cricket, {b} football and {c} hockey. {ab} play cricket and football, {bc} football and hockey, {ca} hockey and cricket, and {abc} play all three. How many play at least one?", ans, f"{a} + {b} + {c} − {ab} − {bc} − {ca} + {abc} = {ans}.", [a + b + c, a + b + c - ab - bc - ca, ans + abc])


@T(C, "Overlapping sets")
def _(r):
    a, b = r.randint(20, 80), r.randint(20, 80)
    i = r.randint(1, min(a, b) - 1)
    k = r.choice(["only A", "exactly one"])
    if k == "only A":
        return Q(f"{a} people use app A, {b} use app B and {i} use both. How many use only app A?", a - i, f"{a} − {i} = {a - i}.", [a, i, b - i if b - i != a - i else a - i + 2])
    return Q(f"{a} people use app A, {b} use app B and {i} use both. How many use exactly one app?", a + b - 2 * i, f"({a} − {i}) + ({b} − {i}) = {a + b - 2 * i}.", [a + b - i, a + b, a + b - 2 * i + 1])


# =================================================================== Other
C = "Other Quantitative Topics"


@T(C, "Number series")
def _(r):
    a, d, k = r.randint(1, 30), r.randint(2, 15), r.randint(4, 6)
    seq = [a + i * d for i in range(k + 1)]
    return Q(f"Find the next number: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], f"Add {d} each time.", [seq[-1] + 1, seq[-1] + d, seq[-1] - 2])


@T(C, "Number series")
def _(r):
    a, g = r.randint(1, 9), r.randint(2, 4)
    seq = [a * g ** i for i in range(6)]
    return Q(f"Find the next number: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], f"Multiply by {g} each time.", [seq[-2] + seq[-3], seq[-1] + g, seq[-1] - a])


@T(C, "Number series")
def _(r):
    a, d, inc = r.randint(1, 20), r.randint(1, 9), r.randint(1, 4)
    seq = [a]
    for i in range(5):
        seq.append(seq[-1] + d + i * inc)
    return Q(f"Find the next number: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], f"The differences go up by {inc} each time.", [seq[-1] + inc, seq[-1] - inc, seq[-2] + d])


@T(C, "Number series")
def _(r):
    s = r.randint(1, 15)
    k = r.choice([2, 3])
    seq = [(s + i) ** k for i in range(5)]
    return Q(f"Find the next number: {', '.join(map(str, seq[:-1]))}, ?", seq[-1], f"{'Squares' if k == 2 else 'Cubes'} of consecutive numbers.", [seq[-1] + 1, seq[-1] + 2 * s + 3, seq[-2] * 2])


@T(C, "Stocks, shares & banker's discount")
def _(r):
    fv, n = r.choice([10, 50, 100]), r.randint(10, 500)
    rate = r.choice([5, 8, 10, 12, 15, 20])
    return Q(f"A company pays a {rate}% dividend on ₹{fv} shares. What does a holder of {n} shares receive?", f"₹{fmt(F(n * fv * rate, 100))}", f"{n} × {fv} × {rate}/100 = {fmt(F(n * fv * rate, 100))}.", [f"₹{n * fv}", f"₹{fmt(F(n * rate, 1))}", f"₹{fmt(F(n * fv * rate, 100) + 50)}"])


@T(C, "Stocks, shares & banker's discount")
def _(r):
    mv, fv = r.choice([80, 90, 110, 120, 125, 150, 160, 200, 250]), 100
    rate = r.choice([5, 6, 8, 10, 12, 15, 20])
    ans = F(rate * fv * 100, mv * 100)
    y = F(rate * fv, mv)
    return Q(f"A ₹{fv} share pays {rate}% dividend and is bought at ₹{mv}. What is the yield on the money invested?", f"{float(y):.2f}%", f"Dividend {rate} ÷ price {mv} × 100 = {float(y):.2f}%.", [f"{rate}%", f"{float(y) + 1:.2f}%", f"{float(y) - .5:.2f}%"])


@T(C, "Stocks, shares & banker's discount")
def _(r):
    bill, rate, t = 1000 * r.randint(1, 40), r.choice([4, 5, 6, 8, 10, 12]), r.choice([3, 6, 9, 12])
    bd = F(bill * rate * t, 1200)
    return Q(f"Find the banker's discount on a bill of ₹{bill} due in {t} months at {rate}% per year.", f"₹{fmt(bd)}", f"BD = simple interest on the face value = {bill} × {rate}/100 × {t}/12 = {fmt(bd)}.", [f"₹{fmt(bd * 2)}", f"₹{fmt(bd + 25)}", f"₹{fmt(bd + 60)}"])


SUFF = ["Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are needed", "Either statement alone is sufficient", "Both together are still not sufficient"]


@T(C, "Data sufficiency")
def _(r):
    x, y = r.randint(2, 40), r.randint(2, 40)
    return Q(f"What is the value of x? (1) x + y = {x + y}. (2) x − y = {x - y}.", SUFF[2], "Neither alone fixes x, as each has two unknowns. Together they give x.", [SUFF[0], SUFF[1], SUFF[4]])


@T(C, "Data sufficiency")
def _(r):
    x, y = r.randint(2, 40), r.randint(2, 40)
    return Q(f"What is the value of x? (1) {3}x = {3 * x}. (2) x + y = {x + y}.", SUFF[0], "Statement 1 gives x directly. Statement 2 has two unknowns.", [SUFF[1], SUFF[2], SUFF[3]])


@T(C, "Data sufficiency")
def _(r):
    b, h = 2 * r.randint(2, 20), r.randint(2, 20)
    return Q(f"What is the area of a triangle? (1) Its base is {b}. (2) Its height is {h}.", SUFF[2], f"Area needs both: ½ × {b} × {h}.", [SUFF[0], SUFF[1], SUFF[3]])


@T(C, "Data sufficiency")
def _(r):
    k = r.randint(2, 30)
    return Q(f"What is A's age? (1) A is {k} years older than B. (2) B is older than C.", SUFF[4], "Neither statement ties any age to a number.", [SUFF[0], SUFF[1], SUFF[2]])


@T(C, "Data sufficiency")
def _(r):
    n = r.randint(2, 40)
    return Q(f"Is the integer x even? (1) x + {2 * n} is even. (2) {2 * n + 1}x is even.", SUFF[3], f"Adding an even number keeps parity, so (1) shows x is even. Multiplying by an odd number keeps parity, so (2) does too.", [SUFF[0], SUFF[1], SUFF[2]])
