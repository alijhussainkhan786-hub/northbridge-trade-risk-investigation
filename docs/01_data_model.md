# Stage 1 — Relational Data Model

## 14 Analyst-Facing Tables (+ Case_Review_Log, Data_Quality_Issues as governance logs)
`customers`, `counterparties`, `intermediaries`, `products`, `destinations`, `transactions`, `shipments`, `payments`, `transaction_intermediaries` (bridge table), `alerts`, `claims`, `entity_relationships`, `entity_attributes`, `case_review_log`, `data_quality_issues`.

Full field-level schema: see `docs/data_dictionary.md`.

## Key Relationships
- One-to-many: customers→transactions, counterparties→transactions, products→transactions, destinations→transactions/shipments, transactions→shipments/payments/claims (allowing split shipments and partial payments).
- Many-to-many: `transaction_intermediaries` bridges transactions↔intermediaries (added by approved refinement, avoiding join-inflation); `entity_relationships` is a self-referencing bridge across the polymorphic entity space (customer/counterparty/intermediary).
- Polymorphic references (`entity_type` + `entity_id` pattern): `alerts.subject_*`, `entity_relationships.entity_*_1/2`, `entity_attributes.entity_*`. These cannot be enforced by a DB foreign-key constraint and are validated programmatically (see Stage 3 audit).

## ID Namespace Rules
Non-overlapping prefixes: `CUST`, `CPTY`, `INTM`, `TXN`, `SHIP`, `PAY`, `ALRT`, `CLM`, `REL`, `ATTR`, `PROD`, plus ISO-2 country codes — enabling unambiguous polymorphic-reference validation without a lookup table.

## Control Totals Defined at Design Time
Row-count validation, PK uniqueness, referential integrity (including programmatic polymorphic checks), duplicate detection, date coverage, and reconciliation checks (payments/shipments vs. invoice value; alert-to-transaction and claim-to-transaction linkage rates) — all executed in Stage 3.

## Recommended Storage
SQLite (`data/northbridge.db`) as source of truth, mirrored to per-table CSVs (`data/csv_exports/`) for transparency and pandas ingestion.
