@part advanced-graphs | Advanced Graphs | advanced
## The idea

The Graphs topic covered traversal and connectivity. Here the edges have **weights** or the question is about a special structure: shortest paths, minimum spanning trees, and paths that use every edge exactly once.

| Question | Algorithm | Cost |
|---|---|---|
| Shortest path from one source, **non-negative** weights | **Dijkstra** with a min-heap | O((V + E) log V) |
| Shortest path with at most **k edges**, or with negative weights | **Bellman-Ford** (relax all edges k times) | O(k · E) |
| Connect all nodes with minimum total weight | **Kruskal** (sort edges + Union-Find) or **Prim** (min-heap) | O(E log E) |
| Use every edge exactly once | **Hierholzer's** Eulerian path | O(E) |
| Order from pairwise constraints (alien dictionary) | Build a graph, then topological sort | O(V + E) |
| Shortest path where the "cost" is the worst edge on the way | Dijkstra variant (heap by the maximum so far) | O(V² log V) on a grid |

!tip Signal words :: "network delay", "cheapest", "minimum cost to connect all", "at most k stops", "weights", "itinerary that uses all tickets". Unweighted shortest path is plain BFS; do not reach for Dijkstra then.

**Dijkstra in one sentence:** always expand the unvisited node with the smallest known distance. Once a node is taken from the heap its distance is final, *provided no edge weight is negative*. With a negative edge that argument fails, so use Bellman-Ford.

## The Java toolkit and templates

```java AdvancedGraphs.java
import java.util.*;

public class AdvancedGraphs {

    /** Dijkstra: edges are {from, to, weight}. Returns the distance to every node (Long.MAX_VALUE if unreachable). */
    static long[] dijkstra(int n, int[][] edges, int source) {
        List<List<int[]>> next = new ArrayList<>();
        for (int i = 0; i < n; i++) next.add(new ArrayList<>());
        for (int[] e : edges) next.get(e[0]).add(new int[] { e[1], e[2] });

        long[] dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[source] = 0;
        PriorityQueue<long[]> heap = new PriorityQueue<>((a, b) -> Long.compare(a[1], b[1]));   // {node, distance}
        heap.offer(new long[] { source, 0 });
        while (!heap.isEmpty()) {
            long[] top = heap.poll();
            int u = (int) top[0];
            if (top[1] > dist[u]) continue;                  // a stale entry: a shorter route was found since
            for (int[] edge : next.get(u)) {
                long candidate = dist[u] + edge[1];
                if (candidate < dist[edge[0]]) {
                    dist[edge[0]] = candidate;
                    heap.offer(new long[] { edge[0], candidate });
                }
            }
        }
        return dist;
    }

    /** Network Delay Time: the answer is the largest shortest distance, or -1 if some node is unreachable. */
    static int networkDelayTime(int[][] times, int n, int k) {
        long[] dist = dijkstra(n + 1, times, k);             // nodes are 1-based, so index 0 is unused
        long worst = 0;
        for (int node = 1; node <= n; node++) {
            if (dist[node] == Long.MAX_VALUE) return -1;
            worst = Math.max(worst, dist[node]);
        }
        return (int) worst;
    }

    /** Cheapest Flights Within K Stops: Bellman-Ford limited to k + 1 edges, relaxing from the previous round's costs. */
    static int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        int[] cost = new int[n];
        Arrays.fill(cost, Integer.MAX_VALUE);
        cost[src] = 0;
        for (int round = 0; round <= k; round++) {
            int[] next = cost.clone();                       // read old costs, write new ones: no extra hops in a round
            for (int[] f : flights) {
                if (cost[f[0]] != Integer.MAX_VALUE && cost[f[0]] + f[2] < next[f[1]]) {
                    next[f[1]] = cost[f[0]] + f[2];
                }
            }
            cost = next;
        }
        return cost[dst] == Integer.MAX_VALUE ? -1 : cost[dst];
    }

    /** Min Cost to Connect All Points: Kruskal with a tiny union-find; all pairs are candidate edges (Manhattan distance). */
    static int minCostConnectPoints(int[][] points) {
        int n = points.length;
        List<int[]> edges = new ArrayList<>();               // {weight, a, b}
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                edges.add(new int[] { Math.abs(points[i][0] - points[j][0]) + Math.abs(points[i][1] - points[j][1]), i, j });
        edges.sort((a, b) -> Integer.compare(a[0], b[0]));

        int[] parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int total = 0, used = 0;
        for (int[] e : edges) {
            int ra = find(parent, e[1]), rb = find(parent, e[2]);
            if (ra == rb) continue;                          // would close a cycle
            parent[ra] = rb;
            total += e[0];
            if (++used == n - 1) break;                      // a spanning tree has n - 1 edges
        }
        return total;
    }

    private static int find(int[] parent, int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }
}
```

