@part py-dsa-5 | DSA Patterns in Python · Part 5: Heaps and Graphs | dsa
## Heaps and Top-K

A **heap** is a tree stored in an array that always exposes its minimum (or maximum) in O(1) and supports push and pop in O(log n). Python's `heapq` is a **min-heap** on a plain list. Use a heap whenever the question is "give me the best element so far, repeatedly" or "keep only the k best".

**Signals.** "k largest/smallest/most frequent", "merge k sorted", "running median", "always process the smallest next" (scheduling, Dijkstra).

The top-k trick: to keep the **k largest**, hold a **min-heap of size k**. A new item beats the smallest of the current best k (`heap[0]`) or it does not; each step costs O(log k), so n items cost O(n log k), better than sorting all n.

```python Heaps.py
import heapq
from collections import Counter


class KthLargest:
    """Streaming k-th largest: a min-heap of the k largest values; its root is the answer."""
    def __init__(self, k, nums):
        self.k, self.heap = k, []
        for n in nums:
            self.add(n)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)                      # drop the smallest: it can never be in the top k
        return self.heap[0]


def k_closest(points, k):
    return heapq.nsmallest(k, points, key=lambda p: p[0] ** 2 + p[1] ** 2)


def top_k_frequent(nums, k):
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)


def last_stone_weight(stones):
    heap = [-s for s in stones]                           # a max-heap by negation
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = -heapq.heappop(heap), -heapq.heappop(heap)
        if a != b:
            heapq.heappush(heap, -(a - b))
    return -heap[0] if heap else 0


class MedianFinder:
    """Two heaps: `low` (max-heap) holds the smaller half, `high` (min-heap) the larger half."""
    def __init__(self):
        self.low, self.high = [], []

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))   # the largest of the low half moves up
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))   # keep low the same size or one larger

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


def reorganize_string(s):
    """Rearrange so no two equal letters are adjacent: always place the most frequent letter that is not the previous one."""
    heap = [(-count, ch) for ch, count in Counter(s).items()]
    heapq.heapify(heap)
    result, held = [], None
    while heap or held:
        if not heap:
            return ""                                      # only the held letter is left: impossible
        count, ch = heapq.heappop(heap)
        result.append(ch)
        if held:
            heapq.heappush(heap, held)
        held = (count + 1, ch) if count + 1 < 0 else None  # the letter just used must wait one turn
    return "".join(result)


def least_interval(tasks, cooldown):
    counts = Counter(tasks)
    most = max(counts.values())
    with_most = sum(1 for c in counts.values() if c == most)
    return max(len(tasks), (most - 1) * (cooldown + 1) + with_most)     # idle slots are only forced by the most frequent task


stream = KthLargest(3, [4, 5, 8, 2])
assert [stream.add(x) for x in (3, 5, 10, 9, 4)] == [4, 5, 5, 8, 8]
assert k_closest([[1, 3], [-2, 2]], 1) == [[-2, 2]] and k_closest([[3, 3], [5, -1], [-2, 4]], 2) == [[3, 3], [-2, 4]]
assert top_k_frequent([1, 1, 1, 2, 2, 3], 2) == [1, 2]
assert last_stone_weight([2, 7, 4, 1, 8, 1]) == 1 and last_stone_weight([1]) == 1
median = MedianFinder()
for n, expected in ((1, 1.0), (2, 1.5), (3, 2.0), (4, 2.5)):
    median.add_num(n)
    assert median.find_median() == expected
assert reorganize_string("aab") in ("aba",) and reorganize_string("aaab") == "" and len(reorganize_string("aabbcc")) == 6
assert all(a != b for a, b in zip(reorganize_string("aabbcc"), reorganize_string("aabbcc")[1:]))
assert least_interval(list("AAABBB"), 2) == 8 and least_interval(list("AAABBB"), 0) == 6 and least_interval(list("AAAAAABCDEFG"), 2) == 16
print("heaps ok")
```

```output
```

!interview Min-heap versus max-heap for "k largest" :: Counter-intuitive but standard: to keep the **k largest**, use a **min**-heap of size k, because its root is the *smallest of the best k*, the first thing to evict. To keep the k smallest, use a max-heap (negate values in Python). Say why; it signals you understand the structure rather than the recipe.

