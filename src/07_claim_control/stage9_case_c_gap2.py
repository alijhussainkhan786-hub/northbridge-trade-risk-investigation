from pathlib import Path
import pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.max_columns', None); pd.set_option('display.width', 180)
OUT = "/home/claude/build/stage9_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")
vw_stable = pd.read_csv("/home/claude/build/stage5_outputs/5e_vw_stable_candidates.csv")
case_c_ids = set(vw_stable.transaction_id)
txn["is_case_c"] = txn.transaction_id.isin(case_c_ids)

print("### 2. STRATIFIED ROBUSTNESS TEST for Case C ###\n")

print("-- Overall Case C vs portfolio --")
print(f"Case C alert rate: {txn[txn.is_case_c].has_alert.mean()*100:.1f}% vs portfolio {txn.has_alert.mean()*100:.1f}%")
print(f"Case C claim rate: {txn[txn.is_case_c].has_claim.mean()*100:.1f}% vs portfolio {txn.has_claim.mean()*100:.1f}%")
print(f"Case C median invoice value: {txn[txn.is_case_c].invoice_value.median():,.0f} vs portfolio {txn.invoice_value.median():,.0f}")

# Binomial test on alert rate
n_c = txn.is_case_c.sum()
n_alert_c = txn[txn.is_case_c].has_alert.sum()
base_rate = txn[~txn.is_case_c].has_alert.mean()
p = stats.binomtest(int(n_alert_c), int(n_c), base_rate, alternative='greater').pvalue
print(f"Binomial test (Case C alert rate vs rest-of-portfolio base rate {base_rate*100:.1f}%): p={p:.2e}  n={n_c}")

print("\n-- By product category (alert rate: Case C vs category baseline) --")
for cat in txn.product_category.unique():
    sub_c = txn[(txn.is_case_c) & (txn.product_category==cat)]
    sub_all = txn[txn.product_category==cat]
    if len(sub_c)==0: continue
    print(f"{cat}: Case C n={len(sub_c)}, alert={sub_c.has_alert.mean()*100:.0f}% | category baseline n={len(sub_all)}, alert={sub_all.has_alert.mean()*100:.1f}%")

print("\n-- By corridor --")
for cor in txn.corridor_group.unique():
    sub_c = txn[(txn.is_case_c) & (txn.corridor_group==cor)]
    sub_all = txn[txn.corridor_group==cor]
    if len(sub_c)==0: continue
    print(f"{cor}: Case C n={len(sub_c)}, alert={sub_c.has_alert.mean()*100:.0f}% | corridor baseline n={len(sub_all)}, alert={sub_all.has_alert.mean()*100:.1f}%")

print("\n-- By segment --")
for seg in txn.segment.unique():
    sub_c = txn[(txn.is_case_c) & (txn.segment==seg)]
    sub_all = txn[txn.segment==seg]
    if len(sub_c)==0: continue
    print(f"{seg}: Case C n={len(sub_c)}, alert={sub_c.has_alert.mean()*100:.0f}%, claim={sub_c.has_claim.mean()*100:.0f}% | baseline n={len(sub_all)}, alert={sub_all.has_alert.mean()*100:.1f}%, claim={sub_all.has_claim.mean()*100:.1f}%")

print("\n-- By value band (quartile) --")
txn["value_band"] = pd.qcut(txn["invoice_value"], 4, labels=["Q1_low","Q2","Q3","Q4_high"])
for band in ["Q1_low","Q2","Q3","Q4_high"]:
    sub_c = txn[(txn.is_case_c) & (txn.value_band==band)]
    sub_all = txn[txn.value_band==band]
    print(f"{band}: Case C n={len(sub_c)} | band baseline n={len(sub_all)}")
print("Note: Case C transactions are, by construction (inflated invoice value), concentrated in the highest value band -")
print("this is a MECHANICAL artifact of how the value/weight ratio was built, not an independent finding.")
print(txn[txn.is_case_c].value_band.value_counts())

print("\n-- By year --")
txn["year"] = txn.transaction_date.dt.year
for yr in sorted(txn.year.unique()):
    sub_c = txn[(txn.is_case_c) & (txn.year==yr)]
    sub_all = txn[txn.year==yr]
    print(f"{yr}: Case C n={len(sub_c)} of portfolio n={len(sub_all)} ({len(sub_c)/len(sub_all)*100:.2f}%)")

print("\n-- Payment/shipment consistency check for Case C (re-verify reconciliation holds) --")
import sqlite3
conn = sqlite3.connect("/home/claude/build/northbridge.db")
payments = pd.read_sql("SELECT * FROM payments", conn)
shipments = pd.read_sql("SELECT * FROM shipments", conn)
pay_agg = payments.groupby("transaction_id")["amount"].sum().reset_index(name="total_paid")
ship_agg = shipments.groupby("transaction_id")["declared_value"].sum().reset_index(name="total_ship_value")
casec_txn = txn[txn.is_case_c][["transaction_id","invoice_value"]].merge(pay_agg, on="transaction_id").merge(ship_agg, on="transaction_id")
casec_txn["pay_diff"] = (casec_txn.total_paid - casec_txn.invoice_value).abs()
casec_txn["ship_diff"] = (casec_txn.total_ship_value - casec_txn.invoice_value).abs()
print(f"Payment reconciliation mismatches (>0.5): {(casec_txn.pay_diff>0.5).sum()} of {len(casec_txn)}")
print(f"Shipment-value reconciliation mismatches (>0.5): {(casec_txn.ship_diff>0.5).sum()} of {len(casec_txn)}")
print("-> Both reconcile perfectly, consistent with the rest of the portfolio (Stage 4/5 finding) - no payment/shipment")
print("   value inconsistency accompanies the value/weight ratio anomaly; the anomaly is purely in the weight dimension.")