**What to notice.** In `dijkstra` the heap may hold several entries for one node; the `top[1] > dist[u]` check discards the outdated ones, which is simpler than a "decrease key" operation that `PriorityQueue` does not have. In `findCheapestPrice` the `clone()` matters: updating `cost` in place would let a path use more than one new edge per round and break the stops limit.

### Other patterns in this topic

- **Swim in Rising Water** is Dijkstra where a path's cost is the **highest cell** on it, not the sum: the heap is keyed by that maximum, and the first time you pop the target you have the answer.
- **Reconstruct Itinerary** is an Eulerian path: build adjacency lists sorted lexicographically (a `PriorityQueue` per airport), do a DFS that consumes edges, and add each airport to the route in **post-order**; the reversed list is the itinerary.
- **Alien Dictionary** turns each pair of adjacent words into at most one ordering edge between the first differing letters, then topologically sorts the letters. A cycle, or a longer word before its own prefix, means the input is invalid.

## Pitfalls and interview angle

- **Dijkstra with negative edges** gives wrong answers silently. Know the condition.
- **Using `int` for distances** that can overflow when adding; use `long` or an infinity that cannot overflow.
- **Updating Bellman-Ford costs in place** when the number of edges is limited.
- **Stale heap entries** if you forget the skip check: correct but slower, and wrong if you mark nodes visited at push time.
- **1-based labels** (Network Delay Time): allocate `n + 1` slots.

!interview Interview angle: Why does Dijkstra fail with negative edge weights? :: Dijkstra assumes that when a node is taken from the heap, no later path can be shorter, because any later path must add non-negative weights. A negative edge can make a longer-looking path shorter after the node was finalised, so its distance is wrong. Bellman-Ford, which re-examines every edge repeatedly, handles negative weights (and detects negative cycles).

!keypoints Dijkstra: heap by distance, skip stale entries, non-negative weights only ;; Bellman-Ford relaxes all edges up to k times: use it for "at most k edges" and negative weights ;; Kruskal: sort edges, add the cheapest edge that does not close a cycle (Union-Find) ;; Eulerian paths use Hierholzer's algorithm with post-order output ;; Alien Dictionary is a graph built from adjacent words plus a topological sort ;; Use `long` distances and read the previous round's costs when limiting edges

?? What is the complexity of Dijkstra with a binary heap?
=> O((V + E) log V): each edge may push one heap entry, and each push or pop costs O(log) in the heap size.

?? Why clone the cost array each round in the Cheapest Flights Within K Stops solution?
=> To make sure round i only extends paths that used at most i edges. Updating in place would let one round chain several new edges, so a route could exceed the allowed number of stops.

?? When would you choose Prim's over Kruskal's for a minimum spanning tree?
=> Prim's with a heap suits dense graphs, because it grows one tree and never sorts all edges. Kruskal's suits sparse graphs or when the edges are already given as a list, since it only needs a sort and a Union-Find.
