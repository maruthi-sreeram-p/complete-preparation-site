@part arrays-hashing | Arrays & Hashing | foundations
## The idea

Most first-round problems are about *remembering something you have already seen*. An array gives you cheap access by position. A hash table (`HashMap`, `HashSet`) gives you cheap access by **value**: "have I seen this number?", "how many times did this letter occur?", "which index held the complement?". Trading memory for lookup speed turns many O(n²) double loops into one O(n) pass.

Reach for hashing when the problem says: *duplicate*, *anagram*, *frequency*, *pair that sums to*, *group by*, *first unique*, *consecutive*. Reach for a plain array (instead of a map) when the keys are small and dense, such as lowercase letters: `int[26]` is faster and simpler than `HashMap<Character,Integer>`.

| Operation | `HashMap` / `HashSet` | Array of size n |
|---|---|---|
| Insert, lookup, remove by key | O(1) average | Lookup by index O(1) |
| Iterate | O(n), no guaranteed order | O(n), index order |
| Extra memory | O(n) | O(n) |

!tip Signal words :: "Without sorting", "in O(n) time", "count the number of", "group together" almost always mean a hash table or a counting array.

## The Java toolkit and templates

`HashMap.merge(key, 1, Integer::sum)` counts in one line. `computeIfAbsent(key, k -> new ArrayList<>())` builds groups. A `HashSet` answers "seen before?" with the return value of `add`. When the key is a *collection of values* (a sorted word, a count signature), turn it into a `String` or `List`: **arrays do not compare by content as map keys**.

```java ArraysHashing.java
import java.util.*;

public class ArraysHashing {

    /** Two Sum: remember each value and where you saw it. */
    static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();            // value -> index
        for (int i = 0; i < nums.length; i++) {
            Integer j = seen.get(target - nums[i]);
            if (j != null) return new int[] { j, i };
            seen.put(nums[i], i);
        }
        return new int[0];
    }

    /** Group Anagrams: words with the same sorted letters share a key. */
    static List<List<String>> groupAnagrams(String[] words) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String w : words) {
            char[] letters = w.toCharArray();
            Arrays.sort(letters);
            groups.computeIfAbsent(new String(letters), k -> new ArrayList<>()).add(w);
        }
        return new ArrayList<>(groups.values());
    }

    /** Top K Frequent: bucket the numbers by their count, then read from the highest bucket down. O(n). */
    @SuppressWarnings("unchecked")
    static int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int n : nums) freq.merge(n, 1, Integer::sum);
        List<Integer>[] buckets = new List[nums.length + 1];     // index = frequency
        for (Map.Entry<Integer, Integer> e : freq.entrySet()) {
            if (buckets[e.getValue()] == null) buckets[e.getValue()] = new ArrayList<>();
            buckets[e.getValue()].add(e.getKey());
        }
        int[] result = new int[k];
        int filled = 0;
        for (int f = buckets.length - 1; f >= 0 && filled < k; f--) {
            if (buckets[f] == null) continue;
            for (int n : buckets[f]) if (filled < k) result[filled++] = n;
        }
        return result;
    }

    /** Product of Array Except Self: prefix products going right, suffix products going left. No division. */
    static int[] productExceptSelf(int[] a) {
        int[] out = new int[a.length];
        out[0] = 1;
        for (int i = 1; i < a.length; i++) out[i] = out[i - 1] * a[i - 1];
        int suffix = 1;
        for (int i = a.length - 1; i >= 0; i--) {
            out[i] *= suffix;
            suffix *= a[i];
        }
        return out;
    }

    /** Longest Consecutive Sequence: only start counting at the first number of a run. O(n). */
    static int longestConsecutive(int[] nums) {
        Set<Integer> set = new HashSet<>();
        for (int n : nums) set.add(n);
        int best = 0;
        for (int n : set) {
            if (set.contains(n - 1)) continue;                   // not the start of a run
            int length = 1;
            while (set.contains(n + length)) length++;
            best = Math.max(best, length);
        }
        return best;
    }
}
```

**What to notice.** Every method makes *one pass* and lets the table do the searching. In `longestConsecutive` the inner `while` looks like a nested loop, but each number is visited by the `while` at most once overall, because only run starts enter it: that is why the total stays O(n).

## Pitfalls and interview angle

- **Arrays as keys.** `map.put(new int[]{1,2}, ...)` hashes the *reference*, not the contents. Use a `String`, a `List<Integer>`, or a record.
- **`Integer` equality.** `a == b` on two `Integer` objects is only reliable between -128 and 127. Use `equals`.
- **Iteration order.** `HashMap` has no guaranteed order. If the answer must follow insertion order, use `LinkedHashMap`; if sorted, `TreeMap`.
- **Overflow.** Products and sums of `int` overflow silently; use `long` when the constraints allow large values.
- **Modifying while iterating** a map throws `ConcurrentModificationException`.

!interview Interview angle: Why is a `HashMap` lookup O(1) on average but O(n) in the worst case? :: Keys are spread over buckets by `hashCode`. Many collisions put many entries in one bucket, so a lookup scans them. Since Java 8 a bucket with many entries becomes a balanced tree, which makes the worst case O(log n), and good hash functions keep chains short in practice.

!keypoints Hashing trades memory for O(1) lookups: remember what you have seen ;; Use `int[26]` instead of a map when keys are small and dense ;; Arrays do not work as map keys: build a String or List key ;; `merge`, `computeIfAbsent` and the result of `Set.add` replace many lines of checks ;; Counting by frequency and bucketing by count gives O(n) top-K

?? How would you check for a duplicate in an array in O(n) time?
=> Add each element to a `HashSet`; `add` returns false when the element was already there. It uses O(n) extra space; sorting first avoids the space at the cost of O(n log n).

?? Two words are anagrams. What is a key that is the same for both and different for non-anagrams?
=> Their letters sorted, or a 26-element count array turned into a string. Sorting costs O(k log k) per word, the count signature O(k).

?? Why does the Longest Consecutive Sequence solution only start counting when `n - 1` is absent?
=> Starting from every number would walk each run repeatedly, giving O(n²). Starting only at the beginning of a run visits each number once in total.
