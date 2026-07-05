# Northbridge Trade Risk Investigation — Stage 3 Data Quality Audit Report
Audit performed against the analyst-facing dataset only. Ground-truth file was not consulted.

## 1. File/Database Inventory
`northbridge.db` (SQLite, 15 tables) + 15 mirrored CSVs in `csv_exports/`. Audit executed via direct SQL/pandas queries against the database.

## 2. Table Row Counts
customers 180 · counterparties 260 · intermediaries 45 · products 18 · destinations 30 · transactions 6,000 · shipments 6,090 · payments 7,020 · transaction_intermediaries 9,600 · alerts 960 · claims 180 · entity_relationships 70 · entity_attributes 1,400 · case_review_log 0 · data_quality_issues 0. **Category 1 (observed fact)** — matches the generation manifest.

## 3. Grain Confirmation
| Table | Confirmed grain | Deviation found |
|---|---|---|
| transactions | 1 row/transaction_id | None |
| shipments | 1 row/transaction expected | 5,850 txns ×1, 120 ×2 (split), 30 ×0 (gap) — see DQ0011 |
| payments | 1 row/transaction expected | 5,100 ×1, 780 ×2, 120 ×3 (partial) — see DQ0012 |
| transaction_intermediaries | ≥1 row/transaction | 950 transactions have **zero** intermediary rows (min 1/mean 1.9/max 6 among linked); logged as intelligence gap, not an error |
| claims | 0–1 row/transaction expected | Confirmed 1:1 for all 180 claims present, no multi-claim transactions |

## 4. Primary Key Uniqueness
All 13 tables with defined PKs (customers through entity_attributes) show `total = distinct` — **no duplicate primary keys anywhere.** Category 1 fact.

## 5. Foreign Key / Polymorphic Reference Integrity
All 10 direct FK checks (transactions→customers/counterparties/products/destinations; shipments/payments/transaction_intermediaries/claims→transactions; transaction_intermediaries→intermediaries; claims→customers) return **zero orphans**.

Polymorphic reference checks (Alerts.subject_id, Entity_Attributes.entity_id, Entity_Relationships.entity_id_1/2) all resolve correctly against their declared `entity_type`/`subject_type` — **zero unresolved references.** However, `alerts.subject_type` takes only the value `'transaction'` across all 960 rows, despite the schema supporting `customer`/`counterparty` subjects (DQ0009) — a monitoring-coverage gap relevant to Q7, not an integrity failure.

## 6. Missing-Value Analysis
- `shipments.arrival_date`: 122 nulls (2.0%) — DQ0003
- `counterparties.registration_number`: 96 nulls, all non-GB (38.4% of the 250 non-GB counterparties) — DQ0004
- No other table shows nulls or empty-string pseudo-nulls on inspection.

## 7. Duplicate and Near-Duplicate Screening
- **Exact duplicate rows** (all fields identical except PK): 0.
- **Near-duplicate by normalized legal name** (suffix variation only, e.g. "Ltd" vs "Limited"): 20 counterparty rows across 10 name groups — DQ0005.
- **Shared `registered_address`**: 21 groups covering 47 counterparty rows (18.1% of the table) — DQ0006.
- **Shared `bank_account_hash`**: 17 groups covering 38 counterparty rows (14.6%) — DQ0007. Two of these groups are 4-way clusters (`CPTY00002/45/148/156` and `CPTY00073/141/218/220`); the remainder are 2-way and one 3-way.

**Judgment call:** address strings are built from a visibly small pool of unit numbers and street-type words, so shared addresses could reflect either a genuine common entity **or** coincidental format collision in a limited string space. Shared `bank_account_hash` is a stronger signal than shared address for the same reason (a hashed account number is far less likely to collide by chance than a formulaic address string) — this is why DQ0007 is rated Critical while DQ0006 is rated High. This distinction matters for Stage 6: not all attribute overlaps carry equal evidential weight, and treating them identically would understate/overstate confidence in either direction.

## 8. Date Coverage and Date-Logic Checks
Transaction dates span 2022-01-01 to 2024-12-31 as designed (0 nulls). Downstream dates (shipment/payment/alert/claim) extend into early-to-mid 2025 as expected lag from late-2024 transactions.

Logic violations found:
- 61 shipments (1.0%) with `arrival_date < departure_date` — DQ0001
- 35 payments (0.5%) with `payment_date < transaction_date` — DQ0002
- 0 shipments departing before their transaction date
- 0 alerts predating their subject transaction
- 0 claims predating their transaction

