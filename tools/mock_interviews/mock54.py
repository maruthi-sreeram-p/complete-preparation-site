"""Day 54 - Mock interview 2: Databases and System Design."""
import pathlib
import runpy

_c = runpy.run_path(str(pathlib.Path(__file__).with_name("common.py")))
q, section, info, WRITTEN_FOR_SITE = _c["q"], _c["section"], _c["info"], _c["WRITTEN_FOR_SITE"]

HOW = info("mock-how", "How to run this mock", WRITTEN_FOR_SITE + """

**Format**

1. Databases: answer each question aloud in about 60 to 90 seconds, then compare with **Show answer**.
2. System design: set a **40-minute timer** for each design question. Talk through it with a pen and paper (or a whiteboard), *then* open the answer. Use this order every time:
   1. **Clarify** requirements (what must it do, how many users, what matters most: speed, correctness, cost).
   2. **Estimate** the size (requests per second, storage).
   3. **API and data model.**
   4. **High-level design** (boxes and arrows).
   5. **Deep dive** on the one or two hard parts, and say the **trade-offs** out loud.
3. Add every half-right or missed question to your weak-answers list.

There is rarely one right answer in design. Interviewers score your **reasoning**: do you ask first, estimate, name trade-offs and notice failure modes?""")

DB = section("mock-databases", "Round 1: Databases, what the interviewer will ask", "Examples are standard SQL; where PostgreSQL and MySQL differ, the answer says so.", [
    q("Basic", "What are the ACID properties? Give an example.", """
Take a bank transfer of 100 from A to B.
- **Atomicity**: both the debit and the credit happen, or neither does.
- **Consistency**: the transaction moves the database from one valid state to another (constraints hold, total money is unchanged).
- **Isolation**: concurrent transactions do not see each other's half-finished work (how much is set by the isolation level).
- **Durability**: once committed, the change survives a crash (write-ahead log)."""),
    q("Medium", "Explain the isolation levels and the problems they prevent.", """
| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read uncommitted | possible | possible | possible |
| Read committed | no | possible | possible |
| Repeatable read | no | no | possible by the standard (PostgreSQL and InnoDB prevent most) |
| Serializable | no | no | no |

- **Dirty read**: you read data another transaction has not committed.
- **Non-repeatable read**: you read a row twice and get different values because someone committed in between.
- **Phantom**: the same query returns **different rows** the second time (new rows appeared).

Defaults: PostgreSQL uses *Read committed*; MySQL InnoDB uses *Repeatable read*. Higher isolation = fewer anomalies but more locking or retries."""),
    q("Medium", "How does an index work? What is a composite index?", """
Most indexes are **B-trees**: a sorted structure that finds a key in O(log n) and lets the database read a range in order, instead of scanning the whole table.

A **composite** index on `(a, b, c)` is sorted by `a`, then `b`, then `c`. It helps queries that filter on `a`, on `a, b`, or on `a, b, c` (the **leftmost prefix** rule), but generally **not** on `b` alone. Put equality columns first and the range column last.

A **covering** index contains every column the query needs, so the table is not read at all (index-only scan). Indexes are not free: each one slows `INSERT`/`UPDATE`/`DELETE` and uses space, so index for real queries, not for every column."""),
    q("Medium", "How do you find out why a query is slow?", """
Run `EXPLAIN` to see the plan, and `EXPLAIN ANALYZE` to run it and see **actual** times and row counts (careful with `UPDATE`/`DELETE`: it really executes them).

Look for: a sequential scan on a big table where you expected an index; a big gap between **estimated** and **actual** rows (stale statistics, run `ANALYZE`); sorts or hashes spilling to disk; a nested loop over huge inputs. Then: add or fix an index, rewrite the query, fetch fewer columns/rows, or paginate."""),
    q("Basic", "What are the normal forms? When would you denormalise?", """
- **1NF**: each column holds a single value, no repeating groups.
- **2NF**: every non-key column depends on the **whole** key (no partial dependency on part of a composite key).
- **3NF**: non-key columns depend on **nothing but the key** (no transitive dependency).

"The key, the whole key, and nothing but the key." Normalising removes duplication and update anomalies. **Denormalise** deliberately when reads dominate and joins are too costly (a stored order total, a reporting table), accepting that you must keep the copies consistent."""),
    q("Basic", "INNER, LEFT, RIGHT, FULL and CROSS join: what does each return?", """
- **INNER**: only rows with a match in both tables.
- **LEFT**: all rows of the left table, with the right table's columns `NULL` where there is no match.
- **RIGHT**: the mirror of LEFT. **FULL**: all rows of both sides.
- **CROSS**: every combination (the Cartesian product), N x M rows.
- **Self join**: a table joined to itself (employee and manager).

Trap: after a `LEFT JOIN`, a `WHERE right.col = 'x'` removes the `NULL` rows, turning it into an inner join. Put that condition in the `ON` clause."""),
    q("Medium", "Optimistic vs pessimistic locking. When do you use each?", """
**Optimistic**: assume conflicts are rare. Keep a `version` column; the update is `UPDATE ... SET ..., version = version + 1 WHERE id = ? AND version = ?`. Zero rows updated means someone else changed it first, so you report a conflict (HTTP 409) or retry. No locks are held. In JPA this is `@Version`.

**Pessimistic**: lock the row up front with `SELECT ... FOR UPDATE`, so others wait. Use it when conflicts are **frequent** and a retry is expensive (stock reservation), but keep transactions short to avoid waits and deadlocks."""),
    q("Medium", "Why is `OFFSET` pagination slow on large tables? What is the alternative?", """
`LIMIT 20 OFFSET 100000` makes the database read and throw away 100,000 rows each time, so deep pages get slower. It is also unstable: if rows are inserted while the user pages, items shift or repeat.

**Keyset (seek) pagination** remembers the last row of the previous page: `WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC LIMIT 20`, backed by an index on those columns. It is fast at any depth and stable. The cost: no jumping to "page 57", only next/previous."""),
    q("Medium", "SQL or NoSQL? How do you choose?", """
Start with a **relational database** unless you have a reason not to: transactions, joins, constraints and flexible queries are hard to rebuild. Choose NoSQL for a specific need:
- **Key-value** (Redis, DynamoDB): very fast lookups by key, caching, sessions.
- **Document** (MongoDB): self-contained, varied records read as a whole.
- **Wide-column** (Cassandra): huge write volume, horizontal scale, simple access patterns.
- **Graph**: relationships are the question (friends of friends).

"NoSQL is faster" is a myth; you trade away joins, transactions or consistency to scale a specific access pattern."""),
    q("Medium", "Auto-increment id or UUID for the primary key?", """
A `bigint` identity is small, ordered (good index locality) and fast, but it is guessable and reveals counts, and is awkward across several databases. A random UUID (v4) is globally unique and unguessable, but is bigger and its random order causes **page splits** and poor cache use in a B-tree index.

A **time-ordered UUID (v7)** gives uniqueness *and* index locality. A common pattern is an internal `bigint` key plus a public UUID used in URLs."""),
])

