@part py-core-6 | Core Python · Part 6: Data Structures and Collections | core-python
## Lists and Tuples

A **list** is a dynamic array of references: indexing is O(1), appending is **amortised** O(1), and inserting or deleting in the middle is O(n) because later elements shift. A **tuple** is the immutable sibling: fixed length, hashable when its items are, and slightly smaller and faster.

```python Lists.py
import sys

nums = [5, 3, 8]
nums.append(1)                 # O(1) amortised
nums.extend([9, 7])
nums.insert(0, 42)             # O(n): everything shifts right
print(nums)
print(nums.pop(), nums.pop(0), nums.index(8), nums.count(3))     # last item, first item, position of 8, how many 3s
print(nums)
nums.remove(3)                 # removes the first match, O(n)
del nums[0]
print(nums, len(nums), 8 in nums, nums + [1], nums * 2)

result = nums.sort()           # sorts IN PLACE and returns None
print(result, nums, sorted([3, 1, 2], reverse=True))

sizes, items = [], []
for i in range(20):
    items.append(i)
    if not sizes or sys.getsizeof(items) != sizes[-1][1]:
        sizes.append((len(items), sys.getsizeof(items)))
print(sizes)                   # the list over-allocates, so most appends need no reallocation

point = (3, 4)
single = (1,)                  # the comma makes a tuple, not the parentheses
print(point, single, type((1)), type(()), point + (5,), point.index(4))
```

```output
```

The over-allocation is why `append` is amortised O(1): the array grows by a proportion (about 12.5% plus a constant in CPython), so reallocation happens rarely. The exact byte sizes are an implementation detail.

| Operation | `list` | Notes |
| --- | --- | --- |
| `a[i]`, `a[i] = x` | O(1) | |
| `a.append(x)`, `a.pop()` | O(1) amortised | at the end |
| `a.insert(i, x)`, `a.pop(i)`, `del a[i]` | O(n) | shifts the tail |
| `x in a`, `a.index(x)`, `a.remove(x)` | O(n) | linear scan |
| `a.sort()` | O(n log n) | Timsort, stable, near O(n) on nearly sorted data |
| `a[i:j]` | O(j - i) | copies |

!warning `list.sort()` returns None :: `ordered = items.sort()` leaves `ordered` as `None`. Use `sorted(items)` when you want a new list and `items.sort()` when you want to sort in place. The same convention holds for `reverse()` versus `reversed()`.

??  Why is `list.append` O(1) amortised but `list.insert(0, x)` O(n)?
=> A list is a contiguous array with spare capacity at the end, so appending usually writes into free space, and the occasional resize is spread over many appends. Inserting at the front must move every existing element one slot.
??  When would you use a tuple instead of a list?
=> For a fixed-size record or heterogeneous group (a point, a database row, a return value), when you need a hashable key for a dictionary or set, and to signal that the collection will not change. Lists are for homogeneous sequences that grow, shrink or are reordered.
??  What does `(1)` evaluate to, and how do you write a one-element tuple?
=> `(1)` is just the integer 1 in parentheses; the comma creates the tuple: `(1,)`, or `1,`.

## Dictionaries

A `dict` maps **hashable** keys to values using a hash table. Lookup, insert and delete are **O(1) on average**. Since Python 3.7, dictionaries **preserve insertion order** (a language guarantee). CPython stores a compact array of entries plus a sparse index array, which is why dicts are both fast and ordered.

```python Dicts.py
user = {"name": "Asha", "age": 30}
user["city"] = "Pune"
print(user["name"], user.get("phone"), user.get("phone", "n/a"), "age" in user, len(user))
print(user.pop("age"), user.setdefault("role", "dev"), user)

merged = {"a": 1, "b": 2} | {"b": 3, "c": 4}          # Python 3.9+; the right side wins
print(merged, {**merged, "d": 5})

squares = {n: n * n for n in range(5) if n % 2 == 0}
print(squares, list(squares.items()), dict(zip("abc", [1, 2, 3])))

for key, value in user.items():                       # iterate items, not keys + lookups
    print(key, "->", value)

try:
    {"a": 1}["missing"]
except KeyError as error:
    print("KeyError:", error)

try:
    for key in user:
        user["new"] = 1                               # changing the size while iterating
except RuntimeError as error:
    print("RuntimeError:", error)

shared = dict.fromkeys(["x", "y"], [])                # one list shared by every key
shared["x"].append(1)
print(shared)
```

```output
```

