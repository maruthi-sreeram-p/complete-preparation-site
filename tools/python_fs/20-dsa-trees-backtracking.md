@part py-dsa-4 | DSA Patterns in Python · Part 4: Recursion, Backtracking and Trees | dsa
## Recursion and Divide and Conquer

A **recursive** function solves a problem by solving smaller instances of the same problem. Every correct recursion has three parts: a **base case** that stops, a **smaller subproblem** (progress towards the base case), and **trust** that the recursive call returns the right answer for the smaller input. **Divide and conquer** splits the input, solves the pieces and combines them (merge sort, quickselect, fast exponentiation).

```python Recursion.py
import random


def power(x, n):                                       # fast exponentiation: O(log n) instead of O(n)
    if n < 0:
        return 1 / power(x, -n)
    if n == 0:
        return 1.0
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x


def merge_sort(nums):
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left, right = merge_sort(nums[:mid]), merge_sort(nums[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:                        # <= keeps the sort stable
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    return merged + left[i:] + right[j:]


def count_inversions(nums):
    """Pairs i < j with nums[i] > nums[j]: merge sort, counting while merging."""
    if len(nums) <= 1:
        return nums, 0
    mid = len(nums) // 2
    (left, a), (right, b) = count_inversions(nums[:mid]), count_inversions(nums[mid:])
    merged, i, j, cross = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
            cross += len(left) - i                     # every remaining left element is greater than right[j]
    return merged + left[i:] + right[j:], a + b + cross


def quickselect(nums, k):
    """k-th smallest (0-based) in expected O(n): partition around a random pivot and keep only the side that holds k."""
    pivot = random.choice(nums)
    smaller = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    if k < len(smaller):
        return quickselect(smaller, k)
    if k < len(smaller) + len(equal):
        return pivot
    return quickselect([x for x in nums if x > pivot], k - len(smaller) - len(equal))


def flatten_depth(items):                              # recursion mirrors nested data
    return 1 + max((flatten_depth(i) for i in items if isinstance(i, list)), default=0)


assert power(2, 10) == 1024 and power(2, -2) == 0.25 and power(5, 0) == 1 and abs(power(1.5, 5) - 7.59375) < 1e-9
data = [5, 2, 9, 1, 5, 6, 0]
assert merge_sort(data) == sorted(data) and merge_sort([]) == []
assert count_inversions([2, 4, 1, 3, 5])[1] == 3 and count_inversions([5, 4, 3, 2, 1])[1] == 10 and count_inversions([1, 2, 3])[1] == 0
assert quickselect([3, 2, 1, 5, 6, 4], 4) == 5 and quickselect([7], 0) == 7                     # 2nd largest = index 4 of 6
assert flatten_depth([1, [2, [3]], [4]]) == 3
print("recursion ok")
```

```output
```

!warning Python has a recursion limit and no tail-call optimisation :: The default limit is about 1000 frames (`sys.getrecursionlimit()`). Recursion on a linked list or a skewed tree with 10⁵ nodes raises `RecursionError`. Convert to an explicit stack or loop, or (in contests, carefully) raise the limit. State this when you choose recursion: it shows you know the platform.

??  What are the three ingredients of a correct recursive function?
=> A base case that returns without recursing; a recursive step that moves strictly closer to a base case; and combining the sub-results correctly. Missing or unreachable base cases cause infinite recursion (`RecursionError` in Python).
??  Why is quickselect O(n) on average but O(n²) in the worst case?
=> On average a random pivot halves the data, so the work is n + n/2 + n/4 + ... = O(n). A consistently bad pivot (always the minimum) shrinks the input by one each time, giving O(n²). Randomising the pivot makes the worst case extremely unlikely.
??  What is the recurrence for merge sort and its solution?
=> T(n) = 2T(n/2) + O(n), which solves to O(n log n): log n levels of recursion, each doing O(n) merging work.

## Backtracking: Subsets, Permutations and Combinations

**Idea.** Build a solution one choice at a time. **Choose** an option, **explore** the rest recursively, then **un-choose** (undo) and try the next option. When the partial solution can no longer lead anywhere valid, **prune** and return: pruning is what separates backtracking from blind brute force.

**Signals.** "Generate all ...", "list every ...", "find all combinations that ...", small n (≤ about 20).

