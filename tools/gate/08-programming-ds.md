@part gate-programming-ds | Programming and Data Structures | software
## C basics and output prediction

GATE gives short C programs and asks for the output, so the skill is tracing exactly what the language guarantees. Unless a question says otherwise, assume a 32-bit `int` (4 bytes), `char` is 1 byte, pointers are 8 bytes on a 64-bit machine, and `double` is 8 bytes.

### Operators, precedence and conversions

| Precedence (high to low) | Operators | Associativity |
|---|---|---|
| 1 | postfix `++ --`, `()`, `[]`, `.`, `->` | left to right |
| 2 | prefix `++ --`, unary `+ - ! ~ * &`, `sizeof`, casts | right to left |
| 3 | `* / %` | left to right |
| 4 | `+ -` | left to right |
| 5 | `<< >>` | left to right |
| 6 | `< <= > >=` | left to right |
| 7 | `== !=` | left to right |
| 8, 9, 10 | `&`, then `^`, then `\|` | left to right |
| 11, 12 | `&&`, then `\|\|` | left to right |
| 13 | `?:` | right to left |
| 14 | `= += -= …` | right to left |

- **Integer division truncates toward zero** and `%` takes the sign of the dividend (C99): `7 / 2 = 3`, `-7 / 2 = -3`, `-7 % 3 = -1`.
- **`7 / 2 * 2`** is `(7 / 2) * 2 = 6`, not 7: division happens first, in integers.
- **Mixing signed and unsigned** converts the signed value to unsigned. `-1 < 1u` is **false (0)**, because -1 becomes a huge unsigned number.
- **`&&` and `||` short-circuit.** In `a++ && b++` with `a = 0`, `b++` never runs, but `a++` still increments `a`.
- **Bitwise precedence trap:** `5 & 3 | 4 ^ 1` is `(5 & 3) | (4 ^ 1) = 1 | 5 = 5`.
- **Macros are textual.** With `#define SQR(x) x*x`, `SQR(2+1)` expands to `2+1*2+1 = 5`, not 9. Always parenthesise.
- **`x++` yields the old value, `++x` the new one.** `int j = i++ * 2;` with `i = 5` gives `j = 10` and `i = 6`.
- **`static` locals keep their value between calls** and are initialised once.

```c Static variable
int f(void) {
    static int c = 0;     // initialised once, lives for the whole program
    return ++c;
}
// f(); f(); printf("%d", f());   prints 3
```

!warning Undefined behaviour is not an exam answer :: Expressions such as `i = i++ + ++i` or `a[i] = i++` modify and read a variable without a sequence point. If a question is only valid when you assume an order, the intended answer is usually "undefined" or the question avoids it. Don't invent an order.

!cheat C output cheat codes ::
- **Evaluate step by step on paper,** keeping a column for each variable. Update the variable column after each statement.
- **Integer first, float last:** `7 / 2 * 2.0` is `3 * 2.0 = 6.0`, but `7 / 2.0 * 2` is 7.0.
- **Look for a trap:** short-circuit, a macro without brackets, an unsigned comparison, a `static` local, a missing `break` in a `switch`, or `=` where `==` was meant.
- **`printf("%d", x)` of a `char` or `short`** promotes it to `int`; `%d` with a `double` is wrong.
- **`switch` falls through** to the next case unless there is a `break`.
!end

## Pointers, arrays, strings, structures

### Pointers and arrays

- An array name decays to a pointer to its first element, and `a[i]` is `*(a + i)`. **Pointer arithmetic scales by the element size**: `p + 1` moves 4 bytes for an `int *`.
- `*p++` increments the pointer after reading, but `(*p)++` increments the pointed-to value. `*++p` increments first.
- `p[-1]` is `*(p - 1)`. With `int a[] = {10,20,30,40}; int *p = a + 1; p++;` then `*p` is 30 and `p[-1]` is 20.
- `sizeof(a)` for an array is the total bytes, but for a pointer parameter it is just the pointer size.
- A **pointer to pointer** `**q` dereferences twice: with `int x = 5, *p = &x, **q = &p;`, writing `**q = 9` sets `x = 9`.

### Two-dimensional arrays

