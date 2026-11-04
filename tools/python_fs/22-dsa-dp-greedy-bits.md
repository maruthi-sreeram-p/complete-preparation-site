@part py-dsa-6 | DSA Patterns in Python · Part 6: Dynamic Programming, Greedy and Bits | dsa
## Dynamic Programming: The Method

**Dynamic programming (DP)** solves a problem by combining answers to **overlapping subproblems**, computing each once. If a plain recursion recomputes the same inputs many times (Fibonacci is the textbook case), DP removes the repetition and turns exponential time into polynomial time.

**Signals.** "Count the number of ways", "minimum or maximum cost", "can we reach / is it possible", "longest ...", and a brute force that makes **choices at each step** with repeated states.

The five steps (say them in the interview):

1. **State**: what do you need to know to continue? (`dp[i]` = the best answer using the first i items)
2. **Transition**: how does the state follow from smaller states? (the recurrence)
3. **Base cases**: the smallest states, known directly.
4. **Order**: compute smaller states before larger ones (or let memoisation figure it out).
5. **Answer**: which state holds it, and can you reduce the memory by keeping only the last few states?

```python DpMethod.py
from functools import cache


# Climbing stairs: ways to reach step n taking 1 or 2 steps at a time.  ways(n) = ways(n-1) + ways(n-2)

def ways_recursive(n):                                  # brute force: O(2^n), recomputes the same n again and again
    return 1 if n <= 1 else ways_recursive(n - 1) + ways_recursive(n - 2)


def ways_top_down(n):                                   # memoised recursion: O(n) time, O(n) space
    @cache
    def go(i):
        return 1 if i <= 1 else go(i - 1) + go(i - 2)
    return go(n)


def ways_bottom_up(n):                                  # tabulation: fill the table from the base case upwards
    dp = [1] * (n + 1)
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def ways_constant_space(n):                             # only the last two states matter: O(1) space
    prev, cur = 1, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


def house_robber(nums):                                 # best loot, never two adjacent houses: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    skip, take = 0, 0
    for n in nums:
        skip, take = max(skip, take), skip + n          # simultaneous update: (best without i, best with i)
    return max(skip, take)


def min_cost_climbing(cost):
    one, two = 0, 0                                     # cheapest cost to stand on the previous two steps
    for i in range(2, len(cost) + 1):
        one, two = two, min(two + cost[i - 1], one + cost[i - 2])
    return two


def num_decodings(s):                                   # 'A'=1 ... 'Z'=26: how many ways to read the digits
    if not s or s[0] == "0":
        return 0
    prev2, prev1 = 1, 1                                 # ways for the empty prefix and for the first character
    for i in range(2, len(s) + 1):
        current = prev1 if s[i - 1] != "0" else 0       # a single digit 1-9 extends every earlier decoding
        if 10 <= int(s[i - 2:i]) <= 26:
            current += prev2                            # a valid two-digit number extends the decodings two back
        prev2, prev1 = prev1, current
    return prev1


assert {ways_recursive(10), ways_top_down(10), ways_bottom_up(10), ways_constant_space(10)} == {89}
assert ways_constant_space(5) == 8 and ways_top_down(50) == 20365011074
assert house_robber([2, 7, 9, 3, 1]) == 12 and house_robber([1, 2, 3, 1]) == 4 and house_robber([]) == 0
assert min_cost_climbing([10, 15, 20]) == 15 and min_cost_climbing([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
assert [num_decodings(s) for s in ("12", "226", "06", "10", "27")] == [2, 3, 0, 1, 1]
print("dp method ok")
```

```output
```

Memoisation (top-down) is easiest to write: copy the recurrence and add `@cache`. Tabulation (bottom-up) avoids recursion depth limits and allows **space optimisation**. In interviews: write the recurrence first, then the version you are most confident in, then mention the optimisation.

