@part py-core-13 | Core Python · Part 13: Design Patterns and Best Practices | advanced-python
## Design Patterns the Pythonic Way

The classic Gang of Four patterns were written for languages without first-class functions, modules or duck typing. Many patterns **shrink to a language feature** in Python. Knowing which, and being able to name the pattern anyway, is what interviews test.

| Pattern | Java-style solution | Pythonic form |
| --- | --- | --- |
| Singleton | Private constructor, static instance | A **module** (imported once), or `functools.cache` on a factory function |
| Factory method | Interface plus subclasses | A function or `@classmethod` returning instances; a dict of constructors |
| Builder | Fluent builder class | Keyword arguments with defaults; a dataclass; `dataclasses.replace` |
| Strategy | Interface plus classes | **Pass a function** (`key=len`, `sorted`, `callback`) |
| Observer | Listener interfaces | A list of callables; signals (`blinker`, Django signals) |
| Command | Command objects | A callable; `functools.partial` |
| Iterator | `Iterator` interface | `__iter__` or a **generator** |
| Template method | Abstract base class | Same, or pass the varying step as a function |
| Decorator (structural) | Wrapper class | A wrapper object, or the `@decorator` syntax for functions |
| Adapter | Adapter class | A small wrapper, often a function or class with the expected methods |
| RAII / try-with-resources | `AutoCloseable` | **Context manager** (`with`) |

```python Creational.py
from dataclasses import dataclass, replace
from functools import cache


# Singleton: a cached factory (module-level objects work too)
@cache
def settings():
    print("loading settings once")
    return {"debug": False}

assert settings() is settings()


# Factory: a registry of constructors instead of an if/elif chain
class Exporter:
    registry = {}

    def __init_subclass__(cls, kind, **kw):
        super().__init_subclass__(**kw)
        Exporter.registry[kind] = cls

    @classmethod
    def create(cls, kind):
        try:
            return cls.registry[kind]()
        except KeyError:
            raise ValueError(f"unknown exporter {kind!r}; choose from {sorted(cls.registry)}") from None

    def export(self, rows):
        raise NotImplementedError


class CsvExporter(Exporter, kind="csv"):
    def export(self, rows):
        return "\n".join(",".join(map(str, r)) for r in rows)


class JsonExporter(Exporter, kind="json"):
    def export(self, rows):
        import json
        return json.dumps(rows)


print(Exporter.create("csv").export([(1, "a"), (2, "b")]).replace("\n", " | "))
print(Exporter.create("json").export([[1, "a"]]))
try:
    Exporter.create("xml")
except ValueError as error:
    print(error)


# Builder: a frozen dataclass with defaults replaces a fluent builder
@dataclass(frozen=True)
class Request:
    url: str
    method: str = "GET"
    timeout: float = 5.0
    retries: int = 0

base = Request("https://api.example.com/items")
slow = replace(base, timeout=30.0, retries=3)
print(base, slow, sep="\n")
```

```output
```

```python Behavioural.py
from collections import defaultdict
from functools import partial
from typing import Callable


# Strategy: behaviour passed as a function, no class hierarchy
def percent_off(rate):
    return lambda price: price * (1 - rate)

def flat_off(amount):
    return lambda price: max(0, price - amount)

def checkout(price, *discounts: Callable[[float], float]):
    for discount in discounts:
        price = discount(price)
    return round(price, 2)

print(checkout(1000, percent_off(0.10), flat_off(50)))


# Observer: an event bus is a dict of lists of callables
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)

    def subscribe(self, event, handler):
        self.handlers[event].append(handler)

    def publish(self, event, **payload):
        for handler in self.handlers[event]:
            handler(**payload)

bus = EventBus()
log = []
bus.subscribe("order.paid", lambda order_id, **_: log.append(f"email for {order_id}"))
bus.subscribe("order.paid", lambda order_id, amount, **_: log.append(f"ledger +{amount}"))
bus.publish("order.paid", order_id=7, amount=250)
print(log)


# Command + undo: callables stored in a history
class Editor:
    def __init__(self):
        self.text, self.history = "", []

    def run(self, do, undo):
        do()
        self.history.append(undo)

    def undo(self):
        self.history.pop()()

    def append(self, s):
        self.run(partial(self._append, s), partial(self._truncate, len(s)))

    def _append(self, s):
        self.text += s

    def _truncate(self, n):
        self.text = self.text[:-n]

editor = Editor()
editor.append("Hello")
editor.append(", world")
print(editor.text)
editor.undo()
print(editor.text)


# State machine: a table of allowed transitions beats scattered if statements
TRANSITIONS = {"new": {"paid", "cancelled"}, "paid": {"shipped", "refunded"}, "shipped": {"delivered"}}

def move(state, target):
    if target not in TRANSITIONS.get(state, set()):
        raise ValueError(f"cannot go from {state} to {target}")
    return target

state = move(move("new", "paid"), "shipped")
print(state)
try:
    move("shipped", "new")
except ValueError as error:
    print(error)
```

