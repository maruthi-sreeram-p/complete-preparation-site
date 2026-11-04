@part py-dsa-3 | DSA Patterns in Python · Part 3: Linked Lists, Stacks and Queues | dsa
## Linked List Basics, the Dummy Node and Reversal

A **singly linked list** is a chain of nodes, each holding a value and a reference to the next. Unlike an array you cannot jump to index i; in exchange, inserting or removing **at a node you already hold** is O(1). Interview problems are about **pointer manipulation without losing the rest of the list**.

Three techniques cover most problems:

1. **Dummy (sentinel) node.** Put a fake node before the head so inserting or deleting the first node needs no special case: `dummy = ListNode(0, head)`, work with `dummy`, return `dummy.next`.
2. **Reversal.** Walk with `prev` and `cur`; before pointing `cur.next` backwards, remember the next node.
3. **Two pointers.** A gap of n nodes between two pointers finds the n-th from the end; different speeds find the middle or a cycle.

```python ListBasics.py
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def build(values):
    dummy = cur = ListNode()
    for v in values:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def values(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def reverse_list(head):
    prev, cur = None, head
    while cur:
        cur.next, prev, cur = prev, cur, cur.next     # remember next, point backwards, advance both
    return prev


def reverse_recursive(head):
    if not head or not head.next:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head                              # the node after head now points back at head
    head.next = None
    return new_head


def merge_two_lists(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b                                 # append whichever list still has nodes
    return dummy.next


def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):                             # open a gap of n nodes between the pointers
        fast = fast.next
    while fast:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next                         # slow stands just before the node to delete
    return dummy.next


def add_two_numbers(a, b):                             # digits stored in reverse order
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        total = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        a, b = a.next if a else None, b.next if b else None
    return dummy.next


def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next                      # fewer than k nodes remain: leave them as they are
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            cur.next, prev, cur = prev, cur, cur.next
        group_prev.next, group_prev = kth, group_prev.next


assert values(reverse_list(build([1, 2, 3, 4]))) == [4, 3, 2, 1] and reverse_list(None) is None
assert values(reverse_recursive(build([1, 2, 3]))) == [3, 2, 1]
assert values(merge_two_lists(build([1, 2, 4]), build([1, 3, 4]))) == [1, 1, 2, 3, 4, 4] and values(merge_two_lists(None, build([0]))) == [0]
assert values(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5] and values(remove_nth_from_end(build([1]), 1)) == []
assert values(add_two_numbers(build([2, 4, 3]), build([5, 6, 4]))) == [7, 0, 8] and values(add_two_numbers(build([9, 9]), build([1]))) == [0, 0, 1]
assert values(reverse_k_group(build([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5] and values(reverse_k_group(build([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
print("linked lists ok")
```

```output
```

The tuple assignment `cur.next, prev, cur = prev, cur, cur.next` evaluates the whole right side first, so it is a safe three-way move; writing the same as three separate statements in the wrong order loses the rest of the list.

!tip Draw the pointers :: Before coding any list problem, draw three nodes and the arrows, and mark which pointer changes in which order. Most bugs are a pointer overwritten before its old value was saved, or forgetting to terminate the new tail with `None` (which creates a cycle).

??  Why use a dummy node?
=> It removes the special case where the head itself is inserted, deleted or reassigned: the operation always works on `prev.next`, and the answer is `dummy.next`. It makes list code shorter and less error-prone.
??  How do you find the n-th node from the end in one pass?
=> Advance a fast pointer n steps ahead of a slow pointer, then move both until fast reaches the end; slow is then n nodes from the end (use a dummy node so deleting the head works).
??  Iterative or recursive reversal?
=> Iterative is O(1) space. Recursive reversal is elegant but uses O(n) call stack and can hit Python's recursion limit on long lists. Be able to write both, and say which you would ship.

## Fast and Slow Pointers

**Idea.** Two pointers moving at different speeds (slow by 1, fast by 2) meet if there is a cycle; when fast reaches the end, slow is at the **middle**. The same Floyd cycle-detection idea finds duplicates in an array treated as a linked structure.

