@part py-web-3 | FastAPI Basics · Part 3: Data Access with SQLAlchemy and Testing | web
## SQLAlchemy 2.0 ORM Basics

**SQLAlchemy** is Python's standard database toolkit. It has two layers: **Core** (SQL expressions and connections) and the **ORM** (classes mapped to tables, a **Session** that tracks objects and writes changes). It is the Python counterpart of JPA with Hibernate, with one big difference: SQL stays visible, and `select()` statements are ordinary Python objects you build and run.

| Concept | What it is | Java/Spring comparison |
| --- | --- | --- |
| **Engine** | Connection pool plus dialect for one database | `DataSource` |
| **Model** | A class that maps to a table (`DeclarativeBase` subclass) | `@Entity` |
| **Session** | A unit of work: identity map, change tracking, transaction | `EntityManager` / Hibernate `Session` |
| **`select()`** | A SQL SELECT built in Python | JPQL / Criteria |
| **Alembic** | Schema migrations | Flyway / Liquibase |

The examples use SQLite in memory so they run anywhere; switching to PostgreSQL changes only the URL (`postgresql+psycopg://user:pass@host/db`).

```python OrmBasics.py
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    year: Mapped[int | None]                                            # Optional annotation = nullable column
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime(2026, 11, 4, tzinfo=timezone.utc))
    author: Mapped[Author] = relationship(back_populates="books")


engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)                                        # CREATE TABLE ... (use Alembic in real projects)

with Session(engine) as session:
    asha = Author(name="Asha", books=[Book(title="Python Internals", year=2024), Book(title="Async Patterns", year=2026)])
    session.add(asha)
    print("before flush:", asha.id)                                     # the session has not written anything yet
    session.flush()                                                     # sends the INSERTs, still inside the transaction
    print("after flush:", asha.id, [b.id for b in asha.books])
    session.commit()                                                    # makes it permanent

with Session(engine) as session:
    book = session.scalars(select(Book).where(Book.title.like("Py%"))).one()          # a SELECT built in Python
    print(book.title, book.year, book.author.name)                                      # lazy load of the related Author
    same = session.get(Book, book.id)                                                   # get() uses the identity map: no new query
    print(same is book)

    book.year = 2025                                                                    # changes are tracked automatically
    session.commit()

    newest = session.execute(select(Book.title, Book.year).order_by(Book.year.desc()).limit(1)).first()
    stats = session.execute(select(func.count(Book.id), func.min(Book.year), func.max(Book.year))).one()
    print(newest, tuple(stats))
    print(session.scalar(select(func.count()).select_from(Book).where(Book.year >= 2025)))

    session.delete(session.get(Author, 1))                                              # cascade removes the books too
    session.commit()
    print(session.scalar(select(func.count()).select_from(Book)))
```

```output
```

The ideas to hold onto:

1. **A `Session` is a unit of work.** It tracks loaded objects (identity map: one Python object per row per session), records changes, and sends them on `flush`; `commit` ends the transaction. Always use it as a context manager so it closes.
2. **Nothing is written until `flush` or `commit`**, and `session.rollback()` discards the pending work.
3. **Queries are `select()` statements**: `session.scalars(stmt)` returns objects, `session.execute(stmt)` returns rows (tuples), `.one()`, `.first()`, `.all()` pick the shape.
4. **Annotations drive the schema**: `Mapped[int | None]` is nullable, `Mapped[int]` is `NOT NULL`, `mapped_column(...)` adds options (`primary_key`, `unique`, `index`, `ForeignKey`).
5. **Relationships** (`relationship`) give you object navigation; `back_populates` links both sides; `cascade="all, delete-orphan"` ties the lifecycle of children to the parent.

!interview Session, identity map and unit of work :: Within one session, loading the same row twice returns the **same Python object** (the identity map), and changes to that object are detected at flush time (the unit of work), which then emits INSERT, UPDATE and DELETE in the right dependency order. That is why a session must be **short-lived and not shared between threads or requests**: a long-lived session accumulates stale state.

