@part py-core-4 | Core Python · Part 4: Strings, Text and Time | core-python
## Strings in Depth

A Python `str` is an **immutable sequence of Unicode code points**. There is no separate `char` type: a character is a string of length one. Because strings are immutable, every "modification" returns a new string.

```python StringMethods.py
s = "  Hello, Python World  "
print(s.strip(), "|", s.lstrip(), "|", s.rstrip(), "|")
t = s.strip()
print(t.lower(), t.upper(), t.title(), t.swapcase())
print(t.split(", "), t.split(), t.replace("World", "There"))
print(t.find("Python"), t.find("Java"), t.index("o"), t.count("o"))
print(t.startswith("Hello"), t.endswith(("ld", "rld")), "py" in t.lower())
print("-".join(["a", "b", "c"]), "a,b,,c".split(","), "a b  c".split(" "))
print(t.partition(","), t.rpartition("o"))
print("42".isdigit(), "abc".isalpha(), "ab1".isalnum(), " ".isspace(), "Abc".istitle())
print("py".center(10, "*"), "7".zfill(3), "tab\tsep".expandtabs(4))
```

```output
```

| Task | Use | Avoid |
| --- | --- | --- |
| Check a prefix or suffix | `s.startswith(("http://", "https://"))` | slicing and comparing |
| Remove surrounding whitespace | `s.strip()` (or `strip("chars")`) | regex |
| Split on a delimiter, once | `s.partition("=")` or `s.split("=", 1)` | `s.split("=")` when the value may contain `=` |
| Join many pieces | `"".join(parts)` | `+=` in a loop |
| Case-insensitive compare | `a.casefold() == b.casefold()` | `lower()` (misses `ß`) |
| Replace | `s.replace(old, new)`, `str.translate` for many characters | chained regex |

### Building strings efficiently

```python Join.py
parts = [str(n) for n in range(5)]
print("".join(parts), ",".join(parts))

# Wrong in the worst case: every += may copy the whole string so far (quadratic).
# CPython sometimes optimises it in place, but that is an implementation detail, not a guarantee.
text = ""
for p in parts:
    text += p
print(text)

import io
buffer = io.StringIO()               # for very large or streamed output
for p in parts:
    buffer.write(p)
print(buffer.getvalue())
```

```output
```

Collect the pieces in a list and call `"".join(...)` once (the Python equivalent of `StringBuilder`). Because the pieces must all be `str`, convert numbers first with a comprehension or `map(str, ...)`.

### Immutability, identity and interning

CPython **interns** (shares) some strings: identifier-like literals and single characters, and `sys.intern(s)` does it on request. That is a memory and speed optimisation, so `is` on strings is unreliable: use `==`.

```python Interning.py
import sys

a = "".join(["py", "thon"])
b = "".join(["py", "thon"])
print(a == b, a is b)
print(sys.intern(a) is sys.intern(b))
```

```output
```

!warning Never build a command or a query by string formatting :: `f"SELECT * FROM users WHERE name = '{name}'"` is SQL injection; `os.system(f"ls {path}")` is command injection. Use parameterised queries (`cursor.execute(sql, params)`), `subprocess.run([...], shell=False)` with a list, and `str.format` only with **trusted** format strings: `"{0.__class__}".format(obj)` can read attributes from user-supplied templates.

??  Why is `"".join(parts)` preferred to repeated `+=`?
=> Each `+=` creates a new string and may copy all previous characters, which is quadratic in the worst case. `join` computes the total length once and builds the result in a single pass. CPython sometimes optimises `+=` when it holds the only reference, but that is not guaranteed across implementations.
??  Why use `casefold()` instead of `lower()` for case-insensitive comparison?
=> `casefold` is designed for caseless matching across languages: `"STRASSE".casefold() == "straße".casefold()` is true, while `lower()` leaves `ß` unchanged. It is the right call for comparing user-entered text.
??  What is the difference between `split()` and `split(" ")`?
=> `split()` with no argument splits on runs of any whitespace and drops empty strings, so `"a  b".split()` gives `['a', 'b']`. `split(" ")` splits on every single space, so the same input gives `['a', '', 'b']`.
??  How do you reverse a string, and check for a palindrome ignoring case and punctuation?
=> `s[::-1]` reverses. For the palindrome, build a cleaned string: `c = "".join(ch.casefold() for ch in s if ch.isalnum())` and compare `c == c[::-1]`.

