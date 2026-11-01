@part gate-algorithms | Algorithms | software
## Asymptotic analysis and recurrences

### Notation

| Notation | Meaning | Intuition |
|---|---|---|
| f = O(g) | f ≤ c·g for large n | upper bound |
| f = Ω(g) | f ≥ c·g for large n | lower bound |
| f = Θ(g) | both O(g) and Ω(g) | tight bound |
| f = o(g) | f/g → 0 | strictly smaller |
| f = ω(g) | f/g → ∞ | strictly bigger |

If f = O(g) **and** g = O(f), then f = Θ(g). Worst-case, best-case and average-case are different functions of n; GATE asks for the **worst case** unless it says otherwise.

### Order of growth

log log n < log n < (log n)ᵏ < n^ε < n < n log n < n² < n³ < nᵏ < 2ⁿ < n! < nⁿ.

Useful comparisons: **n^(log n) = 2^(log² n)**, which beats any polynomial but loses to 2ⁿ. **(log n)^(log n) = 2^(log n · log log n)** also beats every polynomial and loses to 2^(√n). To compare two functions, take logarithms of both.

### Solving recurrences

| Recurrence | Solution |
|---|---|
| T(n) = T(n − 1) + 1 | Θ(n) |
| T(n) = T(n − 1) + n | Θ(n²). T(n) = n(n + 1)/2 when T(1) = 1 |
| T(n) = 2T(n − 1) + 1 | Θ(2ⁿ). T(n) = 2ⁿ − 1 when T(0) = 0 |
| T(n) = T(n/2) + 1 | Θ(log n) |
| T(n) = T(n/2) + n | Θ(n) |
| T(n) = 2T(n/2) + 1 | Θ(n) |
| T(n) = 2T(n/2) + n | Θ(n log n) |
| T(n) = T(√n) + 1 | Θ(log log n) |

**Master theorem.** For T(n) = a·T(n/b) + f(n) with a ≥ 1, b > 1, compare f(n) with n^(log_b a):

1. If f(n) = O(n^(log_b a − ε)), then T(n) = Θ(n^(log_b a)). *The leaves dominate.*
2. If f(n) = Θ(n^(log_b a) · logᵏ n), then T(n) = Θ(n^(log_b a) · log^(k+1) n). *Every level costs the same.*
3. If f(n) = Ω(n^(log_b a + ε)) (and a·f(n/b) ≤ c·f(n)), then T(n) = Θ(f(n)). *The root dominates.*

| T(n) | n^(log_b a) | Case | Result |
|---|---|---|---|
| 8T(n/2) + n² | n³ | 1 | Θ(n³) |
| 4T(n/2) + n² | n² | 2 (k = 0) | Θ(n² log n) |
| 3T(n/2) + n | n^1.585 | 1 | Θ(n^(log₂ 3)) |
| 2T(n/2) + n log n | n | 2 (k = 1) | Θ(n log² n) |
| 2T(n/2) + n² | n | 3 | Θ(n²) |
| 7T(n/2) + n² (Strassen) | n^2.81 | 1 | Θ(n^(log₂ 7)) |

### Loop analysis

```c Counting loop iterations
for (i = 1; i < n; i *= 2)        // i = 1, 2, 4, 8, ...
    for (j = 0; j < i; j++)       // inner loop runs i times
        count++;
// total = 1 + 2 + 4 + ... < 2n   -> Theta(n).  For n = 16 it is 1 + 2 + 4 + 8 = 15

for (i = n; i > 0; i /= 2)        // log2(n) + 1 iterations
    for (j = 0; j < n; j++)       // n each time
        count++;
// total = n (log2 n + 1) -> Theta(n log n).  For n = 16 it is 5 * 16 = 80
```

**Amortised analysis.** A dynamic array that doubles when full copies 1 + 2 + 4 + … < 2n elements over n appends, so each append costs O(1) amortised. Appending 16 elements, starting from capacity 1, copies 1 + 2 + 4 + 8 = 15 elements in all.

!cheat Asymptotics cheat codes ::
- **Compare by logs:** log(n^(log n)) = log² n versus log(2ⁿ) = n, so 2ⁿ wins easily.
- **Master theorem in three lines:** compute n^(log_b a), compare to f(n), and pick the bigger one (or add a log if they tie).
- **Substitute small n** into a recurrence to confirm a closed form such as T(10) = 55 for T(n) = T(n − 1) + n.
- **Nested loops:** when the inner bound depends on the outer variable, write the sum, don't multiply the bounds.
- **A halving loop runs ⌊log₂ n⌋ + 1 times.**
- **O(g) and Ω(g) together mean Θ(g).** O alone is only an upper bound, so n = O(n²) is true.
!end

