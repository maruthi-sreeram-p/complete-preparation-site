"""Technical aptitude: fact questions written by hand; output and pseudocode answers come from actually running the logic."""
import io
from contextlib import redirect_stdout

from core import Q, T, hand

C = "Core Computer Science"

hand(C, "Computer fundamentals", [
    ("How many bits are in a byte?", "8", "4", "16", "2", "A byte is 8 bits."),
    ("Which memory loses its contents when power is off?", "RAM", "SSD", "Hard disk", "ROM", "RAM is volatile."),
    ("What does CPU stand for?", "Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Power Unit", "It runs instructions."),
    ("Which is fastest?", "CPU cache", "RAM", "SSD", "Hard disk", "Cache is closest to the CPU."),
    ("What is 1 KB in bytes, in the binary convention?", "1024", "1000", "512", "2048", "2 to the power 10."),
    ("Which is an input device?", "Keyboard", "Monitor", "Printer", "Speaker", "It sends data in."),
    ("What does an operating system do?", "Manages hardware and runs programs", "Only browses the web", "Only stores files on paper", "Only compiles code", "It manages resources."),
    ("Which number system do computers use internally?", "Binary", "Decimal", "Roman", "Base 12", "Circuits have two states."),
    ("What does a compiler do?", "Translates source code to a lower-level form", "Runs a printer", "Designs chips", "Stores passwords", "Source to machine or bytecode."),
    ("What does ASCII represent?", "Characters as numbers", "Images", "Network routes", "Video frames", "A character encoding."),
    ("Which is an example of system software?", "Linux", "Microsoft Word", "A photo editor", "A web game", "An operating system."),
    ("What does BIOS or UEFI do at start-up?", "Initialises hardware and starts the boot process", "Plays sounds only", "Cleans the disk", "Edits documents", "It runs before the OS."),
])
hand(C, "Data structures & algorithms", [
    ("Which structure works in last-in, first-out order?", "Stack", "Queue", "Tree", "Graph", "LIFO."),
    ("Which structure works in first-in, first-out order?", "Queue", "Stack", "Heap", "Tree", "FIFO."),
    ("What is the time complexity of binary search?", "O(log n)", "O(n)", "O(n log n)", "O(1)", "It halves the range."),
    ("What is the worst-case time of quicksort?", "O(n²)", "O(n log n)", "O(n)", "O(log n)", "With bad pivots."),
    ("What is the worst-case time of merge sort?", "O(n log n)", "O(n²)", "O(n)", "O(log n)", "Always splits evenly."),
    ("Average lookup time in a hash table?", "O(1)", "O(n)", "O(log n)", "O(n²)", "With good hashing."),
    ("Which traversal of a binary search tree gives sorted order?", "Inorder", "Preorder", "Postorder", "Level order", "Left, node, right."),
    ("Which algorithm finds shortest paths with non-negative weights?", "Dijkstra's", "Kruskal's", "Bubble sort", "DFS only", "Greedy shortest paths."),
    ("BFS typically uses which structure?", "Queue", "Stack", "Heap only", "Array of strings", "Level by level."),
    ("DFS typically uses which structure?", "Stack or recursion", "Queue", "Hash table", "Heap", "It goes deep first."),
    ("Accessing an array element by index takes", "O(1)", "O(n)", "O(log n)", "O(n²)", "Direct offset."),
    ("Inserting at the head of a linked list takes", "O(1)", "O(n)", "O(log n)", "O(n²)", "Only pointers change."),
    ("A min-heap's root holds", "The smallest element", "The largest element", "The median", "A random element", "Heap property."),
    ("How many edges does a tree with n nodes have?", "n − 1", "n", "n + 1", "2n", "A connected acyclic graph."),
])
hand(C, "OOP concepts", [
    ("Which concept hides internal data behind methods?", "Encapsulation", "Inheritance", "Polymorphism", "Recursion", "Data stays behind an interface."),
    ("Which concept lets a class reuse another's members?", "Inheritance", "Encapsulation", "Abstraction", "Overflow", "An \"is-a\" relationship."),
    ("Method overriding is an example of", "Runtime polymorphism", "Compile-time polymorphism", "Encapsulation", "Abstraction only", "Chosen at run time."),
    ("Method overloading is an example of", "Compile-time polymorphism", "Runtime polymorphism", "Inheritance", "Encapsulation", "Chosen by signature at compile time."),
    ("Can a Java class extend two classes?", "No", "Yes", "Only if abstract", "Only if final", "Java has single class inheritance."),
    ("Can a Java class implement several interfaces?", "Yes", "No", "Only two", "Only with abstract classes", "That is allowed."),
    ("Can an abstract class be instantiated directly?", "No", "Yes", "Only in static methods", "Only once", "It must be subclassed."),
    ("A final class in Java", "Cannot be extended", "Cannot be instantiated", "Must be abstract", "Has no methods", "It cannot be subclassed."),
    ("A constructor's name is", "The same as its class", "Always init", "Always create", "Any name", "In Java and C++."),
    ("\"this\" in Java refers to", "The current object", "The parent class", "A static field", "The next object", "The current instance."),
    ("\"super\" in Java refers to", "The parent class members", "The current object only", "A static block", "A subclass", "It reaches the parent."),
    ("Which best fits composition?", "A car has an engine", "A car is an engine", "An engine is a car", "A car extends engine", "A \"has-a\" relationship."),
    ("The interface segregation principle says", "Prefer small, specific interfaces", "Use one huge interface", "Avoid interfaces", "Use only abstract classes", "SOLID's \"I\"."),
    ("Which keyword shares one field across instances?", "static", "final", "private", "this", "It belongs to the class."),
])
hand(C, "DBMS & SQL", [
    ("Which SQL clause filters rows before grouping?", "WHERE", "HAVING", "ORDER BY", "LIMIT", "HAVING filters groups."),
    ("Which clause filters groups?", "HAVING", "WHERE", "FROM", "SELECT", "After GROUP BY."),
    ("A primary key must be", "Unique and not null", "Unique and nullable", "Duplicate allowed", "A string", "It identifies a row."),
    ("A foreign key", "References a key in another table", "Encrypts a row", "Is always a primary key of its own table", "Cannot be indexed", "It enforces references."),
    ("Which join returns only matching rows?", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "Matches only."),
    ("What does the A in ACID stand for?", "Atomicity", "Availability", "Accuracy", "Access", "All or nothing."),
    ("What does the I in ACID stand for?", "Isolation", "Integrity", "Index", "Identity", "Transactions do not interfere."),
    ("Third normal form removes", "Transitive dependencies", "All keys", "All joins", "All tables", "Non-key depends only on the key."),
    ("Which command removes all rows but keeps the table?", "TRUNCATE", "DROP", "ALTER", "CREATE", "DROP removes the table too."),
    ("COUNT(column) ignores", "NULL values", "Duplicates", "Zero values", "Strings", "COUNT(*) counts every row."),
    ("Which index type is the default in most relational databases?", "B-tree", "Stack", "Queue", "Linked list", "Good for ranges and equality."),
    ("What does a dirty read mean?", "Reading uncommitted data", "Reading a deleted file", "Reading after a commit", "Reading slowly", "Another transaction may roll back."),
    ("Which keeps duplicates?", "UNION ALL", "UNION", "DISTINCT", "INTERSECT", "UNION removes duplicates."),
    ("Which function finds the highest value?", "MAX", "SUM", "AVG", "COUNT", "An aggregate."),
])
hand(C, "Operating systems", [
    ("A process is", "A program in execution", "A file on disk", "A CPU register", "A network port", "Running instance."),
    ("Threads of one process share", "Memory", "Stack", "Registers", "Program counter", "Each has its own stack."),
    ("A deadlock requires", "Circular wait, among other conditions", "A fast CPU", "Only one process", "No resources", "All four Coffman conditions."),
    ("Which schedule can starve long jobs?", "Shortest Job First", "Round Robin", "FIFO with no priorities", "A single process", "Short jobs keep arriving."),
    ("Round Robin scheduling uses", "A time quantum", "Priorities only", "No preemption", "Job length", "Each gets a slice."),
    ("Virtual memory lets a process", "Use more address space than physical RAM", "Run without a CPU", "Avoid all page faults", "Share one register", "With paging to disk."),
    ("A page fault occurs when", "A page is not in memory", "The disk is full", "A file is deleted", "The CPU overheats", "The OS loads it."),
    ("Thrashing means", "Spending most time paging", "Faster programs", "Deleting files", "Losing power", "Too little memory."),
    ("A semaphore is used for", "Synchronisation", "File naming", "Printing", "Compiling", "It controls access."),
    ("A mutex allows", "One holder at a time", "Unlimited holders", "No holders", "Only reads", "Mutual exclusion."),
    ("Which replacement policy evicts the least recently used page?", "LRU", "FIFO", "Random", "MFU", "By name."),
    ("A context switch", "Saves one task's state and loads another's", "Restarts the computer", "Formats memory", "Changes the user", "It has a cost."),
    ("Which is a kernel-mode action?", "Managing page tables", "Adding two local variables", "Sorting an array in user memory", "Calling a local function", "Only the kernel may do this."),
    ("What is a zombie process?", "A finished process whose parent has not read its exit status", "A hacked process", "A process using all CPU", "A frozen window", "It stays in the process table."),
])
hand(C, "Computer networks", [
    ("How many layers does the OSI model have?", "7", "4", "5", "9", "Physical to Application."),
    ("TCP is", "Connection-oriented and reliable", "Connectionless", "Unreliable by design", "A physical layer", "It uses acknowledgements."),
    ("UDP is", "Connectionless with no delivery guarantee", "Connection-oriented", "Always reliable", "Slower than TCP in every case", "No handshake."),
    ("The default HTTPS port is", "443", "80", "22", "25", "HTTP uses 80."),
    ("DNS converts", "Domain names to IP addresses", "IP addresses to MAC only", "HTML to text", "Files to folders", "A naming system."),
    ("How many bits are in an IPv4 address?", "32", "64", "128", "16", "IPv6 has 128."),
    ("A router works mainly at the", "Network layer", "Physical layer", "Application layer", "Session layer", "It forwards packets by IP."),
    ("A switch works mainly at the", "Data link layer", "Application layer", "Transport layer", "Presentation layer", "It uses MAC addresses."),
    ("Which HTTP method is idempotent and usually reads data?", "GET", "POST", "CONNECT", "PATCH", "GET should not change state."),
    ("The TCP handshake is", "SYN, SYN-ACK, ACK", "ACK, ACK, ACK", "SYN, FIN, ACK", "GET, PUT, POST", "Three steps."),
    ("HTTP status 404 means", "Not found", "OK", "Server error", "Redirect", "4xx is a client error."),
    ("HTTP status 500 means", "Internal server error", "Not found", "OK", "Unauthorized", "5xx is a server error."),
    ("What does TLS provide?", "Encryption and authentication of a connection", "Faster disks", "Domain names", "Routing tables", "It secures HTTP as HTTPS."),
    ("Which protocol assigns IP addresses automatically?", "DHCP", "FTP", "ARP", "SMTP", "ARP maps IP to MAC."),
])


