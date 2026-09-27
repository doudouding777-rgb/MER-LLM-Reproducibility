#!/usr/bin/env python3
import csv
import math
import sys
from pathlib import Path


def exact_two_sided_binomial(k, n, p=0.5):
    observed = math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
    total = 0.0
    for i in range(n + 1):
        prob = math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
        if prob <= observed + 1e-18:
            total += prob
    return min(1.0, total)


def main(path):
    b_to_m = 0
    m_to_b = 0
    both_correct = 0
    both_wrong = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            base = int(row["base_correct"])
            mer = int(row["mer_correct"])
            if base and mer:
                both_correct += 1
            elif not base and mer:
                b_to_m += 1
            elif base and not mer:
                m_to_b += 1
            else:
                both_wrong += 1
    discordant = b_to_m + m_to_b
    chi2 = ((abs(b_to_m - m_to_b) - 1) ** 2) / discordant
    p = exact_two_sided_binomial(min(b_to_m, m_to_b), discordant)
    print(f"both_correct,{both_correct}")
    print(f"base_wrong_mer_correct,{b_to_m}")
    print(f"base_correct_mer_wrong,{m_to_b}")
    print(f"both_wrong,{both_wrong}")
    print(f"discordant_total,{discordant}")
    print(f"mcnemar_chi2_continuity_corrected,{chi2}")
    print(f"exact_binomial_two_sided_p,{p}")


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[1] / "paired_statistics" / "FINAL_HISTORICAL_PAIRED_CORRECTNESS.csv"
    main(sys.argv[1] if len(sys.argv) > 1 else default)
