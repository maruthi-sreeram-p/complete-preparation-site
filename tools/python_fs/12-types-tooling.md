@part py-core-12 | Core Python · Part 12: Types, Modern Python and Tooling | advanced-python
## Type Hints and Static Checking

Python stays dynamically typed, but since 3.5 you can **annotate** variables, parameters and return values. The interpreter **ignores** annotations at run time (it only stores them); separate tools read them: **type checkers** (mypy, pyright, pyrefly), editors, and run-time libraries such as **Pydantic** and **FastAPI**. Treat hints as machine-checked documentation that catches a class of bugs before the code runs.

```python Hints.py
from typing import Callable, Literal, TypedDict


def total(prices: list[float], tax: float = 0.18) -> float:        # built-in generics: list[float] (3.9+)
    return sum(prices) * (1 + tax)


def find(users: dict[int, str], user_id: int) -> str | None:       # X | None instead of Optional[X] (3.10+)
    return users.get(user_id)


Mode = Literal["r", "w", "a"]                                       # only these exact values are allowed

def open_file(path: str, mode: Mode = "r") -> None: ...


class UserDict(TypedDict):                                          # a dict with known keys and value types
    id: int
    name: str


def apply(func: Callable[[int, int], int], a: int, b: int) -> int:  # a callable taking two ints, returning an int
    return func(a, b)


def first[T](items: list[T]) -> T:                                  # PEP 695 generic syntax (3.12+)
    return items[0]

type Matrix = list[list[float]]                                     # PEP 695 type alias (3.12+)

print(total([100.0, 50.0]), find({1: "asha"}, 2), apply(max, 3, 9), first(["x", "y"]))
print(total.__annotations__)                                        # the interpreter only STORES the hints
print(first("abc"))                                                   # a str is not a list[T]; nothing stops it at run time
```

```output
```

### Running a type checker

The checker reads the same code and reports mismatches **without running it**:

```python MypyDemo.py
import pathlib
import subprocess
import sys

pathlib.Path("shop.py").write_text('''\
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price: float


def cheapest(items: list[Item]) -> Item | None:
    return min(items, key=lambda i: i.price) if items else None


best = cheapest([Item("pen", 2.5)])
print(best.name)                     # error: best may be None
print(cheapest([("pen", 2.5)]))      # error: wrong element type
Item("pen", "free")                  # error: price must be a float
''')

result = subprocess.run([sys.executable, "-m", "mypy", "--strict", "--no-incremental", "--no-color-output", "--no-error-summary", "shop.py"],
                        capture_output=True, text=True)
print(result.stdout.strip())
print("mypy exit status:", result.returncode)
```

```output
```

What to remember about static types:

| Idea | Detail |
| --- | --- |
| **Gradual** | Annotate as much as you like; unannotated code is treated as `Any`. Start at the boundaries (public functions) |
| **`Optional` is explicit** | `str | None` forces you to handle `None`: the largest category of bugs it catches |
| **Duck typing, checked** | `Protocol` types describe the shape you need (`Iterable`, `SupportsClose`) |
| **`Any` switches checking off** | Prefer `object` (safe) or a real type. `cast(T, x)` asserts, it does not convert |
| **Run it in CI** | `mypy --strict` or `pyright`; type errors then block merges |
| **Not enforced at run time** | `def f(x: int)` accepts a string. Validate untrusted input with Pydantic |
| **FastAPI and Pydantic read hints at run time** | Annotations become request parsing and validation |

!interview Type hints versus Pydantic validation :: Hints are for the checker: a wrong call like `total(["a"])` still *runs* and fails inside the function. **Pydantic** reads the same annotations at run time, converts and validates incoming data (`"42"` becomes `42` or a clear error), which is why web frameworks use it at the boundary. Use hints everywhere, and validation wherever data enters the system.

