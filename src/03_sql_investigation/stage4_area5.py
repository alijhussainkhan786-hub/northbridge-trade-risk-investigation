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
# AREA 5: SHIPMENT / INVOICE CONSISTENCY
# Grain: transaction. Shipments pre-aggregated to transaction grain before joining.
# ===========================================================================
run("5a_shipment_count_distribution", """
SELECT n_shipments, COUNT(*) AS n_txn FROM (
  SELECT transaction_id, COUNT(*) AS n_shipments FROM shipments GROUP BY transaction_id
) GROUP BY n_shipments
UNION ALL
SELECT 0, (SELECT COUNT(*) FROM transactions) - (SELECT COUNT(DISTINCT transaction_id) FROM shipments)
ORDER BY n_shipments
""")

run("5b_shipment_value_vs_invoice", """
WITH ship_agg AS (
  SELECT transaction_id, SUM(declared_value) AS total_ship_value, SUM(declared_weight_kg) AS total_weight
  FROM shipments GROUP BY transaction_id
)
SELECT COUNT(*) AS n_txn_with_shipment,
       SUM(CASE WHEN ABS(sa.total_ship_value - t.invoice_value) <= 0.5 THEN 1 ELSE 0 END) AS n_reconciled,
       SUM(CASE WHEN ABS(sa.total_ship_value - t.invoice_value) > 0.5 THEN 1 ELSE 0 END) AS n_mismatch
FROM transactions t JOIN ship_agg sa ON t.transaction_id = sa.transaction_id
""")

run("5c_value_per_kg_outliers", """
-- Value-per-declared-kg ratio, benchmarked by product category (not a global threshold)
WITH ship_agg AS (
  SELECT transaction_id, SUM(declared_weight_kg) AS total_weight FROM shipments GROUP BY transaction_id
),
ratio AS (
  SELECT t.transaction_id, t.product_id, p.product_category, t.invoice_value, sa.total_weight,
         t.invoice_value / NULLIF(sa.total_weight,0) AS value_per_kg
  FROM transactions t JOIN ship_agg sa ON t.transaction_id = sa.transaction_id
  JOIN products p ON t.product_id = p.product_id
),
cat_stats AS (
  SELECT product_category, AVG(value_per_kg) AS avg_ratio,
         (SELECT AVG((value_per_kg - sub.avg_r)*(value_per_kg - sub.avg_r))
          FROM ratio r2, (SELECT AVG(value_per_kg) avg_r FROM ratio r3 WHERE r3.product_category = ratio.product_category) sub
          WHERE r2.product_category = ratio.product_category) AS dummy
  FROM ratio GROUP BY product_category
)
SELECT r.transaction_id, r.product_category, ROUND(r.value_per_kg,2) AS value_per_kg,
       ROUND(cs.avg_ratio,2) AS category_avg_value_per_kg,
       ROUND(r.value_per_kg / cs.avg_ratio,2) AS ratio_vs_category_avg
FROM ratio r JOIN cat_stats cs ON r.product_category = cs.product_category
WHERE r.value_per_kg / cs.avg_ratio > 5
ORDER BY ratio_vs_category_avg DESC
""", show=30)

run("5d_split_and_zero_shipment_counts", """
SELECT
 (SELECT COUNT(*) FROM (SELECT transaction_id FROM shipments GROUP BY transaction_id HAVING COUNT(*)=2)) AS n_split,
 (SELECT COUNT(*) FROM transactions) - (SELECT COUNT(DISTINCT transaction_id) FROM shipments) AS n_zero
""")

run("5e_shipment_date_issues", """
SELECT COUNT(*) AS n_arrival_before_departure FROM shipments WHERE arrival_date IS NOT NULL AND arrival_date < departure_date
""")
