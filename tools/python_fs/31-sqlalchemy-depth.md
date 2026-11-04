@part py-web-8 | FastAPI Beyond Basics · Part 2: SQLAlchemy in Depth | web
## The Session: Lifecycle, Identity Map and Unit of Work

Every ORM object is in exactly one **state** relative to a session, and knowing the states explains most "why did it not save?" and "DetachedInstanceError" questions.

| State | Meaning | How you get there |
| --- | --- | --- |
| **Transient** | A plain Python object, not in any session | `Account(...)` |
| **Pending** | Added to a session, no row yet | `session.add(obj)` |
| **Persistent** | Has a row and belongs to a session (the identity map holds it) | after `flush`, or loaded by a query |
| **Detached** | Has a row, but its session is closed | `session.close()`, `session.expunge(obj)` |

```python SessionLifecycle.py
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str]
    balance: Mapped[int]


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)


def state(obj):
    s = inspect(obj)
    return next(name for name in ("transient", "pending", "persistent", "detached") if getattr(s, name))


account = Account(owner="asha", balance=100)
print(state(account))

with Session(engine) as session:                                  # default: autoflush=True, expire_on_commit=True
    session.add(account)
    print(state(account), len(session.new), len(session.dirty))
    session.flush()                                               # INSERT is sent; the transaction is still open
    print(state(account), account.id)

    account.balance += 50                                         # the unit of work notices attribute changes
    print("dirty:", account in session.dirty, session.is_modified(account))
    print("sum seen by the query:", session.scalar(select(func.sum(Account.balance))))   # autoflush sent the UPDATE first

    print("same object per row:", session.get(Account, account.id) is account)
    session.commit()                                              # expire_on_commit: attributes are reloaded on next access
    print("expired after commit:", "balance" in inspect(account).unloaded)
    print("reloaded:", account.balance)

    session.expunge(account)                                      # detach one object without closing the session
    print(state(account))

with Session(engine) as session:
    stale = session.get(Account, 1)
    session.commit()                                              # expires the attributes
detached = stale
try:
    print(detached.balance)                                       # the session is closed and the value is expired
except DetachedInstanceError:
    print("DetachedInstanceError: the session closed before the attribute was loaded")

with Session(engine) as session:                                  # merge copies a detached object's state into this session
    attached = session.merge(Account(id=1, owner="asha", balance=999))
    session.commit()
    print(attached.balance, state(attached))
```

```output
```

Why these behaviours exist, and what they cost you:

1. **Identity map**: one object per row per session, so `session.get(...)` twice is one query, and two references to the same row are the same Python object (no inconsistent copies).
2. **Unit of work and autoflush**: changes are tracked on the objects and sent as one batch at `flush`; before a query the session **autoflushes** so the query sees pending changes. This is correct but can surprise you with an unexpected `IntegrityError` at query time.
3. **`expire_on_commit=True`** (the default) clears loaded attributes at commit so you never read stale data; the cost is an extra `SELECT` on the next access, and `DetachedInstanceError` if the session is gone. Web apps that serialise after commit usually set `expire_on_commit=False`.
4. **Session scope = unit of work = request**. Do not keep a session in a global or share it across threads or tasks: it holds state and a connection.

??  What does "autoflush" do and when is it a problem?
=> Before executing a query the session flushes pending changes so the query reflects them. It makes code behave intuitively, but a flush can raise a constraint error (for example a unique violation) at an unexpected place, or cost time in loops that query repeatedly; `session.no_autoflush` disables it for a block.
??  What is a `DetachedInstanceError`?
=> You accessed an unloaded or expired attribute (usually a lazy relationship, or any attribute after `commit()` with `expire_on_commit=True`) on an object whose session is closed. Load what you need inside the session (eager loading), disable expiry on commit, or convert to a schema before the session closes.
??  Difference between `session.add`, `session.merge` and `session.refresh`?
=> `add` makes a new (or detached) object part of the session; `merge` copies the state of a possibly detached object onto the session's own persistent instance for that primary key and returns it; `refresh` reloads an object's attributes from the database, discarding in-memory changes.

