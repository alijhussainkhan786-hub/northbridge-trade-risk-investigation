from pathlib import Path
import sqlite3, pandas as pd
from datetime import date

conn = sqlite3.connect("/home/claude/build/northbridge.db")
reg = pd.read_csv("/home/claude/build/data_quality_issues_register.csv")

today = date.today().isoformat()
rows = []
for _, r in reg.iterrows():
    rows.append({
        "issue_id": r["issue_id"],
        "table_name": r["table_name"],
        "record_id": f"AGGREGATE ({r['count']})",  # these are aggregate/pattern-level issues, not single-record
        "issue_type": r["issue_type"],
        "original_value": r["description"],
        "resolution_applied": "none - logged only, pending approval",
        "resolution_method": r["proposed_handling_method"],
        "confidence_label": r["severity"],
        "date_logged": today,
    })

df = pd.DataFrame(rows)
df.to_sql("data_quality_issues", conn, if_exists="append", index=False)
conn.commit()

check = pd.read_sql("SELECT issue_id, table_name, confidence_label, resolution_applied FROM data_quality_issues ORDER BY issue_id", conn)
print(check.to_string(index=False))
print(f"\nTotal rows in data_quality_issues: {len(check)}")

# re-export CSV mirror + confirm source tables untouched
df_all = pd.read_sql("SELECT * FROM data_quality_issues", conn)
df_all.to_csv("/home/claude/build/csv_exports/data_quality_issues.csv", index=False)

# sanity: confirm no other table's row count changed
for t in ["customers","counterparties","transactions","shipments","payments"]:
    n = pd.read_sql(f"SELECT COUNT(*) c FROM {t}", conn).iloc[0,0]
    print(t, "row count:", n)

conn.close()
