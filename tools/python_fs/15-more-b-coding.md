@more
## Coding Problems: Strings and Arrays

Try each problem on paper or in your editor first (state the complexity you are aiming for), then reveal the reference solution. Every solution below is run, with assertions as its tests, when this page is built.

!qa
**Two Sum.** Given a list of integers and a target, return the indices of the two numbers that add up to the target (exactly one solution exists). `[2, 7, 11, 15]`, target `9` returns `[0, 1]`. Aim for O(n).
=>
```python TwoSum.py
def two_sum(nums, target):
    seen = {}                                   # value -> index of values already visited
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    raise ValueError("no solution")

assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]
print(two_sum([2, 7, 11, 15], 9))
```
```output
```
O(n) time, O(n) space. The brute force is O(n²); the hash map answers "have I seen the complement?" in O(1). Check the complement **before** inserting the current value, so an element is never paired with itself.
!end

!qa
**Group anagrams.** Given a list of words, group the words that are anagrams of each other: `["eat","tea","tan","ate","nat","bat"]` gives `[["eat","tea","ate"],["tan","nat"],["bat"]]` (any order).
=>
```python Anagrams.py
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        groups[tuple(sorted(word))].append(word)         # anagrams share the same sorted letters
    return list(groups.values())

result = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
assert sorted(map(sorted, result)) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
print(result)
```
```output
```
O(n · k log k) for n words of length k. A faster key counts letters instead of sorting: `tuple(Counter(word).items())` sorted, or a 26-slot tuple, which makes it O(n · k).
!end

!qa
**Longest substring without repeating characters.** Return the length of the longest substring of `s` with no repeated character. `"abcabcbb"` gives `3`, `"bbbbb"` gives `1`, `"pwwkew"` gives `3`.
=>
```python LongestSubstring.py
def longest_unique(s):
    last_seen, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= start:
            start = last_seen[ch] + 1                    # move the window past the previous occurrence
        last_seen[ch] = i
        best = max(best, i - start + 1)
    return best

assert [longest_unique(s) for s in ("abcabcbb", "bbbbb", "pwwkew", "", "abba")] == [3, 1, 3, 0, 2]
print(longest_unique("abcabcbb"))
```
```output
```
**Sliding window**, O(n) time, O(alphabet) space. The window `[start, i]` always holds unique characters; on a repeat inside the window, `start` jumps just past the earlier copy. The `>= start` check is what makes `"abba"` come out right.
!end

!qa
**Valid parentheses.** Given a string containing only `()[]{}`, decide whether the brackets are balanced and correctly nested: `"([]{})"` is valid, `"(]"` and `"(()"` are not.
=>
```python Brackets.py
def is_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack                                     # nothing may be left open

assert is_balanced("([]{})") and is_balanced("") and not is_balanced("(]") and not is_balanced("(()") and not is_balanced("]")
print([is_balanced(s) for s in ("([]{})", "(]", "(()")])
```
```output
```
O(n) time, O(n) space. A **stack** matches each closer with the most recent unmatched opener. Edge cases: an empty string, a closer with an empty stack, and leftover openers.
!end

!qa
**Merge intervals.** Merge all overlapping intervals: `[[1,3],[2,6],[8,10],[15,18]]` gives `[[1,6],[8,10],[15,18]]`.
=>
```python Intervals.py
def merge(intervals):
    merged = []
    for start, end in sorted(intervals):                  # sort by start
        if merged and start <= merged[-1][1]:             # overlaps the previous interval
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge([[1, 4], [4, 5]]) == [[1, 5]] and merge([[1, 4], [2, 3]]) == [[1, 4]] and merge([]) == []
print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))
```
```output
```
O(n log n) for the sort, O(n) for the merge. Sorting by start guarantees that an interval can only overlap the **last** merged one. Watch the contained-interval case (`[1,4]` and `[2,3]`), where the end must not shrink: hence `max`.
!end

!qa
**Product of array except self.** For each position return the product of all other elements, **without division**, in O(n): `[1,2,3,4]` gives `[24,12,8,6]`.
=>
```python ProductExceptSelf.py
def product_except_self(nums):
    result = [1] * len(nums)
    prefix = 1
    for i, n in enumerate(nums):                          # result[i] = product of everything to the LEFT
        result[i] = prefix
        prefix *= n
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):                # multiply by the product of everything to the RIGHT
        result[i] *= suffix
        suffix *= nums[i]
    return result

assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
print(product_except_self([1, 2, 3, 4]))
```
```output
```
O(n) time, O(1) extra space beyond the output. Two passes build left and right products; zeros need no special case because there is no division.
!end