```python FastSlow.py
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def build(values, cycle_at=None):
    nodes = [ListNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if cycle_at is not None:
        nodes[-1].next = nodes[cycle_at]
    return nodes[0] if nodes else None


def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def cycle_start(head):
    """After they meet, a pointer from the head and one from the meeting point, moving one step at a time, meet at the cycle start."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None


def middle_node(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow                                         # the second middle for even lengths


def is_palindrome_list(head):
    slow = fast = head
    while fast and fast.next:                           # 1. find the middle
        slow, fast = slow.next, fast.next.next
    prev = None
    while slow:                                         # 2. reverse the second half
        slow.next, prev, slow = prev, slow, slow.next
    left, right = head, prev
    while right:                                        # 3. compare the halves
        if left.val != right.val:
            return False
        left, right = left.next, right.next
    return True


def find_duplicate(nums):
    """Values 1..n in n+1 slots: treat i -> nums[i] as a linked list that must contain a cycle."""
    slow = fast = nums[0]
    while True:
        slow, fast = nums[slow], nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow, fast = nums[slow], nums[fast]
    return slow


def is_happy(n):
    def step(x):
        return sum(int(d) ** 2 for d in str(x))
    slow, fast = n, step(n)
    while fast != 1 and slow != fast:
        slow, fast = step(slow), step(step(fast))
    return fast == 1


cyclic = build([3, 2, 0, -4], cycle_at=1)
assert has_cycle(cyclic) and not has_cycle(build([1, 2, 3])) and not has_cycle(None)
assert cycle_start(cyclic).val == 2 and cycle_start(build([1, 2])) is None
assert middle_node(build([1, 2, 3, 4, 5])).val == 3 and middle_node(build([1, 2, 3, 4])).val == 3
assert is_palindrome_list(build([1, 2, 2, 1])) and is_palindrome_list(build([1, 2, 3, 2, 1])) and not is_palindrome_list(build([1, 2]))
assert find_duplicate([1, 3, 4, 2, 2]) == 2 and find_duplicate([3, 1, 3, 4, 2]) == 3
assert is_happy(19) and not is_happy(2)
print("fast and slow ok")
```

```output
```

Why the cycle start works: let the head be `a` steps from the cycle start, and the meeting point be `b` steps into the cycle, with cycle length `c`. Fast has travelled twice as far as slow, which gives `a = (c - b) + (k-1)c` for some k, so a pointer from the head and one from the meeting point, both moving at speed 1, arrive at the start together. You do not need to derive it in an interview, but you must be able to state that fast's distance is twice slow's.

??  How does Floyd's algorithm detect a cycle without extra memory?
=> A slow pointer moves one step and a fast pointer two. In a cycle the fast pointer gains one node per step on the slow one, so they must eventually meet; if there is no cycle, fast reaches the end. It uses O(1) space, versus O(n) for a visited set.
??  How is "find the duplicate number" a linked list problem?
=> With values in 1..n in an array of n+1 slots, the mapping `i -> nums[i]` is a function whose graph has a cycle that starts at the duplicate value (two indexes point to it). Floyd's algorithm finds the cycle start without modifying the array or using extra space.

## Stack Patterns

A **stack** is last-in, first-out. Use it when the **most recent unresolved item** matters: matching pairs, undo, nested structures, expression evaluation, and as the explicit version of recursion.

