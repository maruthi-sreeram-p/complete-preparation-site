@part py-web-1 | FastAPI Basics · Part 1: Web and FastAPI Foundations | web
## What a Web Framework Does

A web framework turns **HTTP requests into Python function calls** and **return values into HTTP responses**. Underneath, a client sends a request (method, path, headers, optional body); a server program parses it and hands it to your code; your code returns a status code, headers and a body.

```text
GET /items/42?verbose=true HTTP/1.1          <- request line: method, path, query string
Host: api.example.com                        <- headers
Accept: application/json
                                              <- blank line, then an optional body
HTTP/1.1 200 OK                              <- status line
Content-Type: application/json               <- response headers
{"id": 42, "name": "pen"}                    <- response body
```

| Concept | Meaning |
| --- | --- |
| **Method** | `GET` read, `POST` create, `PUT` replace, `PATCH` partial update, `DELETE` remove. `GET` must be safe (no side effects) |
| **Status codes** | 2xx success (200 OK, 201 Created, 204 No Content), 3xx redirect, **4xx client error** (400, 401, 403, 404, 409, 422, 429), **5xx server error** (500, 502, 503) |
| **Headers** | Metadata: `Content-Type`, `Authorization`, `Cache-Control`, `ETag` |
| **Idempotent** | Repeating the call has the same effect as once: `GET`, `PUT`, `DELETE` are; `POST` is not |

### WSGI and ASGI: how Python servers talk to frameworks

A Python web **server** (Gunicorn, Uvicorn) and a **framework** (Django, Flask, FastAPI) need a shared contract:

| Standard | Style | Servers | Frameworks |
| --- | --- | --- | --- |
| **WSGI** (PEP 3333) | Synchronous: one request per worker thread or process, a plain function `app(environ, start_response)` | Gunicorn, uWSGI, Waitress | Flask, Django (classic) |
| **ASGI** | Asynchronous: coroutines, **WebSockets** and long-lived connections, `async def app(scope, receive, send)` | Uvicorn, Hypercorn, Daphne, Granian | **FastAPI**, Starlette, Django (async), Quart |

### Choosing a framework

| | **FastAPI** | **Django** | **Flask** |
| --- | --- | --- | --- |
| Style | API-first, async-friendly, type-hint driven | "Batteries included": ORM, admin, auth, templates, forms | Micro-framework: you pick the pieces |
| Validation and docs | **Automatic** from type hints (Pydantic) and OpenAPI | Forms, DRF serializers | Manual or extensions |
| Database | Your choice (SQLAlchemy usual) | Built-in ORM and migrations | Your choice |
| Best for | JSON APIs, microservices, ML back ends | Full web apps, CMS, admin-heavy products, large teams | Small services, prototypes, learning |
| Learning curve | Low to medium | Medium (many concepts) | Low |

This tree teaches **FastAPI first** (the modern API default), then Django and Flask. The ideas (routing, validation, dependency injection, persistence, security, testing) carry across all three.

!interview Why is FastAPI fast? :: Two reasons. It runs on ASGI with an event loop, so one process serves many concurrent I/O-bound requests (Part 9 of Core Python), and Pydantic v2's validation core is written in Rust. But the framework's speed is rarely your bottleneck: database queries and external calls are. "Fast to develop" (types give you validation, serialisation and docs for free) is the bigger win.

??  What is the difference between WSGI and ASGI?
=> WSGI is the synchronous Python web standard: one blocking call per request. ASGI is the asynchronous successor: it supports `async`/`await`, WebSockets, server-sent events and long-lived connections. FastAPI and Starlette are ASGI; classic Flask and Django are WSGI (Django also supports ASGI).
??  Which HTTP methods are idempotent, and why does it matter?
=> `GET`, `PUT`, `DELETE` (and `HEAD`, `OPTIONS`); `POST` is not. Clients, proxies and retry logic can safely repeat idempotent requests after a timeout; repeating a `POST` may create duplicates unless you add an idempotency key.

## Your First FastAPI App

Install and run (the app below is exercised with `TestClient`, which calls the ASGI app in-process, so no server is needed in tests):

