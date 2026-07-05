from pathlib import Path
import sqlite3, pandas as pd
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage4_outputs"

def run(name, sql, show=15):
    df = pd.read_sql(sql, conn)
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"\n--- {name} ({len(df)} rows, showing top {show}) ---")
    print(df.head(show).to_string(index=False))
    return df

# ===========================================================================
# AREA 2: ALERT CONCENTRATION
# Grain: alerts joined to transactions at transaction grain (1 alert row = 1 alert,
# but a transaction can have >1 alert - pre-aggregate alert counts per transaction
# BEFORE joining to customer/counterparty to avoid fan-out on the transaction side).
# ===========================================================================

# Pre-aggregated: alert count per transaction (grain: transaction_id)
run("2a_alerts_per_customer", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts,
         SUM(CASE WHEN severity='high' THEN 1 ELSE 0 END) AS n_high_sev
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
txn_cust AS (
  SELECT t.transaction_id, t.customer_id FROM transactions t
),
cust_txn_counts AS (
  SELECT customer_id, COUNT(*) AS n_txn FROM transactions GROUP BY customer_id
)
SELECT tc.customer_id,
       ctc.n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       COALESCE(SUM(apt.n_high_sev),0) AS n_high_sev_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/ctc.n_txn,2) AS alerts_per_100_txn,
       ROUND(100.0*COALESCE(SUM(apt.n_high_sev),0)/ctc.n_txn,2) AS high_sev_per_100_txn
FROM txn_cust tc
JOIN cust_txn_counts ctc ON tc.customer_id = ctc.customer_id
LEFT JOIN alert_per_txn apt ON tc.transaction_id = apt.transaction_id
GROUP BY tc.customer_id
ORDER BY high_sev_per_100_txn DESC, n_txn DESC
""", show=15)

run("2b_alerts_per_counterparty", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts,
         SUM(CASE WHEN severity='high' THEN 1 ELSE 0 END) AS n_high_sev
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
cpty_txn_counts AS (
  SELECT counterparty_id, COUNT(*) AS n_txn FROM transactions GROUP BY counterparty_id
)
SELECT t.counterparty_id, ctc.n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       COALESCE(SUM(apt.n_high_sev),0) AS n_high_sev_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/ctc.n_txn,2) AS alerts_per_100_txn
FROM transactions t
JOIN cpty_txn_counts ctc ON t.counterparty_id = ctc.counterparty_id
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
GROUP BY t.counterparty_id
HAVING ctc.n_txn >= 10
ORDER BY alerts_per_100_txn DESC
""", show=15)

run("2c_alerts_by_corridor", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
)
SELECT d.corridor_group, COUNT(DISTINCT t.transaction_id) AS n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/COUNT(DISTINCT t.transaction_id),2) AS alerts_per_100_txn
FROM transactions t
JOIN destinations d ON t.destination_country_id = d.country_id
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
GROUP BY d.corridor_group ORDER BY alerts_per_100_txn DESC
""")

run("2d_alerts_by_product", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
)
SELECT p.product_category, COUNT(DISTINCT t.transaction_id) AS n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/COUNT(DISTINCT t.transaction_id),2) AS alerts_per_100_txn
FROM transactions t JOIN products p ON t.product_id = p.product_id
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
GROUP BY p.product_category ORDER BY alerts_per_100_txn DESC
""")

run("2e_alerts_by_intermediary", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts
  FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
ti_distinct AS (
  SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries
)
SELECT ti.intermediary_id, i.role_type, COUNT(DISTINCT ti.transaction_id) AS n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/COUNT(DISTINCT ti.transaction_id),2) AS alerts_per_100_txn
FROM ti_distinct ti
JOIN intermediaries i ON ti.intermediary_id = i.intermediary_id
LEFT JOIN alert_per_txn apt ON ti.transaction_id = apt.transaction_id
GROUP BY ti.intermediary_id
HAVING n_txn >= 10
ORDER BY alerts_per_100_txn DESC
""", show=15)
