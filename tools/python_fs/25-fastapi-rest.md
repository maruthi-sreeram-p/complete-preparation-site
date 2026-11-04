@part py-web-2 | FastAPI Basics · Part 2: Building REST APIs | web
## A CRUD API, Done Properly

A **REST API** exposes **resources** (nouns) at URLs and uses HTTP methods and status codes to say what to do and what happened. A well-designed CRUD resource looks the same everywhere:

| Operation | Method and URL | Success | Typical errors |
| --- | --- | --- | --- |
| List | `GET /items` | 200 + list | 400/422 bad filters |
| Read one | `GET /items/{id}` | 200 | 404 |
| Create | `POST /items` | **201** + `Location` header + the created item | 409 duplicate, 422 invalid |
| Replace | `PUT /items/{id}` | 200 (or 204) | 404, 422 |
| Partial update | `PATCH /items/{id}` | 200 | 404, 422 |
| Delete | `DELETE /items/{id}` | **204 No Content** | 404 (or 204 again: delete is idempotent) |

The pattern that keeps APIs clean is **three Pydantic models per resource**: what a client may *send* to create, what it may send to update, and what the server *returns* (which adds server-owned fields such as `id` and timestamps and hides secrets).

```python Crud.py
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):                                           # what a client may send to create
    name: Annotated[str, Field(min_length=1, max_length=80)]
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    in_stock: bool = True


class ItemUpdate(BaseModel):                                           # PATCH: every field optional
    name: Annotated[str | None, Field(min_length=1, max_length=80)] = None
    price: Annotated[Decimal | None, Field(gt=0, max_digits=10, decimal_places=2)] = None
    in_stock: bool | None = None


class ItemRead(ItemCreate):                                            # what the server returns: adds server-owned fields
    id: int
    created_at: datetime


app = FastAPI()
DB: dict[int, dict] = {}
NEXT_ID = {"value": 1}


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, response: Response):
    item_id = NEXT_ID["value"]
    NEXT_ID["value"] += 1
    DB[item_id] = {"id": item_id, "created_at": datetime(2026, 11, 4, tzinfo=timezone.utc), **payload.model_dump()}
    response.headers["Location"] = f"/items/{item_id}"                 # tell the client where the new resource lives
    return DB[item_id]


@app.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail=f"item {item_id} not found")
    return DB[item_id]


@app.put("/items/{item_id}", response_model=ItemRead)
def replace_item(item_id: int, payload: ItemCreate):                  # PUT replaces the whole representation
    read_item(item_id)
    DB[item_id].update(payload.model_dump())
    return DB[item_id]


@app.patch("/items/{item_id}", response_model=ItemRead)
def patch_item(item_id: int, payload: ItemUpdate):
    read_item(item_id)
    DB[item_id].update(payload.model_dump(exclude_unset=True))          # only the fields the client actually sent
    return DB[item_id]


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    DB.pop(item_id, None)                                              # idempotent: deleting twice is not an error here


client = TestClient(app)
created = client.post("/items", json={"name": "pen", "price": "12.50"})
print(created.status_code, created.headers["location"], created.json())
print(client.post("/items", json={"name": "", "price": -1}).json()["detail"][0]["msg"])
print(client.patch("/items/1", json={"in_stock": False}).json()["in_stock"], client.get("/items/1").json()["name"])
print(client.patch("/items/1", json={"price": "15"}).json()["price"], client.put("/items/1", json={"name": "ink", "price": "9.99"}).json()["name"])
print(client.delete("/items/1").status_code, client.get("/items/1").status_code, client.delete("/items/1").status_code)
```

```output
```

Points worth remembering:

- **`response_model`** filters and documents what is returned. Return a dict or ORM object with extra fields (a password hash!) and only the declared fields reach the client.
- **`exclude_unset=True`** is what makes PATCH work: it distinguishes "field not sent" from "field sent as null".
- **`PUT` replaces** the representation (all fields required); **`PATCH` changes** the fields sent. Many APIs only offer PATCH.
- Return **201 with a `Location` header** for creation and **204** with no body for deletion.
- Money is a `Decimal` (or an integer in minor units), never `float`.

