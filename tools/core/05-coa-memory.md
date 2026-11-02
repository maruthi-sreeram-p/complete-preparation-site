@part coa-memory | Computer Organisation · Part 5: The Memory Hierarchy | coa
## Why there is a hierarchy

A CPU can execute an instruction in well under a nanosecond, but reading main memory takes around 50 to 100 ns: **a hundred times slower**. If every access went to main memory the CPU would spend almost all of its time waiting. We cannot make a large memory that is both fast and cheap, so we build a **hierarchy**: small, fast, expensive memories close to the CPU, large, slow, cheap ones further away, arranged so that most accesses are served by the fast levels.

| Level | Typical size | Typical access time | Technology |
|---|---|---|---|
| Registers | a few hundred bytes | under 1 ns | flip-flops |
| L1 cache | 32 to 64 KB per core | 1 ns | SRAM |
| L2 cache | 256 KB to 2 MB | 3 to 5 ns | SRAM |
| L3 cache (shared) | 8 to 64 MB | 10 to 20 ns | SRAM |
| Main memory | 8 to 128 GB | 50 to 100 ns | DRAM |
| SSD | hundreds of GB to TB | 50 to 150 µs | flash |
| Hard disk | TB | 5 to 10 ms | magnetic |

Going down the table, **size and latency increase while cost per byte falls**.

### Why it works: locality

Programs do not access memory at random. They show **locality of reference**:

- **Temporal locality:** something used recently is likely to be used again soon (loop variables, the same function called repeatedly).
- **Spatial locality:** things near a recently used address are likely to be used soon (walking through an array, sequential instructions).

A cache keeps recently used data (temporal) and brings whole **blocks** of neighbouring bytes at a time (spatial). The Java loop `for (int i = 0; i < n; i++) sum += a[i];` has both: `sum` and `i` are reused, and `a[i+1]` is next to `a[i]`. Traversing a 2-D array **row by row** is much faster than column by column for exactly this reason: Java stores each row contiguously.

### SRAM, DRAM and ROM

| | SRAM | DRAM |
|---|---|---|
| Cell | 6 transistors (a flip-flop) | 1 transistor + 1 capacitor |
| Speed | fast | slower |
| Density and cost | low density, expensive | high density, cheap |
| Refresh needed | no | **yes**: the capacitor leaks, so every row is refreshed every few ms |
| Used for | caches | main memory |

**ROM** keeps its contents without power (firmware, boot code): PROM, EPROM (UV erasable), EEPROM and **flash** (block-erasable, used in SSDs and USB drives).

### Building memories from chips

A memory of 64K × 16 (65,536 words of 16 bits) from 16K × 4 chips needs (64K / 16K) × (16 / 4) = 4 × 4 = **16 chips**: 4 chips side by side give the 16-bit width, and 4 such rows give the capacity. The 2 high-order address bits drive a **2-to-4 decoder** that selects the row (chip select). **Interleaving** spreads consecutive addresses over several banks so that they can be accessed in parallel.

!cheat Memory quick facts ::
- Words × bits per word = capacity. Chips needed = (total capacity) / (chip capacity).
- Address bits = log₂(number of addressable words).
- Locality: temporal (reuse) and spatial (neighbours). Cache blocks exploit spatial locality.
- SRAM is faster and costlier (caches); DRAM needs refresh (main memory).
- Row-major traversal of an array is faster than column-major in Java and C.
!end

!keypoints The hierarchy gives the illusion of a large, fast memory using locality ;; Temporal locality: reuse; spatial locality: neighbours ;; SRAM (6 transistors, fast) for caches; DRAM (1T1C, refreshed) for main memory ;; Down the hierarchy: bigger, slower, cheaper ;; Chip count = capacity ratio; high address bits select the chip

?? Why does a hierarchy of memories work even though most of the memory is slow?
=> Programs show locality: they reuse recently accessed data and access nearby addresses. A small fast cache therefore satisfies most accesses, and only the occasional miss goes to the slower level, so the average access time is close to the speed of the fast level.

