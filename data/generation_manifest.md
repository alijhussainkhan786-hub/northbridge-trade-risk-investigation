# Northbridge Trade Risk Investigation — Generation Manifest
Stage 2B Controlled Synthetic Data Generation. Fictional data only.

## Reproducibility
- Random seed: **42** (`numpy.random.default_rng(42)`)
- Generation script: `generate_northbridge.py` (deterministic given seed; re-running reproduces identical output)
- Time window: 2022-01-01 to 2024-12-31 (transactions/shipments/payments/alerts/claims); customer onboarding back to 2015-01-01

## Final Row Counts (all matched target exactly — see validation report)
| Table | Rows |
|---|---|
| customers | 180 |
| counterparties | 260 (245 base + 15 noise duplicates) |
| intermediaries | 45 |
| products | 18 |
| destinations | 30 |
| transactions | 6,000 |
| shipments | 6,090 |
| payments | 7,020 |
| transaction_intermediaries | 9,600 |
| alerts | 960 |
| claims | 180 |
| entity_relationships | 70 |
| entity_attributes | 1,400 |
| case_review_log | 0 (populated later) |
| data_quality_issues | 0 (populated later) |
| **Total** | **25,853** |

## Embedded Rates (as generated, confirmed by validation script)
- Alert rate: 960/6000 = 16.00%
- Claim rate: 180/6000 = 3.00%
- Split-shipment rate: 120/6000 = 2.00%
- Zero-shipment rate: 30/6000 = 0.50%
- Partial-payment rate: 900/6000 = 15.00% (780 x2-pay + 120 x3-pay)
- Shipment date-logic errors: 61/6090 = 1.00%
- Missing shipment arrival_date: 122/6090 = 2.00%
- Payment date-logic errors: 35/7020 = 0.50%
- Missing counterparty registration_number (non-GB): ~35% of non-GB counterparties
- Noise duplicate counterparties: 15 rows (unrelated to any planted pattern)

## Planted Pattern Injection Summary
| Pattern | Entities/transactions affected |
|---|---|
| 1. Counterparty Fragmentation | 8 counterparties (2 clusters of 4), 2 customers, 75 reassigned transactions (38 + 37) |
| 2. Value/Weight Implausibility | 25 transactions |
| 3. Third-Party Payment Routing | 120 transactions (2.0%) |
| 4. Intermediary Hub (decoy) | 1 intermediary, 3,360 of 9,600 transaction_intermediary rows (35%) |
| 5. Alert/Claim Co-occurrence | 72 of 180 claims (40%) alert-linked; 108 (60%) independent |

Alert composition: 672 genuine noise (70%) + 288 nominally "pattern-eligible" slots, of which 213 were actually drawn from pattern-linked transactions and 75 backfilled from noise pool (pattern transaction pool was smaller than the 288 quota) — this shortfall is a **generation deviation**, noted below.

## Deviations from Approved Specification
1. **Alert pattern-linked count:** Spec targeted ~288 pattern-linked alerts (30% of 960). Actual pattern-linked alerts = 213, with the remaining 75 backfilled as noise alerts, because the combined pool of Pattern 1/2/3 transactions (approx. 233 unique transactions) was smaller than 288. This is a **minor, disclosed deviation** — it does not affect any control total, and if anything makes the pattern-linked alert share slightly more conservative (22.2% of alerts vs. the intended 30%), which is consistent with the "not every planted-pattern transaction generates an alert" design principle in Stage 2 §9. No corrective action taken; flagged for awareness in Stage 3 audit.
2. All other parameters matched specification exactly (see validation report).

## Output Files
- `northbridge.db` — SQLite database, 15 analyst-facing tables
- `csv_exports/*.csv` — 15 CSV files mirroring the database
- `data_dictionary.md` — field-level dictionary
- `ground_truth/ground_truth.json` — hidden validation-only file, physically separate folder, not joined into the SQLite database or CSV exports
- `generation_manifest.md` — this file
