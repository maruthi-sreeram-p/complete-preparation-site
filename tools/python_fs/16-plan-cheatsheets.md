@part py-core-16 | Core Python · Part 16: Study Plan, Cheat Sheets and Quizzes | advanced-python
## The 25-Day, 4-Week Study Plan

Core Python is fifteen Parts. Read straight through without a plan and most people stall in the collections chapters and never reach concurrency or CPython internals, which are exactly the topics that separate a fresher from an experienced developer. This plan fits the whole of Core Python into **25 study days** over four weeks, about **2 to 3 hours a day**, with one rest day each week.

| Block | Time | What you do |
| --- | --- | --- |
| **Read** | 40% | The day's chapters, with a REPL open. Type every example |
| **Run and break** | 30% | Change the examples, predict the output, run, explain the difference |
| **Retrieve** | 30% | Without the page: the chapter's practice questions, the "what does this print" puzzles, then 2 coding problems |

#### The error log

Keep a plain text file called `errors.txt`. For every question you get wrong, write one line: the topic, what you answered, and the correct idea **in your own words**. At the end of each week re-read only that file. Your own mistakes are the most efficient syllabus there is.

### Week 1: the language, objects and design (days 1 to 7)

Goal: you can explain names versus objects, write idiomatic functions and classes, and say what `==`, `is`, mutability and the MRO mean without notes.

| Day | Read | Code focus |
| --- | --- | --- |
| 1 | Part 1: platform, bytecode, object model, toolchain | Create a venv or `uv` project; inspect bytecode with `dis`; the Java crosswalk table |
| 2 | Part 2: names, types, operators, conversions | Floats, `Decimal`, truthiness puzzles; chained comparisons |
| 3 | Part 2: control flow, slicing, unpacking, functions, I/O | `match`; mutable default trap; closures; `argparse` mini-tool |
| 4 | Part 3: classes, properties, inheritance and the MRO | Bank-style class with `@property`; draw an MRO diamond and verify with `__mro__` |
| 5 | Part 3: dunder methods, ABC and Protocol, dataclasses, enums | A `Vector` and a `Money` value object with full comparison and hashing |
| 6 | Re-read the error log; Part 3 practice questions; puzzles 1 to 15 | Predict first, then run each puzzle |
| 7 | Rest, or one DSA problem | |

### Week 2: text, errors, files, collections and iterators (days 8 to 13)

Goal: you handle text and time correctly, write robust file and error handling, and choose the right container with its Big-O.

| Day | Read | Code focus |
| --- | --- | --- |
| 8 | Part 4: strings, regex, Unicode, numbers, dates | A log-line parser with named groups; UTC datetimes with `zoneinfo` |
| 9 | Part 5: exceptions, context managers, logging | A custom exception hierarchy; a `@contextmanager` timer; `logging` configuration |
| 10 | Part 5: files, `pathlib`, serialization, OS interface | Atomic file write; JSON round trip; a safe `subprocess` call |
| 11 | Part 6: lists, dicts, sets, sorting, heaps, deques | `Counter`, `defaultdict`, `heapq` top-k; multi-key sorting |
| 12 | Part 6: implement your own array list, hash map, LRU cache | Write each from memory, then diff with the page |
| 13 | Part 7: comprehensions, iterators, generators, `itertools`, decorators intro | A generator pipeline over a big file; `@retry` decorator |

### Week 3: concurrency, CPython and runtime features (days 14 to 19)

Goal: you can choose between threads, processes and asyncio, explain the GIL and reference counting, and read what a framework does with decorators, descriptors and signatures.

