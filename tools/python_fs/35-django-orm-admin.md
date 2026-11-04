@part py-django-2 | Django · Part 2: The ORM, Migrations and the Admin | web
## Models and Fields

A Django **model** is a Python class that describes a database table; each attribute is a **field** (a column with a type and validation rules). The ORM translates between objects and SQL, and the same model definition drives migrations, forms, the admin and serializers.

| Field | Column | Notes |
| --- | --- | --- |
| `CharField(max_length=...)`, `TextField` | `varchar`, `text` | `max_length` is required for `CharField` |
| `IntegerField`, `PositiveIntegerField`, `BigIntegerField` | integers | |
| `DecimalField(max_digits, decimal_places)` | exact decimals | **Use for money**, never `FloatField` |
| `BooleanField`, `DateField`, `DateTimeField` | | `auto_now_add=True` sets the creation time |
| `EmailField`, `URLField`, `SlugField`, `UUIDField` | validated strings | validation runs in forms and `full_clean()` |
| `JSONField` | `jsonb` / JSON | flexible data, queryable on PostgreSQL |
| `ForeignKey`, `OneToOneField`, `ManyToManyField` | relations | `on_delete` is required for foreign keys |

Common options: `null=True` (database NULL), `blank=True` (validation allows empty), `default=`, `unique=True`, `db_index=True`, `choices=` (use `TextChoices`), `validators=[...]`. And `class Meta:` for `ordering`, `constraints`, `indexes`, `unique_together`, `verbose_name`.

```python OrmModels.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def run(*args):
    done = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return (done.stdout + done.stderr).strip()


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        from pathlib import Path

        BASE_DIR = Path(__file__).resolve().parent.parent
        SECRET_KEY = "x"
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "catalog"]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        USE_TZ = True
    """,
    "catalog/__init__.py": "",
    "catalog/models.py": """
        from django.core.validators import MinValueValidator
        from django.db import models


        class Category(models.Model):
            name = models.CharField(max_length=60, unique=True)

            class Meta:
                verbose_name_plural = "categories"
                ordering = ["name"]

            def __str__(self):
                return self.name


        class Product(models.Model):
            class Status(models.TextChoices):                       # an enum stored as a string, with labels
                DRAFT = "draft", "Draft"
                ACTIVE = "active", "Active"

            name = models.CharField(max_length=100)
            price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
            stock = models.PositiveIntegerField(default=0)
            status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
            category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
            created = models.DateTimeField(auto_now_add=True)

            class Meta:
                constraints = [models.CheckConstraint(condition=models.Q(price__gte=0), name="price_non_negative")]
                indexes = [models.Index(fields=["status", "price"])]

            def __str__(self):
                return f"{self.name} ({self.price})"

            @property
            def in_stock(self):
                return self.stock > 0
    """,
    "demo.py": """
        import django

        django.setup()
        from decimal import Decimal

        from django.core.exceptions import ValidationError
        from django.db import IntegrityError, transaction

        from catalog.models import Category, Product

        pens = Category.objects.create(name="Pens")
        product = Product(name="Gel pen", price=Decimal("12.50"), stock=40, status=Product.Status.ACTIVE, category=pens)
        product.save()                                                       # INSERT
        print(product.pk, product.get_status_display(), product.in_stock, repr(product.price))

        product.stock -= 5
        product.save(update_fields=["stock"])                                 # UPDATE only the changed column
        product.refresh_from_db()
        print(product.stock)

        bad = Product(name="Broken", price=Decimal("-1"), category=pens)
        try:
            bad.full_clean()                                                  # Python-level validation (forms call this)
        except ValidationError as error:
            print("full_clean:", sorted(error.message_dict))
        try:
            with transaction.atomic():
                Product.objects.create(name="Broken", price=Decimal("-1"), category=pens)    # the database constraint still refuses it
        except IntegrityError as error:
            print("database:", "price_non_negative" in str(error) or "CHECK" in str(error))
        print(Product.objects.count(), str(product), Product._meta.get_field("price").max_digits)
    """,
})

print(run("manage.py", "makemigrations", "catalog").replace("\\", "/"))
print(run("manage.py", "migrate", "--verbosity", "0") or "migrated")
print(run("demo.py"))
```

