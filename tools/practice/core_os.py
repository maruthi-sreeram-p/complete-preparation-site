"""Practice subject: Operating Systems. Numeric answers are computed here, so a wrong figure cannot ship."""
import sys
from pathlib import Path

from common import subject, written

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))
from core_helpers import page_faults  # noqa: E402

# ---- CPU scheduling simulators: processes are (name, arrival, burst)
PROCS = [("P1", 0, 8), ("P2", 1, 4), ("P3", 2, 9), ("P4", 3, 5)]


def waiting_times(order_fn):
    """order_fn(procs) -> {name: completion time}; waiting = completion - arrival - burst."""
    done = order_fn(PROCS)
    return {n: done[n] - a - b for n, a, b in PROCS}


def fcfs(procs):
    t, done = 0, {}
    for n, a, b in sorted(procs, key=lambda p: p[1]):
        t = max(t, a) + b
        done[n] = t
    return done


def sjf(procs):  # non-preemptive shortest job first
    t, done, left = 0, {}, list(procs)
    while left:
        ready = [p for p in left if p[1] <= t] or [min(left, key=lambda p: p[1])]
        n, a, b = min(ready, key=lambda p: (p[2], p[1]))
        t = max(t, a) + b
        done[n] = t
        left.remove((n, a, b))
    return done


def srtf(procs):  # preemptive shortest remaining time first
    remaining = {n: b for n, a, b in procs}
    t, done = 0, {}
    while remaining:
        ready = [n for n, a, b in procs if a <= t and n in remaining]
        if not ready:
            t += 1
            continue
        n = min(ready, key=lambda x: (remaining[x], x))
        remaining[n] -= 1
        t += 1
        if remaining[n] == 0:
            del remaining[n]
            done[n] = t
    return done


def round_robin(procs, quantum):
    remaining = {n: b for n, a, b in procs}
    arrival = {n: a for n, a, b in procs}
    queue, t, done, pending = [], 0, {}, sorted(procs, key=lambda p: p[1])
    admitted = set()

    def admit(now):
        for n, a, b in pending:
            if a <= now and n not in admitted:
                admitted.add(n)
                queue.append(n)

    admit(0)
    while queue or len(admitted) < len(procs):
        if not queue:
            t += 1
            admit(t)
            continue
        n = queue.pop(0)
        run = min(quantum, remaining[n])
        for _ in range(run):
            t += 1
            admit(t)
        remaining[n] -= run
        if remaining[n]:
            queue.append(n)
        else:
            done[n] = t
    return done


def avg(order_fn):
    w = waiting_times(order_fn)
    return sum(w.values()) / len(w)


W_FCFS, W_SJF, W_SRTF, W_RR = avg(fcfs), avg(sjf), avg(srtf), avg(lambda p: round_robin(p, 4))
assert (W_FCFS, W_SJF, W_SRTF) == (8.75, 7.75, 6.5), (W_FCFS, W_SJF, W_SRTF)

REFS = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
F_FIFO, F_LRU, F_OPT = (page_faults(REFS, 3, p) for p in ("FIFO", "LRU", "OPT"))
assert (F_FIFO, F_LRU, F_OPT) == (10, 9, 7)

