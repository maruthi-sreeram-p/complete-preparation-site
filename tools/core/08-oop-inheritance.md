@part oop-inheritance | Object-Oriented Programming · Part 2: Inheritance and Polymorphism | oop
## Inheritance

**Inheritance** lets a class (the **subclass**, child or derived class) acquire the fields and methods of another (the **superclass**, parent or base class) and add or change behaviour. It models an **is-a** relationship: a `Dog` *is an* `Animal`.

```java InheritanceDemo.java
public class InheritanceDemo {

    static class Animal {
        protected final String name;                 // visible to subclasses

        Animal(String name) {
            this.name = name;
            System.out.println("Animal constructor: " + name);
        }

        void eat() { System.out.println(name + " eats"); }
        String sound() { return "..."; }
    }

    static class Dog extends Animal {
        private final String breed;

        Dog(String name, String breed) {
            super(name);                             // the parent constructor runs FIRST
            this.breed = breed;
            System.out.println("Dog constructor: " + breed);
        }

        @Override
        String sound() { return "Woof"; }            // overrides Animal.sound

        void fetch() { System.out.println(name + " fetches"); }   // new behaviour
    }

    public static void main(String[] args) {
        Dog d = new Dog("Rex", "Labrador");
        d.eat();                                     // inherited
        d.fetch();                                   // its own
        System.out.println(d.sound());               // overridden: Woof
    }
}
```

Output: `Animal constructor: Rex`, `Dog constructor: Labrador`, `Rex eats`, `Rex fetches`, `Woof`.

### Rules to remember

- A subclass **inherits** non-private members. It does **not** inherit constructors, but its constructor must call one (`super(...)`); if you omit the call, the compiler inserts `super()` and fails if the parent has no no-argument constructor.
- **Construction runs top-down:** the parent part of the object is built before the child part.
- **`super.method()`** calls the parent's version from an overriding method.
- Java allows **single inheritance of classes** (one `extends`), but a class can implement many interfaces. Every class ultimately extends `java.lang.Object`.
- **`final`** on a class prevents extending it (`String`); on a method it prevents overriding.
- **Private** members exist in the object but are not accessible by name from the subclass.

### What a subclass can change

| Technique | Meaning |
|---|---|
| **Add** | new fields and methods |
| **Override** | replace an inherited instance method with the same signature (use `@Override` so the compiler checks it) |
| **Hide** | a field or a `static` method with the same name in the subclass hides the parent's; it is *not* overriding and is resolved by the declared type |

### Overriding rules

An overriding method must have the **same name and parameter types**, a **return type** that is the same or a subtype (a **covariant return**), an access level that is **the same or wider** (you cannot reduce `public` to `protected`), and may throw only the **same or narrower checked exceptions**. A `static`, `private` or `final` method cannot be overridden.

!cheat Inheritance one-liners ::
- Constructors are not inherited; `super(...)` must be the first statement of a constructor.
- Overriding: same signature, same-or-subtype return, same-or-wider access, no new broader checked exceptions.
- Fields and static methods are **hidden**, not overridden: the declared type decides which one you get.
- `final` class = no subclasses; `final` method = no overriding.
- Java: single class inheritance + multiple interface inheritance. C++ and Python allow multiple class inheritance.
!end

!keypoints Inheritance models is-a and reuses and extends behaviour ;; The parent constructor always runs first (super(...)) ;; Overriding needs the same signature; access may widen but not narrow ;; Fields and static methods are hidden, not overridden ;; Java has single class inheritance but multiple interface inheritance

?? Why must the first line of a subclass constructor call a parent constructor?
=> The parent's part of the object must be initialised before the child's part, which may depend on it. If you write no call, the compiler inserts `super()`; if the parent has no no-argument constructor you must call one explicitly.

?? What is the difference between overriding and hiding?
=> Overriding replaces an instance method, and the version that runs is chosen at run time from the object's actual class. Hiding applies to fields and static methods: the version used is chosen at compile time from the declared type of the reference.

## Polymorphism

**Polymorphism** ("many forms") means one name can refer to different behaviour. Java has two kinds:

| | Compile-time (static) polymorphism | Run-time (dynamic) polymorphism |
|---|---|---|
| Mechanism | **method overloading** (same name, different parameters) | **method overriding** with a superclass reference |
| Decided | by the compiler, from the **declared types** of the arguments | by the JVM, from the **actual class** of the object |
| Also called | early binding | late binding, **dynamic dispatch** |