??  What is the difference between `flush` and `commit`?
=> `flush` sends pending changes to the database inside the current transaction (so ids are assigned and constraints checked) but can still be rolled back; `commit` ends the transaction and makes the changes permanent (it flushes first).
??  What does `session.get(Model, id)` do that `select(...).where(id == ...)` does not?
=> It checks the session's identity map first and only queries the database if the object is not already loaded, so repeated gets of the same id in one session do not hit the database.
??  How is a SQLAlchemy `Session` different from a database connection?
=> A session is the ORM's unit of work and transaction scope; it borrows a connection from the engine's pool when it first needs one and returns it when the transaction ends. Sessions are cheap and per request; connections are pooled and shared.

## Relationships, Transactions and the N+1 Problem

The most common ORM performance bug is **N+1 queries**: one query for a list, then one more per row for a lazily loaded relationship. You cannot fix what you do not measure, so count the statements:

```python NPlusOne.py
from sqlalchemy import ForeignKey, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add_all([Author(name=f"author-{a}", books=[Book(title=f"book-{a}-{b}") for b in range(3)]) for a in range(10)])
    session.commit()

statements = []
event.listen(engine, "before_cursor_execute", lambda conn, cursor, statement, *args: statements.append(statement.split()[0]))


def count_queries(label, load):
    statements.clear()
    with Session(engine) as session:
        authors = load(session)
        total_books = sum(len(a.books) for a in authors)          # touching the relationship may trigger lazy loads
    print(f"{label:<12} {len(statements):>3} statements, {total_books} books")


count_queries("lazy (N+1)", lambda s: s.scalars(select(Author)).all())
count_queries("selectinload", lambda s: s.scalars(select(Author).options(selectinload(Author.books))).all())
count_queries("joinedload", lambda s: s.scalars(select(Author).options(joinedload(Author.books))).unique().all())
```

```output
```

| Strategy | SQL | Use when |
| --- | --- | --- |
| **Lazy** (default) | One query per object on first access | You rarely touch the relationship |
| **`selectinload`** | One extra `SELECT ... WHERE parent_id IN (...)` | A **collection** relationship (one-to-many): the usual best choice |
| **`joinedload`** | A `JOIN` in the same query | A single related object (many-to-one), small collections |
| **`raiseload`** | Raises if lazily accessed | A guard in tests or hot paths so N+1 cannot sneak back |

!tip Catch N+1 in tests :: Add a query counter like the one above to your test fixtures and assert an upper bound for important endpoints (`assert queries <= 3`). Or configure relationships with `lazy="raise"` in the model so any accidental lazy load fails loudly during development.

### Many-to-many and transactions

```python ManyToMany.py
from sqlalchemy import Column, ForeignKey, String, Table, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


book_tags = Table("book_tags", Base.metadata,
                  Column("book_id", ForeignKey("books.id"), primary_key=True),
                  Column("tag_id", ForeignKey("tags.id"), primary_key=True))


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    tags: Mapped[list[Tag]] = relationship(secondary=book_tags)


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as session:
    python, web = Tag(name="python"), Tag(name="web")
    session.add_all([Book(title="Flask", tags=[python, web]), Book(title="Pandas", tags=[python])])
    session.commit()
    print([(b.title, sorted(t.name for t in b.tags)) for b in session.scalars(select(Book).order_by(Book.title))])

# A transaction is all-or-nothing: an error inside the block rolls back everything done in it.
try:
    with Session(engine) as session, session.begin():                        # begin() commits on success, rolls back on error
        session.add(Book(title="Half-saved"))
        session.add(Tag(name="python"))                                      # violates the UNIQUE constraint
except IntegrityError as error:
    print("rolled back:", type(error.orig).__name__)

with Session(engine) as session:
    print(session.scalar(select(Book).where(Book.title == "Half-saved")))   # the first insert did not survive

# Savepoints let one part fail without losing the rest
with Session(engine) as session, session.begin():
    session.add(Book(title="Kept"))
    try:
        with session.begin_nested():
            session.add(Tag(name="web"))                                      # duplicate again
            session.flush()
    except IntegrityError:
        pass
with Session(engine) as session:
    print(session.scalar(select(Book.title).where(Book.title == "Kept")))
```

