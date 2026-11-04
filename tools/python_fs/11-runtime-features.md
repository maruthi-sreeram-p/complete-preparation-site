@part py-core-11 | Core Python · Part 11: Decorators, Descriptors, Metaclasses and the Import System | advanced-python
## Decorators in Depth

Part 7 introduced decorators as "function in, wrapper out". The full picture has four variants, and every serious framework uses all of them (`@app.get`, `@pytest.fixture`, `@dataclass`, `@property`, `@login_required`).

```python Decorators.py
import functools


# 1. Function decorator with arguments (a decorator FACTORY)
def log_calls(prefix):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"{prefix} -> {func.__name__}{args}")
            result = func(*args, **kwargs)
            print(f"{prefix} <- {result!r}")
            return result
        return wrapper
    return decorate


# 2. Class-based decorator: keeps state on an instance
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func, self.calls = func, 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


# 3. Decorator that REGISTERS and returns the function unchanged (the Flask / FastAPI style)
ROUTES = {}

def route(path):
    def register(func):
        ROUTES[path] = func
        return func
    return register


# 4. Class decorator: receives and returns a class
def add_repr(cls):
    fields = [n for n in cls.__init__.__code__.co_varnames[1:cls.__init__.__code__.co_argcount]]
    cls.__repr__ = lambda self: f"{cls.__name__}(" + ", ".join(f"{f}={getattr(self, f)!r}" for f in fields) + ")"
    return cls


@log_calls("[trace]")
def add(a, b):
    return a + b

@CountCalls
def ping():
    return "pong"

@route("/health")
def health():
    return "ok"

@add_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


add(2, 3)
ping(); ping()
print(ping.calls, ping.__name__, list(ROUTES), ROUTES["/health"](), Point(1, 2))


# Stacking: decorators apply from the bottom up, and run from the top down
def tag(name):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*a, **k):
            return f"<{name}>{func(*a, **k)}</{name}>"
        return wrapper
    return decorate

@tag("b")
@tag("i")
def text():
    return "hello"

print(text())
```

```output
```

Rules for decorators you will be asked to write:

1. **Always `functools.wraps`**: it preserves `__name__`, `__doc__`, `__wrapped__` and the signature, which FastAPI, pytest, Sphinx and debuggers read. Class-based decorators use `functools.update_wrapper`.
2. **Forward `*args, **kwargs`** and the return value.
3. **Decorating methods works naturally** because `self` is just the first argument; a *class-based* decorator on a method needs a `__get__` (descriptors, next chapter) to bind it.
4. **Async functions** need an `async def wrapper` that `await`s the wrapped call; a sync wrapper around a coroutine function would return an un-awaited coroutine.
5. **Order matters** when stacking: the decorator nearest the function is applied first (`@tag("i")` wraps `text`, then `@tag("b")` wraps that), as the output shows.

!interview Write a decorator that times a function, then make it work with async functions :: Check `inspect.iscoroutinefunction(func)` and return an `async def wrapper` that records `time.perf_counter()` around `await func(...)`; otherwise a sync wrapper. Mention `functools.wraps`, use `try/finally` so the time is recorded on exceptions too, and that for production you would emit a metric (Prometheus histogram) rather than print.

??  What does `@decorator` do exactly?
=> It is syntax for `func = decorator(func)` executed once, when the function is defined. For `@decorator(args)` Python first calls `decorator(args)` and applies the returned callable to the function. Class decorators work the same way on a class.
??  Why does a decorated function show the wrong name without `functools.wraps`?
=> The returned wrapper is a different function named `wrapper`, so `__name__`, `__doc__` and the signature belong to it. `wraps` copies the original metadata onto the wrapper (and sets `__wrapped__`), so tools see what you expect.
??  How would you apply the same behaviour to every method of a class?
=> Use a class decorator that loops over the class namespace and wraps each callable (`for name, value in vars(cls).items(): ...setattr(cls, name, deco(value))`), or implement `__init_subclass__` or a metaclass. Think twice: explicit decoration is usually clearer.

## Descriptors and the Attribute Machinery

