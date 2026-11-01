@part gate-coa | Computer Organization and Architecture | hardware
## Instruction set and addressing modes

### Instruction formats

An instruction has an **opcode** and zero or more **operand** fields. The number of explicit addresses classifies the machine:

| Type | Example for X = (A + B) × (C + D) | Instructions |
|---|---|---|
| 3-address | ADD T1, A, B / ADD T2, C, D / MUL X, T1, T2 | 3 |
| 2-address | MOV T, A / ADD T, B / MOV U, C / ADD U, D / MUL T, U / MOV X, T | 6 |
| 1-address (accumulator) | LOAD A / ADD B / STORE T / LOAD C / ADD D / MUL T / STORE X | 7 |
| 0-address (stack) | PUSH A, PUSH B, ADD, PUSH C, PUSH D, ADD, MUL, POP X | 8 |

**Instruction length** = opcode bits + operand bits. With 64 opcodes (6 bits) and three register operands among 32 registers (5 bits each), the minimum is 6 + 15 = 21 bits.

### Expanding opcodes

A fixed-length instruction can reuse operand bits as opcode bits for instructions with fewer operands. Suppose a 16-bit instruction with 4-bit fields: a 4-bit opcode gives 16 codes. If 14 are used for 3-address instructions, 2 codes remain and each one expands by the next 4 bits into 16 two-address opcodes, giving 2 × 16 = 32 slots. If 30 are used, 2 remain, and each expands by another 4 bits to 16 one-address opcodes: **2 × 16 = 32** one-address instructions. The rule: *unused codes at a level × 2^(bits added at the next level)*.

### Addressing modes

| Mode | Effective address (EA) | Memory accesses for the operand |
|---|---|---|
| Immediate | none (the operand is in the instruction) | 0 |
| Register | operand is in a register | 0 |
| Direct (absolute) | EA = address field | 1 |
| Register indirect | EA = contents of register | 1 |
| Memory indirect | EA = M[address field] | 2 |
| Indexed / displacement | EA = register + offset | 1 |
| Base register | EA = base register + offset (supports relocation) | 1 |
| PC-relative | EA = PC + offset (the PC already points to the **next** instruction) | 1 |
| Auto-increment / decrement | EA = register, then register ± size | 1 |
| Stack | EA = SP | 1 |

- A relative branch at address 1000 in a 4-byte-instruction machine with offset +20 goes to (1000 + 4) + 20 = **1024**.
- A memory-indirect instruction with a one-word encoding needs 1 (fetch) + 2 = **3** memory accesses.
- Word-addressable memory: address bits = log₂(words). Byte-addressable: log₂(bytes). 28 address bits give 2²⁸ = 256 MB.
- **Endianness:** little-endian stores the least significant byte at the lowest address. 0x12345678 at address 100 puts 0x78 at 100, 0x56 at 101, 0x34 at 102 and 0x12 at 103.

### RISC and CISC

| | RISC | CISC |
|---|---|---|
| Instruction length | fixed | variable |
| Operands in ALU instructions | registers only (**load/store architecture**) | memory operands allowed |
| Addressing modes | few | many |
| Control unit | usually hardwired | usually microprogrammed |
| Registers | many | few |
| Pipelining | easy | harder |

!cheat Instruction-set cheat codes ::
- **Instruction size** = opcode bits + Σ operand bits. For register operands each takes ⌈log₂(registers)⌉ bits.
- **Expanding opcode:** (remaining codes at a level) × 2^(bits gained at next level) = number of instructions at the next level.
- **EA questions:** substitute carefully and watch for "PC already incremented".
- **Memory accesses:** immediate 0, register 0, direct 1, indirect 2, plus 1 for the instruction fetch.
- **Counting instructions for an expression:** a 1-address (accumulator) machine needs a LOAD/STORE for every temporary, so (A+B)×(C+D) needs 7.
!end

## Arithmetic and the ALU

### Datapath and flags

The ALU combines an adder with logic gates. After an operation it sets **status flags**: Z (zero), N (negative), C (carry out), V (signed overflow). Adding 0xFF + 0x01 on 8 bits gives 0x00 with Z = 1 and C = 1, but V = 0 (−1 + 1 = 0 is no overflow). **V = (carry into the sign bit) ⊕ (carry out of the sign bit).** 0x7F + 0x01 = 0x80 sets V = 1.

A ripple-carry adder's delay grows as O(n). A carry-lookahead adder with tree structure grows as **O(log n)**.

### Multiplication

**Shift-and-add:** for each multiplier bit, add the multiplicand (shifted) to the partial product if the bit is 1. The product of two n-bit numbers needs 2n bits.

