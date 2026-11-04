@more
## What Does This Print? Thirty-One Puzzles

These are the output-prediction questions that fill phone screens and online tests. **Predict first, then reveal the answer**: every output below was produced by actually running the code on Python 3.12 when this page was built, so none of it is from memory. Where a result is an implementation detail rather than a language rule, the explanation says so.

!qa
**Puzzle 1.** Aliasing with `+=` and `+`.
```python Puzzle01.py
a = [1, 2]
b = a
b += [3]
c = a
c = c + [4]
print(a, b, c)
```
=>
```output
```
`b += [3]` calls `list.__iadd__`, which extends the **same** list in place, so `a`, `b` share the change. `c = c + [4]` builds a **new** list and rebinds `c`; `a` is untouched.
!end

!qa
**Puzzle 2.** A tuple holding a list.
```python Puzzle02.py
t = ([1], 2)
try:
    t[0] += [9]
except TypeError as error:
    print("TypeError:", error)
print(t)
```
=>
```output
```
`t[0] += [9]` first extends the list in place (the list is mutable) and then tries to store the result back into the tuple (immutable), which fails. Both things happen: the error **and** the changed list.
!end

!qa
**Puzzle 3.** Closures in a loop.
```python Puzzle03.py
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])
```
=>
```output
```
Closures capture the **variable** `i`, not its value, so every lambda reads the final `2` when called. A default argument (`i=i`) evaluates `i` at definition time and freezes the current value.
!end

!qa
**Puzzle 4.** Which keys are equal?
```python Puzzle04.py
d = {1: "int", 1.0: "float", True: "bool"}
print(d, len(d))
```
=>
```output
```
`1 == 1.0 == True` and their hashes agree, so they are one key. The dictionary keeps the **first key object** (`1`) but the **last value** assigned.
!end

!qa
**Puzzle 5.** Chained comparisons.
```python Puzzle05.py
print(1 < 2 < 3, 1 < 3 < 2, 3 > 2 > 1, False == False in [False])
```
=>
```output
```
`a < b < c` means `a < b and b < c` with `b` evaluated once. The last one is `False == False and False in [False]`, which is also `True`. Python's comparison chaining applies to `in`, `is` and `==` too.
!end

!qa
**Puzzle 6.** `finally` with `return` and `continue`.
```python Puzzle06.py
def f():
    try:
        return "try"
    finally:
        print("cleanup")

def g():
    for i in range(3):
        try:
            continue
        finally:
            print("finally", i)
    return "done"

print(f())
print(g())
```
=>
```output
```
`finally` runs **before** the function actually returns, so `cleanup` prints first; the return value was already computed. It also runs on `continue`, `break` and exceptions.
!end

!qa
**Puzzle 7.** Class attributes and inheritance.
```python Puzzle07.py
class A:
    x = 1

class B(A):
    pass

class C(A):
    pass

B.x = 2
A.x = 3
print(A.x, B.x, C.x)
```
=>
```output
```
`B.x = 2` creates a new attribute **on `B`**, shadowing `A.x`. `C` has none of its own, so the lookup falls through to `A`, which now holds 3.
!end

!qa
**Puzzle 8.** A generator is used twice.
```python Puzzle08.py
g = (n * n for n in range(3))
print(list(g), list(g), sum(g))
```
=>
```output
```
A generator is an iterator: the first `list(g)` exhausts it, so the second `list(g)` and `sum(g)` see nothing.
!end

!qa
**Puzzle 9.** `sort` versus `sorted`.
```python Puzzle09.py
nums = [3, 1, 2]
print(nums.sort(), nums, sorted(nums, reverse=True), nums)
```
=>
```output
```
`list.sort()` sorts in place and returns `None`. Arguments are evaluated left to right, so `nums` is already sorted when it is printed the first time, and `sorted(..., reverse=True)` returns a new list without changing `nums`.
!end

!qa
**Puzzle 10.** Slicing beyond the ends.
```python Puzzle10.py
s = "python"
print(repr(s[10:]), s[-100:2], s[::-2], s[4:1:-1])
```
=>
```output
```
Out-of-range **slice** bounds are clipped silently (an out-of-range single *index* would raise `IndexError`). `s[::-2]` walks backwards taking every second character, starting at the end.
!end

