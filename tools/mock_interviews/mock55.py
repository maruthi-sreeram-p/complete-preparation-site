"""Day 55 - Mock interview 3: DSA (2 timed problems) and LLD (one machine-coding problem in 60 minutes)."""
import pathlib
import runpy

_c = runpy.run_path(str(pathlib.Path(__file__).with_name("common.py")))
q, section, info, WRITTEN_FOR_SITE = _c["q"], _c["section"], _c["info"], _c["WRITTEN_FOR_SITE"]

HOW = info("mock-how", "How to run this mock", WRITTEN_FOR_SITE + """

**Part 1: DSA, 2 timed problems (about 25 minutes each)**

Pick two problems from the list below (ask a friend to pick for you, so you do not choose the ones you like). For each:
1. Spend the **first 3 minutes** asking questions and writing examples, *before* any code.
2. Say your approach and its complexity **out loud**, then code it in a plain editor with no autocomplete.
3. Run your own test cases, including empty, one element and duplicates.
4. Only then open **Show answer**.

**Part 2: LLD, one machine-coding problem in 60 minutes**

Use the parking-lot problem. Budget: 10 minutes for requirements and classes, 35 minutes for working code, 10 minutes for tests, 5 minutes to explain trade-offs. It must **run**, not only look good.

Then apply and polish your GitHub README and LinkedIn profile, as the plan says.""")

