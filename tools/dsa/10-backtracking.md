@part backtracking | Backtracking | trees
## The idea

Backtracking builds a solution one decision at a time and **undoes** a decision when it leads nowhere. It is brute force with a safety net: you explore a tree of choices depth-first, and you cut off a branch as soon as it cannot lead to a valid answer.

Every backtracking solution has the same three steps, often called **choose, explore, un-choose**:

1. **Choose** one of the available options and add it to the current partial solution.
2. **Explore** by recursing with the new state.
3. **Un-choose** by removing the option, so the next option starts from a clean state.

The base case records a finished solution (or reaches a dead end). Time is exponential (2ⁿ for subsets, n! for permutations), so the practical skill is **pruning**: stop early when the partial solution already violates a rule.

| Problem family | What the choices are | Duplicate handling |
|---|---|---|
| Subsets, Combinations | Include or skip elements, moving forward only (a `start` index) | Sort, then skip equal neighbours at the same level |
| Permutations | Pick any unused element for the next position | A `used[]` array |
| Combination Sum | Reuse an element (recurse with `i`, not `i + 1`) | Sort and stop when the candidate exceeds the remaining target |
| Grid and string search | Move to a neighbouring cell or split the string | Mark visited, unmark on return |
| N-Queens, Sudoku | Place a piece in a column | Track used columns and diagonals in sets |

!tip Signal words :: "all possible", "generate all", "every combination", "partition", "place so that no two", "find a path in a grid". If the input is small (n ≤ 20) and you must list all answers, backtracking is intended.

## The Java toolkit and templates

!warning Copy the path before you store it :: `result.add(path)` stores a *reference* to the list you keep modifying, so all stored answers end up identical (or empty). Always `result.add(new ArrayList<>(path))`.

```java BacktrackingTemplates.java
import java.util.*;

public class BacktrackingTemplates {

    /** Subsets: every element is either in or out. Moving forward only (start) avoids duplicates. */
    static List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        build(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private static void build(int[] nums, int start, List<Integer> path, List<List<Integer>> result) {
        result.add(new ArrayList<>(path));                  // every path is itself a subset
        for (int i = start; i < nums.length; i++) {
            path.add(nums[i]);                              // choose
            build(nums, i + 1, path, result);               // explore
            path.remove(path.size() - 1);                   // un-choose
        }
    }

    /** Subsets II (with duplicates): sort, then skip an equal value at the same depth. */
    static List<List<Integer>> subsetsWithDup(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> result = new ArrayList<>();
        buildDistinct(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private static void buildDistinct(int[] nums, int start, List<Integer> path, List<List<Integer>> result) {
        result.add(new ArrayList<>(path));
        for (int i = start; i < nums.length; i++) {
            if (i > start && nums[i] == nums[i - 1]) continue;   // same choice at this level: skip
            path.add(nums[i]);
            buildDistinct(nums, i + 1, path, result);
            path.remove(path.size() - 1);
        }
    }

    /** Permutations: any unused element can go next. */
    static List<List<Integer>> permutations(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        permute(nums, new boolean[nums.length], new ArrayList<>(), result);
        return result;
    }

    private static void permute(int[] nums, boolean[] used, List<Integer> path, List<List<Integer>> result) {
        if (path.size() == nums.length) {
            result.add(new ArrayList<>(path));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            used[i] = true;
            path.add(nums[i]);
            permute(nums, used, path, result);
            path.remove(path.size() - 1);
            used[i] = false;
        }
    }

    /** Combination Sum: candidates may be reused, so recurse with i (not i + 1). Sorting enables pruning. */
    static List<List<Integer>> combinationSum(int[] candidates, int target) {
        Arrays.sort(candidates);
        List<List<Integer>> result = new ArrayList<>();
        sum(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }

    private static void sum(int[] c, int remaining, int start, List<Integer> path, List<List<Integer>> result) {
        if (remaining == 0) {
            result.add(new ArrayList<>(path));
            return;
        }
        for (int i = start; i < c.length && c[i] <= remaining; i++) {   // c[i] > remaining: later ones are bigger too
            path.add(c[i]);
            sum(c, remaining - c[i], i, path, result);
            path.remove(path.size() - 1);
        }
    }

    /** Word Search: mark the cell as used while exploring, restore it afterwards. */
    static boolean exist(char[][] board, String word) {
        for (int r = 0; r < board.length; r++)
            for (int c = 0; c < board[0].length; c++)
                if (search(board, word, 0, r, c)) return true;
        return false;
    }

    private static boolean search(char[][] b, String word, int i, int r, int c) {
        if (i == word.length()) return true;
        if (r < 0 || c < 0 || r >= b.length || c >= b[0].length || b[r][c] != word.charAt(i)) return false;
        char saved = b[r][c];
        b[r][c] = '#';                                      // choose: cannot be reused on this path
        boolean found = search(b, word, i + 1, r + 1, c) || search(b, word, i + 1, r - 1, c)
                || search(b, word, i + 1, r, c + 1) || search(b, word, i + 1, r, c - 1);
        b[r][c] = saved;                                    // un-choose
        return found;
    }

    /** N-Queens count: columns and both diagonals are tracked in sets, so each placement check is O(1). */
    static int totalNQueens(int n) {
        return place(0, n, new HashSet<>(), new HashSet<>(), new HashSet<>());
    }

    private static int place(int row, int n, Set<Integer> cols, Set<Integer> diag, Set<Integer> anti) {
        if (row == n) return 1;
        int count = 0;
        for (int col = 0; col < n; col++) {
            if (cols.contains(col) || diag.contains(row - col) || anti.contains(row + col)) continue;
            cols.add(col); diag.add(row - col); anti.add(row + col);
            count += place(row + 1, n, cols, diag, anti);
            cols.remove(col); diag.remove(row - col); anti.remove(row + col);
        }
        return count;
    }
}
```