!interview PUT versus PATCH :: `PUT` is a full replacement and is idempotent; `PATCH` is a partial update (idempotent only if the patch is absolute rather than "increment by 1"). Say which you offer and why. For PATCH, handle the difference between a field that is **absent** (leave unchanged) and one that is explicitly `null` (clear it): `model_dump(exclude_unset=True)` preserves that distinction.

??  Why use separate Create, Update and Read models?
=> They differ: the create model must not accept server-owned fields (`id`, `created_at`, `role`), the update model makes fields optional, and the read model adds those server-owned fields and hides secrets. Using one model for all three invites mass assignment (a client setting `is_admin`) and awkward optionality.
??  Which status codes do you return for create and delete?
=> `201 Created` with a `Location` header (and the created resource) for a successful `POST`, and `204 No Content` for a successful `DELETE`. `404` for a missing resource on read, update and delete if you want strictness, or `204` for an idempotent delete.
??  What does `response_model` do besides documentation?
=> It validates and filters the returned object: fields not declared in the model are dropped, and types are serialised. It is a safety net against leaking internal fields such as password hashes.

## Validation Errors and a Consistent Error Format

FastAPI returns `422` with a `detail` list for invalid input. Clients and operators benefit from **one error format across the whole API**. The standard is **RFC 9457 "Problem Details"** (`application/problem+json`): `type`, `title`, `status`, `detail`, and extension members.

```python Errors.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


class DomainError(Exception):                                          # raised by the service layer, knows nothing about HTTP
    status = 400
    title = "Bad request"

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError):
    status, title = 404, "Resource not found"


class Conflict(DomainError):
    status, title = 409, "Conflict"


def problem(status: int, title: str, detail: str, request: Request, **extra):
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail, "instance": request.url.path, **extra}
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


app = FastAPI()


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):    # one place maps domain errors to HTTP
    return problem(exc.status, exc.title, exc.detail, request)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(part) for part in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return problem(422, "Validation failed", "one or more fields are invalid", request, errors=errors)


@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    return problem(exc.status_code, "HTTP error", str(exc.detail), request)


@app.exception_handler(Exception)
async def unexpected(request: Request, exc: Exception):                # last resort: never leak internals to the client
    return problem(500, "Internal server error", "something went wrong", request)


class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+$")
    age: int = Field(ge=18)


USERS = {"asha@example.com"}


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    if user.email in USERS:
        raise Conflict(f"{user.email} is already registered")
    USERS.add(user.email)
    return {"email": user.email}


@app.get("/users/{email}")
def get_user(email: str):
    if email not in USERS:
        raise NotFound(f"no user {email}")
    return {"email": email}


@app.get("/boom")
def boom():
    raise RuntimeError("secret database password in the message")


client = TestClient(app, raise_server_exceptions=False)
for response in (client.post("/users", json={"email": "bad", "age": 5}), client.post("/users", json={"email": "asha@example.com", "age": 30}),
                 client.get("/users/zed@example.com"), client.get("/nothing"), client.get("/boom")):
    print(response.status_code, response.headers["content-type"], response.json())
```

```output
```

Design rules for errors:

1. **Domain code raises domain exceptions**; **one handler** maps them to HTTP. Services stay free of `HTTPException`, so a CLI or worker can reuse them.
2. **Same shape everywhere**, including validation failures and 404s from the router, so clients write one error parser.
3. **Never leak internals** in 500 responses (stack traces, SQL, paths); log the details server-side with a correlation ID the client can quote.
4. **Be precise with the status**: 400 malformed request, 401 not authenticated, 403 not allowed, 404 not found, 409 conflict with current state, 422 well-formed but invalid, 429 too many requests.

??  What is the difference between 401 and 403?
=> `401 Unauthorized` means the request lacks valid credentials (authenticate and retry); `403 Forbidden` means the caller is authenticated but not allowed to do this. Returning 404 instead of 403 for resources a user must not even know about is a deliberate choice that avoids revealing their existence.
??  Why raise domain exceptions and map them in one handler?
=> The service layer stays independent of HTTP (reusable from jobs and CLIs), the mapping lives in one place, and the error format is consistent. Scattering `HTTPException` through business logic couples the layers and produces inconsistent responses.
??  What is Problem Details (RFC 9457)?
=> A standard JSON error format (`application/problem+json`) with `type`, `title`, `status`, `detail` and `instance`, plus extension members such as a list of field errors. A single machine-readable format makes clients and monitoring simpler.

