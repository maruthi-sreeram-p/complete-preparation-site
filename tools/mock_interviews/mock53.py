"""Day 53 - Mock interview 1: Core Java and Spring Boot."""
import pathlib
import runpy

_c = runpy.run_path(str(pathlib.Path(__file__).with_name("common.py")))
q, section, info, WRITTEN_FOR_SITE = _c["q"], _c["section"], _c["info"], _c["WRITTEN_FOR_SITE"]

HOW = info("mock-how", "How to run this mock", WRITTEN_FOR_SITE + """

**Format (about 90 minutes of questions, plus the 2 timed DSA problems from the plan)**

1. Ask a friend to read the questions, or record yourself. Answer each one aloud in **60 to 90 seconds**.
2. Only then press **Show answer**. Mark the question: *solid*, *half right* or *missed*.
3. Write every *half right* and *missed* question on your weak-answers list. That list is the "done when" of this day.

**What interviewers are really checking**

- Do you know *why* a thing works, not only its name? Always add one reason and one trade-off.
- Do you notice traps? The *Tricky* section is where interviews are won or lost.
- Can you say "I have not used that, but I would expect..." without bluffing?

Questions are tagged **Basic**, **Medium** or **Tricky**. A fresher is expected to be solid on Basic and Medium, and to spot most Tricky ones.""")