**What to notice.** The `i > start` (not `i > 0`) in `buildDistinct` is the subtle part: equal values may both appear *along one path* (`[1, 1]`), but the same value may not start two different branches *at the same level*, which would produce duplicate subsets.

## Pitfalls and interview angle

- **Storing the live list** instead of a copy.
- **Forgetting to undo** every change (`path`, `used`, board cells, sets). A bug usually shows up as missing answers.
- **Duplicate answers** with repeated input values: sort and skip, as above.
- **Not pruning.** Exponential algorithms need early exits (`c[i] <= remaining`, conflict checks) or they time out.
- **Complexity answers**: subsets O(n · 2ⁿ), permutations O(n · n!). The factor n is the cost of copying each answer.

!interview Interview angle: What is the difference between backtracking and plain recursion or DFS? :: Backtracking is DFS over a tree of *partial solutions* with an explicit undo step and pruning. Plain DFS usually visits an existing structure (a tree or graph). The state you modify while exploring is restored on the way back, so the same buffers can be reused for every branch.

!keypoints Choose, explore, un-choose: the undo step is what makes it backtracking ;; Add a copy of the path to the results, never the live list ;; Subsets and combinations move forward with `start`; permutations use `used[]` ;; Sort and skip equal neighbours (`i > start`) to avoid duplicate answers ;; Prune as soon as a partial solution cannot succeed ;; Worst-case time is exponential: O(n·2ⁿ) for subsets, O(n·n!) for permutations

?? Why do all the lists in my result look the same (or empty) at the end?
=> The same `path` list is added to the result every time and then modified. Add `new ArrayList<>(path)` so each result is an independent snapshot.

?? How do you avoid duplicate subsets when the input contains repeated numbers?
=> Sort the array and skip `nums[i]` when `i > start && nums[i] == nums[i - 1]`. This prevents the same value from starting two different branches at the same level while still allowing it along one path.

?? How does pruning change the running time of Combination Sum?
=> Sorting the candidates and stopping the loop when a candidate exceeds the remaining target cuts off whole subtrees of the search. The worst case remains exponential, but many inputs finish far faster.