!qa
**Puzzle 11.** Truthiness.
```python Puzzle11.py
print(bool("False"), bool(0.0), bool([0]), bool(None), all([]), any([]))
```
=>
```output
```
Any non-empty string and any non-empty list are truthy, whatever they contain. `all([])` is `True` (nothing violates the condition) and `any([])` is `False` (nothing satisfies it).
!end

!qa
**Puzzle 12.** Repeating sequences.
```python Puzzle12.py
print(repr("ab" * 0), repr("ab" * -3), [0] * 3, [[]] * 2 == [[], []])
rows = [[]] * 2
rows[0].append(1)
print(rows)
```
=>
```output
```
Multiplying by zero or a negative number gives an empty sequence. `[[]] * 2` is equal to `[[], []]` but contains the **same** inner list twice, which the second part exposes.
!end

!qa
**Puzzle 13.** `else` on loops.
```python Puzzle13.py
for i in range(3):
    if i == 5:
        break
else:
    print("for: no break")

n = 0
while n < 2:
    n += 1
    if n == 5:
        break
else:
    print("while: condition became false at", n)
```
=>
```output
```
The `else` block of a loop runs when the loop ends **without** `break`: for `for`, when the iterable is exhausted; for `while`, when the condition becomes false.
!end

!qa
**Puzzle 14.** A local that shadows a global.
```python Puzzle14.py
x = 10

def f():
    print(x)
    x = 5

try:
    f()
except UnboundLocalError as error:
    print(error)
```
=>
```output
```
Because `x` is assigned somewhere in `f`, Python treats it as **local for the whole function**, so the first `print(x)` reads a local that has no value yet. Use `global x` (rarely) or pass values in.
!end

!qa
**Puzzle 15.** Equality without hashing.
```python Puzzle15.py
class P:
    def __init__(self, v):
        self.v = v
    def __eq__(self, other):
        return self.v == other.v

try:
    {P(1)}
except TypeError as error:
    print(error)
print(P(1) == P(1), P(1) != P(2))
```
=>
```output
```
Defining `__eq__` without `__hash__` sets `__hash__` to `None`, so instances cannot go into sets or serve as dict keys. `!=` is derived automatically from `__eq__`.
!end

!qa
**Puzzle 16.** Shallow versus deep copies.
```python Puzzle16.py
import copy

a = [[1], [2]]
shallow = copy.copy(a)
deep = copy.deepcopy(a)
a[0].append(99)
print(shallow, deep)
```
=>
```output
```
The shallow copy shares the inner lists with `a`, so the change shows through it; the deep copy has its own inner lists.
!end

!qa
**Puzzle 17.** Unpacking.
```python Puzzle17.py
print(*[1, 2, 3], sep="-")
first, *middle, last = range(5)
print(first, middle, last)
a, (b, *c), d = 1, "xyz", 4
print(a, b, c, d)
```
=>
```output
```
`*` in a call spreads the list into arguments. In an assignment `*middle` collects the leftovers **as a list**; unpacking works on any iterable, including the string `"xyz"`.
!end

!qa
**Puzzle 18.** Set operations.
```python Puzzle18.py
print({1, 2} | {2, 3}, {1, 2} & {2, 3}, {1, 2} - {2, 3}, {1, 2} ^ {2, 3})
try:
    {[1]}
except TypeError as error:
    print(error)
```
=>
```output
```
Union, intersection, difference and symmetric difference. A list is mutable and therefore unhashable, so it cannot be a set element.
!end

!qa
**Puzzle 19.** Unicode digits.
```python Puzzle19.py
print(int("٣"), "٣".isdigit(), int("1_000"), float("1e3"), int(" 7 "))
```
=>
```output
```
`int()` accepts any Unicode decimal digit (this is the Arabic-Indic three), underscores between digits and surrounding whitespace. Never assume input is ASCII; validate format explicitly when it matters.
!end

!qa
**Puzzle 20.** String comparison.
```python Puzzle20.py
print("abc" < "abd", "Z" < "a", "apple" < "Apple", sorted(["b", "A", "a", "B"]))
```
=>
```output
```
Strings compare by **code point**, so every uppercase letter sorts before every lowercase one. For human-friendly ordering sort with `key=str.casefold` (or a locale-aware collation).
!end

!qa
**Puzzle 21.** When a default value is computed.
```python Puzzle21.py
items = [1, 2]

def count(n=len(items)):
    return n

items.append(3)
print(count(), len(items))
```
=>
```output
```
Default values are evaluated **once, when `def` runs**. `len(items)` was 2 at that moment and stays 2 however the list changes later.
!end