## Regular Expressions

The `re` module searches text by **pattern**. Always write patterns as **raw strings** (`r"..."`) so that backslashes reach the regex engine unchanged.

```python Regex.py
import re

log = "2026-11-04 10:15:32 ERROR payment-svc order=A-1042 amount=1499.50 user=asha@example.com"

print(re.search(r"\d{4}-\d{2}-\d{2}", log).group())
m = re.search(r"order=(?P<order>[A-Z]-\d+) amount=(?P<amount>\d+\.\d+)", log)
print(m.group("order"), float(m["amount"]), m.span(), m.groupdict())
print(re.findall(r"\b[A-Z]{4,}\b", log))
print(re.sub(r"[\w.]+@[\w.]+", "<email>", log)[-30:])
print(re.split(r"\s+", "a  b\tc\nd"))

pattern = re.compile(r"""
    (?P<user>[\w.+-]+)      # local part
    @
    (?P<domain>[\w-]+(?:\.[\w-]+)+)   # domain
""", re.VERBOSE)
print(pattern.fullmatch("asha@example.com").groupdict())
print(pattern.fullmatch("not an email"))

for hit in re.finditer(r"(\w+)=(\S+)", log):
    print(hit.group(1), "->", hit.group(2))
```

```output
```

| Function | Meaning |
| --- | --- |
| `re.search(p, s)` | First match **anywhere** in `s` (a `Match` or `None`) |
| `re.match(p, s)` | Match only at the **start** |
| `re.fullmatch(p, s)` | The **whole** string must match (use this to validate) |
| `re.findall` / `re.finditer` | All matches (list of strings or groups / iterator of `Match`) |
| `re.sub(p, repl, s)` | Replace (the replacement may be a function) |
| `re.split(p, s)` | Split on a pattern |
| `re.compile(p, flags)` | Reuse a pattern; flags: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE` |

Building blocks: `.` any character, `\d \w \s` classes, `[abc]` set, `^ $` anchors, `* + ? {n,m}` repetition, `(...)` group, `(?P<name>...)` named group, `(?:...)` non-capturing, `a|b` alternation, `(?=...)` lookahead. Quantifiers are **greedy** by default (`.*` takes as much as possible); add `?` (`.*?`) for the shortest match.

!warning Regular expressions can hang your server (ReDoS) :: A pattern with nested repetition such as `(a+)+$` takes exponential time on an input like `"aaaa...ab"`, and Python's `re` backtracks. If a pattern runs on untrusted input (an API field, an upload), keep it simple and anchored, limit the input length, avoid nested quantifiers, and consider the third-party `regex` module's timeout or Google's RE2 bindings.

!tip Do not parse everything with regex :: Use `json`, `csv`, `urllib.parse`, `datetime.fromisoformat`, `html.parser` or a real parser for structured formats. Regex is for **patterns inside text** (log lines, identifiers), not for HTML, nested JSON or email validation to the letter of the RFC.

??  What is the difference between `re.match`, `re.search` and `re.fullmatch`?
=> `match` anchors at the start of the string, `search` finds the first match anywhere, and `fullmatch` requires the pattern to match the entire string. For validation use `fullmatch`; people often forget that `match` accepts trailing garbage.
??  What is a greedy versus a lazy quantifier?
=> Greedy quantifiers (`*`, `+`, `{n,m}`) match as much as possible and backtrack if the rest fails; lazy ones (`*?`, `+?`) match as little as possible. On `"<a><b>"`, `<.*>` matches the whole string and `<.*?>` matches `<a>`.
??  Why use raw strings for regex patterns?
=> In a normal string `"\b"` is a backspace character and `"\d"` triggers an invalid-escape warning, so the engine would not see what you meant. `r"\b\d+"` passes the backslashes through untouched.
??  What is catastrophic backtracking and how do you prevent it?
=> Patterns with nested or overlapping repetition (`(a+)+`, `(.*)*`) can take exponential time on inputs that almost match. Prevent it by simplifying the pattern, anchoring it, using possessive quantifiers or atomic groups (Python 3.11 added both), bounding input length, or using a linear-time engine such as RE2 for untrusted input.

## Unicode, Encodings and Bytes

Python 3 separates **text** (`str`, code points) from **data** (`bytes`, numbers 0 to 255). Turning text into bytes is **encoding**; the reverse is **decoding**. The two are linked by a named encoding, and in practice the encoding to use is **UTF-8**.

```python Encoding.py
import unicodedata