```python StackPatterns.py
class MinStack:
    """push, pop, top and get_min all in O(1): store (value, minimum so far) pairs."""
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append((x, min(x, self.items[-1][1]) if self.items else x))

    def pop(self):
        return self.items.pop()[0]

    def top(self):
        return self.items[-1][0]

    def get_min(self):
        return self.items[-1][1]


def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if token in {"+", "-", "*", "/"}:
            b, a = stack.pop(), stack.pop()               # note the order: a op b
            stack.append(a + b if token == "+" else a - b if token == "-" else a * b if token == "*" else int(a / b))
        else:
            stack.append(int(token))
    return stack[0]


def decode_string(s):
    """'3[a2[c]]' -> 'accaccacc': a stack of (text so far, repeat count)."""
    stack, current, number = [], "", 0
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == "[":
            stack.append((current, number))
            current, number = "", 0
        elif ch == "]":
            previous, repeat = stack.pop()
            current = previous + current * repeat
        else:
            current += ch
    return current


def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)


def calculate(s):                                         # + - and parentheses, using a stack of signs
    stack, result, number, sign = [], 0, 0, 1
    for ch in s + "+":
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-":
            result += sign * number
            number, sign = 0, 1 if ch == "+" else -1
        elif ch == "(":
            stack.append((result, sign))
            result, sign = 0, 1
        elif ch == ")":
            result += sign * number
            number = 0
            previous_result, previous_sign = stack.pop()
            result = previous_result + previous_sign * result
    return result


m = MinStack()
for x in (5, 3, 7, 3, 8):
    m.push(x)
assert (m.get_min(), m.pop(), m.get_min(), m.pop(), m.pop(), m.get_min(), m.top()) == (3, 8, 3, 3, 7, 3, 3)
assert eval_rpn(["2", "1", "+", "3", "*"]) == 9 and eval_rpn(["4", "13", "5", "/", "+"]) == 6
assert decode_string("3[a]2[bc]") == "aaabcbc" and decode_string("3[a2[c]]") == "accaccacc" and decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
assert simplify_path("/home//foo/") == "/home/foo" and simplify_path("/a/./b/../../c/") == "/c" and simplify_path("/../") == "/"
assert calculate("1 + 1") == 2 and calculate("(1+(4+5+2)-3)+(6+8)") == 23 and calculate("2-(5-6)") == 3
print("stacks ok")
```

```output
```

??  When do you reach for a stack?
=> When you must resolve the **most recent** pending item first: matching brackets, parsing nested expressions, undo/redo, DFS without recursion, backtracking history, and "previous greater/smaller element" questions (monotonic stack).
??  How does `MinStack` achieve O(1) `get_min`?
=> Each stack entry stores the value together with the minimum of everything beneath it, so the current minimum is always on top. Popping restores the previous minimum automatically.

## Monotonic Stack

**Idea.** Keep a stack whose values are **monotonic** (always increasing or decreasing). When a new element arrives, pop everything it "resolves", and those pops are exactly where you record answers. Every element is pushed and popped once: O(n).

**Signals.** "Next greater / smaller element", "how many days until a warmer day", "largest rectangle", "span".

```python Monotonic.py
def daily_temperatures(temps):
    answer, stack = [0] * len(temps), []                  # stack of indexes with decreasing temperatures
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            answer[j] = i - j                             # day i is the next warmer day for day j
        stack.append(i)
    return answer


def next_greater_circular(nums):
    n, result, stack = len(nums), [-1] * len(nums), []
    for i in range(2 * n):                                # walk the circle twice
        while stack and nums[stack[-1]] < nums[i % n]:
            result[stack.pop()] = nums[i % n]
        if i < n:
            stack.append(i)
    return result


def largest_rectangle(heights):
    stack, best = [], 0                                   # indexes of bars with increasing heights
    for i, h in enumerate(heights + [0]):                 # a sentinel 0 flushes the stack at the end
        start = i
        while stack and stack[-1][1] > h:
            index, height = stack.pop()
            best = max(best, height * (i - index))        # this bar could extend left to `index`
            start = index
        stack.append((start, h))
    return best


def remove_k_digits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()                                   # a smaller digit later makes the earlier larger one worse
            k -= 1
        stack.append(d)
    stack = stack[:len(stack) - k] if k else stack
    return "".join(stack).lstrip("0") or "0"


class StockSpanner:
    def __init__(self):
        self.stack = []                                   # (price, span)

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert next_greater_circular([1, 2, 1]) == [2, -1, 2] and next_greater_circular([5, 4, 3]) == [-1, 5, 5]
assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10 and largest_rectangle([2, 4]) == 4 and largest_rectangle([1]) == 1
assert remove_k_digits("1432219", 3) == "1219" and remove_k_digits("10200", 1) == "200" and remove_k_digits("10", 2) == "0"
spans = StockSpanner()
assert [spans.next(p) for p in (100, 80, 60, 70, 60, 75, 85)] == [1, 1, 1, 2, 1, 4, 6]
print("monotonic stacks ok")
```