C stores `int a[R][C]` in **row-major** order. The address of `a[i][j]` is `base + (i·C + j) · size`. For `int a[3][4]` at 1000, `a[2][1]` is at 1000 + (2·4 + 1)·4 = 1036.

### Strings

A C string is a `char` array ending in `'\0'`. `char s[] = "GATE";` has `sizeof(s) = 5` (four letters and the terminator) and `strlen(s) = 4`. `strlen` counts up to, not including, the terminator.

### Structures, padding and unions

Each member sits at an address that is a multiple of its own size (alignment), and the struct's total size is padded to a multiple of its largest member's alignment.

```c Padding
struct A { char a; int b; char c; };  // a at 0, 3 bytes padding, b at 4, c at 8, 3 padding: size 12
struct B { int b; char a; char c; };  // b at 0, a at 4, c at 5, 2 padding: size 8
union  U { int i; double d; char c; };// all members share the same bytes: size = largest = 8
```

Reordering members from large to small usually shrinks a struct. A union's size is the size of its largest member.

### Memory and parameter passing

- **C passes parameters by value.** A function that changes its own copy does not change the caller's variable. To modify the caller's variable pass its address.
- `malloc` memory that is never `free`d is a **memory leak**. Using memory after `free`, or returning the address of a local variable, gives a **dangling pointer** and undefined behaviour.

```c Call by value and by address
void f(int a, int *b) { a = a + 1; *b = *b + 1; }
// int x = 1, y = 1; f(x, &y);   x stays 1, y becomes 2
```

!cheat Pointer cheat codes ::
- **Draw boxes and arrows.** Write each variable's value and address and follow every `*` and `&`.
- **`p + n` moves n elements, not n bytes.** The difference of two pointers is also in elements.
- **Struct size:** list member offsets, align each to its size, then pad the total to the largest alignment.
- **`sizeof("GATE")` is 5**, `strlen("GATE")` is 4.
- **Row-major address** = base + (i × columns + j) × element size.
- **Returning a pointer to a local array is a bug.** The array dies when the function returns.
!end

## Functions, recursion and scope

### The call stack

Each call pushes an **activation record** (parameters, return address, locals). When the function returns the record is popped. A recursion that goes n levels deep before returning has **n + 1 records** on the stack at its deepest, and a recursion with no base case overflows the stack.

### Recursion patterns to recognise

| Function | Result or count |
|---|---|
| `f(n) = f(n-1) + f(n-2)`, `f(0)=f(1)=1` | f(6) = 13; the number of calls to compute f(n) is 2f(n) − 1 |
| `power(x, y) = x * power(x, y-1)` | y + 1 calls, time linear in y |
| `gcd(a, b) = gcd(b, a % b)` | stops when b = 0; at most O(log min) calls |
| Tower of Hanoi `H(n) = 2H(n-1) + 1` | 2ⁿ − 1 moves |
| Binary recursion `g(n-1), print n, g(n-1)` | prints the "ruler sequence": g(3) prints 1 2 1 3 1 2 1 |

```c Ruler sequence
void g(int n) {
    if (n > 0) {
        g(n - 1);
        printf("%d ", n);
        g(n - 1);
    }
}
// g(3) prints: 1 2 1 3 1 2 1
```

A call is **tail recursive** if the recursive call is the very last thing done, with no pending work: `return fact(n-1, n*acc);` is tail recursive, but `return n * fact(n-1);` is not. A compiler can turn tail recursion into a loop and use constant stack space.

### Scoping rules

- **Static (lexical) scoping,** which C uses: a free variable refers to the declaration visible where the function is **written**.
- **Dynamic scoping:** it refers to the most recent declaration on the **call stack**.

```c Static versus dynamic scope
int x = 10;
void f(void) { printf("%d", x); }
void g(void) { int x = 20; f(); }
// g() prints 10 under static scoping (C) and 20 under dynamic scoping
```

!cheat Recursion cheat codes ::
- **Draw the recursion tree.** The number of calls is the number of nodes, and the stack depth is the height of the tree plus one.
- **Fibonacci-style calls:** calls(n) = 1 + calls(n-1) + calls(n-2). With calls(0) = calls(1) = 1: 1, 3, 5, 9, 15, 25. The 15 is the number of calls for n = 5.
- **Print before or after the recursive call?** Printing before gives pre-order, after gives post-order.
- **Dynamic scoping = look at who called me.** Static scoping = look at where I was written.
- **Hanoi moves:** 2ⁿ − 1. For 5 disks that is 31.
!end