!qa
**Maximum subarray.** Find the contiguous subarray with the largest sum and return that sum: `[-2,1,-3,4,-1,2,1,-5,4]` gives `6` (the subarray `[4,-1,2,1]`).
=>
```python Kadane.py
def max_subarray(nums):
    best = current = nums[0]
    for n in nums[1:]:
        current = max(n, current + n)                     # extend the run, or start again at n
        best = max(best, current)
    return best

assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([1]) == 1 and max_subarray([-3, -1, -2]) == -1 and max_subarray([5, 4, -1, 7, 8]) == 23
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))
```
```output
```
**Kadane's algorithm**: O(n) time, O(1) space. At each element decide whether a running sum that has gone negative is worth keeping (it is not). Initialise from the first element, not zero, so all-negative arrays work.
!end

!qa
**Move zeroes.** Move all zeros to the end of a list **in place**, keeping the order of the non-zero items: `[0,1,0,3,12]` becomes `[1,3,12,0,0]`.
=>
```python MoveZeroes.py
def move_zeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]   # swap keeps the work to one pass
            write += 1

data = [0, 1, 0, 3, 12]
move_zeroes(data)
assert data == [1, 3, 12, 0, 0]
other = [0, 0, 1]
move_zeroes(other)
assert other == [1, 0, 0]
print(data)
```
```output
```
**Two pointers**: O(n) time, O(1) space. `write` marks where the next non-zero item belongs; `read` scans. The function mutates its argument and returns `None`, a Python convention that signals in-place work.
!end

!qa
**Valid palindrome.** Is the string a palindrome, considering only letters and digits and ignoring case? `"A man, a plan, a canal: Panama"` is true.
=>
```python Palindrome.py
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].casefold() != s[right].casefold():
            return False
        left, right = left + 1, right - 1
    return True

assert is_palindrome("A man, a plan, a canal: Panama") and is_palindrome("") and not is_palindrome("race a car")
print(is_palindrome("A man, a plan, a canal: Panama"))
```
```output
```
O(n) time, O(1) space with two pointers. The one-liner `c = [ch.casefold() for ch in s if ch.isalnum()]; return c == c[::-1]` is also fine and clearer when memory is not constrained; mention both.
!end

## Coding Problems: Collections, Recursion and Dynamic Programming

!qa
**Top K frequent elements.** Return the `k` most frequent values of a list: `[1,1,1,2,2,3]`, `k=2` gives `[1,2]`.
=>
```python TopK.py
import heapq
from collections import Counter

def top_k(nums, k):
    counts = Counter(nums)
    return [value for value, _ in counts.most_common(k)]          # O(n log k) internally with a heap

def top_k_heap(nums, k):
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)

assert top_k([1, 1, 1, 2, 2, 3], 2) == [1, 2] == top_k_heap([1, 1, 1, 2, 2, 3], 2)
assert top_k([1], 1) == [1]
print(top_k([1, 1, 1, 2, 2, 3], 2))
```
```output
```
O(n) to count plus O(m log k) to select among m distinct values. Bucket sort by frequency gives O(n) overall: `buckets[count].append(value)`, then read from the highest frequency down.
!end

!qa
**Flatten a nested list** of arbitrary depth, lazily: `[1, [2, [3, 4]], 5]` yields `1, 2, 3, 4, 5`. Strings must not be split into characters.
=>
```python Flatten.py
def flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)                     # recursion through yield from
        else:
            yield item

assert list(flatten([1, [2, [3, 4]], 5])) == [1, 2, 3, 4, 5]
assert list(flatten(["ab", ["cd"], []])) == ["ab", "cd"]
print(list(flatten([1, [2, [3, 4]], 5])))
```
```output
```
O(n) time for n leaves, O(depth) stack. It is a generator, so huge structures stream. Very deep nesting can hit the recursion limit: use an explicit stack (`stack = [iter(items)]`) in that case.
!end

