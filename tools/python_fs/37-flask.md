@part py-flask-1 | Flask · Part 1: The Micro-Framework | web
## Flask in One Page

**Flask** is a **micro-framework**: a small core (routing, request and response objects, Jinja2 templates, sessions, a test client) built on **Werkzeug** (WSGI utilities) and **Jinja2**, and nothing else. You add what you need (a database layer, forms, authentication, migrations) from the ecosystem. That freedom makes it excellent for small services, prototypes, internal tools and for **learning how web frameworks work**.

| | **Flask** | **Django** | **FastAPI** |
| --- | --- | --- | --- |
| Interface | WSGI (sync); async views supported but limited | WSGI and ASGI | ASGI |
| Included | Routing, templates, sessions, testing | ORM, admin, auth, forms, migrations, ... | Routing, validation, DI, OpenAPI |
| Structure | Yours to design (blueprints help) | Prescribed (apps, MVT) | Yours (routers, dependencies) |
| Validation | Manual / extensions (WTForms, marshmallow, Pydantic) | Forms, serializers | Pydantic built in |

```python FlaskBasics.py
from flask import Flask, abort, jsonify, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.config.update(SECRET_KEY="dev-only-change-me", TESTING=True)

BOOKS = {1: {"id": 1, "title": "Python Internals"}, 2: {"id": 2, "title": "<script>alert(1)</script>"}}


@app.get("/")                                              # shortcut for @app.route("/", methods=["GET"])
def index():
    return "hello from Flask"                              # a str becomes a text/html response


@app.get("/books/<int:book_id>")                           # converters: int, float, string, path, uuid
def book(book_id):
    if book_id not in BOOKS:
        abort(404)
    return jsonify(BOOKS[book_id])                         # jsonify sets the JSON content type


@app.post("/books")
def create_book():
    payload = request.get_json(silent=True)                # None instead of an exception when the body is not valid JSON
    if not payload or not payload.get("title"):
        return jsonify(error="title is required"), 400     # (body, status) tuple
    new_id = max(BOOKS) + 1
    BOOKS[new_id] = {"id": new_id, "title": payload["title"]}
    return jsonify(BOOKS[new_id]), 201, {"Location": url_for("book", book_id=new_id)}     # (body, status, headers)


@app.get("/search")
def search():
    q = request.args.get("q", "").lower()                  # query string; .args is a read-only MultiDict
    limit = request.args.get("limit", 10, type=int)
    return jsonify([b for b in BOOKS.values() if q in b["title"].lower()][:limit])


@app.get("/page/<int:book_id>")
def page(book_id):                                         # Jinja2 auto-escapes variables: user text cannot inject markup
    return render_template_string("<h1>{{ book.title }}</h1><p>{{ book.title|upper }}</p>", book=BOOKS[book_id])


@app.get("/visit")
def visit():
    session["visits"] = session.get("visits", 0) + 1       # a signed cookie: tamper-proof but readable by the user
    return jsonify(visits=session["visits"])


client = app.test_client()
print(client.get("/").text, client.get("/books/1").json, client.get("/books/9").status_code)
created = client.post("/books", json={"title": "Flask Handbook"})
print(created.status_code, created.headers["Location"], client.post("/books", data="not json", content_type="application/json").status_code)
print(client.get("/search?q=python&limit=5").json, client.get("/page/2").text)
print(client.get("/visit").json, client.get("/visit").json)
print(url_for.__module__, sorted(rule.rule for rule in app.url_map.iter_rules() if rule.rule != "/static/<path:filename>"))
```

```output
```

The pieces to notice:

- **Routes** are plain functions registered with decorators; the return value (string, dict, `jsonify(...)`, tuple, or `Response`) becomes the HTTP response. `url_for("endpoint", **values)` builds URLs from function names.
- **`request`, `session`, `g` and `current_app`** are **context-local proxies**: they look like globals but refer to the current request. This is convenient and is also what makes Flask code harder to test and to use outside a request (you need an application or request context).
- **Jinja2 auto-escaping** turned `<script>alert(1)</script>` into text in the page, the same XSS defence as Django's templates.
- **`session`** is a **signed cookie** (tamper-proof, not encrypted): never store secrets in it; `SECRET_KEY` must be long, random and secret.
- The **test client** (`app.test_client()`) calls the WSGI app in-process, with cookies kept between requests.

??  What are the application context and the request context in Flask?
=> Contexts that make `current_app`, `g` (per-request scratch space), `request` and `session` available as if they were globals. The application context holds app-level state (config, extensions); the request context holds the current request and session. Outside a request (a CLI script, a test) you push one explicitly with `app.app_context()` or `app.test_request_context()`.
??  Is the Flask `session` secure?
=> It is a cookie signed with `SECRET_KEY`, so the client cannot modify it but can read it. Keep only small, non-secret data (user id, flags), set `HttpOnly`/`Secure`/`SameSite` cookie options, rotate the key if leaked, or use server-side sessions (Flask-Session with Redis) for larger or sensitive state.
??  When would you pick Flask over Django or FastAPI?
=> For small services, prototypes and teams who want to choose each component; also where the codebase already uses it. For a large product with many screens Django's built-ins save time; for typed, async-heavy APIs FastAPI fits better.

## Blueprints, the Application Factory and Configuration

A growing Flask app is organised with **blueprints** (groups of routes, templates and handlers) and an **application factory** (a function that builds the app), so each test or deployment can create a fresh configured instance.

```python Factory.py
import os

from flask import Blueprint, Flask, current_app, jsonify, request

api = Blueprint("api", __name__, url_prefix="/api/v1")
admin = Blueprint("admin", __name__, url_prefix="/admin")


@api.get("/config")
def show_config():
    return jsonify(env=current_app.config["ENV_NAME"], debug=current_app.debug, page_size=current_app.config["PAGE_SIZE"])


@api.errorhandler(ValueError)                                       # handlers can be scoped to a blueprint ...
def bad_value(error):
    return jsonify(error=str(error)), 400


@api.get("/double")
def double():
    return jsonify(result=int(request.args["n"]) * 2)               # int("x") raises ValueError -> the handler above


@admin.before_request                                               # ... and so can request hooks
def require_admin_header():
    if request.headers.get("X-Role") != "admin":
        return jsonify(error="forbidden"), 403


@admin.get("/stats")
def stats():
    return jsonify(users=42)


class Config:
    ENV_NAME = "default"
    PAGE_SIZE = 20


class TestConfig(Config):
    ENV_NAME = "test"
    TESTING = True
    PAGE_SIZE = 2


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)                       # defaults ...
    app.config.from_prefixed_env("APP")                            # ... overridden by environment variables like APP_PAGE_SIZE=50
    app.register_blueprint(api)
    app.register_blueprint(admin)

    @app.errorhandler(404)
    def not_found(error):                                          # an app-wide handler: a consistent JSON error body
        return jsonify(error="not found", path=request.path), 404

    return app


os.environ["APP_PAGE_SIZE"] = "50"
production, testing = create_app().test_client(), create_app(TestConfig).test_client()
print(production.get("/api/v1/config").json, testing.get("/api/v1/config").json)
print(testing.get("/api/v1/double?n=21").json, testing.get("/api/v1/double?n=abc").status_code, testing.get("/missing").json)
print(testing.get("/admin/stats").status_code, testing.get("/admin/stats", headers={"X-Role": "admin"}).json)
```

```output
```

The factory pattern is what lets tests create isolated apps with their own config, and lets one codebase run as a web process, a CLI (`flask --app mypkg:create_app shell`) and a worker. Typical Flask project layout:

```text Flask project layout
shop/
  pyproject.toml
  src/shop/
    __init__.py          # create_app()
    config.py            # Config classes
    extensions.py        # db, migrate, login manager: created here, initialised in create_app
    models.py
    api/__init__.py      # Blueprint("api", ...)
    api/routes.py
    templates/ static/
  tests/conftest.py      # app and client fixtures
```