```output
```

Two structural patterns are worth drawing by hand in an interview:

- **Adapter / facade**: wrap an awkward or third-party API in a small class with the interface *you* want, so the rest of the code (and your tests) depend on your interface, not theirs. The repository pattern for databases and a `PaymentGateway` wrapper are the usual examples.
- **Proxy**: an object with the same interface that adds behaviour (caching, lazy loading, access checks, logging); `__getattr__` makes a generic one in a few lines.

!interview What is dependency injection in Python, and do you need a framework? :: Pass collaborators in instead of constructing them inside (`OrderService(repo, notifier)`), so tests can pass fakes. In Python you rarely need a container: constructor parameters and default values are enough. FastAPI's `Depends` provides injection per request, which is the same idea with a framework that builds and caches the dependencies for you.

??  Which classic design patterns are unnecessary in Python and why?
=> Singleton (modules are singletons), Strategy and Command (functions are first-class), Iterator (generators), Factory and Builder in their heavy forms (functions, classmethods, keyword arguments and dataclasses), and RAII wrappers (context managers). The idea of each pattern remains; the class machinery usually does not.
??  How do you implement a singleton in Python?
=> The simplest is a module-level object, since a module is imported and executed once. Alternatives: a cached factory function (`@functools.cache`), or `__new__` returning one instance. Prefer injecting a single instance explicitly, which stays testable.
??  When would you use the State pattern?
=> When an object's behaviour depends on a lifecycle (order: new, paid, shipped). A transition table (dict of allowed moves), or an `Enum` with methods, makes legal transitions explicit and testable; separate state classes help only when each state has substantial behaviour.

## Pythonic Idioms and Effective Practices

**The Zen of Python** in practice: readability counts; explicit beats implicit; simple beats complex; errors should never pass silently. Concretely:

| Instead of | Write |
| --- | --- |
| `for i in range(len(xs)): xs[i]` | `for x in xs:` or `for i, x in enumerate(xs):` |
| `if x == True`, `if len(xs) > 0` | `if x:`, `if xs:` |
| `if x == None` | `if x is None` |
| Manual open/close | `with open(path, encoding="utf-8") as f:` |
| `s = ""; for p in parts: s += p` | `"".join(parts)` |
| `d.has_key(k)` then index | `d.get(k, default)`, `setdefault`, `defaultdict` |
| `list(map(lambda x: x*2, xs))` | `[x * 2 for x in xs]` |
| `isinstance(x, list) or isinstance(x, tuple)` | `isinstance(x, (list, tuple))` |
| Returning a tuple of 5 things | A dataclass or `NamedTuple` |
| `try: ... except: pass` | Catch the specific error, handle or log |
| Class with only `__init__` and one method | A function |
| `from module import *` | Import names explicitly |
| Mutable default argument | `None` sentinel |
| String-built paths | `pathlib.Path` |
| `print` for diagnostics | `logging` |

```python Refactor.py
# BEFORE: nested conditions, a flag, a mutable default, and a magic number
def process_old(orders, results=[]):
    ok = False
    for o in orders:
        if o is not None:
            if o["status"] == "paid":
                if o["amount"] > 0:
                    if o["amount"] > 10000:
                        results.append(o["id"] + ":review")
                    else:
                        results.append(o["id"] + ":ship")
                    ok = True
    return results if ok else None


# AFTER: guard clauses, named constants, no flag, no shared state, returns a list
REVIEW_THRESHOLD = 10_000

def decide(order):
    if order["status"] != "paid" or order["amount"] <= 0:
        return None
    return "review" if order["amount"] > REVIEW_THRESHOLD else "ship"

def process(orders):
    decisions = ((o["id"], decide(o)) for o in orders if o)
    return [f"{order_id}:{action}" for order_id, action in decisions if action]


orders = [
    {"id": "A", "status": "paid", "amount": 500},
    None,
    {"id": "B", "status": "paid", "amount": 20_000},
    {"id": "C", "status": "cancelled", "amount": 100},
    {"id": "D", "status": "paid", "amount": 0},
]
assert process(orders) == ["A:ship", "B:review"]
assert process_old(orders, []) == process(orders)       # same behaviour, much easier to read and test
assert process([]) == []
print(process(orders))
```

```output
```

### Code smells to recognise

