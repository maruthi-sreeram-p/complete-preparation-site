@part py-dsa-2 | DSA Patterns in Python · Part 2: Arrays and Strings Patterns | dsa
## Prefix Sum and Difference Array

**Idea.** Precompute running totals once, then answer any "sum of a range" in O(1): `sum(nums[i..j]) = prefix[j+1] - prefix[i]`. Combined with a hash map of earlier prefix values it counts subarrays with a given sum in one pass. The **difference array** is the inverse: it applies many range updates in O(1) each and rebuilds the array once at the end.

**Signals.** "Sum of a range", "number of subarrays whose sum is k", "apply +x to indexes i..j many times".

```python Prefix.py
class RangeSum:
    """Immutable array, many range-sum queries: O(n) to build, O(1) per query."""
    def __init__(self, nums):
        self.prefix = [0]
        for n in nums:
            self.prefix.append(self.prefix[-1] + n)

    def query(self, left, right):                  # inclusive indexes
        return self.prefix[right + 1] - self.prefix[left]


def subarray_sum(nums, k):
    """Number of contiguous subarrays with sum k. prefix[j] - prefix[i] == k  <=>  prefix[i] == prefix[j] - k."""
    count, running, seen = 0, 0, {0: 1}                # the empty prefix has sum 0
    for n in nums:
        running += n
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return count


def longest_balanced(nums):
    """Longest subarray with equally many 0s and 1s: treat 0 as -1 and look for a repeated prefix sum."""
    first, running, best = {0: -1}, 0, 0
    for i, n in enumerate(nums):
        running += 1 if n else -1
        if running in first:
            best = max(best, i - first[running])
        else:
            first[running] = i
    return best


def flight_bookings(n, bookings):
    """Difference array: each booking is two O(1) updates, then one pass of running sums."""
    diff = [0] * (n + 2)
    for first, last, seats in bookings:
        diff[first] += seats
        diff[last + 1] -= seats
    out, running = [], 0
    for i in range(1, n + 1):
        running += diff[i]
        out.append(running)
    return out


q = RangeSum([-2, 0, 3, -5, 2, -1])
assert (q.query(0, 2), q.query(2, 5), q.query(0, 5)) == (1, -1, -3)
assert subarray_sum([1, 1, 1], 2) == 2 and subarray_sum([1, 2, 3], 3) == 2 and subarray_sum([1, -1, 0], 0) == 3
assert longest_balanced([0, 1]) == 2 and longest_balanced([0, 1, 0]) == 2 and longest_balanced([1, 1, 1]) == 0
assert flight_bookings(5, [[1, 2, 10], [2, 3, 20], [2, 5, 25]]) == [10, 55, 45, 25, 25]
print("prefix sums ok")
```

```output
```

The `seen = {0: 1}` seed is the classic detail: it counts subarrays that start at index 0. Prefix sums with a hash map work with **negative numbers**, unlike a sliding window.

??  Why can't a sliding window solve "subarrays with sum k" when numbers can be negative?
=> A window relies on monotonic behaviour (growing it increases the sum, shrinking decreases it). Negative numbers break that, so you cannot decide which end to move. Prefix sums with a hash map make no such assumption.
??  When do you use a difference array?
=> When there are many range updates ("add x to every element from i to j") and the array is read only afterwards: each update is O(1) and one final pass reconstructs everything in O(n), instead of O(n) per update.

## Two Pointers

**Idea.** Two indexes move through the data, usually from both ends of a sorted array or at different speeds, so one pass replaces a nested loop: O(n²) becomes O(n) (after an O(n log n) sort if needed).

**Signals.** Sorted array and a pair/triple with a target; in-place removal or partitioning; palindromes; "container" problems.

