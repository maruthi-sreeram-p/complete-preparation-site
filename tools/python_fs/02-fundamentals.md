@part py-core-2 | Core Python · Part 2: Language Fundamentals | core-python
## Names, Values and Built-in Types

A Python program is a sequence of statements that bind **names** to **objects**. There are no declarations: assigning creates the name, and assigning again rebinds it (possibly to an object of a different type). The built-in types you will use every day:

| Type | Example | Mutable? | Notes |
| --- | --- | --- | --- |
| `int` | `42`, `1_000_000`, `0xFF`, `0b1010` | no | Unbounded; underscores allowed for readability |
| `float` | `3.14`, `1e-3` | no | 64-bit IEEE 754 double, like Java's `double` |
| `complex` | `3 + 4j` | no | Rarely used outside science |
| `bool` | `True`, `False` | no | A subclass of `int` (`True == 1`) |
| `str` | `"text"`, `'text'` | no | Unicode text, no separate `char` type |
| `bytes` | `b"abc"` | no | Raw bytes |
| `NoneType` | `None` | no | The single "no value" object |
| `list`, `tuple`, `dict`, `set`, `frozenset` | `[1]`, `(1,)`, `{"a": 1}`, `{1}` | list, dict, set: yes | Part 6 |

```python Literals.py
big = 1_000_000_000_000
mask = 0b1111_0000
colour = 0xFF8800
speed = 3.0e8
point = 3 + 4j

print(big, mask, colour, speed)
print(abs(point), point.real, point.imag)
print(type(True), isinstance(True, int), True + True)
print(0.1 + 0.2, 0.1 + 0.2 == 0.3)
```

```output
```

`0.1 + 0.2` is not `0.3` in **any** language that uses binary floating point, because 0.1 has no exact binary representation. Never compare floats with `==`; use `math.isclose`, and never use `float` for money. Use `decimal.Decimal` (exact decimal arithmetic) or integers in the smallest unit (paise, cents):

```python Money.py
import math
from decimal import Decimal

print(math.isclose(0.1 + 0.2, 0.3))
print(Decimal("0.1") + Decimal("0.2"), Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal(0.1))          # the float 0.1 really contains this
price_paise = 19_999         # integers in the smallest unit never drift
print(price_paise * 3 / 100)
```

```output
```

!warning Build Decimal from strings, not floats :: `Decimal(0.1)` captures the binary error of the float; `Decimal("0.1")` is exact. A very common review comment in billing code.

### Naming and style (PEP 8)

| Kind | Convention | Example |
| --- | --- | --- |
| Variable, function, method, module | `snake_case` | `total_price`, `read_file` |
| Class | `PascalCase` | `OrderService` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| "Internal" name | leading underscore | `_cache`, `_helper()` |
| Name that avoids a keyword clash | trailing underscore | `class_`, `type_` |

PEP 8 is the community style guide; formatters (`ruff format`, `black`) and linters (`ruff`, `flake8`) enforce it automatically. Indentation is **syntax**: four spaces per level, never tabs mixed with spaces.

### Mutable and immutable, and what "assignment" does

```python Aliasing.py
text = "py"
text += "thon"          # builds a NEW string and rebinds the name
print(text)

items = ["a"]
alias = items
items += ["b"]          # mutates the list in place: alias sees it
print(alias, alias is items)

t = (1, 2)
try:
    t[0] = 9
except TypeError as error:
    print("tuples are immutable:", error)
```

```output
```

!keypoints Names are bound to objects, never declared ;; int is unbounded, float is a double ;; Never compare floats with == and never use float for money ;; bool is an int subclass ;; Indentation is syntax; PEP 8 is the style guide ;; Immutable objects are rebound, mutable objects change in place

??  Why does `0.1 + 0.2 == 0.3` evaluate to `False`, and what do you do instead?
=> 0.1 and 0.2 cannot be stored exactly in binary floating point, so the sum is `0.30000000000000004`. Compare with `math.isclose(a, b)` (a tolerance), and for money use `decimal.Decimal` built from strings or integers in the smallest currency unit.
??  Is `bool` a separate type from `int`?
=> `bool` is a subclass of `int` with exactly two instances, so `True == 1`, `True + True == 2` and `isinstance(True, int)` is true. It surprises people in code like `sum(flags)` (which counts the true values, deliberately) or when a `bool` slips into a place that expected a number.
??  What is the difference between `+=` on a string and `+=` on a list?
=> Strings are immutable, so `s += "x"` creates a new string and rebinds `s`. Lists are mutable, so `lst += [x]` extends the same list object in place (it calls `__iadd__`), which is visible through every other name bound to that list.

