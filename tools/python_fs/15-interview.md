@part py-core-15 | Core Python · Part 15: Interview Preparation | advanced-python
## How Python Interviews Work

A typical process for a fresher or junior to mid-level Python or full-stack role has four to six stages. Knowing what each stage measures tells you what to practise.

| Stage | What it checks | How to prepare |
| --- | --- | --- |
| Online assessment or phone screen | Fundamentals and speed: output questions, small coding problems, SQL | Parts 2 to 7 and the DSA stage; time yourself |
| Coding round(s) | Problem solving in Python: data structures, complexity, clean code | 2 DSA problems a day; practise talking while coding |
| Python depth round | Language internals: GIL, memory, decorators, generators, async | Parts 8 to 11; the question banks below |
| Framework / back-end round | FastAPI, Django or Flask, databases, REST design, auth, testing | The web stage |
| System design / LLD | Design a service or classes; trade-offs; scaling | The design stage |
| Behavioural / project deep dive | Ownership, debugging stories, teamwork | The interview stage |

### How to answer a technical question

1. **Restate the problem** and ask about input size, edge cases (empty, duplicates, negatives, `None`) and constraints.
2. **Give the brute force first** with its complexity, then improve it: "this is O(n²); a dictionary makes it O(n)".
3. **Name the data structure and why**: "a set gives O(1) membership".
4. **Write clean Python**: meaningful names, comprehensions where they help, standard-library tools (`Counter`, `deque`, `heapq`, `bisect`, `itertools`).
5. **Test with examples aloud**, including edge cases, before declaring it done.
6. **State complexity** (time and space) and one trade-off or extension.

### What interviewers love and hate

| They respond well to | They respond badly to |
| --- | --- |
| "Let me think about the complexity first" | Silence for five minutes |
| Using `enumerate`, `zip`, `Counter`, `defaultdict` naturally | C-style index loops and manual counting |
| Admitting a gap, then reasoning to an answer | Bluffing about internals |
| Asking about edge cases and constraints | Starting to code before understanding |
| Explaining why `is` is wrong for strings | Memorised answers with no examples |
| Mentioning testing and error handling | Mutable default arguments, bare `except` |

!tip A one-minute answer template for conceptual questions :: **Definition** (one sentence), **why it exists** (the problem it solves), **a tiny example**, **a trade-off or pitfall**. For "What is the GIL?": a lock letting one thread run bytecode at a time; protects reference counting; CPU-bound threads do not scale but I/O-bound ones do; use processes or free-threaded builds for CPU work.

??  How do you approach a coding problem you have never seen?
=> Clarify the requirements and constraints, work a small example by hand, propose a brute-force solution and its complexity, look for the bottleneck and a data structure that removes it (hash map, sorting, two pointers, heap, DP), code it cleanly, then test edge cases and state the complexity.
??  What do you do when you are stuck?
=> Say what you know and what blocks you, simplify (smaller input, a special case), try a related pattern aloud, and ask for a hint rather than going silent. Interviewers assess how you reason as much as the final code.

## Interview Q&A: Language, OOP, Strings, Exceptions and Files