```python TwoPointers.py
def two_sum_sorted(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo, hi]
        if s < target:
            lo += 1                                    # need a larger sum
        else:
            hi -= 1                                    # need a smaller sum
    return []


def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i and nums[i] == nums[i - 1]:
            continue                                   # skip duplicate first elements
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                result.append([nums[i], nums[lo], nums[hi]])
                lo, hi = lo + 1, hi - 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1                            # skip duplicate second elements
    return result


def max_area(heights):
    lo, hi, best = 0, len(heights) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(heights[lo], heights[hi]))
        if heights[lo] < heights[hi]:                  # the shorter wall limits the area: move it
            lo += 1
        else:
            hi -= 1
    return best


def remove_duplicates(nums):                           # sorted, in place: returns the new length
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write


def trap(height):                                      # trapping rain water in O(1) space
    lo, hi, left_max, right_max, water = 0, len(height) - 1, 0, 0, 0
    while lo < hi:
        if height[lo] < height[hi]:
            left_max = max(left_max, height[lo])
            water += left_max - height[lo]
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            water += right_max - height[hi]
            hi -= 1
    return water


assert two_sum_sorted([2, 7, 11, 15], 9) == [0, 1] and two_sum_sorted([1, 2], 7) == []
assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]] and three_sum([0, 0, 0, 0]) == [[0, 0, 0]] and three_sum([1, 2]) == []
assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49 and max_area([1, 1]) == 1
data = [0, 0, 1, 1, 1, 2, 2, 3]
assert remove_duplicates(data) == 4 and data[:4] == [0, 1, 2, 3]
assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6 and trap([4, 2, 0, 3, 2, 5]) == 9
print("two pointers ok")
```

```output
```

Why moving the shorter wall is safe in `max_area`: the area is limited by the shorter wall, so any container that keeps it and shrinks the width is strictly worse; discarding it loses nothing. Proving that the pointer move is safe is what interviewers want to hear.

??  Why does the two-pointer approach to two-sum need a sorted array?
=> Sortedness tells you which pointer to move: if the sum is too small only moving the left pointer can increase it; if too big only moving the right can decrease it. Without order, that decision has no justification.
??  How do you handle duplicates in 3Sum?
=> Sort, skip equal values for the first element (`nums[i] == nums[i-1]`), and after recording a triple advance the left pointer past equal values. Otherwise the same triple is reported many times.

## Sliding Window: Fixed Size

**Idea.** Keep a window of exactly k elements and update its aggregate as it slides: add the entering element and remove the leaving one, O(1) per step, O(n) overall instead of O(nk).

```python WindowFixed.py
from collections import Counter


def max_sum_k(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]                # slide: add the new element, drop the old one
        best = max(best, window)
    return best


def find_anagrams(s, p):
    """Start indexes of anagrams of p inside s: a fixed window of len(p) with letter counts."""
    need, window, out = Counter(p), Counter(), []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            left = s[i - len(p)]
            window[left] -= 1
            if window[left] == 0:
                del window[left]                       # keep the counters comparable
        if window == need:
            out.append(i - len(p) + 1)
    return out


def check_inclusion(s1, s2):
    return bool(find_anagrams(s2, s1))


def max_vowels(s, k):
    vowels, count = set("aeiou"), 0
    best = 0
    for i, ch in enumerate(s):
        count += ch in vowels
        if i >= k:
            count -= s[i - k] in vowels
        best = max(best, count)
    return best


assert max_sum_k([2, 1, 5, 1, 3, 2], 3) == 9 and max_sum_k([4], 1) == 4
assert find_anagrams("cbaebabacd", "abc") == [0, 6] and find_anagrams("abab", "ab") == [0, 1, 2]
assert check_inclusion("ab", "eidbaooo") and not check_inclusion("ab", "eidboaoo")
assert max_vowels("abciiidef", 3) == 3 and max_vowels("leetcode", 3) == 2
print("fixed windows ok")
```

```output
```

??  What is the difference between a fixed and a variable sliding window?
=> A fixed window has a given length k, so it moves one element in and one out per step. A variable window changes size to satisfy a condition (the longest or shortest window that is valid), expanding the right end and shrinking the left end as needed.

## Sliding Window: Variable Size

**Idea.** Expand `right` one element at a time; while the window violates the condition, shrink from `left`. Every element enters and leaves at most once, so the work is O(n) even though there is a loop inside a loop.

**Signals.** "Longest / shortest substring or subarray such that ..." with a condition that is maintained incrementally and that becomes **false when the window grows** (or true when it shrinks).