??  Are Python type hints enforced?
=> Not by the interpreter. They are metadata stored in `__annotations__`. Static checkers (mypy, pyright) verify them before running; libraries such as Pydantic, FastAPI and dataclass validators read them at run time to parse and validate data.
??  What is the difference between `Optional[int]`, `int | None` and a default of `None`?
=> `Optional[int]` and `int | None` mean exactly the same: the value is an int or `None` (the `|` spelling is 3.10+). A default of `None` is about the *default value*; a parameter `x: int = None` is a type error in strict checking because the annotation does not allow `None`: write `x: int | None = None`.
??  When do you use `TypeVar` or the new `def f[T]` syntax?
=> To say "the output type depends on the input type": `def first[T](items: list[T]) -> T` returns whatever the list holds. Without it you would have to write `Any` and lose type information.

## Modern Python: What Changed From 3.8 to 3.14

Real code runs on whatever the team standardised on, and interview questions mention features by version. This table is a map of the language you will meet; check the "What's New" page of each release for details.

| Version | Highlights for application developers |
| --- | --- |
| **3.8** | Walrus operator `:=`; positional-only parameters `/`; f-string `=` debug; `functools.cached_property` |
| **3.9** | `dict | dict`; built-in generics (`list[int]`); `str.removeprefix`; `zoneinfo`; new PEG parser |
| **3.10** | `match` statement; `X | Y` types; parenthesised `with`; `zip(strict=True)`; much better error messages; `aiter`/`anext` |
| **3.11** | **10 to 60% faster** (specialising interpreter, zero-cost exceptions); `ExceptionGroup` and `except*`; `tomllib`; `asyncio.TaskGroup` and `timeout`; `Self`; `StrEnum`; fine-grained error locations |
| **3.12** | PEP 695 (`def f[T]`, `type X = ...`); nicer f-strings (nested quotes); per-interpreter GIL; `itertools.batched`; `typing.override`; faster comprehensions (inlined); `datetime.utcnow` deprecated |
| **3.13** | New interactive REPL; **experimental free-threaded build** and **experimental JIT**; removal of many "dead batteries" (PEP 594); `copy.replace` |
| **3.14** | **t-strings** (template string literals, PEP 750); **deferred evaluation of annotations** (PEP 649/749); free-threaded build officially supported; `concurrent.interpreters`; Zstandard in the standard library (`compression.zstd`); incremental GC; remote-debugging hooks |
| **3.15** (due October 2026) | Check the release notes: expected items include explicit lazy imports (PEP 810) and UTF-8 as the default text encoding (PEP 686) |

```python Modern.py
from typing import override
from itertools import batched


class Base:
    def run(self) -> str:
        return "base"


class Child(Base):
    @override                                   # a type checker errors if Base has no run(): catches renames
    def run(self) -> str:
        return "child"


songs = {"gold": ["a", "b"], "silver": ["c"]}
print(f"{"gold" if songs["gold"] else "none"}: {", ".join(songs["gold"])}")     # 3.12: same quotes inside f-strings
print(list(batched(range(7), 3)), Child().run())

with (open("a.txt", "w") as first, open("b.txt", "w") as second):             # 3.10: parenthesised context managers
    first.write("1")
    second.write("2")

for index, name in enumerate(["x", "y"], start=1):
    match (index, name):                                                        # 3.10: structural pattern matching
        case (1, str() as label):
            print("first:", label)
        case (n, label):
            print("other:", n, label)
```

```output
```

!tip Know your minimum version :: A library or service declares `requires-python = ">=3.10"` and may then use that version's syntax everywhere. Libraries support the oldest version still receiving security fixes; applications can pin the newest. CI should test the minimum and the newest versions you claim to support (`tox`, `nox` or a GitHub Actions matrix).

??  Name three features added in each of 3.10, 3.11 and 3.12.
=> 3.10: `match`, `X | Y` type syntax, better error messages. 3.11: speed-ups, `ExceptionGroup`/`except*`, `tomllib`, `TaskGroup`. 3.12: PEP 695 generics and `type` aliases, nested-quote f-strings, per-interpreter GIL.
??  What are t-strings in Python 3.14?
=> Template string literals (`t"Hello {name}"`) that look like f-strings but produce a structured `Template` object instead of a finished string, so libraries can process the interpolated values safely (escaping for HTML, SQL parameters) rather than concatenating them. Check the release notes for the current API.
??  Why did the pace of Python releases matter for applications?
=> A new feature release arrives every October and each is supported about five years, so there are always several supported versions. You pin one for applications, test the range for libraries, and plan upgrades yearly rather than every five years.

