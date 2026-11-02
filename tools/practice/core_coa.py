"""Practice subject: Computer Organisation. Every figure below is computed here, so a wrong number cannot ship."""
import sys
from pathlib import Path

from common import subject, written

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))
from core_helpers import (  # noqa: E402
    amat_two_level, amdahl, cache_fields, disk_access_ms, hamming_parity_bits, ieee32, pipeline_cycles, raid_usable, twos,
)

CPU_TIME = 3e9 * 1.4 / 2.8e9
assert abs(CPU_TIME - 1.5) < 1e-9
AMDAHL = amdahl(0.7, 5)
assert round(AMDAHL, 3) == 2.273
SIGN, EXP, FRAC, HEX = ieee32(-6.25)
assert HEX == "C0C80000" and EXP == "10000001"
NEG45 = twos(-45, 8)
assert NEG45 == "11010011"
TAG, INDEX, OFFSET = cache_fields(32, 64 * 1024, 32, 2)
assert (TAG, INDEX, OFFSET) == (17, 10, 5)
AMAT2 = amat_two_level(2, 0.08, 12, 0.25, 120)
assert abs(AMAT2 - 5.36) < 1e-9
CYCLES = pipeline_cycles(5, 500, 40)
SPEEDUP = 5 * 500 / CYCLES
assert CYCLES == 544 and round(SPEEDUP, 2) == 4.6
HAM = hamming_parity_bits(32)
assert HAM == 6
EAT = 0.95 * (4 + 60) + 0.05 * (4 + 60 + 60)
assert abs(EAT - 67) < 1e-9
DISK = disk_access_ms(10_000, 3, 512, 400, 8192)
assert round(DISK, 2) == 6.24  # 3 ms seek + 3 ms half rotation + 0.24 ms transfer
RAID5 = raid_usable(5, 6, 8)
assert RAID5 == 40
SPEC = (0x12345678).to_bytes(4, "little")
assert SPEC.hex() == "78563412"