## Operators and Expressions

```python Operators.py
print(7 / 2, 7 // 2, 7 % 2, 2 ** 10)          # true division, floor division, modulo, power
print(-7 // 2, -7 % 2, divmod(-7, 2))          # floor division rounds toward minus infinity
print(int(-3.5), round(-3.5), round(2.5), round(3.5))   # int() truncates; round() goes to the even neighbour on a tie
print(-2 ** 2, (-2) ** 2, 2 ** 3 ** 2)         # ** binds tighter than unary minus and is right associative
print(5 & 3, 5 | 3, 5 ^ 3, ~5, 1 << 4, -8 >> 1)
print((7).bit_count(), bin(10), hex(255), oct(8))
```

```output
```

Three differences from Java deserve a mark in the margin: `/` always gives a `float` (use `//` for integer division); `//` and `%` **floor** (so `-7 % 2` is `1`, matching mathematics, where Java gives `-1`); and `round()` uses banker's rounding (a tie goes to the even neighbour).

### Comparison, logic and membership

```python Logic.py
age = 25
print(18 <= age < 65)                  # chained comparison: one expression, age evaluated once
print("" or "default", 0 or 5, [] and 1, "x" and "y")   # and/or return one of their OPERANDS
first, second = [], []
print(None is None, first == second, first is second)
print("py" in "python", 3 in [1, 2, 3], "k" in {"k": 1}, 2 not in (1, 3))

name = None
label = name or "anonymous"            # classic default idiom (careful: also replaces "" and 0)
print(label)
print("even" if age % 2 == 0 else "odd")

if (n := len("hello")) > 3:           # the walrus operator assigns inside an expression
    print("long word of", n, "letters")
```

```output
```

`and` / `or` do not produce booleans; they **return the operand that decided the result** and **short-circuit** (the right side is not evaluated if the left already decides). `x or default` is handy, but it also replaces valid falsy values such as `0` and `""`; use `x if x is not None else default` when those are legitimate.

### Precedence you should know by heart

From tightest to loosest: `**`, unary `-` `~`, `* / // %`, `+ -`, shifts, `&`, `^`, `|`, comparisons (including `in`, `is`), `not`, `and`, `or`, conditional expression, assignment. When unsure, use parentheses: readers will thank you.

!tip Augmented assignment and swapping :: `x += 1`, `x //= 2`, `flags |= MASK` all work. Swap two names without a temporary: `a, b = b, a` (the right side is evaluated into a tuple first).

??  What is the result of `-7 // 2` and `-7 % 2` in Python, and how does Java differ?
=> `-4` and `1`: Python floors the quotient and the remainder takes the sign of the divisor, so `(a // b) * b + a % b == a` always holds. In Java `-7 / 2` is `-3` (truncation) and `-7 % 2` is `-1`.
!qa
What does this print? Explain the second line.
```python ShortCircuit.py
def noisy(value):
    print("evaluating", value)
    return value

print(noisy(0) and noisy(1))
print(noisy(0) or noisy(2))
print(noisy("") or noisy("fallback") or noisy("never"))
```
=>
```output
```
`and` stops at the first falsy operand and returns it; `or` stops at the first truthy operand and returns it. `noisy("never")` is never called, which is the short-circuit that makes guards like `user and user.name` safe.
!end
??  When would `x or default` be a bug?
=> When `x` can legitimately be falsy (`0`, `0.0`, `""`, `[]`, `False`). `count or 10` turns a real count of 0 into 10. Use `10 if count is None else count`.

## Type Conversion and Truthiness

Python converts **explicitly**: you call the type. It rarely converts for you, and only in arithmetic between numeric types (`int` to `float`).

```python Conversions.py
print(int("42"), int(" 7 "), int("1_000"), int("ff", 16), int(3.99), int(True))
print(float("3.5"), float("inf"), float("-inf"), str(3.0), str(10 ** 20))
print(list("abc"), tuple([1, 2]), set("hello") == set("olleh"), dict([("a", 1), ("b", 2)]))
print(1 + 2.5, 2 * True, 10 / 5, type(10 / 5))

for text in ("3.5", "abc", ""):
    try:
        print(int(text))
    except ValueError as error:
        print("ValueError:", error)

nan = float("nan")
print(nan == nan, nan != nan)
```

```output
```

