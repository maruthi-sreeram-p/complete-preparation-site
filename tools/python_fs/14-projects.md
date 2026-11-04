@part py-core-14 | Core Python · Part 14: Projects | advanced-python
## How to Work Through the Projects

Reading teaches recognition; **building** teaches recall. Each project below is a complete, small program with a specification, a reference solution and a test suite (as `assert`s, so every listing is verified when this page is built). Use them like this:

1. **Read the requirements only.** Close the page and build your own version in a new folder. Time-box it: 60 to 90 minutes.
2. **Write the tests first for the tricky rules** (overdraft, expiry, ordering), then the code.
3. **Compare with the reference solution.** Do not copy: note what differs and why.
4. **Do the extensions.** They are what turns the exercise into interview material.
5. **Explain the design aloud** for five minutes, as if to an interviewer: data structures, invariants, failure modes, complexity, what you would change at 100x the scale.

| Project | Skills it exercises | Part |
| --- | --- | --- |
| A. Bank account manager | Classes, dataclasses, exceptions, money as integers, atomic transfers | 2, 3, 5 |
| B. Log file analyzer | Files, regex, generators, `Counter`, statistics, formatting | 4, 5, 6, 7 |
| C. Concurrent order processor | Threads, locks, queues, idempotency, invariants | 8 |
| D. In-memory key-value store | Data structures, time, TTL and LRU eviction, snapshots, a command parser | 6, 3 |

Each project is a single file so it is easy to run: `python bank.py`. In a real repository you would split it into a package with a `tests/` folder and run `pytest` (Part 12).

!tip Habits to practise in every project :: Type-hint public functions. Use `dataclass(frozen=True)` for records. Raise specific exceptions with helpful messages. Keep I/O at the edges, logic in pure functions. Inject the clock and random source so tests are deterministic. Write the `assert`s as a test list before the implementation.

## Project A: A Bank Account Manager

**Requirements.** Accounts have an id, an owner and a balance. Operations: deposit, withdraw, transfer, statement. Rules: amounts are positive; a withdrawal may not take the balance below zero unless the account has an agreed overdraft limit; a transfer either completes completely or changes nothing; every successful operation is recorded in an immutable transaction log. **Never use floats for money**: store integer paise.

