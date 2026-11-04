@part py-core-3 | Core Python · Part 3: Object-Oriented Python | core-python
## Classes and Objects

A class is a **template that is itself an object**. Calling it creates an instance: Python allocates the object (`__new__`) and then initialises it (`__init__`). Methods are plain functions stored in the class; when you access one through an instance, Python **binds** the instance to the first parameter, conventionally called `self`.

```python Account.py
class Account:
    bank = "Trail Bank"                 # class attribute: shared by all instances
    count = 0

    def __init__(self, owner, balance=0):
        self.owner = owner              # instance attributes live in self.__dict__
        self.balance = balance
        Account.count += 1

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def __repr__(self):
        return f"Account(owner={self.owner!r}, balance={self.balance})"

    @classmethod
    def opened(cls, owner):             # alternative constructor: receives the class
        return cls(owner, balance=100)

    @staticmethod
    def valid_owner(name):              # no self, no cls: just a namespaced function
        return bool(name.strip())


a = Account("Asha", 50)
b = Account.opened("Ravi")
a.deposit(25)
print(a, b, Account.count)
print(a.__dict__, Account.bank, a.bank)
print(Account.valid_owner("  "), a.deposit, Account.deposit(a, 5))
```

```output
```

Read the last line: `a.deposit` is a **bound method**, and `Account.deposit(a, 5)` is exactly what `a.deposit(5)` expands to. There is no hidden magic: `self` is an ordinary parameter that Python fills in.

### Where attributes live, and how lookup works

`a.x` searches, in order: **data descriptors on the type** (such as properties), the **instance** `__dict__`, then the **class and its bases** (in MRO order). Assignment `a.x = 1` always writes to the instance, never the class. That asymmetry creates the classic shared-state bug:

```python ClassVsInstance.py
class Team:
    members = []                 # class attribute: ONE list for every Team

    def __init__(self, name):
        self.name = name

    def add(self, person):
        self.members.append(person)   # mutates the shared list

x, y = Team("x"), Team("y")
x.add("asha")
print(y.members, x.members is y.members)

x.count = 5                      # writes to the INSTANCE, shadowing any class attribute
print(x.count, hasattr(y, "count"))

class FixedTeam:
    def __init__(self, name):
        self.members = []        # per-instance state belongs in __init__
        self.name = name
```

```output
```

!tip Three method kinds, one rule :: Instance method: needs this object's data (`self`). `@classmethod`: needs the class, typically an alternative constructor (`Account.opened`) or a factory that works in subclasses (`cls(...)`). `@staticmethod`: needs neither; it is a function that lives in the class for organisation, and often belongs at module level instead.

### Python versus Java in one table

| Java | Python |
| --- | --- |
| Fields declared in the class body | Attributes created on assignment, normally in `__init__` |
| `this` (implicit) | `self` (explicit first parameter) |
| Constructor overloading | One `__init__` with default/keyword arguments, plus `@classmethod` factories |
| `static` field and method | Class attribute, `@classmethod`, `@staticmethod` |
| `toString()`, `equals()`, `hashCode()` | `__str__`/`__repr__`, `__eq__`, `__hash__` |
| `new Account("Asha")` | `Account("Asha")` |

??  What is `self`, and is it a keyword?
=> It is just the conventional name of the first parameter of an instance method. When you call `obj.method()`, Python passes `obj` as that first argument (the function is bound to the instance on attribute access). It is not a keyword, but every tool and reader expects it to be called `self`.
??  What is the difference between a class attribute and an instance attribute?
=> A class attribute lives in the class and is shared by all instances (and found by lookup when the instance has no attribute of that name). An instance attribute lives in the instance's `__dict__`. Assigning through an instance always creates or updates the instance attribute, so mutable class attributes (a shared list) are a common bug.
??  When do you use @classmethod and when @staticmethod?
=> `@classmethod` when the method needs the class: alternative constructors (`from_json`, `opened`) and factories that must work for subclasses via `cls`. `@staticmethod` when it needs neither the instance nor the class and is only grouped with the class for organisation; often a module-level function is clearer.
!qa
What does this print, and why do `a` and `b` disagree?
```python Shadow.py
class Counter:
    total = 0

a, b = Counter(), Counter()
a.total += 1          # reads Counter.total (0), writes a NEW instance attribute
Counter.total += 10   # changes the class attribute
print(a.total, b.total, Counter.total)
```
=>
```output
```
`a.total += 1` is `a.total = a.total + 1`: it reads the class value 0 but stores 1 on the **instance**, which then shadows the class attribute. `b` has no instance attribute, so it sees the class value 10.
!end