| Day | Read | Code focus |
| --- | --- | --- |
| 14 | Part 8: concurrency concepts, the GIL, threads, locks | The race and deadlock demos; fix them |
| 15 | Part 8: thread pools, futures, processes | `ThreadPoolExecutor` vs `ProcessPoolExecutor` timing on your own machine |
| 16 | Part 9: event loop, tasks, `TaskGroup`, timeouts, semaphores | Async fetcher with a concurrency limit |
| 17 | Part 9: blocking code in async, streams, pitfalls | Reproduce the "blocked loop" bug and fix it with `to_thread` |
| 18 | Part 10: object model, reference counting, GC, leaks, bytecode | A `tracemalloc` leak hunt; `cProfile` a slow function |
| 19 | Part 11: decorators, descriptors, metaclasses, imports, diagnostics | A validated descriptor; an `__init_subclass__` registry; `faulthandler` |

### Week 4: tooling, practice and interviews (days 20 to 25)

Goal: you write tested, typed, linted, packaged code, and you can solve and explain interview problems under time.

| Day | Read | Code focus |
| --- | --- | --- |
| 20 | Part 12: types, modern Python, pytest | Add hints and run `mypy --strict`; write fixtures and `parametrize` |
| 21 | Part 12: packaging, ruff, pre-commit; Part 13 patterns | `pyproject.toml`; the refactor exercise; strategy and observer |
| 22 | Part 13: secure coding; Part 14 Projects A and B | SQL injection and password-hash demos; build the bank and the log analyzer |
| 23 | Part 14 Projects C and D | Concurrent processor and key-value store with tests |
| 24 | Part 15: Q&A banks, puzzles 16 to 31, coding problems | Timed: 3 problems in 60 minutes, spoken aloud |
| 25 | The part-by-part quizzes, then the final mock interview | Score it; write the error log; plan the next stage (DSA and FastAPI) |

!tip After day 25 keep three habits :: Two DSA problems a day (the DSA stage next in this tree), one small project per month that you deploy, and one new standard-library module per week (`itertools`, `functools`, `contextlib`, `pathlib`, `statistics`...). Fluency comes from range, not from re-reading.

??  Name the three blocks of the daily loop and say which one is skipped most often.
=> Read, run-and-break, retrieve. Retrieval (answering without the page) is skipped most often and gives the most learning per minute, because recalling an answer strengthens memory far more than re-reading it.
??  Why keep an error log?
=> Each entry is a personalised list of the ideas you actually misunderstand. Reviewing it weekly directs your time to your weak spots instead of re-reading what you already know.

## Cheat Sheets

These tables are meant to be scanned, not read. They compress the tree into reference pages you can review the night before an interview or keep open while coding. Each says where the full explanation lives.

### Keywords, built-in types and truth values (Parts 1 and 2)

| Group | Keywords (Python 3.12: 35) |
| --- | --- |
| Values | `True`, `False`, `None` |
| Logic | `and`, `or`, `not`, `is`, `in` |
| Flow | `if`, `elif`, `else`, `for`, `while`, `break`, `continue`, `pass`, `match`\*, `case`\* |
| Functions and classes | `def`, `return`, `lambda`, `yield`, `class`, `global`, `nonlocal`, `del` |
| Errors and resources | `try`, `except`, `finally`, `raise`, `assert`, `with`, `as` |
| Modules | `import`, `from` |
| Async | `async`, `await` |

\* soft keywords, usable as names elsewhere (also `type` and `_`).

| Type | Mutable | Hashable | Ordered | Typical use |
| --- | --- | --- | --- | --- |
| `int`, `float`, `bool`, `complex` | no | yes | n/a | numbers (`int` unbounded; money uses `Decimal`) |
| `str` | no | yes | yes | text (Unicode) |
| `bytes` / `bytearray` | no / yes | yes / no | yes | binary data |
| `tuple` | no | if items are | yes | records, dict keys |
| `list` | yes | no | yes | growable sequence |
| `dict` | yes | no | insertion order | key to value |
| `set` / `frozenset` | yes / no | no / yes | no | uniqueness, membership |
| `None` | no | yes | n/a | no value |

Falsy: `None`, `False`, any numeric zero, and empty `""`, `b""`, `[]`, `()`, `{}`, `set()`, `range(0)`. Everything else is truthy (including `"0"` and `[0]`).

### Operators and precedence (Part 2)

