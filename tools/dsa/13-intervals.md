@part intervals | Intervals | advanced
## The idea

An interval is a pair `[start, end]`: a meeting, a booking, a range of IDs. Problems ask you to merge overlapping ranges, insert a new one, count how many are active at once, or remove the fewest so that none overlap. They share one move: **sort first**, then sweep once.

Two intervals `a` and `b` (with `a.start <= b.start`) **overlap** when `b.start <= a.end`. Drawing the number line and thinking about the three cases (completely before, overlapping, completely after) removes most mistakes.

| Task | Sort by | Sweep with |
|---|---|---|
| Merge Intervals | start | Compare each interval with the last merged one |
| Insert Interval | already sorted | Add everything before, merge the overlapping ones, add everything after |
| Non-overlapping Intervals (remove the fewest) | **end** | Keep the interval that ends earliest; count the ones that start before the last kept end |
| Meeting Rooms II (how many rooms) | start | A min-heap of end times, or two sorted arrays of starts and ends |
| Minimum Interval to Include Each Query | intervals by start, queries ascending | A min-heap keyed by interval size |

!tip Signal words :: "meetings", "overlap", "merge ranges", "calendar", "minimum number to remove", "how many at the same time". The answer to "fewest to remove so none overlap" is the same as "most you can keep", which is a **greedy by earliest end** problem.

## The Java toolkit and templates

Sort with a comparator, and prefer `Integer.compare(a[0], b[0])` over subtraction to avoid overflow.

```java Intervals.java
import java.util.*;

public class Intervals {

    /** Merge Intervals: after sorting by start, an interval either extends the last merged one or starts a new one. */
    static int[][] merge(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> merged = new ArrayList<>();
        for (int[] current : intervals) {
            if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < current[0]) {
                merged.add(current);                                   // a gap: start a new group
            } else {
                int[] last = merged.get(merged.size() - 1);
                last[1] = Math.max(last[1], current[1]);               // overlap: extend the end
            }
        }
        return merged.toArray(new int[0][]);
    }

    /** Insert Interval into a sorted, non-overlapping list in one pass. */
    static int[][] insert(int[][] intervals, int[] added) {
        List<int[]> result = new ArrayList<>();
        int i = 0;
        while (i < intervals.length && intervals[i][1] < added[0]) result.add(intervals[i++]);   // entirely before
        while (i < intervals.length && intervals[i][0] <= added[1]) {                             // overlapping
            added[0] = Math.min(added[0], intervals[i][0]);
            added[1] = Math.max(added[1], intervals[i][1]);
            i++;
        }
        result.add(added);
        while (i < intervals.length) result.add(intervals[i++]);                                  // entirely after
        return result.toArray(new int[0][]);
    }

    /** Non-overlapping Intervals: keep the interval that ends first; every interval that starts earlier is removed. */
    static int eraseOverlapIntervals(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));   // by END
        int removed = 0;
        int lastEnd = Integer.MIN_VALUE;
        for (int[] interval : intervals) {
            if (interval[0] >= lastEnd) lastEnd = interval[1];           // fits after the last kept one
            else removed++;                                              // overlaps: drop it
        }
        return removed;
    }

    /** Meeting Rooms II: the heap holds the end times of the rooms in use; reuse a room that has become free. */
    static int minMeetingRooms(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        PriorityQueue<Integer> endTimes = new PriorityQueue<>();
        for (int[] meeting : intervals) {
            if (!endTimes.isEmpty() && endTimes.peek() <= meeting[0]) endTimes.poll();   // reuse the earliest-ending room
            endTimes.offer(meeting[1]);
        }
        return endTimes.size();
    }

    /** Meeting Rooms: can one person attend all meetings? Sorted, no meeting may start before the previous ends. */
    static boolean canAttendAll(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] < intervals[i - 1][1]) return false;
        }
        return true;
    }
}
```

**What to notice.** `merge` compares with `<` so that `[1,2]` and `[2,3]` merge; whether touching intervals should merge is a requirement to **ask about**. In `minMeetingRooms` the heap size at the end equals the peak number of overlapping meetings, because a room is only added when no existing room is free.

## Pitfalls and interview angle

- **Sorting by the wrong key.** Merging needs start order; "keep the most" needs end order.
- **Mutating the input** (`last[1] = ...`) changes the caller's arrays. It is fine if allowed; say so, or copy.
- **Touching endpoints.** Decide whether `[1,2]` and `[2,3]` overlap and use `<` or `<=` consistently.
- **Subtraction in comparators** (`a[0] - b[0]`) can overflow.
- **Insert Interval** is O(n) because the input is already sorted; do not sort again.

!interview Interview angle: Why does sorting by end time give the maximum number of non-overlapping intervals? :: Choosing the interval that finishes earliest leaves the most room for everything after it. Any optimal solution can be transformed, by swapping its first interval for the earliest-ending one, without losing any interval, so the greedy choice is safe. Sorting by start would let one very long interval block many short ones.

!keypoints Sort first, then sweep once: O(n log n) ;; Sort by start to merge; sort by end to keep the most intervals ;; Two intervals overlap when the later one starts at or before the earlier one ends ;; A min-heap of end times counts rooms or concurrent meetings ;; Ask whether touching endpoints overlap ;; Use `Integer.compare` in comparators

?? How do you decide whether two intervals overlap?
=> After ordering them by start, interval b overlaps a when `b.start <= a.end` (or `<` if touching endpoints do not count). Otherwise there is a gap.

?? Why does Meeting Rooms II use a min-heap of end times?
=> The heap's top is the room that frees up first. If the next meeting starts after that time, the room is reused; otherwise a new room is needed. The final heap size is the number of rooms.

?? What is the time complexity of Merge Intervals?
=> O(n log n) for the sort plus O(n) for the sweep, so O(n log n) overall, with O(n) space for the output.
