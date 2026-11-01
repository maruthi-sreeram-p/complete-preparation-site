"""Names available inside the `!py` checks of tools/gate/mcq/*.txt (see build_gate.py)."""
import collections
import functools
import heapq
import itertools
import math
import re
import struct
from fractions import Fraction
from math import ceil, comb, factorial, floor, gcd, log2, perm, sqrt  # noqa: F401


def num(text):
    """The number in an option such as '1,024', '3/4', '2.5 ns' or '40%' (the first token)."""
    token = str(text).split()[0].replace(",", "").replace("−", "-").rstrip("%")
    return Fraction(token) if "/" in token else float(token) if "." in token else int(token)


def phi(n):
    """Euler's totient."""
    return sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)


def stirling2(n, k):
    """Partitions of an n-set into exactly k non-empty blocks."""
    return sum((-1) ** j * comb(k, j) * (k - j) ** n for j in range(k + 1)) // factorial(k)


def bell(n):
    return sum(stirling2(n, k) for k in range(n + 1))


def derangements(n):
    return sum((-1) ** k * factorial(n) // factorial(k) for k in range(n + 1))


def catalan(n):
    return comb(2 * n, n) // (n + 1)


def lcm(*values):
    return functools.reduce(lambda a, b: a * b // math.gcd(a, b), values)


def det(matrix):
    """Exact determinant of a square matrix of ints or Fractions."""
    m = [[Fraction(x) for x in row] for row in matrix]
    n, sign, result = len(m), 1, Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if m[r][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
            sign = -sign
        result *= m[col][col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            m[r] = [a - factor * b for a, b in zip(m[r], m[col])]
    return sign * result


def rank(matrix):
    """Exact rank of a matrix of ints or Fractions."""
    m = [[Fraction(x) for x in row] for row in matrix]
    rows, cols, r = len(m), len(m[0]), 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if m[i][c] != 0), None)
        if pivot is None:
            continue
        m[r], m[pivot] = m[pivot], m[r]
        for i in range(rows):
            if i != r and m[i][c] != 0:
                factor = m[i][c] / m[r][c]
                m[i] = [a - factor * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def integrate(f, a, b, n=20000):
    """Simpson's rule, accurate enough to check the answers of definite-integral questions."""
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += f(a + i * h) * (4 if i % 2 else 2)
    return total * h / 3


def deriv(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def close(a, b, tol=1e-4):
    return abs(float(a) - float(b)) < tol


def prime_implicants(minterms, n):
    """Quine-McCluskey. Minterms (including don't-cares) are ints; a cube is (value, mask of '-' bits)."""
    cubes = {(m, 0) for m in minterms}
    primes = set()
    while cubes:
        new, used = set(), set()
        listed = sorted(cubes)
        for i, (v1, m1) in enumerate(listed):
            for v2, m2 in listed[i + 1:]:
                diff = v1 ^ v2
                if m1 == m2 and diff and diff & (diff - 1) == 0:
                    new.add((v1 & ~diff, m1 | diff))
                    used.update({(v1, m1), (v2, m2)})
        primes |= cubes - used
        cubes = new
    return primes


def covers(cube, minterm):
    value, mask = cube
    return minterm & ~mask == value


def literals(cube, n):
    return n - bin(cube[1]).count("1")


def essential_primes(minterms, dont_cares, n):
    primes = prime_implicants(list(minterms) + list(dont_cares), n)
    return {p for m in minterms for p in [[q for q in primes if covers(q, m)]] if len(p) == 1 for p in p}


def min_sop(minterms, dont_cares, n):
    """-> (number of product terms, number of literals, cubes) of a minimum SOP: fewest terms, then fewest literals."""
    primes = sorted(prime_implicants(list(minterms) + list(dont_cares), n))
    for k in range(1, len(primes) + 1):
        best = None
        for combo in itertools.combinations(primes, k):
            if all(any(covers(c, m) for c in combo) for m in minterms):
                lits = sum(literals(c, n) for c in combo)
                if best is None or lits < best[1]:
                    best = (k, lits, combo)
        if best:
            return best
    return None


def cube_str(cube, n, names="ABCDEFGH"):
    """A cube printed as a product term, e.g. A'C."""
    value, mask = cube
    return "".join(names[i] + ("" if value >> (n - 1 - i) & 1 else "'") for i in range(n) if not mask >> (n - 1 - i) & 1) or "1"


def cache_misses(blocks, sets, ways, policy="LRU"):
    """Misses of a set-associative cache (sets=1: fully associative, ways=1: direct-mapped) on a list of block numbers."""
    store = [[] for _ in range(sets)]
    misses = 0
    for b in blocks:
        s = store[b % sets]
        if b in s:
            if policy == "LRU":
                s.remove(b)
                s.append(b)
            continue
        misses += 1
        if len(s) == ways:
            s.pop(0)
        s.append(b)
    return misses


def booth_ops(multiplier, bits):
    """Number of add/subtract steps Booth's algorithm performs for a multiplier given as a bit string."""
    padded = multiplier + "0"
    return sum(1 for i in range(bits) if padded[bits - 1 - i] != padded[bits - i])


def bst_build(keys):
    """-> (root, {key: [left, right]}) for keys inserted into a BST in the given order."""
    root, nodes = None, {}
    for k in keys:
        nodes[k] = [None, None]
        if root is None:
            root = k
            continue
        cur = root
        while True:
            side = 0 if k < cur else 1
            if nodes[cur][side] is None:
                nodes[cur][side] = k
                break
            cur = nodes[cur][side]
    return root, nodes


def bst_height(keys):
    """Height in edges (a single node has height 0)."""
    root, nodes = bst_build(keys)
    h = lambda n: -1 if n is None else 1 + max(h(nodes[n][0]), h(nodes[n][1]))  # noqa: E731
    return h(root)


def postorder(root, nodes):
    if root is None:
        return []
    return postorder(nodes[root][0], nodes) + postorder(nodes[root][1], nodes) + [root]


def can_pop(sequence, n):
    """Can 1..n, pushed in order, be popped in this order?"""
    stack, nxt = [], 1
    for want in sequence:
        while (not stack or stack[-1] != want) and nxt <= n:
            stack.append(nxt)
            nxt += 1
        if not stack or stack[-1] != want:
            return False
        stack.pop()
    return True


def heap_insert_all(values):
    """Max-heap built by repeated insertion (sift up); 0-based list."""
    a = []
    for v in values:
        a.append(v)
        i = len(a) - 1
        while i > 0 and a[(i - 1) // 2] < a[i]:
            a[(i - 1) // 2], a[i] = a[i], a[(i - 1) // 2]
            i = (i - 1) // 2
    return a


def is_max_heap(a):
    return all(a[(i - 1) // 2] >= a[i] for i in range(1, len(a)))


def lcs_len(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if x == y else max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]


def matrix_chain(p):
    """Minimum scalar multiplications for matrices with dimensions p[i-1] x p[i]."""
    n = len(p) - 1
    m = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            m[i][j] = min(m[i][k] + m[k + 1][j] + p[i] * p[k + 1] * p[j + 1] for k in range(i, j))
    return m[0][n - 1]


def knapsack01(items, capacity):
    """items: (weight, value) pairs."""
    best = [0] * (capacity + 1)
    for w, v in items:
        for c in range(capacity, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[capacity]


def lis_len(a):
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)


def coin_ways(coins, amount):
    ways = [1] + [0] * amount
    for c in coins:
        for x in range(c, amount + 1):
            ways[x] += ways[x - c]
    return ways[amount]


def huffman(freqs):
    """-> (total weighted path length, {index: code length}) for a Huffman tree."""
    heap = [(f, i, [i]) for i, f in enumerate(freqs)]
    heapq.heapify(heap)
    depth = {i: 0 for i in range(len(freqs))}
    total, counter = 0, len(freqs)
    while len(heap) > 1:
        f1, _, s1 = heapq.heappop(heap)
        f2, _, s2 = heapq.heappop(heap)
        for i in s1 + s2:
            depth[i] += 1
        total += f1 + f2
        heapq.heappush(heap, (f1 + f2, counter, s1 + s2))
        counter += 1
    return total, depth


def dijkstra(graph, source):
    """graph: {u: [(v, w), ...]} with non-negative weights -> {vertex: distance}."""
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, math.inf):
            continue
        for v, w in graph.get(u, []):
            if d + w < dist.get(v, math.inf):
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist


def kruskal(n, edges):
    """edges: (w, u, v) with vertices 0..n-1 -> (total weight, chosen edges)."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total, chosen = 0, []
    for w, u, v in sorted(edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            chosen.append((w, u, v))
    return total, chosen


def scc_count(n, edges):
    """Strongly connected components of a directed graph (vertices 0..n-1), by mutual reachability."""
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return len({frozenset(j for j in range(n) if reach[i][j] and reach[j][i]) for i in range(n)})


def strings_upto(alphabet, maxlen):
    out = ['']
    frontier = ['']
    for _ in range(maxlen):
        frontier = [s + c for s in frontier for c in alphabet]
        out += frontier
    return out


def min_dfa_states(pred, alphabet='ab', prefix_len=8, suffix_len=8):
    """Number of Myhill-Nerode classes of a language, i.e. the states of its minimal complete DFA.
    Prefixes are told apart by how they behave on all suffixes up to suffix_len."""
    suffixes = strings_upto(alphabet, suffix_len)
    return len({tuple(pred(p + s) for s in suffixes) for p in strings_upto(alphabet, prefix_len)})


def regex_lang(pattern, alphabet='ab', maxlen=8):
    """Strings (up to maxlen) matched by a Python regex."""
    compiled = re.compile(pattern)
    return {s for s in strings_upto(alphabet, maxlen) if compiled.fullmatch(s)}


def pred_lang(pred, alphabet='ab', maxlen=8):
    return {s for s in strings_upto(alphabet, maxlen) if pred(s)}


def cfg_language(rules, start, maxlen):
    """All terminal strings of length <= maxlen derivable from start. rules: {'S': ['aSb', '']}; capitals are nonterminals."""
    lang = {nt: set() for nt in rules}
    changed = True
    while changed:
        changed = False
        for nt, prods in rules.items():
            for prod in prods:
                strings = {''}
                for sym in prod:
                    if sym.isupper():
                        strings = {a + b for a in strings for b in lang[sym] if len(a) + len(b) <= maxlen}
                    else:
                        strings = {a + sym for a in strings if len(a) + 1 <= maxlen}
                    if not strings:
                        break
                new = strings - lang[nt]
                if new:
                    lang[nt] |= new
                    changed = True
    return lang[start]


def count_parses(rules, start, w):
    """Number of distinct parse trees of w (grammars without epsilon or unit-production cycles)."""
    memo = {}

    def nonterminal(A, i, j):
        key = (A, i, j)
        if key not in memo:
            memo[key] = 0
            memo[key] = sum(sequence(prod, 0, i, j) for prod in rules[A])
        return memo[key]

    def sequence(prod, k, i, j):
        if k == len(prod):
            return 1 if i == j else 0
        sym = prod[k]
        if sym.isupper():
            return sum(nonterminal(sym, i, m) * sequence(prod, k + 1, m, j) for m in range(i, j + 1))
        return sequence(prod, k + 1, i + 1, j) if i < j and w[i] == sym else 0

    return nonterminal(start, 0, len(w))


# ---------------------------------------------------------------- compilers
# Grammars: {'E': ['TX'], 'X': ['+TX', '']}; capitals are non-terminals, everything else is a terminal, '' is epsilon.

def first_follow(grammar, start):
    first = {nt: set() for nt in grammar}

    def first_seq(seq):
        out = set()
        for sym in seq:
            if sym.isupper():
                out |= first[sym] - {''}
                if '' not in first[sym]:
                    return out
            else:
                out.add(sym)
                return out
        out.add('')
        return out

    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for p in prods:
                f = first_seq(p)
                if not f <= first[nt]:
                    first[nt] |= f
                    changed = True
    follow = {nt: set() for nt in grammar}
    follow[start].add('$')
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for p in prods:
                for i, sym in enumerate(p):
                    if sym.isupper():
                        rest = first_seq(p[i + 1:])
                        add = rest - {''}
                        if '' in rest:
                            add |= follow[nt]
                        if not add <= follow[sym]:
                            follow[sym] |= add
                            changed = True
    return first, follow, first_seq


def ll1_table(grammar, start):
    """-> (table {(nonterminal, terminal): [productions]}, is_ll1)."""
    _, follow, first_seq = first_follow(grammar, start)
    table = {}
    for nt, prods in grammar.items():
        for p in prods:
            f = first_seq(p)
            for t in (f - {''}) | (follow[nt] if '' in f else set()):
                table.setdefault((nt, t), []).append(p)
    return table, all(len(v) == 1 for v in table.values())


def _closure0(grammar, items):
    items = set(items)
    todo = list(items)
    while todo:
        nt, prod, dot = todo.pop()
        if dot < len(prod) and prod[dot].isupper():
            for p in grammar[prod[dot]]:
                item = (prod[dot], p, 0)
                if item not in items:
                    items.add(item)
                    todo.append(item)
    return frozenset(items)


def lr0_automaton(grammar, start):
    """Augmented with Z -> start. -> (states, transitions {(state index, symbol): state index})."""
    g = dict(grammar)
    g['Z'] = [start]
    states = [_closure0(g, {('Z', start, 0)})]
    trans, todo = {}, [0]
    while todo:
        i = todo.pop()
        symbols = {prod[dot] for _, prod, dot in states[i] if dot < len(prod)}
        for sym in sorted(symbols):
            moved = _closure0(g, {(nt, prod, dot + 1) for nt, prod, dot in states[i] if dot < len(prod) and prod[dot] == sym})
            if moved not in states:
                states.append(moved)
                todo.append(len(states) - 1)
            trans[(i, sym)] = states.index(moved)
    return states, trans


def lr_kind(grammar, start):
    """-> dict of booleans for LR(0), SLR(1), LALR(1), CLR(1) plus state counts."""
    _, follow, first_seq = first_follow(grammar, start)
    states, trans = lr0_automaton(grammar, start)
    lr0 = slr = True
    for i, state in enumerate(states):
        reduces = [(nt, p) for nt, p, d in state if d == len(p) and nt != 'Z']
        shifts = {p[d] for nt, p, d in state if d < len(p) and not p[d].isupper()}
        if reduces and (len(reduces) > 1 or shifts):
            lr0 = False
        seen = set(shifts)
        for nt, p in reduces:
            if follow[nt] & seen:
                slr = False
            seen |= follow[nt]
    g = dict(grammar)
    g['Z'] = [start]

    def closure1(items):
        items = set(items)
        todo = list(items)
        while todo:
            nt, prod, dot, la = todo.pop()
            if dot < len(prod) and prod[dot].isupper():
                f = first_seq(prod[dot + 1:] + la)
                for p in g[prod[dot]]:
                    for t in f - {''}:
                        item = (prod[dot], p, 0, t)
                        if item not in items:
                            items.add(item)
                            todo.append(item)
        return frozenset(items)

    s1 = [closure1({('Z', start, 0, '$')})]
    todo = [0]
    while todo:
        i = todo.pop()
        for sym in sorted({p[d] for _, p, d, _ in s1[i] if d < len(p)}):
            moved = closure1({(nt, p, d + 1, la) for nt, p, d, la in s1[i] if d < len(p) and p[d] == sym})
            if moved not in s1:
                s1.append(moved)
                todo.append(len(s1) - 1)

    def conflict_free(state_items):
        by_la = {}
        for nt, p, d, la in state_items:
            if d == len(p) and nt != 'Z':
                by_la.setdefault(la, []).append((nt, p))
        shifts = {p[d] for _, p, d, _ in state_items if d < len(p) and not p[d].isupper()}
        return all(len(v) == 1 for v in by_la.values()) and not (set(by_la) & shifts)

    clr = all(conflict_free(s) for s in s1)
    merged = {}
    for s in s1:
        core = frozenset((nt, p, d) for nt, p, d, _ in s)
        merged.setdefault(core, set()).update(s)
    lalr = all(conflict_free(s) for s in merged.values())
    return {'lr0': lr0, 'slr': slr, 'lalr': lalr, 'clr': clr, 'lr0_states': len(states), 'clr_states': len(s1), 'lalr_states': len(merged)}


def slr_reductions(grammar, start, tokens):
    """Number of reduce moves an SLR(1) parser makes on tokens (a string of terminals)."""
    _, follow, _ = first_follow(grammar, start)
    states, trans = lr0_automaton(grammar, start)
    action = {}
    for i, state in enumerate(states):
        for nt, p, d in state:
            if d < len(p) and not p[d].isupper():
                action[(i, p[d])] = ('s', trans[(i, p[d])])
            elif d == len(p) and nt == 'Z':
                action[(i, '$')] = ('acc',)
            elif d == len(p):
                for a in follow[nt]:
                    assert (i, a) not in action, 'not SLR(1)'
                    action[(i, a)] = ('r', nt, p)
    stack, pos, reductions = [0], 0, 0
    tokens += '$'
    while True:
        act = action[(stack[-1], tokens[pos])]
        if act[0] == 's':
            stack.append(act[1])
            pos += 1
        elif act[0] == 'r':
            _, nt, p = act
            del stack[len(stack) - len(p):]
            stack.append(trans[(stack[-1], nt)])
            reductions += 1
        else:
            return reductions


TOKEN_RE = re.compile(r'\s*(?:(\d+\.\d+|\d+)|([A-Za-z_]\w*)|("(?:\\.|[^"\\])*")|(>>=|<<=|==|!=|<=|>=|\+\+|--|&&|\|\||[-+*/%=<>!&|^~?:;,.(){}\[\]]))')


def count_tokens(code):
    pos, n = 0, 0
    code = code.rstrip()
    while pos < len(code):
        m = TOKEN_RE.match(code, pos)
        assert m, code[pos:]
        pos = m.end()
        n += 1
    return n


def leaders(n, jumps):
    """Leaders of a 1-based list of n three-address instructions; jumps maps an instruction number to its target."""
    found = {1}
    for i, target in jumps.items():
        found.add(target)
        if i + 1 <= n:
            found.add(i + 1)
    return sorted(found)


def liveness(blocks, succ):
    """blocks: {name: (use, def)}; succ: {name: [successors]} -> (IN, OUT) for live variables."""
    IN = {b: set() for b in blocks}
    OUT = {b: set() for b in blocks}
    changed = True
    while changed:
        changed = False
        for b, (use, defs) in blocks.items():
            out = set().union(*[IN[s] for s in succ.get(b, [])]) if succ.get(b) else set()
            inn = use | (out - defs)
            if out != OUT[b] or inn != IN[b]:
                OUT[b], IN[b] = out, inn
                changed = True
    return IN, OUT


def forward_flow(blocks, pred, meet, init):
    """blocks: {name: (gen, kill)}. meet: 'union' or 'intersection'. init: starting OUT set of every block.
    Blocks with no predecessors get IN = empty. -> (IN, OUT)."""
    OUT = {b: set(init) for b in blocks}
    IN = {b: set() for b in blocks}
    changed = True
    while changed:
        changed = False
        for b, (gen, kill) in blocks.items():
            ps = pred.get(b, [])
            if not ps:
                inn = set()
            elif meet == 'union':
                inn = set().union(*[OUT[p] for p in ps])
            else:
                inn = set.intersection(*[OUT[p] for p in ps])
            out = gen | (inn - kill)
            if inn != IN[b] or out != OUT[b]:
                IN[b], OUT[b] = inn, out
                changed = True
    return IN, OUT


def dag(stmts):
    """stmts: (target, op, a, b) or (target, 'copy', a). -> (leaf count, interior node count) of the DAG of a basic block."""
    node_of, leaves, interior = {}, {}, {}

    def node(x):
        if x in node_of:
            return node_of[x]
        leaves.setdefault(x, ('leaf', x))
        return leaves[x]

    for s in stmts:
        if s[1] == 'copy':
            node_of[s[0]] = node(s[2])
        else:
            key = (s[1], node(s[2]), node(s[3]))
            interior.setdefault(key, key)
            node_of[s[0]] = key
    return len(leaves), len(interior)


# ---------------------------------------------------------------- operating systems

def schedule(procs, policy, quantum=None):
    """procs: [(name, arrival, burst)] or [(name, arrival, burst, priority)] (lower number = higher priority).
    policy: 'fcfs', 'sjf' (non-preemptive), 'srtf', 'prio' (non-preemptive) or 'rr'. -> {name: completion time}."""
    names = [p[0] for p in procs]
    arrival = {p[0]: p[1] for p in procs}
    burst = {p[0]: p[2] for p in procs}
    prio = {p[0]: (p[3] if len(p) > 3 else 0) for p in procs}
    rem = dict(burst)
    done, t = {}, 0
    if policy == 'rr':
        queue, added = [], set()

        def admit():
            for n in sorted(names, key=lambda n: (arrival[n], names.index(n))):
                if arrival[n] <= t and n not in added:
                    added.add(n)
                    queue.append(n)

        while len(done) < len(names):
            admit()
            if not queue:
                t += 1
                continue
            p = queue.pop(0)
            for _ in range(min(quantum, rem[p])):
                t += 1
                rem[p] -= 1
                admit()
            if rem[p] > 0:
                queue.append(p)
            else:
                done[p] = t
        return done
    running = None
    while len(done) < len(names):
        ready = [n for n in names if arrival[n] <= t and n not in done]
        if not ready:
            t += 1
            continue
        if policy == 'srtf' or running is None or running in done:
            key = {'fcfs': lambda n: (arrival[n], names.index(n)),
                   'sjf': lambda n: (burst[n], arrival[n], names.index(n)),
                   'srtf': lambda n: (rem[n], arrival[n], names.index(n)),
                   'prio': lambda n: (prio[n], arrival[n], names.index(n))}[policy]
            running = min(ready, key=key)
        rem[running] -= 1
        t += 1
        if rem[running] == 0:
            done[running] = t
    return done


def sched_stats(procs, policy, quantum=None):
    """-> (average waiting time, average turnaround time)."""
    done = schedule(procs, policy, quantum)
    tat = {p[0]: done[p[0]] - p[1] for p in procs}
    wt = {p[0]: tat[p[0]] - p[2] for p in procs}
    return sum(wt.values()) / len(procs), sum(tat.values()) / len(procs)


def page_faults(refs, frames, policy):
    """policy: 'FIFO', 'LRU' or 'OPT'."""
    mem, faults = [], 0
    for i, p in enumerate(refs):
        if p in mem:
            if policy == 'LRU':
                mem.remove(p)
                mem.append(p)
            continue
        faults += 1
        if len(mem) == frames:
            if policy in ('FIFO', 'LRU'):
                mem.pop(0)
            else:
                future = refs[i + 1:]
                victim = max(mem, key=lambda x: future.index(x) if x in future else len(future) + 1)
                mem.remove(victim)
        mem.append(p)
    return faults


def disk_head(requests, head, policy, high=199):
    """Total head movement. policy: 'FCFS', 'SSTF', 'SCAN-up' (goes to the last cylinder) or 'LOOK-up'."""
    if policy == 'FCFS':
        order = list(requests)
    elif policy == 'SSTF':
        left, order, cur = list(requests), [], head
        while left:
            nxt = min(left, key=lambda r: abs(r - cur))
            order.append(nxt)
            left.remove(nxt)
            cur = nxt
    else:
        up = sorted(r for r in requests if r >= head)
        down = sorted((r for r in requests if r < head), reverse=True)
        order = up + ([high] if policy == 'SCAN-up' else []) + down
    total, cur = 0, head
    for r in order:
        total += abs(r - cur)
        cur = r
    return total


def safe_sequences(available, allocation, maximum):
    """All safe sequences (lists of process indices) of the Banker's algorithm."""
    n = len(allocation)
    need = [[m - a for m, a in zip(M, A)] for M, A in zip(maximum, allocation)]

    def go(avail, done, seq):
        if len(seq) == n:
            yield list(seq)
            return
        for i in range(n):
            if i not in done and all(x <= y for x, y in zip(need[i], avail)):
                yield from go([a + b for a, b in zip(avail, allocation[i])], done | {i}, seq + [i])

    return list(go(list(available), frozenset(), []))


def race_values(n):
    """Possible final values of a shared counter when two threads each increment it n times without synchronisation
    (each increment is a load followed by a store of load+1)."""
    from functools import lru_cache

    @lru_cache(None)
    def go(c, i1, r1, i2, r2):
        if i1 == 2 * n and i2 == 2 * n:
            return frozenset([c])
        out = set()
        if i1 < 2 * n:
            out |= go(c, i1 + 1, c, i2, r2) if i1 % 2 == 0 else go(r1 + 1, i1 + 1, r1, i2, r2)
        if i2 < 2 * n:
            out |= go(c, i1, r1, i2 + 1, c) if i2 % 2 == 0 else go(r2 + 1, i1, r1, i2 + 1, r2)
        return frozenset(out)

    return sorted(go(0, 0, 0, 0, 0))


# ---------------------------------------------------------------- databases
import sqlite3


def sql(setup, query):
    """Runs the setup script and the query on a fresh in-memory SQLite database -> list of rows."""
    con = sqlite3.connect(':memory:')
    con.executescript(setup)
    rows = con.execute(query).fetchall()
    con.close()
    return rows


def attr_closure(x, fds):
    """Closure of the attribute set x (a string) under fds (a list of (lhs, rhs) strings)."""
    result = set(x)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if set(lhs) <= result and not set(rhs) <= result:
                result |= set(rhs)
                changed = True
    return ''.join(sorted(result))


def candidate_keys(attrs, fds):
    attrs = set(attrs)
    keys = []
    for k in range(1, len(attrs) + 1):
        for combo in itertools.combinations(sorted(attrs), k):
            if set(attr_closure(''.join(combo), fds)) >= attrs and not any(set(key) <= set(combo) for key in keys):
                keys.append(''.join(combo))
    return keys


def count_superkeys(attrs, fds):
    attrs = sorted(attrs)
    return sum(1 for k in range(len(attrs) + 1) for c in itertools.combinations(attrs, k)
               if set(attr_closure(''.join(c), fds)) >= set(attrs))


def normal_form(attrs, fds):
    """Highest normal form among 1NF, 2NF, 3NF, BCNF, judged on all FDs implied by fds."""
    attrs = sorted(attrs)
    keys = candidate_keys(attrs, fds)
    prime = set(''.join(keys))
    bcnf = third = second = True
    for k in range(1, len(attrs)):
        for combo in itertools.combinations(attrs, k):
            x = ''.join(combo)
            closure = set(attr_closure(x, fds))
            determined = closure - set(x)
            if not determined or closure >= set(attrs):
                continue
            bcnf = False
            if any(a not in prime for a in determined):
                third = False
                if any(set(x) < set(key) for key in keys):
                    second = False
    return 'BCNF' if bcnf else '3NF' if third else '2NF' if second else '1NF'


def lossless(attrs, parts, fds):
    """Chase test for a lossless-join decomposition."""
    attrs = sorted(attrs)
    rows = [{a: ('a', a) if a in part else ('b', i, a) for a in attrs} for i, part in enumerate(parts)]
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            for r1, r2 in itertools.combinations(rows, 2):
                if all(r1[a] == r2[a] for a in lhs):
                    for a in rhs:
                        if r1[a] != r2[a]:
                            keep = r1[a] if r1[a][0] == 'a' else r2[a] if r2[a][0] == 'a' else min(r1[a], r2[a])
                            for r in rows:
                                for b in attrs:
                                    if r[b] in (r1[a], r2[a]):
                                        r[b] = keep
                            changed = True
    return any(all(r[a][0] == 'a' for a in attrs) for r in rows)


def preserves_dependencies(parts, fds):
    for lhs, rhs in fds:
        z = set(lhs)
        changed = True
        while changed:
            changed = False
            for part in parts:
                gained = set(attr_closure(''.join(sorted(z & set(part))), fds)) & set(part)
                if not gained <= z:
                    z |= gained
                    changed = True
        if not set(rhs) <= z:
            return False
    return True


def minimal_cover(fds):
    """Canonical cover as a sorted list of (lhs, rhs) with single-attribute right sides."""
    work = [(lhs, a) for lhs, rhs in fds for a in rhs]
    work = list(dict.fromkeys(work))
    for i, (lhs, rhs) in enumerate(work):
        for a in list(lhs):
            reduced = lhs.replace(a, '')
            if reduced and rhs in attr_closure(reduced, work):
                lhs = reduced
        work[i] = (lhs, rhs)
    work = list(dict.fromkeys(work))
    for fd in list(work):
        rest = [f for f in work if f != fd]
        if fd[1] in attr_closure(fd[0], rest):
            work = rest
    return sorted(work)


def fds_equivalent(f, g):
    covers = lambda a, b: all(set(r) <= set(attr_closure(l, a)) for l, r in b)  # noqa: E731
    return covers(f, g) and covers(g, f)


def conflict_serializable(schedule):
    """schedule: [('T1', 'R', 'x'), ...] -> (is conflict serializable, precedence-graph edges)."""
    edges = set()
    for i, (t1, op1, x1) in enumerate(schedule):
        for t2, op2, x2 in schedule[i + 1:]:
            if t1 != t2 and x1 == x2 and 'W' in (op1, op2):
                edges.add((t1, t2))
    nodes = {t for t, _, _ in schedule}
    remaining, es = set(nodes), set(edges)
    while remaining:
        free = [n for n in remaining if not any(b == n for a, b in es if a in remaining)]
        if not free:
            return False, edges
        remaining -= {free[0]}
    return True, edges


EMP_SETUP = """
CREATE TABLE Emp(eid INT, name TEXT, dept TEXT, salary INT);
INSERT INTO Emp VALUES (1,'Asha','CS',50),(2,'Ben','CS',60),(3,'Chitra','EE',55),(4,'Dev','EE',NULL),(5,'Esha','ME',70),(6,'Farid','CS',60);
CREATE TABLE Dept(did INT, dname TEXT);
INSERT INTO Dept VALUES (1,'CS'),(2,'EE'),(3,'ME'),(4,'CE');
"""


# ---------------------------------------------------------------- networks
import ipaddress  # noqa: E402


def crc_remainder(data, generator):
    """Remainder (as a bit string of len(generator) - 1 bits) of data followed by zeros, divided by generator, modulo 2."""
    r = len(generator) - 1
    bits = list(data + '0' * r)
    for i in range(len(data)):
        if bits[i] == '1':
            for j, g in enumerate(generator):
                bits[i + j] = str(int(bits[i + j]) ^ int(g))
    return ''.join(bits[-r:])


def bit_stuff(bits):
    """Insert a 0 after every run of five consecutive 1s."""
    out, run = [], 0
    for b in bits:
        out.append(b)
        run = run + 1 if b == '1' else 0
        if run == 5:
            out.append('0')
            run = 0
    return ''.join(out)


def inet_checksum(words):
    """Internet checksum (16-bit one's complement of the one's-complement sum) of a list of 16-bit words."""
    total = sum(words)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def distance_vector_cost(neighbour_costs, advertised):
    """Cost to a destination = min over neighbours of (link cost + neighbour's advertised distance)."""
    return min(neighbour_costs[n] + advertised[n] for n in neighbour_costs)
