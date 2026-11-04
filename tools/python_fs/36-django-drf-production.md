@part py-django-3 | Django · Part 3: Django REST Framework, Security and Production | web
## Django REST Framework: Serializers and ViewSets

**Django REST Framework (DRF)** adds the API layer to Django: **serializers** (validation and conversion between model instances and JSON), **views and viewsets**, **routers**, **authentication**, **permissions**, **throttling**, **pagination**, **filtering** and a browsable API. It is the most widely used way to build REST APIs on Django.

| DRF piece | Role | FastAPI equivalent |
| --- | --- | --- |
| `Serializer` / `ModelSerializer` | Validate input, build output | Pydantic model |
| `APIView`, generics, `ViewSet` | Handle requests | Path operation functions |
| `Router` | Generate URLs for a viewset | `include_router` |
| `permission_classes` | Who may do what | `Depends(require_...)` |
| `authentication_classes` | Identify the caller | `Depends(current_user)` |
| `throttle_classes` | Rate limits | rate-limit dependency |
| `PageNumberPagination` | Paginate lists | pagination dependency |

One project, written to disk and tested, shows all of it working together: a per-user **notes API**.

```python DrfNotes.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("notes_site")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def manage(*args):
    done = subprocess.run([sys.executable, "manage.py", *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return done.stdout + done.stderr


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        SECRET_KEY = "x"
        ALLOWED_HOSTS = ["testserver"]
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "django.contrib.sessions", "django.contrib.messages",
                          "rest_framework", "rest_framework.authtoken", "notes"]
        MIDDLEWARE = ["django.contrib.sessions.middleware.SessionMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware"]
        ROOT_URLCONF = "config.urls"
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        REST_FRAMEWORK = {
            "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication", "rest_framework.authentication.SessionAuthentication"],
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],     # secure by default: opt OUT per view
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 2,
        }
    """,
    "config/urls.py": """
        from django.urls import include, path
        from rest_framework.routers import DefaultRouter

        from notes.views import BurstView, NoteViewSet

        router = DefaultRouter()
        router.register("notes", NoteViewSet, basename="note")

        urlpatterns = [path("api/", include(router.urls)), path("api/burst/", BurstView.as_view())]
    """,
    "notes/__init__.py": "",
    "notes/models.py": """
        from django.conf import settings
        from django.db import models


        class Note(models.Model):
            owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
            title = models.CharField(max_length=100)
            body = models.TextField(blank=True)
            done = models.BooleanField(default=False)
            created = models.DateTimeField(auto_now_add=True)

            class Meta:
                ordering = ["-id"]
    """,
    "notes/serializers.py": """
        from rest_framework import serializers

        from .models import Note


        class NoteSerializer(serializers.ModelSerializer):
            owner = serializers.ReadOnlyField(source="owner.username")        # exposed, never writable by the client

            class Meta:
                model = Note
                fields = ["id", "owner", "title", "body", "done", "created"]
                read_only_fields = ["id", "created"]

            def validate_title(self, value):                                  # field-level validation: validate_<field>
                value = value.strip()
                if len(value) < 3:
                    raise serializers.ValidationError("Title must have at least 3 characters.")
                return value
    """,
    "notes/permissions.py": """
        from rest_framework import permissions


        class IsOwner(permissions.BasePermission):
            def has_object_permission(self, request, view, obj):              # object-level rule: defence in depth with get_queryset
                return obj.owner == request.user
    """,
    "notes/views.py": """
        from rest_framework import filters, viewsets
        from rest_framework.decorators import action
        from rest_framework.response import Response
        from rest_framework.throttling import UserRateThrottle
        from rest_framework.views import APIView

        from .models import Note
        from .permissions import IsOwner
        from .serializers import NoteSerializer


        class NoteViewSet(viewsets.ModelViewSet):                              # list, create, retrieve, update, partial_update, destroy
            serializer_class = NoteSerializer
            permission_classes = [IsOwner] + viewsets.ModelViewSet.permission_classes
            filter_backends = [filters.SearchFilter, filters.OrderingFilter]
            search_fields = ["title", "body"]
            ordering_fields = ["created", "title"]

            def get_queryset(self):
                return Note.objects.filter(owner=self.request.user).select_related("owner")   # users only ever see THEIR notes

            def perform_create(self, serializer):
                serializer.save(owner=self.request.user)                      # the owner comes from the session, not from the payload

            @action(detail=True, methods=["post"])                            # extra route: POST /api/notes/<id>/complete/
            def complete(self, request, pk=None):
                note = self.get_object()
                note.done = True
                note.save(update_fields=["done"])
                return Response(self.get_serializer(note).data)


        class BurstThrottle(UserRateThrottle):
            rate = "3/min"


        class BurstView(APIView):
            throttle_classes = [BurstThrottle]

            def get(self, request):
                return Response({"ok": True})
    """,
    "notes/tests.py": """
        from django.contrib.auth import get_user_model
        from django.core.cache import cache
        from rest_framework.authtoken.models import Token
        from rest_framework.test import APITestCase

        from .models import Note

        User = get_user_model()


        class NotesApiTests(APITestCase):
            def setUp(self):
                cache.clear()                                                 # throttle counters live in the cache
                self.asha, self.ravi = User.objects.create_user("asha", password="pw"), User.objects.create_user("ravi", password="pw")
                for title in ("Buy milk", "Call mum", "Pay rent", "Plan trip", "Read book"):
                    Note.objects.create(owner=self.asha, title=title, body="remember")
                Note.objects.create(owner=self.ravi, title="Ravi's secret")

            def login(self, user):
                token = Token.objects.create(user=user)
                self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

            def test_anonymous_requests_are_401(self):
                self.assertEqual(self.client.get("/api/notes/").status_code, 401)

            def test_list_is_paginated_and_private(self):
                self.login(self.asha)
                data = self.client.get("/api/notes/").json()
                self.assertEqual((data["count"], len(data["results"]), bool(data["next"])), (5, 2, True))       # Ravi's note is not counted
                self.assertNotIn("Ravi's secret", str(data))

            def test_create_sets_the_owner_and_validates(self):
                self.login(self.ravi)
                created = self.client.post("/api/notes/", {"title": "  Gym  ", "owner": "asha", "done": False}, format="json")
                self.assertEqual((created.status_code, created.json()["owner"], created.json()["title"]), (201, "ravi", "Gym"))     # payload owner ignored
                bad = self.client.post("/api/notes/", {"title": "x"}, format="json")
                self.assertEqual((bad.status_code, bad.json()["title"][0]), (400, "Title must have at least 3 characters."))

            def test_other_users_notes_are_404_not_403(self):
                self.login(self.ravi)
                asha_note = Note.objects.filter(owner=self.asha).first()
                self.assertEqual(self.client.get(f"/api/notes/{asha_note.pk}/").status_code, 404)
                self.assertEqual(self.client.delete(f"/api/notes/{asha_note.pk}/").status_code, 404)

            def test_search_ordering_and_custom_action(self):
                self.login(self.asha)
                found = self.client.get("/api/notes/?search=milk").json()
                self.assertEqual([n["title"] for n in found["results"]], ["Buy milk"])
                ordered = self.client.get("/api/notes/?ordering=title&page_size=5").json()["results"]
                self.assertEqual(ordered[0]["title"], "Buy milk")
                pk = found["results"][0]["id"]
                self.assertTrue(self.client.post(f"/api/notes/{pk}/complete/").json()["done"])

            def test_query_budget_for_the_list_endpoint(self):
                self.client.force_authenticate(self.asha)                    # no token lookup query
                with self.assertNumQueries(2):                               # COUNT for the paginator + SELECT for the page (owner is joined)
                    self.client.get("/api/notes/")

            def test_throttling_returns_429(self):
                self.login(self.asha)
                statuses = [self.client.get("/api/burst/").status_code for _ in range(4)]
                self.assertEqual(statuses, [200, 200, 200, 429])
    """,
})
output = manage("test", "notes", "-v", "2")
print(sorted(re.findall(r"^(test_\w+) \(notes\.tests\.NotesApiTests\.\w+\) \.\.\. (\w+)", output, re.M)))
print(re.search(r"Ran \d+ tests?", output)[0], "OK" if re.search(r"^OK", output, re.M) else output[-800:])
```

