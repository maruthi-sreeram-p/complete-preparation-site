@part py-dsa-7 | DSA Patterns in Python · Part 7: Revision and Interview Playbook | dsa
## Pattern Recognition Cheat Sheet

Read each problem for its **signals**, name the pattern, then recall the template. This is the one-page map for the night before an interview.

| If you see... | Think... | Template (see Part) | Typical cost |
| --- | --- | --- | --- |
| Sorted array + pair/triple; palindromes; partition in place | **Two pointers** | `lo, hi` towards each other; or `read/write` (2) | O(n) |
| Contiguous subarray/substring, "longest/shortest such that" | **Sliding window** | expand `right`, `while invalid: left += 1` (2) | O(n) |
| Range sums; count subarrays with sum k | **Prefix sums + hash map** | `seen = {0: 1}`; `running - k` (2) | O(n) |
| "Does the complement exist?", counts, duplicates | **Hash map / set / Counter** | one pass, store what you saw (2) | O(n) |
| Sorted/rotated array; "minimum x such that feasible" | **Binary search** (index or on the answer) | `first_true(lo, hi, feasible)` (2) | O(log n) |
| Overlapping ranges, meetings | **Sort by start (or end) + merge/heap** | (2) | O(n log n) |
| Best single run; reachability; local rules | **Kadane / greedy scan** | one pass, a few variables (2, 6) | O(n) |
| Linked list: cycle, middle, k-th from end, reversal | **Dummy node, fast/slow** | (3) | O(n) |
| Brackets, nested structure, undo | **Stack** | push openers, pop on closers (3) | O(n) |
| Next greater/smaller, spans, histogram | **Monotonic stack** | pop while the new value resolves them (3) | O(n) |
| Window maximum, BFS levels | **Deque / queue** | (3, 4) | O(n) |
| "Generate all", permutations, subsets, constraints | **Backtracking** | choose, explore, un-choose, prune (4) | exponential |
| Tree: depth, paths, validity, LCA | **DFS recursion** (return info to the parent) | (4) | O(n) |
| Tree levels, shortest path unweighted, spread | **BFS** | `for _ in range(len(queue))` (4, 5) | O(V + E) |
| Prefix/dictionary search | **Trie** | (4) | O(length) |
| k best, merge k, running median | **Heap** | min-heap of size k (5) | O(n log k) |
| Dependencies, ordering, schedules | **Topological sort** | Kahn: in-degree zero queue (5) | O(V + E) |
| Connected? merge groups? cycle on adding edges? | **Union-Find** | `find` with compression (5) | ~O(n) |
| Shortest path with weights | **Dijkstra** (heap); Bellman-Ford for negatives or edge limits | (5) | O((V+E) log V) |
| Count ways, min/max cost, overlapping subproblems | **Dynamic programming** | state, transition, base, order (6) | O(states × choices) |
| Safe local choice (sort + scan), exchange argument | **Greedy** | (6) | O(n log n) |
| Odd one out, powers of two, subsets of a tiny set | **Bit manipulation** | XOR, `n & (n - 1)`, masks (6) | O(n) |

!cheat Eight questions to ask of any problem ::
1. What are the **input size and constraints**? (target complexity)
2. Is it **sorted**, or would sorting help?
3. Is the answer a **contiguous** piece, a **subset/arrangement**, a **path**, or a **number**?
4. Does a **greedy choice** hold, or are there **repeated subproblems**?
5. Is there a **graph** hiding (grid, words, states)?
6. What does the brute force **repeat**? Remove that with a map, memo or heap.
7. What are the **edge cases**? (empty, one element, duplicates, negatives, cycles, disconnected)
8. Can I say the **time and space** and the trade-off out loud?
!end