??  Why use an application factory?
=> It builds a fresh, configured app on demand: tests can create apps with test configuration and an isolated database, several configurations can coexist, extensions are initialised per app (`init_app`), and circular imports between the app object and the modules that need it disappear.
??  What is a blueprint?
=> A reusable bundle of routes, handlers, templates and static files with a URL prefix, registered on the app. It is Flask's unit of modularity: an `auth`, `api` or `admin` package each owns its routes and is mounted where needed.

## Data, Authentication and Validation

Flask has no ORM; **SQLAlchemy** (directly, or through `Flask-SQLAlchemy`) is the usual choice, with **Flask-Migrate** (Alembic), **Flask-Login** or a token library for authentication, and **Pydantic**, **marshmallow** or **WTForms** for validation. The example below wires them by hand to show the moving parts: a per-request SQLAlchemy session in `g`, password hashing, login via the session cookie, and Pydantic validation.

```python FlaskApp.py
from functools import wraps

from flask import Flask, g, jsonify, request, session
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field, ValidationError
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

hasher = PasswordHash.recommended()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str]


class Credentials(BaseModel):                                      # validation with Pydantic
    email: EmailStr
    password: str = Field(min_length=8)


def create_app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY="change-me", SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    @app.before_request
    def open_session():
        g.db = Session(engine)                                      # one session per request, stored in g

    @app.teardown_request
    def close_session(error):
        db = g.pop("db", None)
        if db is not None:
            db.rollback() if error else db.commit()
            db.close()

    def login_required(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = g.db.get(User, session["user_id"]) if "user_id" in session else None
            if user is None:
                return jsonify(error="login required"), 401
            g.user = user
            return view(*args, **kwargs)
        return wrapper

    @app.errorhandler(ValidationError)
    def invalid(error):
        return jsonify(errors=[{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in error.errors()]), 422

    @app.post("/register")
    def register():
        data = Credentials.model_validate(request.get_json(silent=True) or {})          # raises ValidationError -> 422 above
        if g.db.scalar(select(User).where(User.email == data.email)):
            return jsonify(error="email already registered"), 409
        g.db.add(User(email=data.email, password_hash=hasher.hash(data.password)))
        return jsonify(email=data.email), 201

    @app.post("/login")
    def login():
        data = Credentials.model_validate(request.get_json(silent=True) or {})
        user = g.db.scalar(select(User).where(User.email == data.email))
        if user is None or not hasher.verify(data.password, user.password_hash):
            return jsonify(error="incorrect email or password"), 401
        session.clear()                                             # a new session on login prevents session fixation
        session["user_id"] = user.id
        return jsonify(ok=True)

    @app.post("/logout")
    def logout():
        session.clear()
        return "", 204

    @app.get("/me")
    @login_required
    def me():
        return jsonify(email=g.user.email)

    return app


client = create_app().test_client()
print(client.get("/me").status_code, client.post("/register", json={"email": "bad", "password": "short"}).json)
print(client.post("/register", json={"email": "asha@example.com", "password": "correct horse"}).status_code,
      client.post("/register", json={"email": "asha@example.com", "password": "correct horse"}).status_code)
print(client.post("/login", json={"email": "asha@example.com", "password": "wrong-password"}).status_code, client.get("/me").status_code)
print(client.post("/login", json={"email": "asha@example.com", "password": "correct horse"}).json, client.get("/me").json)
print(client.post("/logout").status_code, client.get("/me").status_code)
```

```output
```

Notes for real projects: with Flask-Login the decorator and user loader are provided; **CSRF protection** is needed for cookie-authenticated form posts (Flask-WTF/CSRFProtect); rate-limit `/login` (Flask-Limiter with Redis); set `SESSION_COOKIE_SECURE=True` in production; and keep secrets in the environment. For APIs consumed by SPAs and mobile apps, issue tokens (JWT) instead of relying on the session cookie.