Parsing user input is where conversions fail, so wrap them in `try`/`except ValueError` (Part 5) and report which value was wrong.

### Truthiness

Every object has a truth value, used by `if`, `while`, `and`, `or`, `not`. The **falsy** values are `None`, `False`, numeric zero (`0`, `0.0`, `0j`), and **empty containers** (`""`, `[]`, `()`, `{}`, `set()`, `range(0)`). Everything else is truthy, including `"0"`, `"False"` and a list that contains only falsy items. A class can define `__bool__` or `__len__` to decide for itself.

```python Truthiness.py
for value in (0, 0.0, "", [], {}, None, "0", "False", [0], 1, -1):
    print(f"{value!r:>8} -> {bool(value)}")
```

```output
```

The idiom is `if items:` rather than `if len(items) > 0:` and `if not name:` rather than `if name == "":`. Use `is None` when `None` is meaningful and must be told apart from empty.

!warning bool("False") is True :: Any non-empty string is truthy, so `bool(os.environ["DEBUG"])` is `True` even when the variable is `"false"` or `"0"`. Parse flags explicitly: `value.lower() in {"1", "true", "yes"}`. This causes real production bugs.

??  Is `int("3.5")` valid? What about `int(3.5)`?
=> `int("3.5")` raises `ValueError` because the string is not an integer literal; use `int(float("3.5"))` if you mean it. `int(3.5)` is valid and truncates toward zero to `3`.
??  List the falsy values in Python.
=> `None`, `False`, zero of any numeric type, and empty sequences and collections (`""`, `b""`, `[]`, `()`, `{}`, `set()`, `range(0)`), plus instances whose `__bool__` returns false or whose `__len__` returns 0.
??  Why does `nan == nan` evaluate to False?
=> IEEE 754 defines NaN as unequal to everything, including itself. Test for it with `math.isnan(x)`. This also means a NaN breaks sorting and makes `x in [nan]` depend on identity.

## Control Flow

### if, for, while

```python Flow.py
temperature = 31
if temperature > 35:
    advice = "stay in"
elif temperature > 25:
    advice = "light clothes"
else:
    advice = "jacket"
print(advice)

for i in range(3):                       # 0, 1, 2
    print("step", i)

for position, fruit in enumerate(["apple", "kiwi"], start=1):
    print(position, fruit)

for name, score in zip(["asha", "ravi"], [91, 78]):
    print(f"{name:>5}: {score}")

count = 0
while True:
    count += 1
    if count % 2 == 0:
        continue                         # skip even numbers
    if count > 7:
        break
    print("odd", count)
```

```output
```

`range(start, stop, step)` produces a **lazy sequence** that takes constant memory however long it is; `len(range(10**12))` and `5 in range(10**12)` are instant. `enumerate` gives `(index, item)` pairs and `zip` walks several iterables together (it stops at the shortest; pass `strict=True` to raise if lengths differ).

### The loop `else` clause

A `for` or `while` loop may have an `else` block that runs **only if the loop finished without `break`**. It is the clean way to write "search, and do something if not found":

```python LoopElse.py
def first_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            print("found", n)
            break
    else:
        print("no even number")

first_even([3, 5, 8, 9])
first_even([3, 5, 7])
```

```output
```

### match: structural pattern matching (3.10+)

`match` is not a C-style `switch`. It tests the **shape** of a value and can pull parts out in the same step:

```python Match.py
def describe(command):
    match command:
        case "quit" | "exit":
            return "leaving"
        case ["move", x, y]:
            return f"move to {x},{y}"
        case ["say", *words]:
            return "say " + " ".join(words)
        case {"type": "click", "pos": (x, y)}:
            return f"click at {x},{y}"
        case int(n) if n < 0:
            return "negative number"
        case int() | float():
            return "a number"
        case _:
            return "unknown"

for c in ("quit", ["move", 3, 4], ["say", "hi", "there"],
          {"type": "click", "pos": (5, 6)}, -3, 2.5, "dance"):
    print(describe(c))
```

```output
```

Patterns can be literals, alternatives (`|`), sequences, mappings, class patterns (`Point(x=0, y=y)`), captures (a bare name binds), guards (`if ...`) and the wildcard `_`. A bare name in a pattern **captures**, it does not compare: to compare against a constant use a dotted name (`Color.RED`) or a literal.