DSA = section("mock-dsa", "Part 1: Timed DSA problems", "Five problems that appear again and again. Each answer has the idea, complexity, working Java and the follow-up question the interviewer is likely to ask.", [
    q("Basic", "Valid Parentheses: given a string of `()[]{}`, decide whether the brackets are balanced and correctly nested.", """
**Idea**: a **stack**. On an opening bracket push the *closing* one you expect; on a closing bracket the top of the stack must equal it. At the end the stack must be empty.

```java
public boolean isValid(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        switch (c) {
            case '(' -> stack.push(')');
            case '[' -> stack.push(']');
            case '{' -> stack.push('}');
            default -> { if (stack.isEmpty() || stack.pop() != c) return false; }
        }
    }
    return stack.isEmpty();
}
```
**Complexity**: O(n) time, O(n) space. **Edge cases**: empty string (valid), one closing bracket first, extra opening brackets at the end.
**Follow-up**: "What if the string also contains letters?" (ignore other characters). "Can you do it in O(1) space for a single bracket type?" (a counter is enough).""",
      hint="Which structure gives you 'the most recent opening bracket'?"),
    q("Medium", "Longest Substring Without Repeating Characters: return the length of the longest substring of `s` with no repeated character. (`\"abcabcbb\"` gives 3)", """
**Idea**: **sliding window** with two pointers. Keep a map from character to the **last index** where you saw it. Move `end` forward; if the character was seen *inside the current window*, jump `start` to just after that index. Track the best window length.

```java
public int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> last = new HashMap<>();
    int best = 0, start = 0;
    for (int end = 0; end < s.length(); end++) {
        Integer seen = last.get(s.charAt(end));
        if (seen != null && seen >= start) start = seen + 1;
        last.put(s.charAt(end), end);
        best = Math.max(best, end - start + 1);
    }
    return best;
}
```
**Complexity**: O(n) time (each index is visited once), O(k) space for k distinct characters.
**The trap**: forgetting `seen >= start`. A character seen *before* the window must not move `start` backwards.
**Follow-up**: "Return the substring itself" (remember the best `start`). "What if the input is a stream?" (the window and the map are all you keep).""",
      hint="Two pointers and a map of last-seen positions."),
    q("Medium", "Merge Intervals: given intervals `[[1,3],[2,6],[8,10],[15,18]]`, merge all that overlap. (Result: `[[1,6],[8,10],[15,18]]`)", """
**Idea**: **sort by start**, then sweep. If the current interval starts after the last merged interval ends, it is separate; otherwise extend the last interval's end with the larger of the two ends.

```java
public int[][] merge(int[][] intervals) {
    int[][] sorted = intervals.clone();
    Arrays.sort(sorted, (a, b) -> Integer.compare(a[0], b[0]));
    List<int[]> out = new ArrayList<>();
    for (int[] cur : sorted) {
        if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) {
            out.add(new int[] {cur[0], cur[1]});
        } else {
            int[] last = out.get(out.size() - 1);
            last[1] = Math.max(last[1], cur[1]);
        }
    }
    return out.toArray(new int[0][]);
}
```
**Complexity**: O(n log n) for the sort, O(n) extra space.
**Edge cases**: `[1,4]` and `[4,5]` touch, so they merge (ask whether touching counts); one interval contained in another (`[1,10]`, `[2,3]`): that is why you use `Math.max`; an empty input.
**Follow-up**: "Insert one new interval into an already sorted list in O(n)." """,
      hint="What order makes overlapping intervals neighbours?"),
    q("Medium", "Top K Frequent Elements: return the `k` most frequent values in an array. Can you beat O(n log n)?", """
**Idea**: count with a `HashMap`, then keep a **min-heap of size k** of (value, count). When the heap grows past `k`, remove the smallest count. What remains are the top `k`.

```java
public int[] topKFrequent(int[] nums, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    for (int n : nums) count.merge(n, 1, Integer::sum);
    PriorityQueue<Map.Entry<Integer, Integer>> heap = new PriorityQueue<>(Map.Entry.comparingByValue());
    for (Map.Entry<Integer, Integer> e : count.entrySet()) {
        heap.offer(e);
        if (heap.size() > k) heap.poll();
    }
    int[] result = new int[k];
    for (int i = k - 1; i >= 0; i--) result[i] = heap.poll().getKey();
    return result;
}
```
**Complexity**: O(n + d log k) time for d distinct values, O(d) space. That is better than sorting when `k` is small.
**Beating it**: **bucket sort**. A value cannot occur more than `n` times, so make `n + 1` buckets indexed by frequency and read them from the highest: O(n) time.
**Follow-up**: "What if there are ties at the boundary?" (ask what the problem expects).""",
      hint="Count first. Then which structure keeps only the best k?"),
    q("Medium", "Search in Rotated Sorted Array: a sorted array of distinct values was rotated at an unknown point (`[4,5,6,7,0,1,2]`). Find `target` in O(log n).", """
**Idea**: **binary search**. At each step one half is always sorted. Find the sorted half, check whether the target lies inside it, and discard the other half.

```java
public int search(int[] a, int target) {
    int lo = 0, hi = a.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == target) return mid;
        if (a[lo] <= a[mid]) {                        // left half is sorted
            if (a[lo] <= target && target < a[mid]) hi = mid - 1; else lo = mid + 1;
        } else {                                      // right half is sorted
            if (a[mid] < target && target <= a[hi]) lo = mid + 1; else hi = mid - 1;
        }
    }
    return -1;
}
```
**Complexity**: O(log n) time, O(1) space.
**The traps**: `a[lo] <= a[mid]` needs `<=` (a one-element half); write `mid` as `lo + (hi - lo) / 2` to avoid integer overflow; check the target against **both ends** of the sorted half.
**Follow-up**: "What if the array has duplicates?" (the worst case degrades to O(n), because `a[lo] == a[mid]` tells you nothing).""",
      hint="After you pick mid, is the left half or the right half guaranteed sorted?"),
])