!interview "Is this greedy or DP?" :: Ask whether a locally best choice can be proved globally safe. If you can find a counter-example (coins `[1, 3, 4]`, amount 6: greedy takes 4+1+1, optimal is 3+3), it is DP. If sorting plus a simple rule always works (interval scheduling by earliest end time), it is greedy.

??  What two properties must a problem have for dynamic programming to apply?
=> **Overlapping subproblems** (the same smaller problems recur, so caching helps) and **optimal substructure** (an optimal solution is built from optimal solutions to subproblems).
??  Top-down or bottom-up: how do you choose?
=> Top-down (memoisation) is quicker to write and only computes needed states; bottom-up avoids recursion depth limits and allows rolling arrays to cut space. In Python the recursion limit and call overhead often favour bottom-up for large n.
??  What does "reduce the space" mean for DP tables?
=> If `dp[i]` depends only on the last one or two rows or values, keep just those (two variables, or two rows) instead of the whole table, taking O(n) or O(n·m) space down to O(1) or O(m).

## DP on Grids and Paths

**State**: the cell `(r, c)`. **Transition**: the answer for a cell comes from the cells you can arrive from (above and left).

```python GridDp.py
def unique_paths(m, n):
    row = [1] * n                                         # the first row has one path to each cell
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]                          # paths from above (row[c]) + paths from the left (row[c - 1])
    return row[-1]


def unique_paths_obstacles(grid):
    row = [0] * len(grid[0])
    row[0] = 1
    for line in grid:
        for c, cell in enumerate(line):
            if cell == 1:
                row[c] = 0                                # an obstacle blocks every path through it
            elif c:
                row[c] += row[c - 1]
    return row[-1]


def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [float("inf")] * cols
    dp[0] = 0
    for r in range(rows):
        dp[0] += grid[r][0]                               # the first column can only be reached from above
        for c in range(1, cols):
            dp[c] = grid[r][c] + min(dp[c], dp[c - 1])    # from above (old dp[c]) or from the left (new dp[c - 1])
    return dp[-1]


def minimum_total_triangle(triangle):
    dp = triangle[-1][:]                                  # start from the bottom row and fold upwards
    for row in reversed(triangle[:-1]):
        dp = [value + min(dp[i], dp[i + 1]) for i, value in enumerate(row)]
    return dp[0]


def maximal_square(matrix):
    best, prev = 0, [0] * (len(matrix[0]) + 1)
    for row in matrix:
        cur = [0]
        for c, cell in enumerate(row, start=1):
            # the side of the largest square whose bottom-right corner is here: 1 + min(up, left, up-left)
            cur.append(1 + min(prev[c], cur[c - 1], prev[c - 1]) if cell == "1" else 0)
            best = max(best, cur[-1])
        prev = cur
    return best * best


assert unique_paths(3, 7) == 28 and unique_paths(3, 2) == 3 and unique_paths(1, 1) == 1
assert unique_paths_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2 and unique_paths_obstacles([[0, 1], [0, 0]]) == 1
assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7 and min_path_sum([[1, 2, 3], [4, 5, 6]]) == 12
assert minimum_total_triangle([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]) == 11 and minimum_total_triangle([[-10]]) == -10
assert maximal_square([list("10100"), list("10111"), list("11111"), list("10010")]) == 4 and maximal_square([list("0")]) == 0
print("grid dp ok")
```

```output
```

??  Why can the grid DP keep only one row?
=> Each cell depends on the cell above (the previous row, still in the same array position) and the cell to the left (already updated in this row), so a single row updated left to right holds everything needed: O(n) space instead of O(m·n).
??  How does the "maximal square" recurrence work?
=> `dp[r][c]` is the side of the largest all-ones square with its bottom-right corner at `(r, c)`. If the cell is 1, it is 1 plus the minimum of the squares ending above, to the left and diagonally above-left, because all three must extend for a bigger square to fit.

## Knapsack Patterns

**State**: `dp[i][w]` = best value using the first i items with capacity w. Each item is either **taken or not** (0/1 knapsack), and the table collapses to one dimension if you iterate capacities in the right direction.

