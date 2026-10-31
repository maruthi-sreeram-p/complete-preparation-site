@part greedy | Greedy | advanced
## The idea

A greedy algorithm makes the choice that looks best **right now** and never reconsiders it. It is fast (usually O(n) or O(n log n)) and short to code, but it is only correct when a *local* best choice is guaranteed to be part of a *global* best answer. Proving that is the real work.

Two arguments justify a greedy choice:

- **Greedy stays ahead.** After every step, the greedy solution is at least as good as any other solution at that step (Jump Game: the farthest reachable index).
- **Exchange argument.** Take any optimal solution and swap its first choice for the greedy choice; the result is no worse (interval scheduling by earliest end).

!tip Signal words :: "minimum number of ...", "maximum ... possible", "can you reach", "schedule", "partition so that", where sorting or a running best would work. If you cannot explain *why* the greedy choice is safe, test it against a counterexample before trusting it.

| Problem | Greedy choice | Why it is safe |
|---|---|---|
| Jump Game | Track the farthest reachable index | If you can reach i, you can reach everything before i too |
| Jump Game II | Jump only when you reach the end of the current range | Each jump extends the range as far as possible |
| Gas Station | If the tank goes negative, restart after that station | No station in between can be a valid start |
| Partition Labels | End a part at the last occurrence of every letter seen | A part must contain all copies of its letters |
| Maximum Subarray (Kadane) | Drop the running sum when it becomes negative | A negative prefix only hurts any later subarray |
| Hand of Straights | Always start a group from the smallest remaining card | The smallest card can only start a group |

!warning Greedy is tempting and often wrong :: Coin change with coins {1, 3, 4} and amount 6: greedy takes 4 + 1 + 1 (three coins); the best is 3 + 3 (two). When the greedy choice cannot be proved, the problem needs DP.

## The Java toolkit and templates

```java GreedyTemplates.java
import java.util.*;

public class GreedyTemplates {

    /** Jump Game: keep the farthest index reachable so far; if you stand beyond it, you are stuck. */
    static boolean canJump(int[] nums) {
        int farthest = 0;
        for (int i = 0; i < nums.length; i++) {
            if (i > farthest) return false;
            farthest = Math.max(farthest, i + nums[i]);
        }
        return true;
    }

    /** Jump Game II: a "level" is the range reachable with the current number of jumps (like BFS levels). */
    static int jump(int[] nums) {
        int jumps = 0, levelEnd = 0, farthest = 0;
        for (int i = 0; i < nums.length - 1; i++) {
            farthest = Math.max(farthest, i + nums[i]);
            if (i == levelEnd) {                         // must jump now to go further
                jumps++;
                levelEnd = farthest;
            }
        }
        return jumps;
    }

    /** Maximum Subarray (Kadane): extend the running sum, or restart if it has become a burden. */
    static int maxSubArray(int[] nums) {
        int current = nums[0], best = nums[0];
        for (int i = 1; i < nums.length; i++) {
            current = Math.max(nums[i], current + nums[i]);
            best = Math.max(best, current);
        }
        return best;
    }

    /** Gas Station: if total gas >= total cost a solution exists, and it starts right after the last failure. */
    static int canCompleteCircuit(int[] gas, int[] cost) {
        int total = 0, tank = 0, start = 0;
        for (int i = 0; i < gas.length; i++) {
            int gain = gas[i] - cost[i];
            total += gain;
            tank += gain;
            if (tank < 0) {                              // cannot get past station i from the current start
                start = i + 1;
                tank = 0;
            }
        }
        return total >= 0 ? start : -1;
    }

    /** Partition Labels: extend the current part to the last occurrence of every letter inside it. */
    static List<Integer> partitionLabels(String s) {
        int[] last = new int[26];
        for (int i = 0; i < s.length(); i++) last[s.charAt(i) - 'a'] = i;
        List<Integer> sizes = new ArrayList<>();
        int start = 0, end = 0;
        for (int i = 0; i < s.length(); i++) {
            end = Math.max(end, last[s.charAt(i) - 'a']);
            if (i == end) {
                sizes.add(end - start + 1);
                start = i + 1;
            }
        }
        return sizes;
    }

    /** Hand of Straights: repeatedly start a group at the smallest remaining card. */
    static boolean isNStraightHand(int[] hand, int groupSize) {
        if (hand.length % groupSize != 0) return false;
        TreeMap<Integer, Integer> counts = new TreeMap<>();
        for (int card : hand) counts.merge(card, 1, Integer::sum);
        while (!counts.isEmpty()) {
            int first = counts.firstKey();
            for (int card = first; card < first + groupSize; card++) {
                Integer have = counts.get(card);
                if (have == null) return false;
                if (have == 1) counts.remove(card);
                else counts.put(card, have - 1);
            }
        }
        return true;
    }
}
```

**What to notice.** Each method is a single pass with a few variables. The hard part of each is the one-sentence **reason** the choice is safe; practise saying it out loud, because that is what an interviewer asks for after the code.

## Pitfalls and interview angle

- **Assuming greedy works** without a proof or a counterexample search. Try small inputs by hand.
- **Sorting by the wrong criterion** in scheduling problems (earliest end, not earliest start or shortest).
- **Forgetting the global feasibility check**, such as `total >= 0` in Gas Station.
- **Off-by-one in loops** such as `i < nums.length - 1` in Jump Game II: you do not need to jump from the last index.
- **Greedy versus DP confusion.** If choices interact (taking one item changes what else is possible in complicated ways), use DP.

!interview Interview angle: How do you prove a greedy algorithm correct? :: Either show the greedy solution stays ahead of any other solution after every step, or use an exchange argument: take any optimal solution, replace its first choice with the greedy choice, and show the result is still optimal. If you cannot find such an argument, look for a counterexample or switch to DP.

!keypoints Greedy takes the locally best choice and never revisits it ;; It is correct only when the local choice is part of a global optimum: be ready to say why ;; "Stays ahead" and exchange arguments are the two standard proofs ;; Sorting by the right key is half the problem in scheduling tasks ;; Coin change with arbitrary coins is the classic case where greedy fails ;; When in doubt, test small cases or fall back to DP

?? Why is Kadane's algorithm greedy?
=> It decides at each element whether to extend the current subarray or start fresh, keeping the running sum only while it helps. A negative running sum can only reduce any later subarray, so discarding it is always safe.

?? Why does restarting after a failure work in Gas Station?
=> If you cannot reach station j starting from i, you cannot reach it from any station between i and j either, because each of them would arrive at j with no more gas than the run from i did. So the next candidate start is j.

?? Give an example where greedy fails.
=> Coin change with coins {1, 3, 4} and amount 6. Greedy picks 4 + 1 + 1 (three coins), but 3 + 3 uses two. A DP over amounts finds the minimum.