SQL = section("mock-sql", "SQL questions you will be asked to write", "Write the query on paper first, then check.", [
    q("Medium", "Write a query for the **second highest salary** in `employee(id, salary)`. What if there is no second one?", """
```sql
SELECT MAX(salary) AS second_highest
FROM employee
WHERE salary < (SELECT MAX(salary) FROM employee);
```
It returns `NULL` when there is no second distinct salary, which is usually what you want. Alternatives: `SELECT DISTINCT salary FROM employee ORDER BY salary DESC LIMIT 1 OFFSET 1`, or a window function for the **Nth** highest:
```sql
SELECT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk FROM employee
) t WHERE rnk = 2;
```
Ask the interviewer: do duplicates count as one? (`DENSE_RANK` vs `RANK` vs `ROW_NUMBER`.)"""),
    q("Medium", "Find the highest-paid employee **in each department**, including ties.", """
```sql
SELECT name, department_id, salary
FROM (
  SELECT e.*, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk
  FROM employee e
) t
WHERE rnk = 1;
```
`PARTITION BY` restarts the ranking per department. `RANK` gives ties the same rank, so all tied top earners appear. `ROW_NUMBER` would pick only one."""),
    q("Medium", "Delete duplicate rows from `person(id, email)`, keeping the one with the lowest id.", """
```sql
DELETE FROM person
WHERE id NOT IN (
  SELECT MIN(id) FROM person GROUP BY email
);
```
In MySQL you cannot select from the table you are deleting from in a subquery; wrap it in a derived table (`SELECT min_id FROM (SELECT MIN(id) AS min_id FROM person GROUP BY email) x`). Then add a **unique constraint** on `email` so it cannot happen again."""),
    q("Medium", "Find employees who earn more than their manager (`employee(id, name, salary, manager_id)`).", """
```sql
SELECT e.name
FROM employee e
JOIN employee m ON e.manager_id = m.id
WHERE e.salary > m.salary;
```
A **self join**: the same table twice under two aliases, one for the employee and one for the manager."""),
])

