@part tries | Tries | trees
## The idea

A **trie** (prefix tree) stores strings one character per edge. All words that share a prefix share the path from the root. That makes **prefix questions** cost O(length of the prefix), no matter how many words are stored: "does any word start with `pre`?", "list all words with this prefix", "does this string match a pattern with wildcards?".

A `HashSet<String>` answers "is this exact word present?" just as fast, but it cannot answer prefix questions without scanning every word. That contrast is the whole case for a trie.

| Operation | Trie | `HashSet<String>` |
|---|---|---|
| Insert / exact search a word of length L | O(L) | O(L) to hash |
| Does any word start with prefix p? | O(len p) | O(n · L), scan all |
| Enumerate all words with a prefix | O(len p + output) | O(n · L) |
| Memory | Up to 26 pointers per node | Strings only |

!tip Signal words :: "prefix", "autocomplete", "dictionary of words", "word search in a grid with many words", "wildcard '.'", "longest common prefix".

## The Java toolkit and templates

A node holds an array of children (26 for lowercase letters) and a flag marking the end of a word. Use a `HashMap<Character, Node>` instead when the alphabet is large or unknown.

```java TrieTemplates.java
import java.util.*;

public class TrieTemplates {

    static class Trie {
        private static class Node {
            final Node[] next = new Node[26];
            boolean word;                                   // a word ends at this node
        }

        private final Node root = new Node();

        void insert(String word) {
            Node node = root;
            for (char c : word.toCharArray()) {
                int i = c - 'a';
                if (node.next[i] == null) node.next[i] = new Node();
                node = node.next[i];
            }
            node.word = true;
        }

        boolean search(String word) {
            Node node = find(word);
            return node != null && node.word;               // the path exists AND a word ends here
        }

        boolean startsWith(String prefix) {
            return find(prefix) != null;
        }

        private Node find(String s) {
            Node node = root;
            for (char c : s.toCharArray()) {
                node = node.next[c - 'a'];
                if (node == null) return null;
            }
            return node;
        }

        /** Design Add and Search Words: '.' matches any one letter, so try every child there. */
        boolean searchWithDots(String pattern) {
            return match(root, pattern, 0);
        }

        private boolean match(Node node, String pattern, int i) {
            if (node == null) return false;
            if (i == pattern.length()) return node.word;
            char c = pattern.charAt(i);
            if (c != '.') return match(node.next[c - 'a'], pattern, i + 1);
            for (Node child : node.next) {
                if (child != null && match(child, pattern, i + 1)) return true;
            }
            return false;
        }

        /** All stored words that start with the prefix, in alphabetical order. */
        List<String> wordsWithPrefix(String prefix) {
            List<String> out = new ArrayList<>();
            Node start = find(prefix);
            if (start != null) collect(start, new StringBuilder(prefix), out);
            return out;
        }

        private void collect(Node node, StringBuilder path, List<String> out) {
            if (node.word) out.add(path.toString());
            for (int i = 0; i < 26; i++) {
                if (node.next[i] == null) continue;
                path.append((char) ('a' + i));
                collect(node.next[i], path, out);
                path.deleteCharAt(path.length() - 1);       // backtrack
            }
        }
    }
}
```

**What to notice.** `search` and `startsWith` share `find`; the only difference is the final `word` check, which is also the most common bug: forgetting it makes `search("app")` succeed when only `"apple"` was inserted.

### Word Search II: a trie plus backtracking

Searching a grid for many words one at a time repeats work. Build a trie of all the words, then run one DFS from every cell, walking the trie in step with the grid: stop a path the moment the current letters are not a prefix of any word. Store the complete word at its end node, mark visited cells in place while exploring, and **remove found words and empty branches** from the trie to prune future searches. That pruning is what makes the hard version pass.

## Pitfalls and interview angle

- **Forgetting the end-of-word flag**, so prefixes count as words.
- **Memory.** `Node[26]` per node is large when words are few and long. A `HashMap` or a compressed (radix) trie is smaller.
- **Alphabet assumptions.** `c - 'a'` throws `ArrayIndexOutOfBoundsException` on uppercase letters or digits.
- **Recursion depth** equals word length, which is fine, but wildcard search can branch 26 ways per level.

!interview Interview angle: When would you choose a trie over a hash set? :: When queries depend on prefixes: autocomplete, "is there any word starting with ...", or pruning a search early as in Word Search II. For plain membership tests a hash set is simpler and uses less memory.

!keypoints A trie shares prefixes, so prefix queries cost O(length of the prefix) ;; Each node needs children plus an end-of-word flag ;; `search` is `find` plus a check of the flag; `startsWith` is just `find` ;; Wildcards turn a search into DFS over children ;; Word Search II = trie plus grid DFS, pruning as words are found ;; Use a map for children when the alphabet is not tiny

?? Why does a trie answer "does any word start with this prefix?" faster than a hash set?
=> Following the prefix's characters down the trie takes O(length of the prefix) and the existence of the path is the answer. A hash set has no way to ask about prefixes, so it would scan every stored word.

?? What goes wrong if `search` only checks that the path exists?
=> It returns true for any prefix of a stored word, for example `search("app")` after inserting only "apple". You must also check that a word ends at the final node.

?? How does a trie speed up Word Search II compared with running Word Search for each word?
=> One DFS explores the grid once for all words together, and a path is abandoned as soon as its letters are not a prefix of any word in the trie. Searching per word repeats the grid exploration for every word.