!qa
**Subsets and permutations (backtracking).** Return all subsets of a list of distinct numbers, and all permutations. `[1,2,3]` has 8 subsets and 6 permutations.
=>
```python Backtracking.py
def subsets(nums):
    result, path = [], []

    def backtrack(start):
        result.append(path[:])                           # every partial path is a subset
        for i in range(start, len(nums)):
            path.append(nums[i])                          # choose
            backtrack(i + 1)                              # explore
            path.pop()                                    # un-choose

    backtrack(0)
    return result

def permutations(nums):
    result = []

    def backtrack(path, remaining):
        if not remaining:
            result.append(path)
            return
        for i, n in enumerate(remaining):
            backtrack(path + [n], remaining[:i] + remaining[i + 1:])

    backtrack([], nums)
    return result

assert len(subsets([1, 2, 3])) == 8 and [] in subsets([1, 2, 3]) and [1, 2, 3] in subsets([1, 2, 3])
assert len(permutations([1, 2, 3])) == 6 and permutations([1, 2]) == [[1, 2], [2, 1]]
print(subsets([1, 2, 3]))
print(permutations([1, 2, 3]))
```
```output
```
Subsets: O(n · 2ⁿ); permutations: O(n · n!). The pattern is **choose, explore, un-choose**. In real code `itertools.permutations` and `itertools.combinations` do this in C; interviewers want to see the recursion.
!end

!qa
**Coin change.** Given coin denominations and an amount, return the fewest coins that make the amount, or `-1`: coins `[1,2,5]`, amount `11` gives `3` (5+5+1).
=>
```python CoinChange.py
def coin_change(coins, amount):
    INF = amount + 1
    best = [0] + [INF] * amount                           # best[a] = fewest coins for amount a
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                best[a] = min(best[a], best[a - coin] + 1)
    return best[amount] if best[amount] != INF else -1

assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1 and coin_change([1], 0) == 0 and coin_change([186, 419, 83, 408], 6249) == 20
print(coin_change([1, 2, 5], 11))
```
```output
```
**Dynamic programming**: O(amount × coins) time, O(amount) space. Greedy (largest coin first) is wrong for denominations like `[1, 3, 4]`, amount `6` (greedy gives 4+1+1, optimal is 3+3). State the recurrence out loud: `best[a] = 1 + min(best[a - coin])`.
!end

!qa
**Longest common subsequence.** Return the length of the longest common subsequence of two strings: `"abcde"` and `"ace"` gives `3`.
=>
```python Lcs.py
def lcs(a, b):
    previous = [0] * (len(b) + 1)
    for ch in a:
        current = [0]
        for j, other in enumerate(b, start=1):
            current.append(previous[j - 1] + 1 if ch == other else max(previous[j], current[j - 1]))
        previous = current                                # only the previous row is needed
    return previous[-1]

assert lcs("abcde", "ace") == 3 and lcs("abc", "def") == 0 and lcs("", "x") == 0 and lcs("AGGTAB", "GXTXAYB") == 4
print(lcs("abcde", "ace"))
```
```output
```
O(len(a) × len(b)) time; O(len(b)) space by keeping two rows (a full table would be O(len(a) × len(b)) and lets you reconstruct the subsequence by walking back).
!end

!qa
**Binary search and its variants.** Find any index of `target` in a sorted list or `-1`; then find the first and last index of a value with duplicates.
=>
```python BinarySearch.py
from bisect import bisect_left, bisect_right

def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2                              # Python ints do not overflow
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def first_last(nums, target):
    left = bisect_left(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, bisect_right(nums, target) - 1]

data = [1, 2, 2, 2, 5, 8]
assert search(data, 5) == 4 and search(data, 7) == -1 and search([], 1) == -1
assert first_last(data, 2) == [1, 3] and first_last(data, 3) == [-1, -1]
print(search(data, 5), first_last(data, 2))
```
```output
```
O(log n). Know the loop invariant (`target` is always inside `[lo, hi]` if present) and the off-by-one choices (`<=`, `mid ± 1`). For first/last occurrence use `bisect_left` and `bisect_right`.
!end