## Encapsulation and Properties

Python has **no access modifiers**. It has conventions that tools and teammates respect:

| Spelling | Meaning |
| --- | --- |
| `name` | Public API |
| `_name` | "Internal: do not rely on it". Not enforced |
| `__name` | **Name mangled** to `_ClassName__name` to avoid clashes in subclasses. Not privacy |
| `__name__` | Reserved for Python (dunder names). Do not invent your own |

Instead of writing `getX()` and `setX()` up front, expose a plain attribute. If you later need validation or a computed value, turn it into a **property** without changing any caller. That freedom is why Python code does not start with getters.

```python Properties.py
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius            # goes through the setter below

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):                 # read-only computed attribute
        return self._celsius * 9 / 5 + 32


t = Temperature(25)
t.celsius = 30
print(t.celsius, t.fahrenheit)
try:
    t.celsius = -300
except ValueError as error:
    print("rejected:", error)
try:
    t.fahrenheit = 100
except AttributeError as error:
    print("AttributeError:", error)
```

```output
```

```python Mangling.py
class Base:
    def __init__(self):
        self.__secret = "base"      # stored as _Base__secret
        self._hint = "internal"

class Child(Base):
    def __init__(self):
        super().__init__()
        self.__secret = "child"     # stored as _Child__secret: no clash

c = Child()
print(sorted(vars(c)))
print(c._Base__secret)              # still reachable: mangling is not security
```

```output
```

!interview Is there private in Python? :: No: by design Python trusts developers ("we are all consenting adults"). A leading underscore is a signal, name mangling prevents *accidental* clashes in inheritance, and nothing stops `obj._Class__name`. If you need real protection from untrusted code you use a process or sandbox boundary, not attribute naming.

??  Why do Python classes usually not have getters and setters?
=> Public attributes can later be replaced by properties with the same name, so callers never change. Writing `get_x`/`set_x` up front adds noise without benefit. Use properties only when you need validation, laziness, a computed value or a read-only attribute.
??  What does a double leading underscore do?
=> It triggers name mangling: inside a class body `__x` becomes `_ClassName__x`. The purpose is to avoid accidental name clashes between a class and its subclasses, not to hide data; the mangled name is still accessible.
??  How do you make an attribute read-only?
=> Define a `@property` with a getter and no setter (assignment then raises `AttributeError`), or make the class frozen with `@dataclass(frozen=True)`, or use `__slots__` with a read-only property. Python cannot make a plain attribute truly immutable.

## Inheritance, super() and the MRO

```python Inheritance.py
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

    def intro(self):
        return f"I am {self.name}. {self.speak()}"      # late binding: calls the subclass's speak


class Dog(Animal):
    def __init__(self, name, trick):
        super().__init__(name)                          # run the parent's initialiser
        self.trick = trick

    def speak(self):
        return f"{self.name} barks"


d = Dog("Rex", "sit")
print(d.intro())
print(isinstance(d, Animal), issubclass(Dog, Animal), type(d).__name__, Dog.__mro__)
```

```output
```

Every method call is **dynamically dispatched**: `intro` is defined in `Animal`, but `self.speak()` finds `Dog.speak` because lookup starts at the object's real type. There is no `virtual` keyword and no `@Override` requirement (the optional `typing.override` decorator in 3.12+ lets a type checker verify you really override something).

### Multiple inheritance and the MRO

Python allows several base classes. To decide which method wins, each class gets a **method resolution order** (MRO) computed by the **C3 linearisation**: a list in which every class appears before its bases and the order you wrote the bases in is preserved. `super()` does not mean "the parent": it means **"the next class in the MRO of the instance's type"**.

```python Diamond.py
class A:
    def hello(self):
        return ["A"]

class B(A):
    def hello(self):
        return ["B"] + super().hello()

class C(A):
    def hello(self):
        return ["C"] + super().hello()

class D(B, C):
    def hello(self):
        return ["D"] + super().hello()

print(D().hello())
print([k.__name__ for k in D.__mro__])
```

```output
```

