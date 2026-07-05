from pathlib import Path
import sqlite3, pandas as pd
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage4_outputs"

def run(name, sql, show=20):
    df = pd.read_sql(sql, conn)
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"\n--- {name} ({len(df)} rows) ---")
    print(df.head(show).to_string(index=False))
    return df

# ===========================================================================
# AREA 6: INTERMEDIARY CONCENTRATION
# Grain: intermediary_id. Bridge table de-duplicated to distinct (transaction_id,
# intermediary_id) pairs before aggregation to avoid role/sequence fan-out.
# ===========================================================================
run("6a_txn_share_by_intermediary", """
WITH ti_distinct AS (SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries)
SELECT ti.intermediary_id, i.role_type, i.country,
       COUNT(DISTINCT ti.transaction_id) AS n_txn,
       ROUND(100.0*COUNT(DISTINCT ti.transaction_id)/(SELECT COUNT(DISTINCT transaction_id) FROM ti_distinct),2) AS pct_share
FROM ti_distinct ti JOIN intermediaries i ON ti.intermediary_id = i.intermediary_id
GROUP BY ti.intermediary_id ORDER BY n_txn DESC
""", show=10)

run("6b_customer_counterparty_diversity_per_intermediary", """
WITH ti_distinct AS (SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries)
SELECT ti.intermediary_id, i.role_type,
       COUNT(DISTINCT t.customer_id) AS n_distinct_customers,
       COUNT(DISTINCT t.counterparty_id) AS n_distinct_counterparties,
       COUNT(DISTINCT ti.transaction_id) AS n_txn
FROM ti_distinct ti
JOIN transactions t ON ti.transaction_id = t.transaction_id
JOIN intermediaries i ON ti.intermediary_id = i.intermediary_id
GROUP BY ti.intermediary_id ORDER BY n_txn DESC
""", show=10)

run("6c_hub_hhi_concentration_index", """
-- Herfindahl-Hirschman Index style concentration measure across intermediaries (descriptive only)
WITH ti_distinct AS (SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries),
shares AS (
  SELECT intermediary_id, COUNT(DISTINCT transaction_id)*1.0/(SELECT COUNT(DISTINCT transaction_id) FROM ti_distinct) AS share
  FROM ti_distinct GROUP BY intermediary_id
)
SELECT ROUND(SUM(share*share),4) AS hhi_index, COUNT(*) AS n_intermediaries
FROM shares
""")

# ===========================================================================
# AREA 7: COUNTERPARTY CONCENTRATION
# Grain: counterparty_id.
# ===========================================================================
run("7a_top_counterparties_by_value", """
SELECT counterparty_id, COUNT(*) AS n_txn, ROUND(SUM(invoice_value),2) AS total_value,
       ROUND(100.0*SUM(invoice_value)/(SELECT SUM(invoice_value) FROM transactions),2) AS pct_of_portfolio_value
FROM transactions GROUP BY counterparty_id ORDER BY total_value DESC
""", show=15)

run("7b_counterparty_alert_and_claim_rate", """
WITH alert_per_txn AS (
  SELECT subject_id AS transaction_id, COUNT(*) AS n_alerts FROM alerts WHERE subject_type='transaction' GROUP BY subject_id
),
claim_per_txn AS (SELECT transaction_id, COUNT(*) AS n_claims FROM claims GROUP BY transaction_id)
SELECT t.counterparty_id, COUNT(*) AS n_txn,
       COALESCE(SUM(apt.n_alerts),0) AS n_alerts,
       ROUND(100.0*COALESCE(SUM(apt.n_alerts),0)/COUNT(*),2) AS alert_rate_per_100,
       COALESCE(SUM(cpt.n_claims),0) AS n_claims,
       ROUND(100.0*COALESCE(SUM(cpt.n_claims),0)/COUNT(*),2) AS claim_rate_per_100
FROM transactions t
LEFT JOIN alert_per_txn apt ON t.transaction_id = apt.transaction_id
LEFT JOIN claim_per_txn cpt ON t.transaction_id = cpt.transaction_id
GROUP BY t.counterparty_id
HAVING n_txn >= 10
ORDER BY alert_rate_per_100 DESC
""", show=15)
