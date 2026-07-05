from pathlib import Path
import pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
OUT = "/home/claude/build/stage5_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")

print("### 3. ALERT CONCENTRATION ROBUSTNESS ###\n")

# Overall base rate for reference
overall_alert_rate = txn["has_alert"].mean()
print(f"Portfolio overall alert rate: {overall_alert_rate*100:.2f}%\n")

# Top customers by alert rate, n>=15
cust_alert = txn.groupby("customer_id").agg(n_txn=("transaction_id","count"), alert_rate=("has_alert","mean")).reset_index()
cust_alert = cust_alert[cust_alert.n_txn>=15].sort_values("alert_rate", ascending=False)
print("Top 10 customers by alert rate (n>=15):")
print(cust_alert.head(10).assign(alert_rate=lambda d: (d.alert_rate*100).round(2)).to_string(index=False))

top2 = cust_alert.head(2)["customer_id"].tolist()
rest = cust_alert.iloc[2:]
print(f"\nGap check: rank1/2 = {cust_alert.iloc[0].alert_rate*100:.1f}%/{cust_alert.iloc[1].alert_rate*100:.1f}% vs rank3 = {cust_alert.iloc[2].alert_rate*100:.1f}% -> statistical step, not smooth cluster (gap = {(cust_alert.iloc[1].alert_rate-cust_alert.iloc[2].alert_rate)*100:.1f}pp)")

# Binomial test: is each top customer's alert rate significantly above overall base rate, given their n?
print("\n-- Binomial test vs overall base rate (16.0%) for top-5 customers --")
for _, row in cust_alert.head(5).iterrows():
    n_alerts = int(round(row.alert_rate * row.n_txn))
    res = stats.binomtest(n_alerts, int(row.n_txn), overall_alert_rate, alternative='greater')
    print(f"{row.customer_id}: n={int(row.n_txn)}, alerts={n_alerts}, rate={row.alert_rate*100:.1f}%, p-value(vs base rate)={res.pvalue:.6f}")

# Control for product mix: does top customer's product mix differ from portfolio, and does that alone explain elevated alert rate?
print("\n-- Product-mix control for top-2 customers --")
for cid in top2:
    sub = txn[txn.customer_id==cid]
    mix = sub["product_category"].value_counts(normalize=True).round(2)
    print(f"{cid} product mix (top 3): {mix.head(3).to_dict()}")
    # expected alert rate if this customer only had "portfolio-average" alert behavior per product category
    cat_rates = txn.groupby("product_category")["has_alert"].mean()
    expected_rate = sub["product_category"].map(cat_rates).mean()
    observed_rate = sub["has_alert"].mean()
    print(f"  Observed alert rate: {observed_rate*100:.1f}% | Expected if only product-mix driven: {expected_rate*100:.1f}%")

# Control for corridor mix similarly
print("\n-- Corridor-mix control for top-2 customers --")
for cid in top2:
    sub = txn[txn.customer_id==cid]
    cor_rates = txn.groupby("corridor_group")["has_alert"].mean()
    expected_rate = sub["corridor_group"].map(cor_rates).mean()
    observed_rate = sub["has_alert"].mean()
    print(f"{cid}: Observed {observed_rate*100:.1f}% | Expected if only corridor-mix driven: {expected_rate*100:.1f}%")

# Control for segment
print("\n-- Segment control for top-2 customers --")
for cid in top2:
    sub = txn[txn.customer_id==cid]
    seg = sub["segment"].iloc[0]
    seg_rate = txn[txn.segment==seg]["has_alert"].mean()
    print(f"{cid} (segment={seg}): Observed {sub['has_alert'].mean()*100:.1f}% | Segment baseline: {seg_rate*100:.1f}%")

# Time period control - is the elevated rate concentrated in one period or spread across the window?
print("\n-- Time distribution of alerts for top-2 customers --")
for cid in top2:
    sub = txn[txn.customer_id==cid].copy()
    sub["year"] = sub["transaction_date"].dt.year
    print(f"{cid} alert rate by year:")
    print(sub.groupby("year")["has_alert"].agg(["count","mean"]).rename(columns={"mean":"alert_rate"}).assign(alert_rate=lambda d: (d.alert_rate*100).round(1)).to_string())

# Counterparty-side robustness (same approach, condensed)
print("\n### Counterparty-side robustness (top cluster CPTY00002/148/156/218/220/141/073) ###")
cluster_cptys = ["CPTY00002","CPTY00148","CPTY00156","CPTY00218","CPTY00220","CPTY00141","CPTY00073"]
cpty_alert = txn.groupby("counterparty_id").agg(n_txn=("transaction_id","count"), alert_rate=("has_alert","mean")).reset_index()
cpty_alert_ranked = cpty_alert[cpty_alert.n_txn>=15].sort_values("alert_rate", ascending=False).reset_index(drop=True)
print("Rank position of cluster members among n>=15 counterparties:")
for c in cluster_cptys:
    row = cpty_alert_ranked[cpty_alert_ranked.counterparty_id==c]
    if len(row):
        rank = row.index[0]+1
        print(f"  {c}: rank {rank} of {len(cpty_alert_ranked)}, alert_rate={row.iloc[0].alert_rate*100:.1f}%, n_txn={int(row.iloc[0].n_txn)}")

cpty_binom = []
for c in cluster_cptys:
    row = cpty_alert[cpty_alert.counterparty_id==c].iloc[0]
    n_alerts = int(round(row.alert_rate*row.n_txn))
    res = stats.binomtest(n_alerts, int(row.n_txn), overall_alert_rate, alternative='greater')
    cpty_binom.append((c, int(row.n_txn), n_alerts, row.alert_rate*100, res.pvalue))
print("\nBinomial test vs base rate for cluster counterparties:")
for c,n,a,r,p in cpty_binom:
    print(f"  {c}: n={n}, alerts={a}, rate={r:.1f}%, p={p:.6f}")