`D().hello()` visits `D`, `B`, `C`, `A`, each exactly once: `B`'s `super()` goes to `C` (the next class in `D`'s MRO), not to `A`. This **cooperative** style works when every method calls `super()`. It is also why multiple inheritance is used mostly for **mixins**: small classes that add one capability and are written to cooperate.

```python Mixin.py
import json

class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=True)

class ReprMixin:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(vars(self).items()))
        return f"{type(self).__name__}({fields})"

class User(JsonMixin, ReprMixin):
    def __init__(self, name, age):
        self.name, self.age = name, age

u = User("Asha", 30)
print(u.to_json())
print(u)
```

```output
```

!warning Prefer composition when the relationship is "has a" :: Inheritance couples a subclass to every detail of its base. If you are tempted to inherit only to reuse code (`class Stack(list)`, `class OrderService(Repository)`), hold the other object in an attribute and delegate instead. A class that *is* a kind of the other (a `Dog` is an `Animal`, a `ValidationError` is an `Exception`) is the legitimate use.

!cheat Inheritance in five lines ::
- Lookup order is `type(obj).__mro__`; print it when behaviour surprises you.
- `super()` = next class in the MRO of the instance, so it is cooperative, not "the parent".
- Call `super().__init__(...)` in every `__init__` you override, or the base is not initialised.
- Mixins: small, state-free, one capability, placed to the **left** of the main base.
- `isinstance(x, A)` accepts subclasses; `type(x) is A` does not. Prefer `isinstance`.
!end

??  What is the MRO and how is it computed?
=> The method resolution order is the sequence of classes Python searches for an attribute: `Class.__mro__`. It is computed by C3 linearisation, which keeps the order of bases as written, ensures each class appears before its parents, and raises `TypeError` if no consistent order exists.
??  What does `super()` actually do in multiple inheritance?
=> It returns a proxy that delegates to the **next class after the current one in the MRO of the object's type**. In a diamond that is how each class's method runs exactly once when every method calls `super()`; it is not necessarily the direct parent.
??  Why can forgetting `super().__init__()` be a bug?
=> The base class's initialiser never runs, so attributes it sets are missing (an `AttributeError` later), resources it opens are not created, and in cooperative multiple inheritance the rest of the chain is skipped.
??  When do you choose composition over inheritance?
=> When the relationship is "has a" or "uses a", when you only want to reuse code, when the base class has a wide interface you do not want to expose, or when behaviour should be swapped at run time (a strategy object). Choose inheritance for a genuine "is a" relationship with substitutable behaviour.

## The Data Model: Special Methods

Python's operators and built-in functions are **protocols** built on special ("dunder") methods. `len(x)` calls `x.__len__()`, `x + y` calls `x.__add__(y)`, `for i in x` calls `x.__iter__()`. Implement the methods and your objects work with the whole language, which is the reason Python code feels uniform.

| You write | Python calls | Purpose |
| --- | --- | --- |
| `repr(x)`, `str(x)` | `__repr__`, `__str__` | Debug form, display form |
| `x == y`, `x != y` | `__eq__` | Equality |
| `hash(x)`, `x in {..}` | `__hash__` | Dictionary and set keys |
| `x < y` etc. | `__lt__`, `__le__`, ... | Ordering, sorting |
| `len(x)`, `bool(x)` | `__len__`, `__bool__` | Size, truthiness |
| `x[i]`, `x[i] = v` | `__getitem__`, `__setitem__` | Indexing and slicing |
| `for a in x`, `a in x` | `__iter__`, `__contains__` | Iteration, membership |
| `x(args)` | `__call__` | Callable objects |
| `x + y`, `x * 2` | `__add__`, `__mul__` (and `__radd__`) | Arithmetic |
| `with x:` | `__enter__`, `__exit__` | Context managers (Part 5) |

```python Vector.py
from functools import total_ordering
import math

@total_ordering
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented            # let Python try the other side, then give up
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))        # equal objects MUST have equal hashes

    def __lt__(self, other):
        return abs(self) < abs(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__                       # makes 2 * v work too

    def __bool__(self):
        return bool(self.x or self.y)

    def __len__(self):
        return 2

    def __getitem__(self, index):
        return (self.x, self.y)[index]


v, w = Vector(3, 4), Vector(1, 1)
print(v + w, 2 * v, abs(v), v == Vector(3, 4), v > w)
print(len({v, Vector(3, 4), w}), bool(Vector(0, 0)), list(v), v[1], max(v, w))
```