```python Backtracking.py
def subsets(nums):
    result, path = [], []

    def go(start):
        result.append(path[:])                         # every partial path is itself a subset
        for i in range(start, len(nums)):
            path.append(nums[i])                       # choose
            go(i + 1)                                  # explore
            path.pop()                                 # un-choose

    go(0)
    return result


def subsets_with_dup(nums):
    nums.sort()
    result, path = [], []

    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                               # skip a duplicate at the same decision level
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result


def permutations(nums):
    result, used, path = [], [False] * len(nums), []

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True; path.append(nums[i])
            go()
            path.pop(); used[i] = False

    go()
    return result


def combinations(n, k):
    result, path = [], []

    def go(start):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, n + 1 - (k - len(path)) + 1):      # prune: not enough numbers left to fill the path
            path.append(i)
            go(i + 1)
            path.pop()

    go(1)
    return result


def combination_sum(candidates, target):               # each number may be reused
    result, path = [], []

    def go(start, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue                               # prune
            path.append(candidates[i])
            go(i, remaining - candidates[i])           # i, not i + 1: reuse allowed
            path.pop()

    go(0, target)
    return result


def generate_parentheses(n):
    result = []

    def go(current, opened, closed):
        if len(current) == 2 * n:
            result.append(current)
            return
        if opened < n:
            go(current + "(", opened + 1, closed)
        if closed < opened:                            # a ")" is only valid if something is open
            go(current + ")", opened, closed + 1)

    go("", 0, 0)
    return result


assert len(subsets([1, 2, 3])) == 8 and sorted(map(tuple, subsets_with_dup([1, 2, 2]))) == [(), (1,), (1, 2), (1, 2, 2), (2,), (2, 2)]
assert len(permutations([1, 2, 3])) == 6 and permutations([1, 2]) == [[1, 2], [2, 1]]
assert combinations(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]] and combination_sum([2], 1) == []
assert generate_parentheses(3) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
print("backtracking ok")
```

```output
```

!cheat The backtracking template ::
```
def go(state):
    if state is complete: record a COPY of it; return
    for each option available from state:
        if option is invalid or cannot lead to a solution: continue   # prune
        apply option
        go(next state)
        undo option
```
Record a **copy** (`path[:]`), because `path` keeps changing. To avoid duplicates, sort first and skip equal values at the same level.
!end

??  What is the difference between backtracking and brute force?
=> Both explore a tree of choices, but backtracking abandons a branch as soon as it violates a constraint (pruning), which can cut the search drastically. The worst case is still exponential, which is why it suits small n.
??  Why append `path[:]` and not `path` to the result?
=> `path` is one list that is mutated for the whole search; appending it stores a reference that ends up empty or wrong. A slice copy captures the state at that moment.
??  How do you avoid duplicate subsets when the input has duplicates?
=> Sort the numbers, and in the loop skip `nums[i]` if `i > start` and it equals `nums[i - 1]`: at one decision level you only try each distinct value once.

## Backtracking on Grids and Constraints

```python Constraints.py
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        saved, board[r][c] = board[r][c], "#"          # mark the cell as used on this path
        found = any(go(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = saved                            # un-choose
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))


def count_n_queens(n):
    cols, diag1, diag2 = set(), set(), set()           # occupied columns and the two diagonal directions

    def place(row):
        if row == n:
            return 1
        total = 0
        for col in range(n):
            if col in cols or row - col in diag1 or row + col in diag2:
                continue
            cols.add(col); diag1.add(row - col); diag2.add(row + col)
            total += place(row + 1)
            cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)
        return total

    return place(0)


def partition_palindromes(s):
    result, path = [], []

    def go(start):
        if start == len(s):
            result.append(path[:])
            return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:                   # prune: only continue from palindromic pieces
                path.append(piece)
                go(end)
                path.pop()

    go(0)
    return result


def letter_combinations(digits):
    letters = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    if not digits:
        return []
    result = [""]
    for d in digits:
        result = [prefix + ch for prefix in result for ch in letters[d]]
    return result


board = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
assert exist(board, "ABCCED") and exist(board, "SEE") and not exist(board, "ABCB")
assert [count_n_queens(n) for n in (1, 4, 6, 8)] == [1, 2, 4, 92]
assert partition_palindromes("aab") == [["a", "a", "b"], ["aa", "b"]]
assert letter_combinations("23") == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"] and letter_combinations("") == []
print("constraint search ok")
```

```output
```

Constraint problems are backtracking with **fast validity checks**: sets for columns and diagonals make each N-Queens placement check O(1). A Sudoku solver is the same shape (row, column and box sets). Without pruning N-Queens would examine nⁿ boards; with it, the n = 8 search is trivial.

??  How do you check N-Queens diagonals in O(1)?
=> Cells on the same "\" diagonal share `row - col`, and on the same "/" diagonal share `row + col`. Keep a set for each, plus a set of used columns, and a placement is valid when none of the three contain the new cell's values.
??  Why must the word-search DFS restore the cell after exploring?
=> The cell is temporarily marked as visited so the path does not reuse it, but other paths from different start cells or branches may need it. Un-marking on the way back is the "un-choose" step of backtracking.

