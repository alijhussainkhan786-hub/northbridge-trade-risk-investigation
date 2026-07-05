from pathlib import Path
import sqlite3, pandas as pd, numpy as np
pd.set_option('display.max_columns', None)
conn = sqlite3.connect("/home/claude/build/northbridge.db")

def q(sql):
    return pd.read_sql(sql, conn)

print("##### 1-2. INVENTORY & ROW COUNTS #####")
tables = q("SELECT name FROM sqlite_master WHERE type='table'")['name'].tolist()
for t in sorted(tables):
    n = q(f"SELECT COUNT(*) c FROM {t}").iloc[0,0]
    print(f"{t}: {n}")

print("\n##### 3. GRAIN CONFIRMATION #####")
# transactions: 1 row per transaction_id
print("transactions grain check (dup transaction_id):", q("SELECT transaction_id, COUNT(*) c FROM transactions GROUP BY transaction_id HAVING c>1").shape[0])
# shipments: rows per transaction_id (expected 0/1/2)
ship_grain = q("SELECT transaction_id, COUNT(*) c FROM shipments GROUP BY transaction_id")
print("shipments per transaction distribution:\n", ship_grain['c'].value_counts())
n_txn = q("SELECT COUNT(*) c FROM transactions").iloc[0,0]
print("transactions with zero shipments:", n_txn - ship_grain.shape[0])
# payments: rows per transaction_id
pay_grain = q("SELECT transaction_id, COUNT(*) c FROM payments GROUP BY transaction_id")
print("payments per transaction distribution:\n", pay_grain['c'].value_counts())
print("transactions with zero payments:", n_txn - pay_grain.shape[0])
# transaction_intermediaries: rows per transaction
ti_grain = q("SELECT transaction_id, COUNT(*) c FROM transaction_intermediaries GROUP BY transaction_id")
print("intermediary roles per transaction - min/mean/max:", ti_grain['c'].min(), ti_grain['c'].mean(), ti_grain['c'].max())
print("transactions with zero intermediary rows:", n_txn - ti_grain.shape[0])
# claims: rows per transaction (expect 0 or 1 mostly)
claim_grain = q("SELECT transaction_id, COUNT(*) c FROM claims GROUP BY transaction_id")
print("claims per transaction distribution:\n", claim_grain['c'].value_counts())

print("\n##### 4. PRIMARY KEY UNIQUENESS #####")
pk_map = {"customers":"customer_id","counterparties":"counterparty_id","intermediaries":"intermediary_id",
    "products":"product_id","destinations":"country_id","transactions":"transaction_id",
    "shipments":"shipment_id","payments":"payment_id","transaction_intermediaries":"transaction_intermediary_id",
    "alerts":"alert_id","claims":"claim_id","entity_relationships":"relationship_id",
    "entity_attributes":"attribute_id"}
for t, pk in pk_map.items():
    total = q(f"SELECT COUNT(*) c FROM {t}").iloc[0,0]
    distinct = q(f"SELECT COUNT(DISTINCT {pk}) c FROM {t}").iloc[0,0]
    print(f"{t}.{pk}: total={total} distinct={distinct} {'OK' if total==distinct else 'FAIL - DUPLICATE PKs'}")