??  What is the complexity of finding the k largest of n items with a heap?
=> O(n log k) time and O(k) space: each of the n items is compared with the heap root and, if better, costs one push and one pop of O(log k). Sorting would be O(n log n); quickselect is O(n) on average.
??  How does the two-heap median finder work?
=> A max-heap holds the smaller half and a min-heap the larger half, kept balanced (sizes equal or the lower one larger by one). The median is the lower root, or the mean of both roots. Insertion is O(log n), lookup O(1).
??  Why is `heapq.heapify` O(n) rather than O(n log n)?
=> Sifting down from the middle of the array towards the root, most nodes are near the leaves and move very little; the sum of the sift-down costs over all levels converges to O(n).

## Graph Representation, DFS and BFS

A **graph** is nodes (vertices) and edges. Store it as an **adjacency list** (a dict from node to neighbours): O(V + E) space, the right choice for sparse graphs and what interviews expect. Many problems hide a graph: a grid (cells are nodes, moves are edges), a word list (words one letter apart), a state machine.

- **DFS** (stack or recursion) goes deep first: connectivity, cycles, components, paths, backtracking.
- **BFS** (queue) goes level by level: **shortest path in an unweighted graph**, fewest moves, nearest something.
- Always track **visited**, or a cycle makes the search run forever.

```python GraphSearch.py
from collections import defaultdict, deque


def build_graph(n, edges, directed=False):
    graph = defaultdict(list)
    for a, b in edges:
        graph[a].append(b)
        if not directed:
            graph[b].append(a)
    return graph


def shortest_path_length(graph, start, goal):
    queue, distance = deque([start]), {start: 0}
    while queue:
        node = queue.popleft()
        if node == goal:
            return distance[node]
        for nxt in graph[node]:
            if nxt not in distance:                       # visited check doubles as the distance table
                distance[nxt] = distance[node] + 1
                queue.append(nxt)
    return -1


def count_components(n, edges):
    graph, seen, components = build_graph(n, edges), set(), 0
    for start in range(n):
        if start in seen:
            continue
        components += 1
        stack = [start]
        while stack:                                       # iterative DFS
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(graph[node])
    return components


def has_cycle_undirected(n, edges):
    graph, seen = build_graph(n, edges), set()

    def dfs(node, parent):
        seen.add(node)
        for nxt in graph[node]:
            if nxt == parent:
                continue
            if nxt in seen or dfs(nxt, node):
                return True
        return False

    return any(dfs(v, -1) for v in range(n) if v not in seen)


def has_cycle_directed(n, edges):
    graph = build_graph(n, edges, directed=True)
    state = [0] * n                                        # 0 = unvisited, 1 = on the current path, 2 = finished

    def dfs(node):
        state[node] = 1
        for nxt in graph[node]:
            if state[nxt] == 1 or (state[nxt] == 0 and dfs(nxt)):
                return True                                # reaching a node still on the path = a back edge = cycle
        state[node] = 2
        return False

    return any(dfs(v) for v in range(n) if state[v] == 0)


def is_bipartite(n, edges):
    graph, colour = build_graph(n, edges), {}
    for start in range(n):
        if start in colour:
            continue
        colour[start], queue = 0, deque([start])
        while queue:
            node = queue.popleft()
            for nxt in graph[node]:
                if nxt not in colour:
                    colour[nxt] = 1 - colour[node]
                    queue.append(nxt)
                elif colour[nxt] == colour[node]:
                    return False                           # an odd cycle
    return True


def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2)   # multi-source BFS
    fresh = sum(row.count(1) for row in grid)
    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1
    return -1 if fresh else minutes


def word_ladder(begin, end, words):
    words = set(words)
    if end not in words:
        return 0
    buckets = defaultdict(list)                            # "h*t" -> words matching that wildcard pattern
    for w in words | {begin}:
        for i in range(len(w)):
            buckets[w[:i] + "*" + w[i + 1:]].append(w)
    queue, seen = deque([(begin, 1)]), {begin}
    while queue:
        word, steps = queue.popleft()
        if word == end:
            return steps
        for i in range(len(word)):
            for nxt in buckets[word[:i] + "*" + word[i + 1:]]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, steps + 1))
    return 0


def max_area_of_island(grid):
    rows, cols, best = len(grid), len(grid[0]), 0

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != 1:
            return 0
        grid[r][c] = 0                                     # mark visited by sinking the land
        return 1 + dfs(r + 1, c) + dfs(r - 1, c) + dfs(r, c + 1) + dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            best = max(best, dfs(r, c))
    return best


g = build_graph(6, [(0, 1), (1, 2), (0, 3), (3, 4), (4, 2)])
assert shortest_path_length(g, 0, 2) == 2 and shortest_path_length(g, 0, 5) == -1 and shortest_path_length(g, 2, 2) == 0
assert count_components(5, [(0, 1), (1, 2), (3, 4)]) == 2 and count_components(3, []) == 3
assert has_cycle_undirected(4, [(0, 1), (1, 2), (2, 0)]) and not has_cycle_undirected(4, [(0, 1), (1, 2), (2, 3)])
assert has_cycle_directed(3, [(0, 1), (1, 2), (2, 0)]) and not has_cycle_directed(3, [(0, 1), (0, 2), (1, 2)])
assert is_bipartite(4, [(0, 1), (1, 2), (2, 3), (3, 0)]) and not is_bipartite(3, [(0, 1), (1, 2), (2, 0)])
assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4 and oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1 and oranges_rotting([[0]]) == 0
assert word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5 and word_ladder("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
assert max_area_of_island([[1, 1, 0], [0, 1, 0], [0, 0, 1]]) == 3
print("graph search ok")
```

