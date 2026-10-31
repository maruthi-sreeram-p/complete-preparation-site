@part graphs | Graphs | advanced
## The idea

A graph is nodes connected by edges. Grids, courses with prerequisites, friend networks, word transformations and maps are all graphs in disguise. The skill is (1) **modelling** the problem as nodes and edges, and (2) picking the right traversal.

| Need | Tool | Notes |
|---|---|---|
| Visit everything reachable, count components | DFS or BFS with a `visited` set | O(V + E) |
| Shortest path in an **unweighted** graph (fewest moves) | BFS | First time you reach a node is the shortest |
| Order tasks with prerequisites, detect a cycle | Topological sort (Kahn's algorithm with in-degrees, or DFS) | Only for directed graphs |
| "Are these two connected?", merge groups, find a redundant edge | Union-Find (disjoint set) | Nearly O(1) per operation |
| Shortest path with weights | Dijkstra | See *Advanced Graphs* |

!tip Signal words :: "number of islands or regions", "connected", "prerequisite", "course schedule", "shortest number of steps", "minimum moves", "clone", "valid tree". A grid is a graph where each cell has up to four neighbours.

How a graph is stored decides the code: an **adjacency list** (`List<List<Integer>>` or `Map<Integer, List<Integer>>`) takes O(V + E) space and suits sparse graphs, an **adjacency matrix** takes O(V²) and suits dense graphs and quick edge checks, and a grid needs no extra structure: the neighbours are computed from the coordinates.

## The Java toolkit and templates

```java GraphTemplates.java
import java.util.*;

public class GraphTemplates {

    /** Number of Islands: DFS flood fill; each island is sunk (marked visited) as soon as it is counted. */
    static int numIslands(char[][] grid) {
        int islands = 0;
        for (int r = 0; r < grid.length; r++) {
            for (int c = 0; c < grid[0].length; c++) {
                if (grid[r][c] == '1') {
                    islands++;
                    sink(grid, r, c);
                }
            }
        }
        return islands;
    }

    private static void sink(char[][] grid, int r, int c) {
        if (r < 0 || c < 0 || r >= grid.length || c >= grid[0].length || grid[r][c] != '1') return;
        grid[r][c] = '0';                                    // visited
        sink(grid, r + 1, c);
        sink(grid, r - 1, c);
        sink(grid, r, c + 1);
        sink(grid, r, c - 1);
    }

    /** Rotting Oranges: BFS from all rotten oranges at once; the number of levels is the number of minutes. */
    static int orangesRotting(int[][] grid) {
        Queue<int[]> queue = new ArrayDeque<>();
        int fresh = 0;
        for (int r = 0; r < grid.length; r++)
            for (int c = 0; c < grid[0].length; c++) {
                if (grid[r][c] == 2) queue.add(new int[] { r, c });
                else if (grid[r][c] == 1) fresh++;
            }
        int[][] moves = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } };
        int minutes = 0;
        while (!queue.isEmpty() && fresh > 0) {
            minutes++;
            for (int size = queue.size(); size > 0; size--) {          // one level = one minute
                int[] cell = queue.poll();
                for (int[] m : moves) {
                    int r = cell[0] + m[0], c = cell[1] + m[1];
                    if (r >= 0 && c >= 0 && r < grid.length && c < grid[0].length && grid[r][c] == 1) {
                        grid[r][c] = 2;
                        fresh--;
                        queue.add(new int[] { r, c });
                    }
                }
            }
        }
        return fresh == 0 ? minutes : -1;
    }

    /** Course Schedule II via Kahn's algorithm: edge {a, b} means a must come before b. Empty result = cycle. */
    static int[] topologicalOrder(int n, int[][] edges) {
        List<List<Integer>> next = new ArrayList<>();
        for (int i = 0; i < n; i++) next.add(new ArrayList<>());
        int[] inDegree = new int[n];
        for (int[] e : edges) {
            next.get(e[0]).add(e[1]);
            inDegree[e[1]]++;
        }
        Queue<Integer> ready = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (inDegree[i] == 0) ready.add(i);
        int[] order = new int[n];
        int taken = 0;
        while (!ready.isEmpty()) {
            int u = ready.poll();
            order[taken++] = u;
            for (int v : next.get(u)) if (--inDegree[v] == 0) ready.add(v);
        }
        return taken == n ? order : new int[0];              // fewer than n means a cycle blocked some nodes
    }

    /** Union-Find with path compression and union by size. */
    static class UnionFind {
        private final int[] parent, size;
        int components;

        UnionFind(int n) {
            parent = new int[n];
            size = new int[n];
            components = n;
            for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
        }

        int find(int x) {
            while (parent[x] != x) {
                parent[x] = parent[parent[x]];               // path compression
                x = parent[x];
            }
            return x;
        }

        /** @return false when a and b were already connected (the edge would close a cycle) */
        boolean union(int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) return false;
            if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
            parent[rb] = ra;
            size[ra] += size[rb];
            components--;
            return true;
        }
    }

    /** Redundant Connection: the first edge whose endpoints are already connected. */
    static int[] findRedundantConnection(int[][] edges) {
        UnionFind uf = new UnionFind(edges.length + 1);
        for (int[] e : edges) if (!uf.union(e[0], e[1])) return e;
        return new int[0];
    }
}
```

**What to notice.** In `orangesRotting`, **multi-source BFS** starts with every rotten orange in the queue, so all of them spread in parallel. `size` is read before the level loop so that one pass equals one minute. `UnionFind.union` returning a boolean is what turns "redundant connection" and "graph valid tree" into one-liners.

## Pitfalls and interview angle

- **Marking visited too late.** Mark a node when you *enqueue* it (BFS), not when you dequeue it, or it can be queued many times.
- **Directed versus undirected.** Add the edge in both directions for undirected graphs, and remember that "parent" must be ignored when detecting cycles with DFS.
- **Cycle detection in directed graphs** needs three states (unvisited, in progress, done) in DFS, or Kahn's algorithm; a plain `visited` set gives false positives.
- **Deep recursion.** DFS on a 1000 x 1000 grid can overflow the Java stack: use BFS or an explicit stack.
- **Modifying the input grid** is fine in interviews if you say so; otherwise use a separate `boolean[][]`.

!interview Interview angle: BFS or DFS for shortest path in a maze? :: BFS. It explores in order of distance, so the first time it reaches the target is via a shortest path (in an unweighted graph). DFS finds *a* path, not necessarily the shortest one.

!keypoints Model the problem: what are the nodes, what are the edges? ;; DFS or BFS with a visited set is O(V + E); BFS gives shortest paths in unweighted graphs ;; Multi-source BFS starts with all sources in the queue ;; Kahn's algorithm orders prerequisites and detects cycles by counting taken nodes ;; Union-Find answers connectivity and finds the edge that closes a cycle ;; Mark visited when enqueuing; beware recursion depth on large grids

?? How do you detect a cycle in a directed graph?
=> Run Kahn's algorithm: if fewer than n nodes can be taken (some never reach in-degree 0), a cycle exists. Or use DFS with three states and report a cycle when you reach a node that is still in progress.

?? Why does BFS find the shortest path in an unweighted graph?
=> It visits nodes in non-decreasing order of distance from the source, so the first time a node is reached it is by a path with the fewest edges.

?? What does Union-Find give you that DFS does not?
=> Fast incremental connectivity: after each new edge you can ask whether two nodes are already connected in nearly O(1), without re-traversing the graph. That suits problems where edges arrive one by one.