## Binary Tree DFS

A **binary tree** node has a value and up to two children. Almost every tree problem is a **depth-first traversal** where each node asks its children for information and combines it: the recursion mirrors the structure.

```python TreeDfs.py
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def build_tree(vals):                                  # level-order list with None for missing children
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


def max_depth(node):
    return 0 if not node else 1 + max(max_depth(node.left), max_depth(node.right))


def is_same(a, b):
    if not a or not b:
        return a is b
    return a.val == b.val and is_same(a.left, b.left) and is_same(a.right, b.right)


def invert(node):
    if node:
        node.left, node.right = invert(node.right), invert(node.left)
    return node


def is_symmetric(root):
    def mirror(a, b):
        if not a or not b:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    return mirror(root.left, root.right) if root else True


def diameter(root):
    best = 0

    def depth(node):                                   # returns height; records the best path through each node
        nonlocal best
        if not node:
            return 0
        left, right = depth(node.left), depth(node.right)
        best = max(best, left + right)
        return 1 + max(left, right)

    depth(root)
    return best


def max_path_sum(root):
    best = float("-inf")

    def gain(node):                                    # best downward path starting at node (never below 0)
        nonlocal best
        if not node:
            return 0
        left, right = max(gain(node.left), 0), max(gain(node.right), 0)
        best = max(best, node.val + left + right)      # a path that bends at this node
        return node.val + max(left, right)

    gain(root)
    return best


def has_path_sum(node, target):
    if not node:
        return False
    if not node.left and not node.right:
        return node.val == target
    return has_path_sum(node.left, target - node.val) or has_path_sum(node.right, target - node.val)


def good_nodes(root):
    def go(node, highest):
        if not node:
            return 0
        return (node.val >= highest) + go(node.left, max(highest, node.val)) + go(node.right, max(highest, node.val))
    return go(root, float("-inf"))


def lowest_common_ancestor(root, p, q):
    if not root or root.val in (p, q):
        return root
    left, right = lowest_common_ancestor(root.left, p, q), lowest_common_ancestor(root.right, p, q)
    return root if left and right else left or right


def inorder_iterative(root):                           # explicit stack: no recursion limit
    result, stack, node = [], [], root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.val)
        node = node.right
    return result


tree = build_tree([3, 9, 20, None, None, 15, 7])
assert max_depth(tree) == 3 and max_depth(None) == 0
assert is_same(build_tree([1, 2, 3]), build_tree([1, 2, 3])) and not is_same(build_tree([1, 2]), build_tree([1, None, 2]))
assert inorder_iterative(invert(build_tree([4, 2, 7, 1, 3, 6, 9]))) == [9, 7, 6, 4, 3, 2, 1]
assert is_symmetric(build_tree([1, 2, 2, 3, 4, 4, 3])) and not is_symmetric(build_tree([1, 2, 2, None, 3, None, 3]))
assert diameter(build_tree([1, 2, 3, 4, 5])) == 3 and max_path_sum(build_tree([-10, 9, 20, None, None, 15, 7])) == 42
assert has_path_sum(build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]), 22)
assert good_nodes(build_tree([3, 1, 4, 3, None, 1, 5])) == 4
assert lowest_common_ancestor(build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]), 5, 1).val == 3
assert lowest_common_ancestor(build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]), 5, 4).val == 5
assert inorder_iterative(build_tree([1, None, 2, 3])) == [1, 3, 2]
print("tree dfs ok")
```

```output
```

| Traversal | Order | Use |
| --- | --- | --- |
| Preorder | node, left, right | copy a tree, serialise |
| Inorder | left, node, right | **sorted order for a BST** |
| Postorder | left, right, node | delete, compute from children (height, diameter) |

!interview The "diameter" and "max path sum" trick :: Both need the best path that **bends at a node**, which cannot be returned to the parent. Use a helper that **returns** the one-sided value the parent needs and **updates a variable** (`nonlocal best`) with the two-sided value. Naming that separation is the key insight in many hard tree problems.

??  How do you traverse a tree without recursion?
=> Use an explicit stack: for inorder, push nodes while going left, pop and visit, then go right. For preorder push the right child before the left; for BFS use a queue. This avoids Python's recursion limit on deep trees.
??  What is the time and space complexity of a DFS on a binary tree?
=> O(n) time, since each node is visited once; O(h) space for the call stack, where h is the height: O(log n) for a balanced tree and O(n) for a skewed one.