print("\n##### 5. FOREIGN KEY / POLYMORPHIC INTEGRITY #####")
fk_checks = [
    ("transactions.customer_id -> customers", "SELECT COUNT(*) c FROM transactions t LEFT JOIN customers c ON t.customer_id=c.customer_id WHERE c.customer_id IS NULL"),
    ("transactions.counterparty_id -> counterparties", "SELECT COUNT(*) c FROM transactions t LEFT JOIN counterparties c ON t.counterparty_id=c.counterparty_id WHERE c.counterparty_id IS NULL"),
    ("transactions.product_id -> products", "SELECT COUNT(*) c FROM transactions t LEFT JOIN products p ON t.product_id=p.product_id WHERE p.product_id IS NULL"),
    ("transactions.destination_country_id -> destinations", "SELECT COUNT(*) c FROM transactions t LEFT JOIN destinations d ON t.destination_country_id=d.country_id WHERE d.country_id IS NULL"),
    ("shipments.transaction_id -> transactions", "SELECT COUNT(*) c FROM shipments s LEFT JOIN transactions t ON s.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("shipments.origin_country_id -> destinations", "SELECT COUNT(*) c FROM shipments s LEFT JOIN destinations d ON s.origin_country_id=d.country_id WHERE d.country_id IS NULL"),
    ("shipments.destination_country_id -> destinations", "SELECT COUNT(*) c FROM shipments s LEFT JOIN destinations d ON s.destination_country_id=d.country_id WHERE d.country_id IS NULL"),
    ("payments.transaction_id -> transactions", "SELECT COUNT(*) c FROM payments p LEFT JOIN transactions t ON p.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("transaction_intermediaries.transaction_id -> transactions", "SELECT COUNT(*) c FROM transaction_intermediaries ti LEFT JOIN transactions t ON ti.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("transaction_intermediaries.intermediary_id -> intermediaries", "SELECT COUNT(*) c FROM transaction_intermediaries ti LEFT JOIN intermediaries i ON ti.intermediary_id=i.intermediary_id WHERE i.intermediary_id IS NULL"),
    ("claims.transaction_id -> transactions", "SELECT COUNT(*) c FROM claims c LEFT JOIN transactions t ON c.transaction_id=t.transaction_id WHERE t.transaction_id IS NULL"),
    ("claims.customer_id -> customers", "SELECT COUNT(*) c FROM claims c LEFT JOIN customers cu ON c.customer_id=cu.customer_id WHERE cu.customer_id IS NULL"),
]
for label, sql in fk_checks:
    orphans = q(sql).iloc[0,0]
    print(f"{label}: orphans={orphans} {'OK' if orphans==0 else 'FAIL'}")

# Polymorphic checks
print("\n-- Polymorphic reference checks --")
alerts = q("SELECT * FROM alerts")
print("alerts.subject_type distinct values:", alerts['subject_type'].unique())
txn_ids = set(q("SELECT transaction_id FROM transactions")['transaction_id'])
bad_alert = alerts[(alerts.subject_type=='transaction') & (~alerts.subject_id.isin(txn_ids))]
print("alerts with unresolved transaction subject_id:", len(bad_alert))

ea = q("SELECT * FROM entity_attributes")
er = q("SELECT * FROM entity_relationships")
cust_ids = set(q("SELECT customer_id FROM customers")['customer_id'])
cpty_ids = set(q("SELECT counterparty_id FROM counterparties")['counterparty_id'])
intm_ids = set(q("SELECT intermediary_id FROM intermediaries")['intermediary_id'])
pool = {"customer": cust_ids, "counterparty": cpty_ids, "intermediary": intm_ids}

def poly_bad(df, idcol, typecol):
    mask = ~df.apply(lambda r: r[idcol] in pool.get(r[typecol], set()), axis=1)
    return df[mask]

bad_ea = poly_bad(ea, "entity_id", "entity_type")
print("entity_attributes unresolved polymorphic refs:", len(bad_ea))
bad_er1 = poly_bad(er, "entity_id_1", "entity_type_1")
bad_er2 = poly_bad(er.rename(columns={"entity_id_2":"entity_id","entity_type_2":"entity_type"}), "entity_id","entity_type")
print("entity_relationships side-1 unresolved:", len(bad_er1), "| side-2 unresolved:", len(bad_er2))

print("\n##### 6. MISSING-VALUE ANALYSIS #####")
for t in sorted(tables):
    df = q(f"SELECT * FROM {t}")
    if df.empty:
        print(f"{t}: 0 rows (schema only)")
        continue
    miss = df.isnull().sum()
    miss = miss[miss > 0]
    if len(miss):
        print(f"\n{t} ({len(df)} rows):")
        for col, cnt in miss.items():
            print(f"  {col}: {cnt} missing ({cnt/len(df)*100:.1f}%)")
    else:
        print(f"{t}: no nulls detected by pandas (note: check for empty-string / sentinel nulls separately)")

print("\n-- Check for empty-string pseudo-nulls (not caught by isnull) --")
for t in sorted(tables):
    df = q(f"SELECT * FROM {t}")
    if df.empty: continue
    for col in df.select_dtypes(include='object').columns:
        n_empty = (df[col].astype(str).str.strip() == '').sum()
        if n_empty > 0:
            print(f"{t}.{col}: {n_empty} empty-string values")

print("\n##### 7. DUPLICATE / NEAR-DUPLICATE SCREENING #####")
# Exact duplicate rows (ignoring PK) in counterparties
cpty = q("SELECT * FROM counterparties")
cols_no_pk = [c for c in cpty.columns if c != 'counterparty_id']
exact_dupes = cpty[cpty.duplicated(subset=cols_no_pk, keep=False)]
print(f"counterparties exact-duplicate rows (all fields identical except PK): {len(exact_dupes)}")
print(exact_dupes[['counterparty_id','legal_name','registration_number','country']].sort_values('legal_name').to_string(index=False) if len(exact_dupes) else "none")

# Near-duplicate by legal_name normalization
def norm_name(n):
    return (n.replace("Ltd","").replace("Limited","").replace("LLC","").replace("L.L.C.","")
             .replace(".","").replace(",","").strip().lower())
cpty['name_norm'] = cpty['legal_name'].apply(norm_name)
near_dupes = cpty[cpty.duplicated(subset=['name_norm'], keep=False)].sort_values('name_norm')
print(f"\ncounterparties near-duplicate by normalized legal_name: {len(near_dupes)} rows across {near_dupes['name_norm'].nunique()} name groups")
print(near_dupes[['counterparty_id','legal_name','country']].to_string(index=False) if len(near_dupes) else "none")

# Shared address / bank_account_hash clusters (entity-resolution relevant)
addr_counts = cpty.groupby('registered_address')['counterparty_id'].apply(list)
addr_clusters = addr_counts[addr_counts.apply(len) > 1]
print(f"\ncounterparty registered_address values shared by >1 counterparty_id: {len(addr_clusters)} address groups")
for addr, ids in addr_clusters.items():
    print(f"  '{addr}': {ids}")

bank_counts = cpty.groupby('bank_account_hash')['counterparty_id'].apply(list)
bank_clusters = bank_counts[bank_counts.apply(len) > 1]
print(f"\ncounterparty bank_account_hash values shared by >1 counterparty_id: {len(bank_clusters)} groups")
for bh, ids in bank_clusters.items():
    print(f"  '{bh}': {ids}")

print("\n##### 8. DATE COVERAGE & DATE-LOGIC CHECKS #####")
for t, datecol in [("transactions","transaction_date"),("shipments","departure_date"),
                    ("shipments","arrival_date"),("payments","payment_date"),
                    ("alerts","alert_date"),("claims","claim_date"),("customers","onboarding_date")]:
    r = q(f"SELECT MIN({datecol}) mn, MAX({datecol}) mx, COUNT(*) - COUNT({datecol}) nulls FROM {t}")
    print(f"{t}.{datecol}: {r.iloc[0]['mn']} to {r.iloc[0]['mx']} | nulls={r.iloc[0]['nulls']}")

print("\n-- Logic violations --")
v1 = q("SELECT s.shipment_id, s.transaction_id, s.departure_date, s.arrival_date FROM shipments s WHERE s.arrival_date IS NOT NULL AND s.arrival_date < s.departure_date")
print(f"shipments with arrival_date < departure_date: {len(v1)}")

v2 = q("""SELECT s.shipment_id, s.transaction_id, t.transaction_date, s.departure_date
          FROM shipments s JOIN transactions t ON s.transaction_id=t.transaction_id
          WHERE s.departure_date < t.transaction_date""")
print(f"shipments departing before transaction_date: {len(v2)}")

v3 = q("""SELECT p.payment_id, p.transaction_id, t.transaction_date, p.payment_date
          FROM payments p JOIN transactions t ON p.transaction_id=t.transaction_id
          WHERE p.payment_date < t.transaction_date""")
print(f"payments predating transaction_date: {len(v3)}")

v4 = q("""SELECT a.alert_id, a.subject_id, t.transaction_date, a.alert_date
          FROM alerts a JOIN transactions t ON a.subject_id=t.transaction_id
          WHERE a.subject_type='transaction' AND a.alert_date < t.transaction_date""")
print(f"alerts predating their subject transaction_date: {len(v4)}")

v5 = q("""SELECT c.claim_id, c.transaction_id, t.transaction_date, c.claim_date
          FROM claims c JOIN transactions t ON c.transaction_id=t.transaction_id
          WHERE c.claim_date < t.transaction_date""")
print(f"claims predating transaction_date: {len(v5)}")

print("\n##### 9. SHIPMENT/PAYMENT/TRANSACTION RECONCILIATION #####")
pay_sum = q("""SELECT p.transaction_id, SUM(p.amount) total_paid
               FROM payments p GROUP BY p.transaction_id""")
txn = q("SELECT transaction_id, invoice_value FROM transactions")
merged = txn.merge(pay_sum, on="transaction_id", how="left")
merged["diff"] = (merged["total_paid"] - merged["invoice_value"]).round(2)
mismatch = merged[merged["diff"].abs() > 0.5]
print(f"Transactions where SUM(payments) != invoice_value (tolerance 0.50): {len(mismatch)} of {len(merged)}")
print(mismatch["diff"].describe())

ship_val_sum = q("SELECT transaction_id, SUM(declared_value) total_ship_value FROM shipments GROUP BY transaction_id")
merged2 = txn.merge(ship_val_sum, on="transaction_id", how="left")
merged2["diff"] = (merged2["total_ship_value"] - merged2["invoice_value"]).round(2)
mismatch2 = merged2[merged2["diff"].abs() > 0.5]
print(f"\nTransactions where SUM(shipment declared_value) != invoice_value: {len(mismatch2)} of {len(merged2)}")
n_no_ship = merged2["total_ship_value"].isnull().sum()
print(f"Transactions with no shipment (contributing to mismatch/NaN): {n_no_ship}")

print("\n##### 10. ALERT & CLAIM LINKAGE CHECKS #####")
n_alerts = q("SELECT COUNT(*) c FROM alerts").iloc[0,0]
n_alert_txn_linked = q("SELECT COUNT(*) c FROM alerts WHERE subject_type='transaction'").iloc[0,0]
print(f"Alerts linked to a transaction subject: {n_alert_txn_linked}/{n_alerts} ({n_alert_txn_linked/n_alerts*100:.1f}%)")
print("NOTE: subject_type currently only takes value 'transaction' in this dataset -- no customer- or")
print("      counterparty-level alerts present, despite schema allowing it. Coverage gap for Q7 (segment-level conversion).")

n_claims = q("SELECT COUNT(*) c FROM claims").iloc[0,0]
claims_df = q("SELECT * FROM claims")
alerts_df = q("SELECT * FROM alerts WHERE subject_type='transaction'")
alerted_txns = set(alerts_df["subject_id"])
claims_df["has_prior_alert"] = claims_df["transaction_id"].isin(alerted_txns)
n_linked = claims_df["has_prior_alert"].sum()
print(f"\nClaims where the underlying transaction has >=1 alert on record: {n_linked}/{n_claims} ({n_linked/n_claims*100:.1f}%)")
print("Base rate for comparison -- overall transaction alert rate: {:.1f}%".format(n_alert_txn_linked/6000*100))
print("(Descriptive relationship only at this audit stage -- no causal or investigative claim made.)")

print("\n##### 11. MANY-TO-MANY JOIN INFLATION RISK TESTS #####")
# Naive join transactions -> transaction_intermediaries -> payments would inflate row count
naive = q("""SELECT COUNT(*) c FROM transactions t
             JOIN transaction_intermediaries ti ON t.transaction_id = ti.transaction_id
             JOIN payments p ON t.transaction_id = p.transaction_id""")
print(f"Naive 3-way join (transactions x transaction_intermediaries x payments) row count: {naive.iloc[0,0]} vs base transactions: 6000")
print("-> Confirms fan-out risk: any invoice_value or amount aggregation on this naive join would be overstated by ~{:.1f}x".format(naive.iloc[0,0]/6000))

# Intermediary degree check (informational, not a conclusion)
deg = q("""SELECT intermediary_id, COUNT(DISTINCT transaction_id) n_txn
           FROM transaction_intermediaries GROUP BY intermediary_id ORDER BY n_txn DESC LIMIT 5""")
print("\nTop 5 intermediaries by distinct transaction count (network degree) -- descriptive only:")
print(deg.to_string(index=False))
top_share = deg.iloc[0]['n_txn'] / q("SELECT COUNT(DISTINCT transaction_id) c FROM transaction_intermediaries").iloc[0,0]
print(f"Top intermediary's share of all transaction-intermediary-linked transactions: {top_share*100:.1f}%")
print("(Concentration alone does not indicate risk -- role_type and peer context required before any interpretation; deferred to later stages.)")

print("\n##### 12. ENTITY-RESOLUTION DATA-QUALITY RISKS #####")
print(f"- {len(near_dupes)} counterparty rows fall into {near_dupes['name_norm'].nunique()} normalized-name groups (legal-suffix variation only)")
print(f"- {len(addr_clusters)} registered_address values are shared by >1 counterparty_id")
print(f"- {len(bank_clusters)} bank_account_hash values are shared by >1 counterparty_id")
print("- Address strings are drawn from a small combinatorial pool (limited unit numbers/street-type words),")
print("  so shared-address matches include BOTH deliberate-looking clusters AND likely coincidental format collisions.")
print("  Address/bank overlap alone cannot distinguish the two without further attribute cross-checks (Stage 6 task).")
missing_reg = q("SELECT COUNT(*) c FROM counterparties WHERE registration_number IS NULL").iloc[0,0]
non_gb = q("SELECT COUNT(*) c FROM counterparties WHERE country != 'GB'").iloc[0,0]
print(f"- {missing_reg} of {non_gb} non-GB counterparties have no registration_number ({missing_reg/non_gb*100:.1f}%) -- resolution by registration number not reliably available for this subset (intelligence gap, not evidence of anything).")