```output
```

Notice the layers of protection, which are deliberate: **field validators and `full_clean()`** (run by forms and the admin, not by `save()`), and **database constraints** (`CheckConstraint`, `unique`, foreign keys), which hold no matter which code path writes the row. `save()` itself does **not** validate: call `full_clean()` yourself when you create objects outside forms.

!tip Money, enums and defaults :: Store money as `DecimalField` (or integer minor units), statuses as `TextChoices` (readable in code, validated by forms, a short string in the database), and keep `null=True` for genuinely unknown values; for strings use `blank=True` with the empty string rather than `null=True`, so there is only one "no value".

??  What is the difference between `null=True` and `blank=True`?
=> `null` is a database setting (the column may store NULL); `blank` is a validation setting (forms and `full_clean()` accept an empty value). A text field is usually `blank=True` without `null`; a nullable date needs both.
??  Does `Model.save()` run validators?
=> No. Validators run in `full_clean()`, which forms and the admin call, so objects created in code (`objects.create`, `save`) bypass them unless you call `full_clean()`. Constraints you must always hold belong in the database too.
??  Why use `TextChoices`?
=> It gives named constants (`Product.Status.ACTIVE`), human labels, validation of allowed values in forms, and `get_status_display()`, while storing a plain string. It avoids scattered magic strings.

## QuerySets: Lazy, Chainable and Translated to SQL

A **QuerySet** represents a query. It is **lazy** (building it runs no SQL), **chainable** (`filter().exclude().order_by()` each return a new QuerySet) and **cached** once evaluated (iterating, slicing with a step, `list()`, `len()`, `bool()`, `exists()` and friends trigger SQL).

```python QuerySets.py
import os
import pathlib
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def run(*args):
    done = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return (done.stdout + done.stderr).strip()


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        from pathlib import Path

        BASE_DIR = Path(__file__).resolve().parent.parent
        SECRET_KEY = "x"
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "catalog"]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
        USE_TZ = True
    """,
    "catalog/__init__.py": "",
    "catalog/models.py": """
        from django.db import models


        class Category(models.Model):
            name = models.CharField(max_length=60, unique=True)


        class Product(models.Model):
            name = models.CharField(max_length=100)
            price = models.DecimalField(max_digits=10, decimal_places=2)
            stock = models.PositiveIntegerField(default=0)
            status = models.CharField(max_length=10, default="draft")
            category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    """,
    "demo.py": """
        import django

        django.setup()
        from django.db import connection
        from django.db.models import Avg, Count, F, Max, Q, Sum
        from django.test.utils import CaptureQueriesContext

        from catalog.models import Category, Product

        pens, ink = Category.objects.create(name="Pens"), Category.objects.create(name="Ink")
        Product.objects.bulk_create([                                         # ONE INSERT for many rows
            Product(name="Gel pen", price="12.50", stock=40, status="active", category=pens),
            Product(name="Fountain pen", price="120.00", stock=3, status="active", category=pens),
            Product(name="Pencil", price="4.00", stock=0, status="draft", category=pens),
            Product(name="Blue ink", price="45.00", stock=15, status="active", category=ink),
            Product(name="Black ink", price="45.00", stock=0, status="active", category=ink),
        ])

        qs = Product.objects.filter(status="active").exclude(stock=0)         # nothing has run yet
        print(type(qs).__name__, str(qs.query).split(" WHERE ")[1][:60])
        print(list(qs.order_by("-price").values_list("name", flat=True)))     # evaluation: the SQL runs now

        print(Product.objects.filter(name__icontains="PEN").count(), Product.objects.filter(price__range=(10, 50)).count(), Product.objects.filter(category__name="Ink").count())
        print(Product.objects.filter(Q(stock=0) | Q(price__gt=100)).values_list("name", flat=True).order_by("name"))
        print(Product.objects.filter(stock__lt=F("price")).count())            # compare a column with another column: no Python loop
        print(Product.objects.aggregate(total=Sum("stock"), average=Avg("price"), top=Max("price")))
        per_category = Category.objects.annotate(n=Count("products"), stock=Sum("products__stock")).order_by("name")
        print([(c.name, c.n, c.stock) for c in per_category])

        Product.objects.filter(category=ink).update(price=F("price") * 2)     # ONE UPDATE; no read-modify-write race
        print(Product.objects.get(name="Blue ink").price)
        product, created = Product.objects.get_or_create(name="Gel pen", defaults={"price": 1, "category": pens})
        print(created, product.pk)
        print(Product.objects.exists(), Product.objects.filter(name="nope").exists(), Product.objects.filter(name="nope").first())

        with CaptureQueriesContext(connection) as queries:
            subset = Product.objects.filter(status="active")                  # lazy
            first_ten = subset[:10]                                           # still lazy: becomes LIMIT 10
            evaluated = list(first_ten)
            again = list(first_ten)                                           # served from the QuerySet's result cache
        print(len(evaluated), len(queries), "query for two uses of the same evaluated QuerySet")
        try:
            Product.objects.get(status="active")
        except Product.MultipleObjectsReturned:
            print("get() needs exactly one row")
    """,
})
run("manage.py", "makemigrations", "catalog")
run("manage.py", "migrate", "--verbosity", "0")
print(run("demo.py"))
```

