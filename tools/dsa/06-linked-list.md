@part linked-list | Linked List | foundations
## The idea

A linked list stores elements in nodes that point to the next node. There is no index: reaching the k-th element costs O(k). In exchange, inserting or removing a node you already hold costs O(1), and the list can grow without copying. Interview problems on linked lists are almost never about the structure itself; they test whether you can **rewire pointers without losing the rest of the list**.

Three moves solve most of them:

- **Dummy node.** A fake node placed before the head removes the special case of changing the head (removing the first node, merging, partitioning).
- **Reverse in place.** Walk the list once, pointing each node backwards. It is the building block of Reorder List, Reverse Nodes in k-Group and palindrome checks.
- **Fast and slow pointers.** Two pointers at different speeds find the middle, detect a cycle, and locate the n-th node from the end.

!tip Signal words :: "in place", "O(1) extra space", "cycle", "middle", "n-th from the end", "merge sorted lists", "reverse".

## The Java toolkit and templates

```java LinkedListTemplates.java
import java.util.*;

public class LinkedListTemplates {

    static class ListNode {
        int val;
        ListNode next;
        ListNode(int val) { this.val = val; }
    }

    /** Reverse a list: save next, point backwards, step forward. Do it in that order. */
    static ListNode reverse(ListNode head) {
        ListNode prev = null;
        while (head != null) {
            ListNode next = head.next;       // 1. remember the rest
            head.next = prev;                // 2. point backwards
            prev = head;                     // 3. advance both pointers
            head = next;
        }
        return prev;
    }

    /** Merge two sorted lists with a dummy head. */
    static ListNode mergeTwoLists(ListNode a, ListNode b) {
        ListNode dummy = new ListNode(0), tail = dummy;
        while (a != null && b != null) {
            if (a.val <= b.val) { tail.next = a; a = a.next; }
            else { tail.next = b; b = b.next; }
            tail = tail.next;
        }
        tail.next = a != null ? a : b;       // append whatever is left
        return dummy.next;
    }

    /** Floyd's cycle detection: the fast pointer laps the slow one if there is a cycle. */
    static boolean hasCycle(ListNode head) {
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    /** Remove the n-th node from the end: keep two pointers n nodes apart. */
    static ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode lead = dummy, trail = dummy;
        for (int i = 0; i < n; i++) lead = lead.next;
        while (lead.next != null) {
            lead = lead.next;
            trail = trail.next;
        }
        trail.next = trail.next.next;        // trail is the node before the one to remove
        return dummy.next;
    }

    /** The middle node (the second middle for even length): used by Reorder List and palindrome checks. */
    static ListNode middle(ListNode head) {
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }

    /** LRU Cache: a LinkedHashMap in access order evicts the least recently used entry. */
    static class LRUCache<K, V> extends LinkedHashMap<K, V> {
        private final int capacity;

        LRUCache(int capacity) {
            super(16, 0.75f, true);          // true = order by access, not by insertion
            this.capacity = capacity;
        }

        @Override
        protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return size() > capacity;
        }
    }
}
```

**What to notice.** `removeNthFromEnd` uses the dummy node so that removing the *head* needs no special case: `trail` can be the dummy. The `LRUCache` shortcut is fine to mention in an interview, but you will usually be asked to build the real thing: a `HashMap<K, Node>` plus a doubly linked list with dummy head and tail nodes, moving a node to the front on every access.

## Pitfalls and interview angle

- **Losing the rest of the list** by overwriting `next` before saving it.
- **Null checks**: `fast != null && fast.next != null` in that order.
- **Forgetting to cut a link** after splitting a list in two (Reorder List): the first half must end with `null`, or you create a cycle.
- **Cycle start.** After Floyd meets, put one pointer back at the head and move both one step at a time; they meet at the cycle start.
- **Comparing nodes** with `==` compares identity, which is what you want; comparing `val` is a different question.

!interview Interview angle: Why do the fast and slow pointers meet inside a cycle? :: Once both are in the cycle, the fast pointer gains one step on the slow one each round, so the gap between them shrinks by one every iteration and must reach zero. In a list with no cycle the fast pointer reaches `null` first.

!keypoints Linked list problems are pointer-rewiring problems: save `next` before you overwrite it ;; A dummy head removes head special cases ;; Reverse in place with `prev`, `head`, `next` ;; Fast and slow pointers find the middle, a cycle, and the n-th from the end ;; Cut links after splitting a list, or you create a cycle ;; LRU Cache = hash map plus doubly linked list, O(1) get and put

?? How do you find the middle of a linked list in one pass?
=> Move a slow pointer one step and a fast pointer two steps. When the fast pointer reaches the end, the slow pointer is at the middle.

?? Why use a dummy node when merging two lists?
=> The head of the merged list is not known until the first comparison. A dummy node gives `tail` something to attach to from the start, and `dummy.next` is the result, with no special case for the first node.

?? What are the time and space costs of getting and putting in an LRU cache built from a hash map and a doubly linked list?
=> Both O(1). The map finds the node in O(1) and the doubly linked list moves it to the front or removes the tail in O(1).