```python Bank.py
from dataclasses import dataclass, field
from itertools import count
from threading import RLock


class BankError(Exception):
    """Base class: callers can catch every banking failure with one except."""


class InsufficientFunds(BankError):
    def __init__(self, account_id, needed, available):
        super().__init__(f"account {account_id}: need {needed / 100:.2f}, available {available / 100:.2f}")


class UnknownAccount(BankError):
    pass


@dataclass(frozen=True)
class Transaction:
    number: int
    kind: str                # "deposit", "withdraw", "transfer-in", "transfer-out"
    amount: int              # paise
    balance_after: int


@dataclass
class Account:
    id: str
    owner: str
    overdraft_limit: int = 0
    balance: int = 0
    history: list[Transaction] = field(default_factory=list)

    def _record(self, number, kind, amount):
        self.history.append(Transaction(number, kind, amount, self.balance))

    def statement(self):
        lines = [f"{t.number:>3} {t.kind:<13} {t.amount / 100:>10.2f} {t.balance_after / 100:>10.2f}" for t in self.history]
        return "\n".join([f"Statement for {self.owner} ({self.id})", *lines])


class Bank:
    def __init__(self):
        self._accounts: dict[str, Account] = {}
        self._numbers = count(1)
        self._lock = RLock()                                  # one lock keeps multi-account operations atomic

    def open(self, account_id, owner, overdraft_limit=0):
        with self._lock:
            if account_id in self._accounts:
                raise BankError(f"account {account_id} already exists")
            self._accounts[account_id] = Account(account_id, owner, overdraft_limit)
            return self._accounts[account_id]

    def _get(self, account_id):
        try:
            return self._accounts[account_id]
        except KeyError:
            raise UnknownAccount(account_id) from None

    @staticmethod
    def _positive(amount):
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("amount must be a positive integer number of paise")

    def deposit(self, account_id, amount):
        self._positive(amount)
        with self._lock:
            account = self._get(account_id)
            account.balance += amount
            account._record(next(self._numbers), "deposit", amount)

    def withdraw(self, account_id, amount):
        self._positive(amount)
        with self._lock:
            account = self._get(account_id)
            if account.balance - amount < -account.overdraft_limit:
                raise InsufficientFunds(account_id, amount, account.balance + account.overdraft_limit)
            account.balance -= amount
            account._record(next(self._numbers), "withdraw", amount)

    def transfer(self, source_id, target_id, amount):
        self._positive(amount)
        with self._lock:                                      # validate everything BEFORE changing anything
            source, target = self._get(source_id), self._get(target_id)
            if source is target:
                raise BankError("cannot transfer to the same account")
            if source.balance - amount < -source.overdraft_limit:
                raise InsufficientFunds(source_id, amount, source.balance + source.overdraft_limit)
            number = next(self._numbers)
            source.balance -= amount
            target.balance += amount
            source._record(number, "transfer-out", amount)
            target._record(number, "transfer-in", amount)

    def total(self):
        with self._lock:
            return sum(a.balance for a in self._accounts.values())


bank = Bank()
asha = bank.open("A-1", "Asha")
ravi = bank.open("R-1", "Ravi", overdraft_limit=50_00)
bank.deposit("A-1", 1000_00)
bank.withdraw("A-1", 250_50)
bank.transfer("A-1", "R-1", 300_00)
bank.withdraw("R-1", 340_00)                                  # uses the overdraft: balance -40.00

assert (asha.balance, ravi.balance) == (449_50, -40_00)
assert bank.total() == 1000_00 - 250_50 - 340_00          # transfers move money, only deposits and withdrawals change the total

for bad in (lambda: bank.withdraw("A-1", 10_000_00), lambda: bank.withdraw("R-1", 20_00),
            lambda: bank.transfer("A-1", "X-9", 1_00), lambda: bank.deposit("A-1", -5), lambda: bank.deposit("A-1", 12.5)):
    try:
        bad()
        raise AssertionError("expected a failure")
    except (BankError, ValueError):
        pass

before = (asha.balance, ravi.balance)
try:
    bank.transfer("A-1", "R-1", 9_999_00)
except InsufficientFunds as error:
    print("rejected:", error)
assert (asha.balance, ravi.balance) == before                 # a failed transfer changed nothing
assert [t.kind for t in asha.history] == ["deposit", "withdraw", "transfer-out"]
print(asha.statement())
```

```output
```

**Design notes.** Integers avoid float drift; validation happens **before** mutation, so a failed transfer cannot leave half an update; an `RLock` around every mutation makes the operations atomic across threads; the transaction log is append-only and immutable; one `BankError` base lets an API layer map all domain errors to a single HTTP 4xx handler.

**Extensions.** (1) Interest: add `apply_monthly_interest()` using `Decimal` and banker's rounding, and explain why. (2) Idempotent transfers: accept an `idempotency_key` and make repeats a no-op. (3) Persist accounts to SQLite through a repository interface and run the same tests against the fake and the real one. (4) Expose it as a FastAPI service (web stage) with `POST /transfers`. (5) Deadlock thought-experiment: if you used one lock **per account** instead of one global lock, how would you order acquisition?

!interview The question behind this project :: "How do you make a money transfer safe?" Validate first, mutate second, in one atomic unit (a lock here; a **database transaction** in a real system); never use floats; record an immutable ledger; make retries idempotent; and explain that with two services you need a saga or outbox, since one lock no longer spans both.

??  Why store money as integers?
=> Binary floats cannot represent most decimal amounts exactly, so totals drift and rounding differs between systems. Integers of the smallest unit (paise, cents) or `Decimal` give exact arithmetic that reconciles with the ledger.
??  How would you make `transfer` safe if each account had its own lock?
=> Acquire both locks in a global order (for example sorted by account id) so two opposite transfers cannot each hold one lock and wait for the other, release in a `finally`, and keep validation and mutation inside the locked section.

## Project B: A Log File Analyzer

**Requirements.** Read a web-server log, one entry per line, `timestamp level service message [key=value ...]`. Report: entries per level; the five most frequent error messages; the slowest five requests (`latency=...ms`); p50 and p95 latency; errors per service; and the busiest minute. It must **stream** the file (it may be gigabytes) and ignore malformed lines while counting them.

