@part math-geometry | Math & Geometry | advanced
## The idea

These problems rarely need a new data structure. They test whether you can handle **numbers and grids carefully**: overflow, rounding, edge cases, in-place transformations of a matrix, and a few classic algorithms (greatest common divisor, fast exponentiation, cycle detection on a number sequence).

| Area | The key idea | Problems |
|---|---|---|
| **Matrix in place** | Express a rotation or a traversal as a few simple moves (transpose then reverse rows; shrinking boundaries) | Rotate Image, Spiral Matrix, Set Matrix Zeroes |
| **Digits and strings of digits** | Process from the least significant digit with a carry; use an array of digits | Plus One, Multiply Strings |
| **Fast power** | Square the base and halve the exponent: O(log n) | Pow(x, n) |
| **Number sequences** | A sequence that repeats is a cycle: Floyd's tortoise and hare | Happy Number |
| **Counting with coordinates** | A hash map keyed by a point, count pairs that form a shape | Detect Squares |

!tip Signal words :: "in place", "without converting to integer", "without built-in power", "rotate", "spiral", "digits", "overflow". When values can reach 10⁹ or more, immediately ask yourself whether `int` is big enough.

## The Java toolkit and templates

```java MathGeometry.java
import java.util.*;

public class MathGeometry {

    /** Rotate Image 90 degrees clockwise in place: transpose, then reverse every row. */
    static void rotate(int[][] m) {
        int n = m.length;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int t = m[i][j];
                m[i][j] = m[j][i];
                m[j][i] = t;
            }
        }
        for (int[] row : m) {
            for (int l = 0, r = n - 1; l < r; l++, r--) {
                int t = row[l];
                row[l] = row[r];
                row[r] = t;
            }
        }
    }

    /** Spiral Matrix: shrink four boundaries as each side is consumed. */
    static List<Integer> spiralOrder(int[][] m) {
        List<Integer> out = new ArrayList<>();
        int top = 0, bottom = m.length - 1, left = 0, right = m[0].length - 1;
        while (top <= bottom && left <= right) {
            for (int c = left; c <= right; c++) out.add(m[top][c]);
            top++;
            for (int r = top; r <= bottom; r++) out.add(m[r][right]);
            right--;
            if (top <= bottom) {                                   // a single remaining row must not be walked twice
                for (int c = right; c >= left; c--) out.add(m[bottom][c]);
                bottom--;
            }
            if (left <= right) {                                   // likewise for a single remaining column
                for (int r = bottom; r >= top; r--) out.add(m[r][left]);
                left++;
            }
        }
        return out;
    }

    /** Pow(x, n) by repeated squaring. n is widened to long because -Integer.MIN_VALUE overflows an int. */
    static double myPow(double x, int n) {
        long exponent = n;
        if (exponent < 0) {
            x = 1 / x;
            exponent = -exponent;
        }
        double result = 1;
        while (exponent > 0) {
            if ((exponent & 1) == 1) result *= x;                  // this bit of the exponent is set
            x *= x;
            exponent >>= 1;
        }
        return result;
    }

    /** Happy Number: the digit-square sequence either reaches 1 or enters a cycle. Floyd detects the cycle in O(1) space. */
    static boolean isHappy(int n) {
        int slow = n, fast = next(n);
        while (fast != 1 && slow != fast) {
            slow = next(slow);
            fast = next(next(fast));
        }
        return fast == 1;
    }

    private static int next(int n) {
        int sum = 0;
        while (n > 0) {
            int digit = n % 10;
            sum += digit * digit;
            n /= 10;
        }
        return sum;
    }

    /** Plus One on an array of digits: carry from the right; if every digit was 9, the result is longer. */
    static int[] plusOne(int[] digits) {
        for (int i = digits.length - 1; i >= 0; i--) {
            if (digits[i] < 9) {
                digits[i]++;
                return digits;
            }
            digits[i] = 0;
        }
        int[] longer = new int[digits.length + 1];
        longer[0] = 1;
        return longer;
    }

    /** Multiply Strings as in school: digit i of a times digit j of b lands in positions i + j and i + j + 1. */
    static String multiply(String a, String b) {
        if (a.equals("0") || b.equals("0")) return "0";
        int[] digits = new int[a.length() + b.length()];
        for (int i = a.length() - 1; i >= 0; i--) {
            for (int j = b.length() - 1; j >= 0; j--) {
                int product = (a.charAt(i) - '0') * (b.charAt(j) - '0') + digits[i + j + 1];
                digits[i + j + 1] = product % 10;
                digits[i + j] += product / 10;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int d : digits) {
            if (sb.length() == 0 && d == 0) continue;              // strip leading zeros
            sb.append(d);
        }
        return sb.toString();
    }

    /** Greatest common divisor (Euclid). */
    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }
}
```

**What to notice.** `myPow` multiplies the result only when the current exponent bit is 1 and squares the base every round, so it does about 31 multiplications instead of up to 2 billion. In `spiralOrder` the two `if` guards prevent walking a lone row or column twice, the classic bug on non-square matrices.

## Pitfalls and interview angle

- **Overflow.** `int` holds about ±2.1 × 10⁹. Products of two such values need `long`. `Math.abs(Integer.MIN_VALUE)` is still negative. `Math.multiplyExact` and `Math.addExact` throw instead of wrapping.
- **Floating-point equality.** Never compare `double` values with `==`; use a tolerance. Prefer integers, or integer cross-multiplication for slopes and ratios.
- **Integer division and modulo with negatives.** `-7 / 2` is `-3` and `-7 % 2` is `-1` in Java; use `Math.floorMod` when you need a non-negative remainder.
- **Modifying a matrix while reading it** (Set Matrix Zeroes): use the first row and column as markers, with two flags remembering whether they themselves must be zeroed.
- **Not asking about the edge cases**: empty input, one row or column, zero, negative exponents.

!interview Interview angle: Why can `Math.abs(Integer.MIN_VALUE)` return a negative number? :: The range of `int` is asymmetric: -2³¹ to 2³¹ - 1. There is no positive 2³¹, so negating the minimum value wraps back to itself. Widen to `long` before negating, as the `myPow` method does with the exponent.

!keypoints Matrix problems become simple moves: rotate = transpose + reverse rows ;; Shrinking four boundaries gives the spiral; guard the last row and column ;; Fast exponentiation squares the base and halves the exponent: O(log n) ;; A repeating number sequence is a cycle: use Floyd instead of a set when space matters ;; Think about overflow first: use `long`, `Math.addExact`, and remember `Math.abs(Integer.MIN_VALUE)` ;; Use `Math.floorMod` for non-negative remainders

?? How do you rotate a square matrix by 90 degrees in place?
=> Transpose it (swap `m[i][j]` with `m[j][i]` for j > i) and then reverse each row. That rotates clockwise; reversing columns instead of rows, or reversing before transposing, gives the other directions.

?? Why is `x * x` as an `int` risky for large inputs?
=> The product of two values near 10⁵ already exceeds 2³¹ and wraps around silently to a wrong, possibly negative number. Cast one operand to `long` before multiplying.

?? How does Pow(x, n) run in O(log n)?
=> The exponent is processed bit by bit: the base is squared each round and the result is multiplied by it whenever the current bit is 1. An exponent below 2³¹ has at most 31 bits, so at most about 62 multiplications are needed.