### Dynamic dispatch

```java Zoo.java
import java.util.List;

public class Zoo {

    static abstract class Shape {
        abstract double area();
        @Override public String toString() { return getClass().getSimpleName() + " area=" + String.format("%.2f", area()); }
    }

    static class Circle extends Shape {
        private final double r;
        Circle(double r) { this.r = r; }
        @Override double area() { return Math.PI * r * r; }
    }

    static class Rectangle extends Shape {
        private final double w, h;
        Rectangle(double w, double h) { this.w = w; this.h = h; }
        @Override double area() { return w * h; }
    }

    static double totalArea(List<? extends Shape> shapes) {
        double sum = 0;
        for (Shape s : shapes) sum += s.area();      // which area()? decided at run time, per object
        return sum;
    }

    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Circle(1), new Rectangle(2, 3));
        shapes.forEach(System.out::println);          // Circle area=3.14, Rectangle area=6.00
        System.out.printf("%.2f%n", totalArea(shapes));   // 9.14
    }
}
```

`totalArea` knows only `Shape`. You can add a `Triangle` tomorrow and `totalArea` works unchanged: this is the **open/closed principle** (Part 3) made possible by polymorphism.

**How it works.** Each class has a **virtual method table (vtable)**: an array of pointers to its instance methods. An object has a hidden pointer to its class's table. A call `s.area()` loads the object's table and jumps to the entry for `area`, so the method that runs depends on the real class. The cost is one extra indirection per call (and the JIT often removes even that when only one implementation is loaded).

### Upcasting and downcasting

- **Upcasting** (subclass reference → superclass type) is implicit and always safe: `Shape s = new Circle(1);`. Through `s` you can call only what `Shape` declares, but **overridden methods still run the Circle version**.
- **Downcasting** (back to the subclass) needs an explicit cast and is checked at run time: a wrong cast throws `ClassCastException`. Guard with `instanceof`: `if (s instanceof Circle c) { ... c.radius ... }`.

If you find yourself downcasting often, the design is probably missing a method on the superclass type.

### Overloading is decided by the declared type

```java Overloads.java
public class Overloads {

    static void show(Object o)  { System.out.println("Object"); }
    static void show(String s)  { System.out.println("String"); }

    static class Animal { String who() { return "Animal"; } }
    static class Dog extends Animal { @Override String who() { return "Dog"; } }

    static String describe(Animal a) { return "describe(Animal)"; }
    static String describe(Dog d)    { return "describe(Dog)"; }

    public static void main(String[] args) {
        Object o = "hello";
        show(o);                 // Object: the compiler looks at the declared type Object
        show("hello");           // String: the most specific applicable overload
        show((Object) "hello");  // Object

        Animal a = new Dog();
        System.out.println(a.who());          // Dog: overriding is resolved at run time
        System.out.println(describe(a));      // describe(Animal): overloads use the declared type, not the object
    }
}
```

!warning Gotcha: overloading is not polymorphism in the run-time sense :: `describe(a)` calls the `Animal` overload even though the object is a `Dog`, because overload selection uses the **declared (static) type**. Only overriding is resolved by the object's real type. Interview questions on this exact point are very common.

### Fields are not polymorphic

```java FieldHiding.java
public class FieldHiding {

    static class Parent { String name = "parent"; String get() { return name; } }
    static class Child extends Parent { String name = "child"; }

    public static void main(String[] args) {
        Parent p = new Child();
        System.out.println(p.name);       // parent: the field is chosen by the declared type
        System.out.println(p.get());      // parent: get() is inherited and sees Parent.name
        System.out.println(((Child) p).name);   // child
    }
}
```

!keypoints Overloading: compile time, declared types; overriding: run time, actual class (dynamic dispatch) ;; A vtable per class lets a call find the right method through one indirection ;; Upcasting is implicit and safe; downcasting is checked at run time and can throw ClassCastException ;; Overloaded methods are chosen by the static type of the argument ;; Fields and static methods are not polymorphic

?? What does `Animal a = new Dog(); a.who();` call, and what decides it?
=> It calls `Dog.who()` if Dog overrides it. Instance methods are dispatched dynamically using the actual class of the object, not the declared type of the reference.

?? How does the JVM implement run-time polymorphism cheaply?
=> Each class has a virtual method table of its instance methods and each object points to its class. A call indexes the table to find the method to run, which costs one extra indirection, and the JIT compiler can often inline the call when only one implementation exists.