??  You read "find the minimum capacity such that all packages ship in D days". Which pattern, and what do you binary search?
=> Binary search on the answer: search capacities between `max(weights)` and `sum(weights)`, with a greedy O(n) `feasible(capacity)` check that counts days. The feasibility is monotonic (a larger capacity never needs more days).
??  "Return all valid IP addresses from a digit string." Which pattern?
=> Backtracking: choose the length of each of four segments (1 to 3 digits), prune segments with leading zeros or values above 255, and record a copy when four segments consume the whole string.

## Mixed Interview Questions

Solve each cold, then reveal. These combine patterns, which is how real interviews look.

!qa
**Insert, delete and get random in O(1).** Design a set that supports `insert(x)`, `remove(x)` and `get_random()` (each existing element equally likely), all in average O(1).
=>
```python RandomizedSet.py
import random


class RandomizedSet:
    def __init__(self):
        self.items, self.index = [], {}                       # a list for random access + a dict value -> position

    def insert(self, x):
        if x in self.index:
            return False
        self.index[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x):
        if x not in self.index:
            return False
        position, last = self.index[x], self.items[-1]
        self.items[position] = last                           # overwrite the removed slot with the last element ...
        self.index[last] = position
        self.items.pop()                                      # ... then drop the (now duplicate) tail: O(1)
        del self.index[x]
        return True

    def get_random(self):
        return random.choice(self.items)


rs = RandomizedSet()
assert rs.insert(1) and not rs.insert(1) and rs.insert(2) and rs.remove(1) and not rs.remove(1)
assert rs.get_random() == 2 and rs.insert(3) and rs.get_random() in (2, 3)
print("randomized set ok")
```
```output
```
A list gives O(1) random access, a dictionary gives O(1) lookup; deleting from the middle of a list is O(n), so **swap the element with the last one and pop**. Remember to update the moved element's index, including when removing the last element itself (the order of the assignments handles it).
!end

!qa
**Time-based key-value store.** `set(key, value, timestamp)` and `get(key, timestamp)` returning the value with the largest timestamp not after the query (or `""`).
=>
```python TimeMap.py
from bisect import bisect_right
from collections import defaultdict


class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)                        # key -> timestamps in increasing order (the sets arrive in order)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        i = bisect_right(self.times[key], timestamp)          # the first timestamp AFTER the query
        return self.values[key][i - 1] if i else ""


tm = TimeMap()
tm.set("foo", "bar", 1)
tm.set("foo", "bar2", 4)
assert tm.get("foo", 1) == "bar" and tm.get("foo", 3) == "bar" and tm.get("foo", 4) == "bar2" and tm.get("foo", 0) == "" and tm.get("none", 5) == ""
print("time map ok")
```
```output
```
Binary search over the timestamps of one key: O(log n) per `get`, O(1) per `set`. The pattern is "a sorted history plus `bisect`".
!end

!qa
**Valid Sudoku.** Check whether a partially filled 9x9 board is valid: no repeated digit in any row, column or 3x3 box (empty cells are `"."`).
=>
```python Sudoku.py
def is_valid_sudoku(board):
    seen = set()
    for r in range(9):
        for c in range(9):
            digit = board[r][c]
            if digit == ".":
                continue
            keys = {("row", r, digit), ("col", c, digit), ("box", r // 3, c // 3, digit)}
            if keys & seen:
                return False
            seen |= keys
    return True


valid = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]
invalid = ["83..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]
assert is_valid_sudoku(valid) and not is_valid_sudoku(invalid)                # the second has two 8s in the first column
print("sudoku ok")
```
```output
```
One pass, one set of tagged keys. The box index is `(r // 3, c // 3)`. This is "hash set of seen states" in its cleanest form.
!end