A **descriptor** is an object with `__get__`, and optionally `__set__` and `__delete__`, stored as a **class attribute**. When an attribute is looked up on an instance, Python checks the class for a descriptor first and calls its methods. This one mechanism implements `property`, methods, `classmethod`, `staticmethod`, `__slots__` and the fields of Django and SQLAlchemy models.

```python Descriptors.py
class Positive:
    """A reusable validated field."""

    def __set_name__(self, owner, name):          # called once when the class is created
        self.private = "_" + name

    def __get__(self, instance, owner):
        if instance is None:                       # accessed on the class itself
            return self
        return getattr(instance, self.private)

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.private[1:]} must be positive, got {value}")
        setattr(instance, self.private, value)


class Product:
    price = Positive()                             # one descriptor object shared by all instances
    quantity = Positive()

    def __init__(self, price, quantity):
        self.price, self.quantity = price, quantity   # these go through Positive.__set__


p = Product(9.99, 3)
print(p.price, p.quantity, vars(p))
try:
    p.quantity = -1
except ValueError as error:
    print("ValueError:", error)

# Functions are non-data descriptors: that is how methods get bound
class Greeter:
    def hi(self):
        return "hi"

g = Greeter()
print(type(Greeter.__dict__["hi"]).__name__, Greeter.hi.__get__(g, Greeter)(), g.hi.__self__ is g)
```

```output
```

| Kind | Defines | Lookup precedence |
| --- | --- | --- |
| **Data descriptor** | `__get__` and `__set__` (or `__delete__`) | Beats the instance `__dict__` |
| **Non-data descriptor** | only `__get__` (functions, `classmethod`, `cached_property`) | The instance `__dict__` wins over it |
| Plain class attribute | no descriptor methods | Instance `__dict__` wins |

### `__getattr__`, `__getattribute__` and `__setattr__`

```python Hooks.py
class Config:
    def __init__(self, **values):
        self.__dict__["_values"] = dict(values)

    def __getattr__(self, name):                   # called ONLY when normal lookup fails
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(f"no setting {name!r}") from None

    def __setattr__(self, name, value):            # called for EVERY assignment
        print(f"set {name}")
        self._values[name] = value


c = Config(host="localhost")
print(c.host)
c.port = 8000
print(c.port, hasattr(c, "missing"))
```

```output
```

`__getattr__` is a **fallback** for missing attributes (proxies, lazy loading, dynamic APIs); `__getattribute__` runs for **every** access and is easy to make infinitely recursive, so use it only when you must. Reading `self.x` inside them needs care: go through `object.__getattribute__` or `self.__dict__`.

!realworld Where descriptors hide :: Django model fields (`name = models.CharField()`), SQLAlchemy columns (`Mapped[str]`), Pydantic and dataclass fields, `@property`, `@cached_property`, `functools.partialmethod` and every bound method are all descriptors. When a framework "magically" turns a class attribute into per-instance data and per-class metadata, a descriptor (often with `__set_name__`) is how.

??  What is a descriptor and where is it stored?
=> An object implementing `__get__` (and optionally `__set__`/`__delete__`) that is stored as an attribute of a **class**. Attribute access on instances is routed through it, which is how properties, methods, `classmethod` and ORM fields are implemented.
??  What is the difference between a data and a non-data descriptor?
=> A data descriptor defines `__set__` or `__delete__` as well as `__get__` and takes precedence over the instance dictionary; a non-data descriptor only defines `__get__`, so an instance attribute of the same name overrides it. Functions are non-data descriptors, which is why you can shadow a method on one instance.
??  When is `__getattr__` called, compared with `__getattribute__`?
=> `__getattribute__` is called for every attribute access; `__getattr__` is called only after normal lookup (instance, class, bases) has raised `AttributeError`. Implement `__getattr__` for fallbacks; override `__getattribute__` rarely and carefully.

## Classes Are Objects: `type`, `__init_subclass__` and Metaclasses

A class is an instance of its **metaclass**; by default `type`. The `class` statement is a convenient way to call `type(name, bases, namespace)`, which you can also do by hand to create classes at run time:

```python Metaclass.py
# The two spellings are equivalent
def hello(self):
    return "hello"

Dynamic = type("Dynamic", (object,), {"hello": hello, "kind": "generated"})
print(Dynamic().hello(), Dynamic.kind, type(Dynamic).__name__, Dynamic.__name__)


# 1. The modern, simple hook: __init_subclass__ runs when a subclass is DEFINED
class Plugin:
    registry = {}

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[name or cls.__name__.lower()] = cls


class CsvExporter(Plugin, name="csv"):
    pass

class JsonExporter(Plugin):
    pass

print(sorted(Plugin.registry), Plugin.registry["csv"] is CsvExporter)


# 2. A metaclass changes how classes are built; here it enforces a rule at class-creation time
class RequireDocstrings(type):
    def __new__(mcls, name, bases, namespace):
        for key, value in namespace.items():
            if callable(value) and not key.startswith("_") and not value.__doc__:
                raise TypeError(f"{name}.{key} needs a docstring")
        return super().__new__(mcls, name, bases, namespace)


class Documented(metaclass=RequireDocstrings):
    def ok(self):
        """Has a docstring."""

try:
    class Sloppy(metaclass=RequireDocstrings):
        def missing(self):
            return 1
except TypeError as error:
    print("TypeError:", error)

print(type(Documented).__name__, isinstance(Documented, type))
```

```output
```

| Tool | When |
| --- | --- |
| **Class decorator** | Modify or register a class after it is built. Simplest |
| **`__init_subclass__`** | React to subclassing: plugin registries, validation, default attributes. Covers most "metaclass" needs |
| **`__set_name__`** | A descriptor learns its attribute name |
| **Metaclass** | Change class *creation* itself: control the namespace (`__prepare__`), inject methods, build a model from field declarations (Django ORM, SQLAlchemy declarative, `Enum`, `ABCMeta`) |

!warning Metaclasses are a last resort :: "Metaclasses are deeper magic than 99% of users should ever worry about" (Tim Peters). They complicate inheritance (conflicting metaclasses), debugging and tool support. Reach for a decorator, `__init_subclass__` or composition first. You need to *understand* them because frameworks use them, not because your code should.

??  What is a metaclass?
=> The class of a class: the callable that builds a class object from its name, bases and namespace. By default it is `type`. A custom metaclass can validate or transform the class body, register classes or add methods; `ABCMeta` and `EnumMeta` are examples in the standard library.
??  How can you create a class dynamically?
=> Call `type(name, bases, namespace)` (or `types.new_class` for more control). It returns a class object just like the `class` statement would.
??  When would you choose `__init_subclass__` over a metaclass?
=> Whenever you only need to run code when a subclass is defined (register it, validate attributes, set defaults). It is simpler, composes with multiple inheritance and does not create metaclass conflicts.

## Introspection and Reflection

Python lets a program inspect itself, which is the basis of dependency injection, serialisation, ORMs, test discovery and API frameworks.

```python Introspection.py
import inspect
from dataclasses import dataclass, fields
from typing import Annotated, get_type_hints


def create_user(name: str, age: int = 18, *tags: str, active: bool = True) -> dict:
    """Create a user."""


sig = inspect.signature(create_user)
for param in sig.parameters.values():
    default = "required" if param.default is inspect.Parameter.empty else param.default
    print(f"{param.name:<8} {param.kind.name:<17} annotation={getattr(param.annotation, '__name__', param.annotation)} default={default}")
print(sig.return_annotation.__name__, get_type_hints(create_user)["age"])


@dataclass
class Item:
    name: str
    price: float = 0.0

    def total(self, qty: int) -> float:
        return self.price * qty

print([f.name for f in fields(Item)], [n for n, _ in inspect.getmembers(Item, inspect.isfunction)][:3])
item = Item("pen", 2.5)
method = getattr(item, "total")                       # attribute access by NAME at run time
print(method(4), hasattr(item, "colour"), getattr(item, "colour", "none"))
setattr(item, "colour", "blue")
print(vars(item), type(item).__mro__[0].__name__, callable(method), inspect.isclass(Item))

# How a framework decides what to inject: it reads the signature of YOUR function
def handler(request, user_id: int, db):
    pass

print([p for p in inspect.signature(handler).parameters])
```