```output
```

| Task | Algorithm | Cost |
| --- | --- | --- |
| Reachable? components? | DFS or BFS with a visited set | O(V + E) |
| Fewest edges (unweighted shortest path) | **BFS** | O(V + E) |
| Cycle in an **undirected** graph | DFS, ignoring the parent edge (or union-find) | O(V + E) |
| Cycle in a **directed** graph | DFS with three colours (a back edge to a node on the current path) | O(V + E) |
| Two-colourable? | BFS/DFS colouring | O(V + E) |
| Spread from many sources at once | **Multi-source BFS** (put all sources in the queue first) | O(V + E) |

??  Why does BFS find the shortest path in an unweighted graph?
=> It explores nodes in order of increasing distance: all nodes at distance d are dequeued before any at distance d + 1, so the first time it reaches a node is along a shortest path. With weighted edges this breaks and you need Dijkstra.
??  How do you detect a cycle in a directed graph?
=> DFS with three states: unvisited, on the current recursion path, finished. If an edge leads to a node that is on the current path, there is a cycle. (An edge to a finished node is fine.) Kahn's topological sort detects it too, by failing to remove all nodes.
??  What is multi-source BFS and when do you use it?
=> Put all source nodes in the queue at distance 0 before starting, so the search expands from all of them simultaneously. It computes, for every cell, the distance to the nearest source in one pass (rotting oranges, walls and gates, 01-matrix).

## Topological Sort

For a **directed acyclic graph** (DAG) of dependencies, a **topological order** lists every node after all nodes it depends on. It answers: "in what order can tasks run?", and fails exactly when the graph has a cycle. **Kahn's algorithm**: repeatedly remove nodes with in-degree 0.

```python Topological.py
from collections import defaultdict, deque


def topological_order(n, prerequisites):
    """prerequisites: pairs (course, must_take_first). Returns an order, or [] if a cycle makes it impossible."""
    graph, indegree = defaultdict(list), [0] * n
    for course, first in prerequisites:
        graph[first].append(course)
        indegree[course] += 1
    queue = deque(v for v in range(n) if indegree[v] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == n else []                # unprocessed nodes are on a cycle


def can_finish(n, prerequisites):
    return len(topological_order(n, prerequisites)) == n


def alien_order(words):
    """Derive the letter order from a sorted list of words in an unknown alphabet."""
    graph = {ch: set() for w in words for ch in w}
    for a, b in zip(words, words[1:]):
        if len(a) > len(b) and a.startswith(b):
            return ""                                      # "abc" before "ab" is invalid
        for x, y in zip(a, b):
            if x != y:
                graph[x].add(y)                            # the first difference decides the order
                break
    indegree = {ch: 0 for ch in graph}
    for ch in graph:
        for nxt in graph[ch]:
            indegree[nxt] += 1
    queue = deque(ch for ch in graph if indegree[ch] == 0)
    out = []
    while queue:
        ch = queue.popleft()
        out.append(ch)
        for nxt in graph[ch]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return "".join(out) if len(out) == len(graph) else ""


def minimum_semesters(n, relations):
    """Parallel courses: the number of Kahn 'layers' is the minimum number of semesters (the longest chain)."""
    graph, indegree = defaultdict(list), [0] * (n + 1)
    for first, second in relations:
        graph[first].append(second)
        indegree[second] += 1
    layer = [v for v in range(1, n + 1) if indegree[v] == 0]
    semesters, taken = 0, 0
    while layer:
        semesters += 1
        taken += len(layer)
        following = []
        for node in layer:
            for nxt in graph[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    following.append(nxt)
        layer = following
    return semesters if taken == n else -1


order = topological_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])
position = {course: i for i, course in enumerate(order)}
assert len(order) == 4 and all(position[first] < position[course] for course, first in [(1, 0), (2, 0), (3, 1), (3, 2)])
assert can_finish(2, [(1, 0)]) and not can_finish(2, [(1, 0), (0, 1)]) and topological_order(2, [(1, 0), (0, 1)]) == []
assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf" and alien_order(["abc", "ab"]) == "" and alien_order(["z", "x", "z"]) == ""
assert minimum_semesters(3, [(1, 3), (2, 3)]) == 2 and minimum_semesters(3, [(1, 2), (2, 3), (3, 1)]) == -1
print("topological sort ok")
```

