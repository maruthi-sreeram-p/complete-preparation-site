"""
The NeetCode 150 grouped by NeetCode's 18 topics, with the dependency edges of its roadmap.

Single source for tools/build_dsa_topics.py, which writes both the "DSA by topic" tree and the practice subjects.

problem tuple: (LeetCode number, title, LeetCode slug, difficulty, needs a LeetCode premium account)
Links are https://leetcode.com/problems/<slug>/ . The problem set is NeetCode's; the numbers and titles are LeetCode's.
"""

E, M, H = "Easy", "Medium", "Hard"

TOPICS = [
    {
        "id": "arrays-hashing", "title": "Arrays & Hashing", "tier": "foundations", "requires": [],
        "tag": "hash-table", "gfg": "https://www.geeksforgeeks.org/dsa/hashing-data-structure/",
        "problems": [
            (217, "Contains Duplicate", "contains-duplicate", E, False),
            (242, "Valid Anagram", "valid-anagram", E, False),
            (1, "Two Sum", "two-sum", E, False),
            (49, "Group Anagrams", "group-anagrams", M, False),
            (347, "Top K Frequent Elements", "top-k-frequent-elements", M, False),
            (271, "Encode and Decode Strings", "encode-and-decode-strings", M, True),
            (238, "Product of Array Except Self", "product-of-array-except-self", M, False),
            (36, "Valid Sudoku", "valid-sudoku", M, False),
            (128, "Longest Consecutive Sequence", "longest-consecutive-sequence", M, False),
        ],
    },
    {
        "id": "two-pointers", "title": "Two Pointers", "tier": "foundations", "requires": ["arrays-hashing"],
        "tag": "two-pointers", "gfg": "https://www.geeksforgeeks.org/dsa/two-pointers-technique/",
        "problems": [
            (125, "Valid Palindrome", "valid-palindrome", E, False),
            (167, "Two Sum II - Input Array Is Sorted", "two-sum-ii-input-array-is-sorted", M, False),
            (15, "3Sum", "3sum", M, False),
            (11, "Container With Most Water", "container-with-most-water", M, False),
            (42, "Trapping Rain Water", "trapping-rain-water", H, False),
        ],
    },
    {
        "id": "binary-search", "title": "Binary Search", "tier": "foundations", "requires": ["two-pointers"],
        "tag": "binary-search", "gfg": "https://www.geeksforgeeks.org/dsa/binary-search/",
        "problems": [
            (704, "Binary Search", "binary-search", E, False),
            (74, "Search a 2D Matrix", "search-a-2d-matrix", M, False),
            (875, "Koko Eating Bananas", "koko-eating-bananas", M, False),
            (153, "Find Minimum in Rotated Sorted Array", "find-minimum-in-rotated-sorted-array", M, False),
            (33, "Search in Rotated Sorted Array", "search-in-rotated-sorted-array", M, False),
            (981, "Time Based Key-Value Store", "time-based-key-value-store", M, False),
            (4, "Median of Two Sorted Arrays", "median-of-two-sorted-arrays", H, False),
        ],
    },
    {
        "id": "stack", "title": "Stack", "tier": "foundations", "requires": ["arrays-hashing"],
        "tag": "stack", "gfg": "https://www.geeksforgeeks.org/dsa/stack-data-structure/",
        "problems": [
            (20, "Valid Parentheses", "valid-parentheses", E, False),
            (155, "Min Stack", "min-stack", M, False),
            (150, "Evaluate Reverse Polish Notation", "evaluate-reverse-polish-notation", M, False),
            (22, "Generate Parentheses", "generate-parentheses", M, False),
            (739, "Daily Temperatures", "daily-temperatures", M, False),
            (853, "Car Fleet", "car-fleet", M, False),
            (84, "Largest Rectangle in Histogram", "largest-rectangle-in-histogram", H, False),
        ],
    },
    {
        "id": "sliding-window", "title": "Sliding Window", "tier": "foundations", "requires": ["two-pointers"],
        "tag": "sliding-window", "gfg": "https://www.geeksforgeeks.org/dsa/window-sliding-technique/",
        "problems": [
            (121, "Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock", E, False),
            (3, "Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters", M, False),
            (424, "Longest Repeating Character Replacement", "longest-repeating-character-replacement", M, False),
            (567, "Permutation in String", "permutation-in-string", M, False),
            (76, "Minimum Window Substring", "minimum-window-substring", H, False),
            (239, "Sliding Window Maximum", "sliding-window-maximum", H, False),
        ],
    },
    {
        "id": "linked-list", "title": "Linked List", "tier": "foundations", "requires": ["two-pointers"],
        "tag": "linked-list", "gfg": "https://www.geeksforgeeks.org/dsa/linked-list-data-structure/",
        "problems": [
            (206, "Reverse Linked List", "reverse-linked-list", E, False),
            (21, "Merge Two Sorted Lists", "merge-two-sorted-lists", E, False),
            (141, "Linked List Cycle", "linked-list-cycle", E, False),
            (143, "Reorder List", "reorder-list", M, False),
            (19, "Remove Nth Node From End of List", "remove-nth-node-from-end-of-list", M, False),
            (138, "Copy List with Random Pointer", "copy-list-with-random-pointer", M, False),
            (2, "Add Two Numbers", "add-two-numbers", M, False),
            (287, "Find the Duplicate Number", "find-the-duplicate-number", M, False),
            (146, "LRU Cache", "lru-cache", M, False),
            (23, "Merge k Sorted Lists", "merge-k-sorted-lists", H, False),
            (25, "Reverse Nodes in k-Group", "reverse-nodes-in-k-group", H, False),
        ],
    },
    {
        "id": "trees", "title": "Trees", "tier": "trees", "requires": ["binary-search", "sliding-window", "linked-list"],
        "tag": "binary-tree", "gfg": "https://www.geeksforgeeks.org/dsa/binary-tree-data-structure/",
        "problems": [
            (226, "Invert Binary Tree", "invert-binary-tree", E, False),
            (104, "Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree", E, False),
            (543, "Diameter of Binary Tree", "diameter-of-binary-tree", E, False),
            (110, "Balanced Binary Tree", "balanced-binary-tree", E, False),
            (100, "Same Tree", "same-tree", E, False),
            (572, "Subtree of Another Tree", "subtree-of-another-tree", E, False),
            (235, "Lowest Common Ancestor of a Binary Search Tree", "lowest-common-ancestor-of-a-binary-search-tree", M, False),
            (102, "Binary Tree Level Order Traversal", "binary-tree-level-order-traversal", M, False),
            (199, "Binary Tree Right Side View", "binary-tree-right-side-view", M, False),
            (1448, "Count Good Nodes in Binary Tree", "count-good-nodes-in-binary-tree", M, False),
            (98, "Validate Binary Search Tree", "validate-binary-search-tree", M, False),
            (230, "Kth Smallest Element in a BST", "kth-smallest-element-in-a-bst", M, False),
            (105, "Construct Binary Tree from Preorder and Inorder Traversal", "construct-binary-tree-from-preorder-and-inorder-traversal", M, False),
            (124, "Binary Tree Maximum Path Sum", "binary-tree-maximum-path-sum", H, False),
            (297, "Serialize and Deserialize Binary Tree", "serialize-and-deserialize-binary-tree", H, False),
        ],
    },
    {
        "id": "tries", "title": "Tries", "tier": "trees", "requires": ["trees"],
        "tag": "trie", "gfg": "https://www.geeksforgeeks.org/dsa/introduction-to-trie-data-structure-and-algorithm-tutorials/",
        "problems": [
            (208, "Implement Trie (Prefix Tree)", "implement-trie-prefix-tree", M, False),
            (211, "Design Add and Search Words Data Structure", "design-add-and-search-words-data-structure", M, False),
            (212, "Word Search II", "word-search-ii", H, False),
        ],
    },
    {
        "id": "heap-priority-queue", "title": "Heap / Priority Queue", "tier": "trees", "requires": ["trees"],
        "tag": "heap-priority-queue", "gfg": "https://www.geeksforgeeks.org/dsa/heap-data-structure/",
        "problems": [
            (703, "Kth Largest Element in a Stream", "kth-largest-element-in-a-stream", E, False),
            (1046, "Last Stone Weight", "last-stone-weight", E, False),
            (973, "K Closest Points to Origin", "k-closest-points-to-origin", M, False),
            (215, "Kth Largest Element in an Array", "kth-largest-element-in-an-array", M, False),
            (621, "Task Scheduler", "task-scheduler", M, False),
            (355, "Design Twitter", "design-twitter", M, False),
            (295, "Find Median from Data Stream", "find-median-from-data-stream", H, False),
        ],
    },
    {
        "id": "backtracking", "title": "Backtracking", "tier": "trees", "requires": ["trees"],
        "tag": "backtracking", "gfg": "https://www.geeksforgeeks.org/dsa/backtracking-algorithms/",
        "problems": [
            (78, "Subsets", "subsets", M, False),
            (39, "Combination Sum", "combination-sum", M, False),
            (46, "Permutations", "permutations", M, False),
            (90, "Subsets II", "subsets-ii", M, False),
            (40, "Combination Sum II", "combination-sum-ii", M, False),
            (79, "Word Search", "word-search", M, False),
            (131, "Palindrome Partitioning", "palindrome-partitioning", M, False),
            (17, "Letter Combinations of a Phone Number", "letter-combinations-of-a-phone-number", M, False),
            (51, "N-Queens", "n-queens", H, False),
        ],
    },
    {
        "id": "graphs", "title": "Graphs", "tier": "advanced", "requires": ["backtracking"],
        "tag": "graph", "gfg": "https://www.geeksforgeeks.org/dsa/graph-data-structure-and-algorithms/",
        "problems": [
            (200, "Number of Islands", "number-of-islands", M, False),
            (133, "Clone Graph", "clone-graph", M, False),
            (695, "Max Area of Island", "max-area-of-island", M, False),
            (417, "Pacific Atlantic Water Flow", "pacific-atlantic-water-flow", M, False),
            (130, "Surrounded Regions", "surrounded-regions", M, False),
            (994, "Rotting Oranges", "rotting-oranges", M, False),
            (286, "Walls and Gates", "walls-and-gates", M, True),
            (207, "Course Schedule", "course-schedule", M, False),
            (210, "Course Schedule II", "course-schedule-ii", M, False),
            (684, "Redundant Connection", "redundant-connection", M, False),
            (323, "Number of Connected Components in an Undirected Graph", "number-of-connected-components-in-an-undirected-graph", M, True),
            (261, "Graph Valid Tree", "graph-valid-tree", M, True),
            (127, "Word Ladder", "word-ladder", H, False),
        ],
    },
    {
        "id": "dp-1d", "title": "1-D Dynamic Programming", "tier": "advanced", "requires": ["backtracking"],
        "tag": "dynamic-programming", "gfg": "https://www.geeksforgeeks.org/dsa/dynamic-programming/",
        "problems": [
            (70, "Climbing Stairs", "climbing-stairs", E, False),
            (746, "Min Cost Climbing Stairs", "min-cost-climbing-stairs", E, False),
            (198, "House Robber", "house-robber", M, False),
            (213, "House Robber II", "house-robber-ii", M, False),
            (5, "Longest Palindromic Substring", "longest-palindromic-substring", M, False),
            (647, "Palindromic Substrings", "palindromic-substrings", M, False),
            (91, "Decode Ways", "decode-ways", M, False),
            (322, "Coin Change", "coin-change", M, False),
            (152, "Maximum Product Subarray", "maximum-product-subarray", M, False),
            (139, "Word Break", "word-break", M, False),
            (300, "Longest Increasing Subsequence", "longest-increasing-subsequence", M, False),
            (416, "Partition Equal Subset Sum", "partition-equal-subset-sum", M, False),
        ],
    },
    {
        "id": "intervals", "title": "Intervals", "tier": "advanced", "requires": ["heap-priority-queue"],
        "tag": "line-sweep", "gfg": "https://www.geeksforgeeks.org/dsa/merging-intervals/",
        "problems": [
            (57, "Insert Interval", "insert-interval", M, False),
            (56, "Merge Intervals", "merge-intervals", M, False),
            (435, "Non-overlapping Intervals", "non-overlapping-intervals", M, False),
            (252, "Meeting Rooms", "meeting-rooms", E, True),
            (253, "Meeting Rooms II", "meeting-rooms-ii", M, True),
            (1851, "Minimum Interval to Include Each Query", "minimum-interval-to-include-each-query", H, False),
        ],
    },
    {
        "id": "greedy", "title": "Greedy", "tier": "advanced", "requires": ["heap-priority-queue"],
        "tag": "greedy", "gfg": "https://www.geeksforgeeks.org/dsa/greedy-algorithms/",
        "problems": [
            (53, "Maximum Subarray", "maximum-subarray", M, False),
            (55, "Jump Game", "jump-game", M, False),
            (45, "Jump Game II", "jump-game-ii", M, False),
            (134, "Gas Station", "gas-station", M, False),
            (846, "Hand of Straights", "hand-of-straights", M, False),
            (1899, "Merge Triplets to Form Target Triplet", "merge-triplets-to-form-target-triplet", M, False),
            (763, "Partition Labels", "partition-labels", M, False),
            (678, "Valid Parenthesis String", "valid-parenthesis-string", M, False),
        ],
    },
    {
        "id": "advanced-graphs", "title": "Advanced Graphs", "tier": "advanced", "requires": ["heap-priority-queue", "graphs"],
        "tag": "shortest-path", "gfg": "https://www.geeksforgeeks.org/dsa/graph-data-structure-and-algorithms/",
        "problems": [
            (743, "Network Delay Time", "network-delay-time", M, False),
            (332, "Reconstruct Itinerary", "reconstruct-itinerary", H, False),
            (1584, "Min Cost to Connect All Points", "min-cost-to-connect-all-points", M, False),
            (778, "Swim in Rising Water", "swim-in-rising-water", H, False),
            (269, "Alien Dictionary", "alien-dictionary", H, True),
            (787, "Cheapest Flights Within K Stops", "cheapest-flights-within-k-stops", M, False),
        ],
    },
    {
        "id": "dp-2d", "title": "2-D Dynamic Programming", "tier": "advanced", "requires": ["graphs", "dp-1d"],
        "tag": "dynamic-programming", "gfg": "https://www.geeksforgeeks.org/dsa/dynamic-programming/",
        "problems": [
            (62, "Unique Paths", "unique-paths", M, False),
            (1143, "Longest Common Subsequence", "longest-common-subsequence", M, False),
            (309, "Best Time to Buy and Sell Stock with Cooldown", "best-time-to-buy-and-sell-stock-with-cooldown", M, False),
            (518, "Coin Change II", "coin-change-ii", M, False),
            (494, "Target Sum", "target-sum", M, False),
            (97, "Interleaving String", "interleaving-string", M, False),
            (329, "Longest Increasing Path in a Matrix", "longest-increasing-path-in-a-matrix", H, False),
            (72, "Edit Distance", "edit-distance", M, False),
            (115, "Distinct Subsequences", "distinct-subsequences", H, False),
            (312, "Burst Balloons", "burst-balloons", H, False),
            (10, "Regular Expression Matching", "regular-expression-matching", H, False),
        ],
    },
    {
        "id": "bit-manipulation", "title": "Bit Manipulation", "tier": "advanced", "requires": ["dp-1d"],
        "tag": "bit-manipulation", "gfg": "https://www.geeksforgeeks.org/dsa/bitwise-algorithms/",
        "problems": [
            (136, "Single Number", "single-number", E, False),
            (191, "Number of 1 Bits", "number-of-1-bits", E, False),
            (338, "Counting Bits", "counting-bits", E, False),
            (190, "Reverse Bits", "reverse-bits", E, False),
            (268, "Missing Number", "missing-number", E, False),
            (371, "Sum of Two Integers", "sum-of-two-integers", M, False),
            (7, "Reverse Integer", "reverse-integer", M, False),
        ],
    },
    {
        "id": "math-geometry", "title": "Math & Geometry", "tier": "advanced", "requires": ["dp-2d", "bit-manipulation"],
        "tag": "math", "gfg": "https://www.geeksforgeeks.org/dsa/mathematical-algorithms/",
        "problems": [
            (48, "Rotate Image", "rotate-image", M, False),
            (54, "Spiral Matrix", "spiral-matrix", M, False),
            (73, "Set Matrix Zeroes", "set-matrix-zeroes", M, False),
            (202, "Happy Number", "happy-number", E, False),
            (66, "Plus One", "plus-one", E, False),
            (50, "Pow(x, n)", "powx-n", M, False),
            (43, "Multiply Strings", "multiply-strings", M, False),
            (2013, "Detect Squares", "detect-squares", M, False),
        ],
    },
]

TIERS = [
    ("foundations", "Foundations", "Arrays, pointers, windows, stacks, binary search and linked lists: the tools everything else is built from", "violet"),
    ("trees", "Trees and recursion", "Trees, tries, heaps and backtracking: recursion that branches", "blue"),
    ("advanced", "Graphs, DP and the rest", "Graphs, dynamic programming, intervals, greedy, bits and maths", "teal"),
]

if __name__ == "__main__":
    ids = [t["id"] for t in TOPICS]
    assert len(ids) == len(set(ids)), "duplicate topic id"
    nums = [p[0] for t in TOPICS for p in t["problems"]]
    assert len(nums) == len(set(nums)), "a problem appears twice"
    for t in TOPICS:
        for r in t["requires"]:
            assert r in ids, (t["id"], r)
    counts = {lv: sum(1 for t in TOPICS for p in t["problems"] if p[3] == lv) for lv in (E, M, H)}
    print(len(nums), "problems", counts, "premium:", sum(1 for t in TOPICS for p in t["problems"] if p[4]))