?? Why must DRAM be refreshed but SRAM need not be?
=> A DRAM cell stores its bit as charge on a capacitor, which leaks away within milliseconds, so each row must be read and rewritten periodically. An SRAM cell is a flip-flop that holds its state as long as power is applied.

## Cache memory

A **cache** is a small, fast memory between the CPU and main memory that holds copies of recently used blocks. When the CPU asks for an address:

- **Hit:** the block is in the cache; the data returns quickly.
- **Miss:** the block is fetched from the next level (taking the **miss penalty**), stored in the cache and then delivered.

**Hit rate** = hits / accesses; **miss rate** = 1 − hit rate. Memory is divided into **blocks** (lines) of, say, 64 bytes, and a whole block is transferred on a miss.

### Mapping: where can a block go?

The address is split into three fields:

**| Tag | Index | Block offset |**

- **Offset** (log₂ block size bits) selects the byte inside the block.
- **Index** selects the cache **set** (or line).
- **Tag** is the rest; it is stored with the block and compared on each access to see whether *this* memory block is the one in the line.

| Mapping | A block may go in | Index bits | Hardware |
|---|---|---|---|
| **Direct-mapped** | exactly one line: block number mod (number of lines) | log₂(lines) | simplest, fastest, but **conflict misses** |
| **Fully associative** | any line | 0 (no index) | compare all tags in parallel: costly, only for small caches or TLBs |
| **k-way set-associative** | any of the k lines in one set: block number mod (number of sets) | log₂(sets) | a compromise used by real CPUs (4-way, 8-way) |

**Worked example.** A 32-bit address, 32 KB cache, 64-byte blocks.
- Block offset: log₂ 64 = **6** bits. Number of blocks: 32 KB / 64 B = 512.
- **Direct-mapped:** 512 sets, index = **9** bits, tag = 32 − 9 − 6 = **17** bits.
- **4-way:** 512 / 4 = 128 sets, index = **7** bits, tag = 32 − 7 − 6 = **19** bits.
- **Fully associative:** no index, tag = 32 − 6 = **26** bits.

More associativity means a longer tag and more comparators, but fewer conflict misses.

**Conflict example.** Blocks 0, 4, 8, 16 are accessed repeatedly in a direct-mapped cache with 4 lines. All four map to line 0 (block mod 4 = 0), so every access evicts the previous one: a **miss every time**, although the cache has three empty lines. A fully associative cache of the same size misses only the first four times.

### Replacement and write policies

When a set is full, a **replacement policy** picks a victim: **LRU** (least recently used: best, costly to track), **FIFO**, or **random** (cheap, nearly as good for large caches).

When the CPU **writes**, two questions arise:

| Policy | What happens on a write hit | Notes |
|---|---|---|
| **Write-through** | update the cache **and** memory | simple, memory always current, but slow: a **write buffer** hides the cost |
| **Write-back** | update only the cache and set a **dirty bit**; write the block to memory when it is evicted | far less memory traffic; needs the dirty bit |

On a write **miss**, **write-allocate** loads the block into the cache first (usual with write-back); **no-write-allocate** writes straight to memory (usual with write-through).

### The three Cs of cache misses

| Miss type | Cause | Reduced by |
|---|---|---|
| **Compulsory** (cold) | first access to a block | larger blocks, prefetching |
| **Capacity** | the working set is bigger than the cache | a bigger cache |
| **Conflict** | too many blocks map to the same set | more associativity |

A fourth cause matters on multicore machines: **coherence misses**, when another core invalidated the block.

!cheat Cache field formulas ::
- Offset bits = log₂(block size). Number of blocks = cache size / block size.
- Number of sets = blocks / associativity. Index bits = log₂(sets).
- Tag bits = address bits − index bits − offset bits.
- Direct-mapped: sets = blocks. Fully associative: sets = 1, no index bits.
- Total tag storage = number of blocks × tag bits (plus valid and dirty bits).
!end

