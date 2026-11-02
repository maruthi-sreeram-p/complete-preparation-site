@part coa-io | Computer Organisation · Part 6: Input/Output, Buses and Storage | coa
## Buses and I/O organisation

The CPU, memory and I/O devices are connected by **buses**: shared sets of wires with a protocol. A classic system bus has three groups of lines:

| Lines | Carries | Direction |
|---|---|---|
| **Address bus** | the address of the memory location or device | CPU → others |
| **Data bus** | the data being transferred | both ways |
| **Control bus** | read/write, clock, interrupt request, bus grant and other signals | both ways |

**Bus width** matters: a 32-bit address bus reaches 2³² = 4 GiB; a 64-bit data bus moves 8 bytes per transfer. **Bandwidth** = width × transfers per second: a 64-bit bus at 100 MHz transfers 8 B × 100 × 10⁶ = **800 MB/s**. Modern computers replace one shared bus with **point-to-point links** (PCIe lanes, memory channels, USB) because a long shared bus cannot run fast.

### Bus arbitration

When several devices (masters) want the bus at once, an **arbiter** decides who gets it:

- **Daisy chain:** the grant signal passes from device to device; the nearest one has priority. Simple, but far devices can starve.
- **Centralised parallel:** each device has its own request and grant lines going to a central arbiter. Flexible priorities, more wires.
- **Distributed:** devices negotiate among themselves.

### Talking to a device

A device is attached through a **controller** with a few **registers**: a *status* register (is it ready, is there an error?), a *command* register and a *data* register. There are two ways to address them:

| | Memory-mapped I/O | Isolated (port-mapped) I/O |
|---|---|---|
| Device registers appear as | **ordinary memory addresses** | a separate I/O address space |
| Instructions used | normal LOAD and STORE | special IN and OUT instructions |
| Address space | shares the memory address space | extra space, but fewer instructions to protect |
| Used by | ARM, RISC-V, most modern designs | x86 (in addition to memory-mapped) |

With memory-mapped I/O, writing a byte to address 0xFFFF0000 might print a character. This is also why the compiler must not "optimise away" reads of such addresses: in C they are declared `volatile`.

!cheat Bus and I/O facts ::
- Bus bandwidth = width (bytes) × transfers per second.
- Address bits = log₂(number of addressable locations); a wider data bus moves more per transfer.
- Daisy chaining: nearest device wins. Parallel arbitration: central arbiter, any priority order.
- Memory-mapped I/O: no special instructions, devices share the address space. Isolated I/O: separate space, IN/OUT.
- A controller has status, command and data registers.
!end

!keypoints A system bus has address, data and control lines ;; Bandwidth = width × transfers per second ;; The arbiter decides which master gets the bus: daisy chain, parallel or distributed ;; Memory-mapped I/O uses ordinary loads and stores; isolated I/O uses IN and OUT ;; Devices are driven through controller registers (status, command, data)

?? What is the bandwidth of a 32-bit data bus that does one transfer per clock at 200 MHz?
=> 4 bytes × 200 × 10⁶ = 800 MB/s.

?? What is the main difference between memory-mapped and isolated I/O?
=> In memory-mapped I/O the device registers share the memory address space and are accessed with normal load and store instructions. In isolated I/O the devices live in a separate address space accessed with dedicated IN and OUT instructions.

## Programmed I/O, interrupts and DMA

How does the CPU know a key was pressed or a disk block has arrived? There are three methods.

### 1. Programmed I/O (polling)

The CPU repeatedly reads the device's status register in a loop until it says "ready", then transfers the data. It is simple, but the CPU does nothing useful while it waits (**busy waiting**), which is unacceptable for slow devices.

### 2. Interrupt-driven I/O

The CPU starts the operation and continues with other work. When the device is ready it raises an **interrupt request (IRQ)**. The CPU finishes the current instruction, saves its state, and runs an **interrupt service routine (ISR)**.

**What happens on an interrupt:**

1. The device asserts the interrupt line.
2. The CPU completes the current instruction and checks for pending interrupts.
3. It **saves the PC and the flags** (on the stack), and disables further interrupts if needed.
4. It identifies the source and jumps to the ISR: through a **vector table** (the device supplies a vector number that indexes the table of ISR addresses) or by polling.
5. The ISR handles the device, then executes **return from interrupt**, which restores the flags and the PC.

| Term | Meaning |
|---|---|
| **Maskable interrupt** | can be ignored (disabled) by the CPU: devices |
| **Non-maskable interrupt (NMI)** | cannot be disabled: hardware failures |
| **Priority** | when two interrupts arrive, the higher priority is served first; a higher-priority interrupt may **nest** inside a running ISR |
| **Exception (trap)** | raised *by the CPU* in response to an instruction: divide by zero, page fault, system call |