```output
```

??  What is the N+1 query problem and how do you fix it?
=> Loading a list with one query and then touching a lazy relationship on each of the N items issues N further queries. Fix it by eager loading: `selectinload` for collections, `joinedload` for single related objects, and verify the statement count in tests.
??  When do you choose `selectinload` over `joinedload`?
=> For one-to-many collections: `joinedload` multiplies parent rows by the number of children (a wide, duplicated result), while `selectinload` runs a second, simple `IN` query with no duplication. Use `joinedload` for many-to-one or one-to-one, where the join adds no extra rows.
??  What does `with session.begin():` give you?
=> A transaction scope: it commits when the block completes and rolls back if an exception escapes, so partial writes never remain. `begin_nested()` creates a savepoint for a sub-unit that may fail independently.

## Migrations with Alembic

In production you never call `create_all`: the schema changes over time, and every database (developer laptops, CI, staging, production) must reach the same state through **versioned, reviewed migration scripts**. **Alembic** is the standard tool: it compares your models with the database, generates a migration script, and applies it with a recorded version.

```bash Alembic workflow
alembic init migrations                              # once: creates alembic.ini and migrations/env.py (point env.py at Base.metadata)
alembic revision --autogenerate -m "add isbn to books"   # compare models and database, write migrations/versions/<id>_add_isbn.py
alembic upgrade head                                 # apply every pending migration
alembic downgrade -1                                 # undo the last one
alembic history --verbose                            # the chain of revisions
alembic current                                      # which revision this database is at
```

The migration engine is a normal Python API, so you can see exactly what autogenerate would do:

```python AlembicDemo.py
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, Integer, String, create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///:memory:")

with engine.begin() as connection:
    operations = Operations(MigrationContext.configure(connection))
    # What a hand-written migration's upgrade() contains:
    operations.create_table("books", Column("id", Integer, primary_key=True), Column("title", String(200), nullable=False))
    operations.add_column("books", Column("year", Integer))
    operations.create_index("ix_books_title", "books", ["title"])

print(sorted(c["name"] for c in inspect(engine).get_columns("books")), [i["name"] for i in inspect(engine).get_indexes("books")])


class Book(Base):                                                 # the NEW desired model: adds isbn, drops year
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    isbn: Mapped[str | None] = mapped_column(String(13))


with engine.connect() as connection:
    diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)    # the heart of --autogenerate
for operation in diff:
    print(operation[0], operation[2].name if hasattr(operation[2], "name") else operation[2], getattr(operation[3] if len(operation) > 3 else None, "name", ""))
```

```output
```

Rules for migrations that do not hurt in production:

1. **Review every autogenerated script**: autogenerate cannot detect renames (it sees a drop and an add, which loses data) or data migrations.
2. **Make them reversible** (`downgrade`) where possible, and test upgrade and downgrade in CI against a real PostgreSQL.
3. **Be backwards compatible**: deploy in steps ("expand then contract"): add the new nullable column, deploy code that writes both, backfill, switch reads, and only later drop the old column. Old and new application versions run side by side during a rolling deployment.
4. **Avoid long locks**: on large tables, adding an index (`CREATE INDEX CONCURRENTLY` on PostgreSQL), adding a column with a default, or rewriting a column can block traffic. Know your database's rules.
5. **One migration per change, committed with the code** that needs it.