| Variant | Loop direction over capacity | Typical problem |
| --- | --- | --- |
| **0/1** (each item once) | **backwards** (high to low) so an item is not reused | knapsack, subset sum, partition, target sum |
| **Unbounded** (reuse allowed) | **forwards** (low to high) so an item can be reused | coin change (min coins, number of ways) |
| **Counting combinations** | items in the outer loop | coin change II |
| **Counting permutations** | amounts in the outer loop | combination sum IV |

```python Knapsack.py
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for w in range(capacity, weight - 1, -1):         # backwards: each item is used at most once
            dp[w] = max(dp[w], dp[w - weight] + value)
    return dp[capacity]


def can_partition(nums):                                  # equal-sum split = subset sum to total/2
    total = sum(nums)
    if total % 2:
        return False
    reachable = {0}
    for n in nums:
        reachable |= {r + n for r in reachable}           # every sum reachable before, with and without n
    return total // 2 in reachable


def coin_change(coins, amount):                           # minimum coins (unbounded)
    best = [0] + [float("inf")] * amount
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                best[a] = min(best[a], best[a - coin] + 1)
    return -1 if best[amount] == float("inf") else best[amount]


def change_ways(amount, coins):                           # number of COMBINATIONS (order does not matter)
    ways = [1] + [0] * amount
    for coin in coins:                                    # coins outer: each combination is counted once
        for a in range(coin, amount + 1):
            ways[a] += ways[a - coin]
    return ways[amount]


def combination_sum_iv(nums, target):                     # number of ORDERED sequences (permutations)
    ways = [1] + [0] * target
    for a in range(1, target + 1):                        # amounts outer: different orders count separately
        for n in nums:
            if n <= a:
                ways[a] += ways[a - n]
    return ways[target]


def target_sum(nums, target):                             # assign + or -: count subsets with sum (total + target) / 2
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    goal, ways = (total + target) // 2, None
    ways = [1] + [0] * goal
    for n in nums:
        for s in range(goal, n - 1, -1):
            ways[s] += ways[s - n]
    return ways[goal]


def ones_and_zeroes(strs, m, n):                          # a two-dimensional knapsack: capacity = (m zeros, n ones)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        zeros, ones = s.count("0"), s.count("1")
        for i in range(m, zeros - 1, -1):
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)
    return dp[m][n]


assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9 and knapsack([2], [3], 1) == 0
assert can_partition([1, 5, 11, 5]) and not can_partition([1, 2, 3, 5]) and not can_partition([1])
assert coin_change([1, 2, 5], 11) == 3 and coin_change([2], 3) == -1 and coin_change([1, 3, 4], 6) == 2
assert change_ways(5, [1, 2, 5]) == 4 and change_ways(3, [2]) == 0 and change_ways(0, [7]) == 1
assert combination_sum_iv([1, 2, 3], 4) == 7
assert target_sum([1, 1, 1, 1, 1], 3) == 5 and target_sum([1], 1) == 1 and target_sum([1, 2], 10) == 0
assert ones_and_zeroes(["10", "0001", "111001", "1", "0"], 5, 3) == 4
print("knapsack ok")
```

```output
```

??  Why does the 0/1 knapsack loop capacities backwards and the unbounded one forwards?
=> In a single-row table, `dp[w - weight]` must still hold the value from *before* this item was considered for 0/1 (so go backwards and the earlier cells are untouched); for unbounded you *want* it to include this item already (so go forwards and reuse is allowed).
??  Coin change: why does the loop order change the count of combinations versus permutations?
=> With coins in the outer loop, each coin is introduced once and combinations are built in a fixed coin order, so each multiset is counted once. With amounts outer and coins inner, every order of the same coins is a different path, so sequences are counted.

## DP on Strings and Sequences

**State** is usually a pair of prefix lengths `(i, j)` for two strings, or the prefix length plus one extra quantity for one sequence.