**Booth's algorithm** handles signed multipliers. Scan the multiplier from the right, looking at the pair (bᵢ, bᵢ₋₁), with b₋₁ = 0:

| bᵢ bᵢ₋₁ | Action |
|---|---|
| 0 0 or 1 1 | shift only |
| 0 1 | **add** the multiplicand |
| 1 0 | **subtract** the multiplicand |

For multiplier 1101 (−3): pairs are (1,0) subtract, (0,1) add, (1,0) subtract, (1,1) nothing, i.e. 3 add/subtract operations. A long run of 1s costs only two operations, so Booth is fast for such numbers. The **worst case is an alternating pattern** (0101…), which needs an operation at every bit.

### Division

**Restoring division** of n-bit numbers takes n iterations of shift and subtract, restoring the remainder when the subtraction goes negative. **Non-restoring division** avoids the restore step by adding in the next iteration instead.

!cheat ALU cheat codes ::
- **Overflow vs carry:** carry matters for unsigned arithmetic, V matters for signed. They are independent.
- **Booth operations** = number of boundaries between runs of 0s and 1s in the multiplier (with an appended 0 on the right).
- **n-bit × n-bit** gives a 2n-bit product, e.g. 16×16 needs 32 bits.
- **Division by n-bit divisor:** n iterations.
- **Lookahead:** gates compute all carries from G and P in parallel, so delay is logarithmic in the width, not linear.
!end

## Control unit

The control unit generates the control signals that sequence the fetch–decode–execute cycle.

| | Hardwired | Microprogrammed |
|---|---|---|
| Implementation | combinational logic and state counters | a control store (ROM) of microinstructions |
| Speed | **faster** | slower (extra memory access per micro-step) |
| Flexibility | hard to change | easy to change or extend |
| Used in | RISC | CISC |

### Microinstructions

- A **horizontal** microinstruction has one bit per control signal. It is wide and allows much parallelism, with little decoding.
- A **vertical** microinstruction encodes groups of mutually exclusive signals in fields, so it is narrower, and needs decoders, but allows less parallelism.
- The **control address register** (CAR) holds the address of the next microinstruction. Sequencing uses an incrementer, a branch field and a condition select.
- **Control store size** = (number of microinstructions) × (microinstruction width). A 1K-word store with 40 horizontal signals and a 10-bit next-address field uses 1024 × 50 = 51 200 bits.
- **Encoded width:** a field choosing among n signals (plus "none") needs ⌈log₂(n + 1)⌉ bits. Fields of 16, 8 and 4 signals need 5 + 4 + 3 = 12 bits.

!cheat Control-unit cheat codes ::
- **Hardwired = fast, rigid, RISC. Microprogrammed = flexible, slower, CISC.**
- **Horizontal = wide + parallel. Vertical = narrow + encoded.**
- **Bits = ⌈log₂(n + 1)⌉ per field** when a "no signal" choice is required, ⌈log₂ n⌉ when it is not. Read the question.
- **Control memory** = words × width. Don't forget the next-address field.
!end

## Memory hierarchy and cache

### Why it works

Programs show **temporal locality** (reuse recently used items) and **spatial locality** (use nearby items). Traversing a C array row by row exhibits spatial locality. The hierarchy: registers → cache (SRAM) → main memory (DRAM) → disk, each larger, slower and cheaper per bit. **DRAM needs periodic refresh**; SRAM does not.

### Performance formulas

- **Hit ratio** h = hits / accesses.
- **Average memory access time (AMAT)** = hit time + miss rate × miss penalty.
- If the miss path goes cache then memory (hierarchical): T = h·t_c + (1 − h)(t_c + t_m). If memory is accessed in parallel (simultaneous): T = h·t_c + (1 − h)·t_m.
- **Two levels:** AMAT = t_L1 + m_L1 (t_L2 + m_L2 · t_mem), where m_L2 is the local miss rate of L2.
- **CPU time = IC × CPI × clock period.** With memory stalls, CPI = base CPI + (memory accesses per instruction) × miss rate × miss penalty.
- **Miss penalty with a narrow bus:** latency + (words per block) × (time per transfer).

### Organisation and address breakdown

Memory address = **tag | index | offset**.

| Organisation | Where a block can go | Index bits |
|---|---|---|
| Direct-mapped | exactly one line: block mod (number of lines) | log₂(lines) |
| k-way set-associative | any of k lines in set (block mod sets) | log₂(sets) |
| Fully associative | any line | 0 |

Steps: offset bits = log₂(block size); number of blocks = cache size / block size; number of sets = blocks / k; index bits = log₂(sets); **tag bits = address bits − index − offset**.