## Arrays, stacks and queues

### Array address formulas

For a one-dimensional array `A[lb..ub]`: address of `A[i]` = base + (i − lb) × w. For a two-dimensional `A[l1..u1][l2..u2]` with n₂ = u2 − l2 + 1 columns:

- **Row-major:** base + ((i − l1) × n₂ + (j − l2)) × w
- **Column-major:** base + ((j − l2) × n₁ + (i − l1)) × w, where n₁ is the number of rows

For `A[1..5][1..8]`, row-major, base 2000, w = 4: `A[3][4]` is at 2000 + (2·8 + 3)·4 = 2076.

A lower-triangular n × n matrix needs only n(n + 1)/2 cells. Stored row by row with 1-based indices, `a[i][j]` (i ≥ j) is at position i(i − 1)/2 + j. So `a[5][3]` is at 13.

### Stacks

A stack is last-in first-out with **push**, **pop** and **peek** in O(1).

- **Postfix evaluation:** scan left to right, push operands, and on an operator pop two, apply, push the result. `5 3 + 2 * 7 -` gives (5 + 3) × 2 − 7 = 9.
- **Infix to postfix:** operands go straight to the output, operators wait on a stack until a lower-or-equal precedence operator arrives. `A + B * C - D` becomes `A B C * + D -`.
- **Balanced brackets, next-greater-element and undo** all use a stack.
- **Stack permutations:** if 1, 2, …, n are pushed in order, with pops allowed at any time, the number of possible pop sequences is the Catalan number Cₙ (14 for n = 4). A sequence is impossible if it needs a larger number to come out before a smaller one that was pushed earlier but is not on top. With 1, 2, 3 pushed in order, **3, 1, 2** cannot happen.

### Queues

A queue is first-in first-out with **enqueue** and **dequeue** in O(1) using a linked list or a circular array. In a circular array of size N with `front` and `rear` indices, the elements are (rear − front + N) mod N + 1 when the queue is non-empty and `rear` points at the last element. A **deque** allows insertion and deletion at both ends.

A queue can be built from **two stacks** (push onto one, pour into the other for dequeue). Each element moves at most twice, so n enqueues and n dequeues take O(n) in total, i.e. O(1) amortised per operation.

!cheat Stack and queue cheat codes ::
- **Postfix by hand:** scan, push numbers, and the top two items are the operands (the second item popped is the left operand).
- **Stack permutations:** number of valid pop orders = Catalan(n). Test a candidate by simulating push and pop.
- **Circular queue count:** (rear − front + N) mod N + 1 when `rear` is the last element's index.
- **Operator order in infix → postfix:** equal precedence pops first for left-associative operators.
- **Triangular matrix:** n(n+1)/2 cells and row-by-row position i(i−1)/2 + j.
!end

## Linked lists

| Operation | Singly (head only) | Doubly |
|---|---|---|
| Insert at head | O(1) | O(1) |
| Insert at tail | **O(n)** (O(1) with a tail pointer) | O(n) / O(1) with tail |
| Delete the head | O(1) | O(1) |
| Delete a node **given a pointer to it** | O(n) to find the previous node (O(1) trick: copy the next node over it, if it is not the last) | **O(1)** |
| Search | O(n) | O(n) |
| Reverse | O(n) time, O(1) extra space | O(n) |