## Searching, sorting and hashing

### Searching

- **Linear search:** Θ(n) comparisons in the worst case.
- **Binary search** on a sorted array: at most **⌊log₂ n⌋ + 1** comparisons. For n = 1000 that is 10.

### Sorting

| Algorithm | Best | Average | Worst | Space | Stable? |
|---|---|---|---|---|---|
| Bubble | n | n² | n² | 1 | yes |
| Selection | n² | n² | n² | 1 | no |
| Insertion | n | n² | n² | 1 | yes |
| Merge | n log n | n log n | n log n | n | yes |
| Quick | n log n | n log n | **n²** | log n | no |
| Heap | n log n | n log n | n log n | 1 | no |
| Counting | n + k | n + k | n + k | n + k | yes |
| Radix | d(n + b) | d(n + b) | d(n + b) | n + b | yes |

- **Inversions:** the number of pairs i < j with a[i] > a[j]. Insertion sort does exactly as many swaps as there are inversions, so its time is Θ(n + inversions). The array 5, 2, 4, 1, 3 has 7 inversions. Merge sort counts inversions in O(n log n).
- **Quick sort** with the first or last element as pivot degrades to its worst case, n(n − 1)/2 comparisons, on an already sorted array.
- **Merge sort worst case:** T(n) = 2T(n/2) + n − 1, which for n = 8 gives 17 comparisons.
- **Lower bound for comparison sorting:** a decision tree has n! leaves and height at least ⌈log₂ n!⌉ = Θ(n log n). Sorting 5 elements needs at least ⌈log₂ 120⌉ = 7 comparisons.
- **Counting sort** takes Θ(n + k) for keys in 0…k − 1. **Radix sort** with base b and d digits takes Θ(d(n + b)); n integers below n² sorted in base n need 2 passes, i.e. Θ(n).

### Selection problems

| Task | Comparisons |
|---|---|
| Find the maximum of n | n − 1 |
| Merge two sorted lists of sizes m and n (worst case) | m + n − 1 |
| Maximum and minimum together | ⌈3n/2⌉ − 2 (pair up the elements) |
| Second largest (tournament) | n + ⌈log₂ n⌉ − 2 |
| k-th smallest | Θ(n) on average (quickselect); median of medians gives Θ(n) in the worst case |

### Hashing

A hash function h maps keys into m slots. The **load factor** is α = n/m.

- **Chaining:** each slot has a list. An unsuccessful search examines α keys on average, so costs 1 + α; with n = 2000 keys in m = 500 slots the average chain has 4 keys.
- **Open addressing** stores everything in the table and probes a sequence of slots. α < 1. With uniform hashing an unsuccessful search takes about **1/(1 − α)** probes (2 at α = 0.5).
- **Linear probing** (h(k) + i) suffers **primary clustering**; quadratic probing suffers milder secondary clustering; double hashing (h₁(k) + i·h₂(k)) avoids both.
- **Deleting** from an open-addressed table must leave a *tombstone*. Simply emptying the slot breaks later searches that probe through it.
- The probability that 3 keys hashed uniformly into 10 slots land in different slots is (10·9·8)/10³ = 0.72.

```text Linear probing, m = 7, h(k) = k mod 7
insert 10 -> slot 3
insert 17 -> 17 mod 7 = 3 (taken) -> slot 4
insert  3 ->  3 mod 7 = 3, 4 taken -> slot 5
insert 24 -> 24 mod 7 = 3, 4, 5 taken -> slot 6
```

!cheat Sorting and hashing cheat codes ::
- **Stable sorts:** bubble, insertion, merge, counting, radix. **Not stable:** selection, quick, heap.
- **Already sorted input:** insertion sort O(n), quick sort (first pivot) O(n²), merge sort O(n log n).
- **Comparison counts:** max n − 1, merge m + n − 1, min and max ⌈3n/2⌉ − 2, second largest n + ⌈log n⌉ − 2.
- **Hash tables:** chaining → α, open addressing → 1/(1 − α). Simulate the probe sequence by hand and write the table after each insert.
- **Binary search** is only valid on sorted data. Its worst case is ⌊log₂ n⌋ + 1.
!end