## Testing and Running Flask

```python FlaskPytest.py
import pathlib
import re
import subprocess
import sys

pathlib.Path("app.py").write_text('''\
from flask import Flask, jsonify, request


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(TESTING=False, ITEMS=[])
    if config:
        app.config.update(config)

    @app.get("/items")
    def list_items():
        return jsonify(app.config["ITEMS"])

    @app.post("/items")
    def add_item():
        name = (request.get_json(silent=True) or {}).get("name")
        if not name:
            return jsonify(error="name required"), 400
        app.config["ITEMS"].append(name)
        return jsonify(name=name), 201

    return app
''')

pathlib.Path("conftest.py").write_text('''\
import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True, "ITEMS": []})          # a fresh app (and fresh state) for every test


@pytest.fixture
def client(app):
    return app.test_client()
''')

pathlib.Path("test_items.py").write_text('''\
import pytest


def test_starts_empty(client):
    assert client.get("/items").json == []


def test_add_and_list(client):
    assert client.post("/items", json={"name": "pen"}).status_code == 201
    assert client.get("/items").json == ["pen"]


@pytest.mark.parametrize("payload", [{}, {"name": ""}, None])
def test_rejects_bad_payloads(client, payload):
    assert client.post("/items", json=payload).status_code == 400


def test_each_test_has_its_own_state(client):
    assert client.get("/items").json == []                     # items added by other tests are gone
''')

run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header"], capture_output=True, text=True)
print(re.sub(r" in \d+\.\d+s", "", run.stdout).strip())
```

```output
```

```bash Running Flask
flask --app shop:create_app run --debug                     # development server with the debugger and auto-reload (never in production)
gunicorn "shop:create_app()" --workers 4 --bind 0.0.0.0:8000  # production: a real WSGI server, several worker processes
```

The built-in development server and the interactive debugger must **never** face the internet (the debugger allows code execution). In production: Gunicorn or uWSGI behind nginx or a load balancer, configuration from the environment, and the same checklist as any Python service (health endpoints, JSON logs, migrations as a release step).

!cheat Flask cheat sheet ::
| Need | Code |
| --- | --- |
| Route | `@app.get("/x/<int:id>")`, `@app.post("/x")`, `@bp.route(..., methods=[...])` |
| Request data | `request.args` (query), `request.form`, `request.get_json()`, `request.files`, `request.headers` |
| Response | `return jsonify(...), 201, {"Location": ...}`; `abort(404)`; `redirect(url_for("endpoint"))` |
| Templates | `render_template("page.html", x=1)`; Jinja2 auto-escapes `{{ x }}` |
| State | `session` (signed cookie), `g` (per request), `current_app.config` |
| Modularity | `Blueprint`, `create_app()`, `app.config.from_object/from_prefixed_env` |
| Hooks | `@app.before_request`, `@app.after_request`, `@app.teardown_request`, `@app.errorhandler(...)` |
| Test | `app.test_client()`, `client.get/post(json=...)`, fixtures building a fresh app |
| Run | `flask --app pkg run --debug` (dev), `gunicorn "pkg:create_app()"` (prod) |
!end

??  How does Flask handle concurrency, and how do you run it in production?
=> Flask is a WSGI application: each request is handled by a worker (process or thread) of the WSGI server, so concurrency comes from Gunicorn workers and threads, not from Flask itself. Run it behind Gunicorn or uWSGI with several workers, behind a reverse proxy; never use the development server in production.
??  What are `g` and `current_app`?
=> `g` is a per-request namespace for sharing objects such as a database session or the current user between functions; `current_app` is a proxy to the active application, used in blueprints and extensions to reach configuration without importing the app object.
??  How would you add input validation to Flask routes?
=> Parse the body with Pydantic (or marshmallow/WTForms) in the route or a decorator, return a 422 or 400 with field errors on failure, and keep validation separate from persistence. Flask itself does not validate input.