```output
```

!interview Why is the monotonic stack O(n) with a nested `while`? :: Each element is pushed exactly once and popped at most once, so the total number of pops across the whole run is at most n. The inner loop is amortised O(1) per element, the same argument as the sliding window.

??  What does the stack hold in "daily temperatures" and when is an answer recorded?
=> Indexes of days still waiting for a warmer day, in decreasing temperature order. When a warmer day arrives, every colder day on top of the stack is popped, and for each the answer is the difference of indexes.
??  Explain the idea behind the largest rectangle in a histogram.
=> For each bar, the widest rectangle using its height extends left and right until a shorter bar. A stack of increasing heights finds both limits: when a shorter bar arrives, the popped bar's right limit is the current index and its left limit is the index below it on the stack. A sentinel zero flushes the remaining bars.

## Queue, Deque and the Monotonic Deque

A **queue** is first-in first-out (BFS, scheduling, streaming); a **deque** adds O(1) operations at both ends, which makes the **sliding window maximum** possible in O(n): keep indexes in a deque ordered so the front is always the maximum of the current window.

```python QueuePatterns.py
from collections import deque


class MyQueue:
    """A FIFO queue from two stacks: amortised O(1) per operation."""
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def pop(self):
        self._shift()
        return self.outbox.pop()

    def peek(self):
        self._shift()
        return self.outbox[-1]

    def _shift(self):
        if not self.outbox:                               # move everything only when the outbox is empty
            while self.inbox:
                self.outbox.append(self.inbox.pop())


def sliding_window_max(nums, k):
    window, result = deque(), []                          # indexes whose values are in decreasing order
    for i, n in enumerate(nums):
        while window and nums[window[-1]] <= n:
            window.pop()                                  # smaller elements can never be a future maximum
        window.append(i)
        if window[0] <= i - k:
            window.popleft()                              # the front index left the window
        if i >= k - 1:
            result.append(nums[window[0]])
    return result


def longest_subarray_within_limit(nums, limit):
    """Longest subarray whose max - min <= limit: two monotonic deques inside a variable window."""
    max_q, min_q, left, best = deque(), deque(), 0, 0
    for right, n in enumerate(nums):
        while max_q and max_q[-1] < n:
            max_q.pop()
        max_q.append(n)
        while min_q and min_q[-1] > n:
            min_q.pop()
        min_q.append(n)
        while max_q[0] - min_q[0] > limit:
            if max_q[0] == nums[left]:
                max_q.popleft()
            if min_q[0] == nums[left]:
                min_q.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best


class RecentCounter:
    def __init__(self):
        self.times = deque()

    def ping(self, t):
        self.times.append(t)
        while self.times[0] < t - 3000:                   # drop requests older than 3000 ms
            self.times.popleft()
        return len(self.times)


q = MyQueue()
q.push(1); q.push(2)
assert q.peek() == 1 and q.pop() == 1
q.push(3)
assert q.pop() == 2 and q.pop() == 3
assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7] and sliding_window_max([1], 1) == [1] and sliding_window_max([9, 8, 7], 2) == [9, 8]
assert longest_subarray_within_limit([8, 2, 4, 7], 4) == 2 and longest_subarray_within_limit([10, 1, 2, 4, 7, 2], 5) == 4
counter = RecentCounter()
assert [counter.ping(t) for t in (1, 100, 3001, 3002)] == [1, 2, 3, 3]
print("queues and deques ok")
```

```output
```

??  How do you implement a queue with two stacks, and what is the cost?
=> Push onto an inbox stack; for pop or peek, if the outbox is empty move every element from the inbox to the outbox (reversing the order), then pop from the outbox. Each element moves at most once, so every operation is amortised O(1).
??  Why does the sliding window maximum deque stay in decreasing order?
=> A new element that is larger than the tail makes the smaller tail elements useless: they are older and smaller, so they can never be a maximum again. Popping them keeps the front as the maximum, and the front is dropped when its index leaves the window.