```python LogAnalyzer.py
import io
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Iterator

LINE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2} (?P<level>[A-Z]+) (?P<service>[\w-]+) (?P<message>.*?)(?: latency=(?P<latency>\d+)ms)?$")


@dataclass(frozen=True)
class Entry:
    minute: str
    level: str
    service: str
    message: str
    latency_ms: int | None


def parse(lines: Iterable[str], bad: list[str]) -> Iterator[Entry]:
    """A generator: constant memory however large the input."""
    for line in lines:
        match = LINE.match(line.rstrip("\n"))
        if not match:
            if line.strip():
                bad.append(line.strip())
            continue
        latency = match["latency"]
        yield Entry(match["ts"], match["level"], match["service"], match["message"], int(latency) if latency else None)


def analyse(entries: Iterable[Entry]):
    levels, errors, per_minute = Counter(), Counter(), Counter()
    by_service_errors = defaultdict(int)
    latencies, requests = [], []
    for e in entries:                                   # ONE pass over the data
        levels[e.level] += 1
        per_minute[e.minute] += 1
        if e.level == "ERROR":
            errors[e.message] += 1
            by_service_errors[e.service] += 1
        if e.latency_ms is not None:
            latencies.append(e.latency_ms)
            requests.append(e)
    cuts = statistics.quantiles(latencies, n=100, method="inclusive")
    return {
        "levels": dict(levels),
        "top_errors": errors.most_common(2),
        "errors_by_service": dict(by_service_errors),
        "p50": cuts[49], "p95": cuts[94],
        "slowest": [(e.message, e.latency_ms) for e in sorted(requests, key=lambda r: r.latency_ms, reverse=True)[:3]],
        "busiest_minute": per_minute.most_common(1)[0],
    }


LOG = """\
2026-11-04 10:00:01 INFO api GET /items latency=42ms
2026-11-04 10:00:07 INFO api GET /items/7 latency=35ms
2026-11-04 10:00:12 ERROR payments timeout calling bank
2026-11-04 10:01:03 INFO api POST /orders latency=310ms
this line is garbage
2026-11-04 10:01:09 ERROR payments timeout calling bank
2026-11-04 10:01:15 WARN api slow response GET /search latency=900ms
2026-11-04 10:01:44 ERROR api database connection reset
2026-11-04 10:02:00 INFO api GET /items latency=40ms
2026-11-04 10:02:30 INFO api GET /health latency=3ms
"""

bad: list[str] = []
report = analyse(parse(io.StringIO(LOG), bad))

assert report["levels"] == {"INFO": 5, "ERROR": 3, "WARN": 1}
assert report["top_errors"][0] == ("timeout calling bank", 2)
assert report["errors_by_service"] == {"payments": 2, "api": 1}
assert report["slowest"][0] == ("slow response GET /search", 900)
assert report["busiest_minute"] == ("2026-11-04 10:01", 4)
assert bad == ["this line is garbage"]
assert 3 < report["p95"] <= 900

for key, value in report.items():
    print(f"{key:<18} {value}")
print("malformed lines skipped:", len(bad))
```

```output
```

**Design notes.** `parse` is a generator and `analyse` consumes it once, so memory is O(distinct messages), not O(lines). The regex has **named groups** and one optional trailing group; `Counter.most_common`, `defaultdict` and `statistics.quantiles` replace hand-written loops. Malformed input is *counted and reported*, never silently dropped and never fatal.

**Extensions.** (1) Add a command line (`argparse`: file path, `--since`, `--level`, `--format json|table`) and read `-` as standard input. (2) Handle gzip files (`gzip.open(path, "rt")`) and rotate through several files lazily. (3) Compute p95 in constant memory with a streaming algorithm (t-digest or a fixed histogram) and compare with the exact value. (4) Parse in parallel with `ProcessPoolExecutor` by splitting the file on line boundaries, and measure when it helps. (5) Emit Prometheus metrics instead of a report.

??  Why write `parse` as a generator?
=> A generator reads and yields one line at a time, so memory stays constant for any file size, processing starts immediately, and stages compose (parse, filter, aggregate) without intermediate lists. A list-returning function would load the whole file.
??  How would you compute the p95 of latency over billions of entries?
=> You cannot keep every value. Use a streaming quantile sketch (t-digest, HdrHistogram) or fixed-width histogram buckets, accept a small bounded error, and merge sketches from parallel workers. Exact quantiles need sorting or selection over all data.

## Project C: A Concurrent Order Processor