QUESTIONS = [
    written("os-process-thread", "Process or thread?", "Easy",
        "What is the difference between a process and a thread? Why are threads called lightweight?",
        "A **process** is a program in execution with its **own address space** (code, heap, stack), open files and OS resources. A **thread** is a unit of execution **inside** a process: threads of one process **share** the code, heap and open files, but each has its own **stack, program counter and registers**.\n\n"
        "Threads are lightweight because creating one and switching between threads of the same process is cheaper: no new address space, and no switch of page tables (and fewer TLB flushes). Communication is also cheaper (shared memory), but that sharing is why threads need synchronisation. Processes are isolated: one crashing does not corrupt another."),
    written("os-context-switch", "What is a context switch?", "Medium",
        "Describe a context switch and say why it is pure overhead.",
        "A context switch saves the state of the running process or thread (program counter, registers, stack pointer, and for processes the memory-management information) in its **process control block (PCB)** and loads the saved state of the next one chosen by the scheduler.\n\n"
        "It is overhead because **no useful work** happens during it, and it has indirect costs too: the CPU caches and TLB hold the old process's data, so the new one suffers misses (a process switch costs more than a thread switch within one process because the address space changes). Too-short time slices therefore waste throughput."),
    written("os-scheduling-numeric", "Average waiting time of scheduling algorithms", "Medium",
        "Four processes arrive and need CPU bursts: P1 arrives at 0 with burst 8, P2 at 1 with 4, P3 at 2 with 9, P4 at 3 with 5. Compute the average waiting time under FCFS, non-preemptive SJF and SRTF (preemptive SJF).",
        f"Waiting time = completion time − arrival time − burst time.\n\n"
        f"- **FCFS** (order P1, P2, P3, P4): P1 0-8, P2 8-12, P3 12-21, P4 21-26. Waiting: 0, 7, 10, 18. Average = **{W_FCFS}**.\n"
        f"- **SJF, non-preemptive:** P1 runs 0-8 (nothing else has arrived that is shorter when it starts); then the shortest ready job each time: P2 8-12, P4 12-17, P3 17-26. Waiting: 0, 7, 15, 9. Average = **{W_SJF}**.\n"
        f"- **SRTF** (preemptive): the process with the least remaining time always runs. Average = **{W_SRTF}**.\n\n"
        f"SRTF gives the smallest average waiting time of the three, but it needs to know burst lengths in advance and can starve long jobs. Round robin with quantum 4 gives {W_RR} on this input: fairer response times, worse average waiting.",
        hint="Draw a Gantt chart. For waiting time use completion − arrival − burst."),
    written("os-scheduling-algos", "Choosing a scheduling algorithm", "Medium",
        "Compare FCFS, SJF, Round Robin and priority scheduling. Which suits an interactive system?",
        "- **FCFS:** simple and fair in arrival order, but a long job delays everyone behind it (**convoy effect**).\n"
        "- **SJF / SRTF:** minimises average waiting time, but needs burst predictions and can **starve** long jobs.\n"
        "- **Round Robin:** each process gets a time **quantum** in turn: good **response time**, the usual choice for interactive systems. A quantum that is too large behaves like FCFS; one that is too small wastes time in context switches.\n"
        "- **Priority:** the most important runs first; low-priority processes can starve, fixed by **aging** (raise priority with waiting time).\n\n"
        "Real systems (Linux CFS, Windows) combine ideas: multilevel feedback queues with priorities, time slices and aging."),
    written("os-deadlock", "Deadlock", "Medium",
        "State the four necessary conditions for deadlock and explain how you can prevent it.",
        "Deadlock requires **all four**: (1) **mutual exclusion**: a resource is held by one process at a time; (2) **hold and wait**: a process holds resources while waiting for more; (3) **no preemption**: resources cannot be taken away; (4) **circular wait**: a cycle of processes each waiting for a resource held by the next.\n\n"
        "**Prevention** breaks one condition: request all resources at once (breaks hold-and-wait); allow preemption; or impose a **global order** on resources and always acquire them in that order (breaks circular wait, the most practical). **Avoidance** (Banker's algorithm) grants a request only if the system stays in a safe state. **Detection and recovery** looks for cycles in the wait-for graph and kills or rolls back a process. Many systems simply ignore it and rely on timeouts."),
    written("os-sync", "Mutex, semaphore and monitor", "Medium",
        "What is a race condition? Compare a mutex, a semaphore and a monitor.",
        "A **race condition** happens when the result depends on the unpredictable interleaving of threads, typically two threads doing a read-modify-write on shared data (`count++` is load, add, store). The code that touches shared data is the **critical section**, which must be executed by one thread at a time (mutual exclusion).\n\n"
        "- **Mutex (lock):** binary lock with an owner: only the thread that locked it may unlock it.\n"
        "- **Semaphore:** an integer counter with atomic `wait` (P, decrement, blocking at 0) and `signal` (V, increment). A **counting** semaphore limits access to N identical resources; a binary semaphore resembles a mutex but has no owner and can be used for signalling between threads.\n"
        "- **Monitor:** a language construct that bundles shared data, the procedures that use it and a lock, with **condition variables** (`wait`/`notify`). Java's `synchronized` with `wait/notify` is a monitor."),
    written("os-producer-consumer", "Producer-consumer with semaphores", "Hard",
        "Describe how to solve the bounded-buffer producer-consumer problem with semaphores.",
        "Use three semaphores for a buffer of size N: `empty = N` (free slots), `full = 0` (filled slots), and `mutex = 1` (protects the buffer structure).\n\n"
        "```\nProducer:  wait(empty); wait(mutex); add item; signal(mutex); signal(full)\nConsumer:  wait(full);  wait(mutex); remove item; signal(mutex); signal(empty)\n```\n\n"
        "`empty` makes a producer block when the buffer is full and `full` makes a consumer block when it is empty. `mutex` keeps two threads from corrupting the buffer. **Order matters:** if a producer did `wait(mutex)` before `wait(empty)` and the buffer were full, it would sleep holding the mutex and the consumer could never get in: deadlock. In Java the same pattern is a `BlockingQueue`."),
    written("os-paging-seg", "Paging versus segmentation", "Medium",
        "Compare paging and segmentation. What is internal and external fragmentation?",
        "**Paging** divides logical memory into fixed-size **pages** and physical memory into **frames** of the same size; a page table maps pages to frames. It removes external fragmentation and any page can go in any free frame, but the last page of a process wastes space (**internal fragmentation**, on average half a page).\n\n"
        "**Segmentation** divides memory into variable-size **logical units** (code, stack, heap, a module) with a base and limit each. It matches the programmer's view and supports protection and sharing per segment, but suffers **external fragmentation**: free memory exists in many small holes between segments. Many systems combine them (paged segments).\n\n"
        "**Internal fragmentation** = wasted space *inside* an allocated block. **External fragmentation** = free space that is split into pieces too small to use."),
    written("os-virtual-memory", "Virtual memory and thrashing", "Medium",
        "What is virtual memory and what is thrashing?",
        "**Virtual memory** lets a process use an address space larger than physical memory: only the pages in use (the **working set**) are in RAM and the rest stay on disk. A page-table entry marks a page absent; touching it causes a **page fault**, the OS loads the page (replacing another if needed) and restarts the instruction. Benefits: programs bigger than RAM, process isolation, simple memory sharing, on-demand loading.\n\n"
        "**Thrashing** occurs when processes do not have enough frames for their working sets, so they fault constantly and the system spends most of its time moving pages instead of computing: CPU utilisation collapses. Remedies: reduce the multiprogramming level, give each process enough frames (working-set or page-fault-frequency policies), or add RAM."),
    written("os-page-replacement", "Page replacement", "Medium",
        f"For the reference string {REFS} with 3 frames, count the page faults for FIFO, LRU and the optimal policy.",
        f"- **FIFO** evicts the oldest page: **{F_FIFO}** faults.\n- **LRU** evicts the least recently used page: **{F_LRU}** faults.\n- **Optimal** evicts the page whose next use is farthest in the future: **{F_OPT}** faults (the minimum possible; it needs knowledge of the future, so it is used only as a benchmark).\n\n"
        "FIFO can suffer **Belady's anomaly** (more frames, more faults). LRU and OPT are **stack algorithms** and never do. LRU is approximated in practice with a reference bit (the clock or second-chance algorithm), because exact LRU is expensive to track.",
        hint="Keep the frame contents after every reference and mark each fault."),
    written("os-syscall-modes", "System calls and kernel mode", "Easy",
        "What is a system call? Why does the CPU have user mode and kernel mode?",
        "A **system call** is the controlled entry point through which a user program asks the kernel to do something privileged: read a file, create a process, allocate memory, send a network packet (`read`, `write`, `fork`, `mmap`). The program executes a special instruction (a **trap**) which switches the CPU to **kernel mode**, runs the kernel routine, and returns to user mode.\n\n"
        "Two modes protect the system: in **user mode** a program cannot execute privileged instructions (I/O, changing page tables, disabling interrupts) or touch kernel memory, so a buggy or malicious program cannot crash the machine or read other programs' data. Only the kernel runs in kernel mode."),
    written("os-fork-zombie", "fork, exec, zombie and orphan", "Medium",
        "Explain `fork()` and `exec()`. What are zombie and orphan processes?",
        "`fork()` creates a **child** that is a copy of the parent (copy-on-write makes it cheap); it returns 0 in the child and the child's PID in the parent. `exec()` **replaces** the current process image with a new program. A shell runs a command by `fork()` then `exec()` in the child while the parent `wait()`s.\n\n"
        "A **zombie** is a process that has terminated but whose parent has not yet called `wait()` to read its exit status: it keeps only a process-table entry. An **orphan** is a process whose parent has terminated; the init/systemd process adopts it. A pile of zombies means the parent never reaps its children."),
    written("os-file-system", "Inodes and file systems", "Hard",
        "In a Unix-like file system, what is an inode and what is the difference between a hard link and a symbolic link?",
        "An **inode** stores a file's **metadata** (owner, permissions, size, timestamps, link count) and pointers to its **data blocks** (direct pointers, then single, double and triple indirect blocks for large files), but **not the file name**. A directory is a table mapping names to inode numbers.\n\n"
        "A **hard link** is another directory entry pointing to the **same inode**: the file data is deleted only when the link count reaches zero, and hard links cannot cross file systems or point to directories. A **symbolic (soft) link** is a small file containing a **path**; it can cross file systems and point to directories, but it **dangles** if the target is removed."),
    written("os-interrupts", "Interrupts and the kernel", "Medium",
        "What happens when an interrupt occurs while a process is running?",
        "The hardware finishes the current instruction, saves the program counter and flags, switches to kernel mode and jumps through the **interrupt vector table** to the **interrupt service routine (ISR)**. The ISR handles the device (read the data, acknowledge) as quickly as possible, often only queueing the work, and then returns from the interrupt. The scheduler may then choose a different process, so an interrupt such as a timer tick is also how **preemptive multitasking** happens. Interrupts come from devices; **exceptions/traps** come from the running instruction (page fault, divide by zero, system call)."),
    written("os-containers", "Containers versus virtual machines", "Medium",
        "How is a container different from a virtual machine?",
        "A **virtual machine** emulates hardware with a **hypervisor** and runs a **complete guest OS** with its own kernel: strong isolation, heavy (GBs, minutes to boot). A **container** is an ordinary process (or group) on the host kernel, isolated with **namespaces** (own view of processes, network, mounts) and limited with **cgroups** (CPU, memory, I/O): lightweight (MBs, starts in a second) and dense, but all containers share the host kernel, so a kernel vulnerability affects them all and a container cannot run a different OS kernel. Docker packages an application with its dependencies into an image that runs the same on any host with a compatible kernel."),
]

SUBJECT = subject("core-os", "Operating Systems", "Core subjects", 40,
    "Processes and threads, scheduling, synchronisation, deadlock, memory management and file systems. Scheduling and page-replacement answers are computed, not estimated.",
    QUESTIONS,
    platforms=[
        {"name": "GeeksforGeeks: Operating Systems", "url": "https://www.geeksforgeeks.org/operating-systems/operating-systems/", "note": "Tutorials and practice questions"},
        {"name": "OSTEP (free book)", "url": "https://pages.cs.wisc.edu/~remzi/OSTEP/", "note": "Operating Systems: Three Easy Pieces"},
    ])