A **system call** is deliberately a trap: your Java program asking the OS to read a file ends in an instruction that traps into the kernel.

### 3. Direct memory access (DMA)

Interrupting the CPU for every byte is wasteful when moving blocks of data. A **DMA controller** transfers data between the device and memory **by itself**, taking over the bus. The CPU only programs it (source, destination, count) and gets **one interrupt when the whole block is done**.

- **Burst mode:** the DMA controller holds the bus for the whole block; the CPU is blocked meanwhile.
- **Cycle stealing:** it takes the bus for one transfer at a time, between CPU accesses.

**Numeric comparison.** A device delivers 4 MB/s in 4-byte words: 10⁶ words per second. A CPU at 1 GHz takes 500 cycles to run the ISR for one word: 10⁶ × 500 = 5 × 10⁸ cycles per second: **50% of the CPU**. With DMA moving 4 KB blocks (1,000 blocks per second) and 1,000 cycles per block interrupt: 10⁶ cycles per second: **0.1% of the CPU**.

!cheat I/O methods compared ::
- **Polling:** simplest, wastes the CPU, fine for fast devices that are almost always ready.
- **Interrupts:** CPU free between events, but overhead per event (save state, ISR, restore).
- **DMA:** best for bulk data: one interrupt per block, the CPU is only slowed by bus sharing.
- Interrupt sequence: finish instruction → save PC and flags → find the ISR (vector) → run → return.
- Traps and exceptions come from the CPU itself (system calls, page faults, divide by zero).
!end

!interview Interview angle: Interrupts versus polling, when is polling better? :: With interrupts, every event costs a context save, the ISR and a restore. If a device produces events extremely often (a fast network card at high load), the interrupt overhead can swamp the CPU, so high-speed drivers use polling or a hybrid (interrupt once, then poll until empty, as Linux NAPI does). For slow or rare events interrupts are better because the CPU can do other work in between.

!keypoints Polling wastes the CPU in a busy-wait loop ;; An interrupt saves the PC and flags, finds the ISR through a vector table, and returns ;; Exceptions and traps are raised by the CPU itself; a system call is a trap ;; DMA moves blocks without the CPU and interrupts once at the end ;; Burst mode blocks the CPU; cycle stealing interleaves with it

?? Why is DMA better than interrupt-driven I/O for disk transfers?
=> Interrupt-driven I/O interrupts the CPU for every word (or small unit), spending many cycles on state saving and the ISR. A DMA controller moves the whole block itself and interrupts the CPU once at the end, leaving the CPU free for other work.

?? What does the CPU do when it receives an interrupt?
=> It finishes the current instruction, saves the PC and flags, identifies the interrupting device (for example through the vector table), runs the interrupt service routine, and finally restores the saved state with a return-from-interrupt instruction.

## Storage devices

### Hard disks

A hard disk has **platters** divided into **tracks** and **sectors** (typically 512 bytes or 4 KB). A head must **seek** to the right track, wait for the sector to **rotate** under it, and then **transfer** the data.

**Access time = seek time + rotational latency + transfer time**

- **Rotational latency** on average is **half a rotation**: at 7,200 rpm one rotation takes 60,000 / 7,200 = 8.33 ms, so the average latency is 4.17 ms.
- **Transfer time** = (bytes to transfer / bytes per track) × time per rotation.

**Example.** 7,200 rpm, average seek 4 ms, 512-byte sectors, 200 sectors per track, reading 4 KB: rotation 8.33 ms; half = 4.17 ms; the track holds 102,400 bytes so the transfer is 4,096 / 102,400 × 8.33 ≈ 0.33 ms. Access time ≈ 4 + 4.17 + 0.33 = **8.5 ms**. Seek and rotation dominate, which is why random access on a disk is so much slower than sequential, and why databases are designed around sequential I/O.

### Solid-state drives (SSD)

An SSD stores bits in **NAND flash**: no moving parts, so random access takes tens of microseconds. Quirks that matter to software:

- Data is **read and written in pages** (4 to 16 KB) but **erased in blocks** (many pages), and a page cannot be overwritten in place.
- Each cell survives a limited number of erase cycles, so the controller does **wear levelling** and **garbage collection**; the **TRIM** command tells it which blocks are free.
- Random reads are fast, small random writes are comparatively expensive (write amplification).

### RAID: combining disks

**RAID** (redundant array of independent disks) combines disks for speed, reliability or both. With N disks of capacity C:

| Level | Idea | Usable capacity | Survives |
|---|---|---|---|
| **RAID 0** | striping, no redundancy | N × C | no disk failure |
| **RAID 1** | mirroring | N × C / 2 | one disk per mirrored pair |
| **RAID 5** | striping with one block of **distributed parity** | (N − 1) × C | **one** disk |
| **RAID 6** | two parity blocks | (N − 2) × C | **two** disks |
| **RAID 10** | stripe of mirrors | N × C / 2 | one disk per mirror (more in the best case) |

