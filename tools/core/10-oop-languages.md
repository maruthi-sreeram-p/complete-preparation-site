@part oop-languages | Object-Oriented Programming · Part 4: OOP Across Languages and Interview Practice | oop
## OOP in Java, C++, Python and C#

The ideas are the same everywhere; the **defaults and the machinery** differ. Many interview questions ("why does Java not have multiple inheritance?", "what is a virtual destructor?") are really questions about those differences.

| Feature | Java | C++ | Python | C# |
|---|---|---|---|---|
| Typing | static, compiled to bytecode | static, compiled to machine code | **dynamic**, interpreted | static, compiled to IL |
| Memory management | **garbage collector** | **manual** (RAII, smart pointers) | garbage collector (reference counting + cycle detector) | garbage collector |
| Multiple class inheritance | **no** (interfaces only) | **yes** (virtual inheritance for the diamond) | **yes** (MRO) | no (interfaces only) |
| Method overriding by default | **every instance method is virtual** | only if declared `virtual` | every method can be replaced | only with `virtual` / `override` |
| Constructors / destructors | constructors; no destructor (use try-with-resources) | constructors **and destructors** | `__init__`; `__del__` rarely used | constructors; finalisers; `IDisposable` |
| Access control | `private`, package, `protected`, `public` | `private`, `protected`, `public` | **by convention** (`_x`, `__x` name mangling) | like Java, plus `internal` |
| Interfaces | `interface` | abstract class with pure virtual functions | abstract base classes, protocols (duck typing) | `interface` |
| Generics | **type erasure** | **templates** (instantiated per type) | not needed (dynamic) | reified generics |
| Operator overloading | no (except `+` on String) | **yes** | **yes** (dunder methods) | yes |
| Everything is an object | no (primitives exist) | no | **yes** (even ints and functions) | no |
| Parameter passing | by value (references are values) | by value, by reference (`&`), by pointer | object references (like Java) | by value, `ref`, `out` |

!cheat One-line differences that get asked ::
- Java: single class inheritance + interfaces, GC, all instance methods virtual.
- C++: multiple inheritance, manual memory, `virtual` is opt-in, destructors, templates.
- Python: duck typing, dunder methods, no real `private`, multiple inheritance with the MRO.
- C#: Java-like, plus properties, delegates and events, `struct` value types.
- Java generics are erased at run time; C++ templates generate code per type.
!end

!keypoints Java: GC, single inheritance, virtual by default ;; C++: manual memory, destructors, multiple inheritance, virtual is opt-in ;; Python: dynamic typing, duck typing, convention-based privacy, MRO for multiple inheritance ;; Generics: Java erases them, C++ instantiates templates

?? Why is every instance method virtual in Java but not in C++?
=> Java chose safety and simplicity: overriding always works, and the JIT removes the cost when only one implementation exists. C++ follows the principle of not paying for what you do not use, so a method is dispatched dynamically only if it is declared `virtual`.

?? How does Python get polymorphism without declaring interfaces?
=> Through duck typing: if an object has the method the caller uses, it works ("if it walks like a duck..."). The type is checked only when the call is made at run time, so unrelated classes with the same method name are interchangeable.

## C++ and Python specifics

!note About the C++ snippets :: The C++ code in this chapter is standard C++17 written to be short and was checked by reading, not compiled here. Compile it yourself with `g++ -std=c++17 file.cpp` to see the output. The Python and Java snippets were run.

### C++: the object lifetime is yours

In C++ objects can live on the **stack** (destroyed automatically at the end of the scope) or the **heap** (`new`, destroyed with `delete`). Because there is no garbage collector, a class releases its resources in its **destructor**, and the idiom **RAII** (resource acquisition is initialisation) ties a resource (memory, file, lock) to an object's lifetime: the resource is acquired in the constructor and released in the destructor, even when an exception is thrown. Modern C++ uses `std::unique_ptr` and `std::shared_ptr` instead of raw `new` and `delete`.

```cpp
#include <iostream>
#include <memory>

struct Base {
    virtual ~Base() { std::cout << "~Base\n"; }       // virtual destructor
    virtual void hello() { std::cout << "Base\n"; }
};

struct Derived : Base {
    ~Derived() override { std::cout << "~Derived\n"; }
    void hello() override { std::cout << "Derived\n"; }
};

int main() {
    std::unique_ptr<Base> p = std::make_unique<Derived>();  // freed automatically
    p->hello();                                              // prints Derived (virtual dispatch)
}   // prints ~Derived then ~Base
```

Without `virtual` on `~Base`, deleting a `Derived` through a `Base*` is **undefined behaviour**: the `Derived` destructor would not run. A class meant to be a base class needs a virtual destructor.