```output
```

The vocabulary you need:

| Need | Write |
| --- | --- |
| Filter | `filter(price__gte=10)`, `exclude(...)`, lookups: `__exact`, `__iexact`, `__contains`, `__icontains`, `__in`, `__gt/gte/lt/lte`, `__range`, `__startswith`, `__isnull`, `__year` |
| Related field | `filter(category__name="Ink")` (the double underscore walks relations) |
| OR, NOT | `Q(a=1) \| Q(b=2)`, `~Q(a=1)` |
| Column to column / atomic update | `F("price") * 2` inside `update()` or `filter()` |
| Aggregate to one value | `aggregate(Sum("stock"))` |
| Aggregate per row/group | `annotate(n=Count("products"))` |
| Choose columns | `values("name")` (dicts), `values_list("name", flat=True)`, `only()`, `defer()` |
| One row | `get(pk=1)` (raises `DoesNotExist` / `MultipleObjectsReturned`), `first()`, `last()` |
| Existence and counts | `exists()`, `count()` (cheaper than `len()` or truthiness of a big QuerySet) |
| Bulk work | `bulk_create`, `bulk_update`, `update()`, `delete()` on a QuerySet: set-based, few queries |
| Upsert | `get_or_create`, `update_or_create` (wrap in a unique constraint to be race-safe) |

!warning Evaluate QuerySets deliberately :: `if qs:` or `len(qs)` loads **every row**; use `qs.exists()` and `qs.count()`. Looping `for p in Product.objects.all(): p.stock += 1; p.save()` issues one query per row; use `update(stock=F("stock") + 1)`. Passing a QuerySet to a template that loops twice is fine (it caches), but accessing a related object in the loop causes N+1 (next chapter).

??  Why are QuerySets lazy and why does it matter?
=> Building a QuerySet only describes a query; SQL runs when you evaluate it (iterate, slice with a step, `list`, `len`, `bool`, `exists`, `count`...). Laziness lets you compose filters in several places and run one query, and avoid queries you never need; the cost is that evaluation points are easy to miss and may happen in templates.
??  What is the point of `F()` expressions?
=> They refer to column values inside the database, so `update(stock=F("stock") - 1)` is one atomic SQL statement with no read-modify-write cycle in Python (and therefore no lost updates), and `filter(a__gt=F("b"))` compares two columns without loading rows.
??  How do `aggregate` and `annotate` differ?
=> `aggregate` collapses the whole QuerySet into one dictionary of values (total stock, average price). `annotate` adds a computed value to each object (or group) in the QuerySet, such as the number of products per category.

## Relationships and the N+1 Problem