**Requirements.** Orders arrive on a queue from many producers; a pool of workers processes them. A worker reserves stock, charges (simulated) payment and records the result. Rules: **never oversell**; the same order delivered twice (at-least-once delivery) must be processed **once** (idempotency); failures of the payment step must **release** the reserved stock; shutdown must drain the queue.

```python OrderProcessor.py
import queue
import random
import threading
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    sku: str
    quantity: int


class Inventory:
    def __init__(self, stock):
        self._stock = dict(stock)
        self._lock = threading.Lock()

    def reserve(self, sku, quantity):
        with self._lock:                                 # check-then-act must be ONE critical section
            if self._stock.get(sku, 0) < quantity:
                return False
            self._stock[sku] -= quantity
            return True

    def release(self, sku, quantity):
        with self._lock:
            self._stock[sku] += quantity

    def snapshot(self):
        with self._lock:
            return dict(self._stock)


class Processor:
    def __init__(self, inventory, payment, workers=4):
        self.inventory, self.payment = inventory, payment
        self.orders = queue.Queue()
        self.results = {}                                # order id -> outcome
        self.duplicates = []
        self._lock = threading.Lock()
        self._threads = [threading.Thread(target=self._work) for _ in range(workers)]

    def start(self):
        for t in self._threads:
            t.start()

    def submit(self, order):
        self.orders.put(order)

    def stop(self):
        for _ in self._threads:
            self.orders.put(None)                        # one poison pill per worker
        for t in self._threads:
            t.join()                                     # the queue is drained before the workers exit

    def _work(self):
        while (order := self.orders.get()) is not None:
            with self._lock:                             # idempotency: claim the order id atomically
                if order.id in self.results:                     # duplicate delivery: keep the first outcome
                    self.duplicates.append(order.id)
                    continue
                self.results[order.id] = "processing"
            outcome = self._process(order)
            with self._lock:
                self.results[order.id] = outcome

    def _process(self, order):
        if not self.inventory.reserve(order.sku, order.quantity):
            return "out-of-stock"
        try:
            self.payment(order)
        except Exception:
            self.inventory.release(order.sku, order.quantity)       # compensate: never leak reserved stock
            return "payment-failed"
        return "confirmed"


initial = {"pen": 50, "ink": 10}
inventory = Inventory(initial)
rng = random.Random(7)                                    # seeded: the same orders every run


def flaky_payment(order):
    if order.id.endswith("13"):
        raise RuntimeError("card declined")


processor = Processor(inventory, flaky_payment, workers=4)
processor.start()
orders = [Order(f"O-{i}", rng.choice(["pen", "ink"]), rng.randint(1, 3)) for i in range(60)]
for order in orders:
    processor.submit(order)
for order in orders[:5]:                                  # at-least-once delivery: the first five arrive twice
    processor.submit(order)
processor.stop()

outcomes = Counter(processor.results.values())
sold = Counter()
for order in orders:
    if processor.results[order.id] == "confirmed":
        sold[order.sku] += order.quantity
remaining = inventory.snapshot()

assert len(processor.results) == 60 and "processing" not in outcomes
assert all(remaining[sku] >= 0 for sku in initial)                         # never oversold
assert all(sold[sku] + remaining[sku] == initial[sku] for sku in initial)  # every unit is accounted for
assert sorted(processor.duplicates) == sorted(o.id for o in orders[:5])              # duplicates were ignored, not re-processed
assert processor.results["O-13"] in {"payment-failed", "out-of-stock"}          # which one depends on timing, never "confirmed"
assert outcomes["out-of-stock"] > 0                                         # demand exceeds stock, so some orders must lose
print("some orders confirmed, some lost the race for stock:", {"confirmed", "out-of-stock"} <= set(outcomes))
print("never oversold:", all(remaining[s] >= 0 for s in initial), "| units conserved:", all(sold[s] + remaining[s] == initial[s] for s in initial))
print("duplicate deliveries ignored:", len(processor.duplicates))
```

```output
```

The program prints **invariants**, not which orders won the last units, because that depends on thread timing; a concurrent program is verified by properties that must hold on **every** interleaving. Notice the design choices: one lock makes each stock check-and-decrement atomic; the order id is *claimed* before processing (idempotency); the compensation (`release`) runs when payment fails; poison pills let workers drain and exit.