**Object slicing.** Copying a `Derived` object into a variable of type `Base` (by value) copies only the `Base` part and loses the derived data and behaviour. Pass polymorphic objects by pointer or reference.

**Rule of three/five.** If a class manages a resource and needs a custom destructor, copy constructor or copy assignment, it probably needs all three (and move operations, the rule of five). Otherwise two copies would both free the same resource: a double free. The **rule of zero** says to use members that manage themselves (`std::string`, `std::vector`, smart pointers) so you write none of them.

| C++ term | Meaning | Java counterpart |
|---|---|---|
| `virtual` function | dispatched at run time | every instance method |
| pure virtual (`= 0`) | abstract method | `abstract` method |
| class with only pure virtuals | interface | `interface` |
| copy constructor | how a copy is made | `clone()` or a copy constructor |
| reference `T&` | alias, cannot be null or reseated | none |
| `const` member function | does not modify the object | `final` fields / immutable class |

### Python: everything is dynamic

```python
class Account:
    interest = 0.04                    # class attribute: shared by all instances

    def __init__(self, owner, balance=0):
        self.owner = owner             # instance attributes are created on assignment
        self._balance = balance        # single underscore: "internal", a convention only

    @property
    def balance(self):                 # read-only property: the Python way to encapsulate
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def __repr__(self):                # dunder (special) method: how the object prints
        return f"Account({self.owner!r}, {self._balance})"

    def __eq__(self, other):           # operator overloading: ==
        return isinstance(other, Account) and (self.owner, self._balance) == (other.owner, other._balance)

a = Account("Asha", 100)
a.deposit(50)
print(a, a.balance, a == Account("Asha", 150))
print(Account.interest, a.interest)
```

That prints `Account('Asha', 150) 150 True` and then `0.04 0.04`.

**Key Python points:**

- **Duck typing and the MRO.** There is no `implements`. For multiple inheritance Python linearises the parents with the **C3 algorithm**; `ClassName.__mro__` shows the order and `super()` follows it, which solves the diamond problem predictably.
- **No true private members.** `_x` is a hint, `__x` triggers **name mangling** (renamed to `_Class__x`), but nothing is enforced: "we are all consenting adults".
- **Dunder methods** (`__init__`, `__str__`, `__repr__`, `__eq__`, `__len__`, `__iter__`, `__enter__`/`__exit__`) let your objects work with built-in syntax.
- **Mutable default arguments** are shared between calls:

```python
def add(item, bucket=[]):          # the list is created ONCE, when the function is defined
    bucket.append(item)
    return bucket

print(add(1), add(2))              # [1, 2] [1, 2]  not [1] [2]
```

!interview Interview angle: Python has no private keyword. How do you encapsulate? :: By convention and by tools: prefix internal names with an underscore, expose controlled access with `@property`, and validate in setters or methods. Double underscores trigger name mangling to avoid accidental clashes in subclasses, not real privacy. Python relies on programmer discipline and documentation instead of enforcement.

!keypoints C++: stack or heap objects, destructors, RAII, virtual destructors for base classes ;; Slicing copies only the base part: pass polymorphic objects by pointer or reference ;; Rule of three/five/zero: manage resources with smart pointers and standard containers ;; Python: duck typing, @property, dunder methods, convention-based privacy ;; Beware Python's shared mutable default arguments

?? Why must a base class intended for polymorphic use have a virtual destructor in C++?
=> Deleting a derived object through a base-class pointer calls only the base destructor if it is not virtual (undefined behaviour), so derived resources are never released. A virtual destructor makes the call dispatch to the derived destructor first.

?? What does `__mro__` give you in Python?
=> The method resolution order: the linear sequence of classes searched when looking up a method or attribute, computed with the C3 algorithm. `super()` follows it, which makes multiple inheritance and the diamond problem predictable.

## Low-level design: a parking lot

**Low-level design (LLD)** interviews ask you to turn a short problem statement into classes. A reliable method:

1. **Clarify requirements** (vehicle types, floors, payment, how tickets work). Write down what is in and out of scope.
2. **Find the nouns** (candidate classes: Vehicle, ParkingSpot, ParkingLot, Ticket) and the **verbs** (candidate methods: park, unpark, calculateFee).
3. **Decide relationships:** is-a (inheritance), has-a (composition), uses (dependency).
4. **Apply principles and patterns where they pay off:** Strategy for pricing, Factory for vehicles, no pattern if none is needed.
5. **Walk through scenarios** (a car enters, the lot is full, a vehicle leaves) and handle the edge cases.