**Two-pointer techniques:** a slow pointer moving one step and a fast pointer moving two. When the fast pointer reaches the end of a list of 9 nodes, the slow pointer is at node 5, the middle. If the list has a cycle the two pointers eventually meet (**Floyd's tortoise and hare**), which detects a cycle in O(n) time and O(1) space.

```c Walk to the second-last node
// list: 1 -> 2 -> 3 -> 4 -> 5
struct node *p = head;
while (p->next->next != NULL)
    p = p->next;
printf("%d", p->d);   // prints 4
```

!cheat Linked-list cheat codes ::
- **Draw the nodes and the pointer after each statement.** Most output questions are lost by skipping one step.
- **Reversal needs three pointers** (previous, current, next) and runs in one pass.
- **O(1) deletion needs a doubly linked list** or a pointer to the *previous* node.
- **A tail pointer makes enqueue O(1)** for a singly linked queue.
- **Middle and cycle problems = slow and fast pointers.**
!end

## Trees and binary search trees

### Binary tree facts

For a binary tree with root at height 0:

- Maximum nodes at level i is 2ⁱ, and in a tree of height h is **2^(h+1) − 1**. Minimum height of n nodes is ⌊log₂ n⌋.
- If every internal node has exactly two children, **leaves = internal nodes + 1**. A full tree with 20 leaves has 19 internal nodes and 39 nodes in all.
- The number of different **shapes** of binary trees with n nodes is the Catalan number Cₙ: C₄ = 14. With distinct labelled nodes it is Cₙ × n!.
- A **complete** tree with n nodes has height ⌊log₂ n⌋ (100 nodes → 6).

### Traversals

| Order | Visit | Use |
|---|---|---|
| Preorder | root, left, right | copy a tree |
| Inorder | left, root, right | sorted order of a BST |
| Postorder | left, right, root | delete a tree, evaluate expressions |
| Level order | by depth | BFS with a queue |

**Rebuilding a tree:** the inorder sequence together with either the preorder or the postorder sequence determines the tree. Preorder and postorder alone do **not** (unless every internal node has two children). Method: the first preorder item (or last postorder item) is the root; find it in the inorder sequence to split into left and right subtrees; repeat.

Example: preorder A B D E C F and inorder D B E A F C give the postorder **D E B F C A**.

### Binary search trees

Left subtree < node < right subtree. Search, insert and delete cost **O(h)**: O(log n) when balanced and **O(n)** for a skewed tree, which is what sorted insertion order gives. The inorder traversal of a BST is sorted. To delete a node with two children, replace it by its **inorder successor** (the smallest key in the right subtree) or predecessor, then delete that node. The number of insertion orders that give the same BST is a count of ways to interleave the left and right insertions: for keys 1, 2, 3 the tree with root 2 arises from the orders 2,1,3 and 2,3,1.

### AVL trees

An AVL tree keeps |height(left) − height(right)| ≤ 1 at every node, restoring it by rotations (LL, RR, LR, RL). The minimum number of nodes N(h) of an AVL tree of height h satisfies **N(h) = N(h − 1) + N(h − 2) + 1** with N(0) = 1 and N(1) = 2, so N = 1, 2, 4, 7, 12, 20 … The height is O(log n), at most about 1.44 log₂ n.

!cheat Tree cheat codes ::
- **Rebuild from traversals:** inorder splits, preorder (or postorder from the back) names the root. Always start from the root.
- **Full binary tree:** L = I + 1, so n = 2L − 1.
- **Skewed BST** comes from inserting sorted keys, so its height is n − 1.
- **BST traversal from a preorder list:** the first element is the root; elements smaller than it come first (left subtree), then the larger ones.
- **AVL minimum nodes:** 1, 2, 4, 7, 12, 20. Each is the previous two plus 1.
- **Preorder + postorder gives a unique tree only for full trees.**
!end

## Binary heaps and priority queues

A **binary heap** is a complete binary tree stored in an array with the heap property: in a **max-heap** every parent is ≥ its children (a min-heap is the reverse). Using 1-based indexing, the parent of `i` is `⌊i/2⌋`, and the children of `i` are `2i` and `2i + 1`. The parent of `a[11]` is `a[5]`.

| Operation | Method | Time |
|---|---|---|
| Insert | add at the end, sift up | O(log n) |
| Extract max/min | move the last element to the root, sift down | O(log n) |
| Peek | read `a[1]` | O(1) |
| **Build heap** from n elements | sift down from ⌊n/2⌋ to 1 | **O(n)** |
| Heapsort | build heap, then n extractions | O(n log n) |
| Search for an arbitrary key | no structure helps | O(n) |

- The leaves are the nodes with index > ⌊n/2⌋, so there are ⌈n/2⌉ leaves (5 for n = 10).
- The height is ⌊log₂ n⌋.
- Inserting 10, 20, 15, 30, 25 one by one into a max-heap gives the array **30 25 15 10 20**.
- The number of different max-heaps on n distinct keys: 1, 1, 2, 3, 8, 20 for n = 1 … 6. For {1,2,3,4} there are 3.

!cheat Heap cheat codes ::
- **Draw the tree while you sift.** Compare with the parent only on the way up, with the larger child on the way down.
- **Build-heap is linear** because most nodes are near the bottom and sift down only a little.
- **The k-th smallest of a min-heap is not at a fixed place,** so finding it needs k extractions: O(k log n).
- **Largest element of a min-heap** is at one of the leaves, so locating it costs O(n).
- **Parent = ⌊i/2⌋, children = 2i, 2i+1** (for a 0-based array: (i − 1)/2, 2i + 1, 2i + 2).
!end

## Graphs: representation and traversal

A graph G = (V, E). Two standard representations:

| | Adjacency matrix | Adjacency list |
|---|---|---|
| Space | O(V²) | O(V + E) |
| Is (u, v) an edge? | O(1) | O(degree) |
| List all neighbours | O(V) | O(degree) |
| Best for | dense graphs | sparse graphs |

- **BFS** uses a queue and visits vertices in order of distance from the source. **DFS** uses a stack or recursion. Both take **O(V + E)** with adjacency lists.
- With edges A–B, A–C, B–D, C–D, D–E and neighbours visited alphabetically from A: BFS order A B C D E, DFS order **A B D C E**.
- The number of **connected components** equals the number of times you must start a fresh DFS or BFS.
- A **topological order** exists only for a directed acyclic graph (DAG). The edges a→c, b→c, c→d have exactly two topological orders (a b c d and b a c d).
- For an adjacency matrix A of a simple undirected graph, (Aᵏ)[i][j] counts walks of length k from i to j, and **trace(A³) / 6 is the number of triangles**.

!cheat Graph cheat codes ::
- **Pick the representation by density:** E close to V² → matrix, E close to V → list.
- **Trace DFS with the recursion stack.** Remember to go back up after a dead end.
- **Counting components:** count the DFS restarts.
- **Counting topological orders:** repeatedly pick any vertex with in-degree 0 and multiply the choices.
- **Detect a cycle** in an undirected graph by seeing an already-visited vertex that is not the parent.
!end

## Cheat sheet: Programming and Data Structures on one page

| Topic | Fact |
|---|---|
| Integer division | truncates toward zero; `%` follows the dividend's sign |
| Short-circuit | `&&`, `\|\|` skip the right side |
| Macro pitfall | `SQR(x) x*x` with `SQR(2+1)` is 5 |
| Pointer arithmetic | `p + 1` moves one element |
| Row-major address | base + (i·C + j)·size |
| Struct size | align members, pad to the largest alignment |
| Fibonacci calls | 1, 3, 5, 9, 15, 25 |
| Hanoi | 2ⁿ − 1 moves |
| Stack pop sequences | Catalan(n) |
| Postfix evaluation | push operands; operator pops two |
| BST | O(h); inorder is sorted |
| Rebuild a tree | inorder + preorder or postorder |
| Full binary tree | leaves = internal + 1 |
| AVL minimum nodes | N(h) = N(h−1) + N(h−2) + 1 |
| Heap | parent ⌊i/2⌋, children 2i and 2i+1; build O(n) |
| BFS and DFS | O(V + E) with lists |
| Triangles | trace(A³) / 6 |

??  Why does `SQR(2+1)` give 5 and not 9 when `SQR(x)` is defined as `x*x`?
=> The preprocessor substitutes text: `2+1*2+1`. Multiplication binds tighter than addition, so the value is 2 + 2 + 1 = 5. The macro should be `((x)*(x))`.
??  Reconstruct the tree whose preorder is A B D E C F and inorder is D B E A F C. What is its postorder?
=> A is the root. In the inorder sequence D B E is the left subtree and F C the right. In the left part B is the root with D and E as children. In the right part C is the root with F as its left child. The postorder is D E B F C A.
??  Why can a heap be built in O(n) even though each sift-down costs O(log n)?
=> Half of the nodes are leaves and need no work, a quarter sift down at most one level, an eighth at most two, and so on. The sum n/4·1 + n/8·2 + … is linear.
??  What is the difference between static and dynamic scoping, and which does C use?
=> Under static scoping a free variable is resolved in the environment where the function is defined; under dynamic scoping it is resolved through the chain of callers. C uses static scoping.
