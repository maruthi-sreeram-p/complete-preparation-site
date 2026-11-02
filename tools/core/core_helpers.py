"""Names available inside the `!py` checks of tools/core/mcq/*.txt (see build_core.py and build_gate.py).

Everything from the GATE helpers (num, cache_misses, booth_ops, min_sop ...) is available, plus the functions below
for data representation, pipelines, caches, memory and disks.
"""
import itertools
import struct
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gate"))
from helpers import *  # noqa: E402,F401,F403
from helpers import num  # noqa: E402,F401  (re-exported explicitly)


# ---------------------------------------------------------------- data representation
def twos(n, bits):
    """Two's complement bit string of n in `bits` bits."""
    assert -(1 << (bits - 1)) <= n < (1 << (bits - 1)), f"{n} does not fit in {bits} bits"
    return format(n & ((1 << bits) - 1), f"0{bits}b")


def from_twos(bit_string):
    value = int(bit_string, 2)
    return value - (1 << len(bit_string)) if bit_string[0] == "1" else value


def ones_complement(n, bits):
    """One's complement bit string of n (negative numbers: invert the magnitude)."""
    return format(n, f"0{bits}b") if n >= 0 else format(~(-n) & ((1 << bits) - 1), f"0{bits}b")


def add_overflows(a, b, bits):
    """True if a + b overflows a `bits`-bit two's complement register."""
    return not (-(1 << (bits - 1)) <= a + b < (1 << (bits - 1)))


def ieee32(x):
    """(sign, exponent bits, fraction bits, hex) of a number as IEEE 754 single precision."""
    raw = struct.unpack(">I", struct.pack(">f", x))[0]
    b = format(raw, "032b")
    return b[0], b[1:9], b[9:], format(raw, "08X")


def ieee32_value(hex_string):
    return struct.unpack(">f", struct.pack(">I", int(hex_string, 16)))[0]


def ieee64(x):
    raw = struct.unpack(">Q", struct.pack(">d", x))[0]
    b = format(raw, "064b")
    return b[0], b[1:12], b[12:], format(raw, "016X")


def hamming_parity_bits(m):
    """Smallest r with 2**r >= m + r + 1 (single-error-correcting Hamming code for m data bits)."""
    r = 0
    while 2 ** r < m + r + 1:
        r += 1
    return r


def gray(n):
    return n ^ (n >> 1)


# ---------------------------------------------------------------- performance and pipelines
def amdahl(fraction, factor):
    """Overall speedup when `fraction` of the run time is made `factor` times faster."""
    return 1 / ((1 - fraction) + fraction / factor)


def pipeline_cycles(stages, instructions, stall_cycles=0):
    """Cycles to run `instructions` through an ideal `stages`-stage pipeline plus extra stall cycles."""
    return stages + instructions - 1 + stall_cycles


def amat(hit_time, miss_rate, miss_penalty):
    return hit_time + miss_rate * miss_penalty


def amat_two_level(h1, m1, h2, m2, memory):
    """Average memory access time with an L1 (hit time h1, local miss rate m1) and L2 (h2, local miss rate m2) cache."""
    return h1 + m1 * (h2 + m2 * memory)


def cache_fields(address_bits, cache_bytes, block_bytes, ways):
    """-> (tag bits, index bits, offset bits) of a set-associative cache (ways=1: direct mapped)."""
    blocks = cache_bytes // block_bytes
    sets = blocks // ways
    offset = block_bytes.bit_length() - 1
    index = sets.bit_length() - 1
    return address_bits - index - offset, index, offset


def data_hazards(program):
    """Read-after-write dependences in a list of (dest, src1, src2) register tuples: -> list of (producer index, consumer index)."""
    found = []
    for j, (_, *sources) in enumerate(program):
        for i in range(j):
            if program[i][0] in sources and program[i][0] is not None:
                found.append((i, j))
    return found


def page_faults(reference, frames, policy="LRU"):
    """Page faults for a reference string with FIFO, LRU or OPT replacement."""
    memory, faults = [], 0
    for i, page in enumerate(reference):
        if page in memory:
            if policy == "LRU":
                memory.remove(page)
                memory.append(page)
            continue
        faults += 1
        if len(memory) == frames:
            if policy == "OPT":
                future = reference[i + 1:]
                victim = max(memory, key=lambda p: future.index(p) if p in future else len(future) + 1)
                memory.remove(victim)
            else:
                memory.pop(0)
        memory.append(page)
    return faults


# ---------------------------------------------------------------- storage and I/O
def disk_access_ms(rpm, seek_ms, sector_bytes, sectors_per_track, transfer_bytes):
    """Average access time in ms: seek + half a rotation + transfer."""
    rotation_ms = 60000 / rpm
    transfer_ms = rotation_ms * (transfer_bytes / (sector_bytes * sectors_per_track))
    return seek_ms + rotation_ms / 2 + transfer_ms


def raid_usable(level, disks, disk_tb):
    return {0: disks, 1: disks / 2, 5: disks - 1, 6: disks - 2, 10: disks / 2}[level] * disk_tb


# ---------------------------------------------------------------- logic
def truth_table(function, variables):
    """Output column of `function(*bits)` over all input combinations, MSB first."""
    return [int(bool(function(*bits))) for bits in itertools.product((0, 1), repeat=variables)]


def same_function(f, g, variables):
    return truth_table(f, variables) == truth_table(g, variables)


def minterms(function, variables):
    return [i for i, out in enumerate(truth_table(function, variables)) if out]


def ripple_delay(bits, carry_ns, sum_ns=0):
    """Worst-case delay of a ripple-carry adder: the carry passes through every stage, the last stage also produces a sum."""
    return bits * carry_ns + sum_ns