```java ParkingLot.java
import java.util.*;

public class ParkingLot {

    enum Size { SMALL, MEDIUM, LARGE }

    enum VehicleType {
        BIKE(Size.SMALL), CAR(Size.MEDIUM), TRUCK(Size.LARGE);
        final Size needs;
        VehicleType(Size needs) { this.needs = needs; }
    }

    record Vehicle(String plate, VehicleType type) { }
    record Ticket(int id, String plate, int spotNumber, long enteredAtMinute) { }

    static class Spot {
        final int number; final Size size; private Vehicle parked;
        Spot(int number, Size size) { this.number = number; this.size = size; }
        boolean fits(Vehicle v) { return parked == null && size.compareTo(v.type().needs) >= 0; }   // a bigger spot may hold a smaller vehicle
        void park(Vehicle v) { parked = v; }
        void free() { parked = null; }
    }

    interface PricingStrategy { long fee(Vehicle v, long minutes); }          // Strategy pattern: the rule can change

    static class HourlyPricing implements PricingStrategy {
        public long fee(Vehicle v, long minutes) {
            long hours = Math.max(1, (minutes + 59) / 60);                    // round up to whole hours
            long rate = switch (v.type()) { case BIKE -> 10; case CAR -> 30; case TRUCK -> 60; };
            return hours * rate;
        }
    }

    private final List<Spot> spots = new ArrayList<>();
    private final Map<Integer, Ticket> active = new HashMap<>();
    private final Map<Integer, Vehicle> vehicles = new HashMap<>();
    private final PricingStrategy pricing;
    private int nextTicket = 1;

    ParkingLot(List<Size> layout, PricingStrategy pricing) {
        for (int i = 0; i < layout.size(); i++) spots.add(new Spot(i + 1, layout.get(i)));
        this.pricing = pricing;
    }

    Optional<Ticket> park(Vehicle v, long nowMinute) {
        Optional<Spot> spot = spots.stream().filter(s -> s.fits(v)).min(Comparator.comparing((Spot s) -> s.size));   // smallest spot that fits
        if (spot.isEmpty()) return Optional.empty();                         // the lot is full for this vehicle
        spot.get().park(v);
        Ticket t = new Ticket(nextTicket++, v.plate(), spot.get().number, nowMinute);
        active.put(t.id(), t);
        vehicles.put(t.id(), v);
        return Optional.of(t);
    }

    long unpark(int ticketId, long nowMinute) {
        Ticket t = active.remove(ticketId);
        if (t == null) throw new IllegalArgumentException("unknown ticket " + ticketId);
        spots.get(t.spotNumber() - 1).free();
        return pricing.fee(vehicles.remove(ticketId), nowMinute - t.enteredAtMinute());
    }

    public static void main(String[] args) {
        ParkingLot lot = new ParkingLot(List.of(Size.SMALL, Size.MEDIUM, Size.LARGE), new HourlyPricing());
        Ticket car = lot.park(new Vehicle("KA01AB1234", VehicleType.CAR), 0).orElseThrow();
        System.out.println("car in spot " + car.spotNumber());                              // car in spot 2
        System.out.println(lot.park(new Vehicle("KA02CD5678", VehicleType.TRUCK), 10).isPresent());   // true (spot 3)
        System.out.println(lot.park(new Vehicle("KA03EF9012", VehicleType.TRUCK), 20).isPresent());   // false: full for trucks
        System.out.println("fee " + lot.unpark(car.id(), 130));                             // fee 90  (3 hours x 30)
    }
}
```

**Design notes an interviewer will ask about.** *Why a `Strategy` for pricing?* Rates change without touching the lot (open/closed). *Why records for `Vehicle` and `Ticket`?* They are immutable values. *Where would you add concurrency?* `park` must be made atomic (a lock or a concurrent structure), otherwise two cars can take the same spot. *How would it scale?* Index free spots by size (a queue per size) instead of scanning all spots.

!keypoints LLD method: requirements, nouns and verbs, relationships, principles and patterns, scenarios ;; Use enums and records for fixed sets and value objects ;; Strategy keeps changeable rules (pricing) out of the core class ;; State the concurrency story: make the critical operation atomic ;; Say how the design would change for scale

?? What are the first things you should do in a low-level design interview?
=> Clarify the requirements and scope (actors, features, constraints), then identify the main entities (nouns) and actions (verbs) before drawing classes. Starting to code immediately usually leads to a design that misses requirements.

?? Why is the parking lot's pricing a Strategy instead of an if/else on vehicle type inside the lot class?
=> Pricing is a rule that changes independently of parking logic. Behind a Strategy interface a new pricing scheme is a new class, and the lot never changes: the open/closed principle, plus easy testing of each scheme alone.

## Interview traps and answers