DSATALK = section("mock-dsa-tricky", "Part 1b: Questions about how you solve problems", "Interviewers ask these while you code. Your habits matter as much as the solution.", [
    q("Tricky", "You get a problem. What exactly do you do in the first five minutes?", """
1. **Restate** it in your own words and ask about the **constraints**: input size, can values be negative, duplicates, sorted or not, empty input, what to return when there is no answer.
2. Work **one or two examples** by hand, including a tricky one.
3. Say the **brute force** and its complexity first (it shows you understand the problem), then look for what makes it slow: repeated work, unnecessary scanning.
4. Name the **pattern** (hash map, two pointers, sliding window, stack, heap, binary search, BFS/DFS, dynamic programming) and agree on the plan **before** coding.
5. Code with clear names, then **walk through** your example line by line."""),
    q("Tricky", "Your solution passes the example but the interviewer says it is wrong. What do you do?", """
Do not argue and do not panic. **Ask for a failing input**, or invent your own: empty, one element, all equal, the largest size, negatives, already sorted, reverse sorted. Trace the code by hand on it and find the line that is wrong. Narrating this calmly is a positive signal, because debugging is a core skill."""),
    q("Tricky", "The interviewer asks: 'Can you do better?' What is the right reaction?", """
It does not always mean your answer is wrong. First state the complexity you have and **what the bottleneck is** (the sort? the nested loop?). Then ask what a lower bound could be: you cannot answer a search in a sorted array faster than O(log n). Offer a trade-off: spend O(n) memory (a hash map) to save time. If you cannot see a better way, say so, keep the working solution, and explain what you would try (heap, bucket, precomputation)."""),
    q("Tricky", "What if the input does not fit in memory, or arrives as a stream?", """
Think about what you must keep. For a stream: a **sliding window** or a running aggregate (count, min, max), a **heap of size k** for the top k, a hash map only if the number of distinct values is small. If too large, process in **chunks** and merge (external sort), or use approximate structures (a Bloom filter, count-min sketch). Say it is a trade-off between memory and exactness."""),
    q("Tricky", "What are the complexities of common Java collection operations? Why does a bad `hashCode` hurt?", """
`ArrayList`: get O(1), add at end amortised O(1), insert in the middle O(n). `HashMap`/`HashSet`: get, put, contains O(1) average. `TreeMap`: O(log n) and ordered. `PriorityQueue`: offer and poll O(log n), peek O(1). `ArrayDeque`: push and pop O(1). `String` concatenation in a loop is O(n^2) overall.

A bad `hashCode` (for example a constant) puts every key in one bucket, so a `HashMap` degrades toward O(n) per operation (O(log n) after treeification). It is also why you must not use mutable keys."""),
])

LLD_HOW = info("mock-lld-how", "Part 2: LLD, the 60-minute plan", """
**The problem (machine coding)**: *Design and code a parking lot.* Cars, motorcycles and trucks enter and leave. Each vehicle gets a ticket with a spot; on exit it pays a fee based on how long it stayed. The lot can be full.

**Clarify first (2 minutes)**: how many floors? Do vehicle types need different spot sizes? How is the fee calculated (hourly? different per type)? Can two vehicles arrive at the same time (concurrency)? Do we need persistence or only in memory? *Write the assumptions on the page.*

**Minute plan**

| Minutes | What |
|---|---|
| 0 to 10 | Requirements, nouns become classes, verbs become methods |
| 10 to 45 | Working code for the happy path, then the error cases |
| 45 to 55 | A runnable `main` or unit tests (full lot, unknown ticket, fee) |
| 55 to 60 | Explain trade-offs and how you would extend it |

**Order of work**: first a design that compiles and runs end to end, with the simplest possible choices. Add patterns only where a requirement pulls them in (a pricing **Strategy**, because the fee rule will change). Do not start with ten interfaces.""")