!qa
**Number of islands.** In a grid of `"1"` (land) and `"0"` (water), count the islands (groups of land connected up, down, left, right).
=>
```python Islands.py
from collections import deque

def num_islands(grid):
    if not grid:
        return 0
    rows, cols, seen, count = len(grid), len(grid[0]), set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                queue = deque([(r, c)])
                seen.add((r, c))
                while queue:                              # BFS flood fill
                    y, x = queue.popleft()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and (ny, nx) not in seen:
                            seen.add((ny, nx))
                            queue.append((ny, nx))
    return count

grid = ["11000", "11000", "00100", "00011"]
assert num_islands(grid) == 3 and num_islands([]) == 0 and num_islands(["0"]) == 0
print(num_islands(grid))
```
```output
```
O(rows × cols) time and space. Mark cells as seen when you **enqueue** them, not when you dequeue, or the same cell is queued many times. A recursive DFS is shorter but can hit the recursion limit on large grids.
!end

!qa
**Merge k sorted lists** into one sorted list, efficiently.
=>
```python MergeK.py
import heapq

def merge_k(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]     # (value, which list, position)
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heapq.heappop(heap)
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out

lists = [[1, 4, 7], [2, 5], [], [0, 3, 6, 9]]
assert merge_k(lists) == sorted(sum(lists, [])) == list(heapq.merge(*lists))
print(merge_k(lists))
```
```output
```
O(N log k) for N total items and k lists, O(k) extra space. The heap always holds the smallest unmerged item of each list. In production use `heapq.merge`, which does this lazily.
!end

## Concurrency Coding Tasks

!qa
**Rate limiter.** Implement a thread-safe token-bucket limiter: `allow()` returns whether a call may proceed, allowing bursts up to `capacity` and refilling `rate` tokens per second. Make time injectable so it is testable.
=>
```python RateLimiter.py
import threading
import time

class TokenBucket:
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate, self.capacity, self.clock = rate, capacity, clock
        self.tokens, self.updated = float(capacity), clock()
        self._lock = threading.Lock()

    def allow(self, cost=1):
        with self._lock:                                  # refill and spend in one critical section
            now = self.clock()
            self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
            self.updated = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False

now = [0.0]
bucket = TokenBucket(rate=2, capacity=3, clock=lambda: now[0])
assert [bucket.allow() for _ in range(4)] == [True, True, True, False]      # burst of 3, then empty
now[0] += 1.0                                                              # one second: 2 tokens refilled
assert [bucket.allow() for _ in range(3)] == [True, True, False]
now[0] += 100                                                              # long idle: capped at capacity
assert sum(bucket.allow() for _ in range(10)) == 3
print("token bucket ok")
```
```output
```
Token bucket allows bursts; a **fixed window** counter is simpler but permits double bursts at window edges; a **sliding window log** is exact but uses more memory. In a distributed service the state lives in Redis (atomic Lua script or `INCR` with expiry), covered in the Redis part of this tree.
!end

!qa
**Ping-pong.** Two threads must print `ping` and `pong` alternately, exactly `n` times each, no matter how the scheduler runs them.
=>
```python PingPong.py
import threading

def ping_pong(n):
    out = []
    turn_ping, turn_pong = threading.Event(), threading.Event()
    turn_ping.set()                                       # ping goes first

    def ping():
        for _ in range(n):
            turn_ping.wait()
            turn_ping.clear()
            out.append("ping")
            turn_pong.set()

    def pong():
        for _ in range(n):
            turn_pong.wait()
            turn_pong.clear()
            out.append("pong")
            turn_ping.set()

    threads = [threading.Thread(target=ping), threading.Thread(target=pong)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return out

assert ping_pong(4) == ["ping", "pong"] * 4
print(ping_pong(3))
```
```output
```
Two `Event`s hand a baton back and forth; each thread waits for its turn, clears the flag, acts, then signals the other. `Condition` or two `Semaphore(0)` objects work as well. The point is expressing **ordering** with synchronisation, never with `sleep`.
!end

