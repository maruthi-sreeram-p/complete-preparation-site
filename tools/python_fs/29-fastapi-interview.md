@part py-web-6 | FastAPI Basics · Part 6: Interview Preparation and Study Plan | web
## Interview Q&A: FastAPI and Pydantic

??  What is FastAPI and why choose it?
=> A modern Python web framework for building APIs on ASGI (Starlette) with Pydantic for validation. It generates OpenAPI documentation automatically from type hints, supports async and sync endpoints, has built-in dependency injection and is very productive for JSON APIs and microservices. Choose it for API-first services; choose Django when you need an admin, ORM, auth and templates out of the box.
??  How does FastAPI use type hints?
=> It reads function signatures at start-up: path template names become path parameters, simple types become query parameters, Pydantic models become JSON bodies, and annotations drive validation, conversion, error messages and the OpenAPI schema.
??  What happens when validation fails?
=> FastAPI returns `422 Unprocessable Entity` with a `detail` list (location, message, type of each error) and never calls your function. You can customise the format with a `RequestValidationError` handler.
??  What is the difference between a path parameter, a query parameter and a body?
=> A path parameter is part of the URL template (`/items/{id}`) and identifies a resource; query parameters (`?limit=10`) filter or modify; the body (JSON validated by a Pydantic model) carries data to create or change. `Header`, `Cookie`, `Form` and `File` read other sources.
??  Pydantic v2 versus v1: what changed that matters?
=> v2 has a Rust core (much faster), `model_validate`/`model_dump` instead of `parse_obj`/`dict`, `field_validator`/`model_validator` instead of `validator`/`root_validator`, `ConfigDict` instead of the `Config` class, `from_attributes` instead of `orm_mode`, and stricter, more consistent coercion rules.
??  What is `response_model` for?
=> It validates and filters what the endpoint returns and documents it in OpenAPI. Fields not in the model are dropped, so internal fields (password hashes) cannot leak, and types are serialised consistently.
??  How do you handle PATCH correctly?
=> Use an update model with optional fields and `model_dump(exclude_unset=True)`, so fields the client did not send are left alone, while an explicit `null` clears a value.
??  What is dependency injection in FastAPI?
=> Endpoints declare dependencies with `Depends(callable)`. FastAPI resolves the graph per request, caches each result for the request, runs `yield` dependencies' cleanup after the response, validates dependency parameters and lets tests replace them via `app.dependency_overrides`.
??  How do `yield` dependencies work and what are they used for?
=> The code before `yield` runs before the endpoint and provides the value; the code after (in `finally`) runs when the request is finished. They manage per-request resources: database sessions (commit or roll back), connections, locks, temporary files.
??  What are `lifespan` events?
=> An async context manager passed as `FastAPI(lifespan=...)` that runs once at start-up (create pools and clients, load models) and shutdown (close them). Shared resources are stored on `app.state`. It replaces `on_event("startup")`.
??  How is a background task different from a Celery task?
=> `BackgroundTasks` run in the same process after the response and are lost if the process dies; they suit tiny best-effort work. Celery (or Arq, RQ) uses a broker and separate workers, giving durability, retries, scheduling and scaling for long or important jobs.
??  How do you version an API?
=> Usually in the path (`/v1/...`) using separate routers, only for breaking changes; keep old versions working with a deprecation period, share the service layer, and document the change in the changelog and OpenAPI.

## Interview Q&A: Async, Performance and Concurrency in FastAPI