DBTRICK = section("mock-db-tricky", "Round 2: Tricky database questions", "Each one hides a trap.", [
    q("Tricky", "You added an index on `last_name`, but `WHERE LOWER(last_name) = 'rao'` is still slow. Why? Name other reasons an index is ignored.", """
Wrapping the column in a function means the stored (sorted) values cannot be searched directly. Fix: compare the column as it is, or create a **functional index** on `LOWER(last_name)`.

Other causes: a leading wildcard (`LIKE '%rao'`); an **implicit type conversion** (comparing a number column with a string); `OR` across different columns; a low-selectivity condition (a boolean that matches half the table, so scanning is cheaper); using the second column of a composite index without the first; and stale statistics."""),
    q("Tricky", "`SELECT * FROM a WHERE id NOT IN (SELECT a_id FROM b)` returns **no rows**, although some ids are not in `b`. Why?", """
If the subquery returns even one `NULL`, `x NOT IN (..., NULL)` evaluates to *unknown*, never true, so nothing is returned. SQL uses three-valued logic.

Use `NOT EXISTS`:
```sql
SELECT * FROM a WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id);
```
or make sure the subquery column is `NOT NULL`."""),
    q("Tricky", "`COUNT(*)` vs `COUNT(column)` vs `COUNT(DISTINCT column)`. And `WHERE` vs `HAVING`?", """
`COUNT(*)` counts rows. `COUNT(column)` counts rows where the column is **not NULL**. `COUNT(DISTINCT column)` counts distinct non-null values.

`WHERE` filters **rows before** grouping; `HAVING` filters **groups after** aggregation, so only `HAVING` can use `COUNT(*) > 5`. Logical order: `FROM` / `JOIN` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `SELECT` -> `ORDER BY` -> `LIMIT`. That is why you cannot use a `SELECT` alias in `WHERE`."""),
    q("Tricky", "Two transactions deadlock. What happened, and how do you prevent it?", """
Transaction 1 locks row A and waits for B; transaction 2 locks B and waits for A. Neither can proceed. The database detects the cycle and **kills one** (the victim gets an error).

Prevention: always lock rows in the **same order**, keep transactions **short**, do not wait for user input inside a transaction, use proper indexes (fewer rows locked), and **retry** the victim transaction in the application."""),
    q("Tricky", "A table has an index on `(country, city)`. Does `WHERE city = 'Pune'` use it?", """
Normally **no** (or only by scanning the whole index): the index is sorted by `country` first, so rows for one city are scattered. The leftmost-prefix rule means it supports `country` or `country + city`. Some databases can do an "index skip scan" when `country` has few distinct values. If you need to search by city alone, add an index on `city`."""),
    q("Tricky", "In a LEFT JOIN, why does adding `WHERE o.status = 'PAID'` lose the customers with no orders?", """
Customers without orders have `NULL` in every `o.` column. `NULL = 'PAID'` is not true, so the `WHERE` removes those rows: the left join silently became an inner join. Move the condition into the join: `LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'PAID'`."""),
])