!qa
**Async fetch with a concurrency limit and timeout.** Fetch many URLs concurrently, at most `limit` at a time, each with a timeout, returning results in input order and recording failures instead of aborting the batch.
=>
```python AsyncFetch.py
import asyncio

async def fake_fetch(url):
    await asyncio.sleep({"slow": 1.0, "fast": 0.01}.get(url.split("/")[-1], 0.02))
    if url.endswith("boom"):
        raise ConnectionError("refused")
    return f"body of {url}"

async def fetch_all(urls, limit=3, timeout=0.2):
    semaphore = asyncio.Semaphore(limit)
    in_flight = peak = 0

    async def one(url):
        nonlocal in_flight, peak
        async with semaphore:
            in_flight += 1
            peak = max(peak, in_flight)
            try:
                async with asyncio.timeout(timeout):
                    return await fake_fetch(url)
            except TimeoutError:
                return "timeout"
            except ConnectionError as error:
                return f"error: {error}"
            finally:
                in_flight -= 1

    results = await asyncio.gather(*(one(u) for u in urls))
    return results, peak

urls = ["http://x/fast", "http://x/slow", "http://x/boom", "http://x/a", "http://x/b", "http://x/c", "http://x/d"]
results, peak = asyncio.run(fetch_all(urls))
assert results[0] == "body of http://x/fast" and results[1] == "timeout" and results[2] == "error: refused" and len(results) == 7
assert peak == 3
print(results[:3], "peak concurrency:", peak)
```
```output
```
A `Semaphore` caps concurrency, `asyncio.timeout` bounds each call, `gather` preserves input order, and exceptions are converted into values so one failure does not cancel the batch (use `return_exceptions=True` or a `TaskGroup` with per-task handling in other designs).
!end

!qa
**Retry decorator.** Write `@retry(attempts, base_delay, exceptions)` with exponential backoff that re-raises the last error, retries only the given exception types, and has an injectable `sleep` for tests.
=>
```python Retry.py
import functools
import time

def retry(attempts=3, base_delay=0.1, exceptions=(Exception,), sleep=time.sleep):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts - 1:
                        raise                              # out of attempts: surface the real error
                    sleep(base_delay * 2 ** attempt)       # 0.1, 0.2, 0.4 ...
        return wrapper
    return decorate

delays, calls = [], []

@retry(attempts=4, base_delay=0.1, exceptions=(ConnectionError,), sleep=delays.append)
def flaky():
    calls.append(1)
    if len(calls) < 3:
        raise ConnectionError("down")
    return "ok"

assert flaky() == "ok" and len(calls) == 3 and delays == [0.1, 0.2]

@retry(attempts=2, exceptions=(ConnectionError,), sleep=lambda s: None)
def bad_input():
    raise ValueError("not retried")

try:
    bad_input()
except ValueError:
    print("ValueError passed straight through; backoff delays were", delays)
```
```output
```
Only retry **transient, idempotent** operations; add jitter (`random.uniform`) so many clients do not retry in lockstep; cap the delay and the total time; and never retry on programming errors such as `ValueError`.
!end

## Output Prediction and Debugging Drills

Each drill shows code that misbehaves. Find the bug first, then check the diagnosis and fix. The failing behaviour and the fixed behaviour are both produced by running the code.

!qa
**Drill 1.** This word counter crashes on the first word. Why, and what are two clean fixes?
```python Drill01.py !fail
words = "to be or not to be".split()
counts = {}
for word in words:
    counts[word] += 1
print(counts)
```
=>
```output
```
`counts[word]` does not exist yet, so `+= 1` raises `KeyError`. Fixes:
```python Drill01Fixed.py
from collections import Counter, defaultdict

words = "to be or not to be".split()
by_counter = Counter(words)

by_default = defaultdict(int)
for word in words:
    by_default[word] += 1

manual = {}
for word in words:
    manual[word] = manual.get(word, 0) + 1

assert by_counter == by_default == manual == {"to": 2, "be": 2, "or": 1, "not": 1}
print(dict(by_counter))
```
```output
```
!end

!qa
**Drill 2.** Remove every inactive user from the dictionary. What is wrong?
```python Drill02.py !fail
users = {"asha": True, "ravi": False, "meera": True, "john": False}
for name, active in users.items():
    if not active:
        del users[name]
print(users)
```
=>
```output
```
Changing the dictionary's size while iterating over it raises `RuntimeError`. Build a new dictionary (or iterate over a copy):
```python Drill02Fixed.py
users = {"asha": True, "ravi": False, "meera": True, "john": False}
active_only = {name: flag for name, flag in users.items() if flag}      # preferred
for name in [n for n, flag in users.items() if not flag]:               # alternative: iterate over a list of keys
    del users[name]
assert users == active_only == {"asha": True, "meera": True}
print(users)
```
```output
```
!end