!qa
**Subarrays with product less than k** (positive integers): count the contiguous subarrays whose product is strictly less than `k`.
=>
```python ProductLessThanK.py
def num_subarray_product_less_than_k(nums, k):
    if k <= 1:
        return 0
    product, left, count = 1, 0, 0
    for right, n in enumerate(nums):
        product *= n
        while product >= k:
            product //= nums[left]
            left += 1
        count += right - left + 1                              # every subarray ending at `right` and starting in the window
    return count


assert num_subarray_product_less_than_k([10, 5, 2, 6], 100) == 8 and num_subarray_product_less_than_k([1, 2, 3], 0) == 0
print("product window ok")
```
```output
```
A variable sliding window (positive numbers, so growing the window only increases the product). The counting trick: for each right end, the valid starts form the window, contributing `window size` subarrays.
!end

!qa
**Longest increasing path in a matrix.** From any cell you may move up, down, left or right to a strictly larger value. Return the length of the longest path.
=>
```python LongestPath.py
from functools import cache


def longest_increasing_path(matrix):
    rows, cols = len(matrix), len(matrix[0])

    @cache
    def go(r, c):                                              # the longest path starting at (r, c)
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + go(nr, nc))
        return best

    return max(go(r, c) for r in range(rows) for c in range(cols))


assert longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]]) == 4 and longest_increasing_path([[3, 4, 5], [3, 2, 6], [2, 2, 1]]) == 4
assert longest_increasing_path([[1]]) == 1
print("longest increasing path ok")
```
```output
```
DFS with memoisation on a DAG (strictly increasing means no cycles, so no visited set is needed): O(rows × cols) time. It is DP over a graph, which is what the pattern map means by "graph hiding in a grid".
!end

!qa
**Clone a graph.** Given a node of a connected undirected graph (each node has a value and a list of neighbours), return a deep copy.
=>
```python CloneGraph.py
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val, self.neighbors = val, neighbors or []


def clone_graph(node):
    if not node:
        return None
    copies = {node: Node(node.val)}                            # original -> copy, doubles as the visited set
    stack = [node]
    while stack:
        current = stack.pop()
        for neighbour in current.neighbors:
            if neighbour not in copies:
                copies[neighbour] = Node(neighbour.val)
                stack.append(neighbour)
            copies[current].neighbors.append(copies[neighbour])
    return copies[node]


a, b, c = Node(1), Node(2), Node(3)
a.neighbors, b.neighbors, c.neighbors = [b, c], [a, c], [a, b]
copy = clone_graph(a)
assert copy is not a and copy.val == 1 and sorted(n.val for n in copy.neighbors) == [2, 3]
assert copy.neighbors[0] is not b and copy.neighbors[0].neighbors[0] is copy                  # the copy is a real cycle, not shared nodes
print("clone graph ok")
```
```output
```
The dictionary from original to copy is both the memo (reuse existing copies, which preserves cycles) and the visited set.
!end

!qa
**Pacific Atlantic water flow.** Cells of a height grid; water flows to equal or lower neighbours. Return the cells from which water can reach both the top/left edges (Pacific) and the bottom/right edges (Atlantic).
=>
```python PacificAtlantic.py
def pacific_atlantic(heights):
    rows, cols = len(heights), len(heights[0])

    def reach(starts):                                         # flow BACKWARDS: from the ocean uphill
        seen, stack = set(starts), list(starts)
        while stack:
            r, c = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    pacific = reach([(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)])
    atlantic = reach([(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows)])
    return sorted(pacific & atlantic)


grid = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]
assert pacific_atlantic(grid) == [(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]
print("pacific atlantic ok")
```
```output
```
The insight is to **reverse the question**: instead of asking from every cell "can it reach the ocean?" (O(n²m²)), start from the ocean borders and flow uphill, once per ocean: O(n·m). Reversing the direction of a search is a common optimisation.
!end

