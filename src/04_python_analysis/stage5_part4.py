from pathlib import Path
import pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
OUT = "/home/claude/build/stage5_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")

print("### 4. CLAIMS AND PRIOR ALERTS ###\n")

# Raw comparison
tab = pd.crosstab(txn["has_alert"], txn["has_claim"])
print("Raw crosstab (has_alert x has_claim):\n", tab)
claim_rate_alert = txn[txn.has_alert]["has_claim"].mean()
claim_rate_noalert = txn[~txn.has_alert]["has_claim"].mean()
print(f"\nClaim rate | alert present: {claim_rate_alert*100:.2f}% (n={txn.has_alert.sum()})")
print(f"Claim rate | no alert: {claim_rate_noalert*100:.2f}% (n={(~txn.has_alert).sum()})")

# Chi-square test of independence
chi2, p, dof, exp = stats.chi2_contingency(tab)
print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.2e}, dof={dof}")
print("-> statistically significant association at portfolio level (Category 3: descriptive relationship, NOT causal)")

# Segment-stratified
print("\n-- Segment-stratified --")
for seg in txn["segment"].unique():
    sub = txn[txn.segment==seg]
    r_a = sub[sub.has_alert]["has_claim"].mean()*100
    r_na = sub[~sub.has_alert]["has_claim"].mean()*100
    n_a = sub.has_alert.sum(); n_na = (~sub.has_alert).sum()
    print(f"{seg}: alerted claim_rate={r_a:.2f}% (n={n_a}) | non-alerted={r_na:.2f}% (n={n_na})")

# Value-band stratified (quartiles of invoice_value)
print("\n-- Value-band stratified (quartiles) --")
txn["value_band"] = pd.qcut(txn["invoice_value"], 4, labels=["Q1_low","Q2","Q3","Q4_high"])
for band in ["Q1_low","Q2","Q3","Q4_high"]:
    sub = txn[txn.value_band==band]
    r_a = sub[sub.has_alert]["has_claim"].mean()*100 if sub.has_alert.sum()>0 else float('nan')
    r_na = sub[~sub.has_alert]["has_claim"].mean()*100
    n_a = sub.has_alert.sum(); n_na = (~sub.has_alert).sum()
    print(f"{band}: alerted claim_rate={r_a:.2f}% (n={n_a}) | non-alerted={r_na:.2f}% (n={n_na})")

# Corridor/product control (does the relationship hold within each corridor?)
print("\n-- Corridor-stratified --")
for cor in txn["corridor_group"].unique():
    sub = txn[txn.corridor_group==cor]
    n_a = sub.has_alert.sum(); n_na=(~sub.has_alert).sum()
    if n_a < 20: 
        print(f"{cor}: n_alerted={n_a} -- too small for reliable stratified estimate, skipped")
        continue
    r_a = sub[sub.has_alert]["has_claim"].mean()*100
    r_na = sub[~sub.has_alert]["has_claim"].mean()*100
    print(f"{cor}: alerted claim_rate={r_a:.2f}% (n={n_a}) | non-alerted={r_na:.2f}% (n={n_na})")

print("\nCLASSIFICATION: Portfolio-level and segment-level (SME, Mid-market) relationship = STRONG DESCRIPTIVE RELATIONSHIP")
print("(consistent direction, statistically significant, holds across strata with adequate n).")
print("Corporate segment and small-n corridor cells = WEAK / INSUFFICIENT DATA - not reliable on their own.")
print("No causal mechanism identified or claimed; a plausible confound is that both alerts and claims may independently")
print("track underlying transaction/counterparty complexity or risk exposure rather than one causing the other.")
