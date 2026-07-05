from pathlib import Path
import sqlite3, pandas as pd
conn = sqlite3.connect("/home/claude/build/northbridge.db")
OUT = "/home/claude/build/stage4_outputs"
import os
os.makedirs(OUT, exist_ok=True)

def run(name, sql):
    df = pd.read_sql(sql, conn)
    df.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"\n--- {name} ({len(df)} rows) ---")
    print(df.to_string(index=False))
    return df

# ===========================================================================
# AREA 1: PORTFOLIO BASELINE
# Grain: transactions.transaction_id. No joins needed for base counts.
# ===========================================================================
run("1a_txn_by_year_month", """
SELECT strftime('%Y', transaction_date) AS yr, strftime('%m', transaction_date) AS mo,
       COUNT(*) AS n_txn, ROUND(SUM(invoice_value),2) AS total_value
FROM transactions GROUP BY yr, mo ORDER BY yr, mo
""")

run("1b_invoice_value_distribution", """
SELECT
  ROUND(MIN(invoice_value),2) AS min_val, ROUND(MAX(invoice_value),2) AS max_val,
  ROUND(AVG(invoice_value),2) AS mean_val,
  (SELECT invoice_value FROM transactions ORDER BY invoice_value LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM transactions)) AS median_approx,
  ROUND(SUM(invoice_value),2) AS total_value, COUNT(*) AS n_txn
FROM transactions
""")

run("1c_customers_by_segment", """
SELECT segment, COUNT(*) AS n_customers
FROM customers GROUP BY segment ORDER BY n_customers DESC
""")

run("1d_txn_by_corridor", """
SELECT d.corridor_group, COUNT(*) AS n_txn, ROUND(SUM(t.invoice_value),2) AS total_value
FROM transactions t JOIN destinations d ON t.destination_country_id = d.country_id
GROUP BY d.corridor_group ORDER BY n_txn DESC
""")

run("1e_txn_by_product", """
SELECT p.product_category, COUNT(*) AS n_txn, ROUND(SUM(t.invoice_value),2) AS total_value
FROM transactions t JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_category ORDER BY n_txn DESC
""")

run("1f_base_rates", """
SELECT
  (SELECT COUNT(*) FROM transactions) AS n_txn,
  (SELECT COUNT(*) FROM alerts WHERE subject_type='transaction') AS n_alerts,
  ROUND(100.0*(SELECT COUNT(*) FROM alerts WHERE subject_type='transaction')/(SELECT COUNT(*) FROM transactions),2) AS alert_rate_pct,
  (SELECT COUNT(*) FROM claims) AS n_claims,
  ROUND(100.0*(SELECT COUNT(*) FROM claims)/(SELECT COUNT(*) FROM transactions),2) AS claim_rate_pct
""")