```python WindowVariable.py
from collections import Counter, defaultdict


def min_subarray_len(target, nums):                    # positive numbers: shortest window with sum >= target
    left, total, best = 0, 0, float("inf")
    for right, n in enumerate(nums):
        total += n
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best


def longest_k_distinct(s, k):
    counts, left, best = defaultdict(int), 0, 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        while len(counts) > k:                         # too many distinct characters: shrink
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1
        best = max(best, right - left + 1)
    return best


def character_replacement(s, k):
    """Longest substring that becomes one repeated letter with at most k replacements."""
    counts, left, best, top = Counter(), 0, 0, 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        top = max(top, counts[ch])                     # the most frequent letter seen in any window so far
        while (right - left + 1) - top > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def min_window(s, t):
    need, missing, left = Counter(t), len(t), 0
    best = (float("inf"), 0, 0)
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:                            # the window contains every needed character
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]:best[2]]


assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2 and min_subarray_len(100, [1, 2]) == 0
assert longest_k_distinct("eceba", 2) == 3 and longest_k_distinct("aa", 1) == 2 and longest_k_distinct("", 3) == 0
assert character_replacement("AABABBA", 1) == 4 and character_replacement("ABAB", 2) == 4
assert min_window("ADOBECODEBANC", "ABC") == "BANC" and min_window("a", "aa") == "" and min_window("a", "a") == "a"
print("variable windows ok")
```

```output
```

!interview Template for a variable window :: `left = 0; for right in range(n): add s[right]; while window is invalid: remove s[left]; left += 1; update the answer`. For "longest" you update after the shrink loop (the window is valid); for "shortest" you update inside the loop while it is valid. Say that distinction aloud: it shows you understand the pattern rather than a memorised solution.

??  Why is a sliding window O(n) even though it has a `while` inside a `for`?
=> `left` and `right` each move forward at most n times in total and never go back, so the inner loop's total iterations across the whole outer loop are at most n. The cost is 2n, not n².
??  When does the sliding window technique fail?
=> When the condition is not monotonic with window size, for example sums with negative numbers (growing the window can decrease the sum). Use prefix sums with a hash map, or DP, instead.

## Hash Map and Frequency Counting

**Idea.** Trade O(n) memory for O(1) lookups: store what you have seen, counts, first positions or complements, and the brute-force inner loop disappears.

```python HashMaps.py
from collections import Counter


def longest_consecutive(nums):
    """O(n) by only starting a count at the beginning of a run (x - 1 is absent)."""
    values, best = set(nums), 0
    for x in values:
        if x - 1 not in values:
            end = x
            while end + 1 in values:
                end += 1
            best = max(best, end - x + 1)
    return best


def first_unique_char(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1


def four_sum_count(a, b, c, d):
    """Pairs (A+B) in a map, then look up -(C+D): O(n^2) instead of O(n^4)."""
    pair_sums = Counter(x + y for x in a for y in b)
    return sum(pair_sums[-(x + y)] for x in c for y in d)


def is_isomorphic(s, t):
    forward, backward = {}, {}
    for a, b in zip(s, t):
        if forward.setdefault(a, b) != b or backward.setdefault(b, a) != a:
            return False
    return True


def contains_nearby_duplicate(nums, k):
    last = {}
    for i, n in enumerate(nums):
        if n in last and i - last[n] <= k:
            return True
        last[n] = i
    return False


assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4 and longest_consecutive([]) == 0 and longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert first_unique_char("leetcode") == 0 and first_unique_char("loveleetcode") == 2 and first_unique_char("aabb") == -1
assert four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2]) == 2
assert is_isomorphic("egg", "add") and not is_isomorphic("foo", "bar") and not is_isomorphic("ab", "aa")
assert contains_nearby_duplicate([1, 2, 3, 1], 3) and not contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)
print("hash maps ok")
```

```output
```

| Question | Store in the map |
| --- | --- |
| "Have I seen the complement?" (two-sum) | value to index |
| "How many times?" | element to count (`Counter`) |
| "Where did I first see this?" | element or prefix sum to first index |
| "Are these two things the same shape?" | a canonical key: sorted letters, tuple of counts, normalised tuple |
| "Is this in the set?" | a `set`, for O(1) membership |

??  Why is `longest_consecutive` O(n) and not O(n²) despite the inner `while`?
=> The inner loop runs only for the first number of each run (those with no predecessor in the set), and each number belongs to exactly one run, so every element is stepped over once in total.