`ForeignKey` (many-to-one), `OneToOneField` and `ManyToManyField` give you navigation in both directions: `product.category` and `category.products.all()` (the reverse name comes from `related_name`). By default related objects load **lazily**, one query per access, which causes the **N+1 problem**. Django's two fixes:

| Tool | SQL | Use for |
| --- | --- | --- |
| **`select_related("category")`** | A `JOIN`; one query | Forward `ForeignKey` / `OneToOne` (single related object) |
| **`prefetch_related("tags")`** | A second query with `IN (...)`, joined in Python | Many-to-many and reverse foreign keys (collections) |
| `Prefetch("lines", queryset=...)` | Same, with a custom filtered queryset | Filtering or ordering the related collection |

```python NPlusOneDjango.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def run(*args):
    done = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return (done.stdout + done.stderr).strip()


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        SECRET_KEY = "x"
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "library"]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    """,
    "library/__init__.py": "",
    "library/models.py": """
        from django.db import models


        class Tag(models.Model):
            name = models.CharField(max_length=30)


        class Author(models.Model):
            name = models.CharField(max_length=60)


        class Book(models.Model):
            title = models.CharField(max_length=100)
            author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
            tags = models.ManyToManyField(Tag, related_name="books")
    """,
    "library/tests.py": """
        from django.db.models import Prefetch
        from django.test import TestCase

        from .models import Author, Book, Tag


        class NPlusOne(TestCase):
            @classmethod
            def setUpTestData(cls):
                python, web = Tag.objects.create(name="python"), Tag.objects.create(name="web")
                for a in range(5):
                    author = Author.objects.create(name=f"author-{a}")
                    for b in range(2):
                        book = Book.objects.create(title=f"book-{a}-{b}", author=author)
                        book.tags.add(python, web)

            def test_forward_foreign_key(self):
                with self.assertNumQueries(11):                      # 1 for the books + 1 per book for its author
                    [book.author.name for book in Book.objects.all()]
                with self.assertNumQueries(1):                       # select_related: one JOIN
                    [book.author.name for book in Book.objects.select_related("author")]

            def test_many_to_many(self):
                with self.assertNumQueries(11):
                    [list(book.tags.all()) for book in Book.objects.all()]
                with self.assertNumQueries(2):                       # prefetch_related: one extra query with IN (...)
                    [list(book.tags.all()) for book in Book.objects.prefetch_related("tags")]

            def test_reverse_relation_with_a_filtered_prefetch(self):
                recent = Prefetch("books", queryset=Book.objects.filter(title__endswith="-1"), to_attr="second_books")
                with self.assertNumQueries(2):
                    authors = list(Author.objects.prefetch_related(recent))
                self.assertEqual([len(a.second_books) for a in authors], [1] * 5)

            def test_combined(self):
                with self.assertNumQueries(2):
                    books = Book.objects.select_related("author").prefetch_related("tags")
                    [(b.author.name, [t.name for t in b.tags.all()]) for b in books]
    """,
})
output = run("manage.py", "test", "library", "-v", "2")
print(re.findall(r"^test_\w+ \(library\.tests\.NPlusOne\.\w+\) \.\.\. \w+", output, re.M))
print(re.search(r"Ran \d+ tests?", output)[0], "OK" if re.search(r"^OK", output, re.M) else "FAILED")
```

```output
```

The test file **is the lesson**: `assertNumQueries(11)` documents the N+1 (1 + 10), and the fixed versions assert 1 or 2 queries. Keep such assertions on list endpoints and templates in your suite, so an innocent change that adds a related-field access to a loop fails the build instead of the database.

??  What is the difference between `select_related` and `prefetch_related`?
=> `select_related` follows forward foreign keys and one-to-one fields with a SQL `JOIN` in a single query. `prefetch_related` runs a separate query for each relation (many-to-many or reverse foreign key) and joins the results in Python, so it works for collections where a JOIN would multiply rows.
??  What does `related_name` do?
=> It names the reverse accessor on the related model (`author.books`) and the reverse lookup in queries (`Author.objects.filter(books__title=...)`). Without it Django uses `book_set`. Good names make queries read naturally.
??  How do you find N+1 queries in a Django project?
=> `assertNumQueries` in tests, `django-debug-toolbar` or logging `django.db.backends` at DEBUG in development, and APM tools in production. Then add `select_related`/`prefetch_related` or restructure the query.