JAVA = section("mock-core-java", "Round 1: Core Java, what the interviewer will ask", "Typical opening round. Expect follow-ups on every answer.", [
    q("Basic", "What is the difference between `==` and `equals()`, and what is the contract between `equals()` and `hashCode()`?", """
`==` compares primitives by value and references by **identity** (same object). `equals()` compares **logical content** when a class overrides it; the default `Object.equals` is identity.

The contract: if two objects are `equals`, they **must** have the same `hashCode`. The reverse is not required (two different objects may share a hash code). `equals` must be reflexive, symmetric, transitive, consistent, and false for `null`.

If you break it, `HashMap` and `HashSet` cannot find objects you put in them. Override both together, base them on the same fields, prefer immutable fields, and use `Objects.equals` / `Objects.hash` or a `record`."""),
    q("Medium", "How does a `HashMap` work internally?", """
An array of buckets. For a key: `hash = h ^ (h >>> 16)` (mixes the high bits in), then `index = (n - 1) & hash`. Keys that land in the same bucket form a linked list; when a bucket reaches **8** entries and the table has at least **64** buckets it becomes a red-black tree (otherwise the table is resized instead).

When `size > capacity x 0.75` (the load factor) the array **doubles** and entries are redistributed. `get` and `put` are O(1) on average, O(log n) worst case once a bucket is a tree. It allows one `null` key and is **not thread-safe**.""",
      hint="Array, hash, index, collisions, resize."),
    q("Medium", "`HashMap` vs `ConcurrentHashMap` vs `Hashtable` vs `Collections.synchronizedMap`. Which would you use in a multi-threaded service?", """
- `HashMap`: no thread safety; concurrent writes can lose updates or corrupt the structure.
- `Hashtable` and `synchronizedMap`: one lock for the whole map, so every operation queues up.
- `ConcurrentHashMap` (Java 8+): CAS to insert into an empty bucket, otherwise `synchronized` on the **first node of that bucket**. Threads touching different buckets do not block, and reads are mostly lock-free. No `null` keys or values. `size()` is only an estimate while others are writing.

Use `ConcurrentHashMap`, and use its **atomic** methods (`putIfAbsent`, `computeIfAbsent`, `merge`) instead of check-then-put."""),
    q("Basic", "`ArrayList` vs `LinkedList`: when would you use each?", """
`ArrayList` is a resizable array: O(1) `get(i)`, amortised O(1) append, O(n) insert or remove in the middle (elements shift). Its memory is contiguous, so it is **cache friendly**.

`LinkedList` is O(1) to add or remove at a node you already hold, but O(n) to *find* that node, and every element carries two extra pointers.

In practice `ArrayList` wins almost every time. For a queue or stack use `ArrayDeque`, not `LinkedList`."""),
    q("Basic", "Why is `String` immutable? When do you use `StringBuilder`?", """
Immutability makes strings safe to share between threads, safe as `HashMap` keys (the hash code is cached), allows the **string pool**, and prevents a validated value (a path, a class name, a URL) from being changed afterwards.

Building a string in a loop with `+` creates a new object each time, so use `StringBuilder` (fast, not thread-safe). `StringBuffer` is the synchronised version and is rarely needed. A single expression like `a + b + c` is fine: the compiler optimises it."""),
    q("Medium", "Checked vs unchecked exceptions. How do you handle exceptions in a real application?", """
**Checked** (subclasses of `Exception` but not `RuntimeException`) must be declared or caught: for conditions the caller can reasonably recover from. **Unchecked** (`RuntimeException`, `Error`) signal programming errors or broken preconditions.

In practice: let low-level exceptions bubble up, wrap them in a meaningful exception that keeps the original as the *cause*, handle them **once** in one place (in Spring, a `@RestControllerAdvice`), never write an empty `catch`, and never log *and* rethrow (duplicate logs). Use **try-with-resources** for anything `AutoCloseable`: resources close in reverse order and a second exception is kept via `getSuppressed()`."""),
    q("Medium", "Explain garbage collection. What is a memory leak in a language that has GC?", """
The heap is split into a **young** generation (eden and survivor spaces) and an **old** generation. Most objects die young, so frequent minor collections are cheap; survivors are promoted. An object is garbage when it is **unreachable from the GC roots** (thread stacks, static fields...). This is reachability, not reference counting, so cycles are collected. G1 is the default collector; ZGC targets very short pauses.

A "leak" is an object that is still **reachable but no longer needed**: a static collection that only grows, listeners that are never removed, a cache with no eviction, a `ThreadLocal` on a pooled thread, unclosed resources. `System.gc()` is only a request."""),
    q("Medium", "`volatile` vs `synchronized` vs `AtomicInteger`.", """
- `volatile`: a write is visible to later reads by other threads, and it prevents reordering around it. It does **not** make `x++` atomic.
- `synchronized` / `ReentrantLock`: mutual exclusion plus visibility, for a block that protects several variables that must change together.
- `Atomic*`: lock-free atomic read-modify-write using CAS (`incrementAndGet`). `LongAdder` is faster under heavy contention.

Rule of thumb: a flag read by many threads is `volatile`; a counter is `AtomicLong`/`LongAdder`; an invariant over several fields needs a lock."""),
    q("Medium", "Why use a thread pool? How does `ThreadPoolExecutor` decide what to do with a new task?", """
Creating threads is expensive and unbounded threads exhaust memory, so a pool **reuses** threads and **bounds** concurrency.

For each new task: if fewer than `corePoolSize` threads are running, start one; otherwise put the task in the **queue**; if the queue is full and fewer than `maximumPoolSize` threads exist, start another; otherwise apply the **rejection policy**. Size CPU-bound pools near the core count; I/O-bound pools can be larger. Name your threads, and shut the pool down.

On Java 21, for blocking I/O you can use **virtual threads** (`Executors.newVirtualThreadPerTaskExecutor()`): create one per task and do not pool them."""),
    q("Medium", "How do Java Streams work? What can go wrong with them?", """
A stream is a pipeline: a source, lazy **intermediate** operations (`filter`, `map`, `flatMap`, `sorted`), and one **terminal** operation (`collect`, `forEach`, `reduce`) that triggers the work. `map` turns one element into one; `flatMap` turns one element into a stream and flattens the results.

Pitfalls: a stream cannot be reused (`IllegalStateException`); lambdas should not mutate shared state; `parallel()` uses the common fork-join pool, so it is rarely a win for small data or blocking calls; `Collectors.toMap` throws on duplicate keys unless you pass a merge function."""),
    q("Basic", "Interface vs abstract class. What are default methods for?", """
An **interface** is a contract; a class can implement many. Since Java 8 it can have `default` and `static` methods, but no instance state. An **abstract class** can hold state and constructors, but a class extends only one.

`default` methods let you add a method to a published interface without breaking existing implementations. If two interfaces give the same default, the class must override it and may choose one with `A.super.method()`. Use an interface for a capability, an abstract class for a shared base with state."""),
    q("Basic", "Which Java features since version 8 have you actually used?", """
Be honest and specific. A good fresher answer: lambdas and streams, `Optional`, the `java.time` API (Java 8); `var` (10); text blocks and switch expressions (14-15); **records** (16) for immutable data carriers; **sealed** classes and pattern matching for `instanceof` / `switch` (17-21); **virtual threads** (21).

Add one example: "I used a record for the request DTO, so I got constructor, accessors, `equals`, `hashCode` and `toString` for free." Records cannot extend a class, and their fields are final.""", hint="Name two or three you really used, with an example."),
])