## Testing with pytest

`pytest` is the de-facto standard. A test is a plain function named `test_*` that uses plain `assert`; pytest rewrites the assertion to explain **why** it failed. Fixtures, parametrisation and plugins do the rest.

```python PytestDemo.py
import pathlib
import re
import subprocess
import sys

pathlib.Path("calc.py").write_text('''\
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("b must not be zero")
    return a / b


def apply_discount(price, percent):
    return price - price * percent / 100
''')

pathlib.Path("test_calc.py").write_text('''\
import pytest
from calc import apply_discount, divide


@pytest.fixture
def prices():
    return [100, 250]                                   # a fixture: set-up shared by tests that ask for it


def test_divide():
    assert divide(10, 4) == 2.5


@pytest.mark.parametrize("price, percent, expected", [(100, 10, 90), (200, 50, 100), (80, 0, 80)])
def test_discount(price, percent, expected):            # one test function, three cases
    assert apply_discount(price, percent) == expected


def test_zero_division():
    with pytest.raises(ZeroDivisionError, match="must not be zero"):
        divide(1, 0)


def test_fixture(prices, tmp_path, monkeypatch):        # tmp_path: a fresh temp folder; monkeypatch: undoable patching
    (tmp_path / "prices.txt").write_text(",".join(map(str, prices)))
    monkeypatch.setenv("CURRENCY", "INR")
    assert sum(prices) == 350


def test_failure_message():
    assert apply_discount(100, 10) == 91                # deliberately wrong: see how pytest explains it
''')

run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "--tb=short"],
                     capture_output=True, text=True)
print(re.sub(r" in \d+\.\d+s", "", run.stdout).strip())
```

```output
```

Five ideas explain most of pytest:

| Feature | What it gives you |
| --- | --- |
| **Plain `assert`** | Introspected failure messages: you see both sides of the comparison |
| **Fixtures** (`@pytest.fixture`) | Reusable set-up and teardown by **dependency injection**: a test names the fixture as a parameter. Scopes: function (default), module, session. `yield` fixtures clean up after the test. Put shared ones in `conftest.py` |
| **Parametrisation** | `@pytest.mark.parametrize` runs one test over many inputs |
| **Built-in helpers** | `tmp_path`, `monkeypatch`, `capsys`, `caplog`, `pytest.raises`, `pytest.approx` (floats) |
| **Markers and selection** | `-k expr`, `-m slow`, `--lf` (last failed), `-x` (stop at first failure), `-q`, `-n auto` (xdist, parallel) |

### Test doubles and async tests

```python Mocking.py
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import json


def get_rate(client, currency):
    response = client.get(f"/rates/{currency}")
    return json.loads(response)["rate"]


client = MagicMock()
client.get.return_value = '{"rate": 83.2}'
print(get_rate(client, "USD"), client.get.call_args.args, client.get.call_count)


class Payments:
    def charge(self, amount):
        raise RuntimeError("real network call!")


with patch.object(Payments, "charge", return_value="ok") as charge:          # replace for the duration of the block
    print(Payments().charge(50), charge.assert_called_once_with(50))


async def notify(mailer, user):
    await mailer.send(user)
    return "sent"


mailer = AsyncMock()                                                           # awaitable mock for async code
print(asyncio.run(notify(mailer, "asha")), mailer.send.await_args.args)
```

```output
```

**Mock at the boundary you own** (the HTTP client, the clock, the payment gateway), not deep inside your logic, and prefer **fakes** (a small in-memory implementation of the interface) over heavy mocking when behaviour matters. `patch` replaces the name **where it is looked up**, not where it is defined (`patch("orders.requests.get")`, not `patch("requests.get")`). Tests of async code use `pytest-asyncio` or `anyio`'s pytest plugin, and FastAPI endpoints are tested with `TestClient` (web stage).

