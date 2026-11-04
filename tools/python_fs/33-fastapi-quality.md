@part py-web-10 | FastAPI Beyond Basics · Part 4: Testing, Observability and Performance | web
## A Testing Strategy for Services

A service's tests have different jobs at different speeds. The goal is **fast feedback on the rules that matter**, not a coverage number.

| Layer | Tests | Speed | Real dependencies |
| --- | --- | --- | --- |
| **Unit** | Pure functions, domain rules, services with **fake repositories** | milliseconds | none |
| **API** | Routes through `TestClient`: status codes, validation, auth, error format | tens of ms | in-memory database, dependency overrides |
| **Integration** | Repositories and migrations against **real PostgreSQL**, Redis, a broker | seconds | containers (Testcontainers, docker-compose in CI) |
| **Contract** | `openapi.json` snapshot; consumer-driven contracts with other services | fast | none |
| **End-to-end** | A few critical journeys against a deployed environment | minutes | everything |
| **Property-based** | Invariants checked on generated inputs (Hypothesis) | seconds | none |
| **Non-functional** | Load tests, security scans, migration tests | minutes | staging |

Shape it as a **pyramid**: many unit tests, fewer API tests, a handful of integration and end-to-end tests. Common failure modes are an **ice-cream cone** (mostly slow end-to-end tests) and **mock-heavy unit tests** that restate the implementation and break on every refactor.

### Property-based testing with Hypothesis

Example-based tests check inputs you thought of. **Property-based tests** state a rule that must hold for **any** input and let the library hunt for a counter-example, then **shrink** it to the smallest failing case.

```python HypothesisDemo.py
import pathlib
import re
import subprocess
import sys

pathlib.Path("stats.py").write_text('''\
def average(values):
    return sum(values) / len(values)            # BUG: crashes on an empty list


def clamp(value, low, high):
    return max(low, min(value, high))
''')

pathlib.Path("test_properties.py").write_text('''\
from hypothesis import given, settings, strategies as st

from stats import average, clamp


@settings(derandomize=True, database=None)          # reproducible runs for this demonstration
@given(st.lists(st.integers(min_value=-1000, max_value=1000)))
def test_average_is_between_min_and_max(values):
    result = average(values)
    assert min(values) <= result <= max(values)


@settings(derandomize=True, database=None)
@given(st.integers(), st.integers(), st.integers())
def test_clamp_stays_inside_the_range(value, a, b):
    low, high = min(a, b), max(a, b)
    assert low <= clamp(value, low, high) <= high
''')

run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "--tb=short"], capture_output=True, text=True)
text = re.sub(r" in \d+\.\d+s", "", run.stdout)                           # drop the timing so the output is reproducible
for line in text.splitlines():
    if line.startswith("FAILED") or re.match(r"^\d+ (failed|passed)", line):
        print(line.strip())

sys.path.insert(0, ".")                                            # run the property directly to read Hypothesis's shrunk counter-example
import test_properties

try:
    test_properties.test_average_is_between_min_and_max()
except Exception as error:
    notes = " ".join(" ".join(note.split()) for note in getattr(error, "__notes__", []))
    print(type(error).__name__, "|", notes)
```

```output
```

Hypothesis found the empty list (which the author of `average` did not consider) and shrank to the **minimal** counter-example. Properties worth testing in services: "encode then decode returns the original", "a sorted result is ordered and a permutation of the input", "adding then removing an item leaves the cart unchanged", "the total of the invoice equals the sum of its lines", "parsing never crashes on any string" (it may raise a clean error, never an unexpected one).

??  What is the difference between an example-based test and a property-based test?
=> An example test asserts one specific input gives one specific output. A property test states a rule that must hold for all inputs in a described space; the framework generates many inputs, finds a failing one and shrinks it to a minimal counter-example, which finds edge cases you would not have thought of.
??  What is wrong with tests that mock everything?
=> They verify that your code calls the mocks in the way you wrote it, not that the system works, so they pass when the real integration is broken and fail when you refactor safely. Prefer fakes (simple in-memory implementations) and real components where cheap, and mock only at true boundaries such as network calls.

## Async Tests and Test Clients

Async endpoints and async dependencies are tested with `pytest-asyncio` and `httpx.AsyncClient` over `ASGITransport` (no server, no thread hop), which also lets tests `await` your own coroutines directly.