A key must be **hashable**: its hash never changes and equal keys have equal hashes. Strings, numbers, tuples of hashables and frozen dataclasses qualify; lists, dicts and sets do not (`TypeError: unhashable type: 'list'`).

### Specialised dictionaries

```python Specialised.py
from collections import ChainMap, Counter, OrderedDict, defaultdict

by_letter = defaultdict(list)                   # missing keys get a fresh list
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    by_letter[word[0]].append(word)
print(dict(by_letter))

counts = Counter("mississippi")
print(counts, counts.most_common(2), counts["z"])
counts.update("ss")
print(counts["s"], Counter([1, 1, 2]) + Counter([2, 3]))

defaults = {"theme": "dark", "lang": "en"}
overrides = {"lang": "hi"}
config = ChainMap(overrides, defaults)          # lookup falls through the chain, nothing is copied
print(config["lang"], config["theme"], list(config))

recent = OrderedDict.fromkeys("abc")
recent.move_to_end("a")
print(list(recent))
```

```output
```

| Need | Use |
| --- | --- |
| Group values by key | `defaultdict(list)` |
| Count things | `Counter` (`most_common`, arithmetic) |
| Layered configuration, no copying | `ChainMap` |
| Reorder or evict by recency | `OrderedDict` (`move_to_end`, `popitem(last=False)`) |
| Read-only view of a dict | `types.MappingProxyType(d)` |
| Typed fixed keys for JSON-like data | `typing.TypedDict` |

!realworld The two-line word-frequency job :: `Counter(text.lower().split()).most_common(10)` replaces a page of Java. It is also how you build quick log summaries, tag counts and histogram tables in tests and scripts.

??  How is a Python dictionary implemented, and what are the average and worst-case costs?
=> A hash table: the key's hash selects a slot in a sparse index array that points into a dense, insertion-ordered array of entries. Average lookup, insert and delete are O(1); a pathological set of colliding keys degrades to O(n), which is why string hashes are randomised per process (`PYTHONHASHSEED`) to resist hash-flooding attacks.
??  Why can't a list be a dictionary key?
=> Keys must be hashable: their hash must stay constant for their lifetime. A list is mutable, so its contents (and a content-based hash) could change after insertion and the entry would be lost. Use a tuple (or `frozenset`) instead.
??  What does `dict.get(key, default)` give you over `d[key]`?
=> It returns the default instead of raising `KeyError`. When the default is expensive to build, use `if key in d` or `try/except KeyError`, because `get` evaluates its default argument every time. `setdefault` and `defaultdict` cover "insert if missing".
??  What is the bug in `dict.fromkeys(keys, [])`?
=> Every key shares the same list object, so appending to one appears under all of them. Build independent values with a comprehension: `{k: [] for k in keys}`.

## Sets and Frozensets

A `set` is an unordered collection of **unique hashable** items with O(1) average membership tests. It is the right tool for de-duplication, fast `in` checks and mathematical set operations.

```python Sets.py
a, b = {1, 2, 3, 4}, {3, 4, 5}
print(a | b, a & b, a - b, a ^ b)                 # union, intersection, difference, symmetric difference
print({1, 2} <= a, a.isdisjoint({9}), 3 in a)
print(set(), type({}), type({1}), {x % 3 for x in range(10)})

emails = ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]
print(list(dict.fromkeys(emails)))                # de-duplicate, KEEPING ORDER (sets lose it)
print(len(set(emails)), sorted(set(emails)))

tags = {"python", "api"}
tags.add("fastapi")
tags.discard("missing")                            # no error; remove() would raise KeyError
print(sorted(tags))

key = frozenset({"read", "write"})                 # immutable and hashable: usable as a dict key
print({key: "editor"}[frozenset({"write", "read"})])
```

```output
```

`{}` is an empty **dict**, not an empty set: write `set()`. Sets are unordered (do not rely on iteration order, especially of strings, whose hashes are randomised between runs), so sort before printing or comparing in tests.

!interview Why is `x in a_set` fast and `x in a_list` slow? :: A set hashes `x` and jumps to a slot: O(1) on average. A list compares `x` to each element in turn: O(n). Converting a list you will test many times into a set (`allowed = set(ids)`) is the commonest O(n²) to O(n) fix in interviews and in code review.

