@part stack | Stack | foundations
## The idea

A **stack** is last-in, first-out: the most recent thing you saw is the first thing you deal with. It appears whenever the problem has *nesting* (brackets, expressions, function calls) or when you need to find, for every element, the *nearest* element to its left or right that is bigger or smaller.

Two families cover almost all stack problems:

1. **Matching and evaluation.** Push openers or operands, pop when you meet the closer or operator: valid parentheses, reverse Polish notation, min stack.
2. **Monotonic stack.** Keep the stack ordered (always increasing or always decreasing). When a new element breaks the order, pop until it fits; every popped element has just found its "next greater" (or smaller) answer. Daily temperatures, largest rectangle in a histogram, car fleet.

!tip Signal words :: "valid", "nested", "undo", "next greater element", "previous smaller", "span", "histogram".

A monotonic stack looks like a nested loop but each element is pushed once and popped once, so the whole pass is **O(n)**.

## The Java toolkit and templates

!warning Do not use `java.util.Stack` :: It extends `Vector`, so every method is synchronized and it exposes list methods that break the stack idea. Use `Deque<Integer> stack = new ArrayDeque<>()` with `push`, `pop` and `peek`. (`ArrayDeque` does not allow `null` elements, which is also what you want.)

```java StackTemplates.java
import java.util.*;

public class StackTemplates {

    /** Valid Parentheses: every closer must match the most recent opener. */
    static boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            } else {
                if (stack.isEmpty()) return false;
                char open = stack.pop();
                if ((c == ')' && open != '(') || (c == ']' && open != '[') || (c == '}' && open != '{')) return false;
            }
        }
        return stack.isEmpty();
    }

    /** Daily Temperatures: monotonic stack of indices whose temperatures are still waiting for a warmer day. */
    static int[] dailyTemperatures(int[] temps) {
        int[] wait = new int[temps.length];
        Deque<Integer> waiting = new ArrayDeque<>();
        for (int i = 0; i < temps.length; i++) {
            while (!waiting.isEmpty() && temps[i] > temps[waiting.peek()]) {
                int colder = waiting.pop();
                wait[colder] = i - colder;                       // i is the next warmer day
            }
            waiting.push(i);
        }
        return wait;
    }

    /** Largest Rectangle in Histogram: when a bar is lower than the stack top, the top's rectangle is finished. */
    static int largestRectangle(int[] heights) {
        Deque<Integer> stack = new ArrayDeque<>();               // indices of increasing heights
        int best = 0;
        for (int i = 0; i <= heights.length; i++) {
            int current = i == heights.length ? 0 : heights[i];  // a final bar of height 0 flushes the stack
            while (!stack.isEmpty() && current < heights[stack.peek()]) {
                int height = heights[stack.pop()];
                int left = stack.isEmpty() ? -1 : stack.peek();  // nearest lower bar to the left
                best = Math.max(best, height * (i - left - 1));
            }
            stack.push(i);
        }
        return best;
    }

    /** Evaluate Reverse Polish Notation: operands go on the stack, an operator consumes the top two. */
    static int evalRPN(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();
        for (String t : tokens) {
            switch (t) {
                case "+" -> stack.push(stack.pop() + stack.pop());
                case "*" -> stack.push(stack.pop() * stack.pop());
                case "-" -> { int b = stack.pop(), a = stack.pop(); stack.push(a - b); }
                case "/" -> { int b = stack.pop(), a = stack.pop(); stack.push(a / b); }
                default -> stack.push(Integer.parseInt(t));
            }
        }
        return stack.pop();
    }

    /** Min Stack: every entry remembers the minimum at the time it was pushed. */
    static class MinStack {
        private final Deque<int[]> stack = new ArrayDeque<>();   // {value, minSoFar}
        void push(int x) { stack.push(new int[] { x, stack.isEmpty() ? x : Math.min(x, stack.peek()[1]) }); }
        void pop() { stack.pop(); }
        int top() { return stack.peek()[0]; }
        int getMin() { return stack.peek()[1]; }
    }
}
```

**What to notice.** The stacks hold **indices**, not values, whenever the answer needs a distance or a width. The sentinel bar of height 0 at the end of the histogram avoids a second loop to empty the stack.

## Pitfalls and interview angle

- **Popping an empty stack** throws `NoSuchElementException` with `ArrayDeque`. Check `isEmpty()` first.
- **Order of operands** for `-` and `/` in RPN: the *second* popped value is the left operand.
- **`peek()` returns null** (not an exception) on an empty `ArrayDeque`; unboxing that `null` to `int` throws `NullPointerException`.
- **Strict versus non-strict comparison** in a monotonic stack decides how equal values behave. Decide it on purpose and test with duplicates.

!interview Interview angle: Why is a monotonic stack O(n) even though there is a `while` loop inside a `for` loop? :: Each index is pushed exactly once and popped at most once. The inner loop's total iterations across the whole run are therefore at most n, so the total work is O(n), not O(n²).

!keypoints Use a stack for nesting and for nearest greater or smaller element problems ;; Use `ArrayDeque`, never `java.util.Stack` ;; A monotonic stack pops until the order is restored; each pop is an answer found ;; Store indices when you need distances or widths ;; Each element is pushed and popped once, so monotonic stack solutions are O(n)

?? Which data structure would you use for "next greater element" and why?
=> A monotonic (decreasing) stack. Elements wait on the stack until a larger element arrives, and when it does, everything smaller is popped and gets that element as its answer. One pass, O(n).

?? How do you get the minimum of a stack in O(1)?
=> Store with each pushed value the minimum so far (or keep a second stack of minimums). Pop removes both, so `getMin` always reads the top.

?? Why is a sentinel useful at the end of the histogram algorithm?
=> Processing a bar of height 0 after the last real bar forces every remaining bar off the stack, so their rectangles are counted without extra code.