??  What is the difference between a list and a tuple?
=> Lists are mutable, variable-length, and meant for homogeneous collections; tuples are immutable, fixed, hashable when their items are, slightly smaller and faster, and meant for records. Use a tuple as a dict key or a return of several values.
??  What is the difference between `==` and `is`?
=> `==` compares values (`__eq__`), `is` compares identity. Use `is` for `None` and singletons only.
??  Are Python function arguments passed by value or by reference?
=> By object reference (assignment). Mutating a passed mutable object is visible to the caller; rebinding the parameter name is not.
??  What are `*args` and `**kwargs`?
=> `*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict. In calls, `*` and `**` unpack iterables and mappings into arguments.
??  What is the difference between a shallow copy and a deep copy?
=> A shallow copy duplicates the container but shares the nested objects; a deep copy (`copy.deepcopy`) recursively duplicates everything. Mutating a shared nested list through a shallow copy changes the original.
??  How does `@classmethod` differ from `@staticmethod`?
=> A class method receives the class (`cls`), so it can build instances and works with inheritance (alternative constructors). A static method receives neither, so it is just a namespaced function.
??  What is `__init__` versus `__new__`?
=> `__new__` creates and returns the instance (rarely overridden: immutable subclasses, singletons); `__init__` initialises the already-created instance.
??  What are dunder methods and give examples.
=> Special methods Python calls for operators and built-ins: `__repr__`, `__str__`, `__eq__`, `__hash__`, `__len__`, `__iter__`, `__getitem__`, `__call__`, `__enter__`/`__exit__`, `__add__`. They let your classes behave like built-in types.
??  What is the MRO and how does `super()` use it?
=> The method resolution order is the C3-linearised list of classes searched for attributes. `super()` delegates to the next class in the MRO of the instance's type, which makes cooperative multiple inheritance work.
??  What is duck typing?
=> Using an object by its behaviour rather than its declared type: anything with the needed methods works. Protocols and type hints describe it statically.
??  What is the difference between an iterator and an iterable, and a generator?
=> An iterable can produce an iterator (`__iter__`); an iterator yields values with `__next__` and is exhausted after one pass; a generator is an iterator written with `yield`, evaluated lazily.
??  What does `with` do?
=> It calls `__enter__` on entry and `__exit__` on exit (even on exceptions), guaranteeing cleanup for files, locks and transactions. `contextlib.contextmanager` builds one from a generator.
??  How do exceptions propagate, and what is the order of `try/except/else/finally`?
=> An exception travels up the call stack until a matching `except` catches it. `else` runs if no exception occurred, `finally` always runs. Catch specific exceptions; use `raise ... from ...` to keep the cause.
??  Why are strings immutable and how do you build a large string efficiently?
=> Immutability allows safe sharing, hashing and interning. Build with `"".join(parts)` (or `io.StringIO`), not repeated `+=` in a loop.
??  What is the difference between `str`, `bytes` and `bytearray`?
=> `str` is Unicode text, `bytes` an immutable sequence of integers 0 to 255, `bytearray` a mutable version. Encode text to bytes at the boundary and decode on the way in, always naming the encoding.
??  How do you read a huge file safely?
=> Iterate over the file object line by line or read fixed-size chunks inside a `with open(..., encoding="utf-8")` block; never `read()` it whole. Use generators to process the lines lazily.
??  What does `if __name__ == "__main__"` do?
=> Runs the guarded code only when the file is executed as a script and not when it is imported, so a module can be both reusable and runnable.
??  How do `@property`, `__slots__` and `@dataclass` differ in purpose?
=> `@property` turns a method into a computed or validated attribute; `__slots__` removes the per-instance dict to save memory and forbid new attributes; `@dataclass` generates `__init__`, `__repr__`, `__eq__` and optionally ordering and hashing for data holders.
??  What is name mangling?
=> A leading double underscore inside a class renames `__x` to `_ClassName__x` to avoid accidental clashes in subclasses. It is not privacy.

## Interview Q&A: Collections, Generators, Decorators and Functional Python

??  How are dictionaries implemented, and what is their complexity?
=> A hash table with open addressing and a compact insertion-ordered entries array. Average O(1) for get, set and delete; worst case O(n) with pathological collisions (mitigated by hash randomisation). Insertion order is guaranteed since 3.7.
??  What can be a dictionary key?
=> Any hashable object: immutable and with a stable `__hash__` consistent with `__eq__` (strings, numbers, tuples of hashables, frozensets, frozen dataclasses). Lists, dicts and sets cannot.
??  How do you remove duplicates from a list and keep the order?
=> `list(dict.fromkeys(items))`. `list(set(items))` also removes duplicates but loses the order.
??  When would you use `deque`, `heapq`, `Counter` and `defaultdict`?
=> `deque` for queues and sliding windows (O(1) at both ends); `heapq` for priority queues and top-k; `Counter` for frequency counts and multisets; `defaultdict` for grouping and accumulating without key checks.
??  Why is `x in list` slow and `x in set` fast?
=> A list scans linearly, O(n); a set hashes the value and jumps to a bucket, O(1) on average.
??  What does `sorted` use internally, and is it stable?
=> Timsort: O(n log n) worst case, near O(n) on partially sorted data, and stable (equal keys keep their order), which enables multi-key sorts by sorting in passes.
??  What is a list comprehension, and when should you not use one?
=> A compact expression that builds a list from an iterable with an optional filter. Avoid it for side effects, long multi-step logic or deep nesting; use a loop or a generator expression when you do not need the list.
??  What is a generator and why is it memory efficient?
=> A function with `yield` that produces values lazily and keeps its state between calls, so only one item exists at a time and a pipeline processes data of any size in constant memory.
??  What does `yield from` do?
=> It delegates to a sub-generator or iterable, forwarding values (and sent values and exceptions) and returning the sub-generator's return value.
??  What is a closure and what is the late-binding problem?
=> A function that remembers variables from its defining scope. Closures capture variables, not values, so lambdas created in a loop all see the loop variable's final value; fix with a default argument or `functools.partial`.
??  Explain decorators and write the skeleton of one.
=> A decorator takes a function and returns a (usually wrapped) function: `def deco(f): @functools.wraps(f) def wrapper(*a, **k): ...; return f(*a, **k); return wrapper`. The `@deco` syntax means `f = deco(f)`; with arguments you add one more level.
??  What is `functools.lru_cache` and what are its limits?
=> It memoises a pure function's results keyed by its (hashable) arguments with a bounded least-recently-used cache. Limits: arguments must be hashable, memory grows to `maxsize`, results are shared (do not mutate them), and caching methods keeps instances alive.
??  What is the difference between `map`, `filter` and a comprehension?
=> They do the same work; `map` and `filter` return lazy iterators and take functions, comprehensions are more readable for inline expressions. Prefer comprehensions unless you already have a named function.
??  What are `any()` and `all()` and how do they short-circuit?
=> `any` returns True as soon as one element is truthy; `all` returns False as soon as one is falsy. With generator expressions they stop reading early. `all([])` is True and `any([])` is False.
??  What is the difference between `copy`, `deepcopy` and slicing for lists?
=> `lst[:]`, `list(lst)` and `copy.copy(lst)` are shallow copies; `copy.deepcopy(lst)` copies nested objects too. For immutable-only contents a shallow copy suffices.
??  How do you flatten a nested list?
=> One level: `[x for sub in nested for x in sub]` or `itertools.chain.from_iterable`. Arbitrary depth: a recursive generator using `yield from`, guarding against strings.

## Interview Q&A: Concurrency, the GIL, asyncio and CPython

??  What is the GIL and what are its consequences?
=> A lock allowing one thread to execute Python bytecode at a time per interpreter, protecting reference counts. CPU-bound threads do not run in parallel; I/O-bound threads do overlap waits; use processes or native libraries for CPU work. Free-threaded builds (3.13 experimental, 3.14 supported) remove it.
??  Threads, processes or asyncio?
=> I/O-bound with many connections and async libraries: asyncio. A few blocking I/O calls: a thread pool. CPU-bound: a process pool or native code. Mixed workloads: separate them.
??  What is a race condition and how do you prevent it?
=> A timing-dependent bug caused by unsynchronised access to shared mutable state (for example `counter += 1`). Prevent with locks, thread-safe queues, atomic operations, immutability or by avoiding shared state.
??  What is a deadlock and how do you avoid it?
=> Threads waiting on each other's locks forever. Avoid with a global lock order, short critical sections, timeouts on `acquire`, and no blocking calls while holding a lock.
??  How does `asyncio` work?
=> One thread runs an event loop that schedules coroutines; at each `await` a coroutine yields control while waiting for I/O, and the loop resumes others. It is cooperative, so any blocking call stalls everything.
??  What is the difference between `asyncio.gather` and `TaskGroup`?
=> `gather` collects results of awaitables and propagates the first exception while leaving siblings running; `TaskGroup` (3.11+) is structured concurrency: it cancels siblings on failure and raises an `ExceptionGroup`.
??  How do you call blocking code from async code?
=> `await asyncio.to_thread(func, *args)` for blocking I/O, or `loop.run_in_executor` with a process pool for CPU-bound work.
??  How does Python manage memory?
=> Reference counting frees objects immediately at zero; a generational cycle collector handles reference cycles; pymalloc serves small objects from arenas. Memory may not return to the OS because of fragmentation.
??  How do you find a memory leak?
=> Monitor RSS, reproduce under load, use `tracemalloc` snapshot diffs (or `memray`) to find the growing allocation site, then find what still references the objects (unbounded cache, global list, registry).
??  What is the difference between `multiprocessing` start methods?
=> `fork` clones the parent (fast, unsafe with threads), `spawn` starts a fresh interpreter that re-imports the module (default on Windows and macOS; needs the `__main__` guard), `forkserver` forks from a clean server process (default on Linux from 3.14).
??  What makes Python slow, and how do you speed it up?
=> Interpreted bytecode, dynamic typing and object overhead. Fix algorithms first, use built-ins and C-backed libraries (NumPy), cache results, use concurrency for waiting, then profile and consider Cython, mypyc, PyPy or native extensions.

## Interview Q&A: Modern Python, Typing, Testing and Packaging

??  Are type hints enforced at run time?
=> No: the interpreter stores them in `__annotations__`. Static checkers (mypy, pyright) verify them; Pydantic and FastAPI read them at run time for validation and parsing.
??  What is a `Protocol`?
=> A structural type: any class with the required methods and attributes satisfies it without inheriting from it, which models duck typing for type checkers.
??  What is the difference between `dataclass`, `NamedTuple`, `TypedDict` and Pydantic `BaseModel`?
=> `dataclass`: mutable data class with generated methods and no validation; `NamedTuple`: immutable tuple record; `TypedDict`: type-hint for dictionaries with known keys; `BaseModel`: validates and converts data at run time.
??  What does `match` add over `if`/`elif`?
=> Structural pattern matching: it tests the shape of data (sequences, mappings, class patterns) and binds parts of it in one step, with guards and alternatives.
??  How do you write tests in Python?
=> With `pytest`: plain functions and `assert`, fixtures for set-up, `parametrize` for cases, `monkeypatch`/`unittest.mock` at boundaries, coverage in CI, and fakes for I/O.
??  What is a virtual environment and why use one?
=> An isolated directory with its own interpreter and installed packages, so each project has its own dependency versions. Create with `python -m venv` or `uv`, and lock exact versions.
??  What is `pyproject.toml`?
=> The standard project file: build system, metadata, dependencies, entry points and tool configuration (ruff, pytest, mypy).
??  What is the difference between a library and an application regarding dependency versions?
=> Applications lock exact versions for reproducibility; libraries declare compatible ranges so they work alongside other packages.
??  How do you keep a Python codebase healthy?
=> Formatter and linter (ruff), type checker (mypy/pyright), tests with a coverage gate, pre-commit hooks, CI that runs the same checks, dependency audits and code review.
??  What new features of Python 3.10 to 3.14 do you use?
=> Typical answer: `match`, `X | Y` types and better errors (3.10); `TaskGroup`, `tomllib`, exception groups and big speed-ups (3.11); PEP 695 generics and `override` (3.12); the new REPL and free-threaded option (3.13); t-strings and supported free-threading (3.14). Name the ones you have actually used and why.