!qa
**Basic calculator II.** Evaluate an expression with non-negative integers and `+ - * /` (integer division, truncating), no parentheses: `"3+2*2"` is 7, `" 3/2 "` is 1.
=>
```python Calculator.py
def calculate(s):
    stack, number, op = [], 0, "+"
    for i, ch in enumerate(s + "+"):                           # a sentinel operator flushes the last number
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-*/":
            if op == "+":
                stack.append(number)
            elif op == "-":
                stack.append(-number)
            elif op == "*":
                stack.append(stack.pop() * number)             # * and / bind tighter: apply to the previous term now
            else:
                stack.append(int(stack.pop() / number))        # int() truncates toward zero, like the requirement
            number, op = 0, ch
    return sum(stack)


assert calculate("3+2*2") == 7 and calculate(" 3/2 ") == 1 and calculate(" 3+5 / 2 ") == 5 and calculate("14-3/2") == 13 and calculate("2*3-4*5") == -14
print("calculator ok")
```
```output
```
Terms are pushed on a stack; `*` and `/` fix up the top immediately; `+` and `-` just push signed numbers, and the answer is the sum of the stack.
!end

!qa
**K pairs with the smallest sums.** Given two sorted arrays, return the k pairs `(u, v)` (one from each) with the smallest sums.
=>
```python KPairs.py
import heapq


def k_smallest_pairs(a, b, k):
    if not a or not b:
        return []
    heap = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]       # start with each a[i] paired with b[0]
    heapq.heapify(heap)
    result = []
    while heap and len(result) < k:
        _, i, j = heapq.heappop(heap)
        result.append([a[i], b[j]])
        if j + 1 < len(b):
            heapq.heappush(heap, (a[i] + b[j + 1], i, j + 1))         # the next candidate in that row
    return result


assert k_smallest_pairs([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]]
assert k_smallest_pairs([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]] and k_smallest_pairs([1, 2], [3], 3) == [[1, 3], [2, 3]]
print("k pairs ok")
```
```output
```
It is a **merge of k sorted lists** in disguise: row i is `a[i] + b[0], a[i] + b[1], ...`, which is sorted. O(k log k) time instead of the O(n·m) of generating every pair.
!end

## Mock Interview Walkthroughs

Three complete walkthroughs in the shape of a real interview, with the sentences to say. Notice that the code is the **last** third of each conversation.

### Walkthrough 1: top K frequent words

| Stage | What you say |
| --- | --- |
| Clarify | "Given a list of words and k, return the k most frequent, ties broken alphabetically? Can k exceed the number of distinct words? Case sensitive?" |
| Example | "`['i','love','leetcode','i','love','coding'], k = 2` gives `['i','love']` since both have count 2 and `i` is alphabetically first." |
| Brute force | "Count with a hash map, sort all distinct words by `(-count, word)`, take k. That is O(n + m log m) for m distinct words." |
| Improve | "If k is much smaller than m, a heap of size k gives O(n + m log k). With `heapq.nsmallest` and the key `(-count, word)` it is the same code size." |
| Code | below |
| Test | "Ties: both count 2, order alphabetical. k = number of distinct words: returns all. One word." |
| Complexity | "O(n) to count, O(m log k) selection, O(m) space." |

```python TopKWords.py
import heapq
from collections import Counter


def top_k_frequent_words(words, k):
    counts = Counter(words)
    return heapq.nsmallest(k, counts, key=lambda word: (-counts[word], word))


assert top_k_frequent_words(["i", "love", "leetcode", "i", "love", "coding"], 2) == ["i", "love"]
assert top_k_frequent_words(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4) == ["the", "is", "sunny", "day"]
assert top_k_frequent_words(["a"], 1) == ["a"]
print("top k words ok")
```

```output
```

### Walkthrough 2: LRU cache without OrderedDict

| Stage | What you say |
| --- | --- |
| Clarify | "`get` and `put` must be O(1); capacity is fixed; `get` of a missing key returns -1; both operations make the key most recently used?" |
| Design | "A hash map from key to node gives O(1) lookup; a doubly linked list ordered by recency gives O(1) move-to-front and O(1) eviction of the tail. Dummy head and tail nodes remove edge cases." |
| Code | below |
| Test | "Capacity 2: put 1, put 2, get 1, put 3 evicts 2; get 2 is -1; put 4 evicts 1." |
| Follow-ups | "Thread safety: a lock around each method. A distributed cache: shard by consistent hashing. TTL: store an expiry per node. In production I would use `functools.lru_cache` or `OrderedDict`." |

