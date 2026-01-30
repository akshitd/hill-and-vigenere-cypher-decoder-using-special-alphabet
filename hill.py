#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple

# ===== Assignment alphabet (ORDER MATTERS) =====
# A=0 ... Z=25, ','=26, '.'=27, '-'=28
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ,.-"
MOD = len(ALPHABET)
IDX = {ch: i for i, ch in enumerate(ALPHABET)}


def clean_text(s: str) -> str:
    """Uppercase and keep only symbols in the 29-char alphabet."""
    s = s.upper()
    return "".join(ch for ch in s if ch in IDX)


def digram_counts(text: str) -> Counter:
    return Counter(text[i:i + 2] for i in range(len(text) - 1))


def text_to_nums(text: str) -> List[int]:
    return [IDX[ch] for ch in text]


def nums_to_text(nums: List[int]) -> str:
    return "".join(ALPHABET[n % MOD] for n in nums)


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def modinv(a: int, m: int) -> Optional[int]:
    a %= m
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def mat2_inv(M: List[List[int]]) -> Optional[List[List[int]]]:
    """Inverse of 2x2 matrix mod MOD. M = [[a,b],[c,d]]"""
    a, b = M[0]
    c, d = M[1]
    det = (a * d - b * c) % MOD
    inv_det = modinv(det, MOD)
    if inv_det is None:
        return None
    # inv = inv_det * [[d,-b],[-c,a]]
    return [
        [(d * inv_det) % MOD, ((-b) * inv_det) % MOD],
        [(((-c) * inv_det) % MOD), (a * inv_det) % MOD],
    ]


def mat2_mul(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """2x2 multiply mod MOD."""
    return [
        [(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % MOD,
         (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % MOD],
        [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % MOD,
         (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % MOD],
    ]


def hill2_decrypt(cipher: str, K_inv: List[List[int]]) -> str:
    """Decrypt 2x2 Hill: P = K_inv * C (pairs), mod MOD."""
    nums = text_to_nums(cipher)
    # If odd length, drop last char (common in classical Hill tasks)
    if len(nums) % 2 == 1:
        nums = nums[:-1]

    out = []
    for i in range(0, len(nums), 2):
        c0, c1 = nums[i], nums[i + 1]
        p0 = (K_inv[0][0] * c0 + K_inv[0][1] * c1) % MOD
        p1 = (K_inv[1][0] * c0 + K_inv[1][1] * c1) % MOD
        out.append(p0)
        out.append(p1)
    return nums_to_text(out)


def score_english_like(s: str) -> int:
    """
    Very simple scoring: count common English patterns in cleaned text.
    (No spaces exist, but THE/AND/ING etc still appear.)
    """
    pats = ["THE", "AND", "ING", "HER", "HIS", "TH", "HE", "ER", "IN", "RE", "ON", "ED", "YOU", "ION"]
    score = 0
    for p in pats:
        score += s.count(p) * (len(p) ** 2)
    return score


def digram_to_colvec(dg: str) -> List[int]:
    """Return column vector [x;y] for digram."""
    return [IDX[dg[0]], IDX[dg[1]]]


def build_P_matrix(p1: str, p2: str) -> List[List[int]]:
    """
    Build 2x2 matrix from plaintext digrams p1, p2 as columns.
    Example: p1='TH', p2='HE'
    """
    v1 = digram_to_colvec(p1)
    v2 = digram_to_colvec(p2)
    return [[v1[0], v2[0]], [v1[1], v2[1]]]


def build_C_matrix(c1: str, c2: str) -> List[List[int]]:
    """Build 2x2 matrix from ciphertext digrams c1, c2 as columns."""
    v1 = digram_to_colvec(c1)
    v2 = digram_to_colvec(c2)
    return [[v1[0], v2[0]], [v1[1], v2[1]]]


def key_matrix_to_4chars(K: List[List[int]]) -> str:
    return "".join(ALPHABET[x] for row in K for x in row)


def main():
    # Load ciphertext 3 (Hill)
    print("Reading:", Path("3.txt").resolve())
    ct_raw = Path("3.txt").read_text(encoding="utf-8", errors="ignore")
    ct = clean_text(ct_raw)

    print("=== Hill 2x2 key search for ciphertext 3 ===")
    print(f"Length (cleaned): {len(ct)}")
    print(f"Alphabet ({MOD}): {ALPHABET}")

    # Digram frequency to pick candidates (top N)
    dcounts = digram_counts(ct)
    topN = 50  # increase if needed
    candidates = [dg for dg, _ in dcounts.most_common(topN)]

    print(f"\nTop {topN} ciphertext digrams (candidates):")
    print(", ".join(candidates))

    # Plaintext digrams we expect to be frequent (Appendix)
    p1, p2 = "TH", "HE"

    P = build_P_matrix(p1, p2)
    P_inv = mat2_inv(P)
    if P_inv is None:
        raise RuntimeError("Plaintext matrix not invertible mod 29; choose different digrams.")

    print(f"\nUsing assumed plaintext digrams: {p1} and {p2}")
    print(f"Plaintext matrix P: {P}")
    print(f"P inverse mod 29: {P_inv}")

    best = []  # list of (score, c1, c2, K, preview)

    # Try all pairs of candidate ciphertext digrams for (TH, HE)
    prefix = ct[:1200]  # decrypt a longer prefix for better scoring
    for i, c1 in enumerate(candidates):
        for j, c2 in enumerate(candidates):
            if i == j:
                continue

            C = build_C_matrix(c1, c2)
            # K = C * P^{-1} mod 29
            K = mat2_mul(C, P_inv)

            # K must be invertible to decrypt
            K_inv = mat2_inv(K)
            if K_inv is None:
                continue

            pt = hill2_decrypt(prefix, K_inv)
            sc = score_english_like(pt)
            if sc > 0:
                preview = pt[:260]
                best.append((sc, c1, c2, K, preview))

    if not best:
        print("\nNo candidate keys scored > 0.")
        print("Try increasing topN (e.g., 80 or 120), or expand the prefix length.")
        return

    best.sort(reverse=True, key=lambda x: x[0])

    print("\n=== Top 10 candidate keys ===")
    for rank, (sc, c1, c2, K, preview) in enumerate(best[:10], 1):
        print(f"\n#{rank}  score={sc}")
        print(f"Assume Encrypt('{p1}')='{c1}', Encrypt('{p2}')='{c2}'")
        print(f"K (numbers) = {K}")
        print(f"K (4 chars row-by-row) = {key_matrix_to_4chars(K)}")
        print(f"Preview: {preview}")

    # Pick best and decrypt full ciphertext
    sc, c1, c2, K, _ = best[0]
    K_inv = mat2_inv(K)
    assert K_inv is not None

    full_pt = hill2_decrypt(ct, K_inv)
    out_path = Path("cipher3_plaintext.txt")
    out_path.write_text(full_pt, encoding="utf-8")

    print("\n=== BEST KEY CHOSEN ===")
    print(f"Best mapping: Encrypt('{p1}')='{c1}', Encrypt('{p2}')='{c2}'")
    print(f"Key (4 chars row-by-row): {key_matrix_to_4chars(K)}")
    print("Full plaintext written to:", out_path.resolve())


if __name__ == "__main__":
    main()
