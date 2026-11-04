@part py-core-7 | Core Python · Part 7: Functional Python: Iterators, Generators and Comprehensions | core-python
## Comprehensions

A comprehension builds a list, set, dictionary or generator from an iterable in one readable expression. It is Python's answer to Java streams for most everyday work.

```python Comprehensions.py
nums = range(10)
print([n * n for n in nums if n % 2 == 0])                    # list comprehension with a filter
print({n % 3 for n in nums})                                  # set comprehension
print({word: len(word) for word in ["tea", "coffee"]})        # dict comprehension
print([(x, y) for x in "ab" for y in (1, 2)])                 # nested loops, left to right
print([[row * col for col in range(1, 4)] for row in range(1, 4)])   # a 2-D table
print(sum(n for n in nums if n % 2))                          # generator expression: no list is built

labels = ["even" if n % 2 == 0 else "odd" for n in range(4)]  # conditional EXPRESSION goes before `for`
print(labels)

import re
lines = ["id=7", "junk", "id=12"]
print([int(m[1]) for line in lines if (m := re.match(r"id=(\d+)", line))])   # walrus: match once, use twice

x = "outer"
squares = [x * x for x in range(3)]                           # the loop variable does not leak (Python 3)
print(squares, x)
```

```output
```

Rules: write `[expression for item in iterable if condition]`; keep it to one `for` and one `if` for readability (two nested `for` loops are the practical limit); use a normal loop when the body needs statements, side effects or several steps. Use a **generator expression** (parentheses, or bare inside a call such as `sum(...)`) when you only iterate once, because it creates items lazily and uses constant memory.

!tip Comprehension versus map and filter :: `[f(x) for x in xs if p(x)]` is clearer than `list(map(f, filter(p, xs)))` and just as fast. Reach for `map` only with an existing named function (`map(str.strip, lines)`). Never use a comprehension just for side effects (`[print(x) for x in xs]`): it builds a throw-away list.

??  What is the difference between a list comprehension and a generator expression?
=> Square brackets build the whole list in memory immediately; parentheses build a generator that produces one item at a time when asked. Use the generator form when you pass the result to `sum`, `any`, `max`, `join` or loop over it once, because it uses O(1) memory.
??  Does the loop variable of a comprehension leak into the enclosing scope?
=> Not in Python 3: a comprehension has its own scope. (In Python 2 list comprehensions leaked their variable.) PEP 709 inlines comprehensions for speed in 3.12 but keeps this isolation.
??  Write a one-liner that flattens `[[1, 2], [3], [4, 5]]`.
=> `[x for sub in nested for x in sub]` (read the `for` clauses in the same order as nested loops), or `list(itertools.chain.from_iterable(nested))`, which is faster and clearer for deeper use.

## Lambdas, `functools` and `operator`

A `lambda` is an anonymous function limited to **one expression**. Use it for short throwaway callbacks (`key=`, `sorted`, GUI and event handlers); use `def` for anything you would name or test.

```python Functools.py
from functools import cache, cached_property, partial, reduce, singledispatch
from operator import add, itemgetter, mul

print(reduce(add, [1, 2, 3, 4]), reduce(mul, [1, 2, 3, 4], 1), list(map(lambda x: x ** 2, [1, 2, 3])))
print(list(filter(None, [0, 1, "", "a", [], [0]])))              # None as predicate keeps truthy items

def power(base, exponent):
    return base ** exponent

square, cube = partial(power, exponent=2), partial(power, exponent=3)
print(square(5), cube(2), square.func is power, square.keywords)

@cache                                                           # unbounded memoisation (3.9+)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(60), fib.cache_info().currsize)

@singledispatch
def render(value):
    return f"object {value!r}"

@render.register
def _(value: int):
    return f"int {value}"

@render.register
def _(value: list):
    return "list of " + ", ".join(render(v) for v in value)

print(render(3), render("x"), render([1, "y"]))

class Report:
    def __init__(self):
        self.runs = 0

    @cached_property                                             # computed once per instance, then stored
    def expensive(self):
        self.runs += 1
        return 42

r = Report()
print(r.expensive, r.expensive, r.runs)
print(sorted([(1, "b"), (2, "a")], key=itemgetter(1)))
```

```output
```