```output
```

The last lines are the idea behind **FastAPI**: it calls `inspect.signature` on your endpoint, reads each parameter's name, annotation and default, and decides whether it comes from the path, the query string, the body or a dependency. That is why `functools.wraps` matters in decorators (it keeps the signature visible), and why type hints are a runtime API as well as documentation.

| Function | Purpose |
| --- | --- |
| `type(x)`, `isinstance`, `issubclass` | Type tests |
| `dir(x)`, `vars(x)`, `x.__dict__` | Names available; instance attributes |
| `getattr`, `setattr`, `hasattr`, `delattr` | Attribute access by string |
| `inspect.signature`, `getmembers`, `getsource`, `iscoroutinefunction` | Structure of callables and modules |
| `typing.get_type_hints(obj)` | Resolved annotations (including forward references) |
| `importlib.metadata.entry_points()` | Plugins registered by installed packages |

??  How does FastAPI know which arguments of your function come from the request?
=> It inspects the function's signature (`inspect.signature` and type hints): parameters that match path placeholders come from the path, parameters with simple types from the query string, Pydantic model types from the body, and parameters whose default is `Depends(...)` from a dependency. The annotations are read at run time.
??  When is `getattr(obj, name)` better than `obj.name`?
=> When the attribute name is data (from configuration, a request or a loop): dispatching to `handle_<command>` methods, serialising fields by name, plugin lookup. Never pass untrusted names to `getattr`/`setattr`, since they can reach internal attributes.

## Modules and the Import System

`import shop.orders` does four things: look the name up in `sys.modules` (a cache), and if absent **find** the module (finders walk `sys.path`), **load** it (compile or read `.pyc`, execute the top-level code **once**) and **bind** the result. Because the module object is cached, a module is effectively a **singleton**, and top-level code is the right place for definitions but the wrong place for side effects.

```python Imports.py
import importlib
import pathlib
import sys

root = pathlib.Path("demo")
(root / "shop").mkdir(parents=True)
(root / "shop" / "__init__.py").write_text("print('shop package imported')\nVERSION = '1.0'\n")
(root / "shop" / "orders.py").write_text("print('orders module executed')\ndef count():\n    return 3\n")
(root / "shop" / "util.py").write_text("from . import orders          # relative import\ndef twice():\n    return orders.count() * 2\n")
sys.path.insert(0, str(root))

import shop.orders                                  # runs shop/__init__.py, then orders.py
import shop.orders as again                         # second import: served from sys.modules, nothing printed
print(shop.orders is again, "shop.orders" in sys.modules, shop.VERSION)

from shop.util import twice
print(twice())

module = importlib.import_module("shop." + "orders")   # import by name computed at run time
print(module.__name__, module.__file__.endswith("orders.py"), module.__package__)

(root / "shop" / "orders.py").write_text("print('orders v2')\ndef count():\n    return 30\n")
importlib.invalidate_caches()
print(shop.orders.count())                          # unchanged: the module object is cached
importlib.reload(shop.orders)                       # explicit re-execution (rarely a good idea)
print(shop.orders.count())

namespace = root / "ns_pkg"                         # a folder WITHOUT __init__.py is a namespace package
namespace.mkdir()
(namespace / "a.py").write_text("X = 1\n")
import ns_pkg.a
print(ns_pkg.a.X, ns_pkg.__file__)
```

```output
```

### Circular imports

Two modules that import each other at the top level can fail, because the first is only **partially initialised** when the second asks for it:

```python Circular.py
import pathlib
import sys

pathlib.Path("a.py").write_text("from b import b_func\n\ndef a_func():\n    return 'a'\n")
pathlib.Path("b.py").write_text("from a import a_func\n\ndef b_func():\n    return 'b'\n")
sys.path.insert(0, ".")

try:
    import a
except ImportError as error:
    print("ImportError:", str(error).split(" (")[0])

# Fix 1: import the MODULE and use the attribute later; Fix 2: import inside the function; Fix 3: move shared code to a third module
pathlib.Path("c.py").write_text("import d\n\ndef c_func():\n    return 'c' + d.d_func()\n")
pathlib.Path("d.py").write_text("def d_func():\n    import c                      # deferred import: runs only when called\n    return 'd'\n")
import c
print(c.c_func())
```

