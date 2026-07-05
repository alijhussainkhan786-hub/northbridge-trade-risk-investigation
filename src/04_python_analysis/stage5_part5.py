from pathlib import Path
import pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
OUT = "/home/claude/build/stage5_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")

print("### 5. VALUE/WEIGHT ANOMALY SENSITIVITY ###\n")
has_weight = txn.dropna(subset=["value_per_kg"]).copy()
print(f"Transactions with a computable value_per_kg (i.e. >=1 shipment): {len(has_weight)} of {len(txn)}")

print("\n-- Simple ratio-vs-category-average threshold sensitivity --")
for t in [3,5,10,20,50]:
    n = (has_weight["vw_ratio_vs_cat"] > t).sum()
    print(f"  >{t}x category average: {n} candidates ({n/len(has_weight)*100:.2f}%)")

print("\n-- Robust z-score within product category (using median/MAD, robust to outliers) --")
def robust_z(group):
    med = group.median()
    mad = (group - med).abs().median()
    mad_scaled = mad * 1.4826  # normal-consistent scaling
    if mad_scaled == 0:
        return pd.Series(0, index=group.index)
    return (group - med) / mad_scaled

has_weight["robust_z"] = has_weight.groupby("product_category")["value_per_kg"].transform(robust_z)
for z in [3,5,10]:
    n = (has_weight["robust_z"].abs() > z).sum()
    print(f"  |robust_z| > {z}: {n} candidates ({n/len(has_weight)*100:.2f}%)")

print("\n-- IQR-based outlier detection within product category --")
def iqr_flag(group, k=1.5):
    q1, q3 = group.quantile(0.25), group.quantile(0.75)
    iqr = q3 - q1
    return (group > q3 + k*iqr) | (group < q1 - k*iqr)

for k in [1.5, 3.0]:
    flags = has_weight.groupby("product_category")["value_per_kg"].transform(lambda g: iqr_flag(g, k))
    n = flags.sum()
    print(f"  IQR outlier (k={k}): {n} candidates ({n/len(has_weight)*100:.2f}%)")

print("\n-- Overlap between methods (5x ratio vs robust_z>5 vs IQR k=3) --")
set_5x = set(has_weight[has_weight.vw_ratio_vs_cat>5]["transaction_id"])
set_z5 = set(has_weight[has_weight.robust_z.abs()>5]["transaction_id"])
set_iqr3 = set(has_weight[has_weight.groupby("product_category")["value_per_kg"].transform(lambda g: iqr_flag(g,3.0))]["transaction_id"])
print(f"5x-ratio candidates: {len(set_5x)}")
print(f"robust_z>5 candidates: {len(set_z5)}")
print(f"IQR(k=3) candidates: {len(set_iqr3)}")
print(f"Intersection of all 3 methods: {len(set_5x & set_z5 & set_iqr3)}")
print(f"In 5x-ratio but NOT in either other method: {len(set_5x - set_z5 - set_iqr3)}")
print(f"In all pairwise combos (5x & z5): {len(set_5x & set_z5)} | (5x & iqr3): {len(set_5x & set_iqr3)} | (z5 & iqr3): {len(set_z5 & set_iqr3)}")

stable_candidates = set_5x & set_z5 & set_iqr3
print(f"\nSTABLE candidates (flagged by all 3 independent methods): {len(stable_candidates)} of {len(has_weight)} ({len(stable_candidates)/len(has_weight)*100:.2f}%)")
pd.DataFrame({"transaction_id": sorted(stable_candidates)}).to_csv(f"{OUT}/5e_vw_stable_candidates.csv", index=False)

has_weight[["transaction_id","customer_id","counterparty_id","product_category","value_per_kg","vw_ratio_vs_cat","robust_z"]].sort_values("vw_ratio_vs_cat", ascending=False).head(30).to_csv(f"{OUT}/5e_vw_all_methods_top30.csv", index=False)

print("\nCONCLUSION: No single threshold is 'correct'. Candidate count ranges from 0.4% (50x) to 2.6% (3x ratio) depending on")
print("method/threshold. The intersection of 3 independent methods (ratio, robust z-score, IQR) is the most defensible")
print("STABLE candidate set for Stage 6/7, since it is not an artifact of any one method's threshold choice.")