| Tightest to loosest | Operators |
| --- | --- |
| 1 | `(...)`, `[...]`, `{...}`, `x.attr`, `x[i]`, `f(...)` |
| 2 | `**` (right-associative; `-2 ** 2 == -4`) |
| 3 | unary `+x`, `-x`, `~x` |
| 4 | `*`, `/`, `//`, `%`, `@` |
| 5 | `+`, `-` |
| 6 | `<<`, `>>` |
| 7 | `&`, then `^`, then `\|` |
| 8 | `<`, `<=`, `>`, `>=`, `!=`, `==`, `in`, `not in`, `is`, `is not` (chain: `a < b < c`) |
| 9 | `not x`, then `and`, then `or` |
| 10 | `x if cond else y`, `lambda`, `:=` |

`/` always returns `float`; `//` floors toward minus infinity; `%` takes the sign of the divisor; `round()` is banker's rounding; `and`/`or` return an operand and short-circuit.

### Strings, formatting and text (Part 4)

| Task | Code |
| --- | --- |
| Trim, split, join | `s.strip()`, `s.split(",")`, `s.partition("=")`, `",".join(parts)` |
| Test | `s.startswith(("a", "b"))`, `s.isdigit()`, `"x" in s`, `s.casefold()` |
| Replace | `s.replace(a, b)`, `s.translate(table)`, `re.sub(p, r, s)` |
| f-string spec | `f"{x:>10.2f}"` align, width, precision; `{x:,}` thousands; `{x:08b}` binary; `{x!r}`; `{x=}`; `{d:%Y-%m-%d}` |
| Regex | `re.search`, `match` (start), `fullmatch` (validate), `findall`, `finditer`, `sub`, named groups `(?P<n>...)`, raw strings |
| Bytes | `s.encode("utf-8")`, `b.decode("utf-8")`; always name the encoding; `unicodedata.normalize("NFC", s)` |
| Money and decimals | `Decimal("0.10")`, `quantize`; integers of the smallest unit |
| Time | UTC and aware: `datetime.now(timezone.utc)`; `astimezone(ZoneInfo(...))`; `isoformat` / `fromisoformat` |

### Containers and their costs (Part 6)

| Structure | Add | Lookup | Remove | Notes |
| --- | --- | --- | --- | --- |
| `list` | `append` O(1) am. | `x in l` O(n), `l[i]` O(1) | `pop()` O(1), `pop(0)`/`remove` O(n) | `sort` O(n log n), stable |
| `dict` | O(1) avg | O(1) avg | O(1) avg | insertion-ordered; hashable keys |
| `set` | O(1) avg | O(1) avg | O(1) avg | `\| & - ^`; no order |
| `deque` | both ends O(1) | O(n) middle | both ends O(1) | queue, sliding window |
| `heapq` | `heappush` O(log n) | min at `h[0]` O(1) | `heappop` O(log n) | min-heap; negate for max |
| `bisect` | `insort` O(n) | `bisect_left` O(log n) | n/a | sorted list |
| `Counter`, `defaultdict`, `OrderedDict`, `ChainMap` | | | | counting, grouping, recency, layering |

### Methods worth knowing cold

| Object | Methods |
| --- | --- |
| `list` | `append`, `extend`, `insert`, `pop`, `remove`, `index`, `count`, `sort`, `reverse`, `copy`, `clear` |
| `dict` | `get`, `setdefault`, `pop`, `popitem`, `update`, `items`, `keys`, `values`, `fromkeys`, `\|` (3.9+) |
| `set` | `add`, `discard`, `remove`, `union`, `intersection`, `difference`, `issubset`, `isdisjoint` |
| builtins | `len`, `sum`, `min`, `max` (`key=`, `default=`), `sorted`, `reversed`, `enumerate`, `zip`, `map`, `filter`, `any`, `all`, `range`, `isinstance`, `getattr`, `iter`, `next` |

### Comprehensions, unpacking and generators (Part 7)

