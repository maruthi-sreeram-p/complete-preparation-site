@part bit-manipulation | Bit Manipulation | advanced
## The idea

Computers store integers as bits, and operating directly on those bits is both fast and, for some problems, the only way to meet a "constant extra space" requirement. The tricks are few; learning them once pays off across many problems.

| Operator | Meaning | Handy for |
|---|---|---|
| `a & b` | 1 where both are 1 | Testing a bit, clearing bits |
| `a \| b` | 1 where either is 1 | Setting a bit |
| `a ^ b` | 1 where they differ | Finding the odd one out, adding without carry |
| `~a` | Flips every bit | Masks |
| `a << k`, `a >> k` | Multiply or divide by 2ᵏ (`>>` keeps the sign) | Building masks, halving |
| `a >>> k` | Unsigned right shift (fills with zeros) | Walking all 32 bits of a negative number |

The identities worth memorising: `x ^ x = 0`, `x ^ 0 = x`, XOR is commutative and associative, `x & (x - 1)` **clears the lowest set bit**, `x & -x` **isolates the lowest set bit**, and `x & 1` is the parity.

!tip Signal words :: "appears twice except one", "without extra space", "XOR", "number of 1 bits", "power of two", "subset as a mask", "add without +". A subset of up to about 20 items can be stored as one `int` mask, which is how many DP-over-subsets solutions work.

## The Java toolkit and templates

Java `int` is **32 bits, signed, two's complement**, and `long` is 64. There are no unsigned types, so the unsigned shift `>>>` and library helpers such as `Integer.bitCount` matter.

```java BitTricks.java
public class BitTricks {

    /** Single Number: pairs cancel under XOR, the lone number remains. O(n) time, O(1) space. */
    static int singleNumber(int[] nums) {
        int result = 0;
        for (int n : nums) result ^= n;
        return result;
    }

    /** Number of 1 Bits: each step clears the lowest set bit, so it loops once per set bit. */
    static int hammingWeight(int n) {
        int count = 0;
        while (n != 0) {
            n &= n - 1;
            count++;
        }
        return count;
    }

    /** Counting Bits: bits(i) = bits(i / 2) + the last bit of i. */
    static int[] countBits(int n) {
        int[] bits = new int[n + 1];
        for (int i = 1; i <= n; i++) bits[i] = bits[i >> 1] + (i & 1);
        return bits;
    }

    /** Reverse Bits: shift the result left, copy the lowest bit of n, shift n right (unsigned!). */
    static int reverseBits(int n) {
        int result = 0;
        for (int i = 0; i < 32; i++) {
            result = (result << 1) | (n & 1);
            n >>>= 1;                                        // >>> so a negative n does not drag sign bits in
        }
        return result;
    }

    /** Missing Number: XOR every index and every value; each present number cancels its own index. */
    static int missingNumber(int[] nums) {
        int result = nums.length;
        for (int i = 0; i < nums.length; i++) result ^= i ^ nums[i];
        return result;
    }

    /** Sum of Two Integers: XOR is the sum without carries, AND shifted left is the carries. Repeat until no carry. */
    static int getSum(int a, int b) {
        while (b != 0) {
            int carry = (a & b) << 1;
            a ^= b;
            b = carry;
        }
        return a;
    }

    /** Power of two: exactly one bit set. */
    static boolean isPowerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;
    }

    /** Test, set and clear the k-th bit. */
    static boolean hasBit(int x, int k) { return (x >> k & 1) == 1; }
    static int setBit(int x, int k) { return x | (1 << k); }
    static int clearBit(int x, int k) { return x & ~(1 << k); }
}
```

**What to notice.** `getSum` terminates for negative numbers too, because Java `int` arithmetic wraps at 32 bits and the carry eventually shifts out. In `reverseBits`, using `>>` instead of `>>>` would work for positive inputs and quietly fail for negative ones.

## Pitfalls and interview angle

- **`>>` versus `>>>`** on negative numbers. `-8 >> 1` is `-4` (sign kept); `-8 >>> 1` is a large positive number.
- **Shifting by 32 or more.** For `int`, the shift distance is taken modulo 32, so `1 << 32` equals `1`, not `0`. Use `long` (`1L << k`) when k can reach 32.
- **Operator precedence.** `==` binds tighter than `&`, so `x & 1 == 0` does not do what it looks like. Write `(x & 1) == 0`.
- **Overflow in Reverse Integer.** Check before multiplying: compare with `Integer.MAX_VALUE / 10` instead of relying on wrap-around.
- **Readability.** Say what the trick means in a comment; `n &= n - 1` is cryptic to a reader.

!interview Interview angle: Every number in an array appears twice except one. Find it in O(1) space. :: XOR all the numbers. A number XORed with itself is 0, and 0 XOR x is x, and XOR is order independent, so the pairs cancel and only the single number remains. If every number appears *three* times except one, count the bits at each position modulo 3 instead.

!keypoints `x & (x - 1)` clears the lowest set bit; `x & -x` isolates it ;; `x ^ x = 0` and `x ^ 0 = x` make XOR the tool for "find the odd one out" ;; Java `int` is 32-bit signed: use `>>>` to shift without the sign and `1L << k` for k >= 32 ;; XOR is addition without carry; AND shifted left is the carry ;; Parenthesise bit tests: `(x & 1) == 0` ;; A small set can be a bitmask in an `int`

?? What does `n & (n - 1)` do and how does it count set bits?
=> It clears the lowest set bit of n. Repeating it until n is zero takes one iteration per set bit, so the loop count is the number of 1 bits.

?? Why do you use `>>>` instead of `>>` when reversing bits?
=> `>>` copies the sign bit into the vacated positions, so for a negative number the loop would shift in ones and never reach zero in the intended way. `>>>` always shifts in zeros, so all 32 bits are processed correctly.

?? How can you add two integers without using `+`?
=> XOR gives the sum of each bit without carry and `(a & b) << 1` gives the carries. Replace `a` with the XOR and `b` with the carries and repeat until there are no carries left.
