from pathlib import Path
import sqlite3, pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.max_columns', None); pd.set_option('display.width', 200)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage7_outputs"

txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")
cc_net = pd.read_csv("/home/claude/build/stage6_outputs/6b_network_customer_counterparty.csv")
pair_summary = pd.read_csv("/home/claude/build/stage6_outputs/6a_entity_resolution_pairs.csv")
degree = pd.read_csv("/home/claude/build/stage6_outputs/6d_network_intermediary_degree.csv")
vw_stable = pd.read_csv("/home/claude/build/stage5_outputs/5e_vw_stable_candidates.csv")
payments = pd.read_sql("SELECT * FROM payments", conn)
dq = pd.read_sql("SELECT * FROM data_quality_issues", conn)

OVERALL_ALERT_RATE = txn["has_alert"].mean()

# ===========================================================================
# B. WEIGHTING FRAMEWORK -- CAPPED ADDITIVE POINTS, EXPLAINABLE PER-INDICATOR
# Category caps: Alert-based max 3 | Entity-resolution max 4 (IND02+IND03+IND04+IND05 combined,
# but IND03+IND04 alone capped at 3) | Financial-consistency max 3 (IND06+IND07+IND08, IND07 capped at 1)
# Total theoretical max = 3(alert) + 4(entity-res, incl exclusivity) + 3(financial) = 10
# ===========================================================================

# --- CUSTOMER-LEVEL SCORING ---
cust_alert = txn.groupby("customer_id").agg(n_txn=("transaction_id","count"), alert_rate=("has_alert","mean")).reset_index()
cust_alert = cust_alert[cust_alert.n_txn>=10].copy()

def ind01_score(row):
    n_alerts = int(round(row.alert_rate*row.n_txn))
    if row.n_txn>=15:
        p = stats.binomtest(n_alerts, int(row.n_txn), OVERALL_ALERT_RATE, alternative='greater').pvalue
        if p<0.01: return 3, p
        if p<0.05: return 1, p
    elif row.n_txn>=10:
        p = stats.binomtest(n_alerts, int(row.n_txn), OVERALL_ALERT_RATE, alternative='greater').pvalue
        if p<0.05: return 1, p
    return 0, np.nan

cust_alert[["ind01_score","ind01_pvalue"]] = cust_alert.apply(lambda r: pd.Series(ind01_score(r)), axis=1)

# IND02 exclusivity: customer's share of txn/value with their top entity-resolution-linked cluster (if any)
strong_pairs = pair_summary[pair_summary.classification=="STRONG"]
# Build cluster membership via union-find style grouping on STRONG pairs only
import networkx as nx
G = nx.Graph()
G.add_edges_from(strong_pairs[["cpty_a","cpty_b"]].values.tolist())
clusters = {i: c for i, comp in enumerate(nx.connected_components(G)) for c in [comp]}
cpty_to_cluster = {}
for cid, members in enumerate(nx.connected_components(G)):
    for m in members:
        cpty_to_cluster[m] = cid

def exclusivity_for_customer(cust_id):
    sub = cc_net[cc_net.customer_id==cust_id]
    if sub.empty: return 0, None, 0
    sub = sub.copy()
    sub["cluster"] = sub["counterparty_id"].map(cpty_to_cluster)
    if sub["cluster"].isna().all(): return 0, None, 0
    by_cluster = sub.groupby("cluster")["n_txn"].sum()
    top_cluster = by_cluster.idxmax()
    excl = by_cluster.max() / sub["n_txn"].sum()
    return excl, top_cluster, sub["n_txn"].sum()

results = []
for cust_id in cust_alert.customer_id:
    excl, cluster_id, total_txn = exclusivity_for_customer(cust_id)
    score = 3 if excl>=0.95 else (2 if excl>=0.80 else 0)
    results.append((cust_id, excl, cluster_id, score))
excl_df = pd.DataFrame(results, columns=["customer_id","exclusivity_share","linked_cluster_id","ind02_score"])
cust_alert = cust_alert.merge(excl_df, on="customer_id", how="left")

# Entity-resolution score inherited from linked cluster (IND03/IND04 combined, capped at 3)
def cluster_er_score(cluster_id):
    if cluster_id is None or pd.isna(cluster_id): return 0
    members = [m for m,c in cpty_to_cluster.items() if c==cluster_id]
    sub_pairs = pair_summary[(pair_summary.cpty_a.isin(members)) & (pair_summary.cpty_b.isin(members))]
    if (sub_pairs["evidence_buckets"].str.contains("bank")).any():
        # check if ANY pair also has non-bank-only evidence beyond bank (STRONG already implies this) but exclude email/phone-only duplicate signature
        has_extra = sub_pairs["evidence_buckets"].apply(lambda b: any(x in b for x in ["address","declared","name"]) and not any(x in b for x in ["email","phone"]))
        if has_extra.any():
            return 3  # IND03+IND04
        return 2  # IND03 only
    return 0

cust_alert["ind03_04_score"] = cust_alert.apply(
    lambda r: cluster_er_score(r["linked_cluster_id"]) if r["exclusivity_share"] >= 0.20 else 0, axis=1)

# Claim rate for context (not scored at customer level directly here, shown for evidence summary)
cust_claim = txn.groupby("customer_id")["has_claim"].mean().rename("claim_rate")
cust_alert = cust_alert.merge(cust_claim, on="customer_id")

cust_alert["total_score"] = cust_alert["ind01_score"] + cust_alert["ind02_score"] + cust_alert["ind03_04_score"]
cust_alert["priority_band"] = pd.cut(cust_alert["total_score"], bins=[-1,2,5,10], labels=["Low","Medium","High"])
cust_priority = cust_alert.sort_values("total_score", ascending=False)
cust_priority.to_csv(f"{OUT}/7c_priority_customer_level.csv", index=False)

print("### CUSTOMER-LEVEL PRIORITY TABLE (top 10) ###")
print(cust_priority.head(10).to_string(index=False))