## Binary Search on Sorted Data

**Idea.** Halve the search space each step by comparing the middle element: O(log n). The core skill is maintaining a **loop invariant** and choosing the right boundary updates.

```python BinarySearch.py
def search_rotated(nums, target):
    """Sorted array rotated at an unknown pivot: one half is always sorted."""
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                      # the left half is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                          # the right half is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def find_min_rotated(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1                               # the minimum is to the right of mid
        else:
            hi = mid                                   # mid could be the minimum
    return nums[lo]


def find_peak(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1                               # climb to the right
        else:
            hi = mid
    return lo


def search_matrix(matrix, target):                     # rows and columns sorted: treat it as one sorted list
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        value = matrix[mid // cols][mid % cols]
        if value == target:
            return True
        if value < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4 and search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1 and search_rotated([1], 0) == -1
assert find_min_rotated([3, 4, 5, 1, 2]) == 1 and find_min_rotated([11, 13, 15, 17]) == 11 and find_min_rotated([2, 1]) == 1
assert find_peak([1, 2, 3, 1]) == 2 and find_peak([1]) == 0 and find_peak([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
assert search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3) and not search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13)
print("binary search ok")
```

```output
```

!cheat Two loop shapes ::
- **Find an exact value**: `while lo <= hi`, `mid = (lo + hi) // 2`, move with `mid + 1` and `mid - 1`; return inside the loop, `-1` after it.
- **Find a boundary** (first true, minimum): `while lo < hi`, `hi = mid` when `mid` could be the answer, `lo = mid + 1` otherwise; the answer is `lo` after the loop.
- Python integers never overflow, so `(lo + hi) // 2` is safe (in Java use `lo + (hi - lo) / 2`).
!end

??  How do you find the minimum in a rotated sorted array in O(log n)?
=> Compare `nums[mid]` with `nums[hi]`: if mid is larger, the minimum lies right of mid (`lo = mid + 1`); otherwise it is at mid or to its left (`hi = mid`). Loop while `lo < hi`.
??  What is the invariant of a binary search for an exact value?
=> If the target is present, it lies in `nums[lo..hi]`. Each step discards half the range that cannot contain it, so the range shrinks until it is found or empty.

## Binary Search on the Answer

**Idea.** When you are asked for the **smallest (or largest) value that makes a condition true**, and the condition is **monotonic** (once true, it stays true as the value increases), binary search the value itself. You need a `feasible(x)` function; the search range is the possible answers.

**Signals.** "Minimum capacity / speed / time such that ...", "maximise the minimum", "split into k parts to minimise the largest sum".

```python BinaryAnswer.py
import math


def first_true(lo, hi, feasible):
    """Smallest x in [lo, hi] with feasible(x) True, assuming feasible is monotonic (False...False True...True)."""
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def min_eating_speed(piles, hours):                    # Koko eating bananas
    return first_true(1, max(piles), lambda speed: sum(math.ceil(p / speed) for p in piles) <= hours)


def ship_within_days(weights, days):
    def can_ship(capacity):
        needed, load = 1, 0
        for w in weights:
            if load + w > capacity:
                needed, load = needed + 1, 0
            load += w
        return needed <= days
    return first_true(max(weights), sum(weights), can_ship)


def split_array_largest_sum(nums, k):
    def can_split(limit):
        parts, current = 1, 0
        for n in nums:
            if current + n > limit:
                parts, current = parts + 1, 0
            current += n
        return parts <= k
    return first_true(max(nums), sum(nums), can_split)


def integer_sqrt(x):
    return first_true(0, x, lambda r: (r + 1) * (r + 1) > x)       # the first r whose next square exceeds x


assert min_eating_speed([3, 6, 7, 11], 8) == 4 and min_eating_speed([30, 11, 23, 4, 20], 5) == 30
assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15 and ship_within_days([3, 2, 2, 4, 1, 4], 3) == 6
assert split_array_largest_sum([7, 2, 5, 10, 8], 2) == 18
assert [integer_sqrt(n) for n in (0, 1, 8, 16, 99)] == [0, 1, 2, 4, 9]
print("binary search on the answer ok")
```

```output
```