```output
```

Notice that `list(v)` worked without an `__iter__`: Python falls back to the **sequence protocol** (`__getitem__` with 0, 1, 2 ... until `IndexError`). Notice also that `v > w` worked from `__lt__` alone because `@total_ordering` filled in the rest.

### The equality and hashing contract

If two objects are equal they must have the same hash, or dictionaries and sets misbehave. Python protects you in one direction: **defining `__eq__` without `__hash__` makes the class unhashable**.

```python HashContract.py
class Point:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x

p = Point(1)
print(p == Point(1))
try:
    {p}
except TypeError as error:
    print("TypeError:", error)
```

```output
```

For **mutable** objects, do not define `__hash__`: a key whose hash changes after insertion is lost in the dictionary. Make the class immutable (frozen dataclass, named tuple) when you want it hashable.

!interview What is `NotImplemented` for? :: Binary operator methods return it (not raise it) to say "I do not know how to handle this operand type". Python then tries the reflected method on the other operand (`__radd__`, `__eq__` of the right side) and finally raises `TypeError` (or for `==`, falls back to identity). Raising `TypeError` yourself would block the other operand's chance.

??  What is the difference between `__str__` and `__repr__`, and which should you always write?
=> `__repr__` is the unambiguous developer view (shown in the REPL, tracebacks and containers); `__str__` is the friendly view used by `print` and `str()`. Always write `__repr__`; `__str__` falls back to it when absent.
??  Why does defining `__eq__` make a class unhashable?
=> Because the default identity-based hash would no longer agree with your equality (equal objects could have different hashes). Python therefore sets `__hash__ = None`. Define `__hash__` from the same fields as `__eq__`, only for immutable objects.
??  How can your own class support `len()`, `for` loops and `in`?
=> Implement `__len__`, `__iter__` (or `__getitem__`, which gives iteration through the sequence protocol) and `__contains__` (otherwise `in` falls back to iterating). Python treats these as protocols: any object that provides the methods works.
??  What does `@functools.total_ordering` do?
=> Given `__eq__` and one of `__lt__`, `__le__`, `__gt__`, `__ge__`, it generates the other three comparison methods. It is convenient but slower than writing all four, so for hot paths use a dataclass with `order=True` or a key function.

## Abstract Classes, Protocols and Duck Typing

Python's default style is **duck typing**: "if it walks like a duck and quacks like a duck, it is a duck". A function that needs `.read()` simply calls it; the caller can pass a file, a `StringIO`, a socket wrapper or a test fake. There is no interface to implement. When you do want a *contract*, you have two tools.

### Abstract base classes (nominal)

```python Abstract.py
from abc import ABC, abstractmethod
from math import pi

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    def describe(self):
        return f"{type(self).__name__} with area {self.area():.2f}"

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return pi * self.r ** 2

print(Circle(2).describe())
try:
    Shape()
except TypeError as error:
    print("TypeError:", error)
```

```output
```

An ABC cannot be instantiated until every abstract method is overridden, which is Java's `abstract class` and `interface` in one tool. The standard library's `collections.abc` (`Iterable`, `Sequence`, `Mapping`, `MutableMapping`...) are ABCs: subclass `MutableMapping`, implement five methods and you get the rest of the dict API for free.

### Protocols (structural)

`typing.Protocol` describes a contract by **shape**. A class satisfies it without inheriting from it, which is how type checkers model duck typing:

```python Protocols.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class Connection:                      # note: no base class
    def close(self) -> None:
        print("connection closed")

def shutdown(resource: Closeable) -> None:
    resource.close()

shutdown(Connection())
print(isinstance(Connection(), Closeable), isinstance(42, Closeable))
```

```output
```

Use an ABC when you control the hierarchy and want shared code and enforcement at instantiation; use a Protocol when you want to accept anything of the right shape (including third-party classes) and let mypy or pyright check it.

### EAFP: ask forgiveness, not permission

```python Eafp.py
config = {"port": "8080"}

# LBYL (look before you leap)
if "port" in config and config["port"].isdigit():
    port = int(config["port"])

# EAFP (easier to ask forgiveness than permission): the idiomatic style
try:
    port = int(config["port"])
except (KeyError, ValueError):
    port = 8000

print(port)
```

```output
```