```bash Install and run
uv add fastapi "uvicorn[standard]"          # or: python -m pip install fastapi "uvicorn[standard]"
uv run uvicorn main:app --reload            # http://127.0.0.1:8000   docs at /docs
```

```python FirstApp.py
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Shop API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "hello"}                          # a dict becomes JSON automatically


@app.get("/items/{item_id}")                              # a path parameter, converted to int from the annotation
def read_item(item_id: int, verbose: bool = False, q: str | None = None):
    item = {"id": item_id, "name": f"item-{item_id}"}    # `verbose` and `q` come from the query string
    if verbose:
        item["q"] = q
    return item


@app.post("/echo", status_code=201)
async def echo(payload: dict):                            # `async def` runs on the event loop; `def` runs in a thread pool
    return {"received": payload}


client = TestClient(app)

print(client.get("/").json())
print(client.get("/items/42").json())
print(client.get("/items/42?verbose=true&q=pen").json())
print(client.get("/items/abc").status_code, client.get("/items/abc").json()["detail"][0]["msg"])
response = client.post("/echo", json={"a": 1})
print(response.status_code, response.json())
print(client.get("/nope").status_code, client.get("/nope").json())
print(client.post("/").status_code, client.post("/").json())
```

```output
```

What happened, in order:

1. `@app.get(path)` registers the function as the handler for that method and path.
2. `{item_id}` in the path is a **path parameter**; its annotation `int` makes FastAPI convert it, and a value like `abc` is rejected with **422 Unprocessable Entity** and a precise error, without your code running.
3. Parameters that are **not** in the path become **query parameters** (`?verbose=true`), with defaults making them optional. `bool` accepts `true`, `1`, `yes`, `on`.
4. A `dict` (or Pydantic model, list...) return value is serialised to JSON with `Content-Type: application/json`.
5. Unknown paths give `404`, and a wrong method on a known path gives `405 Method Not Allowed`.

### Parameter sources at a glance

| Declared as | Comes from | Example |
| --- | --- | --- |
| Name in the path template | **Path** | `/items/{item_id}` |
| Simple type, not in the path | **Query string** | `?limit=10` |
| Pydantic model or `Body()` | **JSON body** | `{"name": "pen"}` |
| `Header()` | Request header | `User-Agent`, `X-Request-ID` |
| `Cookie()` | Cookie | session id |
| `Depends(...)` | A dependency | database session, current user |
| `File()`, `Form()` | Multipart / form data | uploads (Part 2) |

### The automatic documentation

FastAPI builds an **OpenAPI** description from your code and serves it as JSON at `/openapi.json`, with interactive Swagger UI at `/docs` and ReDoc at `/redoc`:

```python OpenApi.py
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Shop API", version="1.0.0")


@app.get("/items/{item_id}", summary="Read one item", tags=["items"])
def read_item(item_id: int, verbose: bool = False):
    """Return the item with this id."""                  # the docstring becomes the endpoint's description
    return {"id": item_id}


schema = TestClient(app).get("/openapi.json").json()
operation = schema["paths"]["/items/{item_id}"]["get"]
print(schema["info"], sorted(schema["paths"]))
print(operation["summary"], operation["tags"], operation["description"])
print([(p["name"], p["in"], p["required"], p["schema"]["type"]) for p in operation["parameters"]])
```

```output
```

!note Test client and httpx versions :: `TestClient` is built on `httpx`. Recent Starlette releases print a deprecation warning saying the test client should run on `httpx2` instead; the tests still pass. Install whichever package your Starlette version asks for (see its release notes) and pin it in the dev dependencies, so upgrades do not surprise your CI.

That schema is a **contract**: client SDK generators, API gateways, Postman and contract tests all consume it, and it stays in sync with the code because it is generated from it.

!tip def or async def? :: Use `async def` when the body awaits async libraries (an async database driver, `httpx.AsyncClient`). Use plain `def` when it calls blocking code (a synchronous ORM, `requests`, file I/O): FastAPI runs it in a worker thread so it does not block the event loop. The one forbidden combination is **blocking calls inside `async def`** (Part 9 of Core Python).