**Extensions.** (1) Replace threads with `asyncio` and `asyncio.Queue`, using an `asyncio.Lock`, and compare. (2) Add a retry with exponential backoff and jitter for transient payment errors only. (3) Add a **dead-letter queue** for orders that fail repeatedly. (4) Make the idempotency store durable (SQLite or Redis `SET NX`), and discuss why an in-memory dictionary is not enough across restarts. (5) Run 8 workers under a stress loop and prove the invariants still hold; remove the lock and watch them fail.

!realworld This is the shape of every message consumer :: Replace the `queue.Queue` with a Kafka or RabbitMQ consumer and the code is an order service: at-least-once delivery means duplicates, so handlers must be idempotent; failed steps need compensation; shutdown must drain in-flight work. The Kafka and Celery parts of this tree build on exactly this structure.

??  Why does the program check invariants instead of exact outcomes?
=> Thread scheduling is non-deterministic, so which order grabs the last unit varies between runs. Correctness for concurrent code is expressed as properties that must always hold (no overselling, conservation of units, no duplicate processing), and tests assert those.
??  How do you make a consumer idempotent?
=> Record each processed message id (or a natural idempotency key) in durable storage atomically with the side effect, and skip ids already seen. Use a unique constraint or a conditional write (`INSERT ... ON CONFLICT DO NOTHING`, Redis `SET NX`) so two workers cannot both claim it.

## Project D: An In-Memory Key-Value Store

**Requirements.** A Redis-like store: `SET`, `GET`, `DEL`, `INCR`, `EXPIRE`/`TTL`, a maximum size with **LRU eviction**, `SNAPSHOT` to disk and restore, and a text command interface (`execute("SET name asha")`). It must be thread-safe, and its time source must be **injectable** so expiry is testable without sleeping.

```python KeyValueStore.py
import json
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Callable


class KeyValueStore:
    def __init__(self, max_items: int = 1000, clock: Callable[[], float] = time.monotonic):
        self._data: OrderedDict[str, str] = OrderedDict()      # order = recency: oldest first
        self._expires: dict[str, float] = {}
        self._max, self._clock = max_items, clock
        self._lock = threading.RLock()

    # ---- internals (call with the lock held)
    def _alive(self, key):
        deadline = self._expires.get(key)
        if deadline is not None and self._clock() >= deadline:
            self._data.pop(key, None)
            del self._expires[key]                            # lazy expiry: removed when touched
            return False
        return key in self._data

    # ---- commands
    def set(self, key, value, ttl: float | None = None):
        with self._lock:
            self._data[key] = str(value)
            self._data.move_to_end(key)
            if ttl is None:
                self._expires.pop(key, None)
            else:
                self._expires[key] = self._clock() + ttl
            while len(self._data) > self._max:                # evict the least recently used
                oldest, _ = self._data.popitem(last=False)
                self._expires.pop(oldest, None)

    def get(self, key):
        with self._lock:
            if not self._alive(key):
                return None
            self._data.move_to_end(key)
            return self._data[key]

    def delete(self, key):
        with self._lock:
            existed = self._alive(key)
            self._data.pop(key, None)
            self._expires.pop(key, None)
            return existed

    def incr(self, key, by=1):
        with self._lock:                                      # read-modify-write in ONE critical section
            current = int(self.get(key) or 0)
            self.set(key, current + by, None if key not in self._expires else self._expires[key] - self._clock())
            return current + by

    def ttl(self, key):
        with self._lock:
            if not self._alive(key):
                return -2                                     # Redis convention: -2 missing, -1 no expiry
            deadline = self._expires.get(key)
            return -1 if deadline is None else round(deadline - self._clock())

    def snapshot(self, path: Path):
        with self._lock:
            now = self._clock()
            live = {k: self._data[k] for k in list(self._data) if self._alive(k)}      # list(): _alive may delete entries
            ttls = {k: self._expires[k] - now for k in live if k in self._expires}
            path.write_text(json.dumps({"data": live, "ttl": ttls}), encoding="utf-8")

    @classmethod
    def restore(cls, path: Path, **kwargs):
        store = cls(**kwargs)
        saved = json.loads(path.read_text(encoding="utf-8"))
        for key, value in saved["data"].items():
            store.set(key, value, saved["ttl"].get(key))
        return store

    def execute(self, line: str) -> str:
        """A tiny text protocol: SET k v [EX seconds] | GET k | DEL k | INCR k | TTL k"""
        command, *args = line.split()
        match command.upper(), args:
            case "SET", [key, value]:
                self.set(key, value)
                return "OK"
            case "SET", [key, value, "EX", seconds]:
                self.set(key, value, float(seconds))
                return "OK"
            case "GET", [key]:
                value = self.get(key)
                return "(nil)" if value is None else value
            case "DEL", [key]:
                return str(int(self.delete(key)))
            case "INCR", [key]:
                return str(self.incr(key))
            case "TTL", [key]:
                return str(self.ttl(key))
            case _:
                return f"ERR unknown or malformed command: {line!r}"


class FakeClock:                                               # tests move time forward without sleeping
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


clock = FakeClock()
kv = KeyValueStore(max_items=3, clock=clock)

assert kv.execute("SET name asha") == "OK" and kv.execute("GET name") == "asha"
assert kv.execute("INCR visits") == "1" and kv.execute("INCR visits") == "2"
assert kv.execute("DEL missing") == "0" and kv.execute("GET missing") == "(nil)"
assert kv.execute("FLY away").startswith("ERR")

kv.execute("SET session abc EX 30")
assert kv.execute("TTL session") == "30"
clock.now += 31
assert kv.execute("GET session") == "(nil)" and kv.execute("TTL session") == "-2"        # expired without sleeping

kv.set("a", 1); kv.set("b", 2); kv.set("c", 3)
kv.get("a")                                                    # "a" becomes the most recently used
kv.set("d", 4)                                                 # over capacity: "b" is the least recently used
assert kv.get("b") is None and kv.get("a") == "1" and kv.get("d") == "4"

kv.set("temp", "x", ttl=100)
path = Path("dump.json")
kv.snapshot(path)
clone = KeyValueStore.restore(path, max_items=10, clock=clock)
assert clone.get("temp") == "x" and clone.ttl("temp") == 100

threads = [threading.Thread(target=lambda: [clone.incr("counter") for _ in range(500)]) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
assert clone.get("counter") == "2000"                          # no lost updates

for command in ("SET city pune", "INCR hits", "INCR hits", "GET city", "GET hits", "TTL city"):
    print(f"> {command:<14} {clone.execute(command)}")
print("all checks passed")
```

