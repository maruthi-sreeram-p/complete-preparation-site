from common import subject, written

QUESTIONS = [
    written("spring-ioc-di", "Inversion of control and dependency injection", "Easy",
        "What is IoC, what does the Spring container do, and why is constructor injection preferred?",
        "**Inversion of control** means your objects do not create or look up their collaborators; a container creates them and hands them in. The Spring **ApplicationContext** reads configuration (annotations, `@Bean` methods), creates the beans, wires dependencies (**dependency injection**) and manages their lifecycle.\n\n"
        "**Constructor injection** is preferred because dependencies become `final` and cannot be forgotten, the object is never half-built, it works without Spring in a plain unit test (`new Service(mock)`), and a missing dependency or a circular reference fails at startup. Field injection hides the dependencies and makes tests need reflection or the container."),
    written("spring-scopes", "Bean scopes", "Easy",
        "What are the default bean scope and the other common scopes? What is the danger of a singleton holding state?",
        "The default is **singleton**: one shared instance per container. Others: **prototype** (a new instance per injection or lookup), and in web applications **request**, **session** and **application**.\n\n"
        "Singletons are shared by every thread, so a mutable field (a list, a counter, a `SimpleDateFormat`, per-user data) is a concurrency bug. Keep singleton beans stateless or make their state thread-safe. A prototype injected into a singleton is created once at injection time; to get a new one each time, inject an `ObjectProvider` or a lookup method."),
    written("spring-autoconfig", "How does Spring Boot auto-configuration work?", "Medium",
        "Explain what `@SpringBootApplication` includes and how auto-configuration decides what to configure.",
        "`@SpringBootApplication` combines `@SpringBootConfiguration` (a configuration class), `@ComponentScan` (finds your components below the main class's package) and `@EnableAutoConfiguration`.\n\n"
        "Auto-configuration classes listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` are loaded and guarded by **conditions**: `@ConditionalOnClass` (a library is on the classpath), `@ConditionalOnMissingBean` (you have not defined your own), `@ConditionalOnProperty`. So adding `spring-boot-starter-data-jpa` plus a database driver configures a `DataSource` and an `EntityManagerFactory`, and defining your own `DataSource` bean backs the default away. Run with `--debug` to see the conditions report."),
    written("spring-transactional", "@Transactional pitfalls", "Hard",
        "Name three situations where `@Transactional` does not do what you expect.",
        "1. **Self-invocation**: calling a `@Transactional` method from another method of the *same class* bypasses the proxy, so no transaction starts. Move it to another bean.\n"
        "2. **Rollback rules**: by default only unchecked exceptions (`RuntimeException`, `Error`) roll back; a checked exception commits unless you set `rollbackFor`. Catching the exception inside the method also prevents a rollback.\n"
        "3. **Visibility and proxies**: the annotation works on `public` methods of beans called through the Spring proxy; on `private` methods, or on objects you created with `new`, it is ignored.\n\n"
        "Also: a transaction does not cross threads (`@Async`), and long transactions holding a database connection while calling remote services exhaust the connection pool. Keep them short and around the database work only."),
    written("spring-n-plus-1", "The N+1 query problem", "Medium",
        "What is the N+1 problem in JPA, how do you spot it, and how do you fix it?",
        "Loading N parents with one query, then triggering one extra query per parent to load a lazy association (`order.getItems()` inside a loop), gives 1 + N queries. It is invisible in the code and shows up as slow endpoints that get slower with data.\n\n"
        "Spot it by enabling SQL logging (`spring.jpa.show-sql` or a datasource proxy that counts statements) or tests that assert the number of queries. Fix it with a **fetch join** (`JOIN FETCH`), an `@EntityGraph`, batch fetching (`@BatchSize` / `hibernate.default_batch_fetch_size`), or by loading a **DTO projection** with just the needed columns. Making the association `EAGER` is not a fix: it hides the problem and fetches data you often do not need."),
    written("spring-rest-status", "REST status codes and idempotency", "Medium",
        "Which HTTP status codes do you return for create, update, delete, validation errors and missing resources? What does idempotent mean?",
        "Create: **201 Created** with a `Location` header. Read: **200**. Update: **200** with the body or **204 No Content**. Delete: **204**. Invalid input: **400** (or **422** for semantic validation errors) with an error body that names the fields. Not found: **404**. Not logged in: **401**; logged in but not allowed: **403**. Conflict (duplicate, version mismatch): **409**. Server fault: **500**.\n\n"
        "An operation is **idempotent** if repeating it has the same effect as doing it once: `GET`, `PUT`, `DELETE` should be; `POST` normally is not. For a `POST` that must be safe to retry (a payment), accept an **idempotency key** from the client and store the result per key."),
    written("spring-controller-advice", "Central error handling", "Easy",
        "How do you return consistent JSON errors from all controllers?",
        "Write a class annotated `@RestControllerAdvice` with `@ExceptionHandler` methods that map exceptions to a status and an error body (for example `ProblemDetail`, the RFC 9457 format supported by Spring 6). Handle `MethodArgumentNotValidException` for validation (collect field errors), your own `NotFoundException` (404), and a catch-all for unexpected exceptions (500) that logs the stack trace but returns a generic message with a correlation id, never internal details."),
    written("spring-security-jwt", "Session or JWT?", "Medium",
        "Compare server-side sessions with JWT access tokens. How does a request pass through Spring Security?",
        "A **session** stores user state on the server and the browser holds only a session id cookie: easy to revoke, but the server must store (or replicate) sessions. A **JWT** is a signed token carrying the user's identity and claims; services verify the signature without a lookup, which suits stateless APIs and microservices, but a token cannot be revoked before it expires, so keep access tokens short-lived and use refresh tokens, and never put secrets in the payload (it is only signed, not encrypted).\n\n"
        "In Spring Security a request passes through a **filter chain** (`SecurityFilterChain`). An authentication filter (for JWT, a `BearerTokenAuthenticationFilter` or your own) builds an `Authentication` and stores it in the `SecurityContext`; later, authorisation rules (`authorizeHttpRequests`, `@PreAuthorize`) decide access. CSRF protection matters for cookie-based sessions; it is usually disabled for token-based stateless APIs."),
    written("spring-testing", "Testing slices", "Medium",
        "What is the difference between `@SpringBootTest`, `@WebMvcTest` and `@DataJpaTest`? When do you mock and when do you use Testcontainers?",
        "`@SpringBootTest` starts the whole application context: slow, but tests everything together. `@WebMvcTest` loads only the web layer (controllers, filters, converters) and expects collaborators to be mocked (`@MockitoBean`); `@DataJpaTest` loads only JPA repositories on an embedded or containerised database and rolls back after each test. Slices start faster and fail for narrower reasons.\n\n"
        "Mock collaborators in **unit** tests of business logic. Use **Testcontainers** for integration tests that need the real database or broker, because H2 differs from PostgreSQL in dialect, locking and types, so tests can pass on H2 and fail in production."),
    written("spring-circular", "Circular dependencies and bean lifecycle", "Hard",
        "What is a circular dependency, how does Spring treat it, and what is the order of the bean lifecycle?",
        "Bean A needs B and B needs A. With constructor injection neither can be created first, so Spring fails at startup (`BeanCurrentlyInCreationException`); since Spring Boot 2.6 even setter-based cycles are disallowed by default. The fix is a design change: extract the shared logic into a third bean, use events, or depend on an interface in one direction.\n\n"
        "Lifecycle: instantiate the bean (constructor) → inject dependencies → `*Aware` callbacks → `BeanPostProcessor.postProcessBeforeInitialization` → `@PostConstruct` / `InitializingBean` / init method → `postProcessAfterInitialization` (this is where AOP proxies, such as the one for `@Transactional`, are created) → the bean is ready → on shutdown `@PreDestroy` / `DisposableBean`."),
    written("spring-profiles-config", "Configuration and profiles", "Easy",
        "How do you configure an application differently for development and production?",
        "Put settings in `application.yml` (or `.properties`) and override per environment with **profile-specific files** (`application-prod.yml`, activated with `spring.profiles.active=prod`), **environment variables** (`SPRING_DATASOURCE_URL`), or command-line arguments. Bind related properties to a typed class with `@ConfigurationProperties`, validated with `@Validated`. Beans can be restricted with `@Profile(\"dev\")`. Keep secrets (passwords, API keys) out of the repository: read them from environment variables or a secret manager."),
    written("spring-actuator", "Observability with Actuator", "Easy",
        "What does Spring Boot Actuator give you, and how would you use it in production?",
        "Actuator exposes operational endpoints: `/actuator/health` (liveness and readiness for Kubernetes probes, including database and disk checks), `/actuator/metrics` and `/actuator/prometheus` (Micrometer metrics: JVM, HTTP latency, connection pool, custom counters), `/actuator/info`, and others such as `loggers` for changing log levels at runtime. In production, expose only what is needed over a separate management port or behind authentication, scrape metrics with Prometheus, and add tracing (Micrometer Tracing with OpenTelemetry) and structured logs with a correlation id."),
]

SUBJECT = subject("spring-boot", "Spring Boot", "Java and Spring", 11,
    "Dependency injection, REST, data access, security and testing: the Spring questions that follow Core Java in interviews.",
    QUESTIONS,
    platforms=[
        {"name": "Spring Guides", "url": "https://spring.io/guides", "note": "Official step-by-step guides"},
        {"name": "Baeldung: Spring", "url": "https://www.baeldung.com/spring-tutorial", "note": "Practical Spring tutorials"},
        {"name": "GeeksforGeeks: Spring Boot", "url": "https://www.geeksforgeeks.org/advance-java/spring-boot/", "note": "Tutorials and interview questions"},
    ])