| Smell | Symptom | Usual fix |
| --- | --- | --- |
| Long function | Scrolls past a screen; several levels of nesting | Guard clauses, extract functions with names that state intent |
| God class | One class that knows everything | Split by responsibility; compose |
| Primitive obsession | Strings and ints standing for money, emails, ids | Value objects (frozen dataclasses, `NewType`) |
| Boolean flag parameters | `process(order, True, False)` | Keyword-only parameters, separate functions, enums |
| Mutable default or global state | Surprising state shared between calls | `None` default; pass state explicitly |
| Stringly-typed code | `if status == "paid"` repeated everywhere | `Enum` |
| Comments that explain what | `# increment i` | Better names; keep comments for **why** |
| Catch-all `except` | Swallowed bugs | Narrow exceptions, log |
| Copy-paste | The same logic in three places | Extract a function or generator |
| No tests around changes | Fear of refactoring | Characterisation tests first (like the asserts above) |

!tip Refactor with a safety net :: Before changing messy code, pin its current behaviour with a few asserts or tests (as the `process_old` comparison does), refactor in small steps, and run the tests after each step. A refactor that changes behaviour is a rewrite.

??  What does "Pythonic" mean?
=> Code that uses the language's idioms and conventions: iteration over items, comprehensions and generators, context managers, EAFP, duck typing, standard-library tools and readable names. It is code a Python expert reads without friction, not code that is clever.
??  Why are guard clauses preferred to deep nesting?
=> Returning early for invalid or special cases keeps the main path unindented and the conditions next to their reasons, which reduces cognitive load and bugs. Each branch is a small, testable check.
??  How do you avoid boolean flag arguments?
=> Make the flag keyword-only (`ship(order, *, express=True)`) so call sites read well, use an `Enum` when there are more than two modes, or split into two functions with clear names.

## Secure Coding in Python

Most vulnerabilities in Python services come from a short list of mistakes, all of which this tree has met before. The OWASP Top 10 is the checklist; these are the Python forms.

### Injection: never build queries or commands from strings

```python Injection.py
import sqlite3
import subprocess
import sys

db = sqlite3.connect(":memory:")
db.executescript("""
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, secret TEXT);
    INSERT INTO users (name, secret) VALUES ('asha', 'a-secret'), ('ravi', 'r-secret');
""")

attacker_input = "x' OR '1'='1"

vulnerable = f"SELECT name, secret FROM users WHERE name = '{attacker_input}'"       # string-built SQL
print("vulnerable ->", db.execute(vulnerable).fetchall())

safe = db.execute("SELECT name, secret FROM users WHERE name = ?", (attacker_input,)).fetchall()   # parameterised
print("parameterised ->", safe)

filename = "report.txt && echo INJECTED"          # attacker-controlled "file name"
shell_style = subprocess.run(f'"{sys.executable}" -c "import sys; print(sys.argv[1:])" {filename}', shell=True, capture_output=True, text=True)
list_style = subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1:])", filename], capture_output=True, text=True)
print("shell=True  ->", shell_style.stdout.replace("\r\n", " | ").replace("\n", " | ").strip())
print("list of args ->", list_style.stdout.strip())
```

```output
```

The query with `?` placeholders sends the **code** and the **data** separately, so the data can never become code; ORMs (SQLAlchemy, Django) do this for you unless you drop to raw string SQL. The shell version ran `echo INJECTED` as a second command (`&&` chains commands in both `cmd.exe` and POSIX shells); the list version treated the whole text as one harmless argument.

### Secrets, passwords and randomness

```python Secrets.py
import hmac
import secrets
from hashlib import sha256

from pwdlib import PasswordHash

hasher = PasswordHash.recommended()                  # Argon2: a slow, salted, memory-hard password hash
stored = hasher.hash("correct horse battery staple")
print(stored.startswith("$argon2id$"), hasher.verify("correct horse battery staple", stored), hasher.verify("guess", stored))
print(stored != hasher.hash("correct horse battery staple"))      # a random salt makes every hash different

token = secrets.token_urlsafe(32)                    # unguessable: for sessions, reset links, API keys
print(len(token) >= 43, secrets.token_urlsafe(32) != token)

signature = hmac.new(b"server-secret", b"user=7", sha256).hexdigest()
print(hmac.compare_digest(signature, hmac.new(b"server-secret", b"user=7", sha256).hexdigest()))   # constant-time comparison
```

```output
```

### Validating where URLs and paths come from

