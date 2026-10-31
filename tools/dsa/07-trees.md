@part trees | Trees | trees
## The idea

A tree is a recursive structure: a node whose children are themselves trees. That is why nearly every tree problem has a short **recursive** solution, and why the key skill is deciding *what each call returns*.

Two traversals cover everything:

- **Depth-first (DFS)** goes down a path before trying siblings. The order in which you touch the node gives **preorder** (node, left, right), **inorder** (left, node, right; sorted order for a BST) and **postorder** (left, right, node; children are known before the parent, so it suits "compute from the bottom up").
- **Breadth-first (BFS)** visits level by level using a queue. Use it for level order, right side view, and shortest distance in an unweighted tree.

!tip Signal words :: "depth", "height", "balanced", "ancestor", "path sum", "level", "BST", "serialize". For a **BST**, think inorder = sorted, and use the ordering to discard half of the tree at every step.

The pattern for bottom-up problems (diameter, maximum path sum, balanced tree) is: **return one thing to the parent, record another thing globally**. For the diameter, a node returns its *height* to the parent but updates the best *diameter* (left height + right height) through itself.

| Question | Approach | Cost |
|---|---|---|
| Height, depth, same tree, invert | Recursion, postorder | O(n) time, O(h) stack |
| Level order, right side view | BFS with a queue | O(n) time, O(w) queue |
| Validate BST | Pass `(lo, hi)` bounds down | O(n) |
| LCA in a BST | Walk down using the ordering | O(h) |

Here *h* is the height of the tree: O(log n) when balanced and O(n) when it degenerates into a list.

## The Java toolkit and templates

```java TreeTemplates.java
import java.util.*;

public class TreeTemplates {

    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int val) { this.val = val; }
    }

    /** Maximum Depth: the base case is the empty tree. */
    static int maxDepth(TreeNode node) {
        return node == null ? 0 : 1 + Math.max(maxDepth(node.left), maxDepth(node.right));
    }

    /** Invert Binary Tree. */
    static TreeNode invert(TreeNode node) {
        if (node == null) return null;
        TreeNode left = invert(node.left);
        node.left = invert(node.right);
        node.right = left;
        return node;
    }

    /** Level order with BFS: process exactly one level per outer iteration using the queue size. */
    static List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> levels = new ArrayList<>();
        if (root == null) return levels;
        Queue<TreeNode> queue = new ArrayDeque<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            int size = queue.size();                         // the number of nodes on this level
            List<Integer> level = new ArrayList<>();
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.poll();
                level.add(node.val);
                if (node.left != null) queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }
            levels.add(level);
        }
        return levels;
    }

    /** Validate BST: every node must lie strictly between the bounds its ancestors impose. Use long bounds. */
    static boolean isValidBST(TreeNode node, long low, long high) {
        if (node == null) return true;
        if (node.val <= low || node.val >= high) return false;
        return isValidBST(node.left, low, node.val) && isValidBST(node.right, node.val, high);
    }

    /** Diameter: each call returns its height but records the longest path that bends at the node. */
    static int diameter(TreeNode root) {
        int[] best = { 0 };
        height(root, best);
        return best[0];
    }

    private static int height(TreeNode node, int[] best) {
        if (node == null) return 0;
        int left = height(node.left, best), right = height(node.right, best);
        best[0] = Math.max(best[0], left + right);          // path through this node
        return 1 + Math.max(left, right);                   // path going up to the parent
    }

    /** Binary Tree Maximum Path Sum: same shape as the diameter, but negative branches are dropped. */
    static int maxPathSum(TreeNode root) {
        int[] best = { Integer.MIN_VALUE };
        gain(root, best);
        return best[0];
    }

    private static int gain(TreeNode node, int[] best) {
        if (node == null) return 0;
        int left = Math.max(0, gain(node.left, best));
        int right = Math.max(0, gain(node.right, best));
        best[0] = Math.max(best[0], node.val + left + right);
        return node.val + Math.max(left, right);
    }

    /** Lowest Common Ancestor in a BST: the split point where p and q go to different sides. */
    static TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        while (root != null) {
            if (p.val < root.val && q.val < root.val) root = root.left;
            else if (p.val > root.val && q.val > root.val) root = root.right;
            else return root;
        }
        return null;
    }

    /** Kth smallest in a BST: iterative inorder traversal stops at the k-th node. */
    static int kthSmallest(TreeNode root, int k) {
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode node = root;
        while (node != null || !stack.isEmpty()) {
            while (node != null) { stack.push(node); node = node.left; }
            node = stack.pop();
            if (--k == 0) return node.val;
            node = node.right;
        }
        throw new IllegalArgumentException("k is larger than the tree");
    }
}
```

**What to notice.** `isValidBST` passes `long` bounds because a node may legitimately hold `Integer.MIN_VALUE` or `MAX_VALUE`. Checking only each node against its direct children is the classic wrong answer: a deep right descendant can still be smaller than the root.

## Pitfalls and interview angle

- **Checking only parent and child** for a BST instead of carrying bounds.
- **Recursion depth.** A degenerate tree of 100,000 nodes overflows the Java stack with recursion. Mention an iterative traversal with an explicit stack.
- **Mixing "return" and "record"**: a function that returns the height cannot also return the diameter; use a holder such as `int[]` or a field.
- **Forgetting the null base case**, which is also the most common source of `NullPointerException`.
- **BFS level size**: read `queue.size()` *before* the inner loop, because the queue grows during it.

!interview Interview angle: What is the space complexity of recursive DFS on a tree? :: O(h) for the call stack, where h is the height: O(log n) for a balanced tree and O(n) in the worst case of a skewed tree. BFS needs O(w) for the queue, where w is the widest level, which can be about n/2 for a complete tree.

!keypoints Tree problems are recursive: decide what each call returns ;; Preorder, inorder (sorted for a BST) and postorder (bottom-up) are the DFS orders ;; BFS with a queue gives level order; read the queue size before the level loop ;; Bottom-up problems return one value and record another ;; Validate a BST with bounds, not with parent-child checks ;; Recursion depth is O(h); mention an iterative version for skewed trees

?? Why does inorder traversal of a BST give sorted output?
=> At every node the left subtree holds smaller values and the right subtree larger ones. Inorder visits left, node, right, so values come out in increasing order.

?? Why is checking `node.left.val < node.val < node.right.val` not enough to validate a BST?
=> It misses violations from further down: a node in the right subtree of the root's left child can be larger than the root and still satisfy its own parent. You must carry the (low, high) bounds inherited from all ancestors.

?? How do you compute the diameter in O(n)?
=> Do one postorder traversal where each node returns its height to the parent and updates a global maximum with `leftHeight + rightHeight`. Computing heights separately for every node would be O(n²) on a skewed tree.