```python AsyncTests.py
import pathlib
import re
import subprocess
import sys

pathlib.Path("app.py").write_text('''\
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

state = {"started": False, "calls": 0}


@asynccontextmanager
async def lifespan(app):
    state["started"] = True
    yield
    state["started"] = False


app = FastAPI(lifespan=lifespan)


async def slow_lookup(item_id: int) -> dict:
    await asyncio.sleep(0.01)                          # stands in for an async database call
    if item_id > 100:
        raise HTTPException(404, "no such item")
    return {"id": item_id}


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    state["calls"] += 1
    return await slow_lookup(item_id)
''')

pathlib.Path("test_app.py").write_text('''\
import asyncio

import httpx
import pytest
import pytest_asyncio

from app import app, slow_lookup, state


@pytest_asyncio.fixture                                                         # async fixtures need this decorator in strict mode
async def client():
    async with app.router.lifespan_context(app):                                   # run start-up and shutdown around the test
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            yield client


@pytest.mark.asyncio
async def test_endpoint(client):
    response = await client.get("/items/7")
    assert response.status_code == 200 and response.json() == {"id": 7}
    assert state["started"] is True                                                # lifespan ran


@pytest.mark.asyncio
async def test_not_found(client):
    assert (await client.get("/items/500")).status_code == 404


@pytest.mark.asyncio
async def test_concurrent_requests_overlap(client):
    results = await asyncio.gather(*(client.get(f"/items/{i}") for i in range(20)))      # 20 requests at once
    assert [r.json()["id"] for r in results] == list(range(20))


@pytest.mark.asyncio
async def test_coroutines_can_be_awaited_directly():
    assert await slow_lookup(3) == {"id": 3}
''')

run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-W", "ignore", "-o", "asyncio_default_fixture_loop_scope=function"],
                     capture_output=True, text=True)
print(re.sub(r" in \d+\.\d+s", "", run.stdout).strip())
```

```output
```

Rules of thumb: keep **one event loop per test** (the default) so tests stay independent; do not mix sync `TestClient` and async fixtures in one test; override dependencies with `app.dependency_overrides` exactly as in sync tests; and if a test hangs, suspect a forgotten `await` or an awaited event that never fires (add timeouts with `asyncio.timeout` in tests).

### Test data, time and containers

- **Builders and factories** keep tests readable: `make_order(total=500, status="paid")` with sensible defaults beats copy-pasted dictionaries. Libraries: `factory_boy`, `polyfactory`, or 10 lines of your own.
- **Freeze time by injecting it** (a `Clock` dependency or `get_today`), the technique of the Library API project.
- **Real databases in CI**: start PostgreSQL with **Testcontainers** so each run has a clean, realistic database:

```python Testcontainers !skip
import pytest
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:17") as postgres:                     # starts a throw-away database in Docker
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)                                   # or: run the Alembic migrations, which also tests them
        yield engine
```

- **Test the unhappy paths**: timeouts, 503s from dependencies (`httpx.MockTransport`), constraint violations, duplicate submissions, expired tokens.
- **Measure what matters**: `pytest --cov=src --cov-branch --cov-fail-under=85` as a gate, and read the uncovered lines, not the percentage.

??  How do you test a FastAPI application that awaits other services?
=> Replace the outbound HTTP client with an `httpx.MockTransport` or a dependency override returning a fake, drive the app with `httpx.AsyncClient(transport=ASGITransport(app=app))`, and assert both the response and the calls made to the fake. Add tests where the fake times out or returns 503 to verify the resilience logic.
??  Why run integration tests against PostgreSQL in containers?
=> To catch dialect differences, real constraint and transaction behaviour, migration problems and driver issues that an in-memory SQLite database hides, while keeping every run isolated and reproducible.

## Logging, Tracing and Correlation

The request-ID middleware of Part 4 generalises into **distributed tracing**: a request crosses several services, and one **trace ID** ties together the logs and timings of all of them. The standard carrier is the W3C **`traceparent`** header: `version-traceid-parentid-flags`.