## Abstract classes and interfaces

An **abstract class** cannot be instantiated and may contain **abstract methods** (declared without a body) that subclasses must implement. It can also have fields, constructors and concrete methods. An **interface** describes a **contract**: a set of methods a class promises to provide, without any state.

```java Contracts.java
import java.util.List;

public class Contracts {

    interface Payable {
        long amountInPaise();
        default String receipt() { return "Pay " + amountInPaise() / 100.0; }   // default method: shared behaviour
        static Payable free() { return () -> 0; }                                // static factory in the interface
    }

    // abstract class: shared state plus a skeleton (template method) with a step left to subclasses
    static abstract class Report {
        private final String title;
        Report(String title) { this.title = title; }

        public final String render() {                // the algorithm is fixed...
            return "== " + title + " ==\n" + body();   // ...one step varies
        }
        protected abstract String body();
    }

    static class SalesReport extends Report implements Payable {
        SalesReport() { super("Sales"); }
        @Override protected String body() { return "total: 42"; }
        @Override public long amountInPaise() { return 4_999; }
    }

    public static void main(String[] args) {
        SalesReport r = new SalesReport();            // one class, one superclass, one interface
        System.out.println(r.render());
        System.out.println(r.receipt());              // Pay 49.99
        System.out.println(Payable.free().receipt()); // Pay 0.0
    }
}
```

### Abstract class or interface?

| | Abstract class | Interface |
|---|---|---|
| Instantiable | no | no |
| State (instance fields) | **yes** | no (only constants) |
| Constructors | yes | no |
| Methods | abstract and concrete, any access | abstract; `default`, `static` and `private` allowed |
| A class can extend / implement | **one** | **many** |
| Models | a partial implementation shared by related classes (**is-a**, with shared code) | a **capability or role** that unrelated classes can have (**can-do**: `Comparable`, `Runnable`) |
| Evolution | adding a method breaks nothing if it is concrete | adding a `default` method keeps old implementers working |

**Guideline:** start with an **interface** for the public contract (it leaves the single inheritance slot free and is easy to mock in tests). Add an **abstract class** only when subclasses really share state or a skeleton algorithm. A **functional interface** has exactly one abstract method and can be implemented by a lambda: `Comparator`, `Runnable`, `Function`.

### Multiple inheritance and the diamond problem

If a class inherits the **same method from two parents**, which one wins? C++ allows multiple class inheritance and needs `virtual` inheritance to avoid duplicating the shared base. Python resolves it with the **method resolution order (MRO)**, a linearisation computed by the C3 algorithm. Java avoids state conflicts by allowing only one class parent, but interfaces with `default` methods can still collide, and the compiler **forces you to resolve it**:

```java Diamond.java
public class Diamond {

    interface Swimmer { default String move() { return "swim"; } }
    interface Runner  { default String move() { return "run"; } }

    static class Triathlete implements Swimmer, Runner {
        @Override
        public String move() {
            return Swimmer.super.move() + " then " + Runner.super.move();   // must choose explicitly
        }
    }

    public static void main(String[] args) {
        System.out.println(new Triathlete().move());   // swim then run
    }
}
```

### Sealed hierarchies

A **sealed** class or interface lists exactly which classes may extend it, so the compiler can check a `switch` over it is **exhaustive**:

```java Shapes.java
public class Shapes {

    sealed interface Shape permits Circle, Square {}
    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}

    static double area(Shape s) {
        return switch (s) {                            // no default needed: the compiler knows all cases
            case Circle c -> Math.PI * c.r() * c.r();
            case Square q -> q.side() * q.side();
        };
    }

    public static void main(String[] args) {
        System.out.printf("%.2f %.2f%n", area(new Circle(1)), area(new Square(2)));   // 3.14 4.00
    }
}
```

!interview Interview angle: Since Java 8 interfaces can have default methods. Are abstract classes still needed? :: Yes, when subclasses need shared **state** (instance fields), constructors, or non-public members. Interfaces cannot hold instance state. Use an interface for the contract and an abstract class (implementing it) when you also want to share fields and a skeleton algorithm.

!keypoints An abstract class can have state and constructors but a class extends only one ;; An interface is a contract: no instance state, a class can implement many ;; Default methods add behaviour without breaking implementers; conflicts must be resolved explicitly ;; Template method: the abstract class fixes the algorithm and subclasses fill in steps ;; Sealed types give exhaustive switches ;; C++ uses virtual inheritance and Python uses the MRO for the diamond problem

