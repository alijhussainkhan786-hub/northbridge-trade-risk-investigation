# Reproducibility Guide

## Environment
- Python 3.11+, packages: pandas, numpy, scipy, networkx, sqlite3 (stdlib)
- Install: pip install pandas numpy scipy networkx
- No external network access required at any stage (fully offline-reproducible).

## Random Seed
SEED = 42 (numpy.random.default_rng(42)), set once in src/01_generation/generate_northbridge.py. All downstream analysis is deterministic given the generated data/northbridge.db.

## Execution Order
1. Generate data: python src/01_generation/generate_northbridge.py -> produces northbridge.db + CSV exports (paths in script assume a local build/ working directory; adjust OUT_DIR as needed).
2. Audit: python src/02_audit/audit_stage3.py (independent discovery of data-quality issues), then python src/02_audit/log_dq_issues.py (writes the 12 approved issues into data_quality_issues), then python src/02_audit/validate.py (control-total re-verification).
3. SQL investigation: run src/03_sql_investigation/stage4_area1.py through stage4_area8.py in numeric order - each is independent and reads only from northbridge.db.
4. Python analysis: run src/04_python_analysis/stage5_part1.py through stage5_part9.py in order - stage5_part1.py builds a cached enriched transaction frame (txn_enriched.pkl) that later parts depend on; this cache file is a build artefact, not part of the shipped repository, and must be regenerated locally.
5. Entity resolution & network: src/05_entity_resolution/stage6_part1.py through stage6_part4.py, in order (depends on Stage 4/5 outputs).
6. Prioritisation framework: src/06_prioritisation/stage7_part1.py through stage7_part4.py, in order (depends on Stage 5/6 outputs).
7. Claim-control: src/07_claim_control/stage9_case_c_gap1.py, stage9_case_c_gap2.py, stage9_claim_register.py.
8. Dashboard: dashboard/dashboard.html is a static, self-contained file (no build step) - open directly in any browser.

## SQLite / CSV Structure
data/northbridge.db contains all 15 analyst-facing tables. data/csv_exports/ mirrors each table as a standalone CSV. ground_truth/ground_truth.json is physically separate and must never be joined to either.

## Validation Controls to Re-Run After Any Change
- Row counts per table (expect: customers 180, counterparties 260, intermediaries 45, products 18, destinations 30, transactions 6000, shipments 6090, payments 7020, transaction_intermediaries 9600, alerts 960, claims 180, entity_relationships 70, entity_attributes 1400, data_quality_issues 12).
- Alert rate 16.0%, claim rate 3.0%.
- Payment/shipment-to-invoice reconciliation: 0 mismatches (must pre-aggregate to transaction grain first - naive 3-way joins inflate rows 1.87x, see outputs/stage4_sql_investigation/stage4_sql_logic_reference.md).
- Re-running src/02_audit/validate.py reproduces all of the above automatically.

## Known Build-Time Caveat
generate_northbridge.py was originally run with OUT_DIR = <repository-root>; update this constant to your local working directory before running.
