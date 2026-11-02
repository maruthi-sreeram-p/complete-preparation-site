"""Practice subject: Object-Oriented Programming. The two code answers get their output by running the code."""
import sys
from pathlib import Path

from common import subject, written

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))
from core_helpers import run_java  # noqa: E402

DISPATCH_CODE = """public class Main {
    static class Animal { String sound() { return "..."; } static String kind() { return "animal"; } }
    static class Dog extends Animal { @Override String sound() { return "Woof"; } static String kind() { return "dog"; } }
    static String describe(Animal a) { return "Animal overload"; }
    static String describe(Dog d) { return "Dog overload"; }
    public static void main(String[] args) {
        Animal a = new Dog();
        System.out.println(a.sound());
        System.out.println(a.kind());
        System.out.println(describe(a));
    }
}"""
DISPATCH_OUT = run_java(DISPATCH_CODE).split("\n")
assert DISPATCH_OUT == ["Woof", "animal", "Animal overload"], DISPATCH_OUT

INIT_CODE = """public class Main {
    static class Base {
        Base() { System.out.print("Base "); init(); }
        void init() { System.out.print("base-init "); }
    }
    static class Child extends Base {
        int x = 5;
        Child() { System.out.print("Child "); }
        @Override void init() { System.out.print(x + " "); }
    }
    public static void main(String[] args) { new Child(); }
}"""
INIT_OUT = run_java(INIT_CODE)
assert INIT_OUT.split() == ["Base", "0", "Child"], INIT_OUT