```python LruManual.py
class Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=0, value=0):
        self.key, self.value, self.prev, self.next = key, value, None, None


class LRUCache:
    def __init__(self, capacity):
        self.capacity, self.nodes = capacity, {}
        self.head, self.tail = Node(), Node()                   # sentinels: most recent just after head, least recent just before tail
        self.head.next, self.tail.prev = self.tail, self.head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value):
        if key in self.nodes:
            self._unlink(self.nodes[key])
        node = self.nodes[key] = Node(key, value)
        self._push_front(node)
        if len(self.nodes) > self.capacity:
            oldest = self.tail.prev
            self._unlink(oldest)
            del self.nodes[oldest.key]


cache = LRUCache(2)
cache.put(1, 1); cache.put(2, 2)
assert cache.get(1) == 1
cache.put(3, 3)
assert cache.get(2) == -1
cache.put(4, 4)
assert (cache.get(1), cache.get(3), cache.get(4)) == (-1, 3, 4)
print("lru ok")
```

```output
```

### Walkthrough 3: median of two sorted arrays

| Stage | What you say |
| --- | --- |
| Clarify | "Two sorted arrays, possibly empty; return the median of the combined data; required complexity O(log(m + n))?" |
| Brute force | "Merge and take the middle: O(m + n). Good, but not logarithmic." |
| Insight | "The median splits the combined data into a left half and a right half of equal size. I binary search how many elements `i` of the shorter array go in the left half; the rest of the left half, `j = half - i`, comes from the other array. The split is correct when `a_left <= b_right` and `b_left <= a_right`." |
| Edge cases | "`i = 0` or `i = m` means no element on that side: use minus and plus infinity as sentinels." |
| Code | below |

```python MedianTwoArrays.py
def find_median_sorted_arrays(a, b):
    if len(a) > len(b):
        a, b = b, a                                              # binary search over the shorter array
    m, n = len(a), len(b)
    lo, hi, half = 0, m, (m + n + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2                                       # elements of a in the left half
        j = half - i                                             # elements of b in the left half
        a_left, a_right = (a[i - 1] if i else float("-inf")), (a[i] if i < m else float("inf"))
        b_left, b_right = (b[j - 1] if j else float("-inf")), (b[j] if j < n else float("inf"))
        if a_left <= b_right and b_left <= a_right:              # a valid partition
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1                                           # took too many from a
        else:
            lo = i + 1


assert find_median_sorted_arrays([1, 3], [2]) == 2.0 and find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
assert find_median_sorted_arrays([], [1]) == 1.0 and find_median_sorted_arrays([0, 0], [0, 0]) == 0.0 and find_median_sorted_arrays([2], []) == 2.0
import random
for _ in range(200):                                             # compare with the brute force on random inputs
    x, y = sorted(random.sample(range(50), random.randint(0, 8))), sorted(random.sample(range(50), random.randint(1, 8)))
    merged = sorted(x + y)
    expected = merged[len(merged) // 2] if len(merged) % 2 else (merged[len(merged) // 2 - 1] + merged[len(merged) // 2]) / 2
    assert find_median_sorted_arrays(x, y) == expected
print("median ok")
```

```output
```

!interview Property-based checking is a superpower :: The last block compares a clever O(log n) solution with a trivial brute force on 200 random inputs. In an interview, saying "I would test this against a brute force on random small inputs" for any tricky algorithm shows real engineering maturity. Hypothesis (Core Python, Part 12) automates it.