## Migrations: The Schema's Version Control

`makemigrations` compares your models with the migration history and writes a new **migration file**; `migrate` applies unapplied ones in dependency order and records them in `django_migrations`. Look at what is generated, because **you are responsible for it**:

```python Migrations.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


def write(files: dict):
    for name, content in files.items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def run(*args):
    done = subprocess.run([sys.executable, "manage.py", *args], cwd=ROOT, capture_output=True, text=True, env={**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"})
    return (done.stdout + done.stderr).strip()


write({
    "manage.py": "import sys\nfrom django.core.management import execute_from_command_line\nexecute_from_command_line(sys.argv)\n",
    "config/__init__.py": "",
    "config/settings.py": """
        from pathlib import Path

        SECRET_KEY = "x"
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "blog"]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": Path(__file__).resolve().parent.parent / "db.sqlite3"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    """,
    "blog/__init__.py": "",
    "blog/models.py": """
        from django.db import models


        class Post(models.Model):
            title = models.CharField(max_length=100)
            body = models.TextField()
    """,
})
print(run("makemigrations", "blog").replace("\\", "/"))
print(run("sqlmigrate", "blog", "0001"))
run("migrate", "--verbosity", "0")

# The model changes: a new column and a data migration to fill it
(ROOT / "blog" / "models.py").write_text(textwrap.dedent("""
    from django.db import models


    class Post(models.Model):
        title = models.CharField(max_length=100)
        body = models.TextField()
        slug = models.SlugField(max_length=100, default="", blank=True)
""").lstrip())
print(run("makemigrations", "blog", "--name", "add_slug").replace("\\", "/"))
migration = (ROOT / "blog" / "migrations" / "0002_add_slug.py").read_text()
print(re.findall(r"migrations\.(\w+)\(", migration), "dependencies:", re.findall(r"\('blog', '(\w+)'\)", migration))

(ROOT / "blog" / "migrations" / "0003_fill_slugs.py").write_text(textwrap.dedent('''
    from django.db import migrations
    from django.utils.text import slugify


    def fill_slugs(apps, schema_editor):
        Post = apps.get_model("blog", "Post")                  # the historical model: never import the real one in a migration
        for post in Post.objects.all():
            post.slug = slugify(post.title)
            post.save(update_fields=["slug"])


    class Migration(migrations.Migration):
        dependencies = [("blog", "0002_add_slug")]
        operations = [migrations.RunPython(fill_slugs, migrations.RunPython.noop)]      # reversible: the reverse does nothing
''').lstrip())
print(run("showmigrations", "blog"))
print(run("migrate", "blog", "--plan"))
```

```output
```

What to take from the output:

- A migration is **Python code you review**: operations like `CreateModel`, `AddField`, `AlterField`, `RunPython`, with explicit `dependencies`. Commit it with the model change.
- `sqlmigrate` shows the exact SQL, which is how you check that a migration will not take a long lock on a large table.
- **Data migrations** use `apps.get_model(...)` (the model *as it was at that point in history*) and should be **reversible** (a reverse function or `noop`).
- `migrate app 0002` moves to a specific migration (forwards or backwards); `--plan` shows what would run.

Rules for safe production migrations:

1. **Never edit an applied migration**; add a new one. Merge conflicts between developers' migrations are resolved with `makemigrations --merge`.
2. **Expand then contract** for zero-downtime releases: add the nullable column, deploy code that writes it, backfill in batches, make it required, and only later remove the old column.
3. **Watch locks**: adding a `NOT NULL` column with a default, adding an index, or altering a type can lock a big table. On PostgreSQL use `AddIndexConcurrently` and `SeparateDatabaseAndState` patterns, and test on production-sized data.
4. Run migrations as **one release step** before (or after) the new code is rolled out, not at every container start.
5. Keep migrations **fast and independent of application code**: do not import models or helper functions that may change later.