## Loading Strategies and Query Performance

Performance work on an ORM is **counting queries, reading plans and moving work into the database**.

```python QueryPerformance.py
import time

from sqlalchemy import Index, create_engine, delete, exists, func, insert, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, defer, load_only, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int]
    status: Mapped[str]
    total: Mapped[int]
    notes: Mapped[str]


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
rows = [{"customer_id": i % 500, "status": "paid" if i % 3 else "new", "total": i, "notes": "x" * 200} for i in range(20_000)]

# ORM objects versus bulk Core inserts
started = time.perf_counter()
with Session(engine) as session:
    session.add_all([Order(**row) for row in rows[:5_000]])        # one object per row: identity map, change tracking, flush ordering
    session.commit()
orm_time = time.perf_counter() - started

started = time.perf_counter()
with engine.begin() as connection:
    connection.execute(insert(Order), rows[5_000:])                # one executemany: no objects at all
bulk_time = time.perf_counter() - started
print("Core executemany is at least 3x faster per row:", (orm_time / 5_000) > 3 * (bulk_time / 15_000))

with Session(engine) as session:
    print(session.scalar(select(func.count()).select_from(Order)))

    # Fetch only what you need
    full = session.scalars(select(Order).where(Order.id == 1)).one()
    slim = session.scalars(select(Order).options(load_only(Order.id, Order.total)).where(Order.id == 2)).one()
    deferred = session.scalars(select(Order).options(defer(Order.notes)).where(Order.id == 3)).one()
    print("notes loaded:", "notes" in full.__dict__, "notes" in slim.__dict__, "notes" in deferred.__dict__)
    pairs = session.execute(select(Order.customer_id, func.sum(Order.total)).group_by(Order.customer_id).order_by(Order.customer_id).limit(2)).all()
    print("aggregate in SQL, not in Python:", [tuple(p) for p in pairs])
    print("EXISTS instead of count:", session.scalar(select(exists().where(Order.customer_id == 7, Order.status == "new"))))

    # Stream big results instead of materialising them
    seen = 0
    for chunk in session.execute(select(Order.id).execution_options(yield_per=1_000)).partitions():
        seen += len(chunk)
    print("streamed rows:", seen)


def plan(sql):
    with engine.connect() as connection:
        return " / ".join(row[-1] for row in connection.execute(text("EXPLAIN QUERY PLAN " + sql)))


query = "SELECT id FROM orders WHERE customer_id = 7 AND status = 'paid'"
print("before:", plan(query))
Index("ix_orders_customer_status", Order.customer_id, Order.status).create(engine)
print("after: ", plan(query))
```

```output
```

The recurring techniques:

| Problem | Fix |
| --- | --- |
| N+1 queries | `selectinload` / `joinedload`; assert query counts in tests |
| Loading whole rows for two columns | `load_only(...)`, `defer(...)`, or select columns directly (`select(Order.id, Order.total)`) |
| Aggregating in Python | `func.sum`, `group_by`, window functions: let the database do it |
| `count()` just to test existence | `select(exists().where(...))` |
| Loading millions of rows | `yield_per` / server-side cursors; process in chunks |
| Slow inserts and updates | Core `insert()` with a list (executemany), `update().where()` set-based statements, PostgreSQL `COPY` |
| Slow filter or sort | Read the plan (`EXPLAIN` / `EXPLAIN ANALYZE`), add the right composite index (column order matters: equality columns first), avoid functions on indexed columns (`WHERE lower(email) = ...` needs an expression index) |
| Deep `OFFSET` | Keyset pagination (`WHERE id > :last ORDER BY id LIMIT n`) |

The plan lines above are SQLite's wording and change with the SQLite version; PostgreSQL's `EXPLAIN (ANALYZE, BUFFERS)` shows real timings and is the tool to learn: look for **sequential scans on big tables, row-estimate errors and sorts that spill to disk**.