LLD = section("mock-lld", "Part 2: LLD questions and model answers", "The first answer is a complete design. The others are what the interviewer asks while reading your code.", [
    q("Medium", "Design a parking lot. Show the classes and the working core.", """
**Classes** (nouns): `Vehicle` and `VehicleType`, `Spot`, `Ticket`, `ParkingLot`, and a `PricingStrategy` (the part that is most likely to change).

```java
enum VehicleType { MOTORCYCLE, CAR, TRUCK }

record Vehicle(String plate, VehicleType type) {}

class Spot {
    final String id;
    final VehicleType fits;
    private Vehicle parked;
    Spot(String id, VehicleType fits) { this.id = id; this.fits = fits; }
    boolean canPark(Vehicle v) { return parked == null && v.type() == fits; }
    void park(Vehicle v) { parked = v; }
    void free() { parked = null; }
}

record Ticket(String id, Vehicle vehicle, Spot spot, Instant entry) {}

interface PricingStrategy {
    long fee(Duration stayed, VehicleType type);          // in the smallest currency unit
}

class HourlyPricing implements PricingStrategy {
    public long fee(Duration stayed, VehicleType type) {
        long hours = Math.max(1, (stayed.toMinutes() + 59) / 60);   // round up, minimum one hour
        long rate = switch (type) { case MOTORCYCLE -> 10; case CAR -> 30; case TRUCK -> 60; };
        return hours * rate;
    }
}

class ParkingLot {
    private final List<Spot> spots;
    private final PricingStrategy pricing;
    private final Map<String, Ticket> active = new HashMap<>();

    ParkingLot(List<Spot> spots, PricingStrategy pricing) {
        this.spots = List.copyOf(spots);
        this.pricing = pricing;
    }

    /** Empty result means the lot is full for this vehicle type. */
    synchronized Optional<Ticket> enter(Vehicle v, Instant now) {
        return spots.stream().filter(s -> s.canPark(v)).findFirst().map(s -> {
            s.park(v);
            Ticket t = new Ticket(UUID.randomUUID().toString(), v, s, now);
            active.put(t.id(), t);
            return t;
        });
    }

    synchronized long exit(String ticketId, Instant now) {
        Ticket t = active.remove(ticketId);
        if (t == null) throw new IllegalArgumentException("Unknown or already used ticket");
        t.spot().free();
        return pricing.fee(Duration.between(t.entry(), now), t.vehicle().type());
    }
}
```
**Why it is built this way**: the lot owns the rules (`enter`, `exit`); `Spot` only knows its own state; the fee rule sits behind an interface so a weekend price or a monthly pass is a new class, not an edit. `enter` and `exit` are `synchronized`, so two cars can never get the same spot.

**Run it**: create a few spots, `enter` a car, `exit` with a time two hours later, expect `60`; enter until full and check you get `Optional.empty()`.""",
      hint="Which things might change later? Put those behind an interface."),
    q("Medium", "Which SOLID principles did you apply here? Give a concrete example of each.", """
- **S**ingle responsibility: `Spot` tracks occupancy, `ParkingLot` coordinates, `HourlyPricing` only computes the fee.
- **O**pen/closed: add `WeekendPricing` as a new class; `ParkingLot` does not change.
- **L**iskov substitution: any `PricingStrategy` can replace another without the lot noticing.
- **I**nterface segregation: `PricingStrategy` has one method, so implementers carry nothing extra.
- **D**ependency inversion: `ParkingLot` depends on the `PricingStrategy` **interface** and receives it in the constructor, not `new HourlyPricing()` inside."""),
    q("Medium", "How would you add an electric-vehicle spot with a charger, and a monthly pass, **without rewriting** `ParkingLot`?", """
EV: add a type or a capability to the spot (for example `Spot` has a set of features, and a vehicle declares what it needs), and make `canPark` check it. If the matching rule grows, extract a `SpotSelectionStrategy` (nearest to the entrance, cheapest, EV first) and inject it, the same way pricing is injected.

Monthly pass: a new `PricingStrategy` (or a decorator around the existing one) that returns 0 when the plate has a valid pass. The open/closed principle in action: new behaviour is new code behind an existing interface."""),
    q("Medium", "Is this thread-safe? What are the problems with `synchronized` on the whole lot?", """
`enter` and `exit` are atomic, so there are no double bookings. But **one lock for the whole lot** means every entry and exit queues behind it, which is fine for a toy, not for a real garage with many gates.

Improvements: one lock per floor, or a concurrent structure with an atomic compare-and-set on each `Spot` (`AtomicReference<Vehicle>`: `compareAndSet(null, v)`), or free spots kept in a `ConcurrentLinkedQueue` per type so allocation is O(1) instead of scanning the list. Say that you started simple on purpose and would measure before optimising."""),
    q("Medium", "How would you test this?", """
Unit tests with a **fixed time** (pass `Instant` in, as we did, instead of calling `Instant.now()` inside, which makes tests unrepeatable):
- parks a car and returns a ticket; the spot is no longer free;
- a full lot returns `Optional.empty()`;
- a motorcycle never takes a car spot;
- `exit` with an unknown or already-used ticket throws;
- the fee rounds up (61 minutes costs two hours) and has a one-hour minimum;
- after `exit`, the spot can be reused.
Add a small concurrency test: many threads call `enter` for fewer spots than threads and assert that no two tickets share a spot."""),
    q("Medium", "Design an LRU cache with O(1) `get` and `put`. (A very common machine-coding task.)", """
**Idea**: a `HashMap` for O(1) lookup **plus** a doubly linked list ordered by recent use. On every `get` or `put`, move the node to the front; when full, evict the node at the back.

```java
class LruCache<K, V> {
    private class Node {
        K key; V value; Node prev, next;
        Node(K key, V value) { this.key = key; this.value = value; }
    }

    private final int capacity;
    private final Map<K, Node> index = new HashMap<>();
    private final Node head = new Node(null, null);     // sentinels remove null checks
    private final Node tail = new Node(null, null);

    LruCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    synchronized V get(K key) {
        Node n = index.get(key);
        if (n == null) return null;
        unlink(n);
        addFirst(n);
        return n.value;
    }

    synchronized void put(K key, V value) {
        Node n = index.get(key);
        if (n != null) { n.value = value; unlink(n); addFirst(n); return; }
        if (index.size() == capacity) {
            Node lru = tail.prev;
            unlink(lru);
            index.remove(lru.key);
        }
        n = new Node(key, value);
        index.put(key, n);
        addFirst(n);
    }

    private void unlink(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
    private void addFirst(Node n) { n.next = head.next; n.prev = head; head.next.prev = n; head.next = n; }
}
```
**Why both structures**: the map alone cannot tell you which entry is oldest; the list alone needs O(n) to find a key.
**Shortcut to mention**: in Java, `LinkedHashMap` constructed with `accessOrder = true` and an overridden `removeEldestEntry` is an LRU cache in a few lines. Interviewers usually want the manual version.
**Follow-ups**: thread safety (here one lock; `ConcurrentHashMap` plus a lock-free structure is much harder), TTL per entry, and what changes for LFU."""),
    q("Tricky", "Why not make `ParkingLot` a Singleton?", """
A Singleton hides a **global dependency**: it is hard to test (state leaks between tests), hard to have two lots, and it makes the code depend on a hidden instance. It also complicates thread safety and class loading. Prefer to create one instance in `main` (or let Spring do it, as a singleton-scoped **bean**) and **pass it in**. You still get a single instance, without the global."""),
    q("Tricky", "When would you use Strategy, State, Factory and Observer? How do you avoid over-engineering?", """
- **Strategy**: swap an algorithm chosen by the caller (pricing, spot selection, sort order).
- **State**: an object's behaviour depends on its state, and the state changes itself (a vending machine: idle, has money, dispensing).
- **Factory**: creation logic is non-trivial or varies by input (create a `Vehicle` or `Spot` from a type).
- **Observer**: others must react to an event without the source knowing them (notify when the lot is full).

To avoid over-engineering: start with the simplest working code, introduce a pattern only when a **real requirement** (a second pricing rule, a second notification channel) asks for it, and be able to say *what change it makes easy*."""),
    q("Tricky", "Why is the fee a `long` in the smallest currency unit and not a `double`?", """
`double` cannot represent most decimal fractions exactly (0.1 + 0.2 is not 0.3), so money in `double` accumulates errors. Use integers in the **smallest unit** (paise, cents) or `BigDecimal` with an explicit rounding mode. Mention a `Money` value object (amount plus currency) as the next step."""),
])

MOCK_55 = [HOW, DSA, DSATALK, LLD_HOW, LLD]