??  How do you remove duplicates from a list while preserving order?
=> `list(dict.fromkeys(items))`: dictionary keys are unique and keep first-insertion order. `list(set(items))` also de-duplicates but loses the order.
??  What is the difference between `set.remove` and `set.discard`?
=> `remove` raises `KeyError` if the element is absent; `discard` does nothing. Use `discard` when absence is acceptable.
??  When is a `frozenset` needed?
=> When a set must be hashable: as a dictionary key, an element of another set, or a cached function argument. It supports all the read operations of a set but cannot be changed.

## Sorting and Comparing

`sorted(iterable, key=..., reverse=...)` returns a new list; `list.sort()` sorts in place. Both use **Timsort**: O(n log n) worst case, O(n) on nearly sorted data, and **stable**, so equal keys keep their original relative order. That stability is what makes multi-pass sorting work.

```python Sorting.py
from functools import cmp_to_key
from operator import attrgetter, itemgetter
from dataclasses import dataclass

words = ["banana", "Apple", "cherry", "apple", "fig"]
print(sorted(words), sorted(words, key=str.casefold), sorted(words, key=len))
print(sorted(words, key=lambda w: (-len(w), w.casefold())))       # longest first, then alphabetical

rows = [("asha", 91), ("ravi", 78), ("meera", 91), ("john", 78)]
print(sorted(rows, key=itemgetter(1), reverse=True))              # stable: ties keep the input order
print(sorted(sorted(rows), key=itemgetter(1), reverse=True))      # two passes: name, then score

@dataclass
class Emp:
    name: str
    dept: str
    salary: int

staff = [Emp("a", "ops", 50), Emp("b", "dev", 90), Emp("c", "dev", 70)]
print([e.name for e in sorted(staff, key=attrgetter("dept", "salary"))])

legacy = sorted([3, 1, 2], key=cmp_to_key(lambda x, y: y - x))     # old-style comparator, rarely needed
print(legacy, min(rows, key=itemgetter(1)), max(words, key=len))
```

```output
```

Prefer a **key function** (computed once per element) to a comparator. To sort descending by a number and ascending by a string, negate the number or sort in two stable passes. Mixed-type lists cannot be sorted (`TypeError: '<' not supported between 'int' and 'str'`).

### Heaps and binary search

```python Heap.py
import heapq
from bisect import bisect_left, bisect_right, insort

data = [7, 2, 9, 4, 1, 8]
heap = []
for x in data:
    heapq.heappush(heap, x)                 # a min-heap: heap[0] is the smallest
print(heap[0], [heapq.heappop(heap) for _ in range(3)])
print(heapq.nlargest(2, data), heapq.nsmallest(2, data))

tasks = []
heapq.heappush(tasks, (2, "write report"))
heapq.heappush(tasks, (1, "fix prod bug"))   # tuples compare by priority first
print(heapq.heappop(tasks))

max_heap = [-x for x in data]                # simulate a max-heap by negating
heapq.heapify(max_heap)
print(-heapq.heappop(max_heap))

ordered = [10, 20, 20, 30]
print(bisect_left(ordered, 20), bisect_right(ordered, 20), bisect_left(ordered, 25))
insort(ordered, 25)
print(ordered)
```

```output
```

`heapq` keeps a list arranged as a binary heap: push and pop are O(log n), reading the smallest is O(1). `bisect` does binary search on a sorted list (O(log n)); `insort` then costs O(n) for the insertion.

??  Is Python's sort stable, and why does that matter?
=> Yes (Timsort). Items with equal keys keep their relative order, so you can sort by several keys by sorting repeatedly from the least significant key to the most significant, and results are reproducible.
??  How do you sort a list of dictionaries by two fields, one descending?
=> `sorted(rows, key=lambda r: (r["dept"], -r["salary"]))`: negate the numeric field to reverse it. For non-numeric fields sort in two stable passes (secondary key first, with `reverse=True`).
??  How do you get the k largest items of a huge stream with little memory?
=> Keep a min-heap of size k: push each item and pop the smallest when the heap exceeds k, giving O(n log k) time and O(k) memory. `heapq.nlargest(k, iterable)` does this.

## Queues, Deques and Other Containers

Never use a list as a queue: `pop(0)` is O(n). `collections.deque` is a doubly linked list of blocks with O(1) operations at **both** ends.