!interview Interview angle: Write-through or write-back? :: Write-through keeps memory consistent at all times and is simple, but every store goes to memory, so a write buffer is needed. Write-back writes memory only when a dirty block is evicted, saving a great deal of bandwidth for data written repeatedly, which is why L1 and L2 caches in CPUs are write-back. The cost is the dirty bit and the more complex coherence in multiprocessors.

!keypoints An address splits into tag, index and block offset ;; Direct-mapped: one possible line (conflicts); fully associative: any line (costly); set-associative: a compromise ;; Tag bits = address bits − index bits − offset bits ;; Write-back uses a dirty bit and saves memory traffic; write-through updates memory on every write ;; Misses are compulsory, capacity or conflict

?? How many tag, index and offset bits does a 16 KB 2-way set-associative cache with 32-byte blocks use for a 32-bit address?
=> Offset = log₂ 32 = 5 bits. Blocks = 16 KB / 32 B = 512; sets = 512 / 2 = 256, so index = 8 bits. Tag = 32 − 8 − 5 = 19 bits.

?? Why can a direct-mapped cache have a high miss rate even when it is mostly empty?
=> Several frequently used blocks may map to the same line and keep evicting each other (conflict misses) while other lines are unused. Associativity lets such blocks share a set.

## Cache performance

### Average memory access time (AMAT)

**AMAT = hit time + miss rate × miss penalty**

**Example.** Hit time 1 ns, miss rate 5%, miss penalty 100 ns: AMAT = 1 + 0.05 × 100 = **6 ns**. Halving the miss rate to 2.5% gives 3.5 ns, so reducing misses matters far more than shaving the hit time.

### Multilevel caches

With an L1 and an L2 cache, the L1 **miss penalty** is the L2 access time plus L2's own misses going to memory. Using **local** miss rates (misses divided by the accesses to *that* level):

**AMAT = H₁ + m₁ × (H₂ + m₂ × T_memory)**

With L1 hit time 1 ns, L1 local miss rate 10%, L2 hit time 10 ns, L2 local miss rate 20% and memory time 100 ns: AMAT = 1 + 0.1 × (10 + 0.2 × 100) = 1 + 0.1 × 30 = **4 ns**.

### Effect on CPI

Memory stalls add to the base CPI:

**CPI = base CPI + (memory accesses per instruction) × miss rate × miss penalty (in cycles)**

With base CPI 1.2, one instruction fetch plus 0.3 data accesses per instruction (1.3 accesses), a 2% miss rate and a 50-cycle penalty: CPI = 1.2 + 1.3 × 0.02 × 50 = **2.5**. The cache misses double the CPI, so a faster processor core helps little unless the memory system keeps up (the "memory wall").

### Improving performance

- **Larger blocks** reduce compulsory misses (spatial locality) but increase the miss penalty and can cause pollution.
- **Higher associativity** reduces conflict misses but lengthens the hit time.
- **Prefetching** loads blocks before they are asked for.
- **Cache-friendly code:** access memory sequentially, keep the working set small, **loop blocking (tiling)** for matrices. In Java prefer an `int[]` to a `List<Integer>`: the array is contiguous and has far fewer cache misses than boxed objects scattered on the heap.

!cheat Performance formulas ::
- AMAT = hit time + miss rate × miss penalty.
- Two levels: AMAT = H₁ + m₁(H₂ + m₂ · T_mem) with local miss rates.
- Effective CPI = base CPI + accesses per instruction × miss rate × miss penalty.
- Global miss rate of L2 = m₁ × m₂ (local rates multiplied).
!end

!keypoints AMAT = hit time + miss rate × miss penalty ;; With two levels the L1 miss penalty is itself an AMAT of the L2 ;; Memory stalls add accesses per instruction × miss rate × penalty to the CPI ;; Contiguous, sequential access patterns are cache-friendly ;; Reducing the miss rate usually beats reducing the hit time