??  What is the difference between `makemigrations` and `migrate`?
=> `makemigrations` generates migration files from model changes (it does not touch the database); `migrate` applies unapplied migration files to the database and records them. The first is a development step whose output is committed; the second runs on every environment.
??  Why do data migrations use `apps.get_model` instead of importing the model?
=> The imported model reflects the *current* code, which may have fields that do not exist yet at that point in the migration history (or have been removed). `apps.get_model` returns the historical model for exactly that migration state, so the migration keeps working forever.
??  How do you add a required column to a huge table without downtime?
=> In steps: add the column as nullable (cheap), deploy code that writes it, backfill existing rows in batches (a data migration or a background job), then add the `NOT NULL` constraint (validated carefully, on PostgreSQL with `NOT VALID` then `VALIDATE`), and remove old code paths later.

## The Admin Site

Register a model and Django generates a **full CRUD interface** with authentication, permissions, search, filters, pagination, history and bulk actions. It is for **trusted staff** (back office, support, data fixes), not for end users.

```python Admin.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


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
        INSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
                          "django.contrib.messages", "django.contrib.staticfiles", "catalog"]
        MIDDLEWARE = ["django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
                      "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
                      "django.contrib.messages.middleware.MessageMiddleware"]
        ROOT_URLCONF = "config.urls"
        TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
                      "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
                                                          "django.contrib.messages.context_processors.messages"]}}]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        STATIC_URL = "static/"
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    """,
    "config/urls.py": "from django.contrib import admin\nfrom django.urls import path\nurlpatterns = [path('admin/', admin.site.urls)]\n",
    "catalog/__init__.py": "",
    "catalog/models.py": """
        from django.db import models


        class Product(models.Model):
            name = models.CharField(max_length=100)
            price = models.DecimalField(max_digits=8, decimal_places=2)
            active = models.BooleanField(default=True)

            def __str__(self):
                return self.name
    """,
    "catalog/admin.py": """
        from django.contrib import admin, messages

        from .models import Product


        @admin.register(Product)
        class ProductAdmin(admin.ModelAdmin):
            list_display = ["name", "price", "active", "price_with_tax"]       # columns in the list page
            list_filter = ["active"]                                           # the filter sidebar
            search_fields = ["name"]                                           # the search box
            list_editable = ["active"]                                         # edit inline from the list
            actions = ["deactivate"]

            @admin.display(description="Price incl. 18% tax")
            def price_with_tax(self, obj):
                return round(obj.price * 118 / 100, 2)

            @admin.action(description="Deactivate selected products")
            def deactivate(self, request, queryset):
                count = queryset.update(active=False)
                self.message_user(request, f"{count} product(s) deactivated", messages.SUCCESS)
    """,
    "catalog/tests.py": """
        from django.contrib.auth import get_user_model
        from django.test import TestCase

        from .models import Product


        class AdminTests(TestCase):
            @classmethod
            def setUpTestData(cls):
                cls.admin = get_user_model().objects.create_superuser("root", "root@example.com", "pw")
                cls.staff = get_user_model().objects.create_user("clerk", password="pw", is_staff=True)       # staff without permissions
                Product.objects.create(name="Pen", price="10.00")
                Product.objects.create(name="Ink", price="45.00")

            def test_anonymous_users_are_redirected_to_login(self):
                response = self.client.get("/admin/catalog/product/")
                self.assertEqual(response.status_code, 302)
                self.assertIn("/admin/login/", response["Location"])

            def test_changelist_shows_the_computed_column_and_search(self):
                self.client.force_login(self.admin)
                page = self.client.get("/admin/catalog/product/")
                self.assertContains(page, "Price incl. 18% tax")
                self.assertContains(page, "11.80")
                found = self.client.get("/admin/catalog/product/?q=ink")
                self.assertContains(found, "Ink")
                self.assertNotContains(found, "Pen</a>")

            def test_action_updates_rows(self):
                self.client.force_login(self.admin)
                ids = list(Product.objects.values_list("pk", flat=True))
                self.client.post("/admin/catalog/product/", {"action": "deactivate", "_selected_action": ids}, follow=True)
                self.assertFalse(Product.objects.filter(active=True).exists())

            def test_permissions_are_enforced_per_model(self):
                self.client.force_login(self.staff)
                self.assertEqual(self.client.get("/admin/catalog/product/").status_code, 403)       # staff, but no permission on Product
    """,
})
output = manage("test", "catalog")
print(re.search(r"Ran \d+ tests?", output)[0], "OK" if re.search(r"^OK", output, re.M) else output[-600:])
```