| Form | Meaning |
| --- | --- |
| `[f(x) for x in xs if p(x)]` | list comprehension |
| `{k: v for k, v in pairs}`, `{x for x in xs}` | dict and set comprehensions |
| `(f(x) for x in xs)` | generator expression (lazy, one pass) |
| `a, *rest = items`; `first, *_, last = items` | star unpacking |
| `f(*args, **kwargs)`; `{**a, **b}`; `[*a, *b]` | spread into calls and literals |
| `yield`, `yield from` | generator; delegate |
| `itertools`: `chain`, `islice`, `product`, `permutations`, `combinations`, `accumulate`, `groupby` (sorted!), `pairwise`, `batched` | iterator toolbox |
| `functools`: `partial`, `reduce`, `cache`, `lru_cache`, `singledispatch`, `cached_property`, `wraps` | function tools |

### Classes and the data model (Part 3)

| Need | Write |
| --- | --- |
| Readable debug output | `__repr__` (always), `__str__` |
| Equality and hashing | `__eq__` plus `__hash__` (immutable fields only) |
| Ordering | `__lt__` + `@total_ordering`, or `@dataclass(order=True)` |
| Container behaviour | `__len__`, `__getitem__`, `__iter__`, `__contains__` |
| Callable object | `__call__` |
| Context manager | `__enter__`, `__exit__` or `@contextmanager` |
| Arithmetic | `__add__`, `__radd__`, `__mul__`, `__neg__`, return `NotImplemented` for unknown types |
| Attribute control | `@property`, descriptors (`__get__`, `__set__`), `__getattr__`, `__slots__` |
| Data holder | `@dataclass(frozen=True, slots=True)`, `NamedTuple`, `Enum`, `TypedDict` |
| Contract | `abc.ABC` + `@abstractmethod`, `typing.Protocol` |

### Exceptions, files and the OS (Part 5)

| Task | Pattern |
| --- | --- |
| Handle | `try: ... except (A, B) as e: ... else: ... finally: ...` |
| Wrap with cause | `raise DomainError("...") from e` |
| Common built-ins | `ValueError` bad value; `TypeError` wrong type; `KeyError`/`IndexError`; `AttributeError`; `FileNotFoundError`; `ZeroDivisionError`; `StopIteration`; `RecursionError` |
| Read a file | `with open(p, encoding="utf-8") as f: for line in f:` |
| Paths | `Path(...) / "x"`, `.read_text()`, `.write_text()`, `.glob()`, `.exists()`, `.resolve().is_relative_to(base)` |
| Modes | `r` read, `w` truncate, `a` append, `x` exclusive create, `b` binary |
| JSON | `json.dumps(obj, indent=2)`, `json.loads(s)`; `default=` for unsupported types |
| Subprocess | `subprocess.run([...], check=True, capture_output=True, text=True, timeout=...)` |
| Logging | `log = logging.getLogger(__name__)`; `log.info("x %s", v)`; `log.exception("...")` |

### Concurrency and asyncio (Parts 8 and 9)

| Question | Answer |
| --- | --- |
| I/O-bound, few blocking calls | `ThreadPoolExecutor` |
| I/O-bound, very many connections | `asyncio` with async libraries |
| CPU-bound | `ProcessPoolExecutor` (needs `if __name__ == "__main__":`), or native libraries |
| Shared mutable state | `Lock`; or `queue.Queue`; or avoid sharing |
| Deadlock | Same global lock order; timeouts; short critical sections |
| GIL | One thread runs bytecode at a time; 3.13 and 3.14 offer a free-threaded build |

| asyncio | Use |
| --- | --- |
| `asyncio.run(main())` | single entry point |
| `await asyncio.gather(*aws)` / `TaskGroup` | run together (prefer `TaskGroup`) |
| `async with asyncio.timeout(s)` | deadline |
| `asyncio.Semaphore(n)`, `asyncio.Queue` | concurrency limit, worker pool |
| `await asyncio.to_thread(fn)` | blocking call off the loop |
| `task.cancel()` and `except CancelledError: raise` | cancellation |
| Never | `time.sleep`, `requests`, heavy CPU inside `async def` |