QUESTIONS = [
    written("oop-pillars", "The four pillars", "Easy",
        "Name and explain the four pillars of object-oriented programming with a one-line example of each.",
        "- **Encapsulation:** bundle data with the methods that operate on it and hide the internals behind a controlled interface, so the object protects its own invariants. *`BankAccount` keeps `balance` private and offers `deposit` and `withdraw`.*\n"
        "- **Abstraction:** expose what an object does, hide how. *You call `list.sort()` without knowing the algorithm; you code against `List`, not `ArrayList`.*\n"
        "- **Inheritance:** a class reuses and extends another (is-a). *`SavingsAccount extends Account`.*\n"
        "- **Polymorphism:** the same call behaves according to the object's real type. *`shape.area()` runs `Circle.area()` or `Square.area()`.*\n\n"
        "A strong answer adds *why* each matters: encapsulation limits the damage of changes, abstraction reduces coupling, inheritance and polymorphism enable extension without editing existing code."),
    written("oop-overload-override", "Overloading and overriding", "Easy",
        "What is the difference between method overloading and overriding? Which is resolved at compile time?",
        "**Overloading:** several methods with the **same name but different parameter lists** in one class (or hierarchy); the compiler picks one using the **declared types** of the arguments: **compile-time (static) polymorphism**. **Overriding:** a subclass provides its own implementation of an inherited method with the **same signature**; the JVM picks the version from the **actual class** of the object: **run-time (dynamic) polymorphism**. Overriding rules: same signature, same or covariant return type, same or wider access, no broader checked exceptions; `static`, `private` and `final` methods cannot be overridden.",
        hint="Which one needs inheritance? Which one does the compiler decide?"),
    written("oop-dispatch-output", "What does this print? Dispatch and overload resolution", "Medium",
        f"What does this program print, and why?\n\n```java\n{DISPATCH_CODE}\n```",
        f"It prints:\n\n```\n{chr(10).join(DISPATCH_OUT)}\n```\n\n- `a.sound()` prints **Woof**: instance methods are dispatched dynamically on the actual object (a Dog).\n- `a.kind()` prints **animal**: static methods are hidden, not overridden, and are bound at compile time by the declared type (Animal).\n- `describe(a)` picks the **Animal overload**: overloads are chosen from the declared type of the argument, not the object's real type."),
    written("oop-abstract-interface", "Abstract class or interface?", "Medium",
        "When do you use an abstract class and when an interface? Can an interface have implementation?",
        "An **interface** is a contract (what a type can do) that unrelated classes can implement; a class can implement many. Since Java 8 an interface may have **default** and **static** methods (and private helpers since 9) but **no instance state**. An **abstract class** can have fields, constructors and any mix of abstract and concrete methods, but a class extends only **one**.\n\n"
        "Use an **interface** for the public contract and for capabilities (`Comparable`, `Runnable`); use an **abstract class** when related subclasses share **state or a skeleton algorithm** (template method). A common design is both: an interface for callers and an abstract base class providing shared code."),
    written("oop-composition", "Composition over inheritance", "Medium",
        "Why do experienced developers prefer composition over inheritance? Give a concrete failure of inheritance.",
        "Inheritance couples the subclass to the **implementation** of the parent and is fixed at compile time; composition (a field plus delegation) couples only to the **public contract** and can change at run time (swap the delegate: Strategy). The **fragile base class problem**: a `CountingSet extends HashSet` that overrides `add` and `addAll` to count elements reports **6** after adding three elements with `addAll`, because `HashSet.addAll` calls `add` internally, so each element is counted twice. A later change in the library could change this again. The fix is to wrap a `Set` and forward calls. Use inheritance only for a true **is-a** that stays valid in every context (Liskov) and for classes designed for extension."),
    written("oop-solid", "Explain the SOLID principles", "Medium",
        "Explain the SOLID principles briefly, with one example violation.",
        "- **S**ingle responsibility: one reason to change. *A class that calculates, formats and saves an invoice changes for three reasons.*\n"
        "- **O**pen/closed: extend by adding code, not editing old code. *An if/else chain on a type code; use polymorphism.*\n"
        "- **L**iskov substitution: subtypes must keep the parent's promises. *`Penguin extends Bird` throwing from `fly()`.*\n"
        "- **I**nterface segregation: small role-specific interfaces. *A `Robot` forced to implement `eat()`.*\n"
        "- **D**ependency inversion: depend on abstractions and inject implementations. *`OrderService` creating an `SmtpMailer` itself instead of receiving a `Notifier`.*\n\n"
        "They are guidelines for keeping code easy to change, not laws; applying them blindly creates needless abstraction."),
    written("oop-equals-hashcode", "equals and hashCode", "Medium",
        "What is the contract between equals and hashCode, and what breaks if you violate it?",
        "If `a.equals(b)` is true then `a.hashCode() == b.hashCode()` must hold (the reverse is not required: collisions are allowed). `equals` must also be reflexive, symmetric, transitive, consistent and false for null. Hash-based collections find the bucket with `hashCode` and then compare with `equals`, so if you override `equals` only, two equal objects usually have different identity hash codes: `HashSet.contains` returns false, duplicates are stored, and `HashMap.get` misses. Use the same fields in both, avoid mutable fields in `hashCode` of keys, or use a `record`."),
    written("oop-constructor-init", "Constructors and initialisation order", "Hard",
        f"What does this program print, and what does it teach about calling overridable methods from a constructor?\n\n```java\n{INIT_CODE}\n```",
        f"It prints: **{INIT_OUT}**\n\nThe parent constructor runs **first**, before the child's fields are initialised. `Base()` calls `init()`, which is overridden in `Child` and therefore runs, but `x = 5` has not been executed yet, so it prints the default **0**. Lesson: **never call overridable methods from a constructor**; the subclass method may run on a half-built object. Make the method `final`/`private`, or use a factory or `init` step after construction."),
    written("oop-static-instance", "Static versus instance members", "Easy",
        "What is the difference between static and instance members? Why can't a static method use `this`?",
        "An **instance** field or method belongs to each object (each has its own field values). A **static** member belongs to the **class** and is shared by all objects: one copy, usable without creating an object (`Math.max`, counters, constants, factory methods). A static method has **no `this`** because it is not called on an object, so it cannot access instance fields or call instance methods directly. Static members are initialised when the class is loaded (static blocks run once)."),
    written("oop-immutable", "Immutable classes", "Medium",
        "How do you make a class immutable and why is that useful?",
        "Declare the class `final` (or make constructors private), make all fields `private final`, provide no setters, and **copy** any mutable object received in the constructor or returned from a getter (defensive copies). In modern Java a `record` does most of this for you. Benefits: **thread-safe without locks**, safe to share and cache, usable as `HashMap` keys, easy to reason about (no hidden changes), and invariants hold forever once the constructor succeeded. The costs are more allocation for changes and the need for builder-style `withX` methods."),
    written("oop-patterns", "Which design pattern would you use?", "Medium",
        "Name a pattern for each: (1) one shared instance, (2) many optional constructor parameters, (3) interchangeable algorithms chosen at run time, (4) notify many listeners when something changes, (5) add features to an object by wrapping it.",
        "(1) **Singleton** (best as an enum, or a container-managed bean). (2) **Builder**. (3) **Strategy** (Comparator is the classic example). (4) **Observer** (event listeners, publish-subscribe). (5) **Decorator** (Java I/O: `new BufferedReader(new InputStreamReader(in))`).\n\nOther frequent ones: **Factory method** (`List.of`, `Integer.valueOf`), **Adapter** (convert an interface), **Facade** (simplify a subsystem), **Template method** (a skeleton algorithm with steps for subclasses), **Command** (undo/redo)."),
    written("oop-multiple-inheritance", "Multiple inheritance and the diamond problem", "Hard",
        "Why does Java not allow multiple inheritance of classes? How do C++ and Python handle the diamond problem?",
        "With two parents that both extend a common grandparent, a child would inherit two copies of the grandparent's state (or two competing implementations of a method): **which one wins?** Java avoids the ambiguity by allowing a class to extend only one class but implement many interfaces; interfaces carry no instance state, and if two default methods clash the compiler forces you to override and choose (`A.super.m()`).\n\n"
        "**C++** allows multiple inheritance and uses **virtual inheritance** so that the shared base is stored once. **Python** computes a deterministic **method resolution order (MRO)** with the C3 linearisation (`D.__mro__`), and `super()` follows it, so each class is visited once."),
    written("oop-java-cpp", "Java versus C++", "Medium",
        "List the main differences between Java and C++ from an OOP point of view.",
        "- **Memory:** Java uses a garbage collector; C++ is manual (destructors, RAII, smart pointers).\n"
        "- **Inheritance:** Java single class inheritance + interfaces; C++ multiple inheritance.\n"
        "- **Dispatch:** every Java instance method is virtual; in C++ only functions declared `virtual` are.\n"
        "- **Generics:** Java type erasure; C++ templates instantiated per type.\n"
        "- **Operator overloading:** C++ yes; Java no.\n"
        "- **Pointers:** C++ has raw pointers and references; Java has only references (no pointer arithmetic).\n"
        "- **Compilation:** Java compiles to bytecode run by the JVM (JIT); C++ compiles to native machine code.\n"
        "- **Objects:** C++ objects can live on the stack by value (so **slicing** can happen); Java objects always live on the heap and are accessed by reference."),
    written("oop-lld-library", "Design a library management system", "Hard",
        "Outline how you would design a library management system in an interview (classes, relationships and one pattern).",
        "**1. Clarify:** members, books and copies, borrow and return, fines, reservations; scale; out of scope (payments).\n\n"
        "**2. Nouns → classes:** `Book` (title, ISBN) versus `BookCopy` (barcode, status: AVAILABLE, BORROWED, RESERVED, LOST), `Member`, `Librarian`, `Loan` (copy, member, borrowedOn, dueOn, returnedOn), `Library` (facade with `borrow`, `return`, `search`), `Reservation`, `Fine`.\n\n"
        "**3. Relationships:** a `Book` has many `BookCopy`s (composition); a `Loan` links a `Member` and a `BookCopy` (association); `Member` and `Librarian` extend `User` or, better, roles by composition.\n\n"
        "**4. Rules and patterns:** a **Strategy** for fine calculation (per-day rate may change) and for the loan limit per membership type; **Observer** to notify a member when a reserved book is returned; keep the status transitions inside `BookCopy` (encapsulation).\n\n"
        "**5. Edge cases and concurrency:** two members borrowing the last copy (make `borrow` atomic or use optimistic locking), overdue loans, a member over the limit, returning an unknown copy.\n\n"
        "**6. Scale:** indexes on ISBN and title, a search service, and caching for popular lists."),
]

SUBJECT = subject("core-oop", "Object-Oriented Programming", "Core subjects", 43,
    "The pillars, polymorphism, SOLID, design patterns and the questions interviewers ask about them. The code answers were run, not guessed.",
    QUESTIONS,
    platforms=[
        {"name": "GeeksforGeeks: OOP in Java", "url": "https://www.geeksforgeeks.org/java/object-oriented-programming-oops-concept-in-java/", "note": "Tutorials and interview questions"},
        {"name": "Refactoring Guru: Design Patterns", "url": "https://refactoring.guru/design-patterns", "note": "Patterns explained with diagrams and code"},
    ])