```python StringDp.py
from bisect import bisect_left


def edit_distance(a, b):
    prev = list(range(len(b) + 1))                        # turning "" into the first j characters of b costs j insertions
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(prev[j - 1] if ca == cb else 1 + min(prev[j - 1], prev[j], cur[j - 1]))   # replace, delete, insert
        prev = cur
    return prev[-1]


def length_of_lis(nums):
    """Longest strictly increasing subsequence in O(n log n): tails[k] = the smallest tail of an increasing subsequence of length k + 1."""
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def word_break(s, words):
    words, reachable = set(words), [True] + [False] * len(s)
    for end in range(1, len(s) + 1):
        reachable[end] = any(reachable[start] and s[start:end] in words for start in range(end))
    return reachable[-1]


def longest_palindromic_subsequence(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            dp[i][j] = dp[i + 1][j - 1] + 2 if s[i] == s[j] else max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1] if n else 0


def num_distinct(s, t):                                   # how many subsequences of s equal t
    dp = [1] + [0] * len(t)
    for ch in s:
        for j in range(len(t), 0, -1):                    # backwards: each character of s is used once
            if t[j - 1] == ch:
                dp[j] += dp[j - 1]
    return dp[-1]


def count_palindromic_substrings(s):
    count = 0
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                count += 1
                lo, hi = lo - 1, hi + 1
    return count


def max_product_subarray(nums):
    best = high = low = nums[0]                           # track both the largest and smallest product ending here
    for n in nums[1:]:
        candidates = (n, high * n, low * n)               # a negative number can turn the smallest into the largest
        high, low = max(candidates), min(candidates)
        best = max(best, high)
    return best


assert edit_distance("horse", "ros") == 3 and edit_distance("intention", "execution") == 5 and edit_distance("", "abc") == 3
assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and length_of_lis([0, 1, 0, 3, 2, 3]) == 4 and length_of_lis([7, 7, 7]) == 1
assert word_break("leetcode", ["leet", "code"]) and word_break("applepenapple", ["apple", "pen"]) and not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
assert longest_palindromic_subsequence("bbbab") == 4 and longest_palindromic_subsequence("cbbd") == 2 and longest_palindromic_subsequence("") == 0
assert num_distinct("rabbbit", "rabbit") == 3 and num_distinct("babgbag", "bag") == 5
assert count_palindromic_substrings("aaa") == 6 and count_palindromic_substrings("abc") == 3
assert max_product_subarray([2, 3, -2, 4]) == 6 and max_product_subarray([-2, 0, -1]) == 0 and max_product_subarray([-2, 3, -4]) == 24
print("string dp ok")
```

```output
```

??  Explain the edit distance recurrence.
=> `dp[i][j]` is the fewest operations to turn the first i characters of `a` into the first j of `b`. If the characters match it equals `dp[i-1][j-1]`; otherwise 1 plus the minimum of replacing (`dp[i-1][j-1]`), deleting from `a` (`dp[i-1][j]`) or inserting into `a` (`dp[i][j-1]`). The base cases are converting to or from the empty string.
??  How does the O(n log n) longest increasing subsequence work?
=> `tails[k]` holds the smallest possible last value of an increasing subsequence of length k + 1. For each number, binary search the first tail that is at least as large and replace it (or append if none): the list stays sorted and its length is the answer. (The list itself is not the subsequence.)

## DP on Intervals, Trees and States

Three more shapes appear often at harder interviews.