??  How do you practise a mock interview alone?
=> Pick a problem you have not seen, set a 40-minute timer, speak out loud through clarify, example, brute force, improvement, code and test, write the code in a plain editor without autocomplete, then compare with a reference and write down what you missed. Recording yourself helps spot silent stretches.
??  What should you do in the last five minutes of a coding interview?
=> Run your example through the code line by line, test one edge case, state the time and space complexity, and mention the trade-off or follow-up (streaming input, memory limits, parallelism). Do not rewrite the solution; fix what the trace found.

## Complexity and Python Cheat Sheet

| Operation | Cost | | Operation | Cost |
| --- | --- | --- | --- | --- |
| `list` index, append, pop() | O(1) | | `dict`/`set` get, set, `in` | O(1) avg |
| `list.insert(0)`, `pop(0)`, `in` | O(n) | | `sorted`, `list.sort` | O(n log n) |
| `deque` append/pop both ends | O(1) | | `heappush`, `heappop` | O(log n) |
| `heapify` | O(n) | | `bisect_left` | O(log n) |
| slice `a[i:j]` | O(j - i) | | `str` concat / slice | O(length) |

| Algorithm | Time | Space |
| --- | --- | --- |
| Binary search | O(log n) | O(1) |
| Merge sort / heap sort | O(n log n) | O(n) / O(1) |
| Quicksort | O(n log n) average, O(n²) worst | O(log n) |
| BFS / DFS | O(V + E) | O(V) |
| Dijkstra (heap) | O((V + E) log V) | O(V) |
| Bellman-Ford | O(VE) | O(V) |
| Topological sort | O(V + E) | O(V) |
| Union-Find | ~O(α(n)) per op | O(n) |
| Trie insert/search | O(length) | O(total characters) |
| Knapsack (0/1) | O(n · W) | O(W) |
| LCS / edit distance | O(n · m) | O(min(n, m)) |
| Subsets / permutations | O(2ⁿ) / O(n!) | O(n) |

| Python snippet | Purpose |
| --- | --- |
| `from collections import Counter, defaultdict, deque` | counting, grouping, queues |
| `import heapq`; `heapq.heappush(h, x)`; `-x` for a max-heap | priority queue |
| `from bisect import bisect_left, bisect_right, insort` | binary search |
| `from functools import cache` | memoised recursion |
| `float("inf")`, `math.inf` | initial min/max |
| `for dr, dc in ((1,0),(-1,0),(0,1),(0,-1))` | grid neighbours |
| `sorted(x, key=lambda a: (-a.score, a.name))` | multi-key sort |
| `a, b = b, a + b`; `x, *rest = items` | swaps, unpacking |
| `sys.setrecursionlimit(10**6)` | contests only, with care |

## A 14-Week Study Plan

About one hour a day on weekdays and two on weekends; two to three new problems per session, the rest revision. "Re-solve" means from memory a week later.

| Week | Focus | Goal |
| --- | --- | --- |
| 1 | Foundations (Part 1), arrays and hashing | 12 easy problems; write a trace for each |
| 2 | Prefix sums, two pointers, sliding window | 12 problems; re-solve week 1 |
| 3 | Binary search (index and on the answer) | 10 problems including 4 "on the answer" |
| 4 | Intervals, sorting, greedy scans | 10 problems; mock interview 1 |
| 5 | Linked lists, stacks, queues | 12 problems; implement all list operations without notes |
| 6 | Monotonic stack and deque | 8 problems; re-solve weeks 2 to 4 |
| 7 | Recursion and backtracking | 10 problems; draw the recursion tree for each |
| 8 | Trees: DFS, BFS, BST | 14 problems; mock interview 2 |
| 9 | Tries, heaps and top-k | 10 problems; implement `heapq` operations by hand once |
| 10 | Graphs: BFS, DFS, topological sort | 12 problems; grid and word-ladder variants |
| 11 | Union-find and shortest paths | 10 problems; Dijkstra from memory |
| 12 | Dynamic programming 1: 1-D, grids, knapsack | 14 problems; always write state and recurrence first |
| 13 | Dynamic programming 2 and greedy, bits | 12 problems; mock interview 3 |
| 14 | Revision: mixed sets, timed (45 minutes per problem), weak patterns | 3 mock interviews; update the error log |