!interview Why is there no switch statement? :: Python relied on `if`/`elif` chains and dictionary dispatch (`handlers[command]()`) for 30 years. `match` (PEP 634, Python 3.10) was added for *destructuring* data (parsing messages, ASTs, API payloads), not as a faster `switch`. Know both: a dict of functions for a simple mapping, `match` when the shape of the data decides what to do.

!qa
What does this print? What does `case other` do, and why does the `for` loop's `else` run?
```python Capture.py
def check(value):
    match value:
        case 1:
            return "one"
        case other:
            return f"captured {other}"

print(check(1), check(2), check("x"))

limit = 10
for n in range(3):
    if n == limit:
        break
else:
    print("loop finished without break")
```
=>
```output
```
In `match`, `case other` is a **capture pattern**: it matches anything and binds the name, so it works like `default`. The `for` loop runs to the end because `n == limit` is never true, so no `break` happens and the `else` clause runs.
!end
??  When does a loop's `else` block run?
=> Only when the loop ends normally (the iterable is exhausted or the `while` condition becomes false), not when it is left by `break`. A `return` or an exception also skips it.
??  Why is `for i in range(len(items))` usually a smell, and what replaces it?
=> It indexes by hand, which is verbose and error-prone. Iterate directly (`for item in items`), use `enumerate(items)` when you need the index, `zip` to walk two sequences, and `sorted` / `reversed` when order matters.

## Sequences, Slicing and Unpacking

Strings, lists, tuples, `range` and `bytes` are all **sequences**: they support indexing, slicing, `len`, `in`, `+`, `*` and iteration. (Python has no Java-style array syntax; `list` is the everyday "array", and the `array` module and NumPy handle compact numeric arrays.)

```python Slicing.py
s = "abcdefghij"
print(s[0], s[-1], s[2:5], s[:3], s[7:], s[::2], s[::-1], s[-3:])

nums = [10, 20, 30, 40, 50]
nums[1:3] = [21, 22, 23]          # slice assignment can change the length
print(nums, nums[::-1], len(nums))

copy = nums[:]                    # a shallow copy
copy.append(99)
print(nums == copy, nums is copy)

grid = [[0] * 3 for _ in range(2)]    # correct: independent rows
bad = [[0] * 3] * 2                   # wrong: the same row twice
grid[0][0] = 1
bad[0][0] = 1
print(grid, bad)
```

```output
```

Slices are half-open: `s[start:stop:step]` includes `start` and excludes `stop`; negative indexes count from the end; out-of-range slice bounds are silently clipped (but a single out-of-range *index* raises `IndexError`). Slicing always creates a **new** object of the same type, and that copy is **shallow**: nested objects are shared.

### Unpacking

```python Unpacking.py
point = (3, 4)
x, y = point
first, *rest = [1, 2, 3, 4]
*init, last = "abc"
print(x, y, first, rest, init, last)

(a, b), (c, d) = (1, 2), (3, 4)       # nested
print(a + b + c + d)

def min_max(values):
    return min(values), max(values)    # returns ONE tuple

low, high = min_max([4, 9, 2])
print(low, high)

merged = [*range(3), *"ab"]
config = {**{"debug": False}, **{"debug": True, "port": 8000}}
print(merged, config)
```

```output
```

`*` in an assignment collects the leftover items into a list; `*` and `**` in a call or a literal **spread** an iterable or a mapping. Unpacking is the reason Python functions "return several values": they return one tuple that the caller unpacks.

!realworld The list-of-lists bug that reaches production :: `[[0] * n] * m` looks like a grid but repeats **one** inner list `m` times, so changing one cell changes a whole column. It shows up in dynamic-programming tables and game boards. Always build nested lists with a comprehension: `[[0] * n for _ in range(m)]`.

??  What does `a[::-1]` do, and what is the cost?
=> It slices the whole sequence with step -1, producing a reversed **copy** in O(n) time and memory. Use `reversed(a)` to iterate backwards without copying.
??  What is the difference between a shallow copy and a deep copy?
=> A shallow copy (`list(a)`, `a[:]`, `a.copy()`, `copy.copy(a)`) creates a new outer container that still references the same inner objects. `copy.deepcopy(a)` recursively copies the inner objects as well. Mutating a shared inner list through one copy is visible through the other.
??  How do you swap two variables, and how do you take the first element and the rest of a list?
=> `a, b = b, a` swaps, because the right side builds a tuple before assigning. `first, *rest = items` takes the head and collects the tail into a list.

## Functions