```python MoreDp.py
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def build_tree(vals):
    if not vals or vals[0] is None:
        return None
    root, queue, i = TreeNode(vals[0]), None, 1
    queue = deque([root])
    while queue and i < len(vals):
        node = queue.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i]); queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i]); queue.append(node.right)
        i += 1
    return root


# 1. Interval DP: dp[left][right] = best result for the open interval between two balloons left and right.
def max_coins(nums):                                      # burst balloons: choose which balloon to burst LAST in each interval
    nums = [1] + nums + [1]
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for left in range(n - length):
            right = left + length
            dp[left][right] = max(nums[left] * nums[i] * nums[right] + dp[left][i] + dp[i][right] for i in range(left + 1, right))
    return dp[0][n - 1]


# 2. Tree DP: every node returns a small tuple of states to its parent.
def rob_tree(root):
    def go(node):                                         # returns (best if this node is robbed, best if it is skipped)
        if not node:
            return 0, 0
        left_rob, left_skip = go(node.left)
        right_rob, right_skip = go(node.right)
        return node.val + left_skip + right_skip, max(left_rob, left_skip) + max(right_rob, right_skip)
    return max(go(root))


def num_trees(n):                                         # structurally unique BSTs: Catalan numbers
    dp = [1, 1] + [0] * (n - 1)
    for nodes in range(2, n + 1):
        dp[nodes] = sum(dp[left] * dp[nodes - 1 - left] for left in range(nodes))
    return dp[n]


# 3. State-machine DP: the state is "what position am I in" (holding, sold, resting ...).
def max_profit_cooldown(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)


def max_profit_k(k, prices):
    if k >= len(prices) // 2:                             # unlimited transactions: take every rise
        return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))
    buy, sell = [float("-inf")] * (k + 1), [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)
            sell[t] = max(sell[t], buy[t] + p)
    return sell[k]


# 4. Bitmask DP: the state is the set of items already used (n up to about 20).
def shortest_hamiltonian_path(dist):                      # visit every node once: dp[mask][last]
    n = len(dist)
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    for i in range(n):
        dp[1 << i][i] = 0
    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == INF:
                continue
            for nxt in range(n):
                if not mask & (1 << nxt):
                    new = mask | (1 << nxt)
                    dp[new][nxt] = min(dp[new][nxt], dp[mask][last] + dist[last][nxt])
    return min(dp[(1 << n) - 1])


assert max_coins([3, 1, 5, 8]) == 167 and max_coins([1, 5]) == 10
assert rob_tree(build_tree([3, 2, 3, None, 3, None, 1])) == 7 and rob_tree(build_tree([3, 4, 5, 1, 3, None, 1])) == 9
assert [num_trees(n) for n in (1, 2, 3, 4, 5)] == [1, 2, 5, 14, 42]
assert max_profit_cooldown([1, 2, 3, 0, 2]) == 3 and max_profit_cooldown([1]) == 0
assert max_profit_k(2, [3, 2, 6, 5, 0, 3]) == 7 and max_profit_k(2, [2, 4, 1]) == 2 and max_profit_k(100, [1, 2, 3, 4, 5]) == 4
assert shortest_hamiltonian_path([[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]) == 50          # 2 -> 0 -> 1 -> 3 costs 15 + 10 + 25
print("interval, tree and state dp ok")
```

```output
```

??  What is the trick in the "burst balloons" interval DP?
=> Think about the **last** balloon burst in an interval rather than the first: when it is the last one, its two neighbours are the interval's boundaries, so the subproblems on its left and right are independent. Then `dp[l][r] = max over k of nums[l]*nums[k]*nums[r] + dp[l][k] + dp[k][r]`.
??  What is bitmask DP and when does it apply?
=> The state is a subset of items encoded as an integer's bits (`mask`), so `dp[mask][last]` records the best value having used exactly those items. It applies when n is small (about 20): there are 2ⁿ subsets, which is the cost of travelling-salesperson and assignment style problems.

## Greedy

A **greedy** algorithm makes the locally best choice at each step and never revisits it. It is fast (usually a sort plus a scan) but **only correct when you can justify it**. The standard justification is an **exchange argument**: any optimal solution can be transformed, without getting worse, into one that makes the greedy choice first.