The recipe: (1) decide what the answer is a number of; (2) bound it (`lo` = smallest possible, `hi` = largest); (3) write `feasible(x)` as an O(n) greedy check; (4) run `first_true`. Total cost is O(n log range).

??  How do you know a problem can be solved by binary searching the answer?
=> The answer is a number in a known range and feasibility is monotonic: if value x works, every larger (or smaller) value works too. Then "find the minimum feasible x" is a boundary search, and checking feasibility is usually a simple greedy pass.

## Sorting-Based Problems and Intervals

**Idea.** Sorting (O(n log n)) often turns a hard-looking problem into a linear scan: after sorting by start time, only neighbouring intervals can overlap. For "how many resources are needed at once", a min-heap of end times does the bookkeeping.

```python Intervals.py
import heapq
from bisect import bisect_left


def insert_interval(intervals, new):
    result, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < new[0]:          # entirely before
        result.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= new[1]:         # overlapping: absorb into new
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]; i += 1
    result.append(new)
    return result + intervals[i:]                      # entirely after


def min_meeting_rooms(meetings):
    rooms = []                                         # min-heap of end times of rooms in use
    for start, end in sorted(meetings):
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)              # reuse the room that frees up first
        else:
            heapq.heappush(rooms, end)                 # need one more room
    return len(rooms)


def erase_overlap_intervals(intervals):
    """Minimum removals so none overlap: greedy, keep the interval that ends earliest."""
    removed, last_end = 0, float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):
        if start >= last_end:
            last_end = end
        else:
            removed += 1
    return removed


def can_attend_all(meetings):
    ordered = sorted(meetings)
    return all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:]))


def kth_largest(nums, k):
    return sorted(nums, reverse=True)[k - 1]           # O(n log n); a heap or quickselect improves it (Part 5)


assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
assert insert_interval([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [[1, 2], [3, 10], [12, 16]]
assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2 and min_meeting_rooms([[7, 10], [2, 4]]) == 1
assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1 and erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]) == 2
assert can_attend_all([[7, 10], [2, 4]]) and not can_attend_all([[0, 30], [5, 10]])
assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
print("intervals ok")
```

```output
```

??  Why do you sort intervals by start time to merge, but by end time to maximise the number kept?
=> To merge, you scan left to right and only the previous merged interval can overlap the next start, so order by start. To keep as many non-overlapping intervals as possible, the interval that **ends earliest** leaves the most room for the rest (the classic exchange argument), so order by end.
??  How does a heap solve "minimum meeting rooms"?
=> Process meetings by start time and keep a min-heap of the end times of rooms in use. If the earliest-ending room is free by the new start, reuse it; otherwise add a room. The heap size at the end is the answer: O(n log n).

## Kadane, Greedy Scans and In-Place Tricks

**Idea.** One pass with a couple of variables carrying the best answer so far; or rearranging the array in place with swaps, reversals and pointers, in O(1) extra space.

```python Scans.py
def max_profit(prices):                                # buy once, sell once
    low, best = float("inf"), 0
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return best


def can_jump(nums):                                    # greedy: the furthest index reachable so far
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + jump)
    return True


def jump_game_ii(nums):                                # minimum jumps: BFS by "layers" of reachable indexes
    jumps, current_end, farthest = 0, 0, 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps, current_end = jumps + 1, farthest
    return jumps


def sort_colors(nums):                                 # Dutch national flag: three regions, one pass
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low, mid = low + 1, mid + 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1                                  # do not advance mid: the swapped-in value is unchecked


def rotate(nums, k):                                   # rotate right by k in place: reverse all, then the two parts
    n = len(nums)
    k %= n

    def reverse(i, j):
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i, j = i + 1, j - 1

    reverse(0, n - 1); reverse(0, k - 1); reverse(k, n - 1)


def majority_element(nums):                            # Boyer-Moore voting: O(1) space
    candidate, count = None, 0
    for n in nums:
        if count == 0:
            candidate = n
        count += 1 if n == candidate else -1
    return candidate


assert max_profit([7, 1, 5, 3, 6, 4]) == 5 and max_profit([7, 6, 4, 3, 1]) == 0
assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4])
assert jump_game_ii([2, 3, 1, 1, 4]) == 2 and jump_game_ii([2, 3, 0, 1, 4]) == 2 and jump_game_ii([0]) == 0
colors = [2, 0, 2, 1, 1, 0]
sort_colors(colors)
assert colors == [0, 0, 1, 1, 2, 2]
rotated = [1, 2, 3, 4, 5, 6, 7]
rotate(rotated, 3)
assert rotated == [5, 6, 7, 1, 2, 3, 4]
assert majority_element([2, 2, 1, 1, 1, 2, 2]) == 2
print("greedy scans ok")
```