## Divide and conquer

**Divide** the problem into smaller instances, **conquer** them recursively, **combine** the answers. The running time follows from the recurrence.

| Algorithm | Recurrence | Time |
|---|---|---|
| Binary search | T(n) = T(n/2) + 1 | Θ(log n) |
| Merge sort | T(n) = 2T(n/2) + n | Θ(n log n) |
| Quick sort (balanced split) | T(n) = 2T(n/2) + n | Θ(n log n) |
| Maximum subarray | T(n) = 2T(n/2) + n | Θ(n log n) |
| Closest pair of points | T(n) = 2T(n/2) + n | Θ(n log n) |
| Karatsuba multiplication | T(n) = 3T(n/2) + n | Θ(n^1.585) |
| Strassen matrix multiplication | T(n) = 7T(n/2) + n² | Θ(n^2.81) |
| Counting inversions | merge-sort based | Θ(n log n) |

Merge sort uses Θ(n) extra space for merging, while quick sort uses Θ(log n) stack space on average (Θ(n) in the worst case).

!cheat Divide-and-conquer cheat codes ::
- **Count the subproblems and their size:** a subproblems of size n/b with combine cost f(n). Then use the master theorem.
- **Fewer multiplications win:** Karatsuba uses 3 instead of 4 half-size products, and Strassen 7 instead of 8.
- **Combine step cost decides:** linear combine → n log n, constant combine → n.
!end

## Greedy algorithms

A greedy algorithm makes the best local choice at each step and never reconsiders. It is correct only when the problem has the **greedy-choice property** and **optimal substructure**.

| Problem | Greedy rule | Correct? |
|---|---|---|
| Activity selection (maximise the number of compatible intervals) | pick the earliest **finish** time | yes |
| Fractional knapsack | highest value/weight ratio first | yes |
| **0/1 knapsack** | highest ratio first | **no** (use DP) |
| Huffman coding | repeatedly merge the two lowest-frequency nodes | yes |
| Job sequencing with deadlines | highest profit first, placed in the latest free slot ≤ deadline | yes |
| Optimal merge of files | merge the two smallest each time | yes |
| Minimum spanning tree | Kruskal and Prim | yes |
| Single-source shortest paths (non-negative weights) | Dijkstra | yes |
| Coin change | largest coin first | only for canonical systems |

**Worked examples**

- *Activities* (1,3), (2,5), (4,7), (6,9), (8,10), (9,12): by earliest finish pick (1,3), (4,7), (8,10): **3** activities.
- *Huffman* frequencies 3, 5, 7, 9, 12: merge 3 + 5 = 8, then 7 + 8 = 15, then 9 + 12 = 21, then 15 + 21 = 36. The cost (sum of merged weights) is 8 + 15 + 21 + 36 = **80**. For Fibonacci-like frequencies 1, 1, 2, 3, 5, 8 the tree is a chain, and the rarest symbols get codes of length 5.
- *Fractional knapsack*, capacity 40, (value, weight): (30,5), (40,10), (45,15), (60,20). The ratios are 6, 4, 3, 3. Take the first three whole (weight 30, value 115), then 10 of the 20 units of the last item for 30, total **145**. The 0/1 optimum for the same items is only 135.
- *Job sequencing* (profit, deadline): (50,2), (10,1), (20,2), (30,1), (40,3). Take 50 in slot 2, 40 in slot 3, 30 in slot 1, and the other two do not fit: profit **120**.
- *Optimal merge* of file sizes 2, 3, 5, 7: 2 + 3 = 5, 5 + 5 = 10, 7 + 10 = 17. Total cost 5 + 10 + 17 = **32**.
- *Coin change* with coins {1, 3, 4} for 6: greedy takes 4 + 1 + 1 (3 coins) but the optimum is 3 + 3 (2 coins).

!cheat Greedy cheat codes ::
- **Sort by the right key:** finish time for activities, ratio for fractional knapsack, profit for jobs, frequency for Huffman.
- **Huffman cost** = sum of all internal node weights = Σ frequency × code length.
- **Two-minimum merge** (Huffman, optimal merge) uses a heap. The cost is O(n log n).
- **A greedy rule that is not obviously right is usually wrong.** Hunt for a small counterexample, as the coin system {1, 3, 4} gives.
- **A tie in Huffman** can give different trees, but the same total cost.
!end

## Dynamic programming

