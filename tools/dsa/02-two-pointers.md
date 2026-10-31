@part two-pointers | Two Pointers | foundations
## The idea

Instead of two nested loops that try every pair, keep **two indices** and move them according to a rule, so that each index only travels once through the data. The work drops from O(n²) to O(n).

There are two shapes:

- **Opposite ends.** One pointer at the start, one at the end, moving towards each other. It works when the data is **sorted** (or has a monotone property) so that moving a pointer in a direction has a predictable effect: Two Sum II, 3Sum, Container With Most Water, palindrome checks.
- **Same direction (fast and slow).** Both pointers start at the left; one reads ahead while the other marks where to write. It is used to compact or partition an array in place, and to detect cycles in linked lists.

!tip Signal words :: "sorted array", "pair or triplet that sums to", "in place", "without extra space", "palindrome", "remove duplicates".

The reasoning behind opposite-end pointers is a **discard argument**: when the sum is too small, the smaller element can never be part of *any* valid pair with the remaining elements, so you drop it safely. Being able to say that sentence is what interviewers listen for.

## The Java toolkit and templates

```java TwoPointers.java
import java.util.*;

public class TwoPointers {

    /** Valid Palindrome: skip non-alphanumeric characters from both ends. */
    static boolean isPalindrome(String s) {
        int l = 0, r = s.length() - 1;
        while (l < r) {
            while (l < r && !Character.isLetterOrDigit(s.charAt(l))) l++;
            while (l < r && !Character.isLetterOrDigit(s.charAt(r))) r--;
            if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return false;
            l++;
            r--;
        }
        return true;
    }

    /** 3Sum: fix one number, then run Two Sum II on the rest. Sort first and skip duplicates. */
    static List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> out = new ArrayList<>();
        for (int i = 0; i < nums.length - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue;       // same first number: same triplets
            int l = i + 1, r = nums.length - 1;
            while (l < r) {
                int sum = nums[i] + nums[l] + nums[r];
                if (sum < 0) l++;
                else if (sum > 0) r--;
                else {
                    out.add(List.of(nums[i], nums[l], nums[r]));
                    l++;
                    r--;
                    while (l < r && nums[l] == nums[l - 1]) l++;  // skip repeated second numbers
                }
            }
        }
        return out;
    }

    /** Container With Most Water: the shorter wall limits the area, so move it. */
    static int maxArea(int[] height) {
        int l = 0, r = height.length - 1, best = 0;
        while (l < r) {
            best = Math.max(best, Math.min(height[l], height[r]) * (r - l));
            if (height[l] < height[r]) l++;
            else r--;
        }
        return best;
    }

    /** Trapping Rain Water: water above a bar is limited by the lower of the best wall on each side. */
    static int trap(int[] height) {
        int l = 0, r = height.length - 1, leftMax = 0, rightMax = 0, water = 0;
        while (l < r) {
            if (height[l] < height[r]) {
                leftMax = Math.max(leftMax, height[l]);
                water += leftMax - height[l++];
            } else {
                rightMax = Math.max(rightMax, height[r]);
                water += rightMax - height[r--];
            }
        }
        return water;
    }

    /** Same direction: remove duplicates from a sorted array in place; returns the new length. */
    static int removeDuplicates(int[] nums) {
        if (nums.length == 0) return 0;
        int write = 1;
        for (int read = 1; read < nums.length; read++) {
            if (nums[read] != nums[write - 1]) nums[write++] = nums[read];
        }
        return write;
    }
}
```

**What to notice.** In `threeSum`, sorting costs O(n log n) and the double loop O(n²), so the total is O(n²): the best known for the problem. In `trap`, only the side with the *lower* wall is processed, because that side's water level is already decided by its own maximum.

## Pitfalls and interview angle

- **Unsorted input.** Opposite-end pointers need order. If the array is unsorted and you must return indices (Two Sum), use a hash map instead, because sorting loses the original positions.
- **Duplicates in 3Sum.** Skip repeated values for *every* position, or the same triplet appears many times.
- **`l < r` versus `l <= r`.** Use `<` when the two pointers must be different elements.
- **Off-by-one on the inner `while`s** that skip characters: always re-check `l < r`.

!interview Interview angle: How do you justify moving the shorter wall in Container With Most Water? :: The area is limited by the shorter wall times the distance. Moving the taller wall inward can only reduce the distance and cannot raise the limiting height, so it can never beat the current area. Moving the shorter wall is the only move that might improve it, so you may discard the shorter wall for good.

!keypoints Two pointers turn O(n²) pair searches into one O(n) pass ;; Opposite ends need sorted data or a monotone property; same direction compacts or partitions in place ;; Justify each move with a discard argument ;; Sort and skip duplicates for 3Sum ;; Use a hash map, not pointers, when you need original indices from unsorted data

?? Why does Two Sum II work with two pointers but plain Two Sum does not?
=> Two Sum II gives a sorted array, so a sum that is too small means the left element is too small for every remaining partner and a too-large sum means the right one is too big. Plain Two Sum is unsorted, and sorting would lose the indices, so a hash map is the right tool.

?? What is the time and space complexity of 3Sum with sorting and two pointers?
=> O(n²) time (sorting O(n log n) plus n iterations of an O(n) scan) and O(1) extra space apart from the output and sorting.

?? What does the slow pointer represent when removing duplicates in place?
=> The next position to write: everything before it is the compacted result, and the fast pointer reads ahead looking for the next different value.