| Tool | Purpose |
| --- | --- |
| `functools.partial` | Fix some arguments of a function, producing a new callable |
| `functools.reduce` | Fold an iterable into one value (prefer `sum`, `max`, `"".join` when they exist) |
| `functools.cache`, `lru_cache(maxsize)` | Memoise a **pure** function; arguments must be hashable |
| `functools.singledispatch` | Choose an implementation by the type of the first argument |
| `functools.cached_property` | A lazy attribute computed once per instance |
| `functools.wraps` | Keep a decorated function's name and docstring (Part 11) |
| `operator.itemgetter`, `attrgetter`, `add`... | Function versions of operators and lookups, faster than lambdas |

!warning Caching has a memory cost and a purity rule :: `@cache` keeps every result forever, so it can leak memory on unbounded inputs; use `lru_cache(maxsize=...)`. It is correct only for **pure** functions (the same input always gives the same output, no side effects). Caching a method on `self` also keeps the instance alive.

??  When is a lambda the wrong choice?
=> When the logic needs more than one expression, a name for readability, a docstring, a test or a useful traceback (lambdas appear as `<lambda>`). Assigning a lambda to a name (`f = lambda x: ...`) is flagged by linters: write a `def` instead.
??  What does `functools.partial` do and when do you use it?
=> It returns a new callable with some arguments pre-filled: `partial(power, exponent=2)` is `square`. Use it to adapt a function to a callback interface that passes fewer arguments (`threading.Thread(target=partial(send, to=user))`) without writing a lambda.
??  Why must arguments to a function decorated with `@cache` be hashable?
=> The cache is a dictionary keyed by the arguments, so `list` or `dict` arguments raise `TypeError: unhashable type`. Convert to tuples or frozensets, or cache an inner function that takes hashable keys.

## Iterators and the Iteration Protocol

Two protocols power every `for` loop:

- An **iterable** has `__iter__()` returning an iterator (lists, strings, dicts, files, `range`, generators).
- An **iterator** has `__next__()` returning the next item and raising `StopIteration` when finished, and `__iter__()` returning itself.

A `for` loop is shorthand for:

```python Protocol.py
numbers = [10, 20, 30]
iterator = iter(numbers)            # numbers.__iter__()
while True:
    try:
        item = next(iterator)       # iterator.__next__()
    except StopIteration:
        break
    print(item)

print(next(iterator, "exhausted"))  # an exhausted iterator stays exhausted

class Countdown:
    """An iterator class: remembers where it is."""
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

print(list(Countdown(3)), sum(Countdown(4)))
c = Countdown(2)
print(list(c), list(c))              # iterators are ONE-SHOT: the second pass is empty

lines = iter(["a", "b", "", "c"])
print(list(iter(lambda: next(lines), "")))      # iter(callable, sentinel): call until the sentinel appears
```

```output
```

The difference between an iterable and an iterator explains a famous bug: an **iterator can be consumed only once**, but a list (an iterable) can produce a fresh iterator every time.

```python OneShot.py
data = (x * x for x in range(3))          # a generator is an iterator
print(sum(data), sum(data))                # the second sum sees nothing

numbers = [1, 2, 3]                        # a list is an iterable: a new iterator each time
print(sum(numbers), sum(numbers))

pairs = zip("ab", [1, 2])
print(list(pairs), list(pairs))            # zip, map, filter, file objects, reversed: all one-shot
```

```output
```

!interview What happens when you iterate a dict while modifying it? :: Dictionary iterators check the dict's size: adding or removing keys during a `for` raises `RuntimeError: dictionary changed size during iteration`. Iterate over a copy (`for k in list(d)`) or build a new dict. Changing a *value* for an existing key is allowed. Lists do not raise, but removing items from a list while iterating it skips elements, which is a classic bug.

??  What is the difference between an iterable and an iterator?
=> An iterable can produce iterators (`__iter__`) and can be looped over repeatedly. An iterator is the stateful object that yields items with `__next__`, remembers its position and is exhausted after one pass. Every iterator is also iterable (returns itself).
??  Why does `sum(gen)` give 0 the second time?
=> A generator is an iterator: its state moved to the end during the first pass, so a second pass finds nothing. Re-create the generator, or store the data in a list when you need several passes.
??  How does a `for` loop work internally?
=> It calls `iter(obj)` once to get an iterator, then repeatedly calls `next()` on it, running the body for each value and stopping quietly when `StopIteration` is raised. A `for` over a type with only `__getitem__` falls back to the sequence protocol.

## Generators

