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
# AREA 3: CLAIM / ALERT RELATIONSHIP - DESCRIPTIVE ONLY, NO CAUSAL CLAIM
# Grain: transaction. A transaction either has >=1 alert or not; either has a
# claim or not. Cross-tab at transaction grain (pre-aggregated, no fan-out).
# ===========================================================================
run("3a_claim_rate_by_alert_presence", """
WITH txn_alert_flag AS (
  SELECT t.transaction_id,
         CASE WHEN EXISTS (SELECT 1 FROM alerts a WHERE a.subject_type='transaction' AND a.subject_id=t.transaction_id)
              THEN 1 ELSE 0 END AS has_alert
  FROM transactions t
),
txn_claim_flag AS (
  SELECT transaction_id, 1 AS has_claim FROM claims
)
SELECT taf.has_alert,
       COUNT(*) AS n_txn,
       COALESCE(SUM(tcf.has_claim),0) AS n_claims,
       ROUND(100.0*COALESCE(SUM(tcf.has_claim),0)/COUNT(*),2) AS claim_rate_pct
FROM txn_alert_flag taf
LEFT JOIN txn_claim_flag tcf ON taf.transaction_id = tcf.transaction_id
GROUP BY taf.has_alert
""")

run("3b_claim_rate_by_segment_and_alert", """
WITH txn_alert_flag AS (
  SELECT t.transaction_id, t.customer_id,
         CASE WHEN EXISTS (SELECT 1 FROM alerts a WHERE a.subject_type='transaction' AND a.subject_id=t.transaction_id)
              THEN 1 ELSE 0 END AS has_alert
  FROM transactions t
),
txn_claim_flag AS (SELECT transaction_id, 1 AS has_claim FROM claims)
SELECT c.segment, taf.has_alert, COUNT(*) AS n_txn,
       COALESCE(SUM(tcf.has_claim),0) AS n_claims,
       ROUND(100.0*COALESCE(SUM(tcf.has_claim),0)/COUNT(*),2) AS claim_rate_pct
FROM txn_alert_flag taf
JOIN customers c ON taf.customer_id = c.customer_id
LEFT JOIN txn_claim_flag tcf ON taf.transaction_id = tcf.transaction_id
GROUP BY c.segment, taf.has_alert
ORDER BY c.segment, taf.has_alert
""")

run("3c_claims_severity_breakdown_when_alerted", """
WITH claim_max_sev AS (
  SELECT cl.claim_id, cl.transaction_id,
         (SELECT MAX(CASE severity WHEN 'high' THEN 3 WHEN 'medium' THEN 2 WHEN 'low' THEN 1 ELSE 0 END)
          FROM alerts a WHERE a.subject_type='transaction' AND a.subject_id=cl.transaction_id) AS max_sev_code
  FROM claims cl
)
SELECT
  CASE max_sev_code WHEN 3 THEN 'high' WHEN 2 THEN 'medium' WHEN 1 THEN 'low' ELSE 'no_prior_alert' END AS prior_alert_severity,
  COUNT(*) AS n_claims
FROM claim_max_sev GROUP BY prior_alert_severity ORDER BY n_claims DESC
""")