??  How do you find out why a SQLAlchemy-backed endpoint is slow?
=> Log or count the statements per request (`echo=True`, an event listener, or tracing), look for N+1 patterns and repeated queries, take the slowest statements to `EXPLAIN ANALYZE`, check indexes and row estimates, and only then consider ORM overhead (object creation, large result sets). Fix at the right level: query shape first, indexes second, caching third.
??  When should you bypass the ORM for writes?
=> For bulk loads and set-based changes: Core `insert()` with many rows, `update().where(...)`, `COPY` on PostgreSQL. The ORM creates an object per row and tracks it, which costs memory and time that bulk operations do not need.
??  What does a composite index `(customer_id, status)` help and not help?
=> It serves queries that filter on `customer_id`, or on `customer_id` and `status` (the leftmost columns); it does not help a filter on `status` alone, and functions applied to indexed columns usually prevent its use. Put equality columns before range columns.

## Advanced Mapping: Inheritance, Hybrids, Constraints and JSON

```python Mapping.py
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import CheckConstraint, JSON, String, UniqueConstraint, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:                                                 # shared columns: a mixin, not inheritance of tables
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime(2026, 11, 4, tzinfo=timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)  # soft delete: a nullable marker instead of DELETE

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @is_deleted.expression
    def is_deleted(cls):                                              # the same name works in Python AND in SQL expressions
        return cls.deleted_at.is_not(None)


class Status(str, Enum):
    draft = "draft"
    published = "published"


class Content(TimestampMixin, Base):                                   # single-table inheritance: one table, a discriminator column
    __tablename__ = "content"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(100))
    status: Mapped[Status] = mapped_column(default=Status.draft)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    price: Mapped[int | None]
    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "content"}
    __table_args__ = (UniqueConstraint("kind", "title", name="uq_kind_title"), CheckConstraint("price IS NULL OR price >= 0", name="ck_price_non_negative"))


class Article(Content):
    __mapper_args__ = {"polymorphic_identity": "article"}


class Video(Content):
    __mapper_args__ = {"polymorphic_identity": "video"}


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([Article(title="ASGI", meta={"tags": ["web", "async"]}), Video(title="ASGI", price=5), Article(title="Old news")])
    session.commit()
    old = session.scalars(select(Article).where(Article.title == "Old news")).one()
    old.deleted_at = datetime(2026, 11, 5, tzinfo=timezone.utc)
    session.commit()

    print([(type(c).__name__, c.title) for c in session.scalars(select(Content).order_by(Content.id))])    # polymorphic loading
    print([a.title for a in session.scalars(select(Article).where(~Article.is_deleted))])                   # hybrid used in SQL
    print(old.is_deleted, session.scalars(select(Article)).first().meta, Status.draft in {c.status for c in session.scalars(select(Content))})

    for bad in (Article(title="ASGI"), Video(title="neg", price=-1)):                                       # constraints are enforced by the database
        session.add(bad)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            print("IntegrityError:", str(error.orig).split(":")[0], "|", str(error.orig).split(":")[-1].strip())
```

```output
```

Choices to discuss in a design review:

- **Inheritance**: *single-table* (all subclasses in one table, nullable columns; simple and fast, the usual pick), *joined-table* (a table per class joined by key; normalised, joins on every load), *concrete* (separate tables; rarely worth it). Often a `kind` column and composition beat a deep class hierarchy.
- **Soft delete** (a `deleted_at` marker) keeps history and allows undo, but every query must filter it (put it in a default `where`, a view, or a session event) and unique constraints must account for it.
- **Constraints belong in the database** (`UNIQUE`, `CHECK`, `NOT NULL`, foreign keys): application validation can be bypassed by a second service, a script or a race, while the constraint cannot.
- **`JSON` columns** suit flexible, rarely queried attributes; on PostgreSQL use `JSONB` with GIN indexes if you query inside it. Anything you filter on regularly deserves a real column.
- **Hybrid properties** define a computed attribute once for both Python instances and SQL expressions.