!cheat Testing cheat sheet ::
- Pyramid: many fast unit tests, fewer integration tests (real database via containers), a few end-to-end tests.
- Name tests by behaviour (`test_rejects_negative_amount`); one reason to fail per test; Arrange, Act, Assert.
- Fixtures for set-up, `yield` for tear-down, `conftest.py` for sharing, `parametrize` for cases.
- Isolate time, randomness and the network behind parameters or fakes; use `freezegun`-style clocks sparingly.
- `pytest --cov=pkg --cov-fail-under=85`, `-x`, `--lf`, `-k`, `-n auto`.
- Property-based tests (Hypothesis) generate inputs and shrink failures: great for parsers and invariants.
!end

??  What are pytest fixtures and why are they better than set-up methods?
=> Functions decorated with `@pytest.fixture` that provide data or resources; a test requests one by naming it as a parameter, and pytest builds it (and tears it down after a `yield`). They compose (fixtures can use fixtures), have scopes, and keep the test body free of boilerplate, unlike `setUp` methods shared by a whole class.
??  What is the difference between a mock, a stub and a fake?
=> A **stub** returns canned answers; a **mock** also records and verifies how it was called; a **fake** is a lightweight working implementation (an in-memory repository). Prefer fakes and real components where cheap, because over-mocking makes tests mirror the implementation and break on refactors.
??  How do you test code that depends on the current time or randomness?
=> Inject the dependency (a `clock` callable or `Random` instance) so tests pass a fixed one, or patch the lookup (`monkeypatch.setattr`, `time-machine`/`freezegun`). Never make the test wait on the real clock.

## Packaging and Dependencies

A **distribution** is what you install: a **wheel** (`.whl`, pre-built, fast) or an **sdist** (source archive). It is described by **`pyproject.toml`**, the single standard configuration file, and published to **PyPI** (or a private index).

```python Pyproject.py
import tomllib

PYPROJECT = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shop-api"
version = "1.4.0"
description = "Orders service"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115,<1",
    "sqlalchemy[asyncio]>=2.0",
    "pydantic-settings>=2.4",
]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff", "mypy"]

[project.scripts]
shop-api = "shop.cli:main"              # installs a `shop-api` command

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

config = tomllib.loads(PYPROJECT)
project = config["project"]
print(project["name"], project["version"], project["requires-python"])
print(project["dependencies"][0], list(project["optional-dependencies"]), project["scripts"])
print(config["build-system"]["build-backend"], list(config["tool"]))

from importlib.metadata import version
print("installed fastapi is", "a real version:", version("fastapi").count(".") >= 1)
```

```output
```

| Concept | Meaning |
| --- | --- |
| **Dependency specifiers** | `fastapi>=0.115,<1` (a compatible range); `==1.4.2` (exact); `~=1.4` (compatible release); extras `pkg[extra]` |
| **Lock file** (`uv.lock`, `poetry.lock`, `requirements.txt` with hashes) | The exact resolved versions, for reproducible builds. **Applications lock; libraries declare ranges** |
| **Optional dependencies / dependency groups** | `dev`, `test`, `docs` sets installed on demand |
| **Entry points** | `[project.scripts]` creates console commands; plugin systems use entry-point groups |
| **Versioning** | PEP 440 (`1.4.0`, `1.4.0rc1`); semantic versioning is the convention |
| **Build backends** | `hatchling`, `setuptools`, `flit-core`, `uv_build`: selected under `[build-system]` |
| **Publishing** | `uv build` then `uv publish` (or `twine`); prefer **trusted publishing** (OpenID Connect from CI) over long-lived API tokens |

A day-to-day workflow with uv:

```bash uv workflow
uv init shop-api && cd shop-api          # project skeleton with pyproject.toml
uv add fastapi "sqlalchemy[asyncio]"     # add dependencies; updates pyproject.toml and uv.lock
uv add --dev pytest ruff mypy            # development-only group
uv sync                                  # make .venv match the lock file exactly (use --frozen in CI)
uv run pytest                            # run a command inside the project environment
uv lock --upgrade-package fastapi        # upgrade one dependency, review the diff
uv build                                 # create the wheel and sdist in dist/
```