```python Deque.py
from collections import deque, namedtuple
from queue import PriorityQueue, Queue
import array

dq = deque([1, 2, 3])
dq.append(4)
dq.appendleft(0)
print(dq)
print(dq.popleft(), dq.pop(), dq)
dq.rotate(1)
print(dq, deque(range(10), maxlen=3))          # a bounded deque drops the oldest items

q = Queue()                                    # thread-safe FIFO for producers and consumers
q.put("job1")
q.put("job2")
print(q.get(), q.qsize())

pq = PriorityQueue()
pq.put((5, "low"))
pq.put((1, "urgent"))
print(pq.get())

Pt = namedtuple("Pt", "x y")
print(Pt(1, 2), Pt(1, 2)._replace(y=9))

compact = array.array("i", [1, 2, 3])          # typed, compact numeric array
print(compact, compact.itemsize, sum(compact))
```

```output
```

| Structure | Use it for |
| --- | --- |
| `list` | Ordered, growable sequence; stack (`append`, `pop`) |
| `tuple` | Fixed records, dict keys |
| `deque` | FIFO queue, sliding window, O(1) at both ends |
| `dict` | Lookup by key, grouping, caches |
| `set` / `frozenset` | Uniqueness and fast membership |
| `heapq` on a list | Priority queue, top-k, scheduling |
| `queue.Queue` | Thread-safe hand-off between threads |
| `array`, NumPy | Large numeric data |

## Choosing a Data Structure, and Big-O

| Operation | list | deque | dict | set | heap (`heapq`) |
| --- | --- | --- | --- | --- | --- |
| Access by index | O(1) | O(n) middle | n/a | n/a | n/a |
| Lookup by value / key | O(n) | O(n) | **O(1)** avg | **O(1)** avg | O(n) |
| Insert at end | O(1) am. | O(1) | O(1) avg | O(1) avg | O(log n) |
| Insert / pop at front | **O(n)** | **O(1)** | n/a | n/a | O(log n) |
| Delete by value / key | O(n) | O(n) | O(1) avg | O(1) avg | O(n) |
| Min / max | O(n) | O(n) | O(n) | O(n) | **O(1)** / O(log n) pop |
| Iteration | O(n) | O(n) | O(n) | O(n) | O(n) |

```python Speed.py
import timeit

n = 50_000
as_list = list(range(n))
as_set = set(as_list)
target = n - 1                                     # worst case for the list: the last element

list_time = timeit.timeit(lambda: target in as_list, number=200)
set_time = timeit.timeit(lambda: target in as_set, number=200)
print("set lookup is faster by more than 50x:", list_time / set_time > 50)

queue_list = timeit.timeit("l.pop(0); l.append(0)", setup="l = list(range(100_000))", number=2000)
queue_deque = timeit.timeit("d.popleft(); d.append(0)", setup="from collections import deque; d = deque(range(100_000))", number=2000)
print("deque is faster than list.pop(0):", queue_deque < queue_list)
```

```output
```

!cheat Which container? ::
- Ordered growable sequence: `list`. Fixed record or dict key: `tuple`.
- Lookup by key: `dict`. Membership and de-duplication: `set`. Count: `Counter`. Group: `defaultdict(list)`.
- Queue or sliding window: `deque`. Priority or top-k: `heapq`. Sorted insertion/search: `bisect`.
- If you test `x in some_list` in a loop, make it a `set`. If you `pop(0)` a list, make it a `deque`.
- Small collections: the constant factors dominate; measure with `timeit` before optimising.
!end

??  You are testing membership of 100,000 IDs against a list of 1,000,000 allowed IDs. What do you change?
=> Convert the allowed list to a `set` once (O(n)), then each check is O(1) on average, turning O(n·m) into O(n + m).
??  Which data structure for an LRU cache, a sliding-window maximum and a task scheduler?
=> LRU cache: `OrderedDict` (or dict plus doubly linked list) for O(1) get, put and eviction. Sliding-window maximum: a `deque` of indices kept in decreasing order of value. Task scheduler: a `heapq` priority queue keyed by priority or due time.

## Implement Your Own: Array List, Linked List, Hash Map and LRU Cache

Interviewers often ask you to build the structure rather than use it. Writing these shows you understand what Python gives you for free. Each class below is checked with assertions when this page is built.