??  How does FastAPI decide whether a function parameter is a path, query or body parameter?
=> If its name appears in the path template it is a path parameter; if it is a Pydantic model (or declared with `Body`) it comes from the JSON body; otherwise a simple type becomes a query parameter. `Header`, `Cookie`, `Form`, `File` and `Depends` change the source explicitly.
??  What is returned when a client sends a path parameter that cannot be converted to the annotated type?
=> A `422 Unprocessable Entity` with a JSON body listing the location, message and error type of each problem. Your function is never called.
??  Where do `/docs` and `/openapi.json` come from?
=> FastAPI generates an OpenAPI document from the routes, type hints, docstrings and Pydantic models at start-up and serves it with Swagger UI and ReDoc, so documentation cannot drift from the code.

## Pydantic Models and Validation

**Pydantic** turns type annotations into **parsing and validation at run time**. FastAPI uses it for request bodies, query parameters and responses. A `BaseModel` is a class whose fields are annotated; building an instance validates and converts the input, or raises a `ValidationError` listing everything wrong.

```python Pydantic.py
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ValidationError, computed_field, field_validator, model_validator


class Address(BaseModel):
    city: str
    pin: Annotated[str, Field(pattern=r"^\d{6}$")]


class Customer(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=50)]
    email: EmailStr
    age: Annotated[int, Field(ge=18, le=120)]
    balance: Decimal = Decimal("0.00")
    joined: date | None = None
    tags: list[str] = []
    address: Address | None = None

    @field_validator("name")
    @classmethod
    def title_case(cls, value: str) -> str:                       # runs after the type conversion
        return value.strip().title()

    @model_validator(mode="after")
    def tags_unique(self):
        if len(set(self.tags)) != len(self.tags):
            raise ValueError("tags must be unique")
        return self

    @computed_field
    @property
    def domain(self) -> str:
        return self.email.split("@")[1]


good = Customer.model_validate({"name": "  asha rao ", "email": "asha@example.com", "age": "29",        # "29" is coerced to 29
                                "balance": "10.50", "joined": "2026-11-04", "tags": ["vip"], "address": {"city": "Pune", "pin": "411001"}})
print(good.name, good.age, good.balance, good.joined, good.domain)
print(good.model_dump(exclude={"address"}))
print(good.model_dump_json(include={"name", "domain"}))

try:
    Customer(name="A", email="not-an-email", age=15, tags=["x", "x"], address={"city": "Pune", "pin": "12"})
except ValidationError as error:
    for problem in error.errors():
        print(problem["loc"], "->", problem["msg"])
```

```output
```

Key behaviours:

- **Coercion ("lax" mode)**: `"29"` becomes `29`, `"2026-11-04"` a `date`, `"10.50"` a `Decimal`. Use `strict=True` (per field or model) to refuse such conversions.
- **Constraints** go in `Field(...)` (`ge`, `le`, `min_length`, `pattern`) or in `Annotated` types; custom rules in `@field_validator` and `@model_validator`.
- **Errors are structured**: each has a location path (`("address", "pin")`), a message and a type, which FastAPI returns to clients in the 422 body.
- **Serialisation**: `model_dump()` gives a dict, `model_dump_json()` a JSON string; `exclude`, `include`, `exclude_unset` and `by_alias` shape the output.
- **Validation is separate from type hints**: this is what plain dataclasses and `typing` do **not** do (Core Python, Part 12).

```python TypeAdapter.py
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)    # reject unknown fields; immutable instances

    id: int
    name: str
    unit_price: float = Field(alias="unitPrice")                  # accept camelCase JSON, use snake_case in Python


item = Item.model_validate({"id": 1, "name": " pen ", "unitPrice": 2.5})
print(item, item.model_dump(by_alias=True))

try:
    Item.model_validate({"id": 1, "name": "pen", "unitPrice": 2.5, "colour": "blue"})
except ValidationError as error:
    print(error.errors()[0]["type"], error.errors()[0]["loc"])

ints = TypeAdapter(list[int])                                     # validate things that are not models
print(ints.validate_python(["1", 2, 3.0]), ints.validate_json("[4, 5]"))
```

```output
```

!interview Pydantic model, dataclass or TypedDict? :: At a **trust boundary** (HTTP bodies, config files, messages from other services) use Pydantic: it validates and converts. Inside your domain logic, plain dataclasses or Pydantic are both fine; avoid re-validating data you already validated. `TypedDict` only annotates dictionaries for the type checker and validates nothing.

