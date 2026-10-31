@part heap-priority-queue | Heap / Priority Queue | trees
## The idea

A **heap** keeps the smallest (min-heap) or largest (max-heap) element available in O(1) and lets you insert or remove it in O(log n). It does *not* keep everything sorted: it only guarantees the top. That is exactly enough for problems that repeatedly ask for "the best remaining item".

| Pattern | Idea | Problems |
|---|---|---|
| **Top K** | Keep a heap of size k; the heap root is the k-th best so far | Kth Largest in a Stream, K Closest Points, Kth Largest Element |
| **Two heaps** | A max-heap for the lower half and a min-heap for the upper half; the median sits at the tops | Find Median from Data Stream |
| **Scheduling / simulation** | Always take the next most urgent item | Task Scheduler, Last Stone Weight, Design Twitter |
| **Merge k sources** | Heap holds the current head of each source | Merge k Sorted Lists |

!tip Counter-intuitive but true :: For "the k largest", use a **min-heap** of size k. When it overflows, you evict the smallest of your candidates. The heap then always holds the k largest seen so far, and its root is the k-th largest. Cost: O(n log k), better than sorting when k is small.

## The Java toolkit and templates

`PriorityQueue<E>` is a **min-heap** by default. For a max-heap pass `Comparator.reverseOrder()` or a lambda. Its operations: `offer`/`add` O(log n), `poll` O(log n), `peek` O(1), `remove(Object)` O(n).

```java HeapTemplates.java
import java.util.*;

public class HeapTemplates {

    /** Kth Largest Element: a min-heap of size k holds the k largest values seen. */
    static int findKthLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int n : nums) {
            heap.offer(n);
            if (heap.size() > k) heap.poll();               // evict the smallest candidate
        }
        return heap.peek();
    }

    /** K Closest Points to Origin: a max-heap of size k keyed by distance evicts the farthest. */
    static int[][] kClosest(int[][] points, int k) {
        PriorityQueue<int[]> farthestFirst =
                new PriorityQueue<>((a, b) -> Integer.compare(squaredDistance(b), squaredDistance(a)));
        for (int[] p : points) {
            farthestFirst.offer(p);
            if (farthestFirst.size() > k) farthestFirst.poll();
        }
        return farthestFirst.toArray(new int[0][]);
    }

    private static int squaredDistance(int[] p) {
        return p[0] * p[0] + p[1] * p[1];                   // no square root needed to compare distances
    }

    /** Last Stone Weight: repeatedly smash the two heaviest stones. */
    static int lastStoneWeight(int[] stones) {
        PriorityQueue<Integer> heaviest = new PriorityQueue<>(Comparator.reverseOrder());
        for (int s : stones) heaviest.offer(s);
        while (heaviest.size() > 1) {
            int a = heaviest.poll(), b = heaviest.poll();
            if (a != b) heaviest.offer(a - b);
        }
        return heaviest.isEmpty() ? 0 : heaviest.peek();
    }

    /** Find Median from Data Stream: two heaps, balanced so that low has the same size or one more. */
    static class MedianFinder {
        private final PriorityQueue<Integer> low = new PriorityQueue<>(Comparator.reverseOrder()); // max-heap
        private final PriorityQueue<Integer> high = new PriorityQueue<>();                          // min-heap

        void addNum(int num) {
            low.offer(num);
            high.offer(low.poll());                         // the largest of low moves up, keeping low <= high
            if (high.size() > low.size()) low.offer(high.poll());
        }

        double findMedian() {
            return low.size() > high.size() ? low.peek() : (low.peek() + high.peek()) / 2.0;
        }
    }
}
```

**What to notice.** `kClosest` compares **squared** distances, which keeps everything in integers and preserves the order. The two-heap `addNum` always pushes through `low` then `high`, which re-balances automatically with two lines instead of a tangle of `if`s.

## Pitfalls and interview angle

- **Comparator overflow.** `(a, b) -> a - b` can overflow for large or negative values. Use `Integer.compare(a, b)`.
- **Iterating a `PriorityQueue`** does **not** give sorted order: only `poll()` does. `toString` and the for-each loop show the internal array.
- **`remove(Object)` is O(n).** If you need to delete arbitrary items often, use lazy deletion (skip stale entries when they reach the top) or a `TreeMap`.
- **Min versus max confusion** for top-K: the heap type is the *opposite* of the answer you want.
- **Ties.** If equal keys need a rule, put it in the comparator.

!interview Interview angle: Why is building a heap from n elements O(n), but inserting n elements one at a time O(n log n)? :: Bulk heap construction (heapify) sifts down from the middle of the array, and most nodes are near the bottom where sifting is cheap, which sums to O(n). Repeated insertion sifts each new element up through up to log n levels. Java's `PriorityQueue(Collection)` constructor uses the linear heapify.

!keypoints A heap gives the best element in O(1) and removal or insertion in O(log n), but does not keep order ;; Top K largest: min-heap of size k, top K smallest: max-heap of size k, O(n log k) ;; Two heaps (max-heap low, min-heap high) maintain a running median ;; `PriorityQueue` is a min-heap by default; reverse with `Comparator.reverseOrder()` ;; Use `Integer.compare`, not subtraction ;; Iterating a `PriorityQueue` is not sorted; `remove(Object)` is O(n)

?? How do you find the k-th largest element in a stream of numbers?
=> Keep a min-heap of the k largest numbers. For each new number, add it and, if the size exceeds k, remove the smallest. The heap's root is the k-th largest. Each update costs O(log k).

?? When is a heap better than sorting?
=> When you need only the top k of many items or a running best of a stream. A heap costs O(n log k) and O(k) space; sorting costs O(n log n) and needs all data first.

?? Why do you need two heaps to maintain a median?
=> The median is at the boundary between the lower and upper halves of the data. A max-heap of the lower half and a min-heap of the upper half expose both boundary elements at their tops in O(1), and rebalancing keeps the sizes within one.