## 9. Shipment/Payment/Transaction Reconciliation
- `SUM(payments.amount)` reconciles to `transactions.invoice_value` for all 6,000 transactions (tolerance ±0.50) — **0 mismatches.**
- `SUM(shipments.declared_value)` reconciles to `invoice_value` for all transactions that have at least one shipment — **0 mismatches** among the 5,970 with shipments; the 30 zero-shipment transactions simply have no shipment-side value to reconcile (intelligence gap, not a mismatch).

## 10. Alert and Claim Linkage Checks
- 960/960 alerts (100%) carry a resolvable `transaction_id` subject — no orphaned alert subjects.
- 72/180 claims (40.0%) are linked to a transaction that also has ≥1 alert on record, against an overall transaction-level alert rate of 16.0%. This is a **descriptive relationship** (Category 3) only at this stage — no causal claim, no investigative conclusion. It will need a matched-volume control comparison before any further weight is given (deferred to later stages).

## 11. Many-to-Many Join Inflation Risks
A naive join of `transactions ⋈ transaction_intermediaries ⋈ payments` produces 11,220 rows against a 6,000-transaction base — a **1.87x fan-out**. Any `SUM(invoice_value)` or `SUM(payment.amount)` run across this naive join would be materially overstated. **Mandatory control for Stage 4:** aggregate to transaction grain (or use `DISTINCT`/pre-aggregated subqueries) before joining to the bridge table, and document this explicitly in every SQL script that touches `transaction_intermediaries`.

Separately, intermediary `INTM00038` accounts for 66.5% of all distinct transactions linked via the bridge table (3,360 of ~5,050 linked transactions) — a striking concentration. **This is flagged as a descriptive fact only.** Its `role_type` and peer context have not yet been examined, and no risk interpretation is attached at this stage — testing whether this is an ordinary large-scale freight forwarder versus a genuine hub of concern is explicitly deferred to Stage 6/7.

## 12. Entity-Resolution Data-Quality Risks
Summarised from §7 above: 10 near-duplicate name groups, 21 shared-address groups, 17 shared-bank-account groups, and a 38.4% registration-number gap for non-GB counterparties. Combined, these mean **entity resolution (Stage 6) cannot rely on any single attribute** — registration number is too often missing, address strings are too formulaic to be conclusive alone, and only converging evidence across multiple independent attributes (plus, where available, a declared `Entity_Relationships` edge) should raise resolution confidence.

## 13–14. Data-Quality Issue Register with Severity Ratings
See attached `data_quality_issues_register.csv` (12 logged issues). Severity summary:

| Severity | Count | Issues |
|---|---|---|
| Critical | 2 | DQ0007 (shared bank account clusters), DQ0010 (join-inflation risk) |
| High | 4 | DQ0001, DQ0002, DQ0005, DQ0006 |
| Medium | 5 | DQ0003, DQ0004, DQ0008, DQ0009, DQ0011 |
| Low | 1 | DQ0012 |

Severity logic: **Critical** = would silently corrupt a headline financial or entity-resolution metric if not controlled before Stage 4/6. **High** = materially affects a named Stage 0 investigation question if unaddressed. **Medium** = a genuine gap or concentration requiring documentation and cautious interpretation, not a threat to metric integrity. **Low** = expected behaviour requiring only correct aggregation logic.

## 15. Cleaning / Handling Plan (not executed)
No source values will be altered. Proposed handling per issue is recorded in the `proposed_handling_method` column of the register — the consistent pattern is: **flag, do not impute; exclude from a specific metric where the value is unreliable for that metric; route ambiguous entity signals to Stage 6 with a confidence label; and enforce aggregation discipline in SQL rather than modifying data.** All 12 issues are currently `resolution_status = pending approval` and will only be written to the `data_quality_issues` table once you approve this plan — no rows have been added to that table yet.

---
DECISION: Present this audit as the discovered state of the analyst-facing dataset; no cleaning executed.
EVIDENCE: All findings above are Category 1 (observed fact) or Category 3 (descriptive relationship, §10 alert/claim linkage) — no hypothesis or conclusion has been asserted.
ASSUMPTIONS: Address/bank-account overlaps are entity-resolution *candidates*, not confirmed matches; the intermediary concentration in §11 is reported descriptively with no risk interpretation attached.
RISKS: If the join-inflation control (DQ0010) or the shared-attribute distinction (DQ0006 vs DQ0007) is skipped in Stage 4/6, downstream financial totals or entity clusters could be materially wrong or overstated in confidence.
UNRESOLVED QUESTIONS: Whether to formally log these 12 issues into `data_quality_issues` now (a logging action) versus waiting until Stage 4 begins.
NEXT ACTION: Await your approval of this audit and the handling plan before proceeding to Stage 4 (SQL Investigation).