??  Why use Alembic instead of `Base.metadata.create_all()`?
=> `create_all` only creates missing tables; it cannot alter existing ones and leaves no history. Alembic records versioned migrations that evolve an existing schema consistently across environments, can be reviewed and rolled back, and runs in the deployment pipeline.
??  What can't `--autogenerate` detect?
=> Column or table renames (it sees a drop plus an add, which would destroy data), changes in server-side defaults in some cases, data migrations, and some constraint or type changes. Always read and edit the generated script.
??  What does "expand and contract" mean for zero-downtime migrations?
=> Change the schema in compatible phases: first expand (add new columns or tables, keep the old ones), deploy code that works with both, migrate the data, then contract (remove the old structures) in a later release. Old and new code can run together during the rollout.

## Repository, Service and the FastAPI Integration

Putting the pieces together, the layers each have one job: **router** (HTTP), **service** (business rules), **repository** (queries), **session** (a unit of work per request).

```python LibraryApp.py
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship, selectinload, sessionmaker
from sqlalchemy.pool import StaticPool


# ---- persistence ----------------------------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")

    @property
    def author_name(self) -> str:                                          # a convenience the response schema reads
        return self.author.name


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)   # one in-memory DB shared by all threads
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


# ---- schemas ------------------------------------------------------------------------------------------------------
class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=80)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)                       # build the schema from ORM objects
    id: int
    title: str
    author_name: str                                                      # read from the Book.author_name property


# ---- repository and service ---------------------------------------------------------------------------------------
class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, title: str, author_name: str) -> Book:
        author = self.session.scalar(select(Author).where(Author.name == author_name)) or Author(name=author_name)
        book = Book(title=title, author=author)
        self.session.add(book)
        self.session.flush()                                              # assigns the id, keeps the transaction open
        return book

    def list(self, author: str | None, limit: int, offset: int) -> list[Book]:
        stmt = select(Book).options(selectinload(Book.author)).order_by(Book.id).limit(limit).offset(offset)
        if author:
            stmt = stmt.join(Author).where(Author.name == author)
        return list(self.session.scalars(stmt))

    def get(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id, options=[joinedload(Book.author)])      # load the author now: serialisation happens later

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(Book)) or 0


def get_session():
    with SessionLocal() as session:                                       # one session per request
        try:
            yield session
            session.commit()                                              # commit when the handler succeeded
        except Exception:
            session.rollback()
            raise


SessionDep = Annotated[Session, Depends(get_session)]


# ---- HTTP ---------------------------------------------------------------------------------------------------------
app = FastAPI()


@app.post("/books", status_code=201, response_model=BookOut)
def create_book(payload: BookIn, session: SessionDep):
    return BookRepository(session).add(payload.title, payload.author)            # an ORM object: from_attributes builds the schema


@app.get("/books", response_model=list[BookOut])
def list_books(session: SessionDep, author: str | None = None, limit: int = 10, offset: int = 0):
    return BookRepository(session).list(author, limit, offset)


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, session: SessionDep):
    book = BookRepository(session).get(book_id)
    if book is None:
        raise HTTPException(404, "book not found")
    return book


client = TestClient(app)
print(client.post("/books", json={"title": "Python Internals", "author": "Asha"}).json())
client.post("/books", json={"title": "Async Patterns", "author": "Asha"})
client.post("/books", json={"title": "Django Cookbook", "author": "Ravi"})
print([b["title"] for b in client.get("/books").json()], [b["title"] for b in client.get("/books?author=Asha").json()])
print(client.get("/books/2").json(), client.get("/books/99").status_code, client.get("/books?limit=1&offset=2").json())
with SessionLocal() as s:
    print(BookRepository(s).count(), s.scalar(select(func.count()).select_from(Author)))
```

```output
```

Details that matter in real services:

- **`sqlite://` with `StaticPool` and `check_same_thread=False`** is only for tests: in-memory SQLite lives in one connection, and FastAPI runs sync endpoints in worker threads. Production uses PostgreSQL with a real pool.
- **One session per request**, created in a `yield` dependency: commit if the handler returned, roll back if it raised, always close.
- **`expire_on_commit=False`** keeps objects usable after commit (so they can be serialised); otherwise accessing attributes after `commit()` triggers a refresh query.
- **Repositories hold queries**, services hold rules (not shown for brevity here; see the project part), routers hold HTTP. Do not return ORM objects directly from endpoints for public APIs: map them to schemas (`from_attributes=True` helps).

??  Why create one session per request?
=> A session tracks state and holds a connection while a transaction is open. Per-request sessions give each request an isolated unit of work, release connections promptly, and avoid sharing mutable session state across concurrent requests or threads.
??  What does `from_attributes=True` (formerly `orm_mode`) do?
=> It lets a Pydantic model be built from an object's attributes (an ORM instance) instead of only from dictionaries, so `Schema.model_validate(orm_object)` works. It is the bridge between SQLAlchemy models and response schemas.
??  Why not expose ORM models directly as API responses?
=> The ORM model is an internal persistence detail: it may contain relationships that trigger lazy loads (and N+1 queries or errors outside the session), sensitive columns, and fields you do not want to commit to publicly. A response schema is an explicit, stable contract.

## Async SQLAlchemy

With an async driver (`asyncpg` or `psycopg` for PostgreSQL, `aiosqlite` for SQLite) the whole data layer can await instead of blocking threads. The API mirrors the sync one with `AsyncSession` and `await`, with one new rule: **lazy loading cannot happen implicitly**, because attribute access cannot `await`.

```python AsyncOrm.py
import asyncio

from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import MissingGreenlet, StatementError
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")


async def main():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)               # DDL helpers are synchronous: run them via run_sync
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async with sessions() as session, session.begin():
        session.add(Author(name="Asha", books=[Book(title="Async Patterns"), Book(title="Python Internals")]))

    async with sessions() as session:
        author = (await session.scalars(select(Author))).one()
        try:
            print(author.books)                                           # implicit lazy load: impossible in async code
        except (MissingGreenlet, StatementError) as error:                 # SQLAlchemy 2.1 wraps it; 2.0 raised it directly
            print(type(getattr(error, "orig", error)).__name__ + ": lazy loading is not available in async sessions")
        print([b.title for b in await author.awaitable_attrs.books])     # explicit awaitable access (AsyncAttrs)

        authors = (await session.scalars(select(Author).options(selectinload(Author.books)))).all()
        print([(a.name, len(a.books)) for a in authors])                  # preferred: eager-load what you will use

    await engine.dispose()


asyncio.run(main())
```

```output
```

Use async SQLAlchemy when the rest of the request path is async and you want high concurrency on I/O; use the sync version with plain `def` endpoints (run in a thread pool) when your drivers or libraries are synchronous. Mixing both in one session is a bug. Async does not make queries faster: it frees the event loop while they run.

!warning The two classic async ORM mistakes :: (1) Accessing a lazy relationship (`MissingGreenlet`): eager-load with `selectinload` or use `awaitable_attrs`. (2) Sharing one `AsyncSession` between concurrent tasks (`asyncio.gather` on the same session): a session is not safe for concurrent use; give each task its own.

??  Why does `author.books` raise `MissingGreenlet` in async code?
=> Lazy loading would have to run a query inside a plain attribute access, which cannot `await`. Load relationships eagerly in the query (`selectinload`/`joinedload`), or explicitly await them through `awaitable_attrs`.
??  When should you choose the async ORM over the sync one?
=> When your stack is async end-to-end and you need many concurrent in-flight requests waiting on the database. For moderate load, sync SQLAlchemy in threads is simpler, mature, and entirely adequate. Choose based on measured concurrency needs, not fashion.

## Testing the Data Layer