??  Single-table versus joined-table inheritance?
=> Single-table stores every subclass in one table with a discriminator column: fast, no joins, but subclass-specific columns are nullable. Joined-table gives each subclass its own table linked by primary key: normalised and strict, but each load needs a join. Use single-table unless subclasses have many distinct columns.
??  Why enforce uniqueness with a database constraint and not just a check in code?
=> Two concurrent requests can both pass an application-level "does it exist?" check and both insert (a race). A unique constraint makes the database the single arbiter, and the loser gets an `IntegrityError` you can translate to a 409.
??  What is a hybrid property?
=> An attribute defined on the class that works on instances (Python logic) and in queries (a SQL expression), so `Article.is_deleted` can be used both as `obj.is_deleted` and in `select(...).where(Article.is_deleted)`.

## Transactions, Isolation and Concurrency

Two requests updating the same row at once is where correctness bugs live. Know the tools in increasing strength:

| Technique | How | Trade-off |
| --- | --- | --- |
| **Atomic SQL** | `UPDATE counters SET value = value + 1` | Best for counters and balances: no read-modify-write |
| **Optimistic locking** | A version column; `UPDATE ... WHERE id = ? AND version = ?`; zero rows means someone changed it | No locks held; the loser retries or gets a 409 |
| **Pessimistic locking** | `SELECT ... FOR UPDATE` (`with_for_update()`) | Serialises access; use for scarce resources; risk of waiting and deadlocks |
| **Constraints** | Unique and check constraints | The database refuses invalid states even under races |
| **Higher isolation** | `SERIALIZABLE` / `REPEATABLE READ` + retry on serialization failure | Strongest; needs retry logic |

```python Concurrency.py
import pathlib

from sqlalchemy import create_engine, select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import StaleDataError


class Base(DeclarativeBase):
    pass


class Counter(Base):
    __tablename__ = "counters"
    name: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(default=0)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str]
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}                      # SQLAlchemy adds "AND version = ?" to every UPDATE


engine = create_engine(f"sqlite:///{pathlib.Path('concurrency.db').resolve()}")       # a file: two sessions get two real connections
Base.metadata.create_all(engine)
with Session(engine) as s, s.begin():
    s.add_all([Counter(name="hits", value=0), Document(id=1, body="v1")])

# 1. The lost update: both sessions read 0, both write 1
a, b = Session(engine), Session(engine)
ca, cb = a.get(Counter, "hits"), b.get(Counter, "hits")
ca.value = ca.value + 1
a.commit()
cb.value = cb.value + 1
b.commit()
print("read-modify-write result:", Session(engine).get(Counter, "hits").value, "(two increments, one lost)")

# 2. The atomic version cannot lose updates
for _ in range(2):
    with Session(engine) as s, s.begin():
        s.execute(update(Counter).where(Counter.name == "hits").values(value=Counter.value + 1))
print("atomic UPDATE result:", Session(engine).get(Counter, "hits").value)

# 3. Optimistic locking: the second writer is told it is stale
a, b = Session(engine), Session(engine)
da, db = a.get(Document, 1), b.get(Document, 1)
da.body = "edited by A"
a.commit()
db.body = "edited by B"
try:
    b.commit()
except StaleDataError:
    b.rollback()
    print("StaleDataError: B must reload and retry; document is now", Session(engine).get(Document, 1).body, "version", Session(engine).get(Document, 1).version)

# 4. Upsert: insert or update in one statement, safe under concurrency
for _ in range(3):
    with Session(engine) as s, s.begin():
        stmt = sqlite_insert(Counter).values(name="visits", value=1)
        s.execute(stmt.on_conflict_do_update(index_elements=["name"], set_={"value": Counter.value + 1}))
print("upsert result:", Session(engine).get(Counter, "visits").value)
```