A **generator function** contains `yield`. Calling it does not run the body: it returns a generator object (an iterator) that runs **until the next `yield`, pauses with all local state intact, and resumes** on the following `next()`. That gives lazy evaluation with almost no code.

```python Generators.py
import sys

def countdown(n):
    print("start")
    while n > 0:
        yield n               # pause here, hand a value out
        n -= 1
    print("finished")

gen = countdown(3)
print(type(gen).__name__, "nothing printed yet")
print(next(gen), next(gen))
print(list(gen))              # runs the rest

def fibonacci():              # an infinite sequence in constant memory
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

from itertools import islice
print(list(islice(fibonacci(), 10)))

big_list = [n for n in range(1_000_000)]
big_gen = (n for n in range(1_000_000))
print(sys.getsizeof(big_gen) < 1000 < sys.getsizeof(big_list))
```

```output
```

### Pipelines: process huge data in constant memory

```python Pipeline.py
import io

log = io.StringIO("""2026-11-04 INFO start
2026-11-04 ERROR db timeout
2026-11-04 INFO ping
2026-11-05 ERROR disk full
2026-11-05 ERROR db timeout
""")

def lines(source):
    for line in source:                      # a file object is a lazy iterator of lines
        yield line.rstrip("\n")

def errors(rows):
    return (r for r in rows if " ERROR " in r)

def messages(rows):
    return (r.split(" ", 2)[2] for r in rows)

pipeline = messages(errors(lines(log)))     # nothing has run yet
from collections import Counter
print(Counter(pipeline))
```

```output
```

Each stage pulls one item at a time from the previous one, so you can process a 50 GB log with a few kilobytes of memory, and stop early (`any`, `next`, `islice`) without reading the rest.

### `send`, `yield from` and return values

```python Advanced.py
def running_average():
    total, count, average = 0, 0, None
    while True:
        value = yield average                 # `yield` is also an expression: it receives sent values
        total += value
        count += 1
        average = total / count

avg = running_average()
next(avg)                                     # prime: run to the first yield
print(avg.send(10), avg.send(20), avg.send(60))
avg.close()

def inner():
    yield 1
    yield 2
    return "inner result"                     # becomes the value of `yield from`

def outer():
    result = yield from inner()               # delegate: forwards values, receives the return value
    yield f"got {result}"

print(list(outer()))

def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)           # recursion with yield from
        else:
            yield item

print(list(flatten([1, [2, [3, [4]], 5]])))
```

```output
```

Generators that receive values with `send` are the ancestors of `async`/`await` coroutines (Part 9): both are functions that can **suspend and resume**. `yield from` delegates to a sub-generator, forwarding values and capturing its `return` value.

!realworld Generators everywhere in backend code :: Reading a large CSV or an S3 object line by line, paging through a database cursor (`yield` rows in chunks), streaming an HTTP response (`StreamingResponse(generator)` in FastAPI), and FastAPI/pytest **dependencies with `yield`** (setup before, teardown after) are all generators. Knowing that the code after `yield` runs at cleanup is what explains those dependency lifecycles.

??  What is the difference between `return` and `yield` in a function?
=> `return` ends the function and gives back one value. `yield` produces a value and **suspends** the function, keeping its local variables, so it can resume later. A function with `yield` becomes a generator function whose call returns an iterator without running the body.
??  Why use a generator instead of building a list?
=> Lazy evaluation: items are produced on demand, so memory use is O(1), you can model infinite sequences, start processing before the data has all arrived, and stop early. The cost is single-pass access and no `len`/indexing.
??  What does `yield from` do?
=> It delegates to another iterable or generator: values it yields are passed through to the caller, sent values and exceptions are forwarded to it, and when it finishes, its `return` value becomes the result of the `yield from` expression. It is the clean way to compose generators and the model for `await`.

## `itertools`: The Iterator Toolbox

`itertools` provides fast, lazy building blocks written in C. They compose into pipelines without ever building intermediate lists.

