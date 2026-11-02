@part oop-foundations | Object-Oriented Programming · Part 1: Classes, Objects and the Four Pillars | oop
## Why object-oriented programming

In **procedural** programming you write functions that operate on data structures that are passed around. As a program grows, any function can modify any data, and a change to a data structure ripples through the whole code base. **Object-oriented programming (OOP)** bundles **data (state) and the operations on it (behaviour)** into units called **objects**, and lets each object protect its own data.

A **class** is a blueprint: it describes the fields and methods. An **object** (instance) is one thing built from that blueprint, with its own field values. `Car` is a class; your red Swift is an object.

| Term | Meaning | Example |
|---|---|---|
| **Class** | blueprint: fields + methods | `class Student { String name; ... }` |
| **Object / instance** | a concrete thing created from a class | `new Student("Asha")` |
| **Field (attribute, member variable)** | data held by an object | `name`, `balance` |
| **Method** | behaviour: a function belonging to the class | `deposit(500)` |
| **Constructor** | special method that initialises a new object | `Student(String name)` |
| **Message passing** | objects interact by calling each other's methods | `account.deposit(500)` |

### The four pillars

1. **Encapsulation:** hide the internal state and expose a controlled interface, so the object can protect its own **invariants** (rules that must always hold, like "balance never negative").
2. **Abstraction:** show *what* an object does, not *how*. You use `list.sort()` without knowing the algorithm; you depend on an interface, not an implementation.
3. **Inheritance:** a class can **reuse and extend** another class (an `is-a` relationship): `SavingsAccount` is an `Account`.
4. **Polymorphism:** one interface, many implementations: the same call (`shape.area()`) behaves according to the actual object. Subtype polymorphism is covered in Part 2.

!cheat The four pillars in one line each ::
- **Encapsulation** = data hiding + a controlled interface (private fields, public methods).
- **Abstraction** = expose the essential, hide the detail (interfaces, abstract classes).
- **Inheritance** = reuse through an is-a hierarchy (extends).
- **Polymorphism** = same message, behaviour chosen by the object's real type (overriding).
!end

!keypoints OOP bundles state and behaviour into objects ;; A class is a blueprint, an object is an instance ;; The four pillars: encapsulation, abstraction, inheritance, polymorphism ;; Encapsulation protects invariants; abstraction hides detail

?? What is the difference between a class and an object?
=> A class is a blueprint that defines fields and methods. An object is a particular instance created from it, with its own copy of the fields' values. Many objects can come from one class.

?? Which pillar lets you call `shape.area()` without knowing whether the shape is a circle or a square?
=> Polymorphism: the call is resolved at run time according to the actual type of the object, while abstraction lets the caller depend only on the `Shape` interface.

## Classes and objects in Java

```java BankAccount.java
public class BankAccount {

    private static int created = 0;          // one copy shared by the whole class
    private final String owner;              // fixed once the object exists
    private long balanceInPaise;             // each object has its own copy

    public BankAccount(String owner) {
        this(owner, 0);                      // constructor chaining: call the other constructor
    }

    public BankAccount(String owner, long openingBalanceInPaise) {
        if (owner == null || owner.isBlank()) throw new IllegalArgumentException("owner is required");
        if (openingBalanceInPaise < 0) throw new IllegalArgumentException("opening balance cannot be negative");
        this.owner = owner;                  // 'this' is the object being constructed
        this.balanceInPaise = openingBalanceInPaise;
        created++;
    }

    public void deposit(long paise) {
        if (paise <= 0) throw new IllegalArgumentException("deposit must be positive");
        balanceInPaise += paise;
    }

    public void withdraw(long paise) {
        if (paise > balanceInPaise) throw new IllegalStateException("insufficient funds");
        balanceInPaise -= paise;
    }

    public long balance() { return balanceInPaise; }
    public String owner() { return owner; }
    public static int accountsCreated() { return created; }

    public static void main(String[] args) {
        BankAccount a = new BankAccount("Asha", 10_000);
        BankAccount b = new BankAccount("Ben");
        a.deposit(2_500);
        System.out.println(a.owner() + " has " + a.balance());   // Asha has 12500
        System.out.println(b.owner() + " has " + b.balance());   // Ben has 0
        System.out.println(BankAccount.accountsCreated());       // 2
    }
}
```

**What to notice.** The fields are `private`, so no code outside can set the balance to a negative value: the **only way in is through methods that enforce the rules** (encapsulation). `owner` is `final`: assigned once in the constructor. `created` is `static`: it belongs to the class, not to any object. Money is stored as `long` paise, not `double` (see floating point in Computer Organisation Part 2).

### Instance versus static

| | Instance member | Static member |
|---|---|---|
| Belongs to | each object | the class itself (one copy) |
| Accessed as | `account.balance()` | `BankAccount.accountsCreated()` |
| Can use `this` | yes | no (there is no object) |
| Typical use | state and behaviour of one object | counters, constants, utility and factory methods |

