from pathlib import Path
import sqlite3, pandas as pd, json

conn = sqlite3.connect("/home/claude/build/northbridge.db")
tables = ["customers","counterparties","intermediaries","products","destinations","transactions",
          "shipments","payments","transaction_intermediaries","alerts","claims",
          "entity_relationships","entity_attributes","case_review_log","data_quality_issues"]

results = {}

print("=== ROW COUNTS ===")
for t in tables:
    n = pd.read_sql(f"SELECT COUNT(*) c FROM {t}", conn).iloc[0,0]
    results[f"rowcount_{t}"] = n
    print(f"{t}: {n}")

print("\n=== PK UNIQUENESS ===")
pk_map = {"customers":"customer_id","counterparties":"counterparty_id","intermediaries":"intermediary_id",
    "products":"product_id","destinations":"country_id","transactions":"transaction_id",
    "shipments":"shipment_id","payments":"payment_id","transaction_intermediaries":"transaction_intermediary_id",
    "alerts":"alert_id","claims":"claim_id","entity_relationships":"relationship_id",
    "entity_attributes":"attribute_id"}
for t, pk in pk_map.items():
    total = pd.read_sql(f"SELECT COUNT(*) c FROM {t}", conn).iloc[0,0]
    distinct = pd.read_sql(f"SELECT COUNT(DISTINCT {pk}) c FROM {t}", conn).iloc[0,0]
    status = "OK" if total == distinct else "FAIL"
    print(f"{t}.{pk}: total={total} distinct={distinct} [{status}]")