Example: 32 KB, 4-way, 64-byte blocks, 32-bit addresses. Blocks = 512, sets = 128 (7 index bits), offset = 6 bits, tag = 32 − 7 − 6 = **19**.

**Total storage** per line = data bits + tag bits + valid bit (+ dirty bit for write-back). A direct-mapped 16 KB cache with 16-byte blocks and 32-bit addresses has 1024 lines, 4 offset bits, 10 index bits and an 18-bit tag, so each line holds 128 + 18 + 1 = 147 bits and the total is 1024 × 147 = 150 528 bits.

### Policies and misses

| Topic | Details |
|---|---|
| Replacement | LRU, FIFO, random (only needed when there is a choice, i.e. not direct-mapped) |
| Write-through | write to cache and memory at once; a write buffer hides the delay |
| Write-back | write to memory only when a dirty line is evicted; needs a **dirty bit** |
| Write-allocate / no-allocate | whether a write miss loads the block |
| Compulsory miss | first reference to a block |
| Capacity miss | working set is bigger than the cache |
| Conflict miss | too many blocks map to the same set (only in direct-mapped and set-associative caches) |

A larger block reduces compulsory misses through spatial locality, but at fixed capacity it can raise conflict misses and the miss penalty.

!cheat Cache cheat codes ::
- **Write the formula chain:** offset → blocks → sets → index → tag. Doing it in this order avoids mistakes.
- **Block number mod lines** gives the line in a direct-mapped cache. Block 1234 in a 64-line cache goes to line 1234 mod 64 = 18.
- **Associativity moves bits from index to tag.** Fully associative has no index.
- **Cache size** = sets × ways × block size. 32 sets × 2 ways × 16 B = 1024 B.
- **Trace small examples:** list the accesses and mark each hit or miss. Blocks 0, 4, 8 in a 4-line direct-mapped cache all land in line 0 and keep evicting one another.
- **Effective access time with a target:** t = h·t_c + (1 − h)(t_c + t_m). Solve for h: 20 = 10h + 110(1 − h) gives h = 0.9.
- **CPI with misses:** only count the fraction of instructions that access memory (loads and stores) for data misses.
!end

## Memory interfacing

- **Chip arithmetic:** chips needed = (total words / chip words) × (total width / chip width). A 64K × 16 memory from 16K × 8 chips needs (64K/16K) × (16/8) = 8 chips.
- The high-order address bits select a chip row through a decoder. For four rows of chips, 2 address lines drive the decoder.
- **Interleaving:** with low-order interleaving, consecutive addresses go to different modules, so sequential accesses overlap and bandwidth rises.
- Secondary storage (magnetic disks) is no longer named in the 2027 syllabus, so spend your time elsewhere.

## I/O interface: programmed I/O, interrupts and DMA

| Technique | How data moves | CPU involvement |
|---|---|---|
| Programmed I/O | CPU polls the device status and moves each word | CPU is busy waiting |
| Interrupt-driven | device raises an interrupt when ready; CPU runs an ISR per transfer | CPU free between interrupts |
| **DMA** | the DMA controller moves blocks directly between device and memory | CPU involved only at start and end |

- **Memory-mapped I/O** shares the address space with memory so ordinary loads and stores reach device registers. **Isolated I/O** has separate I/O instructions and its own address space.
- **Interrupts:** a vectored interrupt supplies the address (or number) of its service routine; in a non-vectored one the CPU polls to find the source. A **daisy chain** gives the highest priority to the device electrically closest to the CPU.
- **DMA modes:** *burst* keeps the bus until the whole block is moved, *cycle stealing* takes one memory cycle at a time, *transparent* uses cycles the CPU does not need.
- **Interrupt overhead:** 1000 interrupts per second at 20 µs each costs 1000 × 20 µs = 20 ms per second = 2% of the CPU.
- **DMA cost:** a device moving 2 MB/s with 4-byte words does 500 000 transfers per second, and at 100 ns per stolen cycle that uses 500 000 × 100 ns = 0.05 s, or **5%**, of memory time.

!cheat I/O cheat codes ::
- **Interrupt vs DMA:** interrupts free the CPU between words, DMA frees it between blocks.
- **Cycle stealing percentage** = (transfers per second) × (cycle time).
- **Highest priority in daisy chain:** the device nearest the CPU.
- **Burst = whole block, cycle stealing = one word at a time.**
!end

## Instruction pipelining and hazards

A classic five-stage pipeline has IF (fetch), ID (decode and register read), EX (execute), MEM (memory access) and WB (write back).

### Performance

For k stages, n instructions and cycle time T (and no stalls):