??  What does Pydantic add over type hints?
=> Run-time parsing and validation: converting types (`"29"` to `29`), enforcing constraints (ranges, patterns, lengths), producing structured error reports and serialising to dicts and JSON. Type hints alone are only checked by external tools.
??  How do you reject unknown fields in a request body?
=> Set `model_config = ConfigDict(extra="forbid")` on the model: any field that is not declared makes validation fail with an `extra_forbidden` error. The default is to ignore extras.
??  What is the difference between `field_validator` and `model_validator`?
=> A field validator checks or transforms one field's value; a model validator sees the whole model (mode `"before"` for raw input, `"after"` for the built instance) and is used for rules across several fields, such as "end date after start date".

## Dependency Injection with `Depends`

A **dependency** is a callable that FastAPI runs **before** your endpoint and whose result it passes in as an argument. It is how you share a database session, the current user, pagination parameters or settings across endpoints, without globals, and how tests replace them.

```python Dependencies.py
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.testclient import TestClient

app = FastAPI()
events = []                                                       # records the order of set-up and tear-down for the demo


class Pagination:                                                  # a class dependency: its __init__ parameters are query parameters
    def __init__(self, page: Annotated[int, Query(ge=1)] = 1, size: Annotated[int, Query(ge=1, le=100)] = 10):
        self.page, self.size = page, size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


def get_db():                                                      # a dependency with `yield`: set-up before, clean-up after the response
    events.append("open db")
    db = {"items": ["pen", "ink", "pad", "clip", "tape"]}
    try:
        yield db
    finally:
        events.append("close db")


def current_user(x_user: Annotated[str | None, Header()] = None):   # a sub-dependency: reads a header
    if not x_user:
        raise HTTPException(status_code=401, detail="missing X-User header")
    return x_user


def require_admin(user: Annotated[str, Depends(current_user)]):     # depends on another dependency
    if user != "admin":
        raise HTTPException(status_code=403, detail="admins only")
    return user


@app.get("/items")
def list_items(db: Annotated[dict, Depends(get_db)], pagination: Annotated[Pagination, Depends()]):
    events.append("handler")
    return db["items"][pagination.offset:pagination.offset + pagination.size]


@app.delete("/items/{name}")
def delete_item(name: str, db: Annotated[dict, Depends(get_db)], admin: Annotated[str, Depends(require_admin)]):
    db["items"].remove(name)
    return {"deleted": name, "by": admin}


client = TestClient(app)
print(client.get("/items?page=2&size=2").json(), events)
print(client.get("/items?size=500").status_code)
print(client.delete("/items/pen").status_code, client.delete("/items/pen", headers={"X-User": "ravi"}).status_code)
print(client.delete("/items/pen", headers={"X-User": "admin"}).json())

# Tests replace dependencies instead of patching globals
app.dependency_overrides[get_db] = lambda: {"items": ["fake-1", "fake-2"]}
print(client.get("/items").json())
app.dependency_overrides.clear()
```

```output
```

How to read this:

- **Parameters of a dependency are declared like endpoint parameters** (here `page` and `size` come from the query string, and `x_user` from a header), so dependencies are validated and documented too.
- **Dependencies can depend on dependencies** (`require_admin` uses `current_user`); FastAPI builds the graph and runs each dependency once per request (it caches by default).
- **`yield` dependencies** run their `finally` block **after the response is produced**: the standard way to open and close a database session or connection per request.
- **`app.dependency_overrides`** swaps any dependency for a test double; this is why FastAPI code needs no mocking framework to test.
- The `Annotated[T, Depends(...)]` spelling is the current recommended style, and lets you name a dependency once and reuse it: `DbDep = Annotated[Session, Depends(get_db)]`.

!realworld The three dependencies in nearly every service :: `get_db` (a session per request, committed or rolled back at the end), `get_current_user` (parses the token and loads the user, or raises 401), and `get_settings` (cached configuration). Authorisation (`require_admin`), pagination, rate limiting and request IDs are further dependencies layered on top.