```python Itertools.py
import itertools as it
from operator import mul

print(list(it.islice(it.count(10, 5), 4)), list(it.islice(it.cycle("ab"), 5)), list(it.repeat("x", 3)))
print(list(it.chain([1, 2], (3,), "ab")), list(it.chain.from_iterable([[1], [2, 3]])))
print(list(it.accumulate([1, 2, 3, 4])), list(it.accumulate([1, 2, 3, 4], mul)))
print(list(it.pairwise([1, 4, 9, 16])), list(it.batched(range(7), 3)))     # pairwise: 3.10+, batched: 3.12+
print(list(it.takewhile(lambda n: n < 4, range(10))), list(it.dropwhile(lambda n: n < 8, range(10))))
print(list(it.zip_longest("abc", [1, 2], fillvalue="-")))
print(list(it.starmap(pow, [(2, 3), (3, 2)])), list(it.compress("abcd", [1, 0, 1, 0])))

print(list(it.product("ab", [1, 2])))                        # cartesian product
print(list(it.permutations("abc", 2)))                       # ordered, no repeats
print(list(it.combinations("abcd", 2)))                      # unordered
print(len(list(it.combinations_with_replacement("ab", 3))))

people = [("dev", "asha"), ("ops", "ravi"), ("dev", "meera")]
for dept, group in it.groupby(sorted(people), key=lambda p: p[0]):   # input MUST be sorted by the key
    print(dept, [name for _, name in group])
```

```output
```

!warning groupby only groups ADJACENT items :: `itertools.groupby` starts a new group whenever the key changes, so unsorted input gives repeated groups (`dev`, `ops`, `dev`). Sort by the same key first, or collect into a `defaultdict(list)` when order does not matter.

### Aggregations over iterators

`any`, `all`, `sum`, `min`, `max`, `sorted`, `enumerate`, `zip`, `reversed` all accept any iterable and `any`/`all` short-circuit:

```python Aggregates.py
nums = [3, 8, 1, 9, 4]
print(any(n > 8 for n in nums), all(n > 0 for n in nums), sum(n for n in nums if n % 2))
print(max(nums), max(nums, key=lambda n: -n), min(nums, default=None), max([], default="empty"))
print(next((n for n in nums if n > 5), None))              # first match, or a default
print(dict(enumerate("abc", start=1)), list(zip(*[(1, "a"), (2, "b")])))   # zip(*) transposes
```

```output
```

??  Which `itertools` function would you use to generate all pairs of two lists, all orderings of three items, and fixed-size chunks?
=> `product(a, b)` for all pairs, `permutations(items, r)` for orderings, and `batched(iterable, n)` for chunks (Python 3.12+; before that write it with `islice` in a loop).
??  Why does `itertools.groupby` need sorted input?
=> It only compares each element's key with the previous one and starts a new group when the key changes. Equal keys that are not adjacent therefore form separate groups. Sort first by the same key.
??  What is `next((x for x in items if cond(x)), None)` and why is it good?
=> It finds the first matching element lazily and returns `None` (or any default) when there is none. It stops at the first match, unlike a list comprehension, which scans everything, and it avoids a try/except around `next`.

## Closures and a First Look at Decorators

A **closure** is a function that remembers variables from the scope where it was created. Closures are how functions carry configuration, and the mechanism beneath decorators.

```python Closures.py
def multiplier(factor):
    def multiply(x):
        return x * factor            # `factor` is remembered after multiplier() returns
    return multiply

double, triple = multiplier(2), multiplier(3)
print(double(5), triple(5), double.__closure__[0].cell_contents)

# The late-binding trap: closures capture VARIABLES, not values
adders = [lambda x: x + i for i in range(3)]
print([f(10) for f in adders])                 # all see the final i == 2

fixed = [lambda x, i=i: x + i for i in range(3)]    # bind the current value as a default
print([f(10) for f in fixed])
```

```output
```

A **decorator** is a function that takes a function and returns a (usually wrapped) function. The `@name` syntax above a definition is shorthand for `func = name(func)`.

```python Decorators.py
import functools

def counted(func):
    @functools.wraps(func)                       # keep the original name and docstring
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

def retry(times):                                # a decorator FACTORY: takes arguments
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as error:
                    print(f"attempt {attempt} failed: {error}")
            raise ConnectionError("gave up")
        return wrapper
    return decorate

@counted
def add(a, b):
    """Add two numbers."""
    return a + b

failures = iter([ConnectionError("reset"), ConnectionError("timeout")])

@retry(times=3)
def fetch():
    error = next(failures, None)
    if error:
        raise error
    return "payload"

print(add(2, 3), add(4, 5), add.calls, add.__name__, add.__doc__)
print(fetch())
```

```output
```

Part 11 takes decorators much further (class decorators, parameterised and stateful decorators, decorators on methods, async functions). For now remember the three steps: **accept a function, define a wrapper that calls it, return the wrapper**, and always use `functools.wraps`.

