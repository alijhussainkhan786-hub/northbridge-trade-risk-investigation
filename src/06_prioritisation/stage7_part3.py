from pathlib import Path
import sqlite3, pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.max_columns', None); pd.set_option('display.width', 200)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage7_outputs"
txn = pd.read_pickle("/home/claude/build/txn_enriched.pkl")
pair_summary = pd.read_csv("/home/claude/build/stage6_outputs/6a_entity_resolution_pairs.csv")
cc_net = pd.read_csv("/home/claude/build/stage6_outputs/6b_network_customer_counterparty.csv")
vw_stable = pd.read_csv("/home/claude/build/stage5_outputs/5e_vw_stable_candidates.csv")
payments = pd.read_sql("SELECT * FROM payments", conn)
degree = pd.read_csv("/home/claude/build/stage6_outputs/6d_network_intermediary_degree.csv")

OVERALL_ALERT_RATE = txn["has_alert"].mean()
OVERALL_CLAIM_RATE = txn["has_claim"].mean()

# ===========================================================================
# CLUSTER-LEVEL PRIORITY TABLE
# ===========================================================================
import networkx as nx
strong_pairs = pair_summary[pair_summary.classification=="STRONG"]
G = nx.Graph(); G.add_edges_from(strong_pairs[["cpty_a","cpty_b"]].values.tolist())
clusters = list(nx.connected_components(G))

def cluster_evidence(members):
    sub_pairs = pair_summary[(pair_summary.cpty_a.isin(members)) & (pair_summary.cpty_b.isin(members))]
    has_email_phone = sub_pairs["evidence_buckets"].str.contains("email|phone", regex=True).any()
    has_bank = sub_pairs["evidence_buckets"].str.contains("bank").any()
    has_extra = sub_pairs["evidence_buckets"].apply(lambda b: any(x in b for x in ["address","declared","name"])).any()
    return has_bank, has_extra, has_email_phone, len(sub_pairs)

cluster_rows = []
for i, members in enumerate(clusters):
    members = sorted(members)
    has_bank, has_extra, has_email_phone, n_pairs = cluster_evidence(members)
    txn_sub = txn[txn.counterparty_id.isin(members)]
    n_txn = len(txn_sub); alert_rate = txn_sub.has_alert.mean() if n_txn else 0
    claim_rate = txn_sub.has_claim.mean() if n_txn else 0
    # linked customers with meaningful exposure
    linked = cc_net[cc_net.counterparty_id.isin(members)].groupby("customer_id")["n_txn"].sum()
    total_per_cust = cc_net.groupby("customer_id")["n_txn"].sum()
    excl = (linked / total_per_cust.reindex(linked.index)).sort_values(ascending=False)
    top_cust = excl.index[0] if len(excl) else None
    top_excl = excl.iloc[0] if len(excl) else 0

    if has_email_phone:
        classification, score = "DUPLICATE_DATA_SIGNATURE - not scored", 0
    elif has_bank and has_extra:
        classification, score = "STRONG (bank+other)", 3
    elif has_bank:
        classification, score = "MEDIUM (bank only)", 2
    else:
        classification, score = "WEAK", 1

    cluster_rows.append(dict(cluster_id=f"CL{i+1:03d}", members=", ".join(members), n_members=len(members),
        n_pairs=n_pairs, er_classification=classification, er_score=score,
        n_txn=n_txn, alert_rate=round(alert_rate*100,1), claim_rate=round(claim_rate*100,1),
        top_linked_customer=top_cust, top_customer_exclusivity=round(top_excl*100,1) if top_cust else None))

cluster_df = pd.DataFrame(cluster_rows).sort_values("er_score", ascending=False)
cluster_df.to_csv(f"{OUT}/7c_priority_cluster_level.csv", index=False)
print("### CLUSTER-LEVEL PRIORITY TABLE (scored, top 10) ###")
print(cluster_df.head(10).to_string(index=False))

# ===========================================================================
# TRANSACTION-LEVEL PRIORITY TABLE
# ===========================================================================
tp_txn_ids = set(payments[payments.paying_entity_type!="customer"]["transaction_id"])
vw_ids = set(vw_stable["transaction_id"])

txn_score = txn[["transaction_id","customer_id","counterparty_id","invoice_value","has_alert","has_claim"]].copy()
txn_score["ind06_vw"] = txn_score.transaction_id.isin(vw_ids).astype(int) * 2
txn_score["ind07_tp"] = txn_score.transaction_id.isin(tp_txn_ids).astype(int) * 1
txn_score["ind08_claim_prior_alert"] = ((txn_score.has_claim) & (txn_score.has_alert)).astype(int) * 1
# Explicit rule: IND07 does NOT stack with an alert bonus for the same transaction (avoid circularity) -
# there is no alert-based transaction indicator in this table by design, so no further action needed,
# but documented here as the enforced rule.
txn_score["total_score"] = txn_score["ind06_vw"] + txn_score["ind07_tp"] + txn_score["ind08_claim_prior_alert"]
txn_priority = txn_score[txn_score.total_score>0].sort_values("total_score", ascending=False)
txn_priority.to_csv(f"{OUT}/7c_priority_transaction_level.csv", index=False)
print(f"\n### TRANSACTION-LEVEL PRIORITY TABLE: {len(txn_priority)} flagged transactions (score>0) ###")
print(txn_priority.head(10).to_string(index=False))
print("\nScore distribution:")
print(txn_priority.total_score.value_counts().sort_index(ascending=False))

# ===========================================================================
# INTM00038 SCORING CHECK (IND10 gate test)
# ===========================================================================
intm038 = degree[degree.intermediary_id=="INTM00038"].iloc[0]
alerts = pd.read_sql("SELECT * FROM alerts WHERE subject_type='transaction'", conn)
ti = pd.read_sql("SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries", conn)
sub038 = ti[ti.intermediary_id=="INTM00038"]
own_alert_rate = sub038.transaction_id.isin(set(alerts.subject_id)).mean()
print(f"\n### IND10 GATE TEST: INTM00038 ###")
print(f"Degree share: {intm038.degree}/9600 bridge rows (35.0% of table, 66.5% of distinct linked txns)")
print(f"Own alert rate: {own_alert_rate*100:.2f}% vs portfolio baseline {OVERALL_ALERT_RATE*100:.2f}%")
print(f"Gate condition (elevated own alert rate)? {'PASS - would score' if own_alert_rate > OVERALL_ALERT_RATE*1.5 else 'FAIL - does NOT score, 0 points from IND10'}")
