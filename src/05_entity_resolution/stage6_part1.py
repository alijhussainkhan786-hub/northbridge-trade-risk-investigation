from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 180)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage6_outputs"
import os; os.makedirs(OUT, exist_ok=True)

cpty = pd.read_sql("SELECT * FROM counterparties", conn)
rel = pd.read_sql("SELECT * FROM entity_relationships", conn)
ea = pd.read_sql("SELECT * FROM entity_attributes", conn)

def norm_name(n):
    return (n.replace("Ltd","").replace("Limited","").replace("LLC","").replace("L.L.C.","")
             .replace(".","").replace(",","").strip().lower())
cpty["name_norm"] = cpty["legal_name"].apply(norm_name)

# ---------------------------------------------------------------------------
# 1. ENTITY-RESOLUTION EVIDENCE: pairwise candidates across ALL attributes
# ---------------------------------------------------------------------------
def pairwise_matches(df, key, id_col="counterparty_id"):
    m = df.merge(df, on=key, suffixes=("_a","_b"))
    m = m[m[f"{id_col}_a"] < m[f"{id_col}_b"]]
    return m[[f"{id_col}_a", f"{id_col}_b", key]].drop_duplicates()

bank_matches = pairwise_matches(cpty, "bank_account_hash")
bank_matches["evidence_type"] = "shared_bank_account"

addr_matches = pairwise_matches(cpty, "registered_address")
addr_matches["evidence_type"] = "shared_address"

name_matches = pairwise_matches(cpty, "name_norm")
name_matches["evidence_type"] = "near_duplicate_name"

email_matches = pairwise_matches(cpty, "contact_email")
email_matches["evidence_type"] = "shared_email"
print("Shared contact_email matches:", len(email_matches), "(expect 0 - emails generated per-row-index, unique by construction)")

phone_matches = pairwise_matches(cpty, "contact_phone")
phone_matches["evidence_type"] = "shared_phone"
print("Shared contact_phone matches:", len(phone_matches), "(random format, near-zero expected by chance)")

# Declared relationships (counterparty-counterparty only, for comparability)
rel_cc = rel[(rel.entity_type_1=="counterparty") & (rel.entity_type_2=="counterparty")].copy()
rel_cc = rel_cc.rename(columns={"entity_id_1":"counterparty_id_a","entity_id_2":"counterparty_id_b"})
rel_cc["counterparty_id_a2"] = rel_cc[["counterparty_id_a","counterparty_id_b"]].min(axis=1)
rel_cc["counterparty_id_b2"] = rel_cc[["counterparty_id_a","counterparty_id_b"]].max(axis=1)
rel_matches = rel_cc[["counterparty_id_a2","counterparty_id_b2","relationship_type","source","confidence"]].rename(
    columns={"counterparty_id_a2":"counterparty_id_a","counterparty_id_b2":"counterparty_id_b"})
rel_matches["evidence_type"] = "declared_relationship_" + rel_matches["relationship_type"]
print("Declared counterparty-counterparty relationships:", len(rel_matches))

# Combine all pairwise evidence into one long table
all_ev = pd.concat([
    bank_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
    addr_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
    name_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
    email_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
    phone_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
    rel_matches.rename(columns={"counterparty_id_a":"cpty_a","counterparty_id_b":"cpty_b"})[["cpty_a","cpty_b","evidence_type"]],
], ignore_index=True)

# Aggregate evidence per pair: count distinct independent evidence types
pair_summary = all_ev.groupby(["cpty_a","cpty_b"])["evidence_type"].apply(lambda x: sorted(set(x))).reset_index()
pair_summary["n_independent_evidence_types"] = pair_summary["evidence_type"].apply(
    lambda types: len(set(t.split("_")[0]+"_"+t.split("_")[1] if t.startswith("declared") else t for t in types)))
# Simplify: bucket evidence into categories: bank, address, name, declared
def bucket_types(types):
    buckets = set()
    for t in types:
        if t == "shared_bank_account": buckets.add("bank")
        elif t == "shared_address": buckets.add("address")
        elif t == "near_duplicate_name": buckets.add("name")
        elif t == "shared_email": buckets.add("email")
        elif t == "shared_phone": buckets.add("phone")
        elif t.startswith("declared_relationship"): buckets.add("declared")
    return buckets

pair_summary["evidence_buckets"] = pair_summary["evidence_type"].apply(bucket_types)
pair_summary["n_evidence_buckets"] = pair_summary["evidence_buckets"].apply(len)

def classify(buckets):
    if "bank" in buckets and len(buckets) >= 2:
        return "STRONG"
    if "bank" in buckets or "declared" in buckets:
        return "MEDIUM"
    if "address" in buckets or "name" in buckets:
        return "WEAK"
    return "NOT_ENOUGH_EVIDENCE"

pair_summary["classification"] = pair_summary["evidence_buckets"].apply(classify)
pair_summary["evidence_buckets"] = pair_summary["evidence_buckets"].apply(lambda s: sorted(s))
pair_summary = pair_summary.sort_values(["classification","cpty_a"])
pair_summary.to_csv(f"{OUT}/6a_entity_resolution_pairs.csv", index=False)

print(f"\nTotal counterparty pairs with >=1 evidence type: {len(pair_summary)}")
print(pair_summary["classification"].value_counts())
print("\n-- STRONG classification pairs --")
print(pair_summary[pair_summary.classification=="STRONG"].to_string(index=False))
print("\n-- MEDIUM classification pairs (sample) --")
print(pair_summary[pair_summary.classification=="MEDIUM"].head(10).to_string(index=False))