?? Why does Java not allow multiple inheritance of classes?
=> It avoids the ambiguity and complexity of the diamond problem: two parents with their own fields and methods of the same name. Java gets the benefit of multiple inheritance through interfaces, which carry no instance state, and the compiler makes the programmer resolve any default-method conflict.

?? When would you choose an abstract class over an interface?
=> When the related subclasses share state or a partly implemented algorithm (fields, constructors, concrete methods, protected helpers). An interface suits a capability that unrelated classes can implement.

## Composition over inheritance

Inheritance is the most overused feature in OOP. It creates the **tightest possible coupling** between parent and child: the child depends on how the parent works internally. **Composition** (a class *has a* reference to another and **delegates** to it) is usually more flexible.

### The fragile base class problem

```java FragileBase.java
import java.util.*;

public class FragileBase {

    // Inheritance version: counts added elements by overriding add and addAll.
    static class CountingSet<E> extends HashSet<E> {
        private int added = 0;
        @Override public boolean add(E e) { added++; return super.add(e); }
        @Override public boolean addAll(Collection<? extends E> c) { added += c.size(); return super.addAll(c); }
        int added() { return added; }
    }

    // Composition version: wraps a Set and forwards calls.
    static class CountingWrapper<E> {
        private final Set<E> set = new HashSet<>();
        private int added = 0;
        boolean add(E e) { added++; return set.add(e); }
        boolean addAll(Collection<? extends E> c) { boolean changed = false; for (E e : c) changed |= add(e); return changed; }
        int added() { return added; }
    }

    public static void main(String[] args) {
        CountingSet<String> a = new CountingSet<>();
        a.addAll(List.of("x", "y", "z"));
        System.out.println(a.added());        // 6, not 3: HashSet.addAll calls add() internally, so each element is counted twice

        CountingWrapper<String> b = new CountingWrapper<>();
        b.addAll(List.of("x", "y", "z"));
        System.out.println(b.added());        // 3
    }
}
```

The subclass worked only until you knew that `HashSet.addAll` calls `add`. A later version of the library could change that and silently change your count: the subclass depended on an **implementation detail** of its parent. Composition depends only on the **public contract**.

### When inheritance is right

Use inheritance when it is truly **is-a**, the parent was **designed for extension** (documented, with stable hooks), and substitution is always valid. Otherwise prefer composition plus an interface:

| Question | If yes |
|---|---|
| Is the child really a special kind of the parent, in every context? | inheritance may be fine |
| Do you want to reuse code only? | use composition (delegate) |
| Might the behaviour need to change at run time? | composition (swap the delegate: the **Strategy** pattern, Part 3) |
| Do you extend a class you do not control or that was not designed for it? | avoid inheritance |

### The Liskov substitution principle (LSP)

Anywhere a parent is expected, a child must work **without surprising the caller**. The classic violation: a `Square extends Rectangle`. A rectangle lets you set width and height independently; a square cannot, so code that sets width 4 and height 5 and expects an area of 20 gets 25 from a square. Geometry says a square is a rectangle; **behaviour** says it is not a substitutable one. Part 3 covers LSP with the other SOLID principles.

!cheat Prefer composition when ::
- You only need to reuse some behaviour, not model a true is-a.
- The parent class was not designed for extension (most library classes).
- Behaviour should change at run time (swap the delegate).
- You would inherit methods that make no sense for the child (`Stack extends Vector` exposes `insertElementAt`).
- Rule: *favour composition over inheritance*, and design classes either **for** extension (documented) or **forbid** it (`final`).
!end

!keypoints Inheritance couples a child to the parent's implementation; composition couples to its public contract ;; The fragile base class problem: a subclass breaks when the parent changes internally ;; Use inheritance only for a true is-a that is safe in every context ;; Liskov: a subtype must be usable wherever the parent is expected, without surprises ;; Delegate instead of inherit when you want reuse or run-time flexibility

?? What is the fragile base class problem?
=> A subclass relies on how its parent works internally, for example that `addAll` calls `add`. If the parent's implementation changes, the subclass can break even though the parent's public contract is unchanged. Composition avoids it by depending only on the contract.

?? Why is Square extends Rectangle a classic violation of the Liskov substitution principle?
=> A Rectangle promises that width and height can be set independently. A Square must keep them equal, so code written for Rectangles (set width 4, height 5, expect area 20) gives the wrong answer with a Square. The subtype changes behaviour that callers rely on.