```python Functions.py
def greet(name, greeting="Hello", *, punctuation="!"):
    """Return a greeting. `punctuation` can only be passed by keyword."""
    return f"{greeting}, {name}{punctuation}"

print(greet("Asha"))
print(greet("Asha", "Namaste", punctuation="."))
print(greet(greeting="Hi", name="Ravi"))

def total(*numbers, **options):
    scale = options.get("scale", 1)
    return sum(numbers) * scale

print(total(1, 2, 3), total(1, 2, 3, scale=10))
values = [4, 5]
settings = {"scale": 2}
print(total(*values, **settings))

def power(base, exponent, /):          # positional-only (Python 3.8+)
    return base ** exponent

print(power(2, 5), greet.__doc__)
```

```output
```

Parameter kinds, in the order they must appear: positional-only (before `/`), normal, `*args` (extra positionals, a tuple), keyword-only (after `*` or `*args`), `**kwargs` (extra keyword arguments, a dict). Keyword arguments make calls self-documenting: `connect(host, port=5432, timeout=3)`.

### The mutable default argument trap

Defaults are evaluated **once, when the function is defined**, not on each call:

```python DefaultTrap.py
def add_item(item, bucket=[]):          # BUG: one list shared by every call
    bucket.append(item)
    return bucket

print(add_item("a"), add_item("b"), add_item("c"))

def add_item_fixed(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

print(add_item_fixed("a"), add_item_fixed("b"))
```

```output
```

The fix is always the same: default to `None` and create the mutable object inside the function. Linters (ruff `B006`) flag it.

### Scope: LEGB, global and nonlocal

Python resolves a name by searching **L**ocal, **E**nclosing functions, **G**lobal (module), then **B**uilt-in. Assigning to a name inside a function makes it local for the *whole* function; use `global` or `nonlocal` to rebind an outer name.

```python Scope.py
counter = 0

def broken():
    try:
        counter += 1          # assignment makes `counter` local, but it has no value yet
    except UnboundLocalError as error:
        print("UnboundLocalError:", error)

def make_counter():
    count = 0
    def increment():
        nonlocal count        # rebind the enclosing function's variable
        count += 1
        return count
    return increment

broken()
c = make_counter()
print(c(), c(), c())
```

```output
```

`make_counter` returns a **closure**: `increment` remembers `count` after `make_counter` has returned. Closures, and the decorators built on them, get a full treatment in Parts 7 and 11.

### Functions are objects, and arguments are passed by assignment

```python Objects.py
def modify(items, number):
    items.append(4)       # mutates the caller's list
    number += 1           # rebinds a local name only
    items = ["new"]       # rebinds a local name only

data, n = [1, 2, 3], 10
modify(data, n)
print(data, n)

def square(x): return x * x
handlers = {"square": square, "neg": lambda x: -x, "abs": abs}
print({name: fn(-3) for name, fn in handlers.items()})
print(sorted(["bb", "a", "ccc"], key=len, reverse=True))
```

```output
```

Python is neither "call by value" nor "call by reference": the parameter name is **bound to the same object** the caller passed (call by object reference, or call by assignment). Mutating the object is visible to the caller; rebinding the parameter is not. Functions can be stored in variables and dictionaries, passed to other functions (`key=len`), and returned.

!interview Recursion limit and tail calls :: CPython limits recursion depth to about 1000 frames (`sys.getrecursionlimit()`), raising `RecursionError`, and does **not** optimise tail calls. Convert deep recursion to a loop with an explicit stack, or raise the limit carefully for known-shallow algorithms. Interviewers ask this when you solve tree or DFS problems recursively on large inputs.

!cheat Function rules ::
- Parameter order: positional-only `/` , normal, `*args`, keyword-only, `**kwargs`.
- Defaults are evaluated once at definition time: never use `[]`, `{}` or `set()` as a default.
- No `return` (or bare `return`) gives `None`. Returning several values returns one tuple.
- Name lookup: Local, Enclosing, Global, Built-in. Rebind outer names with `nonlocal` / `global`.
- Arguments are passed by object reference: mutation is shared, rebinding is local.
- `lambda` is a single expression; for anything longer use `def`.
!end