DESIGN = section("mock-system-design", "Round 3: System design, what the interviewer will ask", "Do each of these on paper for 30 to 40 minutes first. The answers are outlines to compare with, not scripts.", [
    q("Medium", "How do you approach any system design question?", """
1. **Clarify**: functional requirements, scale (users, requests/second), and priorities (latency? availability? consistency?).
2. **Estimate**: requests per second, read/write ratio, storage per year. It decides whether you need a cache or sharding.
3. **API and data model**: the main endpoints and tables.
4. **High-level design**: client, load balancer, stateless services, database, cache, queue.
5. **Deep dive** on the hardest part (the interviewer will often steer you).
6. **Bottlenecks and failures**: what breaks first, what happens when a node dies, how you monitor it.

Say trade-offs out loud ("I chose X over Y because...")."""),
    q("Medium", "Design a URL shortener.", """
**Requirements**: create a short link, redirect fast, optional expiry. **Estimate**: 100 million new links per month is about 40 writes/second; reads are ~100x more, about 4,000 redirects/second, so it is **read-heavy**.

**API**: `POST /links {url}` returns a short code; `GET /{code}` returns a redirect (`301` is cacheable by browsers but hides later clicks from you; `302` lets you count clicks).

**Short code**: 7 characters of base62 (a-z, A-Z, 0-9) give 62^7, about 3.5 trillion, combinations. Generate it by base62-encoding a unique id (a counter or ID service, so no collisions) or by hashing and checking for a collision.

**Storage**: a key-value shape (`code -> url, created, expiry`). A simple relational table or DynamoDB-style store is fine. **Cache** the hot codes in Redis (cache-aside). Put several stateless servers behind a load balancer.

**Deep dive**: unique ids across servers (ranges handed to each server, or a snowflake-style id), analytics through a queue so redirects stay fast, abuse and rate limiting."""),
    q("Medium", "Design a rate limiter.", """
**Where**: at the API gateway (and optionally per service). **Key**: user id, API key or IP.

**Algorithms**:
- *Fixed window counter*: simple, but allows a burst of 2x at the window boundary.
- *Sliding window log*: exact, but stores every timestamp.
- *Sliding window counter*: approximates with two counters, cheap.
- **Token bucket**: the bucket refills at a steady rate and each request takes a token, so it allows short **bursts** up to the bucket size. A common default.

**Distributed**: keep counters in **Redis**. A read-then-write from several servers races, so do it atomically (`INCR` + `EXPIRE`, or a **Lua script**). Return `429 Too Many Requests` with a `Retry-After` header. Decide what happens if Redis is down: **fail open** (allow) or **fail closed** (block)."""),
    q("Medium", "Explain caching strategies. How do you keep the cache and the database consistent?", """
- **Cache-aside** (most common): read the cache; on a miss read the database and fill the cache. The application manages it.
- **Read-through**: the cache loads from the database itself.
- **Write-through**: write to the cache and the database together: consistent, slower writes.
- **Write-back**: write to the cache and flush later: fast, but data can be lost.

Consistency: set a **TTL**, and on a write **delete** the cached key (deleting is safer than updating it, because concurrent updates can leave stale data). Accept that the cache can be briefly stale, and decide per data type how stale is acceptable. Eviction is usually **LRU** or LFU. Watch the hit ratio."""),
    q("Medium", "The database is the bottleneck. How do you scale it?", """
In order of effort: (1) fix queries and add **indexes**; (2) add a **cache** for hot reads; (3) **read replicas** for read-heavy load (replication is usually asynchronous, so a read right after a write may be stale: "read your own writes" needs care); (4) move heavy work to **queues**; (5) **partition / shard** by a key (user id) when one machine cannot hold the data or write load.

Sharding has costs: cross-shard joins and transactions are hard, re-sharding is painful, and a bad key creates **hot spots**. Do the earlier steps first. Also scale the app tier by keeping services **stateless** behind a load balancer."""),
    q("Medium", "Explain the CAP theorem and eventual consistency.", """
In a distributed system a **network partition** will eventually happen. During one, you must choose: stay **consistent** (reject some requests, so give up availability) or stay **available** (answer, possibly with stale data, so give up consistency). A banking ledger chooses consistency; a social feed chooses availability.

**Eventual consistency**: if no new writes arrive, all replicas converge to the same value after some time. It is fine for likes and feeds, not for account balances. Without a partition you can have both, but there is still a latency versus consistency trade-off."""),
    q("Medium", "Why use a message queue such as Kafka? What delivery guarantees exist?", """
It **decouples** producers from consumers, absorbs traffic spikes, lets consumers fail and catch up, and allows several independent consumers of the same events (Kafka also lets you **replay**).

Guarantees: *at-most-once* (may lose), *at-least-once* (may duplicate), and *exactly-once* (see the tricky round). Most systems use **at-least-once plus idempotent consumers**. Kafka keeps order **per partition**, so choose a key (such as the order id) that keeps related events in one partition. Add **retry topics and a dead-letter queue** for messages that keep failing."""),
    q("Medium", "Design a payment endpoint so a customer is never charged twice, even if the client retries.", """
Use an **idempotency key**. The client sends a unique `Idempotency-Key` header (a UUID) with `POST /payments`. The server stores the key with the request result in a table with a **unique constraint** on the key.

First request: process, store the result under the key. Retry with the same key: return the **stored result** without charging again. Do the "insert key" and the charge state change in one database transaction, and handle two requests with the same key arriving at the same time (the unique constraint makes one lose). Expire old keys after a day or so."""),
])