EAFP avoids race conditions (the file you checked can vanish before you open it), is usually shorter, and costs nothing when the exception does not happen. It is the dominant style for I/O, attribute access and dictionary lookups.

??  What is duck typing, and what is the risk?
=> Code uses an object's behaviour (methods and attributes) rather than its declared type, so any object that provides the needed behaviour works. The risk is that a missing method is found only when the code runs; tests, type hints with a type checker, and Protocols reduce that risk.
??  ABC or Protocol: how do you choose?
=> An ABC is **nominal**: classes must inherit from it and can inherit shared code and enforced abstract methods. A Protocol is **structural**: any class with the right methods conforms, without inheriting, and it is checked by static type checkers (and by `isinstance` only with `@runtime_checkable`). Prefer Protocols for parameters that accept "anything like this", ABCs for plug-in hierarchies you own.
??  What is the difference between EAFP and LBYL?
=> LBYL checks conditions first (`if key in d`), EAFP just does the operation and handles the exception. EAFP is idiomatic Python: it avoids time-of-check-to-time-of-use races and duplicated checks, but use LBYL when failure is common and the check is cheaper than the exception.

## Dataclasses, NamedTuple and Enums

Most classes in real code are **data holders**. Writing `__init__`, `__repr__` and `__eq__` by hand for each is noise, so the standard library generates them.

```python Dataclasses.py
from dataclasses import dataclass, field, replace

@dataclass(order=True)
class Item:
    price: float
    name: str = field(compare=False)
    tags: list = field(default_factory=list, compare=False)

@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    amount: int
    currency: str = "INR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("negative amount")

a, b = Item(9.5, "pen"), Item(3.0, "clip", ["small"])
print(a, sorted([a, b])[0].name)

m = Money(amount=500)
print(m, replace(m, amount=750), m == Money(amount=500), hash(m) == hash(Money(amount=500)))
try:
    m.amount = 1
except Exception as error:
    print(type(error).__name__, "-", error)
```

```output
```

| Option | Effect |
| --- | --- |
| `frozen=True` | Immutable instances; also generates `__hash__` |
| `order=True` | Generates `<`, `<=`, `>`, `>=` comparing fields in declaration order |
| `slots=True` (3.10+) | Uses `__slots__`: lower memory, no stray attributes |
| `kw_only=True` (3.10+) | All fields keyword-only: safer constructors |
| `field(default_factory=list)` | A fresh mutable default per instance |
| `__post_init__` | Validation or derived fields after `__init__` |

```python DataclassTrap.py !fail
from dataclasses import dataclass

@dataclass
class Basket:
    items: list = []        # the same mistake as a mutable default argument
```

```output
```

Dataclasses refuse mutable defaults at class-definition time, which turns a classic bug into an immediate error. Pydantic models (the FastAPI stage) look similar but also **validate and convert** data at run time; dataclasses do not.

### NamedTuple and Enum

```python Enums.py
from enum import Enum, IntEnum, StrEnum, Flag, auto
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

class Status(Enum):
    PENDING = auto()
    PAID = auto()
    SHIPPED = auto()

class Level(IntEnum):
    LOW = 1
    HIGH = 3

class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"

class Perm(Flag):
    READ = auto()
    WRITE = auto()

p = Point(1, 2)
x, y = p
print(p, p.x, x + y, p._asdict())
print(Status.PAID, Status.PAID.name, Status.PAID.value, Status(2), list(Status))
print(Level.HIGH > Level.LOW, Role.ADMIN == "admin", f"role={Role.USER}")
print(Perm.READ | Perm.WRITE, Perm.WRITE in (Perm.READ | Perm.WRITE))
print(Status["SHIPPED"] is Status.SHIPPED)
```

```output
```

Use an `Enum` for a closed set of named choices (statuses, roles, modes) instead of magic strings; `StrEnum` (3.11+) members *are* strings, which makes them convenient in JSON and databases. A `NamedTuple` is an immutable, lightweight record that also unpacks like a tuple.

!cheat Which data holder? ::
| Need | Use |
| --- | --- |
| Quick immutable record, unpacks like a tuple | `NamedTuple` |
| Mutable record with methods and defaults | `@dataclass` |
| Immutable, hashable value object | `@dataclass(frozen=True)` |
| Millions of small objects | `@dataclass(slots=True)` or `__slots__` |
| Validate and convert input (API, config) | Pydantic `BaseModel` |
| Closed set of named values | `Enum` / `StrEnum` / `IntEnum` |
| Just a bag of key/value pairs | `dict` (or `TypedDict` for typing) |
!end

