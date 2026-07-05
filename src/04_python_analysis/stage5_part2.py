from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None); pd.set_option('display.width', 160)
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage5_outputs"

customers = pd.read_sql("SELECT * FROM customers", conn)
counterparties = pd.read_sql("SELECT * FROM counterparties", conn)
intermediaries = pd.read_sql("SELECT * FROM intermediaries", conn)
products = pd.read_sql("SELECT * FROM products", conn)
destinations = pd.read_sql("SELECT * FROM destinations", conn)
transactions = pd.read_sql("SELECT * FROM transactions", conn, parse_dates=["transaction_date"])
shipments = pd.read_sql("SELECT * FROM shipments", conn)
payments = pd.read_sql("SELECT * FROM payments", conn)
ti = pd.read_sql("SELECT * FROM transaction_intermediaries", conn)
alerts = pd.read_sql("SELECT * FROM alerts", conn)
claims = pd.read_sql("SELECT * FROM claims", conn)

# Precompute per-transaction flags (grain: transaction_id, no fan-out)
alert_per_txn = alerts[alerts.subject_type=="transaction"].groupby("subject_id").size().rename("n_alerts")
claim_per_txn = claims.groupby("transaction_id").size().rename("n_claims")
tp_payer = payments[payments.paying_entity_type != "customer"]["transaction_id"].unique()
ship_agg = shipments.groupby("transaction_id").agg(total_weight=("declared_weight_kg","sum")).reset_index()

txn = transactions.merge(customers[["customer_id","segment"]], on="customer_id", how="left") \
                   .merge(destinations[["country_id","corridor_group"]], left_on="destination_country_id", right_on="country_id", how="left") \
                   .merge(products[["product_id","product_category"]], on="product_id", how="left") \
                   .merge(ship_agg, on="transaction_id", how="left")

txn["n_alerts"] = txn["transaction_id"].map(alert_per_txn).fillna(0)
txn["has_alert"] = txn["n_alerts"] > 0
txn["n_claims"] = txn["transaction_id"].map(claim_per_txn).fillna(0)
txn["has_claim"] = txn["n_claims"] > 0
txn["is_tp_payer"] = txn["transaction_id"].isin(tp_payer)
txn["value_per_kg"] = txn["invoice_value"] / txn["total_weight"]
cat_avg = txn.groupby("product_category")["value_per_kg"].transform("mean")
txn["vw_ratio_vs_cat"] = txn["value_per_kg"] / cat_avg
txn["is_vw_mismatch_5x"] = txn["vw_ratio_vs_cat"] > 5

def baseline_table(df, by):
    g = df.groupby(by)
    out = g.agg(
        n_txn=("transaction_id","count"),
        median_value=("invoice_value","median"),
        q1_value=("invoice_value", lambda x: x.quantile(0.25)),
        q3_value=("invoice_value", lambda x: x.quantile(0.75)),
        alert_rate=("has_alert","mean"),
        claim_rate=("has_claim","mean"),
        tp_payer_rate=("is_tp_payer","mean"),
        vw_mismatch_rate=("is_vw_mismatch_5x","mean"),
    ).reset_index()
    for c in ["alert_rate","claim_rate","tp_payer_rate","vw_mismatch_rate"]:
        out[c] = (out[c]*100).round(2)
    for c in ["median_value","q1_value","q3_value"]:
        out[c] = out[c].round(2)
    return out.sort_values("n_txn", ascending=False)

print("### BASELINE BY SEGMENT ###")
b1 = baseline_table(txn, "segment"); print(b1.to_string(index=False)); b1.to_csv(f"{OUT}/5b_baseline_segment.csv", index=False)

print("\n### BASELINE BY CORRIDOR ###")
b2 = baseline_table(txn, "corridor_group"); print(b2.to_string(index=False)); b2.to_csv(f"{OUT}/5b_baseline_corridor.csv", index=False)

print("\n### BASELINE BY PRODUCT CATEGORY ###")
b3 = baseline_table(txn, "product_category"); print(b3.to_string(index=False)); b3.to_csv(f"{OUT}/5b_baseline_product.csv", index=False)

print("\n### BASELINE BY YEAR-MONTH ###")
txn["year_month"] = txn["transaction_date"].dt.to_period("M").astype(str)
b4 = baseline_table(txn, "year_month").sort_values("year_month"); print(b4.to_string(index=False)); b4.to_csv(f"{OUT}/5b_baseline_yearmonth.csv", index=False)

print("\n### BASELINE BY COUNTERPARTY (n>=10) ###")
b5 = baseline_table(txn, "counterparty_id")
b5 = b5[b5["n_txn"]>=10].sort_values("alert_rate", ascending=False)
print(b5.head(15).to_string(index=False)); b5.to_csv(f"{OUT}/5b_baseline_counterparty.csv", index=False)

print("\n### BASELINE BY INTERMEDIARY (n>=10) -- via distinct txn-intermediary pairs, no fan-out ###")
ti_distinct = ti[["transaction_id","intermediary_id"]].drop_duplicates()
txn_ti = ti_distinct.merge(txn, on="transaction_id", how="left")
b6 = baseline_table(txn_ti, "intermediary_id")
b6 = b6[b6["n_txn"]>=10].sort_values("alert_rate", ascending=False)
print(b6.head(15).to_string(index=False)); b6.to_csv(f"{OUT}/5b_baseline_intermediary.csv", index=False)

txn.to_pickle("/home/claude/build/txn_enriched.pkl")  # cache for later parts
print("\nSaved enriched transaction frame for downstream parts.")