```output
```

On PostgreSQL the same upsert is `postgresql.insert(...).on_conflict_do_update(...)`, `with_for_update()` takes a row lock, and a `SERIALIZABLE` transaction can fail with a *serialization failure* that your code must **retry**. Whatever the mechanism, the rule is the same: **a check followed by a write is a race unless the database makes it atomic**.

!interview Optimistic or pessimistic locking? :: Optimistic suits low-contention data (editing a profile, a document): no locks, conflicts are rare and reported as 409 or retried. Pessimistic suits high-contention scarce resources (the last seat, inventory decrement) where retries would thrash: lock the row, or better, use an atomic conditional `UPDATE ... SET stock = stock - 1 WHERE stock > 0` and check the affected row count.

??  How do you prevent lost updates in a web application?
=> Use atomic SQL for counters and balances, optimistic locking with a version column (or ETag with `If-Match`) for edited records, row locks or conditional updates for scarce resources, and database constraints for invariants. Never read, modify in Python and write back without one of these.
??  What does `ON CONFLICT DO UPDATE` give you?
=> An atomic insert-or-update on a unique key in one statement, so concurrent requests cannot both insert the same key or lose an increment. It is the right way to implement counters, idempotent writes and "get or create".
??  What happens on a serialization failure under `SERIALIZABLE` isolation?
=> The database aborts one of the conflicting transactions with an error (PostgreSQL SQLSTATE 40001). The application must catch it and **retry the whole transaction**, so transactions must be short and free of external side effects.

## Engines, Connection Pools and Operations

An **engine** owns a **pool** of database connections. Opening a PostgreSQL connection costs milliseconds and server memory, so the pool reuses them; its limits are a capacity decision.

```python Pooling.py
import pathlib

from sqlalchemy import create_engine, text
from sqlalchemy.exc import TimeoutError as PoolTimeout
from sqlalchemy.pool import QueuePool

engine = create_engine(
    f"sqlite:///{pathlib.Path('pool.db').resolve()}",
    poolclass=QueuePool,
    pool_size=2,              # connections kept open
    max_overflow=1,           # extra connections allowed under burst, closed when returned
    pool_timeout=0.2,         # seconds to wait for a free connection before failing
    pool_pre_ping=True,       # test a connection before use: survives database restarts and idle disconnects
    pool_recycle=1800,        # replace connections older than this (cloud proxies drop idle ones)
)

held = [engine.connect() for _ in range(3)]                          # 2 pool + 1 overflow
print(engine.pool.status())
try:
    engine.connect()                                                   # a fourth request has to wait, then fails
except PoolTimeout as error:
    print("pool exhausted:", str(error).split(" (")[0])
held.pop().close()                                                     # returning a connection frees a slot
with engine.connect() as connection:
    print("connection works again:", connection.execute(text("SELECT 1")).scalar())
for connection in held:
    connection.close()
```

```output
```

Sizing and operating rules:

1. **The budget is the database's `max_connections`** (PostgreSQL default 100, and each connection costs memory). Total connections = `replicas × workers × (pool_size + max_overflow)` and must stay **below the limit** with headroom for migrations, admin tools and failover. A pooler such as **PgBouncer** (transaction mode) lets many app connections share few database connections.
2. **Pool size is not request concurrency.** A pool of 10 can serve 1,000 requests per second if each holds a connection for 5 ms. Big pools hide slow queries and overload the database; small pools queue (watch the wait time as a metric).
3. **A request should hold a connection only while it needs one.** Do not hold a session open across an HTTP call to another service.
4. **`pool_pre_ping=True`** costs one cheap round trip and turns "server closed the connection unexpectedly" into a transparent reconnect.
5. **Timeouts**: connection (`connect_timeout`), statement (`statement_timeout`), lock (`lock_timeout`), idle-in-transaction timeouts on the server. A query without a timeout can hold a worker forever.
6. **Serverless** (AWS Lambda) multiplies instances: use `NullPool` with a managed proxy (RDS Proxy, PgBouncer) instead of per-instance pools.
7. **Read replicas**: route read-only endpoints to a replica engine and accept replication lag (read your own writes from the primary).
8. **Observe it**: pool checked-out and overflow gauges, query duration histograms, slow-query logs (`log_min_duration_statement`), and `pg_stat_statements`.