??  When do you use `async def` and when `def` for an endpoint?
=> `async def` when the body awaits async libraries; plain `def` when it calls blocking code (a sync ORM, `requests`), because FastAPI runs `def` endpoints in a thread pool. Never call blocking code inside `async def`: it freezes the event loop for every request.
??  What happens if you call a blocking function inside an `async def` endpoint?
=> The event loop is blocked for the duration, so no other request on that worker progresses: latency spikes appear while CPU looks idle. Fix with async libraries, `await asyncio.to_thread(...)`, or making the endpoint a plain `def`.
??  How many requests can a single uvicorn worker handle at once?
=> Thousands of concurrent I/O-bound requests (one event loop), but only one piece of Python runs at any instant, so CPU-bound handlers serialise. Scale CPU with more worker processes or replicas.
??  What is the GIL's effect on a FastAPI service?
=> Within one process threads do not run Python in parallel. That is acceptable for I/O-bound work; for CPU-bound work use multiple processes, a task queue or native libraries.
??  How do you run CPU-heavy work triggered by an endpoint?
=> Offload it: a process pool (`run_in_executor`), a task queue (Celery) with the result polled or pushed later, or a separate service. Do not do it inline in a request handler.
??  What is connection pooling and how do you size it?
=> A pool keeps a limited number of open database connections that requests borrow and return. Size it so `workers × (pool_size + max_overflow)` stays below the database's connection limit and matches the real concurrency; too big overloads the database, too small makes requests wait.
??  How do you make an endpoint idempotent and safe to retry?
=> Accept an idempotency key header, store it with the result atomically with the side effect, and return the stored result on a repeat. Use idempotent methods where possible and conditional updates (versions, ETags) for lost-update protection.
??  How would you implement rate limiting?
=> At a gateway or reverse proxy where possible, or with a Redis-backed limiter (token bucket or sliding window using atomic operations) keyed by user or IP, returning 429 with `Retry-After`. In-process counters are wrong with several workers.

## Interview Q&A: Data, Security and Operations

??  How do you prevent SQL injection in a FastAPI and SQLAlchemy project?
=> Never build SQL strings from input; use the ORM or `text()` with bound parameters, allow-list sort columns, validate input with Pydantic, and give the database user least privilege.
??  How do you secure an API with JWT?
=> Hash passwords with Argon2, issue short-lived signed access tokens with `sub`, `exp` and `iss`, verify them on every request with pinned algorithms, send them in the `Authorization` header over HTTPS, use refresh tokens for long sessions, and never put secrets in the payload (it is only signed).
??  What is BOLA and how do you stop it?
=> Broken object-level authorisation: a logged-in user accesses another user's object by changing an id. Check ownership or permission on every object access through a dependency or ownership-aware query, return 404 for objects they must not know exist, and test cross-user access.
??  What is the N+1 problem and how do you detect it?
=> One query for a list plus one per row for a lazy relationship. Detect with a statement counter or `lazy="raise"`; fix with `selectinload`/`joinedload`.
??  How do you run database migrations safely?
=> With Alembic as a separate release step, reviewing autogenerated scripts, keeping schema changes backwards compatible (expand then contract), and testing upgrade and downgrade in CI against the real database engine.
??  How would you test a FastAPI application?
=> Unit-test services with fakes, test routes with `TestClient` and `dependency_overrides` (in-memory or containerised database, fixed clock), assert status codes, error shapes and auth, add query-count and contract (OpenAPI) tests, and run everything in CI with coverage.
??  How do you make a FastAPI service observable?
=> JSON logs with request IDs, RED metrics (rate, errors, duration) exposed for Prometheus, distributed tracing with OpenTelemetry, liveness and readiness endpoints, and error tracking such as Sentry.
??  How do you deploy FastAPI?
=> Package in a small non-root Docker image, run uvicorn (several workers or one per replica) behind a reverse proxy or load balancer with TLS, configure via environment variables, run migrations as a release step, wire health checks and graceful shutdown, and roll out gradually with metrics watching.
??  CORS: what is it and what is the common mistake?
=> A browser mechanism that lets a server permit cross-origin reads. The common mistake is `allow_origins=["*"]` together with credentials, or reflecting any origin. List exact origins; CORS does not protect the API from non-browser clients.

## Cheat Sheets

!cheat FastAPI cheat sheet ::
| Task | Code |
| --- | --- |
| Route | `@app.get("/items/{id}")`, `@app.post(..., status_code=201)` |
| Query param with validation | `q: Annotated[str \| None, Query(max_length=20)] = None` |
| Body | `def create(item: ItemCreate)` |
| Response shape | `response_model=ItemRead`; `response_model_exclude_unset=True` |
| Error | `raise HTTPException(404, "not found")`; custom `@app.exception_handler(MyError)` |
| Dependency | `Depends(get_db)`; `Annotated[Session, Depends(get_db)]`; `yield` for clean-up |
| Router | `APIRouter(prefix="/users", tags=["users"])`; `app.include_router(r)` |
| Start-up and shutdown | `FastAPI(lifespan=lifespan)` |
| Settings | `class Settings(BaseSettings)`; `@lru_cache def get_settings()` |
| Auth | `OAuth2PasswordBearer(tokenUrl=...)`; verify JWT in a dependency |
| Test | `TestClient(app)`; `app.dependency_overrides[dep] = fake` |
| Middleware | `@app.middleware("http")`; `CORSMiddleware`; `GZipMiddleware` |
| Background | `BackgroundTasks.add_task(fn, ...)` |
| Run | `fastapi dev main.py`; `uvicorn pkg.main:app --workers 4` |
!end