word = "café"
data = word.encode("utf-8")
print(len(word), len(data), data, data.decode("utf-8"))
print("😀", len("😀"), len("😀".encode("utf-8")), "😀".encode("utf-16-le"))

# One visible character, two spellings
composed = "é"
decomposed = "é"
print(composed == decomposed, len(composed), len(decomposed))
print(unicodedata.normalize("NFC", decomposed) == composed)
print(unicodedata.name("é"), unicodedata.category("é"))

# The classic bug: decoding with the wrong encoding
print(data.decode("latin-1"))
print(b"caf\xe9".decode("utf-8", errors="replace"))
try:
    b"caf\xe9".decode("utf-8")
except UnicodeDecodeError as error:
    print("UnicodeDecodeError:", error)
```

```output
```

Four facts to remember:

1. `len(s)` counts **code points**, not bytes and not what a user sees as characters. An emoji with a skin-tone modifier or an accented letter in decomposed form can be several code points.
2. The text `"é"` can be one code point (NFC) or two (NFD). **Normalise** (`unicodedata.normalize("NFC", s)`) before comparing or storing text from different sources.
3. `open()` without `encoding=` uses the **platform default** (often not UTF-8 on Windows), which is why a script behaves differently on two machines. Always write `open(path, encoding="utf-8")`. (PEP 686 makes UTF-8 the default from Python 3.15; until your minimum version is 3.15, be explicit.)
4. HTTP bodies, files and sockets deliver `bytes`; decode at the **boundary** and keep `str` inside your program.

```python Bytes.py
payload = bytes([72, 105, 33])
print(payload, payload.decode(), payload[0], list(payload))
buffer = bytearray(b"abc")
buffer[0] = ord("X")
print(buffer, bytes(buffer), buffer.hex(), bytes.fromhex("4869"))
print((258).to_bytes(2, "big"), int.from_bytes(b"\x01\x02", "little"))
```

```output
```

!realworld Mojibake in production :: Text like `cafÃ©` or `�` in a database or CSV export means UTF-8 bytes were decoded as Latin-1 (or the reverse) somewhere in the chain. The fix is never `str.replace`; it is making every boundary (file open, database connection charset, HTTP `Content-Type`, terminal `PYTHONIOENCODING`) say UTF-8 explicitly.

??  What is the difference between `str` and `bytes`?
=> `str` is Unicode text made of code points; `bytes` is an immutable sequence of integers 0 to 255. `str.encode(enc)` produces `bytes`, and `bytes.decode(enc)` produces `str`. Mixing them (`"a" + b"b"`) raises `TypeError`.
??  Why does `len("é")` sometimes return 2?
=> The accent can be stored as a combining code point after `e` (NFD) instead of one precomposed code point (NFC). Both display the same but have different lengths and compare unequal until you normalise with `unicodedata.normalize`.
??  Why should you always pass `encoding="utf-8"` to `open()`?
=> Without it Python uses the locale's default encoding (for example cp1252 on many Windows machines), so the same code reads or writes different bytes on different machines. Being explicit makes behaviour portable.

## Numbers Beyond the Built-ins

| Need | Module | Notes |
| --- | --- | --- |
| Exact decimals, money, rounding modes | `decimal` | Build from strings; set rounding with `quantize` |
| Exact rational numbers | `fractions` | `Fraction(1, 3)` |
| Maths functions and integer helpers | `math` | `isclose`, `gcd`, `lcm`, `comb`, `perm`, `isqrt`, `prod`, `fsum` |
| Statistics | `statistics` | `mean`, `median`, `stdev`, `quantiles` |
| Random numbers | `random` | **Not secure.** Use for simulations and sampling |
| Secure random values | `secrets` | Tokens, passwords, reset links |
| Fast numeric arrays | NumPy (third party) | Vectorised, memory-compact |

```python Numbers.py
import math
import statistics
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

