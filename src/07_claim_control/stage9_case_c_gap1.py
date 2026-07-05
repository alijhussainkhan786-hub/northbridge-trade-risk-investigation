from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 180)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage9_outputs"
import os; os.makedirs(OUT, exist_ok=True)

txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")
vw_stable = pd.read_csv("/home/claude/build/stage5_outputs/5e_vw_stable_candidates.csv")
case_c_ids = set(vw_stable.transaction_id)

shipments = pd.read_sql("SELECT * FROM shipments", conn, parse_dates=["departure_date","arrival_date"])
payments = pd.read_sql("SELECT * FROM payments", conn, parse_dates=["payment_date"])
pair_summary = pd.read_csv("/home/claude/build/stage6_outputs/6a_entity_resolution_pairs.csv")

print("### 1. DATA-QUALITY CROSS-CHECK for Case C (85 transactions) ###\n")
n_case_c = len(case_c_ids)

# Shipment date-logic errors
ship_err_ids = set(shipments[(shipments.arrival_date.notna()) & (shipments.arrival_date < shipments.departure_date)]["transaction_id"])
overlap1 = case_c_ids & ship_err_ids
print(f"Shipment date-logic errors: {len(overlap1)}/{n_case_c} ({len(overlap1)/n_case_c*100:.1f}%) | portfolio rate: {len(ship_err_ids)}/6090 shipments ({len(ship_err_ids)/6090*100:.1f}%)")

# Payment date-logic errors
pay_err_ids = set(payments.merge(txn[["transaction_id","transaction_date"]], on="transaction_id")
                   .pipe(lambda d: d[d.payment_date < d.transaction_date])["transaction_id"])
overlap2 = case_c_ids & pay_err_ids
print(f"Payment date-logic errors: {len(overlap2)}/{n_case_c} ({len(overlap2)/n_case_c*100:.1f}%) | portfolio rate: {len(pay_err_ids)}/6000 ({len(pay_err_ids)/6000*100:.1f}%)")

# Missing arrival_date
missing_arr_ids = set(shipments[shipments.arrival_date.isna()]["transaction_id"])
overlap3 = case_c_ids & missing_arr_ids
print(f"Missing arrival_date: {len(overlap3)}/{n_case_c} ({len(overlap3)/n_case_c*100:.1f}%) | portfolio rate: {len(missing_arr_ids)}/6090 shipments ({len(missing_arr_ids)/6090*100:.1f}%)")

# Split shipments (2 rows)
ship_counts = shipments.groupby("transaction_id").size()
split_ids = set(ship_counts[ship_counts==2].index)
overlap4 = case_c_ids & split_ids
print(f"Split shipments: {len(overlap4)}/{n_case_c} ({len(overlap4)/n_case_c*100:.1f}%) | portfolio rate: {len(split_ids)}/6000 ({len(split_ids)/6000*100:.1f}%)")

# Zero-shipment transactions
all_txn_ids = set(txn.transaction_id)
zero_ship_ids = all_txn_ids - set(shipments.transaction_id.unique())
overlap5 = case_c_ids & zero_ship_ids
print(f"Zero-shipment transactions: {len(overlap5)}/{n_case_c} ({len(overlap5)/n_case_c*100:.1f}%) | portfolio rate: {len(zero_ship_ids)}/6000 ({len(zero_ship_ids)/6000*100:.1f}%)")
print("  (Note: Case C requires >=1 shipment to compute value/weight ratio, so 0% overlap here is EXPECTED/mechanical, not a finding.)")

# Partial-payment transactions
pay_counts = payments.groupby("transaction_id").size()
partial_ids = set(pay_counts[pay_counts>1].index)
overlap6 = case_c_ids & partial_ids
print(f"Partial-payment transactions: {len(overlap6)}/{n_case_c} ({len(overlap6)/n_case_c*100:.1f}%) | portfolio rate: {len(partial_ids)}/6000 ({len(partial_ids)/6000*100:.1f}%)")

# Shared-attribute / entity-resolution clusters (does Case C touch any flagged counterparty?)
flagged_cpty = set(pair_summary[pair_summary.classification.isin(["STRONG","MEDIUM"])]["cpty_a"]) | \
               set(pair_summary[pair_summary.classification.isin(["STRONG","MEDIUM"])]["cpty_b"])
case_c_cpty = set(txn[txn.transaction_id.isin(case_c_ids)]["counterparty_id"])
overlap7 = case_c_cpty & flagged_cpty
print(f"\nCase C counterparties also in a STRONG/MEDIUM entity-resolution cluster: {len(overlap7)}/{len(case_c_cpty)} distinct counterparties")
if overlap7:
    print(f"  Overlapping counterparties: {sorted(overlap7)}")
    overlap_txns = txn[(txn.transaction_id.isin(case_c_ids)) & (txn.counterparty_id.isin(overlap7))]
    print(f"  Corresponding Case C transactions: {len(overlap_txns)} of {n_case_c}")
else:
    print("  None - Case C does not touch any entity-resolution-flagged counterparty.")