!cheat SQLAlchemy 2.0 cheat sheet ::
| Task | Code |
| --- | --- |
| Model | `class Book(Base): id: Mapped[int] = mapped_column(primary_key=True)`; `Mapped[str \| None]` is nullable |
| Relationship | `author: Mapped[Author] = relationship(back_populates="books")` |
| Session | `with Session(engine) as s:`; `s.add(obj)`; `s.flush()`; `s.commit()`; `s.rollback()` |
| Query | `s.scalars(select(Book).where(Book.year > 2020).order_by(Book.title)).all()`; `.one()`, `.first()` |
| Get by key | `s.get(Book, 1)` (identity map first) |
| Eager load | `selectinload(Author.books)` (collections), `joinedload(Book.author)` (single) |
| Transaction | `with s.begin():`; `with s.begin_nested():` (savepoint) |
| Bulk | `s.execute(insert(Book), [{...}, {...}])`; `update(Book).where(...).values(...)` |
| Async | `create_async_engine("postgresql+asyncpg://...")`; `AsyncSession`; `await s.scalars(...)` |
| Migrate | `alembic revision --autogenerate -m "msg"`; `alembic upgrade head` |
!end

!cheat HTTP status codes you must know ::
- **2xx**: 200 OK, 201 Created (+ `Location`), 202 Accepted (async work), 204 No Content.
- **3xx**: 301/308 permanent redirect, 302/307 temporary redirect, 304 Not Modified.
- **4xx**: 400 malformed, 401 not authenticated, 403 not allowed, 404 not found, 405 method not allowed, 409 conflict, 413 payload too large, 415 unsupported media type, 422 validation failed, 429 too many requests.
- **5xx**: 500 server bug, 502 bad gateway, 503 unavailable (retry later), 504 gateway timeout.
!end

## A 10-Day Study Plan

| Day | Study | Build or practise |
| --- | --- | --- |
| 1 | Part 1: HTTP, ASGI, first app, OpenAPI | A hello API with path and query parameters and `TestClient` tests |
| 2 | Part 1: Pydantic models and validators | Customer model with nested address and custom validators |
| 3 | Part 1: dependencies, routers, settings, middleware | Pagination dependency, settings class, request-timing middleware |
| 4 | Part 2: CRUD, status codes, errors | Items API with Create/Update/Read models and Problem Details errors |
| 5 | Part 2: pagination, forms, files, CORS, ETag | Cursor pagination and an upload endpoint with limits |
| 6 | Part 3: SQLAlchemy, relationships, N+1 | Authors and books with a query counter test |
| 7 | Part 3: Alembic, repositories, async, testing | Add a migration; rollback-isolated test fixtures |
| 8 | Part 4: JWT, roles, BOLA, security headers | Login, `/me`, admin route, and a cross-user test |
| 9 | Part 4: logging, health, metrics, Docker | JSON logs, `/readyz`, a Dockerfile |
| 10 | Part 5: build the Library API; this part's Q&A and quiz | Re-implement the borrow rules from memory; take the quiz |

!tip How to talk about your FastAPI project :: Describe the **problem**, the **layers** (router, service, repository), one **rule that was tricky** (the concurrency in borrowing), how you **tested** it (service tests plus API tests with overrides), how it is **secured** (Argon2, JWT, ownership checks) and what you would do at ten times the load (more workers, caching, read replicas, a queue). Concrete trade-offs beat framework names.

??  A teammate says "FastAPI is async, so our endpoints are fast". What do you reply?
=> Async helps concurrency on I/O, not the speed of one request. If handlers call blocking libraries inside `async def`, or do CPU-heavy work, throughput gets worse, not better. Speed comes from queries, indexes, caching and not blocking the loop; measure with profiling and load tests.
??  What would you check first when a FastAPI endpoint is slow in production?
=> Where the time goes: database queries (count and duration, N+1, missing indexes), external calls without timeouts, blocking calls on the event loop, serialisation of huge responses, and pool saturation. Use tracing and a profiler, reproduce with a load test, then fix the biggest contributor.