## Final Checklist and How to Practise on LeetCode

**The habits that produce results**

1. **Pattern first, code second.** After each problem write one line: "signal, pattern, trick". Review the lines weekly; they are your recognition training.
2. **Solve, then re-solve.** A problem is *done* when you can reproduce it from a blank file a week later.
3. **Time-box.** 25 to 30 minutes of honest effort, then read a hint, then the solution; then close it and code from memory.
4. **Keep an error log**: wrong complexity, missed edge case, off-by-one, forgotten visited set.
5. **Talk while you code.** Practise with a friend, a rubber duck or a recorder.
6. **Use the whole standard library**: `Counter`, `heapq`, `bisect`, `deque`, `itertools`, `functools.cache`.

**A balanced list to practise (problem names with LeetCode numbers)**

| Pattern | Problems |
| --- | --- |
| Hashing, arrays | Two Sum (1), Group Anagrams (49), Top K Frequent Elements (347), Longest Consecutive Sequence (128), Product of Array Except Self (238) |
| Two pointers, windows | 3Sum (15), Container With Most Water (11), Trapping Rain Water (42), Longest Substring Without Repeating Characters (3), Minimum Window Substring (76), Sliding Window Maximum (239) |
| Binary search | Search in Rotated Sorted Array (33), Koko Eating Bananas (875), Find Minimum in Rotated Sorted Array (153), Median of Two Sorted Arrays (4), Time Based Key-Value Store (981) |
| Intervals, greedy | Merge Intervals (56), Meeting Rooms II (253), Non-overlapping Intervals (435), Jump Game (55), Gas Station (134) |
| Linked list, stack | Reverse Linked List (206), Merge Two Sorted Lists (21), Linked List Cycle (141), LRU Cache (146), Valid Parentheses (20), Daily Temperatures (739), Largest Rectangle in Histogram (84) |
| Trees | Maximum Depth (104), Validate BST (98), Lowest Common Ancestor (236), Binary Tree Level Order Traversal (102), Binary Tree Maximum Path Sum (124), Implement Trie (208) |
| Backtracking | Subsets (78), Permutations (46), Combination Sum (39), Word Search (79), N-Queens (51) |
| Heaps | Kth Largest Element (215), Find Median from Data Stream (295), Merge k Sorted Lists (23), Task Scheduler (621) |
| Graphs | Number of Islands (200), Clone Graph (133), Course Schedule (207), Pacific Atlantic Water Flow (417), Word Ladder (127), Network Delay Time (743), Cheapest Flights Within K Stops (787), Redundant Connection (684) |
| Dynamic programming | Climbing Stairs (70), House Robber (198), Coin Change (322), Longest Increasing Subsequence (300), Longest Common Subsequence (1143), Edit Distance (72), Word Break (139), Partition Equal Subset Sum (416), Unique Paths (62) |
| Bits | Single Number (136), Number of 1 Bits (191), Missing Number (268) |

Search a problem by its number or name on LeetCode; the free problem set is enough, and editorials explain the standard approaches. Treat sites as practice rooms, not as the syllabus: this guide is the syllabus.

!keypoints Pattern first, then code ;; Say complexity and trade-offs before they ask ;; Dry-run before declaring done ;; Re-solve from memory a week later ;; Test tricky algorithms against a brute force ;; Two problems a day, kept for fourteen weeks

??  What does "done" mean for a practice problem?
=> You can reproduce a correct solution from a blank file, with the complexity and the pattern stated, a week after first solving it. Reading a solution and nodding is not done.
??  You have two weeks before interviews. What do you do?
=> Stop learning new topics. Re-solve the problems from your error log, do two timed mock problems a day across mixed patterns, review the pattern table and cheat sheets, practise explaining out loud, and sleep. Depth of recall beats breadth of exposure at this point.