**Example.** Eight 4 TB disks in RAID 5 give (8 − 1) × 4 = **28 TB** usable. RAID 5 recovers a lost block by XOR-ing the surviving blocks of the stripe, because parity = XOR of the data blocks. A small write costs four I/Os (read old data and parity, write new data and parity): the **small-write penalty**.

!cheat Storage formulas ::
- Disk access time = seek + ½ rotation + transfer. Rotation time = 60 / rpm seconds.
- Average rotational latency = ½ × (60,000 / rpm) ms (7,200 rpm: 4.17 ms; 15,000 rpm: 2 ms).
- Transfer time = (bytes / bytes per track) × rotation time.
- RAID 0: N·C, RAID 1/10: N·C/2, RAID 5: (N−1)·C, RAID 6: (N−2)·C.
- RAID 5 parity: P = D1 ⊕ D2 ⊕ ... ⊕ Dn; a lost block = XOR of the rest.
- SSD: erase by block, write by page, wear levelling, TRIM.
!end

!keypoints Disk access time = seek + half a rotation + transfer; seek and rotation dominate ;; Sequential access is far faster than random on a hard disk ;; SSDs erase by block and write by page, with wear levelling ;; RAID 5 survives one disk failure with (N−1)·C capacity; RAID 6 survives two ;; Parity is the XOR of the data blocks, so a lost block is the XOR of the others

?? What is the average rotational latency of a 15,000 rpm disk?
=> One rotation takes 60,000 / 15,000 = 4 ms, so the average wait is half a rotation: 2 ms.

?? Why does RAID 5 survive one disk failure?
=> Each stripe stores a parity block equal to the XOR of its data blocks. If one disk fails, the missing block of every stripe equals the XOR of all the remaining blocks (data and parity), so it can be reconstructed.

## Putting it all together

This chapter follows two everyday events through everything in Parts 1 to 6. Being able to narrate them is a strong interview answer.

### What happens when your program executes `int v = a[i];`

1. The compiler or JIT turns it into instructions: compute `address = base(a) + i × 4`, then a **load** (displacement addressing).
2. The **fetch** stage reads the load instruction through the **L1 instruction cache**; the pipeline's **decode** stage reads the base register; the **ALU** adds the offset.
3. The address is a **virtual address**. The **TLB** translates it to a physical address (a TLB miss means a page-table walk; a page fault means the OS reads the page from disk, millions of cycles).
4. The **L1 data cache** is searched: the index selects the set, the tags are compared. A **hit** returns in about 1 ns; a miss goes to L2, then L3, then DRAM (50 to 100 ns), bringing a whole **64-byte block** so that `a[i+1]` is already there next time (spatial locality).
5. The value is written back to a register in the write-back stage. If an instruction after it needs the register, **forwarding** or a **load-use stall** applies.

### What happens when you press a key

1. The keyboard controller raises an **interrupt**. The CPU finishes its current instruction, saves the PC and flags, and jumps through the **vector table** to the keyboard ISR.
2. The ISR reads the **device's data register** (memory-mapped I/O), places the key code in a buffer and returns from the interrupt.
3. The OS wakes the process waiting on the input; the scheduler runs it, and the program receives the character through a **system call** (a trap into the kernel).

### Why performance advice follows from the hardware

| Advice | Hardware reason |
|---|---|
| Use arrays and iterate sequentially | cache blocks, spatial locality, prefetching |
| Avoid pointer chasing (linked lists, boxed objects) | every hop is a possible cache miss |
| Keep hot data small | fits in L1/L2: capacity misses |
| Avoid unpredictable branches in hot loops | branch misprediction flushes the pipeline |
| Batch I/O and prefer sequential reads | seek and rotation dominate a disk; DMA works on blocks |
| Do not share a hot variable between threads | cache coherence traffic (false sharing) |

!keypoints A load involves translation (TLB), the cache hierarchy, the pipeline and possibly the disk ;; A key press travels through an interrupt, a vector table, an ISR and a system call ;; Locality, predictable branches and sequential I/O are what hardware rewards ;; Cache coherence makes sharing hot variables between cores expensive

?? Describe what happens, in hardware terms, when a program reads an array element that is not in the cache.
=> The address is translated by the TLB (or a page walk), the L1 cache is searched and misses, the request goes to L2, L3 and finally DRAM. A whole cache block containing the element is brought back and stored in the cache, then the requested word is delivered to a register. Neighbouring elements are now cache hits.

?? Why are linked lists often slower than arrays for traversal even though both are O(n)?
=> An array's elements are contiguous, so each cache block loaded serves several elements and the hardware can prefetch. A linked list's nodes are scattered in memory and each next-pointer dereference is likely to be a cache miss.