```python Tracing.py
import contextvars
import json
import secrets
import re
import sys

import structlog

trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")
TRACEPARENT = re.compile(r"^00-(?P<trace>[0-9a-f]{32})-(?P<parent>[0-9a-f]{16})-(?P<flags>[0-9a-f]{2})$")


def start_span(incoming_header: str | None):
    """Continue the caller's trace if the header is valid; otherwise start a new one."""
    match = TRACEPARENT.match(incoming_header or "")
    trace = match["trace"] if match else secrets.token_hex(16)
    span = secrets.token_hex(8)
    trace_id.set(trace)
    outgoing = f"00-{trace}-{span}-01"                                  # what we send to the next service
    return outgoing, (match["parent"] if match else None)


def add_trace(logger, method, event_dict):
    event_dict["trace_id"] = trace_id.get()
    return event_dict


structlog.configure(processors=[add_trace, structlog.processors.add_log_level, structlog.processors.JSONRenderer(sort_keys=True)],
                    logger_factory=structlog.PrintLoggerFactory(sys.stdout), cache_logger_on_first_use=False)
log = structlog.get_logger()

caller = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"         # the example from the W3C Trace Context specification
outgoing, parent = start_span(caller)
log.info("order created", order_id=42, amount=500)
print(parent, outgoing.split("-")[1] == "4bf92f3577b34da6a3ce929d0e0e4736", len(outgoing.split("-")[2]))
log.warning("downstream slow", dependency="payments", seconds=2.5)

fresh, no_parent = start_span("garbage")                                   # an invalid or absent header starts a new trace
print(no_parent, len(fresh.split("-")[1]), trace_id.get() == fresh.split("-")[1])
```

```output
```

| Concept | Meaning |
| --- | --- |
| **Trace** | The whole journey of one request across services (one trace ID) |
| **Span** | One unit of work in a trace (an endpoint, a database query, an HTTP call) with start, duration, attributes, and a parent span |
| **Context propagation** | Passing the trace ID to the next service (`traceparent` header, a message header in Kafka) |
| **OpenTelemetry** | The vendor-neutral standard and SDKs for traces, metrics and logs; `opentelemetry-instrumentation-fastapi`, `-sqlalchemy`, `-httpx` create spans automatically |
| **Backends** | Jaeger, Tempo, Zipkin, Datadog, Honeycomb: where traces are stored and searched |

A useful logging contract: every line is **one JSON object** with `timestamp`, `level`, `message`, `trace_id`, `service`, and the business identifiers you will search by (`order_id`, `user_id`). Never log secrets, full tokens, card numbers or personal data; sample or rate-limit noisy debug logs; and let the platform ship stdout instead of writing log files in containers.

??  What is the point of the `traceparent` header?
=> It carries the trace ID and the caller's span ID to the next service, so that service can attach its spans and logs to the same trace. Without propagation each service sees an isolated request and a cross-service problem cannot be followed.
??  What is the difference between logs, metrics and traces?
=> Logs are discrete events with context (what happened); metrics are aggregated numbers over time (how many, how fast, how full) cheap to store and alert on; traces follow one request across services with timings (where the time went). You need all three, linked by IDs.

## Performance: Measure, Cache, Then Tune

**Method**: define the target (a latency SLO such as "p95 under 300 ms at 200 requests/second"), **load test** a realistic mix, **profile** the slowest paths, change **one thing**, measure again. Optimising without a measurement is guessing.