```output
```

Admin habits for production: **only staff** get accounts; give each person the **minimum model permissions** (groups); turn on **2FA** and put the admin on a **non-obvious path or behind a VPN/IP allow-list**; use `readonly_fields` and `list_select_related` (the admin has N+1 problems too); and never expose it to customers. It is an excellent internal tool and a poor public UI.

??  Is the Django admin suitable as the application's user interface?
=> For trusted staff doing internal data management, yes: it saves weeks. For customers, no: it is a generic CRUD tool with its own look, permission model and risks. Build customer-facing screens with views and templates (or an API plus a front end).
??  How do you restrict what a staff user can do in the admin?
=> Through Django's permission system: model permissions (`add`, `change`, `delete`, `view`) assigned to users or groups, plus `ModelAdmin` methods such as `has_change_permission` and `get_queryset` for object-level rules. A staff flag alone grants no model access.

## Transactions, Signals and Custom Managers

```python Transactions.py
import os
import pathlib
import re
import subprocess
import sys
import textwrap

ROOT = pathlib.Path("shop")


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
        INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "bank"]
        DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    """,
    "bank/__init__.py": "",
    "bank/models.py": """
        from django.db import models, transaction
        from django.db.models import F


        class ActiveManager(models.Manager):                              # a custom manager: reusable, named queries
            def get_queryset(self):
                return super().get_queryset().filter(closed=False)


        class Account(models.Model):
            owner = models.CharField(max_length=50)
            balance = models.IntegerField(default=0)
            closed = models.BooleanField(default=False)

            objects = models.Manager()
            active = ActiveManager()

            class Meta:
                constraints = [models.CheckConstraint(condition=models.Q(balance__gte=0), name="no_overdraft")]


        class AuditEntry(models.Model):
            text = models.CharField(max_length=100)


        def transfer(source_id, target_id, amount):
            with transaction.atomic():                                      # all or nothing
                Account.objects.filter(pk=source_id).update(balance=F("balance") - amount)     # the CHECK constraint refuses an overdraft
                Account.objects.filter(pk=target_id).update(balance=F("balance") + amount)
                AuditEntry.objects.create(text=f"{source_id}->{target_id}: {amount}")
    """,
    "bank/signals.py": """
        from django.db.models.signals import post_save
        from django.dispatch import receiver

        from .models import Account, AuditEntry


        @receiver(post_save, sender=Account)
        def audit_new_accounts(sender, instance, created, **kwargs):
            if created:
                AuditEntry.objects.create(text=f"opened account for {instance.owner}")
    """,
    "bank/apps.py": """
        from django.apps import AppConfig


        class BankConfig(AppConfig):
            name = "bank"

            def ready(self):
                from . import signals  # noqa: F401  (importing registers the receivers)
    """,
    "bank/tests.py": """
        from django.db import IntegrityError
        from django.test import TestCase, TransactionTestCase

        from .models import Account, AuditEntry, transfer


        class TransferTests(TransactionTestCase):
            def test_success_moves_money_and_writes_the_audit_entry(self):
                a, b = Account.objects.create(owner="asha", balance=100), Account.objects.create(owner="ravi", balance=0)
                transfer(a.pk, b.pk, 30)
                self.assertEqual((Account.objects.get(pk=a.pk).balance, Account.objects.get(pk=b.pk).balance), (70, 30))
                self.assertTrue(AuditEntry.objects.filter(text=f"{a.pk}->{b.pk}: 30").exists())

            def test_failure_rolls_everything_back(self):
                a, b = Account.objects.create(owner="asha", balance=10), Account.objects.create(owner="ravi", balance=0)
                with self.assertRaises(IntegrityError):
                    transfer(a.pk, b.pk, 50)                                    # would overdraw: the whole transaction is undone
                self.assertEqual((Account.objects.get(pk=a.pk).balance, Account.objects.get(pk=b.pk).balance), (10, 0))
                self.assertFalse(AuditEntry.objects.filter(text__contains="->").exists())


        class ManagerAndSignalTests(TestCase):
            def test_signal_audits_account_creation(self):
                Account.objects.create(owner="meera")
                self.assertEqual(AuditEntry.objects.get().text, "opened account for meera")

            def test_custom_manager_hides_closed_accounts(self):
                Account.objects.create(owner="open")
                Account.objects.create(owner="gone", closed=True)
                self.assertEqual(list(Account.active.values_list("owner", flat=True)), ["open"])
                self.assertEqual(Account.objects.count(), 2)
    """,
})
settings = (ROOT / "config" / "settings.py").read_text().replace('"bank"]', '"bank.apps.BankConfig"]')
(ROOT / "config" / "settings.py").write_text(settings)
output = manage("test", "bank")
print(re.search(r"Ran \d+ tests?", output)[0], "OK" if re.search(r"^OK", output, re.M) else output[-700:])
```