```output
```

Import rules for large codebases: use **absolute imports** at module top; **relative imports** only inside a package; no `from x import *` (it hides where names come from and defeats linters); put an `__all__` list in a package's public module to define its API; keep top-level code free of I/O, and move heavy imports (pandas, torch) inside the functions that need them when start-up time matters (`python -X importtime -c "import app"` shows the cost of each import). Python 3.15 is expected to add an explicit *lazy import* syntax (PEP 810); until then, deferred imports inside functions are the tool.

!cheat Import system cheat sheet ::
- `sys.modules` caches modules: top-level code runs once; a module is a singleton.
- `sys.path` is searched in order: script folder, `PYTHONPATH`, standard library, `site-packages`.
- Package = folder with `__init__.py` (or a namespace package without it). Absolute imports by default; `from . import x` inside a package.
- Circular imports: import the module not the name, defer the import into the function, or extract shared code.
- Never name a file after a library (`random.py`, `email.py`); never `import *`.
- `importlib.import_module(name)` for dynamic imports; `importlib.metadata.entry_points` for plugins; `-X importtime` for start-up cost.
!end

??  What happens when you import a module twice?
=> The first import finds, compiles and executes it, then stores the module object in `sys.modules`. The second import returns that cached object, so the top-level code does not run again. `importlib.reload` re-executes it explicitly.
??  Why do circular imports fail and how do you fix them?
=> When `a` imports `b` during its own initialisation and `b` imports names from `a`, the module `a` exists in `sys.modules` but has not defined those names yet. Fix by restructuring (move shared code into a third module), importing the module instead of the name, or importing inside the function that needs it.
??  What is the difference between a regular package and a namespace package?
=> A regular package has an `__init__.py` and lives in one directory. A namespace package has no `__init__.py` and can be spread over several directories on `sys.path`, which lets separately installed distributions contribute to one package name.

## Calling Native Code: ctypes, struct and C Extensions

Python often wraps C: NumPy, `cryptography`, `lxml`, `psycopg`, `orjson`, `uvloop`, PyTorch. You meet native code in three ways:

| Approach | What it is | When |
| --- | --- | --- |
| **`ctypes`** (standard library) | Call functions in shared libraries directly from Python, describe C structs | Quick bindings to an existing library, no compiler |
| **`cffi`** | Cleaner foreign-function interface from C declarations | Larger bindings, PyPy-friendly |
| **C extension / Cython / pybind11 / PyO3 (Rust)** | Compiled modules using the CPython C API | Performance-critical code, new native libraries |

```python Native.py
import ctypes
import struct

class Point(ctypes.Structure):                       # a C struct in memory
    _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_int32)]

p = Point(3, 4)
print(ctypes.sizeof(p), p.x + p.y, bytes(p).hex())

buffer = ctypes.create_string_buffer(b"hello", 16)    # a mutable C char[16]
print(len(buffer), buffer.value, buffer.raw[:6])

packed = struct.pack("<I H 4s", 258, 7, b"abcd")      # fixed binary layouts: network and file formats
print(packed.hex(), struct.unpack("<I H 4s", packed), struct.calcsize("<IH4s"))

view = memoryview(bytearray(b"abcdef"))               # zero-copy slices of a buffer
part = view[2:5]
part[0] = ord("X")
print(bytes(view))
```

```output
```

`struct` packs and unpacks fixed binary layouts (network protocols, file headers); `memoryview` exposes the **buffer protocol** so that slicing does not copy; `ctypes` maps C types. Calling a real library function is `ctypes.CDLL("libname").function`, with `argtypes` and `restype` set explicitly, because a wrong signature crashes the interpreter instead of raising an exception.