Use DP when a problem has **optimal substructure** and **overlapping subproblems**. Memoisation fills the table top-down from recursion. Tabulation fills it bottom-up. Both turn an exponential recursion into a polynomial one.

| Problem | Recurrence idea | Time |
|---|---|---|
| Fibonacci | F(n) = F(n−1) + F(n−2) | O(n) |
| 0/1 knapsack | best[c] = max(best[c], best[c − w] + v) | O(nW) |
| Longest common subsequence (LCS) | equal chars: 1 + L[i−1][j−1], else max(L[i−1][j], L[i][j−1]) | O(mn) |
| Edit distance | min(insert, delete, replace) on a table | O(mn) |
| Matrix chain multiplication | min over splits k of m[i][k] + m[k+1][j] + p[i−1]p[k]p[j] | O(n³) |
| Longest increasing subsequence | L[i] = 1 + max L[j] for a[j] < a[i] | O(n²), or O(n log n) |
| Coin change (ways) | ways[x] += ways[x − c] for each coin | O(n·amount) |
| Floyd–Warshall | d[i][j] = min(d[i][j], d[i][k] + d[k][j]) | O(V³) |
| Grid paths (right/down) | paths[i][j] = paths[i−1][j] + paths[i][j−1] | O(mn); C(m+n, n) |

**Worked results**

- LCS of ACGTTGCA and CTGACTA has length **5**.
- Edit distance between *algorithm* and *altruistic* is **6**.
- Matrix chain with dimensions 10×20, 20×5, 5×30, 30×8 (p = 10, 20, 5, 30, 8): minimum **2600** scalar multiplications.
- The number of full parenthesisations of a product of n matrices is the Catalan number C(n−1): 42 for n = 6.
- 0/1 knapsack, capacity 40, (weight, value): (5,30), (10,40), (15,45), (20,60): optimum **135**, taking weights 5 + 15 + 20.
- Longest increasing subsequence of 3, 10, 2, 1, 20, 4, 6, 12: length **4** (for example 2, 4, 6, 12).
- Ways to make 10 from coins {1, 2, 5}: **10**. A 5×5 grid of cells has C(8, 4) = **70** monotone paths.

!cheat DP cheat codes ::
- **Define the state first,** in words: "L[i][j] = LCS length of the first i and first j characters".
- **Table size = time:** (m+1)(n+1) cells with O(1) work per cell is Θ(mn).
- **0/1 knapsack is pseudo-polynomial:** O(nW) depends on the value of W, not on its bit length.
- **Iterate capacity downwards** in the 1-D knapsack array to use each item once. Iterate upwards to allow repeated items (unbounded).
- **Matrix chain:** count the cost p[i−1]·p[k]·p[j] of the final multiplication, and fill the table by increasing chain length.
- **LIS and LCS are different:** LIS needs the inner loop over earlier elements.
!end

## Graph algorithms

### Traversals and their uses

BFS and DFS both take **O(V + E)** with adjacency lists. BFS gives shortest paths in **unweighted** graphs. DFS gives:

- **Edge classification:** tree, back, forward and cross edges. A directed graph has a **cycle exactly when DFS finds a back edge**.
- **Topological sort** of a DAG: vertices in decreasing finish time.
- **Strongly connected components** in O(V + E) with Kosaraju's or Tarjan's algorithm. The directed graph with edges 1→2, 2→3, 3→1, 3→4, 4→5, 5→4 has 2 SCCs: {1, 2, 3} and {4, 5}.

### Minimum spanning trees

A spanning tree has V − 1 edges. The **cut property** (the lightest edge crossing any cut belongs to some MST) and the **cycle property** (the heaviest edge on a cycle is not in the MST, if unique) justify both algorithms.

| Algorithm | Method | Time |
|---|---|---|
| **Kruskal** | sort edges, add each if it joins two different components (union–find) | O(E log E) = O(E log V) |
| **Prim** | grow one tree, adding the cheapest edge leaving it | O(V²) with an array and a matrix; O(E log V) with a binary heap |

- If all edge weights are **distinct**, the MST is **unique**. Equal weights can give several MSTs, but they all have the same total weight.
- Kruskal on edges AB4, AC2, BC1, BD5, CD8, CE10, DE2, DF6, EF3 (6 vertices) picks BC1, AC2, DE2, EF3 and BD5 for a total of **13**.
- The MST depends only on the *order* of the weights, so replacing every weight w by w² (all positive) leaves the MST unchanged, though the total weight changes.

### Shortest paths