A static method cannot touch instance fields directly, because it is not called on any object.

### What `new` does

`new BankAccount("Ben")` performs these steps in order:

1. **Allocate** memory on the **heap** for the object, with all fields set to default values (0, false, null).
2. Run the **field initialisers** and instance initialiser blocks in the order they appear in the class.
3. Run the **constructor body** (after the call to `super(...)`, which runs the parent's constructor first).
4. Return a **reference** to the new object.

If you write no constructor, Java supplies a **default constructor** with no arguments. As soon as you write any constructor, the default one disappears.

### References, the heap and the stack

A variable of class type holds a **reference** (a pointer-like handle), not the object. The object lives on the **heap**; local variables and the references themselves live in the method's **stack frame**.

```java
BankAccount x = new BankAccount("Asha", 100);
BankAccount y = x;          // y refers to the SAME object: one object, two references
y.deposit(50);
System.out.println(x.balance());   // 150
x = null;                   // x no longer refers to it; y still does
```

An object becomes eligible for **garbage collection** when no reachable reference points to it. You do not free memory yourself in Java or Python; in **C++** you do (with destructors and smart pointers), which Part 4 compares.

!interview Interview angle: Is Java pass-by-value or pass-by-reference? :: Always pass-by-value. For objects the value that is copied is the **reference**. The callee can therefore change the object's state through its copy of the reference, and the caller sees that change, but reassigning the parameter (`p = new Foo()`) changes only the local copy, not the caller's variable.

!keypoints Fields hold state; each object has its own copy of instance fields; static fields belong to the class ;; `new` allocates on the heap, runs initialisers, then the constructor, and returns a reference ;; Constructors can be overloaded and chained with `this(...)`; the default constructor vanishes once you write one ;; Variables hold references; assigning a reference copies the handle, not the object ;; Garbage collection frees objects that are no longer reachable

?? What does a static method not have access to?
=> The `this` reference and the instance fields, because it is called on the class and not on a particular object. It can use only static members and the arguments it receives.

?? Why does `y.deposit(50)` change `x.balance()` after `y = x`?
=> `x` and `y` are two references to the same object on the heap. A method called through either reference changes that one object.

## Encapsulation and abstraction

**Encapsulation** means a class controls access to its state. The tools are **access modifiers**:

| Modifier | Same class | Same package | Subclass (other package) | Everywhere |
|---|---|---|---|---|
| `private` | yes | no | no | no |
| (package-private, no keyword) | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

**Rule of thumb:** make everything as private as possible, and widen access only when there is a reason. Whatever is public becomes a **promise** you must keep.

### Getters and setters: use judgement

Generating a getter and setter for every field is not encapsulation, it is a public field with extra typing. Real encapsulation asks: *what operations make sense?* A `BankAccount` has `deposit` and `withdraw`, not `setBalance`. Expose **behaviour** that keeps the object valid, and expose **read-only** views where needed. Return **copies or unmodifiable views** of internal collections, or callers can modify your state through the back door:

```java Library.java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Library {

    private final List<String> titles = new ArrayList<>();

    public void add(String title) {
        if (title == null || title.isBlank()) throw new IllegalArgumentException("title is required");
        titles.add(title);
    }

    // Leaks the internal list: callers can add, remove or clear it behind our back.
    public List<String> leakyTitles() { return titles; }

    // Safe: a read-only view; attempts to modify it throw UnsupportedOperationException.
    public List<String> titles() { return Collections.unmodifiableList(titles); }

    public static void main(String[] args) {
        Library lib = new Library();
        lib.add("Clean Code");
        lib.leakyTitles().clear();                       // the library's data is destroyed from outside
        System.out.println(lib.titles().size());         // 0
        lib.add("Effective Java");
        try {
            lib.titles().add("Hacked");
        } catch (UnsupportedOperationException e) {
            System.out.println("read-only view");
        }
    }
}
```

### Abstraction

**Abstraction** is deciding what to show and what to hide. You program against an **abstract type** (an interface or abstract class) that lists *what* can be done, while the *how* stays in the implementation. This lets you swap implementations without changing callers: a `List<String>` can be an `ArrayList` today and a `LinkedList` tomorrow.

| | Encapsulation | Abstraction |
|---|---|---|
| Focus | protecting the **data** and enforcing invariants | hiding **complexity** behind a simple interface |
| Achieved by | private fields, controlled methods | interfaces, abstract classes, good naming |
| Question it answers | "who may touch this state?" | "what does the user of this type need to know?" |

!cheat Encapsulation checklist ::
- Fields `private` (and `final` when they never change).
- Validate in constructors and mutators so an invalid object cannot exist.
- Expose operations, not raw state; avoid blind setters.
- Never return a mutable internal collection or array directly: copy it or wrap it.
- Prefer immutable objects (`final` fields, no setters, `record`): they are safe to share between threads.
!end

!keypoints Access modifiers: private < package-private < protected < public ;; Make members as private as possible: public is a promise ;; Encapsulation is about invariants, not about generating getters and setters ;; Do not leak mutable internals: return copies or unmodifiable views ;; Abstraction lets you depend on what a type does, not how it does it

?? Why is a class with a public field and a trivial setter not really encapsulated?
=> Anyone can still put the object into any state, so the class cannot enforce its invariants. Encapsulation means the class controls how its state changes, usually through methods that validate and express meaningful operations.

?? What is the difference between encapsulation and abstraction?
=> Encapsulation protects an object's internal state and enforces rules by restricting access. Abstraction hides complexity by exposing only the essential operations through an interface. One is about control of data, the other about simplifying what the user must understand.

## Identity, equality, copying and immutability

### `==` versus `equals`

For objects, `==` compares **references** (are these the same object?). `equals` compares **meaning** (do these hold the same value?), but only if the class overrides it; the default `Object.equals` is the same as `==`.

```java Money.java
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public final class Money {

    private final long paise;
    private final String currency;

    public Money(long paise, String currency) {
        this.paise = paise;
        this.currency = Objects.requireNonNull(currency);
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) return true;
        if (!(other instanceof Money m)) return false;       // pattern matching for instanceof
        return paise == m.paise && currency.equals(m.currency);
    }

    @Override
    public int hashCode() { return Objects.hash(paise, currency); }

    @Override
    public String toString() { return paise / 100 + "." + String.format("%02d", paise % 100) + " " + currency; }

    public static void main(String[] args) {
        Money a = new Money(1050, "INR");
        Money b = new Money(1050, "INR");
        System.out.println(a == b);                    // false: two different objects
        System.out.println(a.equals(b));               // true: same value
        Set<Money> set = new HashSet<>();
        set.add(a);
        System.out.println(set.contains(b));           // true only because hashCode is overridden too
        System.out.println(a);                         // 10.50 INR
    }
}
```

The **contract**: equal objects must have equal hash codes; `equals` must be reflexive, symmetric, transitive, consistent, and false for `null`. A `HashMap` uses `hashCode` to find the bucket and then `equals` inside it, so overriding one without the other breaks sets and maps. Using a **mutable** field in `hashCode` and then changing it while the object is in a `HashSet` makes the object impossible to find.

### Shallow copy versus deep copy

Copying an object whose fields are references copies the **references**, not the objects they point to:

- **Shallow copy:** the copy shares the nested objects with the original, so changing a nested object through one is visible through the other.
- **Deep copy:** the nested objects are copied too, so the two are independent.

Prefer a **copy constructor** or a factory method to `Object.clone()`, which is awkward and shallow by default.

### Immutable classes

An **immutable** object cannot change after construction (`String`, `Integer`, `LocalDate`, records). To make your own: declare the class `final`, make all fields `private final`, have no setters, and defensively copy any mutable object passed in or returned. Immutable objects are **thread-safe without locks**, can be cached and shared freely, and make good map keys. Java's `record Point(int x, int y) {}` generates the constructor, accessors, `equals`, `hashCode` and `toString` for exactly this kind of value class.

!cheat Identity and equality ::
- `==` on references: same object? `equals`: same value (if overridden).
- Override `equals` and `hashCode` together, using the same fields.
- `hashCode` must be consistent: equal objects → equal hash codes (the reverse need not hold).
- Do not use mutable fields in `hashCode` for objects stored in hash-based collections.
- String literals are interned, `new String("a") == "a"` is false; always compare strings with `equals`.
- Immutable = `final` class, `private final` fields, no setters, defensive copies.
!end

!interview Interview angle: What happens if you override equals but not hashCode? :: Two equal objects may produce different hash codes, so a `HashSet` or `HashMap` looks in the wrong bucket: `contains` returns false for an equal object and duplicates can be stored. The `equals`/`hashCode` contract requires equal objects to have equal hash codes. Generate both together (IDE, `Objects.hash`, or use a `record`).

!keypoints `==` compares references, `equals` compares values when overridden ;; Override equals and hashCode together ;; A shallow copy shares nested objects, a deep copy duplicates them ;; Immutable objects are safe to share and thread-safe ;; Use records for simple value classes

?? Why should a mutable field not be used in hashCode for keys of a HashMap?
=> If the field changes after the object is inserted, its hash code changes, so the map looks in a different bucket and can no longer find the entry, which behaves like a memory leak.

?? What makes a class immutable?
=> The class is final, all fields are private and final, there are no mutators, and any mutable object received in the constructor or returned from a method is defensively copied. Once built, its state never changes.