## Binary Tree BFS and Level Order

**Breadth-first search** visits nodes level by level using a **queue**. Process the nodes already in the queue (one level) before touching the children you just added, by capturing `len(queue)` at the start of each level.

```python TreeBfs.py
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


def level_order(root):
    levels, queue = [], deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):                    # exactly the nodes of the current level
            node = queue.popleft()
            level.append(node.val)
            queue.extend(child for child in (node.left, node.right) if child)
        levels.append(level)
    return levels


def right_side_view(root):
    return [level[-1] for level in level_order(root)]


def zigzag(root):
    return [level if i % 2 == 0 else level[::-1] for i, level in enumerate(level_order(root))]


def min_depth(root):
    if not root:
        return 0
    queue, depth = deque([root]), 1
    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()
            if not node.left and not node.right:
                return depth                           # BFS reaches the first leaf at the minimum depth
            queue.extend(child for child in (node.left, node.right) if child)
        depth += 1


def serialize(root):
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        out.append("#" if node is None else str(node.val))
        if node:
            queue.extend((node.left, node.right))
    return ",".join(out)


def deserialize(data):
    values = data.split(",")
    if values[0] == "#":
        return None
    root = TreeNode(int(values[0]))
    queue, i = deque([root]), 1
    while queue:
        node = queue.popleft()
        for side in ("left", "right"):
            if i < len(values) and values[i] != "#":
                setattr(node, side, TreeNode(int(values[i])))
                queue.append(getattr(node, side))
            i += 1
    return root


tree = build_tree([3, 9, 20, None, None, 15, 7])
assert level_order(tree) == [[3], [9, 20], [15, 7]] and level_order(None) == []
assert right_side_view(build_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
assert zigzag(tree) == [[3], [20, 9], [15, 7]]
assert min_depth(tree) == 2 and min_depth(build_tree([2, None, 3, None, 4])) == 3
assert level_order(deserialize(serialize(tree))) == level_order(tree) and deserialize(serialize(None)) is None
print("tree bfs ok")
```

```output
```

??  When do you use BFS rather than DFS on a tree?
=> When the answer depends on levels or distance from the root: level-order output, right side view, minimum depth (BFS stops at the first leaf), shortest path. DFS suits problems that combine information from children or explore whole root-to-leaf paths.
??  Why capture `len(queue)` at the start of each level?
=> The queue grows as you enqueue children, so a loop over the live length would mix levels. Fixing the count first processes exactly the nodes of the current level.

## BST and Tree Construction

A **binary search tree** keeps `left < node < right` for every node, so search, insert and delete take O(h) and an **inorder traversal is sorted**. Validating a BST needs *ranges*, not just a comparison with the parent.

```python Bst.py
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


def inorder(node):
    return inorder(node.left) + [node.val] + inorder(node.right) if node else []


def is_valid_bst(node, low=float("-inf"), high=float("inf")):
    if not node:
        return True
    return low < node.val < high and is_valid_bst(node.left, low, node.val) and is_valid_bst(node.right, node.val, high)


def kth_smallest(root, k):
    stack, node = [], root
    while True:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right


def lca_bst(root, p, q):
    while root:
        if p < root.val and q < root.val:
            root = root.left
        elif p > root.val and q > root.val:
            root = root.right
        else:
            return root                                # the paths split here (or one of them is the node)


def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root


def build_from_preorder_inorder(preorder, inorder_values):
    index = {v: i for i, v in enumerate(inorder_values)}
    position = 0

    def build(lo, hi):                                 # builds the subtree for inorder[lo..hi]
        nonlocal position
        if lo > hi:
            return None
        root = TreeNode(preorder[position])
        position += 1
        mid = index[root.val]
        root.left = build(lo, mid - 1)                 # the left subtree comes first in preorder
        root.right = build(mid + 1, hi)
        return root

    return build(0, len(inorder_values) - 1)


def sorted_array_to_bst(nums):
    if not nums:
        return None
    mid = len(nums) // 2
    return TreeNode(nums[mid], sorted_array_to_bst(nums[:mid]), sorted_array_to_bst(nums[mid + 1:]))


def height(node):
    return 0 if not node else 1 + max(height(node.left), height(node.right))


assert is_valid_bst(build_tree([2, 1, 3])) and not is_valid_bst(build_tree([5, 1, 4, None, None, 3, 6]))
assert not is_valid_bst(build_tree([5, 4, 6, None, None, 3, 7]))               # 3 is in the right subtree of 5: too small
bst = build_tree([5, 3, 6, 2, 4, None, None, 1])
assert kth_smallest(bst, 3) == 3 and inorder(bst) == [1, 2, 3, 4, 5, 6]
assert lca_bst(build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]), 2, 8).val == 6
assert lca_bst(build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]), 2, 4).val == 2
root = None
for v in (4, 2, 7, 1, 3):
    root = insert(root, v)
assert inorder(root) == [1, 2, 3, 4, 7]
rebuilt = build_from_preorder_inorder([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
assert inorder(rebuilt) == [9, 3, 15, 20, 7] and (rebuilt.val, rebuilt.right.val, rebuilt.right.left.val) == (3, 20, 15)
balanced = sorted_array_to_bst([-10, -3, 0, 5, 9])
assert inorder(balanced) == [-10, -3, 0, 5, 9] and height(balanced) == 3
print("bst ok")
```