??  How do you decide the pool size?
=> Start from the database's connection budget divided by the number of app processes, keep a margin, then measure: the pool is big enough if requests rarely wait for a connection and small enough that the database is not overloaded. Per-process size times processes must stay under `max_connections`.
??  Why use `pool_pre_ping`?
=> Connections sit idle in the pool and may have been closed by the server, a firewall or a failover. A pre-ping check discards dead connections and opens a new one, so a request does not fail with a stale-connection error.
??  What is PgBouncer for?
=> A connection pooler in front of PostgreSQL: many client connections are multiplexed over a small number of server connections, so hundreds of app processes (or serverless functions) can share a database without exhausting `max_connections`. In transaction mode, session-level features (prepared statements, advisory locks) need care.

## Advanced Queries: CTEs, Window Functions and PostgreSQL Features

SQLAlchemy's expression language covers modern SQL, so analytic queries do not need raw strings.

```python SqlFeatures.py
from sqlalchemy import Index, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str]
    rep: Mapped[str]
    amount: Mapped[int]


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
with Session(engine) as s, s.begin():
    s.add_all([Sale(region=r, rep=rep, amount=a) for r, rep, a in
               [("north", "asha", 500), ("north", "ravi", 700), ("north", "meera", 300), ("south", "john", 900), ("south", "lena", 400)]])

with Session(engine) as s:
    ranked = select(Sale.region, Sale.rep, Sale.amount,
                    func.rank().over(partition_by=Sale.region, order_by=Sale.amount.desc()).label("rank"),
                    func.sum(Sale.amount).over(partition_by=Sale.region).label("region_total")).subquery()
    top_two = s.execute(select(ranked.c.region, ranked.c.rep, ranked.c.rank, ranked.c.region_total).where(ranked.c.rank <= 2).order_by(ranked.c.region, ranked.c.rank)).all()
    print([tuple(r) for r in top_two])

    totals = select(Sale.region, func.sum(Sale.amount).label("total")).group_by(Sale.region).cte("totals")     # a common table expression
    above_average = s.execute(select(totals.c.region, totals.c.total).where(totals.c.total > select(func.avg(totals.c.total)).scalar_subquery())).all()
    print([tuple(r) for r in above_average])
```

```output
```

On PostgreSQL you would also reach for these (shown, not run here because they need a PostgreSQL server):

```python PostgreSQL features !skip
from sqlalchemy import ARRAY, String
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import Mapped, mapped_column


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)                  # binary JSON, indexable and queryable
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)           # native arrays

    __table_args__ = (Index("ix_products_attributes", "attributes", postgresql_using="gin"),)


stmt = (insert(Product).values(sku="P-1", attributes={"colour": "red"})
        .on_conflict_do_update(index_elements=["sku"], set_={"attributes": Product.attributes.op("||")({"seen": True})})
        .returning(Product.id))                                                     # RETURNING gives back generated values in one round trip
red_things = select(Product).where(Product.attributes["colour"].astext == "red")    # JSONB path query, served by the GIN index
tagged = select(Product).where(Product.tags.contains(["sale"]))                      # array containment
```

??  Why are window functions useful in application code?
=> They compute ranks, running totals, moving averages and "top N per group" inside the database in one pass, without pulling rows into Python or issuing a query per group. Many "for each group" loops disappear into one statement.
??  When do you choose JSONB over separate columns?
=> For flexible, sparsely populated, semi-structured attributes you rarely filter on; add a GIN index when you do query inside it. Fields you filter, join or constrain regularly deserve real columns with types and constraints.