def run(code):
    out = io.StringIO()
    with redirect_stdout(out):
        exec(code, {})
    return out.getvalue().strip()


# Each template shows Java and runs the same logic in Python, so the answer is real output.
@T(C, "Programming & output prediction")
def _(r):
    n, k = r.randint(3, 12), r.randint(1, 4)
    java = f"int s = 0;\nfor (int i = 1; i <= {n}; i += {k}) {{\n    s += i;\n}}\nSystem.out.println(s);"
    ans = run(f"s=0\nfor i in range(1,{n}+1,{k}):\n    s+=i\nprint(s)")
    return Q(f"What does this Java code print?\n\n```java\n{java}\n```", ans, f"It adds 1, {1 + k}, ... up to {n}, giving {ans}.", [int(ans) + 1, int(ans) + n, max(int(ans) - k, 1)])


@T(C, "Programming & output prediction")
def _(r):
    a, b = r.randint(10, 99), r.randint(2, 9)
    return Q(f"What does this Java code print?\n\n```java\nSystem.out.println({a} / {b} + \" \" + {a} % {b});\n```", f"{a // b} {a % b}", "Integer division drops the fraction, and % gives the remainder.", [f"{a / b:.1f} {a % b}", f"{a // b + 1} {a % b}", f"{a % b} {a // b}"])


