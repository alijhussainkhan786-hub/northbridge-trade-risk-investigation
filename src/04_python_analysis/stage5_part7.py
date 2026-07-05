from pathlib import Path
import pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
OUT = "/home/claude/build/stage5_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")

print("### 7. TIME AND BEHAVIOUR CHANGE ###\n")
txn["period"] = np.where(txn["transaction_date"] < pd.Timestamp("2023-07-01"), "early", "late")

# Customers with sufficient history in both periods (n>=8 each side)
cust_period = txn.groupby(["customer_id","period"]).agg(
    n_txn=("transaction_id","count"), median_value=("invoice_value","median"),
    alert_rate=("has_alert","mean"), claim_rate=("has_claim","mean")
).reset_index()
piv = cust_period.pivot(index="customer_id", columns="period", values=["n_txn","median_value","alert_rate","claim_rate"])
piv.columns = ['_'.join(c) for c in piv.columns]
eligible = piv[(piv.n_txn_early.fillna(0)>=8) & (piv.n_txn_late.fillna(0)>=8)].copy()
print(f"Customers with >=8 transactions in BOTH early (pre-2023-07) and late periods: {len(eligible)} of 180")

eligible["value_change_pct"] = ((eligible.median_value_late - eligible.median_value_early)/eligible.median_value_early*100).round(1)
eligible["alert_rate_change_pp"] = ((eligible.alert_rate_late - eligible.alert_rate_early)*100).round(1)
eligible["claim_rate_change_pp"] = ((eligible.claim_rate_late - eligible.claim_rate_early)*100).round(1)

print("\nTop 10 customers by alert_rate_change (largest increase):")
top_change = eligible.sort_values("alert_rate_change_pp", ascending=False).head(10)
print(top_change[["n_txn_early","n_txn_late","alert_rate_early","alert_rate_late","alert_rate_change_pp"]].round(3).to_string())

eligible.reset_index().to_csv(f"{OUT}/5g_customer_period_change.csv", index=False)

# Same for counterparties
cpty_period = txn.groupby(["counterparty_id","period"]).agg(
    n_txn=("transaction_id","count"), alert_rate=("has_alert","mean"), claim_rate=("has_claim","mean")
).reset_index()
pivc = cpty_period.pivot(index="counterparty_id", columns="period", values=["n_txn","alert_rate","claim_rate"])
pivc.columns = ['_'.join(c) for c in pivc.columns]
eligible_c = pivc[(pivc.n_txn_early.fillna(0)>=8) & (pivc.n_txn_late.fillna(0)>=8)].copy()
print(f"\nCounterparties with >=8 transactions in both periods: {len(eligible_c)} of 260")
eligible_c["alert_rate_change_pp"] = ((eligible_c.alert_rate_late - eligible_c.alert_rate_early)*100).round(1)
print("\nTop 10 counterparties by alert_rate_change:")
print(eligible_c.sort_values("alert_rate_change_pp", ascending=False).head(10)[["n_txn_early","n_txn_late","alert_rate_change_pp"]].to_string())
eligible_c.reset_index().to_csv(f"{OUT}/5g_counterparty_period_change.csv", index=False)

# Check the two flagged customers specifically (CUST00135/70) for period consistency (already shown stable 100% by year in Part 3)
print("\nNote: CUST00135 and CUST00070 (top alert-rate customers) show 100% alert rate in EVERY year 2022-2024 individually")
print("(see Part 3 output) -- i.e. NOT a recent behaviour change, but a consistent pattern across the full window.")
print("This is relevant: a sudden onset would suggest a triggering event; a consistent multi-year pattern instead suggests")
print("either a structural data/monitoring characteristic of this relationship, or a sustained pattern -- cannot distinguish from data alone.")

print("\nCaution: with only ~180 customers and ~260 counterparties, period-based subgroups shrink fast;")
print(f"only {len(eligible)}/180 customers and {len(eligible_c)}/260 counterparties meet the n>=8-per-period bar -- ")
print("changes for smaller entities are NOT reported here due to insufficient sample size, per instruction not to overstate.")