## Pagination, Filtering and Sorting

Never return an unbounded list. Two pagination styles dominate:

| Style | Request | Pros | Cons |
| --- | --- | --- | --- |
| **Offset / limit (page)** | `?page=3&size=20` | Simple; jump to any page; total count | Slow for large offsets; rows shift while paging |
| **Cursor (keyset)** | `?limit=20&after=<opaque cursor>` | Stable and fast on large, changing data | No random access; the cursor must be opaque and signed |

```python Pagination.py
import base64
import json
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.testclient import TestClient

app = FastAPI()
ITEMS = [{"id": i, "name": f"item-{i:02d}", "price": 10 + i % 5, "category": "pen" if i % 2 else "ink"} for i in range(1, 26)]


class SortField(str, Enum):
    id = "id"
    price = "price"
    name = "name"


@app.get("/items")
def list_items(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
    category: Annotated[str | None, Query(max_length=20)] = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    sort: SortField = SortField.id,
    descending: bool = False,
    tag: Annotated[list[str] | None, Query()] = None,                     # repeated parameter: ?tag=a&tag=b
):
    rows = [i for i in ITEMS if (category is None or i["category"] == category) and (min_price is None or i["price"] >= min_price)]
    rows.sort(key=lambda i: (i[sort.value], i["id"]), reverse=descending)
    total, start = len(rows), (page - 1) * size
    return {"items": rows[start:start + size], "page": page, "size": size, "total": total, "pages": -(-total // size), "tags": tag}


def encode_cursor(last_id: int) -> str:                                    # opaque to clients: they must not parse it
    return base64.urlsafe_b64encode(json.dumps({"after": last_id}).encode()).decode()


def decode_cursor(cursor: str) -> int:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()))["after"]


@app.get("/feed")
def feed(limit: Annotated[int, Query(ge=1, le=20)] = 5, after: str | None = None):
    last_id = decode_cursor(after) if after else 0
    rows = [i for i in ITEMS if i["id"] > last_id][: limit + 1]            # fetch one extra row to know if there is a next page
    has_more = len(rows) > limit
    rows = rows[:limit]
    return {"items": [r["id"] for r in rows], "next": encode_cursor(rows[-1]["id"]) if has_more else None}


client = TestClient(app)
page = client.get("/items?page=2&size=10&sort=price&descending=true&category=pen").json()
print(page["total"], page["pages"], [i["id"] for i in page["items"]], page["page"])
print(client.get("/items?sort=colour").status_code, client.get("/items?size=500").status_code, client.get("/items?tag=a&tag=b&size=1").json()["tags"])

first = client.get("/feed?limit=10").json()
second = client.get(f"/feed?limit=10&after={first['next']}").json()
third = client.get(f"/feed?limit=10&after={second['next']}").json()
print(first["items"][-1], second["items"], third["items"], third["next"])
```

```output
```

Cursor pagination uses **keyset** logic (`WHERE id > :last_id ORDER BY id LIMIT n`), which uses the index and does not slow down on page 10,000, unlike `OFFSET 200000`. Fetching `limit + 1` rows tells you whether a next page exists without a separate count query.

!warning Always cap and validate :: `size` needs an upper bound (`le=50`), sort fields should come from an **enum** or allow-list (never put a client string into `ORDER BY`), and filters must be parameters, not string-built SQL. These are the classic sources of denial-of-service and injection bugs in list endpoints.

??  Why is cursor pagination better than offset pagination for large tables?
=> `OFFSET n` makes the database walk and discard n rows, so deep pages get slower, and rows inserted or deleted while a client pages cause duplicates or skips. Keyset pagination seeks directly to the position using an index (`WHERE id > last`) and is stable under changes.
??  How do you let clients choose the sort order safely?
=> Accept an enum or an allow-listed field name and a direction, and map them to column objects in code. Never interpolate the client's string into an `ORDER BY` clause.

## Forms, Files and Background Work

