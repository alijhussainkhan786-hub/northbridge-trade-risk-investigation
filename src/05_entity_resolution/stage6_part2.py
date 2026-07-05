from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 180)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage6_outputs"

transactions = pd.read_sql("SELECT * FROM transactions", conn)
ti = pd.read_sql("SELECT * FROM transaction_intermediaries", conn)
intermediaries = pd.read_sql("SELECT * FROM intermediaries", conn)
alerts = pd.read_sql("SELECT * FROM alerts WHERE subject_type='transaction'", conn)
claims = pd.read_sql("SELECT * FROM claims", conn)
cpty = pd.read_sql("SELECT * FROM counterparties", conn)
pair_summary = pd.read_csv(f"{OUT}/6a_entity_resolution_pairs.csv")

alert_per_txn = alerts.groupby("subject_id").size().rename("n_alerts")
claim_per_txn = claims.groupby("transaction_id").size().rename("n_claims")
transactions["n_alerts"] = transactions["transaction_id"].map(alert_per_txn).fillna(0)
transactions["n_claims"] = transactions["transaction_id"].map(claim_per_txn).fillna(0)

# ===========================================================================
# NETWORK 1: Customer-Counterparty transaction network (weighted edges)
# ===========================================================================
cc_net = transactions.groupby(["customer_id","counterparty_id"]).agg(
    n_txn=("transaction_id","count"), total_value=("invoice_value","sum"),
    n_alerts=("n_alerts","sum"), n_claims=("n_claims","sum")
).reset_index()
cc_net.to_csv(f"{OUT}/6b_network_customer_counterparty.csv", index=False)
print(f"NETWORK 1 (customer-counterparty): {len(cc_net)} edges, {cc_net.customer_id.nunique()} customers, {cc_net.counterparty_id.nunique()} counterparties")

# ===========================================================================
# NETWORK 2: Counterparty-counterparty shared-attribute network (from Part 1)
# already saved as 6a_entity_resolution_pairs.csv
# ===========================================================================
print(f"NETWORK 2 (counterparty-counterparty shared-attribute): {len(pair_summary)} edges (27 STRONG, 24 MEDIUM, 13 WEAK)")

# ===========================================================================
# NETWORK 3: Intermediary network (via shared transactions - which intermediaries co-occur on same txn)
# ===========================================================================
ti_distinct = ti[["transaction_id","intermediary_id"]].drop_duplicates()
multi = ti_distinct.groupby("transaction_id")["intermediary_id"].apply(list)
multi = multi[multi.apply(len) > 1]
from itertools import combinations
co_occur = {}
for ids in multi:
    for a, b in combinations(sorted(set(ids)), 2):
        co_occur[(a,b)] = co_occur.get((a,b), 0) + 1
intm_net = pd.DataFrame([(a,b,c) for (a,b),c in co_occur.items()], columns=["intm_a","intm_b","n_shared_txn"])
intm_net = intm_net.sort_values("n_shared_txn", ascending=False)
intm_net.to_csv(f"{OUT}/6c_network_intermediary_cooccurrence.csv", index=False)
print(f"\nNETWORK 3 (intermediary co-occurrence): {len(intm_net)} edges")
print(intm_net.head(10).to_string(index=False))

# ===========================================================================
# NETWORK 4: Transaction-Intermediary bipartite network summary (degree distribution)
# ===========================================================================
degree = ti_distinct.groupby("intermediary_id")["transaction_id"].nunique().reset_index(name="degree")
degree = degree.merge(intermediaries[["intermediary_id","role_type"]], on="intermediary_id")
degree = degree.sort_values("degree", ascending=False)
degree.to_csv(f"{OUT}/6d_network_intermediary_degree.csv", index=False)
print(f"\nNETWORK 4 (transaction-intermediary degree distribution):")
print(degree.head(10).to_string(index=False))
print(f"Degree distribution stats: mean={degree.degree.mean():.1f}, median={degree.degree.median():.1f}, max={degree.degree.max()}")

# ===========================================================================
# SPECIFIC TEST 1: Do CUST00135/CUST00070 connect to the high-alert counterparty clusters?
# ===========================================================================
print("\n### SPECIFIC TEST 1: CUST00135/070 <-> counterparty clusters ###")
cluster_A = {"CPTY00002","CPTY00045","CPTY00148","CPTY00156"}
cluster_B = {"CPTY00073","CPTY00141","CPTY00218","CPTY00220"}
for cust, cluster, label in [("CUST00135", cluster_A, "Cluster A"), ("CUST00070", cluster_B, "Cluster B")]:
    edges = cc_net[(cc_net.customer_id==cust) & (cc_net.counterparty_id.isin(cluster))]
    other_edges = cc_net[(cc_net.customer_id==cust) & (~cc_net.counterparty_id.isin(cluster))]
    print(f"\n{cust} -> {label} {sorted(cluster)}:")
    print(edges.to_string(index=False))
    print(f"  Txns with {label}: {edges.n_txn.sum()} of {edges.n_txn.sum()+other_edges.n_txn.sum()} total ({edges.n_txn.sum()/(edges.n_txn.sum()+other_edges.n_txn.sum())*100:.1f}%)")
    print(f"  Value with {label}: {edges.total_value.sum():,.0f} of {edges.total_value.sum()+other_edges.total_value.sum():,.0f} total ({edges.total_value.sum()/(edges.total_value.sum()+other_edges.total_value.sum())*100:.1f}%)")
    print(f"  DIRECT LINK CONFIRMED: {cust} transacts directly with all {len(cluster)} members of {label}" if len(edges)==len(cluster) else f"  Direct link with {len(edges)} of {len(cluster)} members")

# Cross-check: does CUST00135 ALSO connect to cluster B, or CUST00070 to cluster A? (tests whether clusters are customer-specific or portfolio-wide)
print("\nCross-check (customer specificity of clusters):")
for cust in ["CUST00135","CUST00070"]:
    for label, cluster in [("Cluster A", cluster_A), ("Cluster B", cluster_B)]:
        n = cc_net[(cc_net.customer_id==cust) & (cc_net.counterparty_id.isin(cluster))].n_txn.sum()
        print(f"  {cust} x {label}: {n} txns")

print("\n### SPECIFIC TEST 2: Are AC003/AC004 genuine clusters or weak overlaps? ###")
print("(See STRONG classification in 6a_entity_resolution_pairs.csv above)")
print("Cluster A (CPTY00002/45/148/156): all pairs STRONG (address+bank, 2 pairs also +declared_relationship)")
print("Cluster B (CPTY00073/141/218/220): all pairs STRONG (address+bank, 1 pair also +declared_relationship)")
print("Neither cluster matches on email/phone (unlike the 15 'noise duplicate' pairs which match on ALL 4-5 attributes)")
print("-> This is CONSISTENT WITH genuinely distinct entity records sharing deliberate core identifiers (bank+address),")
print("   NOT simple duplicate data entry (which would also match incidental fields like email/phone).")
print("   This increases confidence these are real candidate clusters worth Stage 7 prioritisation, ")
print("   but does NOT prove common control or wrongdoing -- alternative explanation: shared corporate services")
print("   provider (registered agent, accountant) could independently produce a shared registered bank intermediary")
print("   account for invoicing purposes in some legitimate structures. This alternative is NOT ruled out by network data alone.")