These are the OOP questions asked most often, with the short answer that scores.

| Question | Answer in one breath |
|---|---|
| Overloading vs overriding | Overloading: same name, different parameters, chosen at compile time by declared types. Overriding: same signature in a subclass, chosen at run time by the object's class. |
| Abstract class vs interface | Abstract class: state, constructors, partial implementation, single inheritance. Interface: a contract (plus default methods), no instance state, many per class. |
| Can a constructor be overridden / inherited? | No: constructors are not inherited, so they cannot be overridden; they can be overloaded and chained with `this(...)` and `super(...)`. |
| Can a class have a private constructor? | Yes: for singletons, utility classes and factory-only construction. |
| `this` vs `super` | `this` is the current object; `super` refers to the parent part, used to call its constructor or an overridden method. |
| `final` / `finally` / `finalize` | `final`: constant, no override, no subclass. `finally`: block that always runs after try. `finalize`: deprecated pre-GC hook: do not use it. |
| Can you override a static method? | No: it is hidden. Static methods are bound to the class at compile time. |
| What is the `Object` class? | The root of every class: `equals`, `hashCode`, `toString`, `getClass`, `clone`, `wait`, `notify`. |
| Shallow vs deep copy | Shallow copies references; deep copies the whole object graph. |
| Aggregation vs composition | Both has-a; in composition the part cannot outlive the whole. |
| Is Java 100% object-oriented? | No: it has primitives (`int`, `double`) and static members. Wrapper classes box primitives. |
| Why are Strings immutable? | Security, thread safety, string pool sharing, cached hash code, safe as map keys. |
| What does polymorphism need? | Inheritance or an interface, overriding, and a superclass reference to a subclass object. |

### Output puzzles

Work out what each program prints, then check yourself against the answers below.

```java Puzzles.java
public class Puzzles {

    static class A {
        static { System.out.print("A-static "); }
        { System.out.print("A-init "); }
        A() { System.out.print("A() "); }
    }

    static class B extends A {
        static { System.out.print("B-static "); }
        { System.out.print("B-init "); }
        B() { System.out.print("B() "); }
    }

    static int f() {
        try { return 1; } finally { System.out.print("finally "); }
    }

    static String g(Object o) { return "Object"; }
    static String g(Integer i) { return "Integer"; }
    static String g(long l) { return "long"; }

    public static void main(String[] args) {
        new B();                                   // 1
        System.out.println();
        new B();                                   // 2
        System.out.println();
        System.out.println(f());                   // 3
        System.out.println(g(5));                  // 4
        Integer x = 127, y = 127, p = 128, q = 128;
        System.out.println((x == y) + " " + (p == q) + " " + p.equals(q));   // 5
        System.out.println("a" + 1 + 2 + " " + (1 + 2 + "a"));              // 6
    }
}
```

Answers: **1** `A-static B-static A-init A() B-init B()` (static blocks run once when the class loads, parent first; then for each object: parent instance initialisers and constructor, then the child's). **2** `A-init A() B-init B()` (the static blocks do not run again). **3** `finally ` then `1` (the `finally` block runs before the method returns). **4** `long`: with the argument `5` (an `int`), the compiler prefers **widening** (`int` to `long`) over **boxing** (`Integer`) over the `Object` overload. **5** `true false true`: `Integer` objects between −128 and 127 are cached, so `==` happens to work for 127 but not for 128, which is why you use `equals`. **6** `a12 3a`: strings concatenate left to right, but `1 + 2` evaluated first gives 3.

!interview Interview angle: Explain a polymorphism example from your own project. :: Pick a real one (a `PaymentMethod` interface with card, UPI and wallet implementations, or a `Notifier` with email and SMS). Say what the interface promises, how the caller depends only on the interface, how a new implementation is added without editing the caller (open/closed), and how you tested it by passing a fake. Concrete beats textbook.

!keypoints Know the one-breath answers: overloading versus overriding, abstract class versus interface, shallow versus deep copy ;; Static blocks run once per class load; instance initialisers and constructors run per object ;; Overload resolution prefers widening, then boxing, then varargs ;; Integer caching makes == unreliable above 127: use equals ;; A strong answer ties a concept to something you built

?? What happens if both the `try` block and the `finally` block contain a return statement?
=> The value returned by the `finally` block overrides the one from `try` (and discards any exception), which is why returning from `finally` is considered bad practice. The compiler warns about it.

?? In what order do static blocks, instance initialisers and constructors run for `new B()` where B extends A?
=> When class B is first used: A's static initialisers, then B's static initialisers (once only). For each new object: A's instance initialisers and A's constructor, then B's instance initialisers and B's constructor.
