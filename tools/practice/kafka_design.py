from common import subject, written

KAFKA = [
    written("kafka-ordering", "Partitions and ordering", "Medium",
        "What does Kafka guarantee about the order of messages, and how do you keep the events of one order together?",
        "Kafka guarantees order **within a partition** only, not across a topic. A producer chooses the partition: with a key, the default partitioner hashes the key, so all records with the same key go to the same partition and are read in order. For ShopStream use the `orderId` as the key.\n\n"
        "Consequences: the number of partitions is the ceiling for consumer parallelism in a group; adding partitions later changes the key-to-partition mapping and can break per-key order across the change; a hot key creates a hot partition that more partitions cannot fix."),
    written("kafka-consumer-groups", "Consumer groups", "Easy",
        "How do consumer groups work? What happens with more consumers than partitions?",
        "Consumers that share a `group.id` form a group, and Kafka assigns each partition to **exactly one** member of the group, so the group as a whole reads every record once. Different groups are independent and each reads every record. If the group has more members than partitions, the extra members are idle (they act as standbys). When a member joins, leaves or stops sending heartbeats, the group **rebalances** and partitions are reassigned."),
    written("kafka-offsets", "Offsets and delivery guarantees", "Medium",
        "When should a consumer commit offsets? Explain at-most-once, at-least-once and exactly-once.",
        "The committed offset is the **next** record to read. Committing *before* processing gives **at-most-once** (a crash loses the records). Committing *after* processing gives **at-least-once** (a crash repeats the records since the last commit): the usual choice, with an **idempotent** handler so a repeat has no extra effect.\n\n"
        "**Exactly-once** is possible inside Kafka (read, process, write to another topic) with transactions and `read_committed` consumers. For effects outside Kafka, such as a database write or an e-mail, you get the same result with at-least-once delivery plus idempotent processing (a unique key or a processed-events table)."),
    written("kafka-rebalance", "Rebalances", "Medium",
        "What causes a consumer group rebalance, and how do you avoid unnecessary ones?",
        "Triggers: a member joins or leaves (a deploy, a crash), a missed heartbeat (`session.timeout.ms`), a consumer that does not call `poll()` within `max.poll.interval.ms` (a slow handler), or a change in the subscribed topics or partitions.\n\n"
        "Reduce them by keeping batch processing well below the poll interval (lower `max.poll.records`, set timeouts on slow calls), using **static membership** (`group.instance.id`) so quick restarts do not rejoin, and using the **cooperative** assignor or the new group protocol so only the moving partitions pause. Make handlers idempotent, because a rebalance causes redelivery of uncommitted records."),
    written("kafka-fast", "Why is Kafka fast?", "Medium",
        "Give four reasons Kafka achieves high throughput.",
        "1. **Sequential disk I/O**: it only appends to log segments, and sequential access is fast even on spinning disks.\n"
        "2. **Page cache**: it relies on the operating system's page cache instead of its own heap cache, so reads of recent data come from memory.\n"
        "3. **Zero copy**: it sends file data from the page cache to the network socket with `sendfile`, without copying through user space.\n"
        "4. **Batching and compression**: producers batch records and compress whole batches; consumers fetch in batches.\n\n"
        "Partitioning adds horizontal scalability on top."),
    written("kafka-retention", "Retention and compaction", "Medium",
        "What is the difference between time-based retention and log compaction? When do you use each?",
        "With **retention** (`retention.ms` / `retention.bytes`) old log segments are deleted after a time or size limit, whether or not they were read. Use it for event streams you process once or for a limited replay window.\n\n"
        "With **log compaction** (`cleanup.policy=compact`) Kafka keeps at least the **latest record per key** and removes older ones; a record with a null value (a tombstone) deletes the key. Use it for changelogs and state: the current price of each product, user profiles, or the internal `__consumer_offsets` topic. A new consumer can rebuild the full current state by reading the compacted topic."),
    written("kafka-dlt", "Failures and dead-letter topics", "Medium",
        "A listener keeps failing on one record. What are your options, and what is a poison pill?",
        "A **poison pill** is a record that can never be processed (malformed JSON, a reference to something that does not exist). Retrying forever blocks the partition behind it.\n\n"
        "Options: retry a few times with a back-off for transient errors; classify permanent errors (validation, conversion) as non-retryable; then publish the record, with the exception and its origin in headers, to a **dead-letter topic** and continue. For long outages use **retry topics** with delays so the main partition is not blocked. Wrap deserializers (`ErrorHandlingDeserializer`) so an unreadable record reaches the error handler instead of failing `poll()` forever, and alert on dead-letter volume."),
    written("kafka-outbox", "The transactional outbox", "Hard",
        "Why is writing to the database and then sending to Kafka unsafe, and how does the outbox pattern solve it?",
        "A service that saves an order and then publishes an event performs a **dual write**: if it crashes between the two, the order exists without its event (or the event without the order), and no transaction spans both systems.\n\n"
        "With the **outbox** pattern the service writes the event into an `outbox` table **in the same database transaction** as the business change, so both commit or neither does. A separate relay then reads new outbox rows and publishes them to Kafka (by polling, or by change data capture with a tool such as Debezium), marking them sent. The relay may publish twice after a crash, so delivery is at-least-once and consumers must be idempotent."),
]