```output
```

**Design notes.** An `OrderedDict` is both the dictionary and the recency list, so `get` and `set` are O(1) with `move_to_end` and eviction is `popitem(last=False)`. **Lazy expiry** (check on access) is how Redis starts; real Redis also samples keys in the background so memory from untouched expired keys is reclaimed. The injected clock makes time-dependent behaviour fast and deterministic to test. One re-entrant lock keeps `incr` atomic.

**Extensions.** (1) Add a **write-ahead log**: append every mutation to a file before applying it, and rebuild state on start by replaying; discuss `fsync` cost versus durability. (2) Add `LPUSH`/`LRANGE` list values and `HSET` hashes with a type-error rule. (3) Serve the protocol over TCP with `asyncio.start_server` (Part 9) and try it with `telnet`. (4) Implement active expiry with a background `asyncio` task or a min-heap of deadlines. (5) Shard keys across several stores with consistent hashing and discuss rebalancing.

!interview Design questions this project prepares for :: "Design an LRU cache" (here), "Design a rate limiter" (a TTL counter per key), "Design a distributed cache" (shard with consistent hashing, replicate for availability, choose eviction and expiry), "How does Redis expire keys?" (lazy plus sampled active expiry), "How does Redis persist?" (RDB snapshots and the append-only log, which is the snapshot and write-ahead log extensions above).

??  What data structures give O(1) get, set and LRU eviction?
=> A hash map for lookup combined with a doubly linked list ordered by recency, so a touched key moves to one end and the other end is evicted. `OrderedDict` provides both in one structure in Python.
??  Why inject the clock into the store?
=> Tests can set the time instead of sleeping, so expiry tests are instant and deterministic, and the behaviour at exact boundaries (the instant a key expires) can be checked precisely. The same trick applies to randomness, UUIDs and any non-deterministic dependency.
??  What is lazy versus active expiry?
=> Lazy expiry checks a key's deadline when it is accessed and removes it then; it costs nothing for keys nobody reads but leaves their memory occupied. Active expiry runs a background process that scans or samples keys (or uses a heap of deadlines) and reclaims memory proactively. Real systems combine both.