```output
```

Points to remember:

- **`transaction.atomic()`** wraps a block in one database transaction (nesting makes savepoints). Django runs each request in autocommit by default; set `ATOMIC_REQUESTS = True` (or use `atomic` explicitly) for all-or-nothing views. Use `transaction.on_commit(callback)` to send emails or enqueue jobs **only after** the transaction commits, so a rollback cannot leave a message about a change that never happened.
- **`F()` plus a constraint** makes the overdraft rule impossible to violate under concurrency; checking the balance in Python first would be a race.
- **Signals** decouple reactions (`post_save`), but they hide control flow: prefer explicit service functions, and use signals for cross-app notifications and framework hooks. Register receivers in `AppConfig.ready()`.
- **Custom managers** package reusable queries (`Account.active`); be aware that a manager that filters rows becomes `_default_manager` in places, so keep an unfiltered `objects` first.
- **`TransactionTestCase`** is required to test real commit/rollback behaviour (the plain `TestCase` wraps everything in a transaction it never commits).

!cheat Django ORM cheat sheet ::
| Task | Code |
| --- | --- |
| Create | `Model.objects.create(...)`, `bulk_create([...])`, `obj.save()` |
| Read | `get(pk=1)`, `filter(...)`, `exclude(...)`, `first()`, `exists()`, `count()` |
| Lookups | `name__icontains`, `price__gte`, `status__in=[...]`, `category__name`, `Q(a) \| Q(b)` |
| Update | `obj.save(update_fields=[...])`, `qs.update(stock=F("stock") - 1)` |
| Delete | `obj.delete()`, `qs.delete()` (respects `on_delete`) |
| Aggregate | `aggregate(Sum("x"))`, `annotate(n=Count("rel"))`, `values("cat").annotate(...)` |
| Avoid N+1 | `select_related("fk")`, `prefetch_related("m2m")`, `Prefetch(...)` |
| Transactions | `with transaction.atomic():`, `transaction.on_commit(fn)`, `select_for_update()` |
| Migrations | `makemigrations`, `sqlmigrate app 0001`, `migrate`, `showmigrations` |
| Debug | `str(qs.query)`, `assertNumQueries(n)`, `django-debug-toolbar` |
!end

??  What does `transaction.on_commit` solve?
=> Side effects such as sending email or queuing a job should happen only if the transaction actually commits. `on_commit` schedules the callback to run after a successful commit, so a rollback cannot leave an email or message about data that was never saved.
??  When would you choose `select_for_update()`?
=> For scarce resources that need row locking inside a transaction (the last seat, a stock decrement, an account balance when atomic `F()` expressions are not enough): it locks the selected rows until the transaction ends so concurrent writers wait. Prefer atomic updates or constraints when they suffice.