!warning Native code can crash the whole process :: A bad pointer in `ctypes`, or a bug in a C extension, produces a segmentation fault that no `try/except` can catch, taking down the worker. Enable `faulthandler` (below) in production so a crash leaves a Python traceback, pin extension versions, and isolate risky native work in a subprocess.

??  When would you write a C extension or use Cython instead of staying in Python?
=> When profiling shows a small hot loop dominating run time that cannot be vectorised with NumPy or sped up algorithmically, or when you need to wrap an existing C/C++/Rust library. Cython, pybind11 and PyO3 make this far less painful than hand-written C API code.
??  What is the buffer protocol and why does it matter?
=> A C-level interface that lets objects (`bytes`, `bytearray`, `array`, NumPy arrays, `mmap`) expose their raw memory so that others can read or write it without copying. `memoryview` is the Python face, and it is how large binary data is handled efficiently.

## Troubleshooting Playbook and Diagnostics Toolbox

Most production problems fall into a few shapes. Match the symptom to the tool:

| Symptom | First look | Tools |
| --- | --- | --- |
| Exception in logs | The last traceback line, then the frame in your code | `logger.exception`, Sentry, `traceback` |
| Wrong result | Reproduce minimally; print intermediate values | `breakpoint()`, `pdb`, tests, `repr()` |
| Hangs / stuck request | Where is every thread right now? | `py-spy dump --pid`, `faulthandler.dump_traceback_later(30)` |
| High CPU | Which function? | `py-spy top`, `cProfile`, `pyinstrument` |
| Memory growing | Who allocates, who holds | `tracemalloc`, `memray`, `objgraph` |
| Slow start-up | Which imports? | `python -X importtime` |
| Crash with no traceback | A native fault | `faulthandler` / `python -X faulthandler`, core dump |
| Works locally, fails in the container | Different Python, packages or encoding | `python -VV`, `pip freeze`, `sys.path`, `locale`, `PYTHONUTF8` |
| Warnings you ignore | They become errors in the next release | `python -W error`, `-X dev` |

```python Faulthandler.py
import faulthandler
import sys


def inner():
    faulthandler.dump_traceback(file=sys.stdout, all_threads=False)   # what every thread is doing, right now


def outer():
    inner()


outer()
```

```output
```

`faulthandler.dump_traceback_later(30, repeat=True)` prints every thread's stack if the program is still running after 30 seconds, which is the cheapest way to see **why a process is hung**; `python -X faulthandler` or `faulthandler.enable()` also dumps the traceback on a crash. Add `-X dev` (or `PYTHONDEVMODE=1`) in tests to enable extra runtime checks, such as resource warnings for unclosed files and the asyncio debug mode.

### A short debugging method

1. **Read the whole traceback** from the bottom; identify the first frame in *your* code.
2. **Reproduce** with the smallest input; write it as a failing test.
3. **Form one hypothesis** and test it (a print, a `breakpoint()`, an assertion), instead of changing things at random.
4. **Check assumptions about the environment**: which interpreter, which versions, which environment variables.
5. **Fix the cause**, keep the test, and add logging or a metric if the failure was hard to see.

!interview "A Python service hangs in production. What do you do?" :: Get a stack dump of the live process without restarting it (`py-spy dump --pid <pid>` or a `faulthandler` timer or signal handler), look for threads blocked on locks, sockets or queues, and for an event loop stuck in a blocking call. Check external dependencies (database locks, a call without a timeout), then thread and connection pool saturation. Fix with timeouts, bounded pools and, for asyncio, removing blocking calls. Then add the signal that would have caught it: a latency alert, a health check that exercises the dependency.

??  How do you find out why a Python process is stuck?
=> Dump the stacks of all threads: `py-spy dump --pid`, `faulthandler.dump_traceback_later` or a signal-triggered dump. Look at what each thread (or the single event-loop thread) is waiting on: a lock, a socket read without timeout, a queue, a blocking call inside a coroutine.
??  What does `python -X dev` give you?
=> Development mode enables additional runtime checks: warnings for resource leaks (unclosed files), asyncio debug mode, faulthandler, stricter memory-allocator checks and more visible deprecation warnings. Use it in tests and CI to catch problems early.