Tests need a database that is **fast, isolated and realistic**. Two recipes give isolation. On SQLite, build a **fresh in-memory database per test** (cheap, and always correct). On PostgreSQL, build the schema once and run each test inside a **transaction that is rolled back**, with the session joined to it through a savepoint (faster for big schemas). In both cases you override the `get_session` dependency with the test's own session. The example runs `pytest` on a small project in a temporary folder and prints the real result.

```python PytestDb.py
import pathlib
import re
import subprocess
import sys

pathlib.Path("app.py").write_text('''\
from fastapi import Depends, FastAPI
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(200))


def make_engine(url="sqlite://"):
    return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)


engine = make_engine()
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_session():
    with SessionLocal() as session:
        yield session


app = FastAPI()


@app.post("/notes", status_code=201)
def add_note(text: str, session: Session = Depends(get_session)):
    note = Note(text=text)
    session.add(note)
    session.commit()
    return {"id": note.id, "text": note.text}


@app.get("/notes")
def list_notes(session: Session = Depends(get_session)):
    return [n.text for n in session.scalars(select(Note).order_by(Note.id))]
''')

pathlib.Path("conftest.py").write_text('''import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import Base, app, get_session, make_engine


@pytest.fixture
def session():
    engine = make_engine()                       # a brand-new in-memory database for EVERY test: slightly slower, always isolated
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session      # the endpoint uses the test's own session
    yield TestClient(app)
    app.dependency_overrides.clear()
''')

pathlib.Path("test_notes.py").write_text('''\
def test_create_and_list(client):
    assert client.post("/notes", params={"text": "first"}).status_code == 201
    assert client.get("/notes").json() == ["first"]


def test_each_test_starts_empty(client):
    assert client.get("/notes").json() == []          # the previous test's note is gone: each test has its own database


def test_session_fixture_sees_api_writes(client, session):
    client.post("/notes", params={"text": "shared"})
    from sqlalchemy import func, select
    from app import Note
    assert session.scalar(select(func.count()).select_from(Note)) == 1
''')

run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "--tb=short", "-W", "ignore"], capture_output=True, text=True)
print(re.sub(r" in \d+\.\d+s", "", run.stdout).strip())
```

```output
```

!cheat Data-layer testing checklist ::
- **Fast unit tests** for services with fake repositories (a dict-backed class): no database at all.
- **Integration tests** for repositories against a real engine: SQLite for speed, **PostgreSQL in a container (Testcontainers)** for fidelity, since SQL dialects, constraints, JSON types and locking differ.
- **Isolation per test**: a fresh in-memory database (as above) on SQLite, or one rolled-back transaction per test on PostgreSQL (`Session(bind=connection, join_transaction_mode="create_savepoint")` inside an outer `connection.begin()`). The default `pysqlite` driver does not honour SAVEPOINT and transaction boundaries the way PostgreSQL does, so do not copy the rollback pattern onto SQLite without the documented workarounds: this very page's first draft leaked rows between tests until it was run.
- **Assert query counts** on list endpoints to catch N+1.
- **Test migrations**: upgrade from an empty database, run the app's tests, then downgrade.
- Use **factories** (`factory_boy` or small helper functions) instead of copy-pasted object construction.
!end

??  Why run integration tests against PostgreSQL even if unit tests use SQLite?
=> SQLite and PostgreSQL differ in types, constraints, concurrency and SQL features (JSONB, arrays, `ON CONFLICT`, locking, isolation levels), so code that passes on SQLite can fail in production. A containerised PostgreSQL (Testcontainers) in CI gives realistic behaviour.
??  How do database tests stay independent of each other?
=> Either every test gets its own throw-away database (in-memory SQLite), or, on PostgreSQL, each test runs inside an outer transaction with the session joined through a savepoint; at the end the outer transaction is rolled back, so even rows the application "committed" disappear and the next test starts clean without rebuilding the schema. Always verify the isolation with a test that checks the previous test left nothing behind.