```python FormsFiles.py
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient

app = FastAPI()
SENT, SEEN_KEYS = [], {}
MAX_BYTES = 1_000
ALLOWED = {"image/png", "text/plain"}


def send_email(to: str, subject: str):                                  # runs AFTER the response has been sent
    SENT.append((to, subject))


@app.post("/signup")
def signup(email: Annotated[str, Form()], password: Annotated[str, Form(min_length=8)], tasks: BackgroundTasks):
    tasks.add_task(send_email, email, "Welcome!")                       # fast for the client, work happens afterwards
    return {"email": email}


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()], title: Annotated[str, Form()] = "untitled"):
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"unsupported type {file.content_type}")
    data = await file.read(MAX_BYTES + 1)                                # never read an unbounded upload fully
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "file too large")
    return {"filename": file.filename, "type": file.content_type, "size": len(data), "title": title}


@app.post("/payments", status_code=201)
def pay(amount: int, idempotency_key: Annotated[str, Header()]):
    if idempotency_key in SEEN_KEYS:                                     # a retry of the same request: replay the first result
        return SEEN_KEYS[idempotency_key]
    result = {"payment_id": len(SEEN_KEYS) + 1, "amount": amount}
    SEEN_KEYS[idempotency_key] = result
    return result


client = TestClient(app)
print(client.post("/signup", data={"email": "a@x.com", "password": "longenough"}).json(), SENT)
print(client.post("/signup", data={"email": "a@x.com", "password": "short"}).status_code)
print(client.post("/upload", files={"file": ("note.txt", b"hello", "text/plain")}, data={"title": "greeting"}).json())
print(client.post("/upload", files={"file": ("x.exe", b"MZ", "application/octet-stream")}).status_code,
      client.post("/upload", files={"file": ("big.txt", b"x" * 2000, "text/plain")}).status_code)
first = client.post("/payments?amount=500", headers={"Idempotency-Key": "abc-1"}).json()
retry = client.post("/payments?amount=500", headers={"Idempotency-Key": "abc-1"}).json()
print(first == retry, len(SEEN_KEYS))
```

```output
```