```output
```

How the pieces cooperate:

1. **`ModelViewSet` + `DefaultRouter`** produce the whole REST surface from one class (`GET/POST /api/notes/`, `GET/PUT/PATCH/DELETE /api/notes/<id>/`) plus the extra `complete` action.
2. **`get_queryset` is the security boundary.** Because it filters by the owner, another user's note simply does not exist for this request: a 404, with no way to enumerate ids. `IsOwner` adds object-level defence in depth.
3. **The serializer is the contract**: `owner` is read-only and comes from `request.user` in `perform_create`, so a client cannot assign notes to someone else (**mass assignment** prevented). Validation errors are field-keyed JSON.
4. **Secure by default**: `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` means a forgotten permission is a closed door, not an open one.
5. **Pagination, search and ordering** are declarative; `select_related("owner")` and the `assertNumQueries(2)` test keep the list endpoint at two queries.
6. **Throttling** protects against abuse and uses the cache (in production a shared cache such as Redis, otherwise each worker counts separately).

!interview ModelSerializer vs Serializer, APIView vs ViewSet :: `ModelSerializer` derives fields and validation from a model (less code, tied to the schema); a plain `Serializer` is declared by hand for non-model input or when the API shape differs from the table. `APIView` gives you full control per HTTP method; generics add common behaviour; `ViewSet` + router collapses a whole CRUD resource into one class. Use the highest level that fits and drop down when behaviour is unusual.