!warning Supply-chain hygiene :: Typosquatted package names, hijacked maintainer accounts and malicious updates are real. Pin and **hash-verify** dependencies in production images (`uv pip install --require-hashes`), review lock-file diffs in pull requests, scan with `pip-audit` or your platform's dependency scanner, avoid `pip install` of random commands from the internet, and install from your organisation's private index where available.

??  What is the difference between a wheel and an sdist?
=> An sdist is a source archive that needs a build step on install; a wheel is a pre-built archive that is just unpacked, so installs are fast and do not need compilers. Packages with C extensions publish a wheel per platform and Python version (plus an sdist as fallback).
??  Why lock dependencies in applications but use ranges in libraries?
=> An application must behave identically in every environment, so it pins the exact resolved versions. A library is installed alongside other packages and must stay compatible with many versions, so it declares the widest range it supports and lets the application's resolver choose.
??  What goes in `[project.scripts]`?
=> Console entry points: `name = "package.module:function"`. The installer creates an executable `name` that imports and calls that function, which is how `pytest`, `uvicorn` and `ruff` commands exist.

## Code Quality Tooling

A professional Python repository has a small, automated quality gate. The tools below cover formatting, linting, types, tests and secrets, and all read `pyproject.toml`.

| Concern | Tool | Typical command |
| --- | --- | --- |
| Formatting | `ruff format` (or `black`) | `ruff format .` |
| Linting and import sorting | `ruff check` (replaces flake8, isort, pyupgrade, many plug-ins) | `ruff check . --fix` |
| Static types | `mypy`, `pyright` | `mypy src` |
| Tests and coverage | `pytest`, `pytest-cov` | `pytest --cov` |
| Security lint | `bandit`, `ruff` S-rules | `bandit -r src` |
| Dependency audit | `pip-audit`, `uv`, Dependabot / Renovate | `pip-audit` |
| Run on every commit | `pre-commit` hooks | `pre-commit run --all-files` |
| Run on every pull request | CI (GitHub Actions) | same commands, in a clean environment |

```toml pyproject.toml excerpt
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "S", "ASYNC", "SIM", "RUF"]   # pycodestyle, pyflakes, isort, bugbear, pyupgrade, bandit, async checks...
ignore = ["S101"]                                                 # allow assert in tests

[tool.mypy]
strict = true
python_version = "3.12"

[tool.pytest.ini_options]
addopts = "-q --strict-markers"
testpaths = ["tests"]
```

Docstrings document the **contract** (what, arguments, returns, raises) and can double as tests with `doctest`:

```pycon Doctest transcript
>>> def slugify(title):
...     """Turn a title into a URL slug."""
...     return "-".join(title.lower().split())
>>> slugify("Python Full Stack")
'python-full-stack'
>>> slugify("  Many   Spaces ")
'many-spaces'
>>> [slugify(t) for t in ("A B", "C")]
['a-b', 'c']
```

The `pycon` block above is itself executed when this page is built, using the same mechanism as `python -m doctest`, so examples in docstrings cannot drift from the code.

!interview What does a good Python CI pipeline run? :: In a clean environment from the lock file: `ruff check` and `ruff format --check`, `mypy` (or `pyright`), `pytest` with coverage and a threshold, a dependency audit, and a build of the Docker image or wheel. Then fast feedback matters more than completeness: cache dependencies, run unit tests first, and run slow integration tests in a second stage. This is the same quality gate you run locally through pre-commit.

??  Why has ruff replaced flake8, isort and black for many teams?
=> One tool written in Rust does linting (hundreds of rules), import sorting, auto-fixes and formatting 10 to 100 times faster, with a single configuration section in `pyproject.toml`. Fewer tools, faster CI and pre-commit hooks, and consistent results.
??  What do you gain from `mypy --strict` on a new project?
=> Every function must be annotated and `Any` leaks are reported, so type information is complete from the start. It is much cheaper than retrofitting types onto a large untyped codebase, and it catches `None` handling bugs and wrong-argument calls before tests run.