?? A cache has a hit time of 2 ns, a miss rate of 4% and a miss penalty of 80 ns. What is the AMAT?
=> AMAT = 2 + 0.04 × 80 = 5.2 ns.

?? Why is looping over a 2-D array row by row faster than column by column in Java?
=> Each row is stored contiguously, so row-by-row access uses all the bytes of every cache block brought in (spatial locality). Column-by-column access jumps a whole row between accesses, touching a different block each time and wasting most of each block.

## Virtual memory

**Virtual memory** gives each process the illusion of a large, private address space. The CPU issues **virtual addresses**; hardware (the **MMU**) translates them to **physical addresses** using a **page table**. Memory is divided into fixed-size **pages** (typically 4 KB); physical memory into **frames** of the same size. The operating system keeps only the active pages in RAM and the rest on disk. (Operating Systems Part 3 covers the OS side in depth.)

A virtual address splits into **page number** and **offset**. For 32-bit virtual addresses and 4 KB pages the offset is 12 bits and the page number is 20 bits.

### The page table

Each process has a page table with one **page table entry (PTE)** per virtual page, holding the frame number plus **valid**, **dirty**, **reference** and **protection** bits.

**Size example.** 32-bit addresses, 4 KB pages, 4-byte PTEs: 2²⁰ entries × 4 B = **4 MB per process**. A 64-bit space would be far too large for one flat table, so real systems use **multi-level** (and inverted) page tables, allocating only the parts in use.

### The TLB

Every memory access would need two memory accesses (page table, then data). A **translation lookaside buffer (TLB)** is a small, fast cache of recent translations.

**Effective access time with a TLB:** a TLB hit costs the TLB time plus one memory access; a miss costs the TLB time plus a page-table access plus the data access.

With a 90% TLB hit ratio, TLB time 10 ns and memory time 100 ns:
EAT = 0.9 × (10 + 100) + 0.1 × (10 + 100 + 100) = 99 + 21 = **120 ns**.

### Page faults

A **page fault** occurs when the page is not in memory (valid bit 0). The OS loads it from disk (millions of cycles) and restarts the instruction. With a memory access time of 100 ns, a fault service time of 8 ms and a fault rate p: EAT = (1 − p) × 100 ns + p × 8,000,000 ns. To keep the slowdown below 10%, p must be below about **1.25 × 10⁻⁶**, one fault in 800,000 accesses. This is why **locality** and good page replacement matter so much, and why excessive paging (**thrashing**) is catastrophic.

**Page replacement.** FIFO, LRU and the unrealistic optimal (OPT). For the reference string 1,2,3,4,1,2,5,1,2,3,4,5, FIFO with 3 frames faults 9 times and with 4 frames faults **10** times: more memory, more faults. This is **Belady's anomaly**; it affects FIFO but never LRU or OPT (stack algorithms).

!cheat Virtual memory formulas ::
- Offset bits = log₂(page size); page number bits = address bits − offset bits.
- Flat page table size = 2^(page number bits) × PTE size.
- EAT (with TLB) = h(t_tlb + t_mem) + (1 − h)(t_tlb + 2·t_mem) for a one-level page table.
- EAT with faults = (1 − p) t_mem + p × t_fault.
- Belady's anomaly: FIFO can fault more with more frames; LRU and OPT cannot.
!end

!keypoints Virtual addresses are translated to physical addresses by the MMU using page tables ;; A flat table for 32-bit addresses and 4 KB pages has 2²⁰ entries ;; The TLB caches translations; its hit ratio sets the effective access time ;; Page faults cost millions of cycles, so the fault rate must be tiny ;; Belady's anomaly: FIFO may fault more with more frames

?? What is the size of a flat page table for a 32-bit address space with 4 KB pages and 4-byte entries?
=> There are 2³² / 2¹² = 2²⁰ pages, so 2²⁰ × 4 B = 4 MB per process.

?? Why is a TLB needed?
=> Without it every memory reference needs an extra memory access to read the page table entry, doubling the access time. The TLB caches recent translations so most references are translated in a single fast lookup.
