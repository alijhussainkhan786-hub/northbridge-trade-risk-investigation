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
# AREA 4: PAYMENT / INVOICE CONSISTENCY
# Grain: transaction. Payments pre-aggregated to transaction grain BEFORE any
# further join, to prevent fan-out.
# ===========================================================================
run("4a_payment_count_distribution", """
SELECT n_payments, COUNT(*) AS n_txn
FROM (SELECT transaction_id, COUNT(*) AS n_payments FROM payments GROUP BY transaction_id)
GROUP BY n_payments ORDER BY n_payments
""")

run("4b_payment_vs_invoice_reconciliation", """
WITH pay_agg AS (
  SELECT transaction_id, SUM(amount) AS total_paid, COUNT(*) AS n_pay FROM payments GROUP BY transaction_id
)
SELECT
  COUNT(*) AS n_txn,
  SUM(CASE WHEN ABS(pa.total_paid - t.invoice_value) <= 0.5 THEN 1 ELSE 0 END) AS n_reconciled,
  SUM(CASE WHEN ABS(pa.total_paid - t.invoice_value) > 0.5 THEN 1 ELSE 0 END) AS n_mismatch
FROM transactions t JOIN pay_agg pa ON t.transaction_id = pa.transaction_id
""")

run("4c_third_party_payer_candidates", """
SELECT p.transaction_id, t.customer_id, t.counterparty_id, p.paying_entity_id, p.paying_entity_type,
       p.settlement_route, p.amount, t.invoice_value
FROM payments p JOIN transactions t ON p.transaction_id = t.transaction_id
WHERE p.paying_entity_type != 'customer'
ORDER BY p.transaction_id
""", show=10)

run("4c_summary_third_party_payer", """
SELECT COUNT(DISTINCT transaction_id) AS n_txn_with_third_party_payer,
       (SELECT COUNT(*) FROM transactions) AS n_txn_total,
       ROUND(100.0*COUNT(DISTINCT transaction_id)/(SELECT COUNT(*) FROM transactions),2) AS pct_of_portfolio
FROM payments WHERE paying_entity_type != 'customer'
""")

run("4d_payment_date_issues", """
SELECT COUNT(*) AS n_payments_predating_txn
FROM payments p JOIN transactions t ON p.transaction_id = t.transaction_id
WHERE p.payment_date < t.transaction_date
""")