??  What does `get_queryset` have to do with security in DRF?
=> It decides which rows a request can see at all. Filtering by the authenticated user there means every detail, update and delete lookup is automatically scoped (other users' objects give 404), which prevents IDOR bugs that object-level permission checks alone can miss on list endpoints.
??  How does DRF validation differ from Django forms validation?
=> Same ideas (field rules, `validate_<field>`, `validate()` for cross-field checks), but serializers work with JSON and return a structured error dictionary instead of rendering HTML. `ModelSerializer` also integrates model validators and uniqueness checks.
??  What are the authentication options in DRF?
=> Session authentication (browser, with CSRF), token authentication (a database-backed key per user), and third-party schemes such as JWT (`djangorestframework-simplejwt`) or OAuth2 (`django-oauth-toolkit`). They are configured globally and per view; permissions then decide what the identified user may do.

## Caching, Async Views and Background Work

### Caching

Django's cache framework has a low-level API and per-view / per-fragment caching, over backends such as **local memory** (development), **Redis** (production; shared between workers) and Memcached.

```python Caching.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("cache_site")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def manage(*args):
    done = subprocess.run([sys.executable, "manage.py", *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return done.stdout + done.stderr


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        SECRET_KEY = "x"
        ALLOWED_HOSTS = ["testserver"]
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "webapp"]
        MIDDLEWARE = ["django.middleware.common.CommonMiddleware"]
        ROOT_URLCONF = "config.urls"
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "demo"}}     # Redis in production
    """,
    "config/urls.py": """
        from django.urls import path

        from webapp import views

        urlpatterns = [path("slow/", views.slow), path("report/<int:n>/", views.report), path("health/", views.health)]
    """,
    "webapp/__init__.py": "",
    "webapp/views.py": """
        import asyncio

        from django.core.cache import cache
        from django.http import JsonResponse
        from django.views.decorators.cache import cache_page

        CALLS = {"slow": 0, "report": 0}


        @cache_page(60)                                                     # the whole response, keyed by URL (and Vary headers)
        def slow(request):
            CALLS["slow"] += 1
            return JsonResponse({"calls": CALLS["slow"]})


        def report(request, n):
            key = f"report:{n}"
            data = cache.get(key)                                           # low-level cache-aside
            if data is None:
                CALLS["report"] += 1
                data = {"n": n, "square": n * n}                            # imagine an expensive query here
                cache.set(key, data, timeout=300)
            return JsonResponse(data)


        async def health(request):                                         # an ASYNC view: runs on the event loop under ASGI
            await asyncio.sleep(0)
            return JsonResponse({"status": "ok"})
    """,
    "webapp/tests.py": """
        from django.core.cache import cache
        from django.test import TestCase

        from . import views


        class CacheTests(TestCase):
            def setUp(self):
                cache.clear()
                views.CALLS.update(slow=0, report=0)

            def test_cache_page_serves_the_second_request_from_cache(self):
                self.assertEqual(self.client.get("/slow/").json(), {"calls": 1})
                self.assertEqual(self.client.get("/slow/").json(), {"calls": 1})        # the view body did not run again
                self.assertEqual(views.CALLS["slow"], 1)

            def test_low_level_cache_aside_and_invalidation(self):
                self.client.get("/report/4/")
                self.client.get("/report/4/")
                self.assertEqual(views.CALLS["report"], 1)
                cache.delete("report:4")                                                # invalidate when the data changes
                self.client.get("/report/4/")
                self.assertEqual(views.CALLS["report"], 2)

            async def test_async_view(self):
                response = await self.async_client.get("/health/")
                self.assertEqual(response.json(), {"status": "ok"})
    """,
})
output = manage("test", "webapp")
print(re.search(r"Ran \d+ tests?", output)[0], "OK" if re.search(r"^OK", output, re.M) else output[-800:])
```

```output
```

!warning Cache invalidation is the hard part :: Every cache needs a **TTL**, an **invalidation rule** (delete or version the key when the data changes), and a story for **stampedes** (many requests recomputing an expired entry at once: add jitter, locks or "stale-while-revalidate"). Never cache user-specific responses under a shared key, and remember that per-process caches (`LocMemCache`) differ between workers: use Redis in production.

### Async views, and when they help

Django supports `async def` views (ASGI), async ORM methods (`await Model.objects.aget(...)`, `async for obj in qs`) and async middleware. They help when a view **awaits I/O** (several HTTP calls, an async driver): they do **not** make ORM calls on a classic sync database driver faster, since those still hop to a thread. Choose async for fan-out to external services; keep ordinary CRUD views synchronous. Run async Django under an **ASGI** server (Uvicorn/Daphne/Hypercorn); WSGI servers run async views in a thread with an event loop per request, which loses the benefit.

### Background work

Anything slow or unreliable (emails, reports, thumbnails, calls to third parties) leaves the request: a **task queue** (Celery with Redis or RabbitMQ, or lighter options such as RQ, Dramatiq, Huey; Django 6.0 added a built-in tasks framework with pluggable backends) runs it in separate worker processes with retries and schedules. The part on Celery in this tree builds one. Use `transaction.on_commit` to enqueue only after the database commit.

??  What are the main ways to cache in Django?
=> Per-site and per-view caching (`cache_page`), template fragment caching (`{% cache %}`), and the low-level API (`cache.get/set/delete`, `get_or_set`) for arbitrary data, over a backend such as Redis. Pick the layer by what is expensive and how stale the data may be, and design invalidation up front.
??  When is an async Django view worthwhile?
=> When the view spends its time waiting on several independent I/O calls that can overlap (HTTP APIs, async clients). For standard database CRUD with a sync driver, async adds little. Use an ASGI server so the event loop is actually used.

## Going to Production

```text Production checklist
Settings        DEBUG=False, SECRET_KEY from the environment, ALLOWED_HOSTS, SECURE_* and cookie flags, check --deploy clean
Database        PostgreSQL, CONN_MAX_AGE or the built-in connection pool, migrations as a release step, backups tested
Static / media  collectstatic -> WhiteNoise or a CDN; user uploads on object storage (S3), never on the app disk
Server          Gunicorn (WSGI) or Uvicorn/Daphne (ASGI) behind nginx or a load balancer; several workers; graceful shutdown
Caching         Redis for cache, sessions, throttling; consistent keys and TTLs
Tasks           Celery or similar for slow work; on_commit; idempotent tasks; retries with backoff
Observability   JSON logs to stdout, request IDs, Sentry, metrics (django-prometheus), health endpoints
Security        HTTPS + HSTS, CSRF and CORS configured, rate limits, dependency audit, least-privilege DB user, admin protected
Performance     assertNumQueries on key pages, select_related/prefetch_related, indexes from real slow-query logs, pagination everywhere
```

A production-minded `settings.py` fragment (values from the environment, shown for reference):

```python settings production !skip
import os
from pathlib import Path

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]                       # KeyError at start-up if missing: fail fast
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")      # trust the proxy that terminates TLS

DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql", "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
    "PASSWORD": os.environ["DB_PASSWORD"], "HOST": os.environ["DB_HOST"], "CONN_MAX_AGE": 60,
}}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": os.environ["REDIS_URL"]}}

LOGGING = {"version": 1, "disable_existing_loggers": False,
           "handlers": {"console": {"class": "logging.StreamHandler"}},
           "root": {"handlers": ["console"], "level": "INFO"}}      # to stdout: the platform collects it
```

Deploy with `gunicorn config.wsgi:application --workers 4` (or `uvicorn config.asgi:application`), run `python manage.py migrate` as a separate release job, `collectstatic` at build time, and probe `/healthz` (a trivial view) and `/readyz` (checks the database) from the orchestrator.

!cheat Django versus FastAPI, when to choose which ::
| | **Django (+ DRF)** | **FastAPI** |
| --- | --- | --- |
| Strength | Everything included: ORM, migrations, admin, auth, forms | Typed, async-first, automatic OpenAPI, light |
| Admin / back office | Free and excellent | Build or integrate yourself |
| Validation | Serializers / forms | Pydantic |
| Async | Supported, partial (ORM mostly sync) | Native |
| Team size and conventions | Large teams love the conventions | Smaller services, explicit design |
| Typical use | Product with many screens, content, internal tools | High-throughput APIs, microservices, ML back ends |
!end

??  How would you structure settings for development, testing and production?
=> A settings package (`base.py`, `dev.py`, `test.py`, `prod.py`) or one module driven by environment variables, with secrets and hosts from the environment, safe defaults only for development, production-only security settings enforced by `check --deploy`, and no secrets in the repository.
??  What does `CONN_MAX_AGE` do?
=> It keeps database connections open for that many seconds and reuses them across requests instead of reconnecting for each one (0 closes after every request). With many workers watch the total against the database's connection limit, or use a pooler such as PgBouncer; newer Django versions also offer native connection pooling for PostgreSQL.
??  What is the safest way to run Django migrations in a deployment pipeline?
=> As a dedicated step before the new code starts receiving traffic (or after, for backwards-compatible changes), executed once rather than by every container, with backwards-compatible migrations (expand, then contract) so old and new application versions can run against the same schema during the rollout.
