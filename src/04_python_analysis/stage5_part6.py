from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage5_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")
payments = pd.read_sql("SELECT * FROM payments", conn, parse_dates=["payment_date"])

print("### 6. THIRD-PARTY PAYER ANALYSIS ###\n")
tp_txn = txn[txn.is_tp_payer]
non_tp_txn = txn[~txn.is_tp_payer]
print(f"Third-party payer transactions: {len(tp_txn)} ({len(tp_txn)/len(txn)*100:.2f}% of portfolio)")

print("\n-- By segment --")
print(pd.crosstab(txn.segment, txn.is_tp_payer, normalize='index').mul(100).round(2))

print("\n-- By corridor --")
print(pd.crosstab(txn.corridor_group, txn.is_tp_payer, normalize='index').mul(100).round(2))

print("\n-- By product category (top 5 by tp rate) --")
prod_tp = txn.groupby("product_category")["is_tp_payer"].mean().sort_values(ascending=False)*100
print(prod_tp.head(5).round(2))

print("\n-- By counterparty (n>=10, top 10 by tp rate) --")
cpty_tp = txn.groupby("counterparty_id").agg(n_txn=("transaction_id","count"), tp_rate=("is_tp_payer","mean")).reset_index()
cpty_tp = cpty_tp[cpty_tp.n_txn>=10].sort_values("tp_rate", ascending=False)
print(cpty_tp.head(10).assign(tp_rate=lambda d: (d.tp_rate*100).round(2)).to_string(index=False))

print(f"\n-- Claim rate comparison --")
print(f"TP-payer txns claim rate: {tp_txn.has_claim.mean()*100:.2f}% (n={len(tp_txn)})")
print(f"Non-TP txns claim rate: {non_tp_txn.has_claim.mean()*100:.2f}% (n={len(non_tp_txn)})")

print(f"\n-- Alert rate comparison --")
print(f"TP-payer txns alert rate: {tp_txn.has_alert.mean()*100:.2f}% (n={len(tp_txn)})")
print(f"Non-TP txns alert rate: {non_tp_txn.has_alert.mean()*100:.2f}% (n={len(non_tp_txn)})")

print("\n-- Payment timing: days from transaction_date to final payment, TP vs non-TP --")
last_pay = payments.groupby("transaction_id")["payment_date"].max().reset_index(name="last_payment_date")
tt = txn[["transaction_id","transaction_date","is_tp_payer"]].merge(last_pay, on="transaction_id")
tt["days_to_final_payment"] = (tt["last_payment_date"] - tt["transaction_date"]).dt.days
print(tt.groupby("is_tp_payer")["days_to_final_payment"].describe()[["count","mean","50%","std"]].round(1))

print("\nNOTE: Third-party payment is a common, legitimate trade-finance practice (factoring, group treasury,")
print("assigned receivables). Elevated claim/alert rate for TP-payer transactions (if observed) is reported as a")
print("descriptive association only -- NOT treated as suspicious by itself, per instruction.")