??  What is dependency injection and what does `Depends` give you?
=> Passing collaborators into a function instead of creating them inside. `Depends` lets an endpoint declare what it needs (database session, current user, settings); FastAPI creates it per request, handles sub-dependencies and cleanup, validates its parameters, documents them in OpenAPI and lets tests override it.
??  How does a `yield` dependency differ from a normal one?
=> A normal dependency returns a value. A `yield` dependency yields the value for the endpoint and resumes after the response is sent, so the code after `yield` (in `finally`) does clean-up such as closing a session or releasing a connection.
??  How do you test an endpoint that uses a database dependency?
=> Set `app.dependency_overrides[get_db] = override` with a function that returns a test session (an in-memory SQLite database or a fake repository), call the endpoint through `TestClient`, and clear the overrides afterwards.

## Configuration, Routers and Project Layout

### Settings from the environment

Twelve-factor apps read configuration from **environment variables**. `pydantic-settings` loads and validates them into a typed object once, so a missing or malformed value fails at start-up instead of in production.

```python Settings.py
import os
from functools import lru_cache

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHOP_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./shop.db"
    debug: bool = False
    port: int = Field(default=8000, ge=1, le=65535)
    allowed_origins: list[str] = ["http://localhost:5173"]
    secret_key: str                                              # required: no default, so it must be provided


@lru_cache                                                       # build once, share everywhere (use as a dependency)
def get_settings() -> Settings:
    return Settings()


try:
    Settings()
except ValidationError as error:
    print("missing:", [e["loc"][0] for e in error.errors()])

os.environ.update({"SHOP_SECRET_KEY": "s3cret", "SHOP_DEBUG": "true", "SHOP_PORT": "9000", "SHOP_ALLOWED_ORIGINS": '["https://app.example.com"]'})
settings = get_settings()
print(settings.debug, settings.port, settings.allowed_origins, settings.database_url)
print(get_settings() is settings, "secret_key" in settings.model_dump())
```

```output
```

Never commit real secrets: `.env` goes in `.gitignore`; production values come from the platform (Kubernetes secrets, a secret manager). Use `SecretStr` for values that must not appear in logs.

### Routers and an application factory

Split an app into **routers**, one per feature, each with its own prefix and tags, and assemble them in one place. A `lifespan` function runs start-up and shutdown code (open pools, warm caches, close clients) once per process.

```python Routers.py
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.testclient import TestClient

log = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.append("startup: create pool")
    app.state.pool = {"connections": 5}                        # shared resources live on app.state
    yield
    log.append("shutdown: close pool")


users = APIRouter(prefix="/users", tags=["users"])
orders = APIRouter(prefix="/orders", tags=["orders"])


@users.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}


@orders.get("/")
def list_orders(request: Request):
    return {"pool": request.app.state.pool, "orders": []}


def create_app() -> FastAPI:                                     # an app factory: tests can build fresh apps
    app = FastAPI(title="Shop", lifespan=lifespan)
    app.include_router(users)
    app.include_router(orders, prefix="/v1")                    # routers can be mounted under another prefix
    return app


with TestClient(create_app()) as client:                         # the `with` block runs lifespan start-up and shutdown
    print(client.get("/users/7").json(), client.get("/v1/orders/").json())
    print(sorted(path for path in client.get("/openapi.json").json()["paths"]))          # the routes, as the OpenAPI schema lists them
print(log)
```

```output
```

A typical project layout:

```text Project layout
shop-api/
  pyproject.toml            # dependencies and tool config (uv.lock next to it)
  src/shop/
    main.py                 # create_app(), includes the routers
    config.py               # Settings
    deps.py                 # get_db, get_current_user, ...
    models.py               # SQLAlchemy ORM models
    schemas.py              # Pydantic request and response models
    repositories.py         # database access
    services.py             # business logic
    routers/
      users.py
      orders.py
  tests/
    conftest.py             # fixtures: app, client, in-memory database
    test_orders.py
  Dockerfile
```

The separation **router (HTTP) to service (rules) to repository (database)** keeps HTTP details out of business logic and makes each layer testable: the same idea as controller, service and repository in Spring.