```output
```

??  When do you need a topological sort?
=> Whenever items have dependencies and you need a valid execution order: build systems, course prerequisites, task schedulers, package installation (pip's resolver), spreadsheet cell evaluation. If the sort cannot place every node, the dependencies contain a cycle.
??  How does Kahn's algorithm detect a cycle?
=> Nodes on a cycle never reach in-degree 0, so they are never queued. If the output contains fewer nodes than the graph, a cycle exists.

## Union-Find (Disjoint Set Union)

**Union-find** maintains groups of elements and answers "are these two in the same group?" and "merge these two groups" in nearly constant time (with path compression and union by size). It is the tool for **dynamic connectivity** and for building minimum spanning trees with Kruskal's algorithm.

```python UnionFind.py
class UnionFind:
    def __init__(self, n):
        self.parent, self.size, self.groups = list(range(n)), [1] * n, n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]      # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                      # already connected: this edge would close a cycle
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.groups -= 1
        return True


def count_provinces(is_connected):
    n = len(is_connected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                uf.union(i, j)
    return uf.groups


def redundant_connection(edges):
    uf = UnionFind(len(edges) + 1)
    for a, b in edges:
        if not uf.union(a, b):
            return [a, b]                                      # the edge that joins two already-connected nodes


def valid_tree(n, edges):
    uf = UnionFind(n)
    return len(edges) == n - 1 and all(uf.union(a, b) for a, b in edges)


def minimum_spanning_tree(n, edges):
    """Kruskal: take the cheapest edge that does not form a cycle."""
    uf, total, used = UnionFind(n), 0, 0
    for a, b, weight in sorted(edges, key=lambda e: e[2]):
        if uf.union(a, b):
            total, used = total + weight, used + 1
    return total if used == n - 1 else -1                      # -1: the graph is not connected


def accounts_merge(accounts):
    uf, owner, name = UnionFind(len(accounts)), {}, {}
    for i, (who, *emails) in enumerate(accounts):
        name[i] = who
        for email in emails:
            if email in owner:
                uf.union(i, owner[email])                      # the same email links two accounts
            else:
                owner[email] = i
    merged = {}
    for email, i in owner.items():
        merged.setdefault(uf.find(i), []).append(email)
    return sorted([name[root]] + sorted(emails) for root, emails in merged.items())


assert count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2 and count_provinces([[1, 0], [0, 1]]) == 2
assert redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3] and redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) and not valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]])
assert minimum_spanning_tree(4, [(0, 1, 10), (0, 2, 6), (0, 3, 5), (1, 3, 15), (2, 3, 4)]) == 19 and minimum_spanning_tree(3, [(0, 1, 1)]) == -1
accounts = [["John", "a@m.com", "b@m.com"], ["John", "c@m.com"], ["John", "a@m.com", "d@m.com"], ["Mary", "m@m.com"]]
assert accounts_merge(accounts) == [["John", "a@m.com", "b@m.com", "d@m.com"], ["John", "c@m.com"], ["Mary", "m@m.com"]]
print("union-find ok")
```

```output
```

??  Union-find or DFS for connected components?
=> For a static graph both are O(V + E). Union-find shines when edges **arrive over time** (dynamic connectivity), when you need to know whether adding an edge creates a cycle, or in Kruskal's algorithm; DFS is simpler when the graph is fully known and you also need paths.
??  What two optimisations make union-find fast, and what is the resulting cost?
=> Union by size (attach the smaller tree to the larger) and path compression (flatten the tree during `find`). Together they give amortised O(α(n)) per operation, where α is the inverse Ackermann function, effectively constant.

## Shortest Paths

| Situation | Algorithm | Cost |
| --- | --- | --- |
| Unweighted edges | BFS | O(V + E) |
| Non-negative weights | **Dijkstra** with a min-heap | O((V + E) log V) |
| Negative weights, or a limit on the number of edges | **Bellman-Ford** | O(VE) |
| All pairs, small graphs | Floyd-Warshall | O(V³) |

**Dijkstra** repeatedly settles the unsettled node with the smallest known distance (the heap), then relaxes its edges. It is greedy and is correct only if **no edge weight is negative**.

```python ShortestPaths.py
import heapq
from collections import defaultdict


def dijkstra(graph, source):
    """graph: node -> list of (neighbour, weight). Returns the shortest distance to every reachable node."""
    dist, heap = {source: 0}, [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue                                           # a stale heap entry: a shorter path was already found
        for nxt, weight in graph[node]:
            nd = d + weight
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    return dist


def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist = dijkstra(graph, k)
    return max(dist.values()) if len(dist) == n else -1


def cheapest_flight(n, flights, src, dst, stops):
    """Bellman-Ford limited to stops + 1 edges: relax from the previous round's values only."""
    cost = [float("inf")] * n
    cost[src] = 0
    for _ in range(stops + 1):
        previous = cost[:]
        for u, v, price in flights:
            if previous[u] + price < cost[v]:
                cost[v] = previous[u] + price
    return -1 if cost[dst] == float("inf") else cost[dst]


def minimum_effort_path(heights):
    """Dijkstra on a grid where the 'distance' of a path is the largest height difference along it."""
    rows, cols = len(heights), len(heights[0])
    effort = [[float("inf")] * cols for _ in range(rows)]
    effort[0][0], heap = 0, [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return e
        if e > effort[r][c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                ne = max(e, abs(heights[nr][nc] - heights[r][c]))
                if ne < effort[nr][nc]:
                    effort[nr][nc] = ne
                    heapq.heappush(heap, (ne, nr, nc))


def floyd_warshall(n, edges):
    dist = [[0 if i == j else float("inf") for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
    for k in range(n):                                         # k = the intermediate node allowed so far
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


graph = defaultdict(list)
for u, v, w in [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 1), ("C", "D", 5)]:
    graph[u].append((v, w))
assert dijkstra(graph, "A") == {"A": 0, "C": 1, "B": 3, "D": 4}
assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2 and network_delay_time([[1, 2, 1]], 2, 2) == -1
flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
assert cheapest_flight(4, flights, 0, 3, 1) == 700 and cheapest_flight(4, flights, 0, 3, 2) == 400 and cheapest_flight(4, flights, 0, 3, 0) == -1
assert minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2 and minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
d = floyd_warshall(3, [(0, 1, 5), (1, 2, 3), (0, 2, 10)])
assert d[0][2] == 8 and d[2][0] == float("inf")
print("shortest paths ok")
```

```output
```

!interview Why can't Dijkstra handle negative edges? :: Dijkstra permanently settles a node when it is popped, assuming no later path can be shorter, which holds only if adding edges never decreases a path's length. A negative edge can make a longer-looking path cheaper after the node was settled. Use Bellman-Ford (which also detects negative cycles), or reweight the graph (Johnson's algorithm).

??  What is the time complexity of Dijkstra with a binary heap?
=> O((V + E) log V): each edge may push one entry (O(log V) each) and each node is settled once. The "stale entry" check (`d > dist[node]`) skips outdated heap entries instead of needing a decrease-key operation.
??  When do you choose BFS, Dijkstra or Bellman-Ford?
=> BFS for unweighted graphs (or all weights equal), Dijkstra for non-negative weights, Bellman-Ford for negative weights or when the number of edges on the path is limited (cheapest flight with at most k stops).