!interview The late-binding closure question :: "What does `[lambda: i for i in range(3)]` return when called?" Every lambda returns `2`, because they share the same variable `i` from the enclosing scope and read it when called, not when created. Fix with a default argument (`lambda i=i: i`), `functools.partial`, or a factory function. It is one of the most frequently asked Python quirks.

??  What is a closure, and where do you see one without noticing?
=> A function that keeps references to variables of its defining scope after that scope has finished. Decorators, callbacks, `functools.partial`-like helpers and factory functions (`multiplier(3)`) are all closures; `function.__closure__` exposes the captured cells.
??  Why use `functools.wraps` in a decorator?
=> Without it, the wrapper replaces the original function's `__name__`, `__doc__`, annotations and signature, which breaks debugging, documentation, introspection (FastAPI reads signatures!) and tools such as `inspect`. `wraps` copies that metadata and sets `__wrapped__`.
??  How does a decorator with arguments (`@retry(times=3)`) work?
=> `retry(times=3)` is called first and returns the actual decorator; that decorator is then applied to the function. It is a function that returns a function that returns a wrapper: three levels of nesting.

## Functional Style in Practice

Python is not a pure functional language, and idiomatic Python does not try to be. Borrow the ideas that make code safer and easier to test:

1. **Prefer pure functions** (output depends only on input, no side effects) for logic; keep I/O at the edges.
2. **Do not mutate arguments**; return new values (`sorted` over `sort`, `{**a, "x": 1}` over `a["x"] = 1` when the caller owns `a`).
3. **Use immutable data** (tuples, frozen dataclasses, `frozenset`) for values that are shared.
4. **Compose small functions** with comprehensions, generators and `itertools` instead of long loops with flags.
5. **Stop at readability**: three nested `map`/`filter`/`reduce` calls are worse than a ten-line loop.

```python Orders.py
from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from itertools import groupby
from operator import attrgetter

@dataclass(frozen=True)
class Order:
    id: int
    customer: str
    amount: float
    status: str

orders = [
    Order(1, "asha", 250.0, "paid"), Order(2, "ravi", 99.5, "cancelled"),
    Order(3, "asha", 120.0, "paid"), Order(4, "meera", 800.0, "paid"),
    Order(5, "ravi", 40.0, "paid"),
]

def is_paid(order):
    return order.status == "paid"

paid = [o for o in orders if is_paid(o)]
totals = defaultdict(float)
for o in paid:
    totals[o.customer] += o.amount

top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
print(top)

by_customer = {c: [o.id for o in grp] for c, grp in groupby(sorted(paid, key=attrgetter("customer")), key=attrgetter("customer"))}
print(by_customer)

compose = lambda *fs: reduce(lambda f, g: lambda x: g(f(x)), fs)
clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))
print(clean("  Fresh Python Course  "))
print(sum(o.amount for o in paid) / len(paid))
```

```output
```

!cheat Functional Python cheat sheet ::
- `[expr for x in xs if cond]`, `{k: v for ...}`, `{x for ...}`, `(expr for ...)` (lazy).
- `any`/`all`/`sum`/`min`/`max`/`next(gen, default)` consume iterables and short-circuit.
- Iterator = one-shot; iterable = restartable. `iter()`, `next()`, `StopIteration`.
- `yield` suspends; `yield from` delegates; generator pipelines run in O(1) memory.
- `itertools`: `chain`, `islice`, `product`, `permutations`, `combinations`, `accumulate`, `groupby` (sorted!), `pairwise`, `batched`.
- `functools`: `partial`, `reduce`, `cache`/`lru_cache`, `singledispatch`, `cached_property`, `wraps`.
- Closures capture variables, not values: bind with a default argument.
- Decorator = function in, wrapper out; always `@functools.wraps`.
!end

??  When should you prefer a for loop over a comprehension or functional pipeline?
=> When the body has several statements, side effects, early exits, try/except or accumulates more than one result, and whenever the one-liner would take longer to read than the loop. The goal is clarity; comprehensions are for simple transformations and filters.
??  Is Python good for functional programming?
=> It supports first-class functions, closures, comprehensions, generators and immutable data, but has no tail-call optimisation, limited lambdas, no persistent data structures in the standard library and mutable defaults. Idiomatic Python borrows functional ideas for clarity rather than following a pure functional style.