```python Greedy.py
import heapq
from collections import Counter


def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1                                          # not enough fuel in total: impossible from anywhere
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                                       # cannot get past i from the current start: no station up to i works
            start, tank = i + 1, 0
    return start


def assign_cookies(greed, cookies):
    greed.sort(); cookies.sort()
    child = 0
    for cookie in cookies:                                 # give each cookie to the least greedy child it can satisfy
        if child < len(greed) and cookie >= greed[child]:
            child += 1
    return child


def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}               # the last position of each letter
    sizes, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])                           # the current part must reach this letter's last occurrence
        if i == end:
            sizes.append(end - start + 1)
            start = i + 1
    return sizes


def candy(ratings):
    n = len(ratings)
    give = [1] * n
    for i in range(1, n):                                  # left to right: higher than the left neighbour gets more
        if ratings[i] > ratings[i - 1]:
            give[i] = give[i - 1] + 1
    for i in range(n - 2, -1, -1):                         # right to left: and more than the right neighbour
        if ratings[i] > ratings[i + 1]:
            give[i] = max(give[i], give[i + 1] + 1)
    return sum(give)


def min_arrows(balloons):                                  # one arrow bursts all balloons whose intervals share a point
    arrows, end = 0, float("-inf")
    for start, stop in sorted(balloons, key=lambda b: b[1]):
        if start > end:
            arrows, end = arrows + 1, stop
    return arrows


def huffman_cost(frequencies):                             # total cost of the optimal prefix code: always merge the two rarest
    heap = list(frequencies)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        merged = heapq.heappop(heap) + heapq.heappop(heap)
        total += merged
        heapq.heappush(heap, merged)
    return total


def fractional_knapsack(items, capacity):                  # items may be split, so best value-per-weight first is optimal
    total = 0.0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        take = min(weight, capacity)
        total += value * take / weight
        capacity -= take
        if capacity == 0:
            break
    return total


assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3 and can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
assert assign_cookies([1, 2, 3], [1, 1]) == 1 and assign_cookies([1, 2], [1, 2, 3]) == 2
assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
assert candy([1, 0, 2]) == 5 and candy([1, 2, 2]) == 4 and candy([5]) == 1
assert min_arrows([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2 and min_arrows([[1, 2], [3, 4], [5, 6]]) == 3
assert huffman_cost([5, 9, 12, 13, 16, 45]) == 224
assert fractional_knapsack([(60, 10), (100, 20), (120, 30)], 50) == 240.0
print("greedy ok")
```

```output
```

!cheat Greedy versus DP, quick test ::
- Can you state a rule ("always take the earliest-ending interval", "merge the two smallest") and prove by exchange that it never hurts? Greedy.
- Does the best choice now depend on future choices in a way you cannot decide locally (0/1 knapsack, coin change with odd coins)? DP.
- Fractional items or divisible resources usually mean greedy; indivisible items usually mean DP.
- Always try to break your greedy with a small counter-example before you code it.
!end

??  Why does the gas station greedy work?
=> If the total gas is at least the total cost, a solution exists. If the running tank drops below zero at index i, no station between the current start and i can be a valid start (each would have had even less fuel on arriving), so the next candidate is i + 1. One pass finds it.
??  Why is the fractional knapsack greedy but the 0/1 knapsack is not?
=> With fractions you can always fill capacity with the best value-per-weight material, so the exchange argument holds. With whole items, a high value-per-weight item can leave unusable capacity, so locally best choices can be globally suboptimal and you need DP.

## Bit Manipulation

Integers are bit patterns, and bitwise operators are single instructions. Use them for **flags and sets** (a bitmask is a tiny set), **parity tricks** (XOR cancels equal values), **powers of two**, and **speed**.