!qa
**Puzzle 22.** String identity (an implementation detail).
```python Puzzle22.py
a = "hello world"
b = "hello world"
c = "".join(["hello", " ", "world"])
print(a == c, a is b, a is c)
```
=>
```output
```
`a == c` is true: equal text. `a is b` happens to be true because the compiler stores one constant for both identical literals in the same code object; `a is c` is false because `join` builds a new string. **Never** use `is` to compare strings: this behaviour differs between versions and implementations.
!end

!qa
**Puzzle 23.** `__slots__`.
```python Puzzle23.py
class S:
    __slots__ = ("a",)

s = S()
s.a = 1
try:
    s.b = 2
except AttributeError as error:
    print(error)
```
=>
```output
```
A class with `__slots__` has no per-instance `__dict__`, so only the declared attributes can be set. That saves memory and catches typos.
!end

!qa
**Puzzle 24.** `max`, `min` and ties.
```python Puzzle24.py
words = ["bb", "aa", "c"]
print(max(words, key=len), min(words, key=len), max([], default="none"), sorted(words, key=len))
```
=>
```output
```
With equal keys `max` returns the **first** maximal element (`bb`, not `aa`). `sorted` is stable, so `bb` stays before `aa`. `default=` avoids `ValueError` on an empty iterable.
!end

!qa
**Puzzle 25.** Removing while iterating.
```python Puzzle25.py
a = [1, 2, 3, 4]
for x in a:
    a.remove(x)
print(a)
```
=>
```output
```
The loop advances an internal index while the list shrinks, so every second element is skipped. Iterate over a copy (`for x in list(a)`) or build a new list with a comprehension.
!end

!qa
**Puzzle 26.** Integer division and rounding.
```python Puzzle26.py
print(7 // 2, -7 // 2, 7 % -3, divmod(-7, 2), round(2.5), round(3.5), round(-0.5))
```
=>
```output
```
`//` floors toward minus infinity, `%` takes the sign of the divisor, and `round` uses banker's rounding (ties go to the even neighbour: 2.5 becomes 2, 3.5 becomes 4, -0.5 becomes 0).
!end

!qa
**Puzzle 27.** Operator precedence.
```python Puzzle27.py
print(not 1 == 2, -2 ** 2, 2 ** -1, 1 if 0 else 2 if 0 else 3, 5 // 2 * 2, 2 + 3 * 4 ** 2 // 5)
```
=>
```output
```
`not` binds looser than `==`; `**` binds tighter than unary minus, so `-2 ** 2` is `-(2 ** 2)`; conditional expressions chain to the right; `*` and `//` share a level and go left to right (`4 ** 2` is 16, `3 * 16` is 48, `48 // 5` is 9).
!end

!qa
**Puzzle 28.** Shadowing a method on one instance.
```python Puzzle28.py
class T:
    def f(self):
        return "method"

t = T()
t.f = lambda: "instance"
print(t.f(), T().f())
```
=>
```output
```
Functions are **non-data descriptors**: an attribute in the instance dictionary wins over them. The lambda stored on `t` is called without `self` because it is not bound.
!end

!qa
**Puzzle 29.** `str` versus `repr`.
```python Puzzle29.py
class Tag:
    def __repr__(self):
        return "repr"
    def __str__(self):
        return "str"

t = Tag()
print(t, [t], f"{t}", f"{t!r}", str([t]))
```
=>
```output
```
`print` and f-strings use `str`; containers show their items with `repr`, so a list of tags prints `[repr]`.
!end

!qa
**Puzzle 30.** The walrus operator in a comprehension.
```python Puzzle30.py
data = [1, 5, 8]
print([y for x in data if (y := x * 2) > 5], y)
```
=>
```output
```
An assignment expression inside a comprehension binds the name in the **enclosing** scope (the comprehension's own loop variable `x` does not leak, but `y` does). It holds the last value assigned.
!end

!qa
**Puzzle 31.** Exception context.
```python Puzzle31.py
def risky():
    try:
        raise ValueError("a")
    except ValueError:
        raise KeyError("b")

try:
    risky()
except KeyError as error:
    print(repr(error), "| context:", repr(error.__context__))
```
=>
```output
```
Raising inside an `except` block links the new exception to the one being handled through `__context__` (shown in tracebacks as "During handling of the above exception, another exception occurred"). Use `raise ... from ...` to state the cause explicitly.
!end