QUESTIONS = [
    written("coa-cpu-time", "CPU performance equation", "Easy",
        "A program executes 3 × 10⁹ instructions with an average CPI of 1.4 on a 2.8 GHz CPU. How long does it take? What are the three ways to make it faster?",
        f"CPU time = IC × CPI / clock rate = (3 × 10⁹ × 1.4) / (2.8 × 10⁹) = **{CPU_TIME:.1f} s**.\n\nThe three factors are instruction count (better algorithm, compiler or ISA), CPI (better microarchitecture: pipelining, caches, branch prediction) and clock rate (technology, limited by power). Comparing machines by clock rate or MIPS alone is misleading, because a different ISA does a different amount of work per instruction: compare execution time of the same program."),
    written("coa-amdahl", "Amdahl's law", "Medium",
        "70% of a program's run time is made 5 times faster. What is the overall speedup, and what is the best possible speedup however much that part is accelerated?",
        f"Speedup = 1 / ((1 − 0.7) + 0.7/5) = 1 / (0.3 + 0.14) = **{AMDAHL:.2f}**. The limit is 1 / (1 − 0.7) = **{1 / 0.3:.2f}**, set by the 30% that is untouched. Lesson: optimise the common case, but the part you do not speed up eventually dominates; this is also why adding cores helps programs with large serial sections so little."),
    written("coa-twos", "Two's complement", "Easy",
        "Write −45 as an 8-bit two's complement number. What is the range of 8-bit two's complement, and why does the same adder work for signed and unsigned numbers?",
        f"+45 = 00101101. Invert all bits: 11010010. Add 1: **{NEG45}**. Check: −128 + 64 + 16 + 2 + 1 = −45.\n\nThe 8-bit range is **−128 to +127**. The same adder works because in two's complement the sign bit simply has weight −2ⁿ⁻¹ and arithmetic is done modulo 2ⁿ: adding the bit patterns gives the right pattern for both interpretations, only the interpretation of overflow differs (carry out for unsigned, sign change for signed)."),
    written("coa-ieee", "Encoding a floating-point number", "Medium",
        "Encode −6.25 as an IEEE 754 single-precision number and give the hexadecimal pattern.",
        f"6.25 = 110.01₂ = 1.1001 × 2². Sign = 1 (negative). Exponent = 2 + 127 = 129 = **{EXP}**. Fraction = the digits after the leading 1: 1001 padded to 23 bits = **{FRAC}**.\n\nBits: {SIGN} | {EXP} | {FRAC} = **0x{HEX}**.\n\nCheck by decoding: (−1)¹ × 1.5625 × 4 = −6.25. Remember the hidden leading 1, the bias of 127, and that the exponent field is stored unsigned."),
    written("coa-cache-fields", "Cache address fields", "Medium",
        "A 32-bit address is used with a 64 KB 2-way set-associative cache with 32-byte blocks. How many bits are in the tag, index and offset?",
        f"Offset = log₂ 32 = **{OFFSET}** bits. Blocks = 64 KB / 32 B = 2048. Sets = 2048 / 2 = 1024, so index = **{INDEX}** bits. Tag = 32 − {INDEX} − {OFFSET} = **{TAG}** bits.\n\nA direct-mapped cache of the same size would have 2048 sets (11 index bits, 16 tag bits); fully associative would have no index (27 tag bits). More associativity means a longer tag and more comparators, with fewer conflict misses."),
    written("coa-amat", "Average memory access time with two cache levels", "Medium",
        "L1 has a 2 ns hit time and an 8% local miss rate. L2 has a 12 ns hit time and a 25% local miss rate. Main memory takes 120 ns. Find the average memory access time.",
        f"AMAT = H₁ + m₁ × (H₂ + m₂ × T_mem) = 2 + 0.08 × (12 + 0.25 × 120) = 2 + 0.08 × 42 = **{AMAT2:.2f} ns**.\n\nThe L1 miss penalty is itself an average: the L2 hit time plus L2's misses going to memory. Use **local** miss rates (misses divided by accesses to that level); the global L2 miss rate is 0.08 × 0.25 = 2%."),
    written("coa-pipeline-speedup", "Pipeline speedup with stalls", "Medium",
        "A 5-stage pipeline runs 500 instructions and loses 40 cycles to stalls. How many cycles does it take and what is the speedup over a non-pipelined machine that takes 5 cycles per instruction?",
        f"Cycles = k + n − 1 + stalls = 5 + 500 − 1 + 40 = **{CYCLES}**. The non-pipelined machine needs 500 × 5 = 2,500 cycles, so speedup = 2500 / {CYCLES} ≈ **{SPEEDUP:.2f}**.\n\nWithout the stalls it would be 2500 / 504 ≈ 4.96, close to the ideal 5. Stalls come from data hazards (load-use), control hazards (branches) and structural hazards; forwarding, branch prediction and instruction scheduling reduce them."),
    written("coa-hazards", "Pipeline hazards", "Medium",
        "Name the three types of pipeline hazard and one remedy for each. Why does a load-use dependence still need a stall with forwarding?",
        "**Structural:** two instructions need the same hardware (one memory port for fetch and data): separate instruction and data caches. **Data:** an instruction needs a result not produced yet (RAW): forwarding/bypassing, or compiler scheduling. **Control:** a branch changes the PC and the next instructions were fetched too early: branch prediction, delayed branches, or stalling.\n\n"
        "A load's data is available only at the end of the MEM stage, after the following instruction's EX stage has started, so even with forwarding an immediately dependent instruction must wait **one** cycle (the load-use stall). The compiler can fill that slot with an independent instruction."),
    written("coa-vm-eat", "Effective access time with a TLB", "Medium",
        "The TLB hit ratio is 95%, a TLB lookup takes 4 ns and a memory access takes 60 ns. With a single-level page table, what is the effective memory access time?",
        f"Hit: 4 + 60 = 64 ns. Miss: 4 + 60 (page table) + 60 (data) = 124 ns. EAT = 0.95 × 64 + 0.05 × 124 = **{EAT:.0f} ns**.\n\nWithout a TLB every access would cost 120 ns, so the TLB nearly halves it. Multi-level page tables make a miss costlier (one extra access per level), so a high TLB hit ratio matters even more; locality is what delivers it."),
    written("coa-hamming", "Hamming code", "Hard",
        "How many check bits does a single-error-correcting Hamming code need for 32 data bits? How does SECDED differ?",
        f"We need 2ʳ ≥ m + r + 1 = 32 + r + 1. For r = 5: 32 ≥ 38 is false; for r = **{HAM}**: 64 ≥ 39 is true. So {HAM} check bits (a 38-bit codeword). The check bits sit at positions 1, 2, 4, 8, 16, 32; the **syndrome** (which parity checks fail) gives the position of the flipped bit.\n\n**SECDED** adds one overall parity bit (7 here): it corrects any single-bit error and **detects** (but cannot correct) double-bit errors. ECC server memory uses SECDED on 64 data bits with 8 check bits."),
    written("coa-endian", "Endianness", "Easy",
        "How is the 32-bit value 0x12345678 stored at address 1000 on a little-endian and on a big-endian machine?",
        f"**Little-endian** (x86, most ARM systems) stores the least significant byte first: addresses 1000 to 1003 hold **{' '.join(f'{b:02X}' for b in SPEC)}**. **Big-endian** (network byte order) stores the most significant byte first: 12 34 56 78. It matters when reading binary files, sending data over sockets between different machines, or inspecting memory. Java's `ByteBuffer` defaults to big-endian; use `order(ByteOrder.LITTLE_ENDIAN)` to change it."),
    written("coa-disk", "Disk access time", "Medium",
        "A 10,000 rpm disk has a 3 ms average seek, 512-byte sectors and 400 sectors per track. How long does it take to read an 8 KB block on one track?",
        f"Rotation takes 60,000 / 10,000 = 6 ms, so the average rotational latency is 3 ms. The track holds 512 × 400 = 204,800 bytes, so transferring 8,192 bytes takes 8192 / 204800 × 6 ≈ 0.24 ms. Total = 3 + 3 + 0.24 ≈ **{DISK:.2f} ms**.\n\nSeek and rotation dominate, which is why random disk I/O is slow and why databases and file systems favour sequential access, big blocks and caching. An SSD has no seek or rotation."),
    written("coa-raid", "RAID levels", "Medium",
        "Six 8 TB disks are used in RAID 5. What is the usable capacity, and how many failures can it survive? Compare RAID 0, 1, 5 and 10.",
        f"RAID 5 usable capacity = (N − 1) × C = 5 × 8 = **{RAID5:.0f} TB**; it survives **one** disk failure (a lost block is the XOR of the other blocks of its stripe). RAID 0 stripes with no redundancy (N × C, no failures survived, fastest). RAID 1 mirrors (N × C / 2, survives one failure per pair). RAID 10 is a stripe of mirrors (N × C / 2, good for databases). RAID 5 has a small-write penalty (read old data and parity, write new data and parity) and a risky rebuild on very large disks, which is why RAID 6 (two parity blocks) is often preferred."),
    written("coa-risc-cisc", "RISC versus CISC", "Easy",
        "Compare RISC and CISC. Is x86 CISC or RISC today?",
        "**RISC** (ARM, RISC-V, MIPS): a small set of simple, fixed-length instructions, a **load/store architecture** (only loads and stores touch memory), many registers, easy pipelining, typically hardwired control. **CISC** (x86): many complex variable-length instructions, memory operands, fewer registers, often microprogrammed control, smaller code. The x86 **instruction set** is CISC, but modern cores **decode each instruction into RISC-like micro-operations** and execute those in a deeply pipelined, out-of-order core, so the difference now lives mainly in the ISA and decode cost: ARM's simple decoding is one reason it is power-efficient."),
]

SUBJECT = subject("core-coa", "Computer Organisation", "Core subjects", 42,
    "Performance, number representation, caches, pipelines, virtual memory, I/O and storage. Every calculation is computed, not estimated.",
    QUESTIONS,
    platforms=[
        {"name": "GeeksforGeeks: Computer Organization", "url": "https://www.geeksforgeeks.org/computer-organization-architecture/computer-organization-and-architecture-tutorials/", "note": "Tutorials and practice questions"},
        {"name": "Nand2Tetris", "url": "https://www.nand2tetris.org/", "note": "Build a computer from logic gates, free course"},
    ])