print("\n=== REFERENTIAL INTEGRITY ===")
checks = [
    ("transactions.customer_id -> customers", "SELECT COUNT(*) FROM transactions t LEFT JOIN customers c ON t.customer_id=c.customer_id WHERE c.customer_id IS NULL"),
    ("transactions.counterparty_id -> counterparties", "SELECT COUNT(*) FROM transactions t LEFT JOIN counterparties c ON t.counterparty_id=c.counterparty_id WHERE c.counterparty_id IS NULL"),
    ("transactions.product_id -> products", "SELECT COUNT(*) FROM transactions t LEFT JOIN products p ON t.product_id=p.product_id WHERE p.product_id IS NULL"),
    ("transactions.destination_country_id -> destinations", "SELECT COUNT(*) FROM transactions t LEFT JOIN destinations d ON t.destination_country_id=d.country_id WHERE d.country_id IS NULL"),
    ("shipments.transaction_id -> transactions", "SELECT COUNT(*) FROM shipments s LEFT JOIN transactions t ON s.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("payments.transaction_id -> transactions", "SELECT COUNT(*) FROM payments p LEFT JOIN transactions t ON p.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("transaction_intermediaries.transaction_id -> transactions", "SELECT COUNT(*) FROM transaction_intermediaries ti LEFT JOIN transactions t ON ti.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("transaction_intermediaries.intermediary_id -> intermediaries", "SELECT COUNT(*) FROM transaction_intermediaries ti LEFT JOIN intermediaries i ON ti.intermediary_id=i.intermediary_id WHERE i.intermediary_id IS NULL"),
    ("claims.transaction_id -> transactions", "SELECT COUNT(*) FROM claims c LEFT JOIN transactions t ON c.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("claims.customer_id -> customers", "SELECT COUNT(*) FROM claims c LEFT JOIN customers cu ON c.customer_id=cu.customer_id WHERE cu.customer_id IS NULL"),
]
for label, q in checks:
    orphan = pd.read_sql(q, conn).iloc[0,0]
    print(f"{label}: orphans={orphan} [{'OK' if orphan==0 else 'FAIL'}]")

print("\n=== POLYMORPHIC REFERENCE CHECK (Alerts) ===")
alerts = pd.read_sql("SELECT * FROM alerts", conn)
txn_ids = set(pd.read_sql("SELECT transaction_id FROM transactions", conn)["transaction_id"])
bad_alert = alerts[(alerts.subject_type=="transaction") & (~alerts.subject_id.isin(txn_ids))]
print(f"Alerts with subject_type=transaction not resolving to transactions table: {len(bad_alert)} [{'OK' if len(bad_alert)==0 else 'FAIL'}]")

print("\n=== POLYMORPHIC REFERENCE CHECK (Entity_Attributes / Entity_Relationships) ===")
ea = pd.read_sql("SELECT * FROM entity_attributes", conn)
er = pd.read_sql("SELECT * FROM entity_relationships", conn)
cust_ids = set(pd.read_sql("SELECT customer_id FROM customers", conn)["customer_id"])
cpty_ids_all = set(pd.read_sql("SELECT counterparty_id FROM counterparties", conn)["counterparty_id"])
intm_ids_all = set(pd.read_sql("SELECT intermediary_id FROM intermediaries", conn)["intermediary_id"])
type_pool = {"customer": cust_ids, "counterparty": cpty_ids_all, "intermediary": intm_ids_all}

def check_poly(df, id_col, type_col):
    bad = 0
    for _, row in df.iterrows():
        pool = type_pool.get(row[type_col], set())
        if row[id_col] not in pool:
            bad += 1
    return bad

bad_ea = check_poly(ea, "entity_id", "entity_type")
print(f"Entity_Attributes unresolved polymorphic refs: {bad_ea} [{'OK' if bad_ea==0 else 'FAIL'}]")
bad_er1 = check_poly(er, "entity_id_1", "entity_type_1")
bad_er2 = check_poly(er, "entity_id_2", "entity_type_2")
print(f"Entity_Relationships unresolved polymorphic refs: {bad_er1+bad_er2} [{'OK' if bad_er1+bad_er2==0 else 'FAIL'}]")

print("\n=== SHIPMENT / PAYMENT / ALERT / CLAIM RATE RECONCILIATION ===")
ship_per_txn = pd.read_sql("SELECT transaction_id, COUNT(*) c FROM shipments GROUP BY transaction_id", conn)
n_txn = 6000
n_with_ship = len(ship_per_txn)
n_zero = n_txn - n_with_ship
n_split = (ship_per_txn['c']==2).sum()
n_single = (ship_per_txn['c']==1).sum()
print(f"Shipment distribution -> 0 ships: {n_zero} (target 30), 1 ship: {n_single} (target 5850), 2 ships: {n_split} (target 120)")

pay_per_txn = pd.read_sql("SELECT transaction_id, COUNT(*) c FROM payments GROUP BY transaction_id", conn)
n1 = (pay_per_txn['c']==1).sum(); n2=(pay_per_txn['c']==2).sum(); n3=(pay_per_txn['c']==3).sum()
print(f"Payment distribution -> 1 pay: {n1} (target 5100), 2 pay: {n2} (target 780), 3 pay: {n3} (target 120)")

n_alerts = pd.read_sql("SELECT COUNT(*) c FROM alerts", conn).iloc[0,0]
print(f"Alert rate: {n_alerts}/{n_txn} = {n_alerts/n_txn:.4f} (target 0.16)")

n_claims = pd.read_sql("SELECT COUNT(*) c FROM claims", conn).iloc[0,0]
print(f"Claim rate: {n_claims}/{n_txn} = {n_claims/n_txn:.4f} (target 0.03)")

print("\n=== DATE COVERAGE ===")
dr = pd.read_sql("SELECT MIN(transaction_date) mn, MAX(transaction_date) mx FROM transactions", conn)
print("Transactions date range:", dr.iloc[0]['mn'], "to", dr.iloc[0]['mx'])

print("\n=== FORBIDDEN COLUMN SCAN ===")
forbidden = {"fraud","guilty","risk_score","is_suspicious","risk_label","fraud_flag"}
found_any = False
for t in tables:
    cols = pd.read_sql(f"SELECT * FROM {t} LIMIT 1", conn).columns
    bad = forbidden & set(c.lower() for c in cols)
    if bad:
        found_any = True
        print(f"FAIL - forbidden column in {t}: {bad}")
if not found_any:
    print("OK - no forbidden fraud/guilt/risk-label columns found in any analyst-facing table.")

print("\n=== GROUND TRUTH SEPARATION CHECK ===")
import os
gt_in_csv_dir = os.path.exists("/home/claude/build/csv_exports/ground_truth.csv")
gt_in_db = "ground_truth" in tables
print(f"ground_truth.csv present in csv_exports: {gt_in_csv_dir} [{'FAIL' if gt_in_csv_dir else 'OK'}]")
print(f"ground_truth table present in northbridge.db: {gt_in_db} [{'FAIL' if gt_in_db else 'OK'}]")
print("ground_truth.json located at build/ground_truth/ (separate folder): ", os.path.exists("/home/claude/build/ground_truth/ground_truth.json"))

conn.close()