```output
```

??  Why does Kadane's algorithm work?
=> The best subarray ending at position i is either the element alone or the best ending at i-1 plus the element; if the running sum goes negative it can only hurt, so restart. Tracking the best seen over all i gives the answer in O(n).
??  In the Dutch national flag partition, why isn't `mid` advanced after swapping with `high`?
=> The value that arrives from the high end has not been examined yet and could be 0 or 2, so it must be processed on the next iteration. After swapping with `low`, the value that arrives is known to be 1, so `mid` can advance.

## Matrix and String Patterns

```python MatrixStrings.py
def spiral_order(matrix):
    result = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        result += matrix[top][left:right + 1]
        result += [matrix[r][right] for r in range(top + 1, bottom + 1)]
        if top < bottom:
            result += matrix[bottom][left:right][::-1]
        if left < right:
            result += [matrix[r][left] for r in range(bottom - 1, top, -1)]
        top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
    return result


def rotate_image(matrix):                              # 90 degrees clockwise in place: transpose, then reverse each row
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()


def set_zeroes(matrix):                                # O(m + n) marker sets (O(1) space versions use the first row/column)
    zero_rows = {i for i, row in enumerate(matrix) if 0 in row}
    zero_cols = {j for row in matrix for j, v in enumerate(row) if v == 0}
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if i in zero_rows or j in zero_cols:
                matrix[i][j] = 0


def longest_palindrome(s):                             # expand around each centre: O(n^2) time, O(1) space
    best = ""
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):      # odd and even lengths
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo, hi = lo - 1, hi + 1
            if hi - lo - 1 > len(best):
                best = s[lo + 1:hi]
    return best


def kmp_search(text, pattern):                         # O(n + m): never re-reads text characters
    if not pattern:
        return 0
    lps, length = [0] * len(pattern), 0                # longest proper prefix that is also a suffix
    for i in range(1, len(pattern)):
        while length and pattern[i] != pattern[length]:
            length = lps[length - 1]
        if pattern[i] == pattern[length]:
            length += 1
        lps[i] = length
    j = 0
    for i, ch in enumerate(text):
        while j and ch != pattern[j]:
            j = lps[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            return i - j + 1
    return -1


def compress(chars):
    out, i = [], 0
    while i < len(chars):
        j = i
        while j < len(chars) and chars[j] == chars[i]:
            j += 1
        out.append(chars[i] + (str(j - i) if j - i > 1 else ""))
        i = j
    return "".join(out)


grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
assert spiral_order(grid) == [1, 2, 3, 6, 9, 8, 7, 4, 5] and spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
rotate_image(grid)
assert grid == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
zeros = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
set_zeroes(zeros)
assert zeros == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
assert longest_palindrome("babad") in ("bab", "aba") and longest_palindrome("cbbd") == "bb" and longest_palindrome("a") == "a"
assert kmp_search("hello world", "o w") == 4 and kmp_search("aaaaab", "aab") == 3 and kmp_search("abc", "d") == -1 and kmp_search("abc", "") == 0
assert compress("aabcccccaaa") == "a2bc5a3"
print("matrix and strings ok")
```

```output
```

??  Why does rotating a matrix 90 degrees clockwise equal "transpose, then reverse each row"?
=> A transpose swaps rows and columns (element (i, j) goes to (j, i)); reversing each row then maps (j, i) to (j, n-1-i), which is exactly the clockwise rotation of (i, j). It uses O(1) extra space.
??  What problem does KMP solve and what is its key idea?
=> Substring search in O(n + m) instead of O(nm). It precomputes for each prefix of the pattern the length of the longest proper prefix that is also a suffix (the failure function), so after a mismatch the pattern pointer jumps back to that length instead of restarting, and the text pointer never moves backwards.