??  What does `@dataclass` generate, and what does it not do?
=> It generates `__init__`, `__repr__` and `__eq__` (and optionally ordering, `__hash__`, slots) from the annotated fields. It does not validate or convert types at run time: `Money(amount="x")` is accepted; the annotations are for readers and type checkers.
??  Why does a dataclass forbid `items: list = []`?
=> A mutable default would be one list shared by all instances. The dataclass raises `ValueError` at class creation; use `field(default_factory=list)` so each instance gets its own.
??  When use Enum instead of constants or strings?
=> When a value must be one of a fixed set. Enums are comparable by identity, iterable, give readable `repr`s, carry a `name` and `value`, and let a type checker catch typos that a magic string hides. `StrEnum` and `IntEnum` interoperate with strings and integers.

## Designing Classes Well

### Immutability, `__slots__` and memory

```python Slots.py
import sys

class Plain:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Slotted:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

p, s = Plain(1, 2), Slotted(1, 2)
print(hasattr(p, "__dict__"), hasattr(s, "__dict__"))
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__), sys.getsizeof(s))
try:
    s.z = 3
except AttributeError as error:
    print("AttributeError:", error)
```

```output
```

`__slots__` replaces the per-instance dictionary with fixed storage. It saves memory when you create very many small objects and prevents typos like `s.zz = 3` from silently creating attributes; the price is that you cannot add attributes dynamically and multiple inheritance with slots is restricted.

### Rules of thumb

1. **A class is justified by state plus behaviour that belong together.** A class with only `__init__` and one method is a function wearing a costume; a class with only static methods is a module.
2. **Prefer composition and small collaborating objects** (inject a `Clock`, a `Repository`, a `Notifier`) over deep hierarchies. Constructor injection makes testing easy with fakes.
3. **Keep `__init__` cheap and honest**: assign attributes; do not do I/O. Use a `@classmethod` (`from_env`, `from_json`) for construction that does work.
4. **Make invalid states impossible**: validate in `__post_init__` or setters; use enums instead of strings; use frozen dataclasses for values.
5. **Program to the smallest interface you need**: accept a `Protocol` or an `Iterable`, return a concrete type.
6. **Implement `__repr__` on everything** you will ever debug.

```python Composition.py
from dataclasses import dataclass
from typing import Protocol

class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...

class ConsoleNotifier:
    def send(self, to, message):
        print(f"to {to}: {message}")

class FakeNotifier:
    def __init__(self):
        self.sent = []
    def send(self, to, message):
        self.sent.append((to, message))

@dataclass
class OrderService:
    notifier: Notifier                  # dependency is injected, not constructed inside

    def place(self, user, item):
        self.notifier.send(user, f"order placed: {item}")

OrderService(ConsoleNotifier()).place("asha", "book")

fake = FakeNotifier()
OrderService(fake).place("ravi", "pen")
print(fake.sent)
```

```output
```

This is dependency inversion without a framework: `OrderService` depends on the `Notifier` *shape*, so a test passes a `FakeNotifier` and production passes the real one. FastAPI's `Depends` (web stage) automates exactly this pattern.

!realworld Value objects prevent a whole class of bugs :: A `Money(amount, currency)` frozen dataclass, a `Email` class that validates in `__post_init__`, an `OrderId` `NewType`: each removes "is this a string of paise or rupees?" ambiguity from your function signatures, and the invalid states cannot even be constructed. Code reviews at product companies reward this.

??  When should you use `__slots__`?
=> When you create very many instances of a small class (millions of records, nodes, events) and want to cut memory and speed up attribute access, or when you want to forbid new attributes. Avoid it for ordinary classes: it complicates inheritance, pickling and dynamic features.
??  What is a good design signal that a class should be a function or a module?
=> A class with only `__init__` plus one other method, or with only static methods, has no state worth encapsulating. A function (possibly with `functools.partial` for configuration) or a module is simpler; Python does not require everything to be a class.
??  How do you make a class easy to test?
=> Pass collaborators in through the constructor (dependency injection) instead of creating them inside, depend on small Protocols, avoid hidden global state, and keep side effects (I/O, time, randomness) behind objects you can replace with fakes.