```python Profiling.py
import cProfile
import io
import json
import pstats
import time

import orjson
from cachetools import TTLCache, cached
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
db_calls = {"count": 0}
clock = [1000.0]
cache = TTLCache(maxsize=128, ttl=60, timer=lambda: clock[0])             # an in-process cache with expiry (a fake clock keeps the demo deterministic)


def load_report(customer_id: int) -> dict:
    db_calls["count"] += 1                                               # stands in for several slow queries
    return {"customer": customer_id, "orders": [{"id": i, "total": i * 3} for i in range(200)]}


@cached(cache)
def cached_report(customer_id: int) -> dict:
    return load_report(customer_id)


@app.get("/report/{customer_id}")
def report(customer_id: int, use_cache: bool = True):
    return cached_report(customer_id) if use_cache else load_report(customer_id)


client = TestClient(app)
for _ in range(5):
    client.get("/report/1")
print("cached: database called", db_calls["count"], "time(s) for 5 requests")
for _ in range(5):
    client.get("/report/2?use_cache=false")
print("uncached: database called", db_calls["count"] - 1, "more times for 5 requests")
clock[0] += 61                                                           # the entry expires
client.get("/report/1")
print("after the TTL the cache reloads:", db_calls["count"] - 6)

profiler = cProfile.Profile()
profiler.enable()
for _ in range(50):
    client.get("/report/3?use_cache=false")
profiler.disable()
stats = pstats.Stats(profiler, stream=io.StringIO())
own = {name: calls for (_, _, name), (_, calls, *_) in stats.stats.items() if name in ("load_report", "report")}
print("profile shows these app functions were called:", own)

payload = {"items": [{"id": i, "name": f"item-{i}", "price": i * 1.5} for i in range(2000)]}
started = time.perf_counter()
for _ in range(50):
    json.dumps(payload)
json_time = time.perf_counter() - started
started = time.perf_counter()
for _ in range(50):
    orjson.dumps(payload)
orjson_time = time.perf_counter() - started
print("orjson is at least 2x faster than json for a big payload:", json_time > 2 * orjson_time)
```

```output
```

The big levers, in the order that usually pays:

1. **The database**: N+1 queries, missing indexes, selecting too many columns or rows, `OFFSET` pagination, long transactions. Most "slow API" tickets end here.
2. **Do less work**: **cache** (in-process `TTLCache`, Redis cache-aside with explicit TTLs and invalidation, HTTP caching with `ETag`/`Cache-Control`), precompute, paginate, return only needed fields.
3. **Do the waiting in parallel**: `asyncio.gather` over independent calls with a concurrency limit; move slow work to a queue and return `202 Accepted`.
4. **Do not block the event loop**: async drivers or `def` endpoints; offload CPU work.
5. **Serialisation**: very large JSON is CPU-bound (`orjson`, smaller payloads, streaming); response models validate every item, so for huge lists consider returning pre-validated data.
6. **Process model**: right number of workers/replicas, keep-alive and proxy buffering, `uvloop` and `httptools` (included in `uvicorn[standard]`).
7. **Only then micro-optimise** Python.

### Capacity and SLOs: the arithmetic

```python Capacity.py
import math

# Little's law: concurrent requests in the system = arrival rate x average time in system
arrival_rate = 400            # requests per second at peak
latency = 0.120               # average seconds per request
in_flight = arrival_rate * latency
print("requests in flight:", in_flight)

# A sync worker handles ONE request at a time; an async worker overlaps I/O waits.
cpu_time = 0.015              # seconds of actual CPU per request
workers_for_cpu = math.ceil(arrival_rate * cpu_time / 0.7)           # keep CPU at about 70% utilisation
print("processes needed for the CPU work alone:", workers_for_cpu)

# Database connections: concurrency at the database = rate x time spent holding a connection
db_hold = 0.030
print("average busy connections:", arrival_rate * db_hold, "-> a pool of 20 per process is far more than needed")

# SLO arithmetic: availability targets as allowed downtime per 30 days
month = 30 * 24 * 60
for target in (99.0, 99.9, 99.95, 99.99):
    print(f"{target}% -> {month * (1 - target / 100):.1f} minutes of error budget per month")
```

```output
```

An **SLO** (service-level objective) is a target on an **SLI** (a measured indicator such as "fraction of requests under 300 ms and not 5xx"); the **error budget** is what you may fail. When the budget is spent, reliability work takes priority over features. Alert on **budget burn rate**, not on single failed requests.

??  A service's p99 latency doubled after a release but the average barely moved. What does that tell you?
=> A small fraction of requests got much slower (a new slow path, lock contention, a cold cache, a GC pause, a particular tenant or input), which averages hide. Look at the latency histogram, slice by endpoint and parameters, and use traces of the slowest requests.
??  What does Little's law say and how do you use it?
=> The average number of requests in the system equals the arrival rate times the average time each spends in it (`L = λ × W`). Use it to estimate concurrency and thus workers, threads and connections: 400 requests/second at 120 ms means about 48 requests in flight on average.
??  Where do you start when asked to make an API three times faster?
=> Measure: define the target and load profile, profile or trace to find where time goes, and fix the biggest contributor (usually database access and N+1 queries), then caching, parallelising independent I/O and removing blocking calls, re-measuring after each change.
