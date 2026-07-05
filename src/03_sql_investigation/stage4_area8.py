from pathlib import Path
import sqlite3, pandas as pd
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage4_outputs"

def run(name, sql, show=25):
    df = pd.read_sql(sql, conn)
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"\n--- {name} ({len(df)} rows) ---")
    print(df.head(show).to_string(index=False))
    return df

# ===========================================================================
# AREA 8: INVESTIGATION QUEUE CANDIDATES
# These are SQL-derived CANDIDATE lists with reason codes only.
# Not risk scores. Not findings. "Appears on queue" = review first, not guilty.
# ===========================================================================

# Q1: High alert-rate customers/counterparties with minimum sample size (n_txn>=15)
# to avoid small-n noise, and requiring a visible gap above the rest of the distribution.
run("8a_queue_high_alert_customers", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts,
         SUM(CASE WHEN severity='high' THEN 1 ELSE 0 END) AS n_high_sev
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
cust_txn AS (SELECT customer_id, COUNT(*) AS n_txn FROM transactions GROUP BY customer_id)
SELECT t.customer_id, ct.n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/ct.n_txn,2) AS alert_rate_per_100,
       'HIGH_ALERT_RATE_MIN_N15' AS reason_code
FROM transactions t
JOIN cust_txn ct ON t.customer_id = ct.customer_id
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
GROUP BY t.customer_id
HAVING ct.n_txn >= 15 AND alert_rate_per_100 >= 25
ORDER BY alert_rate_per_100 DESC
""")

run("8b_queue_high_alert_counterparties", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
cpty_txn AS (SELECT counterparty_id, COUNT(*) AS n_txn FROM transactions GROUP BY counterparty_id)
SELECT t.counterparty_id, ct.n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/ct.n_txn,2) AS alert_rate_per_100,
       'HIGH_ALERT_RATE_MIN_N15' AS reason_code
FROM transactions t
JOIN cpty_txn ct ON t.counterparty_id = ct.counterparty_id
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
GROUP BY t.counterparty_id
HAVING ct.n_txn >= 15 AND alert_rate_per_100 >= 30
ORDER BY alert_rate_per_100 DESC
""")

# Q2: Value/weight mismatch candidates (already built in 5c, re-tag with reason code, threshold=5x)
run("8c_queue_value_weight_mismatch", """
WITH ship_agg AS (SELECT transaction_id, SUM(declared_weight_kg) AS total_weight FROM shipments GROUP BY transaction_id),
ratio AS (
  SELECT t.transaction_id, t.customer_id, t.counterparty_id, p.product_category, t.invoice_value, sa.total_weight,
         t.invoice_value / NULLIF(sa.total_weight,0) AS value_per_kg
  FROM transactions t JOIN ship_agg sa ON t.transaction_id = sa.transaction_id
  JOIN products p ON t.product_id = p.product_id
),
cat_avg AS (SELECT product_category, AVG(value_per_kg) AS avg_ratio FROM ratio GROUP BY product_category)
SELECT r.transaction_id, r.customer_id, r.counterparty_id, r.product_category,
       ROUND(r.value_per_kg/ca.avg_ratio,2) AS ratio_vs_category_avg,
       'VALUE_WEIGHT_MISMATCH_5X' AS reason_code
FROM ratio r JOIN cat_avg ca ON r.product_category = ca.product_category
WHERE r.value_per_kg/ca.avg_ratio > 5
ORDER BY ratio_vs_category_avg DESC
""")

# Q3: Third-party payer candidates
run("8d_queue_third_party_payer", """
SELECT p.transaction_id, t.customer_id, t.counterparty_id, p.paying_entity_id, p.paying_entity_type,
       'THIRD_PARTY_PAYER' AS reason_code
FROM payments p JOIN transactions t ON p.transaction_id = t.transaction_id
WHERE p.paying_entity_type != 'customer'
""")

# Q4: Claim-with-prior-alert candidates
run("8e_queue_claim_with_prior_alert", """
SELECT cl.claim_id, cl.transaction_id, cl.customer_id, cl.claim_amount,
       (SELECT COUNT(*) FROM alerts a WHERE a.subject_type='transaction' AND a.subject_id=cl.transaction_id) AS n_prior_alerts,
       'CLAIM_WITH_PRIOR_ALERT' AS reason_code
FROM claims cl
WHERE EXISTS (SELECT 1 FROM alerts a WHERE a.subject_type='transaction' AND a.subject_id=cl.transaction_id)
""")

# Q5: Shared-attribute candidates via SQL join only (exact match, no fuzzy logic)
run("8f_queue_shared_address", """
SELECT c1.counterparty_id AS cpty_a, c2.counterparty_id AS cpty_b, c1.registered_address,
       'SHARED_ADDRESS_EXACT_MATCH' AS reason_code
FROM counterparties c1 JOIN counterparties c2
  ON c1.registered_address = c2.registered_address AND c1.counterparty_id < c2.counterparty_id
ORDER BY c1.registered_address
""")

run("8g_queue_shared_bank_account", """
SELECT c1.counterparty_id AS cpty_a, c2.counterparty_id AS cpty_b, c1.bank_account_hash,
       'SHARED_BANK_ACCOUNT_EXACT_MATCH' AS reason_code
FROM counterparties c1 JOIN counterparties c2
  ON c1.bank_account_hash = c2.bank_account_hash AND c1.counterparty_id < c2.counterparty_id
ORDER BY c1.bank_account_hash
""")

print("\n=== QUEUE SUMMARY COUNTS ===")
import glob, os
for f in sorted(glob.glob(f"{OUT}/8*.csv")):
    n = sum(1 for _ in open(f)) - 1
    print(os.path.basename(f), ":", n, "candidates")