- **`Form()`** reads `application/x-www-form-urlencoded` or multipart fields; **`UploadFile`** streams the upload to a spooled temp file (not memory). Validate **size, type and name** (never trust the filename or the client's content type: check magic bytes for sensitive cases, store under a generated name, outside the web root).
- **`BackgroundTasks`** runs short work after the response (sending an email, writing an audit row). It runs **in the same process**: if the process dies the task is lost, so anything important or slow belongs in a real queue (Celery, Arq, a message broker; later in this tree).
- An **idempotency key** header lets clients safely retry a non-idempotent `POST` (payments, orders): store the key with the first result and replay it.

??  When is `BackgroundTasks` enough and when do you need Celery?
=> `BackgroundTasks` suits short, best-effort work tied to a request (send a welcome email). Use a task queue when work is long, must survive restarts, needs retries, scheduling, rate control or running on other machines, since background tasks live and die with the web process.
??  What is an idempotency key and how does a server implement it?
=> A client-generated unique key sent with a non-idempotent request. The server stores the key with the response (atomically with the side effect); if the same key arrives again it returns the stored response instead of repeating the action. It makes retries after timeouts safe.

## Cross-Cutting HTTP: CORS, Caching, Compression and Rate Limits

```python HttpConcerns.py
import hashlib
import json

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"], allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"],
                   allow_credentials=True, max_age=600)                  # list origins explicitly; never "*" together with credentials
app.add_middleware(GZipMiddleware, minimum_size=500)

DOC = {"id": 1, "title": "Handbook", "body": "text " * 400}


@app.get("/docs/1")
def get_doc(request: Request, response: Response):
    etag = '"' + hashlib.sha256(json.dumps(DOC, sort_keys=True).encode()).hexdigest()[:16] + '"'
    if request.headers.get("if-none-match") == etag:                     # the client already has this version
        return Response(status_code=304, headers={"ETag": etag})
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=60"
    return DOC


class RateLimiter:                                                       # a fixed-window limiter as a dependency
    def __init__(self, limit: int):
        self.limit, self.hits = limit, {}

    def __call__(self, request: Request, response: Response):
        key = request.client.host
        self.hits[key] = self.hits.get(key, 0) + 1
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - self.hits[key]))
        if self.hits[key] > self.limit:
            raise HTTPException(429, "too many requests", headers={"Retry-After": "30"})


limiter = RateLimiter(limit=2)


@app.get("/search", dependencies=[Depends(limiter)])
def search(q: str):
    return {"q": q}


client = TestClient(app)
preflight = client.options("/search", headers={"Origin": "https://app.example.com", "Access-Control-Request-Method": "GET"})
print(preflight.status_code, preflight.headers["access-control-allow-origin"], preflight.headers["access-control-allow-methods"])
blocked = client.options("/search", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
print(blocked.status_code, "access-control-allow-origin" in blocked.headers)

first = client.get("/docs/1", headers={"Accept-Encoding": "gzip"})
print(first.status_code, first.headers["content-encoding"], first.headers["cache-control"])
again = client.get("/docs/1", headers={"If-None-Match": first.headers["etag"]})
print(again.status_code, again.content)

print([client.get("/search?q=x").status_code for _ in range(3)], client.get("/search?q=x").headers.get("retry-after"))
```

```output
```

| Concern | Tool | Remember |
| --- | --- | --- |
| **CORS** | `CORSMiddleware` | Browsers only. List allowed origins explicitly; `"*"` cannot be combined with credentials; preflight `OPTIONS` requests are answered by the middleware |
| **Caching** | `ETag` + `If-None-Match` (304), `Cache-Control` | Conditional requests save bandwidth and let clients revalidate cheaply |
| **Compression** | `GZipMiddleware` | Worth it for large JSON; a reverse proxy often does it instead |
| **Rate limiting** | Dependency, or at the gateway / reverse proxy / Redis | In-memory counters are per process: use Redis (atomic `INCR` + `EXPIRE`) when you run several workers |
| **Versioning** | `/v1/...` in the path, or a header | Version only for breaking changes; keep old versions working and announce a deprecation date |

!tip OpenAPI is part of the product :: Fill in `summary`, `description`, `tags`, `responses={404: {"model": ProblemDetail}}` and examples (`Field(examples=[...])`, `model_config = {"json_schema_extra": {...}}`). A good schema generates a client SDK, drives contract tests and cuts support questions. Treat a change in `openapi.json` in a pull request like a change in a public interface.

??  Why does CORS exist and how do you configure it correctly?
=> Browsers block a page from reading responses of another origin unless that server opts in through CORS headers. Configure `CORSMiddleware` with an explicit list of allowed origins, methods and headers; do not use `*` with credentials. It protects users' browsers, not your API: non-browser clients ignore it.
??  How do ETags reduce load?
=> The server sends a validator (`ETag`) with a resource; the client sends it back in `If-None-Match`; if the resource is unchanged the server replies `304 Not Modified` with no body. The work to produce the body and transfer it is skipped.
??  Why is an in-memory rate limiter wrong for a multi-worker deployment?
=> Each worker process has its own counters, so the effective limit is multiplied by the number of workers and resets on restart. Keep the counters in shared storage (Redis with atomic increments and expiry) or enforce limits at a gateway.

## REST API Design Checklist

!cheat Design rules that survive code review ::
- **Nouns, plural, lower-case, hyphenated**: `/orders/42/items`, not `/getOrder?id=42`. Nest only one level; use filters for the rest.
- **Methods mean things**: `GET` safe and cacheable, `POST` create (not idempotent), `PUT` replace, `PATCH` partial, `DELETE` remove.
- **Status codes**: 200, 201 + `Location`, 204, 400, 401, 403, 404, 409, 422, 429, 500, 503.
- **Three models per resource** (create, update, read); never expose database models or secrets.
- **One error format** (Problem Details) for every failure, with a correlation ID.
- **Paginate every list**, cap the size, allow-list sort and filter fields.
- **Idempotency keys** for non-idempotent POSTs that clients will retry.
- **Version in the path** only for breaking changes; deprecate with a header and a date.
- **Document with OpenAPI**; treat the schema as a contract and test it.
- **Security basics**: HTTPS only, authenticate every request, authorise every resource, validate every input (Part 4).
!end

??  How would you design an endpoint to cancel an order?
=> Model the action as a state transition: `POST /orders/42/cancellation` (creates a cancellation) or `PATCH /orders/42` with `{"status": "cancelled"}`, validating that the transition is allowed (409 if the order has shipped). Return the updated order, make it idempotent (cancelling a cancelled order returns the same state), and record who and why.
??  Why shouldn't a REST API expose database tables one-to-one?
=> The API is a public contract that should model the domain and stay stable, while tables change with the implementation. One-to-one exposure leaks internals (surrogate keys, join tables, audit columns), couples clients to the schema and encourages chatty or insecure access.