```python DynamicArray.py
class DynamicArray:
    """Growable array with amortised O(1) append, like list."""

    def __init__(self):
        self._capacity = 2
        self._size = 0
        self._data = [None] * self._capacity

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        if not -self._size <= index < self._size:
            raise IndexError("index out of range")
        return self._data[index % self._size]

    def append(self, value):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)          # doubling gives amortised O(1)
        self._data[self._size] = value
        self._size += 1

    def _resize(self, capacity):
        new = [None] * capacity
        for i in range(self._size):
            new[i] = self._data[i]
        self._data, self._capacity = new, capacity

    def __iter__(self):
        return (self._data[i] for i in range(self._size))


arr = DynamicArray()
for i in range(10):
    arr.append(i * i)
assert len(arr) == 10 and arr[3] == 9 and arr[-1] == 81 and list(arr) == [i * i for i in range(10)]
assert arr._capacity == 16
print(list(arr), arr._capacity)
```

```output
```

```python LinkedList.py
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value, self.next = value, next


class LinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def push_front(self, value):                       # O(1)
        self.head = Node(value, self.head)
        self._size += 1

    def append(self, value):                           # O(n) without a tail pointer
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1

    def reverse(self):                                 # classic interview question: O(n) time, O(1) space
        prev, cur = None, self.head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self.head = prev

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def __len__(self):
        return self._size


ll = LinkedList()
for v in (1, 2, 3):
    ll.append(v)
ll.push_front(0)
assert list(ll) == [0, 1, 2, 3] and len(ll) == 4
ll.reverse()
assert list(ll) == [3, 2, 1, 0]
print(list(ll))
```

```output
```

```python HashMap.py
class HashMap:
    """Separate chaining with resizing: O(1) average get and put."""

    def __init__(self, buckets=8):
        self._buckets = [[] for _ in range(buckets)]
        self._size = 0

    def _bucket(self, key):
        return self._buckets[hash(key) % len(self._buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size > 0.75 * len(self._buckets):          # keep the load factor low
            self._grow()

    def get(self, key, default=None):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return default

    def remove(self, key):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def _grow(self):
        old = [pair for bucket in self._buckets for pair in bucket]
        self._buckets = [[] for _ in range(len(self._buckets) * 2)]
        self._size = 0
        for k, v in old:
            self.put(k, v)

    def __len__(self):
        return self._size


m = HashMap()
for i in range(100):
    m.put(f"key{i}", i)
m.put("key7", 700)
assert len(m) == 100 and m.get("key7") == 700 and m.get("key99") == 99 and m.get("nope", -1) == -1
assert m.remove("key7") and not m.remove("key7") and len(m) == 99
print(len(m), len(m._buckets))
```

```output
```

```python Lru.py
from collections import OrderedDict


class LRUCache:
    """Least-recently-used cache: O(1) get and put."""

    def __init__(self, capacity):
        self.capacity = capacity
        self._items = OrderedDict()

    def get(self, key):
        if key not in self._items:
            return -1
        self._items.move_to_end(key)                       # most recently used goes to the end
        return self._items[key]

    def put(self, key, value):
        if key in self._items:
            self._items.move_to_end(key)
        self._items[key] = value
        if len(self._items) > self.capacity:
            self._items.popitem(last=False)                # evict the least recently used


cache = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
assert cache.get("a") == 1
cache.put("c", 3)                                           # evicts "b"
assert cache.get("b") == -1 and cache.get("c") == 3 and cache.get("a") == 1
print(list(cache._items))

# In real code use the standard library:
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80), fib.cache_info())
```

```output
```

!interview LRU cache without OrderedDict :: The classic interview answer is a dictionary from key to node plus a **doubly linked list** ordered by recency: `get` moves the node to the front, `put` inserts at the front and evicts the tail, and every step is O(1). `OrderedDict` is exactly that structure, so naming it, and then being able to draw the manual version, is the strongest answer. `functools.lru_cache` is the production tool for caching pure function results.

??  Why does the dynamic array double its capacity instead of adding a fixed amount?
=> Doubling makes the total copying cost over n appends O(n) (each element is copied a constant number of times on average), so each append is amortised O(1). Growing by a fixed amount would copy O(n) elements every few appends and make n appends O(n²).
??  How does a hash map handle collisions, and what is the load factor?
=> Separate chaining stores colliding keys in a small list per bucket; open addressing probes other slots. The load factor is entries divided by buckets; when it exceeds a threshold the table doubles and rehashes, which keeps chains short and operations O(1) on average. CPython's dict uses open addressing with a compact entries array.
??  How do you reverse a singly linked list in place?
=> Walk the list keeping `prev` and `cur`; for each node point `cur.next` at `prev`, then advance both. O(n) time, O(1) extra space; finally `head = prev`. The tuple assignment `cur.next, prev, cur = prev, cur, cur.next` does the three moves safely because the right side is evaluated first.