| Operation | Meaning | Example |
| --- | --- | --- |
| `a & b` | AND: bits set in both | test a bit: `n & (1 << k)` |
| `a \| b` | OR: bits set in either | set a bit: `n \| (1 << k)` |
| `a ^ b` | XOR: bits that differ | toggle a bit: `n ^ (1 << k)`; `x ^ x == 0` |
| `~a` | NOT (in Python `-a - 1`) | |
| `a << k`, `a >> k` | shifts: multiply or divide by 2ᵏ | `1 << k` is 2ᵏ |
| `n & (n - 1)` | clears the lowest set bit | power-of-two test, bit counting |
| `n & -n` | isolates the lowest set bit | Fenwick trees |

```python Bits.py
def single_number(nums):                                   # every other number appears twice: XOR cancels the pairs
    result = 0
    for n in nums:
        result ^= n
    return result


def single_numbers_two(nums):                              # two numbers appear once, the rest twice
    xor_all = 0
    for n in nums:
        xor_all ^= n                                       # = a ^ b, which is non-zero
    lowest = xor_all & -xor_all                            # a bit where a and b differ
    a = b = 0
    for n in nums:
        if n & lowest:
            a ^= n
        else:
            b ^= n
    return sorted((a, b))


def count_bits(n):                                         # Kernighan: each loop clears one set bit
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count


def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def missing_number(nums):                                  # 0..n with one missing: XOR of indexes and values
    result = len(nums)
    for i, n in enumerate(nums):
        result ^= i ^ n
    return result


def reverse_bits(n, width=32):
    result = 0
    for _ in range(width):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


def subsets_bitmask(items):
    return [[items[i] for i in range(len(items)) if mask >> i & 1] for mask in range(1 << len(items))]


def get_sum(a, b):                                         # add without '+': XOR is the sum without carry, AND << 1 is the carry
    MASK, MAX = 0xFFFFFFFF, 0x7FFFFFFF                     # Python ints are unbounded, so emulate 32 bits for negatives
    while b:
        a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
    return a if a <= MAX else ~(a ^ MASK)


assert single_number([4, 1, 2, 1, 2]) == 4 and single_number([7]) == 7
assert single_numbers_two([1, 2, 1, 3, 2, 5]) == [3, 5]
assert [count_bits(n) for n in (0, 7, 8, 255)] == [0, 3, 1, 8] and all(count_bits(n) == n.bit_count() == bin(n).count("1") for n in range(64))
assert [is_power_of_two(n) for n in (1, 2, 3, 16, 0, -8)] == [True, True, False, True, False, False]
assert missing_number([3, 0, 1]) == 2 and missing_number([0, 1]) == 2 and missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8
assert reverse_bits(43261596) == 964176192
assert subsets_bitmask([1, 2, 3]) == [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
assert get_sum(1, 2) == 3 and get_sum(-2, 3) == 1 and get_sum(-5, -7) == -12
assert (5).bit_length() == 3 and 6 & 3 == 2 and 6 | 3 == 7 and 6 ^ 3 == 5 and -8 >> 1 == -4 and ~5 == -6
print("bit manipulation ok")
```

```output
```

!warning Python integers are unbounded :: There is no fixed-width overflow, so `~x` is `-x - 1`, right shifts of negatives keep the sign, and problems that assume 32-bit wrap-around need an explicit mask (`& 0xFFFFFFFF`) as in `get_sum`. Know this difference from Java and C++ before you translate a bit trick.

??  How does XOR find the single number among pairs?
=> `x ^ x = 0` and `x ^ 0 = x`, and XOR is commutative and associative, so XOR-ing the whole array cancels every pair and leaves the unpaired value. O(n) time and O(1) space.
??  How do you count the set bits of a number quickly?
=> Kernighan's trick: `n &= n - 1` clears the lowest set bit, so the loop runs once per set bit. In Python 3.10+ use `n.bit_count()`.
??  How does a bitmask represent a set and what operations does it give?
=> Bit i of an integer says whether item i is in the set: union is `|`, intersection `&`, difference `& ~`, membership `mask >> i & 1`, and adding or removing an item `mask | 1 << i` or `mask & ~(1 << i)`. It makes subsets of n ≤ 20 items cheap to enumerate and to use as DP states.