- **Total time = (k + n − 1) × T.** For k = 5 and n = 100 that is 104 cycles.
- **Speedup over a non-pipelined machine** = (n × k × T_np) / ((k + n − 1) × T), approaching T_np / T for large n. With equal stages and no overhead it tends to k.
- **Cycle time** = the slowest stage delay + latch overhead. Stage delays 100, 150, 200 and 120 ps give a 200 ps cycle, so 100 instructions take (4 + 99) × 200 = 20 600 ps.
- **Ideal CPI = 1.** With stalls, CPI = 1 + average stall cycles per instruction.
- **Average CPI from an instruction mix** = Σ (fraction × cycles). 40% at 1, 30% at 2, 20% at 3, 10% at 4 gives 0.4 + 0.6 + 0.6 + 0.4 = 2.0.
- **Amdahl's law:** speedup = 1 / ((1 − f) + f/s). If 60% of the work is sped up 4×, the speedup is 1 / (0.4 + 0.15) ≈ 1.82.

### Hazards

| Hazard | Cause | Remedy |
|---|---|---|
| **Structural** | two instructions need the same resource in a cycle (for example one memory port) | duplicate resources, separate instruction and data caches, or stall |
| **Data: RAW** (read after write) | an instruction reads a register an earlier one has not yet written | forwarding, or stall |
| Data: WAR / WAW | later instruction writes before an earlier one reads or writes | only in out-of-order machines, handled by renaming |
| **Control** | a branch changes the PC after later instructions were fetched | branch prediction, delayed branches, earlier resolution |

- **Forwarding** passes the ALU result straight to the next EX stage. With full forwarding, ALU-to-ALU dependences cost 0 stalls. A **load followed by a dependent use** costs **1 stall** because the data is not available until MEM.
- Without forwarding, a dependent instruction right after its producer needs 2 stall cycles (if the register file writes in the first half and reads in the second half of a cycle).
- **Branch penalty example:** 20% branches, 60% of them taken, 3-cycle penalty when taken gives CPI = 1 + 0.2 × 0.6 × 3 = 1.36.
- **CPU time** = IC × CPI / clock rate. 10⁹ instructions at CPI 1.5 on a 2 GHz clock take 0.75 s.

!cheat Pipeline cheat codes ::
- **Pipeline time:** (k + n − 1) cycles. The first instruction takes k cycles and each later one adds 1.
- **Clock period is set by the slowest stage plus latch overhead.** Balance the stages.
- **Stall counting:** write the instructions in a table, one row each, and shift a dependent instruction right until its operand is available.
- **Load-use = 1 stall even with forwarding.**
- **Naming the hazard:** read after write = RAW (true dependence), write after read = WAR, write after write = WAW.
- **CPI with branches:** 1 + (branch fraction) × (taken or mispredicted fraction) × (penalty).
!end

## Cheat sheet: COA on one page

| Topic | Formula or fact |
|---|---|
| Instruction size | opcode bits + operand bits |
| Expanding opcodes | remaining codes × 2^(bits gained) |
| Relative branch | target = (address of next instruction) + offset |
| Signed overflow | carry into sign ⊕ carry out of sign |
| Booth | 01 add, 10 subtract; worst case 0101… |
| Hardwired / microprogrammed | fast, RISC / flexible, CISC |
| Control store | words × width |
| Cache | offset = log₂ block; index = log₂ sets; tag = rest |
| AMAT | hit time + miss rate × miss penalty |
| Hierarchical access time | h·t_c + (1 − h)(t_c + t_m) |
| CPU time | IC × CPI × clock period |
| DMA modes | burst, cycle stealing, transparent |
| Pipeline time | (k + n − 1) × T |
| Load-use hazard | 1 stall with forwarding |
| Amdahl | 1 / ((1 − f) + f/s) |

??  What happens to the tag size when a cache of fixed size becomes more associative?
=> The number of sets falls, so the index shrinks and the tag grows by the same number of bits. A fully associative cache has no index bits.
??  Why does a load followed immediately by a dependent instruction stall even with forwarding?
=> The loaded value is not available until the end of the MEM stage, which is after the dependent instruction already needs it at the start of its EX stage, so one bubble is unavoidable.
??  Compare the CPU involvement in programmed I/O, interrupt-driven I/O and DMA.
=> In programmed I/O the CPU polls and moves every word. In interrupt-driven I/O the CPU is free between words but runs an ISR for each. With DMA the CPU sets up the transfer and handles one interrupt at the end of the block.
??  A 64K × 16 memory is built from 16K × 8 chips. How many chips and how many chip-select address bits?
=> (64K / 16K) × (16 / 8) = 8 chips arranged as 4 rows of 2 chips side by side. Two high-order address bits select the row through a 2-to-4 decoder.