SPRING = section("mock-spring-boot", "Round 2: Spring Boot, what the interviewer will ask", "Most questions start from 'what does this annotation do?' and move to 'what happens underneath?'.", [
    q("Basic", "What does `@SpringBootApplication` do? How does auto-configuration work?", """
It combines `@Configuration`, `@ComponentScan` (scans the package of the class and below) and `@EnableAutoConfiguration`.

Auto-configuration classes are listed in a file inside the starter jars (`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`). Each is guarded by **conditions** such as `@ConditionalOnClass` (a library is on the classpath), `@ConditionalOnProperty` and `@ConditionalOnMissingBean`. That last one is why **your own bean wins**: define a `DataSource` and the default one backs off.

To see what applied and why, run with `--debug` or look at the `conditions` actuator endpoint."""),
    q("Basic", "What is dependency injection? Why constructor injection over field injection?", """
Objects do not create their collaborators; the container creates them and hands them in. That decouples classes and makes them replaceable in tests.

Constructor injection: dependencies are **required and visible**, fields can be `final` (immutability), the class works without Spring in a plain unit test (`new OrderService(fakeRepo)`), and circular dependencies fail fast at startup. Field `@Autowired` hides dependencies, needs reflection in tests, and allows half-built objects. With one constructor you do not even need `@Autowired`."""),
    q("Medium", "How does `@Transactional` work?", """
Spring wraps the bean in a **proxy**. When another bean calls the method, the proxy starts a transaction (or joins the existing one), calls your code, then commits, or rolls back if an **unchecked** exception (`RuntimeException` or `Error`) escapes.

Key settings: `propagation` (`REQUIRED` joins the current transaction, `REQUIRES_NEW` suspends it and starts a new one), `readOnly` (a hint that can skip dirty checking), `rollbackFor` (to also roll back on checked exceptions), and `isolation`. Put it on the **service** layer, around one business operation, and keep transactions short."""),
    q("Medium", "Design the REST API for a 'notes' resource. Which methods and status codes?", """
```
POST   /api/notes        201 Created + Location header
GET    /api/notes?page=0 200 (paged)
GET    /api/notes/{id}   200, or 404
PUT    /api/notes/{id}   200 (replace the whole note)
PATCH  /api/notes/{id}   200 (change some fields)
DELETE /api/notes/{id}   204 No Content
```
`GET`, `PUT` and `DELETE` are **idempotent** (repeating gives the same result); `POST` is not, so payments need an idempotency key. Errors: `400` invalid input, `401` not signed in, `403` signed in but not allowed, `404` not found, `409` conflict (duplicate or stale version). Return errors as a `ProblemDetail` (RFC 9457) so every error has the same shape."""),
    q("Medium", "How do you handle validation and errors globally?", """
Put Bean Validation annotations (`@NotBlank`, `@Size`, `@Email`) on the request DTO and add `@Valid` on the controller parameter. A failure raises `MethodArgumentNotValidException`, which you turn into a `400` with a field-to-message map.

One `@RestControllerAdvice` class with `@ExceptionHandler` methods maps domain exceptions (`NotFoundException` to 404, `ConflictException` to 409) and a final catch-all to a generic 500 that **never leaks a stack trace**. Validate at the edge, and still enforce rules in the service and with database constraints."""),
    q("Medium", "What is the N+1 problem in JPA? How do you find it and fix it?", """
You load N parents with one query, then touching a lazy child collection on each parent fires **one extra query per parent**: 1 + N queries.

Find it: turn on SQL logging or Hibernate statistics, or assert query counts in a test. Fix it: `join fetch` in the query, `@EntityGraph`, batch fetching (`@BatchSize` or `hibernate.default_batch_fetch_size`), or select a **DTO projection** with only the columns you need. Changing the association to `EAGER` is **not** a fix; it usually makes things worse."""),
    q("Medium", "What causes `LazyInitializationException`? What is Open Session In View?", """
You touched a lazy association after the persistence session was closed (usually after the service method returned). Fix by loading what you need inside the transaction: `join fetch`, an entity graph, or map to a DTO inside the service.

Spring Boot enables **Open Session In View** by default (`spring.jpa.open-in-view=true`): the session stays open while the view is rendered, so the exception disappears, but it can **hide N+1 queries** and holds a database connection longer. Many teams switch it off and return DTOs."""),
    q("Medium", "Walk me through Spring Security with JWT. Where do you store the token?", """
A request passes through the **security filter chain**. A JWT filter reads the token, verifies the signature and expiry, builds an `Authentication` and puts it in the `SecurityContext`; then `authorizeHttpRequests` rules and method security (`@PreAuthorize`) decide access. Sessions are stateless. Passwords are stored with **BCrypt** (or Argon2), never plain or fast-hashed.

Storage: `localStorage` is readable by any injected script (XSS). An **HttpOnly, Secure, SameSite** cookie cannot be read by JavaScript, so it survives XSS better, but cookie-based auth needs a CSRF decision (`SameSite=Strict` plus same-site JSON requests covers most cases). JWTs are hard to revoke, so keep them short-lived and add a refresh mechanism."""),
    q("Medium", "How does configuration work: profiles, properties and secrets?", """
Settings live in `application.properties` / `application.yml`. A **profile** (`dev`, `prod`) adds `application-prod.yml` on top, activated with `spring.profiles.active`. Precedence, roughly highest first: command-line arguments, environment variables, profile files, then the base file.

That order is why the **same jar** runs everywhere: you override only what differs (URLs, passwords) with environment variables. Secrets never go in the repository; read them from environment variables or a secret store, and make the app **refuse to start** if a required secret is missing or still the dev default."""),
    q("Medium", "How do you test a Spring Boot application?", """
Use the narrowest test that proves the thing.
- **Unit test** (plain JUnit + Mockito): business logic, no Spring.
- `@WebMvcTest`: only the web layer with `MockMvc`; collaborators replaced with `@MockitoBean` (called `@MockBean` in older versions).
- `@DataJpaTest`: only JPA and repositories, ideally against the real database type via **Testcontainers**.
- `@SpringBootTest`: the full context and real HTTP, for a few end-to-end flows.

A good pyramid has many unit tests, some slice tests and a handful of full tests. Test failures and edge cases, not only the happy path."""),
])

