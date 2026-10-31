@part sliding-window | Sliding Window | foundations
## The idea

A sliding window is a **contiguous range** `[left, right]` of an array or string that you grow on the right and shrink on the left, while keeping a running summary (a sum, a count map, a set) up to date. Because both ends only move forward, the whole scan is **O(n)**, instead of examining every subarray in O(n²).

| Window type | Rule | Typical problems |
|---|---|---|
| **Fixed size** k | Add the new element, remove the one that left | Permutation in String, Sliding Window Maximum, max sum of k elements |
| **Variable, longest** | Grow while the window is valid; shrink only when it becomes invalid | Longest Substring Without Repeating Characters, Longest Repeating Character Replacement |
| **Variable, shortest** | Grow until valid; then shrink as far as it stays valid, recording each time | Minimum Window Substring, smallest subarray with sum >= target |

!tip Signal words :: "subarray" or "substring" (contiguous), "longest", "shortest", "at most k", "contains all of", "without repeating".

The template is always the same: **expand** `right`, **update** the summary, **while the window breaks the rule, shrink** `left`, then **record** the answer. What changes is the rule and the summary.

## The Java toolkit and templates

Use `int[26]` or `int[128]` for letter counts, a `HashMap` for general keys, and an `ArrayDeque` of indices when you need the maximum or minimum of the window.

```java SlidingWindow.java
import java.util.*;

public class SlidingWindow {

    /** Best Time to Buy and Sell Stock: the "window" is the cheapest price so far. */
    static int maxProfit(int[] prices) {
        int cheapest = Integer.MAX_VALUE, best = 0;
        for (int p : prices) {
            cheapest = Math.min(cheapest, p);
            best = Math.max(best, p - cheapest);
        }
        return best;
    }

    /** Longest Substring Without Repeating Characters: jump left past the previous copy of a repeated letter. */
    static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> lastSeen = new HashMap<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            Integer previous = lastSeen.get(c);
            if (previous != null && previous >= left) left = previous + 1;   // the window must not hold two c's
            lastSeen.put(c, right);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    /** Longest Repeating Character Replacement: a window is valid if (length - most frequent letter) <= k. */
    static int characterReplacement(String s, int k) {
        int[] count = new int[26];
        int left = 0, maxFreq = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            maxFreq = Math.max(maxFreq, ++count[s.charAt(right) - 'A']);
            while ((right - left + 1) - maxFreq > k) {                       // too many letters to replace
                count[s.charAt(left++) - 'A']--;
            }
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    /** Permutation in String: a fixed window of s1's length whose letter counts equal s1's. */
    static boolean checkInclusion(String s1, String s2) {
        if (s1.length() > s2.length()) return false;
        int[] need = new int[26], have = new int[26];
        for (int i = 0; i < s1.length(); i++) {
            need[s1.charAt(i) - 'a']++;
            have[s2.charAt(i) - 'a']++;
        }
        if (Arrays.equals(need, have)) return true;
        for (int right = s1.length(); right < s2.length(); right++) {
            have[s2.charAt(right) - 'a']++;                                  // the letter that enters
            have[s2.charAt(right - s1.length()) - 'a']--;                    // the letter that leaves
            if (Arrays.equals(need, have)) return true;
        }
        return false;
    }

    /** Sliding Window Maximum: a deque of indices whose values are decreasing; the front is the maximum. */
    static int[] maxSlidingWindow(int[] nums, int k) {
        int[] result = new int[nums.length - k + 1];
        Deque<Integer> window = new ArrayDeque<>();
        for (int i = 0; i < nums.length; i++) {
            if (!window.isEmpty() && window.peekFirst() <= i - k) window.pollFirst();       // left the window
            while (!window.isEmpty() && nums[window.peekLast()] <= nums[i]) window.pollLast(); // can never be the max
            window.addLast(i);
            if (i >= k - 1) result[i - k + 1] = nums[window.peekFirst()];
        }
        return result;
    }
}
```

**What to notice.** `characterReplacement` never shrinks `maxFreq` when a letter leaves. That is deliberate: a stale (too large) `maxFreq` can only make the window look *more* valid, and the window only matters when it beats the best length seen, which requires a genuinely larger `maxFreq`. Know this trick, and be ready to explain it.

## Pitfalls and interview angle

- **Shrinking too early or too late.** Longest-window problems shrink only when invalid; shortest-window problems shrink while still valid.
- **Updating the answer in the wrong place.** Record it after the shrink loop for "longest", inside it for "shortest".
- **Negative numbers** break "sum >= target" windows, because shrinking no longer reduces the sum monotonically. Use prefix sums and a map or deque instead.
- **Counting with `HashMap<Character,Integer>`** in a hot loop is slower than `int[26]`; and `map.get(c) == map2.get(c)` compares `Integer` references.

!interview Interview angle: How is the sliding window different from two pointers? :: Two pointers is the general idea of two indices moving through the data. A sliding window is the case where the two pointers delimit a contiguous range and you maintain a summary of what is inside it. Both are O(n) because each pointer only moves forward.

!keypoints A window `[left, right]` grows on the right and shrinks on the left, O(n) overall ;; Fixed windows add one and remove one; variable windows shrink while the rule is broken ;; Longest: record after shrinking; shortest: record while shrinking ;; Use `int[26]` for letters and a deque of indices for window maximum ;; Negative numbers break sum-based windows

?? Why is the sliding window solution O(n) although it has a `while` inside a `for`?
=> `left` only moves forward and never past `right`, so across the whole run it moves at most n steps in total. Each element enters and leaves the window once.

?? What does the deque hold in Sliding Window Maximum, and why is it decreasing?
=> Indices of candidates for the maximum, with decreasing values. A smaller element before a newer larger one can never be the maximum of any later window, so it is removed from the back; the front is the current maximum.

?? Why can't you use a sliding window to find the shortest subarray with sum at least k when the array has negative numbers?
=> Adding an element no longer always increases the sum and removing one no longer always decreases it, so there is no monotone rule telling you which end to move.