!qa
**Drill 3.** The order status check never matches even though the text looks right. Why?
```python Drill03.py
status = "".join(["pa", "id"])             # e.g. read from a database or a request
if status is "paid":
    print("shipping")
else:
    print("not shipped")
print(status == "paid")
```
=>
```output
```
`is` compares identity, and the string built at run time is a different object from the literal, so the condition is false even though the text is equal. (Python also warns "is with a literal" at compile time.) Use `==` for values; keep `is` for `None` and singletons.
!end

!qa
**Drill 4.** A checkout total of ten 10-paise items should be exactly 100 paise. What goes wrong with floats and how do you fix it?
```python Drill04.py
total = 0.0
for _ in range(10):
    total += 0.1                            # ten items of 0.10 rupees
print(total, total == 1.0)
```
=>
```output
```
Binary floating point cannot represent 0.1 exactly, so the sum is `0.9999999999999999`. Use integers of the smallest unit or `Decimal` built from strings:
```python Drill04Fixed.py
from decimal import Decimal

paise = sum(10 for _ in range(10))
rupees = sum(Decimal("0.10") for _ in range(10))
assert paise == 100 and rupees == Decimal("1.00")
print(paise, rupees)
```
```output
```
!end

!qa
**Drill 5.** This async code "works" but never calls the function. What is missing?
```python Drill05.py
import asyncio

async def fetch_price():
    await asyncio.sleep(0)
    return 42

async def main():
    price = fetch_price()                    # BUG
    print(type(price).__name__)
    price.close()                            # (only to silence the "never awaited" warning in this demo)
    price = await fetch_price()
    print(price)

asyncio.run(main())
```
=>
```output
```
Calling a coroutine function only creates a coroutine object; nothing runs until it is awaited (or scheduled as a task). Python warns "coroutine ... was never awaited". Always `await` it, or wrap it with `asyncio.create_task`.
!end

!qa
**Drill 6.** `load_price` silently returns 0 for every item. What hides the real bug?
```python Drill06.py
PRICES = {"pen": 12, "ink": 30}

def load_price(item):
    try:
        return PRICES[itme]                  # typo
    except Exception:
        return 0

print(load_price("pen"), load_price("ink"))
```
=>
```output
```
`except Exception` catches the `NameError` caused by the typo and turns it into a plausible-looking `0`. Catch only the error you expect, and let programming errors surface:
```python Drill06Fixed.py
PRICES = {"pen": 12, "ink": 30}

def load_price(item):
    try:
        return PRICES[item]
    except KeyError:
        return 0                             # a documented, deliberate default for unknown items

assert load_price("pen") == 12 and load_price("nothing") == 0
print(load_price("pen"), load_price("ink"), load_price("nothing"))
```
```output
```
!end

!qa
**Drill 7.** Comparing a database timestamp with "now" fails. Why?
```python Drill07.py !fail
from datetime import datetime, timezone

stored = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)      # an aware (UTC) value from the database
now = datetime(2026, 11, 4, 12, 0)                              # a naive value, e.g. from datetime.now() or utcnow()
print(stored < now)
```
=>
```output
```
An aware datetime (it has a time zone) cannot be compared with a naive one. Keep every timestamp aware and in UTC, and create "now" with `datetime.now(timezone.utc)`:
```python Drill07Fixed.py
from datetime import datetime, timedelta, timezone

stored = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)
now = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
assert stored < now and now - stored == timedelta(hours=2)
print(stored < now, now - stored)
```
```output
```
!end

!qa
**Drill 8.** The report mutates the caller's data. Spot the side effect.
```python Drill08.py
def top_scores(scores, n=2):
    scores.sort(reverse=True)               # sorts the caller's list in place
    return scores[:n]

marks = [70, 95, 82, 60]
print(top_scores(marks), marks)
```
=>
```output
```
`list.sort()` mutates its argument, so the caller's list is reordered as a hidden side effect. Use `sorted(scores, reverse=True)` (a new list) or `heapq.nlargest(n, scores)`:
```python Drill08Fixed.py
import heapq

def top_scores(scores, n=2):
    return heapq.nlargest(n, scores)

marks = [70, 95, 82, 60]
assert top_scores(marks) == [95, 82] and marks == [70, 95, 82, 60]
print(top_scores(marks), marks)
```
```output
```
!end