| Algorithm | Handles | Time |
|---|---|---|
| **Dijkstra** | non-negative weights | O((V + E) log V) with a heap; O(V²) with an array |
| **Bellman–Ford** | negative weights, detects negative cycles | O(VE); V − 1 passes of relaxing all edges |
| Shortest path in a DAG | any weights | O(V + E) in topological order |
| **Floyd–Warshall** | all pairs, negative edges (no negative cycles) | O(V³) (about 10⁶ steps for V = 100) |
| BFS | unweighted | O(V + E) |

**Dijkstra fails with negative edges** because it finalises a vertex's distance when it is popped. Worked example: edges S→A 4, S→B 1, B→A 2, A→C 1, B→C 5. Dijkstra finalises B (1), then A (3), then C (4).

!cheat Graph-algorithm cheat codes ::
- **Kruskal by hand:** sort, then write which component each endpoint is in. Skip an edge if both are in the same one.
- **Prim by hand:** keep a "cheapest edge into the tree" label on each outside vertex and update it as the tree grows.
- **MST edge count** is V − 1. If you picked fewer, the graph is disconnected.
- **Dijkstra by hand:** a table of tentative distances, finalising the smallest each round.
- **Negative edge weights?** Use Bellman–Ford (single source) or Floyd–Warshall (all pairs). Dijkstra may give a wrong answer.
- **Dense graph** (E ≈ V²) → Prim with a matrix, O(V²), is as good as any.
!end

## Beyond the listed topics: P and NP in one page

The 2027 syllabus names only complexity analysis, but P and NP questions have appeared in the past, so know the basics.

- **P:** problems solvable in polynomial time. **NP:** problems whose solutions can be *verified* in polynomial time. P ⊆ NP, and whether P = NP is open.
- **NP-hard:** at least as hard as every problem in NP. **NP-complete:** in NP and NP-hard. If any NP-complete problem is in P, then P = NP.
- Known NP-complete: SAT, 3-SAT, clique, vertex cover, Hamiltonian cycle, subset sum, 0/1 knapsack (decision form), graph colouring (3 colours), travelling salesman (decision form).
- In P: shortest path, MST, 2-SAT, matching, linear programming, primality testing.

## Cheat sheet: Algorithms on one page

| Topic | Fact |
|---|---|
| Master theorem | compare f(n) with n^(log_b a) |
| 2T(n/2) + n | Θ(n log n); T(n−1) + n → Θ(n²); T(√n) + 1 → Θ(log log n) |
| Binary search | ⌊log₂ n⌋ + 1 comparisons |
| Comparison-sort lower bound | ⌈log₂ n!⌉ |
| Stable | bubble, insertion, merge, counting, radix |
| Quick sort worst case | n(n − 1)/2 comparisons on sorted input (first pivot) |
| Merge m and n | m + n − 1 |
| Min and max together | ⌈3n/2⌉ − 2 |
| Chaining / open addressing | α / 1/(1 − α) |
| Activity selection | earliest finish |
| Huffman cost | sum of internal node weights |
| 0/1 knapsack, LCS, edit distance, MCM | O(nW), O(mn), O(mn), O(n³) |
| Kruskal / Prim | O(E log V) / O(V²) or O(E log V) |
| Dijkstra / Bellman–Ford / Floyd–Warshall | O((V+E) log V) / O(VE) / O(V³) |
| DFS back edge | cycle in a directed graph |

??  Solve T(n) = 4T(n/2) + n² and say which case of the master theorem applies.
=> n^(log₂ 4) = n² matches f(n) = n² exactly (case 2 with k = 0), so T(n) = Θ(n² log n).
??  Why does the greedy "largest ratio first" rule fail for 0/1 knapsack but work for fractional knapsack?
=> In the fractional version leftover capacity is filled with part of an item, so the rule never wastes capacity. In 0/1 an item cannot be split, so a high-ratio item can leave unused space that a different combination would fill. Example: capacity 40 with the four items of the worked example gives greedy 115 but optimum 135.
??  Why can Dijkstra's algorithm give wrong answers on negative edges?
=> It treats the distance of a popped vertex as final. A negative edge discovered later could still lower that distance, but Dijkstra never revisits it.
??  What is the amortised cost of an append to a dynamic array that doubles when full?
=> Over n appends the total copying is at most 1 + 2 + 4 + … + n/2 < n, so the total work is below 2n and each append costs O(1) amortised, even though a single append can cost Θ(n).