```python Ssrf.py
import ipaddress
from urllib.parse import urlparse


def is_safe_outbound_url(url: str) -> bool:
    """Refuse internal addresses so a user-supplied URL cannot reach your own network (SSRF)."""
    parts = urlparse(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return False
    try:
        ip = ipaddress.ip_address(parts.hostname)
    except ValueError:
        return True                                  # a hostname: ALSO resolve it and check every returned address in real code
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)


for url in ("https://example.com/hook", "http://169.254.169.254/latest/meta-data", "http://127.0.0.1:8080/admin",
            "http://10.0.0.5/internal", "file:///etc/passwd", "https://93.184.216.34/"):
    print(f"{url:<45} {is_safe_outbound_url(url)}")
```

```output
```

!cheat Python security checklist ::
- **Injection**: parameterised SQL; `subprocess.run([...])` without `shell=True`; autoescaped templates; never `eval`/`exec` on input.
- **Deserialisation**: no `pickle.loads` or `yaml.load` on untrusted data; use JSON + validation.
- **Secrets**: from environment or a secret manager; never in code, logs or URLs; rotate. Use `secrets`, not `random`.
- **Passwords**: Argon2 / bcrypt / scrypt via a maintained library; never MD5/SHA-1/plain SHA-256 alone.
- **Files and URLs**: resolve and confine paths; validate and restrict outbound URLs (SSRF); size limits on uploads.
- **TLS**: never `verify=False`; keep CA bundles updated; set timeouts.
- **Dependencies**: pin and audit; review new packages; least-privilege containers.
- **Errors**: return generic messages to clients, log details server-side; `assert` is not validation.
- **Regex and parsers**: bound input size; use `defusedxml` for XML.
!end

!warning eval is never the answer for parsing :: `eval("1 + 2")` executes arbitrary Python (`__import__("os").system(...)`). For user-supplied expressions use `ast.literal_eval` (literals only), `json.loads`, a real parser, or a restricted expression library. `yaml.load` without `SafeLoader`, `pickle`, `marshal` and `shelve` on untrusted data are the same class of bug.

??  How do you prevent SQL injection in Python?
=> Use parameterised queries (`cursor.execute("... WHERE id = %s", (value,))` or `?` placeholders) or an ORM/query builder, never string formatting, concatenation or f-strings. Parameters keep data out of the SQL text. Also give the database user least privilege.
??  How should passwords be stored?
=> Hashed with a slow, salted, memory-hard algorithm (Argon2id, bcrypt, scrypt) through a maintained library, verifying with the library's constant-time check. Never encrypt them reversibly, never use a fast hash such as SHA-256 alone, and never log them.
??  What is SSRF and how does it relate to Python code?
=> Server-side request forgery: your server fetches a user-supplied URL and is tricked into calling internal services (cloud metadata endpoints, admin ports). In Python it appears in webhooks, URL previews and image fetchers. Restrict schemes, resolve hostnames and block private and link-local addresses, ideally through an allow-list and an egress proxy.
??  Why is `assert` unsuitable for input validation?
=> Assertions are removed when Python runs with `-O`, and they raise `AssertionError`, which is not meant for client errors. Validate explicitly and raise a domain or `ValueError`.

## Designing APIs and Libraries

Whether you ship a package to PyPI or a module used by ten teammates, an API is a promise.

1. **Make the common case short and the dangerous case explicit.** Defaults for the safe behaviour; keyword-only parameters for options (`def fetch(url, *, timeout=5.0, retries=0)`).
2. **Be consistent**: naming, argument order, return types (return `list` always, not `list` or `None`; raise for errors rather than returning error codes).
3. **Define the public surface**: `__all__`, a leading underscore for internals, a `py.typed` marker so type checkers read your hints, and docstrings with examples.
4. **Raise your own exception hierarchy** rooted in one base class, and document what each function raises.
5. **Evolve without breaking**: deprecate with `warnings.warn(..., DeprecationWarning, stacklevel=2)` for at least one release, follow semantic versioning, and keep a changelog.
6. **Do not do work at import time**: no network calls, no reading config, no starting threads in module top level.

```python Deprecation.py
import warnings


def old_total(prices):
    warnings.warn("old_total() is deprecated, use total()", DeprecationWarning, stacklevel=2)
    return total(prices)


def total(prices, *, tax=0.0):
    return round(sum(prices) * (1 + tax), 2)


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    result = old_total([10, 20])
print(result, caught[0].category.__name__, str(caught[0].message))
```

```output
```

??  How do you deprecate a function without breaking users?
=> Keep it working, emit a `DeprecationWarning` with a clear replacement and `stacklevel=2` so the warning points at the caller, document it in the changelog, and remove it in a later major version. Tests should run with warnings as errors so you notice your own use of deprecated APIs.
??  Why prefer keyword-only parameters for options?
=> Call sites become self-documenting (`fetch(url, timeout=3)`), the order of optional parameters can change without breaking callers, and new options can be added later without ambiguity.
