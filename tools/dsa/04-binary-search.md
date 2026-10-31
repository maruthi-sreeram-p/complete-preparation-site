@part binary-search | Binary Search | foundations
## The idea

Binary search halves the search space every step, giving **O(log n)**. It needs only one thing: a yes/no question whose answer flips exactly once as you move along the range. "Is `nums[i] >= target`?" flips from false to true in a sorted array. "Can Koko eat all the bananas at speed `k`?" flips from false to true as `k` grows. Find the flip point and you have the answer.

That second example is the idea that separates beginners from experienced candidates: you can binary search **on the answer**, not only on an array. Look for it whenever a problem asks for the *minimum value that is enough* or the *maximum value that still works* and checking one candidate is easy.

!tip Signal words :: "sorted", "rotated", "minimum capacity or speed such that", "smallest value that satisfies", "in O(log n)".

| Variant | Question that flips | Typical problems |
|---|---|---|
| Find an exact value | `nums[mid] < target` | Binary Search, Search a 2D Matrix |
| Lower bound | first index with `nums[i] >= target` | Time Based Key-Value Store |
| Rotated array | which half is sorted | Find Minimum, Search in Rotated Sorted Array |
| On the answer | `canFinish(mid)` | Koko Eating Bananas |
| Partition two arrays | left half is no larger than right half | Median of Two Sorted Arrays |

## The Java toolkit and templates

Pick **one** template and learn it until the boundaries are automatic. The version below keeps the invariant "the answer is in `[lo, hi]`" and uses a half-open style that avoids the infinite loops of `mid = (lo + hi) / 2` mistakes.

```java BinarySearchTemplates.java
public class BinarySearchTemplates {

    /** Lower bound: the first index whose value is >= target (nums.length if none). */
    static int lowerBound(int[] nums, int target) {
        int lo = 0, hi = nums.length;                 // the answer is in [lo, hi]
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;             // not (lo + hi) / 2: that can overflow
            if (nums[mid] < target) lo = mid + 1;     // mid is too small to be the answer
            else hi = mid;                            // mid might be the answer
        }
        return lo;
    }

    /** Exact search built on the lower bound. */
    static int indexOf(int[] nums, int target) {
        int i = lowerBound(nums, target);
        return i < nums.length && nums[i] == target ? i : -1;
    }

    /** Koko Eating Bananas: the smallest speed that finishes within h hours. Binary search on the answer. */
    static int minEatingSpeed(int[] piles, int h) {
        int lo = 1, hi = 0;
        for (int p : piles) hi = Math.max(hi, p);     // eating the biggest pile per hour always works
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            long hours = 0;
            for (int p : piles) hours += (p + mid - 1) / mid;   // ceiling division
            if (hours <= h) hi = mid;                 // fast enough: try slower
            else lo = mid + 1;                        // too slow
        }
        return lo;
    }

    /** Find Minimum in Rotated Sorted Array (distinct values): the minimum is where the order breaks. */
    static int findMin(int[] nums) {
        int lo = 0, hi = nums.length - 1;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (nums[mid] > nums[hi]) lo = mid + 1;   // the minimum is to the right of mid
            else hi = mid;
        }
        return nums[lo];
    }

    /** Search in Rotated Sorted Array (distinct values): one half is always sorted. */
    static int searchRotated(int[] a, int target) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == target) return mid;
            if (a[lo] <= a[mid]) {                    // left half is sorted
                if (a[lo] <= target && target < a[mid]) hi = mid - 1;
                else lo = mid + 1;
            } else {                                  // right half is sorted
                if (a[mid] < target && target <= a[hi]) lo = mid + 1;
                else hi = mid - 1;
            }
        }
        return -1;
    }
}
```

**What to notice.** In `minEatingSpeed` the loop never touches an array being searched: it searches the range of possible speeds `[1, max pile]`, and the sorted-ness comes from the monotone question. The hours are summed in a `long` because a large pile count with a speed of 1 can exceed `int`.

!tip The standard library already has it :: `Arrays.binarySearch(array, key)` returns the index, or `-(insertionPoint) - 1` when the key is absent. `Collections.binarySearch` does the same for lists. Know it, but write the loop yourself in an interview.

## Pitfalls and interview angle

- **Overflow.** `(lo + hi) / 2` overflows for large indices; write `lo + (hi - lo) / 2`.
- **Infinite loops.** With `lo < hi`, always move `lo` to `mid + 1` or `hi` to `mid`, never `lo` to `mid`.
- **Mixing two styles.** `while (lo <= hi)` with `hi = mid - 1` and `while (lo < hi)` with `hi = mid` are both correct but must not be mixed.
- **Wrong search space** on the answer: make sure the true answer lies inside `[lo, hi]` and that the question is monotone.
- **Duplicates** change which half is sorted in rotated arrays; that variant needs extra care.

!interview Interview angle: How do you recognise "binary search on the answer"? :: The problem asks for the smallest or largest value satisfying a condition, checking one candidate value is easy (usually a linear scan), and the condition is monotone: if a value works, every larger value also works (or the reverse). Search the range of candidate values and use the check as the comparison.

!keypoints Binary search needs a yes/no question that flips exactly once ;; Use `lo + (hi - lo) / 2` and one consistent loop style ;; Lower bound is the building block for most variants ;; You can search on the answer, not only on an array ;; In a rotated array, one half around mid is always sorted ;; Sum in `long` when the check can overflow `int`

?? What is the time complexity of binary search and why?
=> O(log n): each step discards half of the remaining range, so n elements need about log₂ n steps.

?? Why does `hi = mid` (not `mid - 1`) appear in the lower-bound loop?
=> `mid` itself may be the first index that satisfies the condition, so it must stay inside the range. The loop ends when `lo == hi`, which is the answer.

?? Koko can eat at most 10 piles of up to 10⁹ bananas in 10⁹ hours. How many check iterations does the search need?
=> About log₂(10⁹), roughly 30. Each check is a linear scan of the piles, so the total is O(n log maxPile).