SDTRICK = section("mock-design-tricky", "Round 4: Tricky design questions", "The follow-ups that separate a memorised answer from an understood one.", [
    q("Tricky", "'CAP: pick any two of three.' Is that correct?", """
It is a common simplification, and misleading. **Partition tolerance is not optional**: networks do fail, so a distributed system must tolerate partitions. The real choice is between **C and A while a partition lasts**. When there is no partition you can have both. A fuller view is **PACELC**: during a partition choose A or C, **E**lse (normally) choose between **L**atency and **C**onsistency."""),
    q("Tricky", "Can you guarantee exactly-once delivery?", """
Not in the general case over an unreliable network: a sender cannot know whether a lost acknowledgement means a lost message or a lost reply. What systems offer is **effectively once** = *at-least-once delivery* + *idempotent processing* (a dedupe key, or a unique constraint that makes a repeated insert harmless). Kafka's "exactly-once" works inside Kafka (idempotent producer and transactions); once you write to an external database, you still need idempotency there."""),
    q("Tricky", "A very popular cache key expires and thousands of requests hit the database at once. What is this and how do you stop it?", """
A **cache stampede** (thundering herd). Remedies: let only one request rebuild the value while others wait or get the **stale** value (a lock or single-flight); add **random jitter** to TTLs so keys do not expire together; refresh **before** expiry; pre-warm known hot keys."""),
    q("Tricky", "You shard users by `user_id`, but one celebrity account gets most of the traffic. What goes wrong?", """
A **hot partition**: the shard that holds that key is overloaded while others idle. Remedies: cache that key aggressively (and replicate reads), split the hot key into several sub-keys (`id#1..#n`) and aggregate, choose a key with better distribution, or handle celebrities through a separate path. Bad shard keys (a date, a country, a low-cardinality field) cause the same problem."""),
    q("Tricky", "Why is consistent hashing used instead of `hash(key) % N` when you add or remove servers?", """
With `% N`, changing N remaps **almost every key**, so a cache cluster would lose nearly all its entries at once. With consistent hashing, servers and keys sit on a ring, and a key belongs to the next server clockwise; adding or removing a server moves only about **1/N** of the keys. **Virtual nodes** (each server appears many times on the ring) even out the load."""),
    q("Tricky", "Your service calls another service that has become slow. What do you do?", """
Never wait forever: set **timeouts**. Retry only **idempotent** calls, with **exponential backoff and jitter**, and a retry budget (retries multiply load on an already struggling service). Add a **circuit breaker**: after repeated failures stop calling for a while and fail fast or return a fallback. Use **bulkheads** (separate thread pools or connection limits) so one slow dependency cannot use up all your threads. Monitor latency percentiles, not only averages."""),
    q("Tricky", "You must update the database **and** publish an event, atomically. How?", """
Two separate systems cannot share one transaction (the dual-write problem: one can succeed and the other fail). Use the **transactional outbox**: in the **same database transaction**, write the business row and an `outbox` row describing the event. A separate process (a poller or change-data-capture such as Debezium) reads the outbox and publishes to Kafka, retrying until it succeeds. Consumers must be **idempotent**, because the event can be published more than once."""),
    q("Tricky", "A business operation spans three microservices and the third one fails. How do you undo the first two?", """
A distributed transaction (two-phase commit) is usually too slow and fragile. Use a **saga**: a sequence of local transactions, each with a **compensating action** (refund, release stock). Either **choreography** (services react to each other's events) or **orchestration** (a coordinator tells each service what to do next). Compensations must be idempotent, and you accept temporary inconsistency in between."""),
])

MOCK_54 = [HOW, DB, SQL, DBTRICK, DESIGN, SDTRICK]