### CPython, performance and memory (Part 10)

| Topic | Fact |
| --- | --- |
| Memory | Reference counting plus a generational cycle collector; pymalloc arenas |
| Leaks | Unbounded caches, globals, registries; find with `tracemalloc` snapshot diffs |
| Speed | Fix the algorithm; built-ins and NumPy; `lru_cache`; `timeit` / `cProfile` / `py-spy` |
| Bytecode | `dis.dis(f)`; 3.11+ specialises hot instructions |
| Objects | Header (refcount, type) + data; `sys.getsizeof` is shallow; `__slots__` saves memory |

### Types, tests and packaging (Part 12)

| Task | Tool or syntax |
| --- | --- |
| Hints | `list[int]`, `dict[str, int]`, `int \| None`, `Callable[[int], str]`, `Literal["a"]`, `TypedDict`, `Protocol`, `def f[T](x: T) -> T` (3.12) |
| Check types | `mypy --strict` or `pyright` |
| Test | `pytest -q -x -k expr --cov`; fixtures, `parametrize`, `tmp_path`, `monkeypatch`, `pytest.raises` |
| Quality | `ruff check . --fix`, `ruff format .`, `pre-commit` |
| Project | `pyproject.toml`; `uv init`, `uv add`, `uv sync`, `uv run`, `uv build` |
| Version | `requires-python = ">=3.12"`; pin and lock applications; range libraries |

### Security checklist (Part 13)

Parameterised SQL; `subprocess` with a list and no `shell=True`; no `eval` or `pickle` on untrusted data; `secrets` for tokens; Argon2 or bcrypt for passwords; validate paths and outbound URLs; `verify=True` for TLS; secrets from the environment; generic error messages to clients.

## Final Mock Interview and What to Do Next

The last section of this part is a **single mixed test** (the "Final Mock Interview" below the cheat sheets, after the part quizzes). Treat it like the real thing: set a timer for **60 minutes**, close the page, and answer on paper before you reveal anything. The questions are a blend of recall and "what does this print" items, and every snippet was run when this page was built.

How to read your score:

| Score | Meaning | Next step |
| --- | --- | --- |
| 27 to 30 of 30 | Interview-ready on core Python | Move on to the DSA and FastAPI stages; keep the error log |
| 22 to 26 | Solid, with specific gaps | Re-read the Parts behind each miss, redo the puzzles |
| 16 to 21 | Fundamentals shaky | Repeat weeks 1 and 2 of the plan before moving on |
| Below 16 | Not yet | Go back to Parts 2 and 3 and rebuild the foundations; build Projects A and B |

!interview "Tell me about a Python project you built." :: Structure the answer in five beats: **the problem** in one sentence, **the design** (two or three modules or classes and why), **one hard bug** you found and how (the debugging method from Part 11), **what you would change** at ten times the load, and **how you tested it**. Prepare this for Projects A to D of Part 14, and for the Library API in the FastAPI stage. Specifics beat adjectives: "I used a `deque` for O(1) pops" beats "I optimised it".

!tip After the mock, do not just read the key :: For every miss, write a three-line program that demonstrates the correct behaviour and run it. Predicting, running and seeing the real output is what converts a wrong belief into a correct one.

!keypoints Plan: 25 days, three blocks a day, an error log ;; Cheat sheets are for review, not first reading ;; Quizzes and the mock test recall under time pressure ;; Score below 22 means repeat the weaker weeks ;; Move on to DSA and FastAPI with two problems a day

??  How should you use the cheat sheets?
=> As compression of what you already learned: scan them the night before an interview and while coding. They are poor for learning a topic the first time; if a row does not trigger a clear picture, go back to the Part named next to it.
??  What do you do after finishing Core Python?
=> Keep a daily DSA habit (the next stage), build and deploy a FastAPI service with a database (the web stage), and keep reading real code and the standard library. Breadth of practice, not another re-read, produces fluency.