??  What does the `lifespan` function do?
=> It is an async context manager run when the application starts and stops: code before `yield` runs at start-up (create connection pools, load models), code after at shutdown (close them). It replaces the older `@app.on_event("startup")` handlers.
??  Why read configuration through a `Settings` class instead of `os.environ` everywhere?
=> It validates and converts everything once at start-up (types, ranges, required values), gives IDE completion and a single place to see all settings, supports `.env` files in development, and can be overridden in tests.
??  Why separate routers, services and repositories?
=> Each layer has one job: routers translate HTTP to Python calls and back, services hold business rules, repositories talk to the database. You can test rules without HTTP, swap the database, and reuse a service from a CLI or a background worker.

## Requests, Responses and Middleware

Most of the time you return plain data and FastAPI builds the response, but you can reach the underlying objects when you need headers, cookies, custom status codes or streaming.

```python ResponsesDemo.py
import time
from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()


@app.middleware("http")                                           # runs around EVERY request
async def add_timing_header(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - started) * 1000:.0f}ms"
    response.headers["X-Request-Path"] = request.url.path
    return response


@app.get("/headers")
def read_headers(request: Request, user_agent: Annotated[str | None, Header()] = None, session: Annotated[str | None, Cookie()] = None):
    return {"user_agent": user_agent, "session": session, "client_host": request.client.host, "query": dict(request.query_params)}


@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie("session", "abc123", httponly=True, samesite="lax", max_age=3600)
    response.headers["Cache-Control"] = "no-store"
    return {"ok": True}


@app.get("/custom")
def custom():
    return JSONResponse({"detail": "teapot"}, status_code=418, headers={"X-Reason": "demo"})


@app.get("/text", response_class=PlainTextResponse)
def text():
    return "plain text"


@app.get("/old", include_in_schema=False)
def old():
    return RedirectResponse("/text", status_code=307)


@app.get("/stream")
def stream():
    def generate():
        for chunk in ("a", "b", "c"):
            yield chunk + "\n"
    return StreamingResponse(generate(), media_type="text/plain")


client = TestClient(app)
r = client.get("/headers?x=1", headers={"User-Agent": "demo/1.0"}, cookies={"session": "s-1"})
print(r.json(), r.headers["x-request-path"], r.headers["x-process-time"].endswith("ms"))
r = client.get("/set-cookie")
print(r.json(), r.headers["set-cookie"].split(";")[0], r.headers["cache-control"])
r = client.get("/custom")
print(r.status_code, r.headers["x-reason"], r.json())
print(client.get("/text").text, client.get("/old", follow_redirects=False).status_code, client.get("/stream").text.split())
```

```output
```

**Middleware** wraps the whole request: use it for cross-cutting concerns (timing, request IDs, security headers, compression, CORS), not for business logic. Keep it light: it runs on every call. Built-in middleware includes `CORSMiddleware`, `GZipMiddleware` and `TrustedHostMiddleware`.

!cheat FastAPI foundations cheat sheet ::
- `@app.get/post/put/patch/delete("/path/{id}")`; path params from the template; other simple types are query params; a Pydantic model is the body.
- `422` means validation failed before your code ran; `HTTPException(status_code, detail)` for your own errors.
- Pydantic: `BaseModel`, `Field(ge=, le=, min_length=, pattern=)`, `field_validator`, `model_validator`, `model_validate`, `model_dump`, `extra="forbid"`.
- `Depends(callable)` injects; `yield` dependencies clean up; `app.dependency_overrides` for tests.
- `APIRouter(prefix=, tags=)` + `include_router`; `lifespan` for start-up and shutdown; `pydantic-settings` for configuration.
- `def` endpoints run in a thread pool; `async def` endpoints must not block the loop.
- `TestClient(app)` tests in-process; `/docs` and `/openapi.json` are generated.
!end

??  What is middleware and when should you use it?
=> A function that wraps every request and response (it receives the request and a `call_next`). Use it for cross-cutting behaviour such as timing, request and correlation IDs, security headers, compression and CORS; do not put business rules there.
??  How do you set a cookie or a custom header from an endpoint?
=> Add a `response: Response` parameter and call `response.set_cookie(...)` or modify `response.headers`, then return your data as usual; or return a `JSONResponse(..., headers={...})` yourself.
??  Which response class do you use to stream a large file or generated data?
=> `StreamingResponse` with a (sync or async) generator, or `FileResponse` for a file on disk. The body is sent in chunks without being held in memory.