@T(C, "Programming & output prediction")
def _(r):
    a, b = r.randint(1, 9), r.randint(1, 9)
    return Q(f"What does this Java code print?\n\n```java\nSystem.out.println({a} + {b} + \"x\" + {a} + {b});\n```", f"{a + b}x{a}{b}", "Left to right: numbers add until a String appears; after that everything is concatenated.", [f"{a}{b}x{a}{b}", f"{a + b}x{a + b}", f"{a}{b}x{a + b}"])


@T(C, "Programming & output prediction")
def _(r):
    x = r.randint(1, 30)
    return Q(f"What does this Java code print?\n\n```java\nint x = {x};\nint y = x++ + ++x;\nSystem.out.println(y);\n```", 2 * x + 2, f"x++ gives {x}, and x becomes {x + 1}. ++x makes it {x + 2}. Sum = {2 * x + 2}.", [2 * x, 2 * x + 1, 2 * x + 3])


@T(C, "Programming & output prediction")
def _(r):
    n = r.randint(3, 12)
    ans = 1
    for i in range(2, n + 1):
        ans *= i
    return Q(f"What does this Java code print?\n\n```java\nlong f(int n) {{ return n <= 1 ? 1 : n * f(n - 1); }}\n// ...\nSystem.out.println(f({n}));\n```", ans, f"It computes {n}! = {ans}.", [ans // n, ans * (n + 1), ans + n])


@T(C, "Programming & output prediction")
def _(r):
    a = r.sample(range(1, 30), r.randint(4, 7))
    i = r.randint(0, len(a) - 1)
    return Q(f"What does this Java code print?\n\n```java\nint[] a = {{{', '.join(map(str, a))}}};\nSystem.out.println(a[{i}] + a.length);\n```", a[i] + len(a), f"a[{i}] = {a[i]}, and the length is {len(a)}.", [a[i], len(a), a[i] + len(a) - 1])


@T(C, "Programming & output prediction")
def _(r):
    s = r.choice(["javatrail", "interview", "backend", "spring", "database", "network", "recursion", "algorithm"])
    i, j = sorted(r.sample(range(0, len(s)), 2))
    return Q(f"What does this Java code print?\n\n```java\nSystem.out.println(\"{s}\".substring({i}, {j}));\n```", s[i:j] or "(empty)", "substring(i, j) includes index i and excludes index j.", [s[i:j + 1], s[i + 1:j + 1] or "x", s[max(i - 1, 0):j], s[i:j - 1] or "y", s[i:] + "!", s[:j] + "?", s])


@T(C, "Logical & pseudocode questions")
def _(r):
    a, b = r.randint(12, 200), r.randint(12, 200)
    x, y = a, b
    while y:
        x, y = y, x % y
    return Q(f"What is printed?\n\n```text\na = {a}, b = {b}\nwhile b != 0:\n    t = b\n    b = a mod b\n    a = t\nprint a\n```", x, f"This is Euclid's algorithm. The HCF is {x}.", [x + 1, x * 2, a * b // x])


@T(C, "Logical & pseudocode questions")
def _(r):
    n = r.randint(100, 99999)
    k = r.choice(["sum", "reverse", "count"])
    if k == "sum":
        ans = sum(map(int, str(n)))
        return Q(f"What is printed?\n\n```text\nn = {n}, s = 0\nwhile n > 0:\n    s = s + (n mod 10)\n    n = n div 10\nprint s\n```", ans, f"It adds the digits: {ans}.", [ans + 1, ans + 9, len(str(n))])
    if k == "reverse":
        ans = int(str(n)[::-1])
        return Q(f"What is printed?\n\n```text\nn = {n}, r = 0\nwhile n > 0:\n    r = r * 10 + (n mod 10)\n    n = n div 10\nprint r\n```", ans, f"It reverses the digits: {ans}.", [n, ans + 1, ans + 10])
    return Q(f"What is printed?\n\n```text\nn = {n}, c = 0\nwhile n > 0:\n    c = c + 1\n    n = n div 10\nprint c\n```", len(str(n)), "It counts the digits.", [len(str(n)) + 1, len(str(n)) - 1, sum(map(int, str(n)))])


@T(C, "Logical & pseudocode questions")
def _(r):
    n = r.randint(2, 10)
    a = r.randint(2, 3)
    c = 0
    for i in range(n):
        for j in range(i + 1):
            c += a
    return Q(f"What is printed?\n\n```text\nc = 0\nfor i = 0 to {n - 1}:\n    for j = 0 to i:\n        c = c + {a}\nprint c\n```", c, f"The inner loop runs 1 + 2 + ... + {n} = {n * (n + 1) // 2} times. Each adds {a}.", [n * n * a, c + a, c - a])


@T(C, "Logical & pseudocode questions")
def _(r):
    a = r.sample(range(1, 60), r.randint(5, 8))
    kind = r.choice(["max", "evens", "sum"])
    if kind == "max":
        return Q(f"What is printed?\n\n```text\na = {a}\nm = a[0]\nfor each x in a:\n    if x > m: m = x\nprint m\n```", max(a), "It tracks the largest value.", [min(a), sum(a), a[0] if a[0] != max(a) else a[1]])
    if kind == "evens":
        ans = sum(1 for x in a if x % 2 == 0)
        return Q(f"What is printed?\n\n```text\na = {a}\nc = 0\nfor each x in a:\n    if x mod 2 = 0: c = c + 1\nprint c\n```", ans, "It counts the even numbers.", [x for x in range(0, 9) if x != ans][:5])
    return Q(f"What is printed?\n\n```text\na = {a}\ns = 0\nfor each x in a:\n    s = s + x\nprint s\n```", sum(a), "It adds all the values.", [sum(a) + 1, sum(a) - a[0], max(a)])