```output
```

!interview The classic BST validation bug :: Checking only `node.left.val < node.val < node.right.val` accepts `[5, 4, 6, None, None, 3, 7]`, because 3 is less than its parent 6 but sits in the **right subtree of 5**. Carry the allowed `(low, high)` range down the recursion, or check that an inorder traversal is strictly increasing.

??  How do you validate a binary search tree?
=> Pass a `(low, high)` range to each recursive call: the node's value must lie strictly between them, the left child gets `(low, node.val)` and the right child `(node.val, high)`. Alternatively an inorder traversal must be strictly increasing.
??  Why does preorder plus inorder identify a unique tree?
=> Preorder gives the root first; finding that value in the inorder sequence splits the nodes into the left and right subtrees; recursing gives each subtree's root from the next preorder items. A dictionary from value to inorder index makes the split O(1), so construction is O(n).

## Tries

A **trie** (prefix tree) stores strings along paths of characters: each node maps a character to a child. Insert, search and prefix queries cost O(length of the word), independent of how many words are stored. Use it for **prefix** problems, autocomplete and spell-checkers.

```python Tries.py
class TrieNode:
    def __init__(self):
        self.children, self.end = {}, False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def _find(self, prefix):
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if not node:
                return None
        return node

    def search(self, word):
        node = self._find(word)
        return bool(node and node.end)

    def starts_with(self, prefix):
        return self._find(prefix) is not None

    def suggestions(self, prefix, limit=3):
        node, out = self._find(prefix), []
        if not node:
            return out

        def walk(current, path):
            if len(out) == limit:
                return
            if current.end:
                out.append(prefix + path)
            for ch in sorted(current.children):
                walk(current.children[ch], path + ch)

        walk(node, "")
        return out


class WordDictionary:
    """add_word and search where '.' matches any one letter."""
    def __init__(self):
        self.root = TrieNode()

    def add_word(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def search(self, word):
        def go(i, node):
            if i == len(word):
                return node.end
            if word[i] == ".":
                return any(go(i + 1, child) for child in node.children.values())
            return word[i] in node.children and go(i + 1, node.children[word[i]])
        return go(0, self.root)


def find_words(board, words):
    """Word Search II: one DFS over the grid guided by a trie, instead of one DFS per word."""
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, TrieNode())
        node.end = w
    found, rows, cols = [], len(board), len(board[0])

    def go(r, c, node):
        ch = board[r][c]
        child = node.children.get(ch)
        if not child:
            return
        if child.end:
            found.append(child.end)
            child.end = False                          # report each word once
        board[r][c] = "#"
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                go(nr, nc, child)
        board[r][c] = ch

    for r in range(rows):
        for c in range(cols):
            go(r, c, root)
    return sorted(found)


trie = Trie()
for w in ("apple", "app", "apply", "apt", "bat"):
    trie.insert(w)
assert trie.search("app") and not trie.search("ap") and trie.starts_with("ap") and not trie.starts_with("c")
assert trie.suggestions("ap") == ["app", "apple", "apply"] and trie.suggestions("z") == []
words = WordDictionary()
for w in ("bad", "dad", "mad"):
    words.add_word(w)
assert words.search("pad") is False and words.search("bad") and words.search(".ad") and words.search("b..") and not words.search("b.")
grid = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
assert find_words(grid, ["oath", "pea", "eat", "rain"]) == ["eat", "oath"]
print("tries ok")
```

```output
```

??  When is a trie better than a hash set of words?
=> For prefix operations: "does any word start with this prefix?", autocomplete and longest common prefix. A hash set answers exact membership in O(length) too but cannot enumerate or test prefixes without scanning all words.
??  Why use a trie in Word Search II?
=> A trie lets one DFS from each cell explore all dictionary words at once and abandon a path the moment no word has that prefix, instead of running a separate search per word. Removing found words (`end = False`) avoids duplicates, and pruning empty branches speeds it up further.