print(round(2.675, 2), Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
drift = 0.0
for _ in range(10):
    drift += 0.1                              # a plain loop accumulates rounding error
print(drift, sum([0.1] * 10), math.fsum([0.1] * 10))
print(Fraction(1, 3) + Fraction(1, 6), Fraction("0.75"), Fraction(3, 4) * 2)
print(math.gcd(12, 18), math.lcm(4, 6), math.comb(5, 2), math.perm(5, 2), math.isqrt(99), math.prod([1, 2, 3, 4]))
print(math.floor(-1.5), math.ceil(-1.5), math.trunc(-1.5), math.inf > 10 ** 100, math.isnan(math.nan))
data = [2, 4, 4, 4, 5, 5, 7, 9]
print(statistics.mean(data), statistics.median(data), statistics.pstdev(data), statistics.mode(data))

import secrets
token = secrets.token_urlsafe(16)
print(len(token) >= 21, secrets.compare_digest("a", "a"))
```

```output
```

`round(2.675, 2)` gives `2.67` because the float nearest to 2.675 is slightly below it. `Decimal` with an explicit rounding mode gives the `2.68` that an invoice expects. `secrets.compare_digest` compares in constant time, which prevents timing attacks when checking tokens.

!interview Random versus secrets :: `random` uses the Mersenne Twister: fast, reproducible with `random.seed(n)`, **predictable** once enough outputs are seen. Anything an attacker must not guess (session IDs, password reset tokens, API keys, OTPs) comes from `secrets` (or `os.urandom`). Using `random` for a token is a classic security finding.

??  Why use `Decimal` or integers for money instead of `float`?
=> Binary floats cannot represent most decimal fractions exactly, so sums drift (`0.1 + 0.2`) and rounding surprises appear (`round(2.675, 2)`). `Decimal` (built from strings) or an integer count of the smallest unit keeps exact arithmetic, and `quantize` gives explicit rounding rules.
??  What is the difference between `math.fsum` and `sum` for floats?
=> `fsum` tracks partial sums to avoid accumulated rounding error and returns a correctly rounded result. A hand-written `+=` loop over `0.1` ten times drifts to `0.9999999999999999`; the built-in `sum` of floats drifted the same way up to Python 3.11, but since 3.12 it uses compensated summation and also gives `1.0`. `fsum` is the version-independent guarantee.
??  Why is `random` unsuitable for tokens?
=> It is a deterministic pseudo-random generator whose state can be inferred from its output. The `secrets` module draws from the operating system's cryptographically secure source and also offers constant-time comparison.

## Dates and Times

The `datetime` module has `date`, `time`, `datetime`, `timedelta`, `timezone` and (with `zoneinfo`) real time zones. The one rule that prevents most bugs: **store and compute in UTC with timezone-aware values; convert to a local zone only for display.**

```python Dates.py
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

d = date(2026, 11, 4)
print(d, d.weekday(), d.isoformat(), d + timedelta(days=30), (date(2027, 1, 1) - d).days)

now_utc = datetime(2026, 11, 4, 10, 30, tzinfo=timezone.utc)
kolkata = now_utc.astimezone(ZoneInfo("Asia/Kolkata"))
print(now_utc.isoformat(), kolkata.isoformat(), kolkata.utcoffset())

parsed = datetime.fromisoformat("2026-11-04T16:00:00+05:30")
print(parsed == now_utc.replace(hour=10, minute=30), parsed.astimezone(timezone.utc).hour)
print(datetime.strptime("04/11/2026 18:45", "%d/%m/%Y %H:%M"), now_utc.strftime("%a %d %b %Y, %I:%M %p"))

delta = timedelta(hours=36, minutes=15)
print(delta, delta.total_seconds(), now_utc + delta)
print(int(now_utc.timestamp()), datetime.fromtimestamp(0, tz=timezone.utc))
```

```output
```

Naive datetimes (no `tzinfo`) cannot be compared with aware ones and mean "some unknown local time". Python's `datetime.utcnow()` returns a *naive* value and is **deprecated since 3.12**: write `datetime.now(timezone.utc)` instead.

### Daylight saving and calendars

Arithmetic on an aware datetime adds **wall-clock** time inside the same zone and ignores DST jumps. For durations, compute in UTC and convert back:

```python Dst.py
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ny = ZoneInfo("America/New_York")
before = datetime(2026, 3, 8, 1, 30, tzinfo=ny)          # clocks jump from 02:00 to 03:00 that night

wall = before + timedelta(hours=1)                         # wall-clock arithmetic
real = (before.astimezone(timezone.utc) + timedelta(hours=1)).astimezone(ny)
print(wall.isoformat())
print(real.isoformat())

import calendar
print(calendar.monthrange(2028, 2)[1], calendar.isleap(2028), calendar.month_name[11])
```

```output
```

```python Timing.py
import time

start = time.perf_counter()
total = sum(i * i for i in range(100_000))
elapsed = time.perf_counter() - start
print(total, elapsed < 5)                  # print a bool, not the time: timings differ per run

print(time.monotonic() <= time.monotonic())
```

```output
```

Use `time.perf_counter()` to measure durations (high resolution and unaffected by clock changes) and `time.monotonic()` for timeouts. Never subtract two `datetime.now()` values to time code: the wall clock can jump. For benchmarks use `timeit`.

!cheat Date and time rules ::
- Store timestamps in UTC; keep them aware (`datetime.now(timezone.utc)`).
- Convert with `astimezone(ZoneInfo("Region/City"))` only at display time. On Windows install `tzdata`.
- Exchange dates as ISO 8601 strings: `isoformat()` and `fromisoformat()`.
- `timedelta` stores days/seconds/microseconds; there is no month or year delta in the standard library (`dateutil.relativedelta`, or `calendar.monthrange`).
- `strftime` formats, `strptime` parses; `%d %m %Y %H %M %S %z %b %a`.
- Measure with `perf_counter`, time out with `monotonic`, never with `datetime.now()`.
!end

??  What is the difference between a naive and an aware datetime?
=> An aware datetime carries a `tzinfo` and therefore denotes a definite instant; a naive one has none and is ambiguous. They cannot be compared or subtracted. In applications store aware UTC values and convert for display.
??  Why is `datetime.utcnow()` discouraged?
=> It returns a naive datetime that *looks* like UTC but is not marked as such, so it is easily misinterpreted as local time. It is deprecated since 3.12; use `datetime.now(timezone.utc)`.
??  How do you handle daylight saving time correctly?
=> Do the arithmetic in UTC and convert to the user's `ZoneInfo` for display. Avoid adding `timedelta` to local aware datetimes across a transition, and be careful with non-existent (spring forward) and repeated (fall back) local times.
??  How would you add one month to a date?
=> The standard library has no month delta because months have different lengths. Use `dateutil.relativedelta(months=1)`, or compute year and month and clamp the day with `calendar.monthrange(year, month)[1]`.