!qa
Predict the output, then explain what each call shares with the others.
```python Shared.py
def append_to(value, target=[]):
    target.append(value)
    return target

first = append_to(1)
second = append_to(2)
print(first, second, first is second)
print(append_to.__defaults__)
```
=>
```output
```
`first` and `second` are the **same list**: the default was created once when `def` ran and is stored in `append_to.__defaults__`, so every call that omits `target` appends to it.
!end
??  What does `def f(a, /, b, *, c)` mean?
=> `a` is positional-only (cannot be passed by name), `b` can be passed either way, and `c` is keyword-only (must be passed by name). Positional-only parameters let an API rename a parameter later without breaking callers; keyword-only parameters force readable call sites.
??  What is a closure?
=> A function that keeps references to variables of the enclosing scopes in which it was defined, even after those scopes have returned. In `make_counter`, `increment` keeps access to `count` through a cell object.
??  Is Python pass-by-value or pass-by-reference?
=> Neither exactly: it passes object references by assignment. The parameter name becomes another name for the caller's object. Mutating a mutable argument is visible to the caller; rebinding the parameter name is not.

## Input, Output and Formatting

### Printing and f-strings

```python Formatting.py
name, price, qty = "Notebook", 1234.5, 3
print(f"{name:<12}|{price:>10,.2f}|{qty:03d}")
print(f"{price * qty:,.1f}", f"{0.256:.1%}", f"{255:#x} {255:08b}")
print(f"{name!r} {name=}", f"{len(name) = }")
print(f"{{literal braces}} and {1 + 2}")

from datetime import date
print(f"{date(2026, 11, 4):%d %b %Y}")

print("a", "b", "c", sep="-", end="!\n")
print("{} costs {:.2f}".format("tea", 12.5), "%s is %d" % ("x", 5))
```

```output
```

An f-string evaluates any expression inside `{}` and applies an optional format spec after the colon: `[[fill]align][sign][#][0][width][,][.precision][type]`. `!r` uses `repr`, and `{x=}` (Python 3.8+) prints the expression and its value, which is a fast debugging trick. Use f-strings for new code; `str.format` and `%` appear in older code and in logging.

### Reading input

```python Input.py
import io
import sys

sys.stdin = io.StringIO("Asha\n42\n")      # simulate what the user would type
name = input("Name? ")
age = int(input("Age? "))
print(f"{name} will be {age + 1} next year")
```

```output
```

`input()` always returns a `str`: convert it, and handle `ValueError`. (The prompt `Name? ` is printed to standard output; the example hides the typing, so the prompts and the answers appear on one line.) Servers do not use `input()`: they read requests, files and environment variables. Command-line tools use `argparse`:

```python Cli.py
import argparse

parser = argparse.ArgumentParser(description="Greet someone")
parser.add_argument("name")
parser.add_argument("--times", type=int, default=1, help="how many greetings")
parser.add_argument("-v", "--verbose", action="store_true")

args = parser.parse_args(["Asha", "--times", "2", "-v"])   # normally: parser.parse_args()
for _ in range(args.times):
    print("Hello,", args.name)
print("verbose:", args.verbose)
```

```output
```

### Multi-line strings, raw strings and repr

```python Strings.py
import textwrap

query = """
    SELECT id, name
    FROM users
    WHERE active = 1
"""
print(textwrap.dedent(query).strip())

path = r"C:\new\table"             # raw string: backslashes are literal
print(path, len(path))
print(str("a\tb"), repr("a\tb"))   # str is for people, repr is for programmers

from pprint import pprint
pprint({"users": [{"id": 1, "roles": ["admin", "dev"]}, {"id": 2, "roles": []}], "total": 2}, width=40)
```

```output
```

Triple-quoted strings span lines (Java's text blocks); `textwrap.dedent` strips the common indentation. `repr(x)` is an unambiguous developer view, `str(x)` is the friendly one; `print` uses `str`, and the REPL echoes `repr`.

!tip Printing to the right place :: `print(..., file=sys.stderr)` writes diagnostics to standard error, `flush=True` forces output immediately (useful in containers), and `logging` (Part 5) is the right tool for anything beyond quick debugging.

??  What is the difference between `str()` and `repr()`?
=> `str()` gives a readable form for end users; `repr()` gives an unambiguous form for developers, ideally one that could rebuild the object. `print` calls `str`, the REPL and tracebacks use `repr`. A class customises them with `__str__` and `__repr__`.
??  How do you print a float with two decimals and thousands separators, left-aligned in a column of width 12?
=> `f"{value:<12,.2f}"`. The spec reads as: align left, width 12, comma separator, two decimal places, fixed-point.
??  How do you read two integers from one line of input?
=> `a, b = map(int, input().split())`. `split()` breaks the line on whitespace, `map(int, ...)` converts each piece, and unpacking assigns them. Wrap it in `try`/`except ValueError` for untrusted input.