DESIGN = [
    written("design-url-shortener", "Design a URL shortener", "Medium",
        "Outline a URL shortener: API, how short codes are generated, storage, and how you scale reads.",
        "**API**: `POST /urls` (long URL in, short code out) and `GET /{code}` (redirect with 301 or 302; use 302 if you want to count clicks).\n\n"
        "**Code generation**: base-62 of a unique counter (a distributed ID generator or a database sequence in ranges handed to each server), or a random 7-character code with a collision check. A counter avoids collisions but is guessable; random codes are not guessable.\n\n"
        "**Storage**: a key-value mapping `code -> long URL` (a relational table with the code as primary key is enough; a NoSQL store scales further). **Reads dominate** (maybe 100:1), so put a cache (Redis) in front keyed by code, add a CDN or edge cache for popular links, and scale the stateless service horizontally. Add expiry, rate limits and abuse checks (malicious URLs)."),
    written("design-rate-limiter", "Rate limiting algorithms", "Medium",
        "Compare fixed window, sliding window and token bucket rate limiting. Where would you keep the counters?",
        "**Fixed window**: count requests per fixed interval (per minute). Simple, but a burst across a boundary can allow twice the limit. **Sliding window** (log or counter): counts over the last N seconds, smoother but needs more memory or a weighted estimate. **Token bucket**: tokens are added at a steady rate up to a capacity and each request takes one; it permits short bursts while enforcing the average rate. **Leaky bucket** smooths output to a constant rate.\n\n"
        "Keep counters in a shared fast store such as **Redis**, using atomic operations (`INCR` with `EXPIRE`, or a Lua script for the token bucket) so all application instances see the same count. Identify clients by API key, user id or IP, return `429 Too Many Requests` with a `Retry-After` header, and decide what happens if the limiter store is unavailable (fail open or closed)."),
    written("design-caching", "Caching strategies and invalidation", "Medium",
        "Describe cache-aside, write-through and write-behind, and the main ways a cache goes wrong.",
        "**Cache-aside**: the application reads the cache, on a miss loads from the database and fills the cache; writes go to the database and invalidate (or update) the cache entry. **Write-through**: writes go to the cache and the database together, so reads are always fresh but writes are slower. **Write-behind**: writes go to the cache and are flushed to the database later: fast, but data can be lost if the cache fails.\n\n"
        "Failure modes: **stale data** (set a TTL and invalidate on writes), **cache stampede** (many requests rebuild a hot key at once: use locks, request coalescing or staggered TTLs), **penetration** (requests for keys that do not exist always reach the database: cache negative results or use a Bloom filter), and **hot keys** or **eviction storms**. Caching trades consistency for speed, so decide how stale each piece of data may be."),
    written("design-cap", "CAP and consistency", "Hard",
        "State the CAP theorem accurately and say what it means when choosing a database.",
        "In the presence of a network **partition**, a distributed system must choose between **consistency** (every read sees the latest write) and **availability** (every request gets a response). When there is no partition, you can have both; the real trade-off then is between latency and consistency (PACELC).\n\n"
        "In practice: a CP system (for example a strongly consistent store used for coordination, or a relational primary with synchronous replicas) refuses or delays requests it cannot answer correctly; an AP system (for example Cassandra or DynamoDB with eventual consistency) keeps answering and reconciles later. Choose per use case: balances and inventory counts need strong consistency, a social feed or a product view counter can tolerate eventual consistency."),
    written("design-scaling-db", "Scaling a database", "Medium",
        "A single relational database is the bottleneck. List the steps you would take, in order.",
        "1. **Measure** and fix the queries first: indexes, query plans, N+1 problems, connection pool size.\n"
        "2. **Cache** hot reads (Redis, application cache).\n"
        "3. **Scale up** the instance (more CPU, memory, faster disks): cheap and quick, with a limit.\n"
        "4. **Read replicas** for read-heavy load, accepting replication lag for those reads.\n"
        "5. **Partition** large tables (by date or key) to keep indexes small and make old data easy to drop.\n"
        "6. **Shard** across servers by a key such as tenant or user id when writes outgrow one machine; this costs cross-shard queries and transactions, so do it last.\n"
        "7. Move suitable data to a store designed for it (search to Elasticsearch, time series to a time-series database, events to Kafka)."),
    written("design-idempotent-payment", "A safe payment API", "Hard",
        "A client may retry a payment request after a timeout. How do you make sure the customer is charged once?",
        "Make the operation **idempotent** with an **idempotency key**: the client sends a unique key (a UUID) with each logical payment. The server stores, in the same transaction as the charge, a row keyed by that key holding the request fingerprint and the result. A retry with the same key returns the stored result instead of charging again; a retry with the same key but a different body is rejected.\n\n"
        "Also: record the payment state as a state machine (`created -> authorised -> captured`), make calls to the payment provider with their idempotency key too, handle the unknown outcome after a timeout by asking the provider for the status before retrying, and reconcile against provider reports. Use a unique constraint on the key so two concurrent retries cannot both succeed."),
]

SUBJECTS = [
    subject("kafka", "Kafka and messaging", "Messaging", 20,
        "Partitions, consumer groups, offsets, failures and patterns: the Kafka questions behind event-driven Java services.",
        KAFKA,
        platforms=[
            {"name": "Apache Kafka documentation", "url": "https://kafka.apache.org/documentation/", "note": "The official reference"},
            {"name": "Confluent Developer", "url": "https://developer.confluent.io/", "note": "Courses and tutorials"},
        ]),
    subject("system-design", "System design", "System design", 30,
        "Short design questions with the reasoning interviewers want to hear: caching, scaling, consistency and safe APIs.",
        DESIGN,
        platforms=[
            {"name": "GeeksforGeeks: System Design", "url": "https://www.geeksforgeeks.org/system-design/system-design-tutorial/", "note": "Tutorials and case studies"},
            {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "note": "A large open-source guide"},
        ]),
]