TRICKY = section("mock-tricky", "Round 3: Tricky questions and traps", "These look easy and have a catch. Say what you *think* happens first, then check.", [
    q("Tricky", "What does this print? `Integer a = 127, b = 127; Integer c = 128, d = 128; System.out.println((a == b) + \" \" + (c == d));`", """
`true false`.

Autoboxing calls `Integer.valueOf`, which **caches** the values -128 to 127. So `a` and `b` are the same object, but `c` and `d` are two different objects, and `==` compares references. Always compare wrapper objects with `equals()`. (Also remember `==` on a `null` wrapper that you unbox throws `NullPointerException`.)"""),
    q("Tricky", "What does each method return? `static int f() { try { return 1; } finally { return 2; } }` and `static int g() { int x = 1; try { return x; } finally { x = 2; } }`", """
`f()` returns **2**: a `return` in `finally` overrides the earlier one (and would also swallow an exception, which is why you never do it).
`g()` returns **1**: the return value is copied *before* `finally` runs, so changing `x` afterwards does not change it.

Follow-up: does `finally` always run? Not if the JVM exits (`System.exit`), crashes, or the thread is killed."""),
    q("Tricky", "You remove an element from an `ArrayList` inside a for-each loop. Sometimes you get `ConcurrentModificationException` and sometimes you do not. Why?", """
The iterator keeps an expected `modCount`; `next()` throws if the list was changed behind its back. But `hasNext()` only checks `cursor != size`. If you remove the **second-to-last** element, the size shrinks to equal the cursor, `hasNext()` returns `false`, and the loop ends silently, skipping the last element.

Correct options: `Iterator.remove()`, `list.removeIf(...)`, or collect the items and remove them afterwards. For concurrent use, `CopyOnWriteArrayList`."""),
    q("Tricky", "You use a mutable object as a `HashMap` key and then change it. What happens?", """
The entry is stored in the bucket for the **old** hash code. After the change, `get(key)` computes a new hash, looks in the wrong bucket and returns `null`. The entry is still in the map, but effectively lost (a memory leak).

Use immutable keys (`String`, `Integer`, `record`, enums). That is another reason `String` is immutable."""),
    q("Tricky", "`private volatile int count;` and many threads run `count++`. Is it safe?", """
No. `count++` is three steps: read, add one, write. Two threads can read the same value, and one increment is lost. `volatile` gives **visibility**, not **atomicity**.

Use `AtomicInteger` / `AtomicLong` (`incrementAndGet`), `LongAdder` for heavy contention, or `synchronized`."""),
    q("Tricky", "What is wrong with `Executors.newFixedThreadPool(8)` and `Executors.newCachedThreadPool()` in production?", """
The fixed pool uses an **unbounded** `LinkedBlockingQueue`: if tasks arrive faster than they finish, the queue grows until you run out of memory, and `maximumPoolSize` is never used. The cached pool can create an **unbounded number of threads**.

Build a `ThreadPoolExecutor` yourself with a **bounded** queue, a sensible maximum and a rejection policy (for example `CallerRunsPolicy` for back-pressure), and give threads names."""),
    q("Tricky", "Is Java pass-by-value or pass-by-reference?", """
Always **pass-by-value**. For objects, the *value* that is copied is the **reference**. So a method can change the object it points to (`list.add(...)` is visible to the caller), but reassigning the parameter (`list = new ArrayList<>()`) only changes the local copy; the caller's variable is untouched."""),
    q("Tricky", "How many objects does `String s = new String(\"a\");` create? Is `s == \"a\"` true?", """
Up to **two**: the literal `"a"` in the string pool (created once when the class is loaded) and a new `String` on the heap. `s == "a"` is **false** (different objects); `s.equals("a")` is true; `s.intern() == "a"` is true because `intern()` returns the pooled instance. In practice you almost never write `new String(...)`."""),
    q("Tricky", "A `@Transactional` method calls another `@Transactional(propagation = REQUIRES_NEW)` method **in the same class**. Does the second one get its own transaction? Another trap: the method throws a checked exception. Is the data rolled back?", """
**No** to the first: the proxy only intercepts calls that come *from another bean*. A call through `this` goes straight to the method, so the annotation is ignored. Fix: move the method to another bean (or inject the bean into itself, which is a workaround). `private` methods cannot be proxied either.

**No** to the second: by default only `RuntimeException` and `Error` roll back. Use `@Transactional(rollbackFor = Exception.class)`. Also, if you catch the exception inside the method, the transaction never sees it and commits."""),
    q("Tricky", "Your repository query uses `join fetch` on a collection **and** a `Pageable`. The log shows a warning and the app gets slow. Why?", """
You cannot paginate in SQL over a joined collection: one parent appears in several rows. Hibernate therefore loads **all** rows and applies `firstResult` / `maxResults` **in memory**, which is slow and can exhaust memory.

Fixes: first query a page of parent **ids**, then fetch those parents with their children (`where p.id in :ids`); or use `@BatchSize` / `default_batch_fetch_size` so children load in a few batched queries; or use a DTO projection."""),
    q("Tricky", "A singleton service has a `@Scope(\"prototype\")` bean injected. Every call seems to use the same instance. Why?", """
The singleton is built **once**, so its dependency is injected **once**; the prototype is only created at that moment. To get a new instance per use, inject an `ObjectProvider<T>` and call `getObject()`, use a `@Lookup` method, or a scoped proxy. Remember also that singleton beans are shared by all threads, so they must not hold mutable per-request state."""),
    q("Tricky", "Two beans implement `PaymentGateway`. The app fails with `NoUniqueBeanDefinitionException`. What are your options?", """
Tell Spring which one: mark one `@Primary`, or select by name with `@Qualifier("stripe")`. If you actually want **all** of them (strategy pattern), inject `List<PaymentGateway>` or `Map<String, PaymentGateway>` and pick at runtime. That is also how you add a new gateway without changing the caller (open for extension, closed for modification)."""),
    q("Tricky", "What is the difference between HTTP 401 and 403? What should you return when a user asks for another user's note?", """
**401 Unauthorized** means *not authenticated*: no or invalid credentials. **403 Forbidden** means *authenticated but not allowed*.

For another user's resource, many APIs return **404**, not 403, so the response does not confirm that the id exists. It is a design decision; say that you chose it and why."""),
])

MOCK_53 = [HOW, JAVA, SPRING, TRICKY]
