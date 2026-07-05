# Stage 4 — SQL Query Logic Reference (Deliverable B)
All queries executed against `northbridge.db`. Full parameterised source in `stage4_area1.py` .. `stage4_area8.py`. Key patterns below; see those files for exact SQL.

## Mandatory fan-out control (applied throughout)
Every query touching `transaction_intermediaries` or `payments` or `shipments` pre-aggregates to `transaction_id` grain in a CTE **before** joining to dimension tables (customers/counterparties/products/destinations). Example pattern used repeatedly:
```sql
WITH ti_distinct AS (
  SELECT DISTINCT transaction_id, intermediary_id FROM transaction_intermediaries
)
SELECT ... FROM ti_distinct ti JOIN intermediaries i ON ... GROUP BY ...
```
Validated: naive 3-way join (transactions × transaction_intermediaries × payments) = 11,220 rows vs. 6,000 transaction grain (1.87x fan-out) — confirmed present and confirmed avoided in all Area 6+ queries by using `DISTINCT`/pre-aggregation.

## Area 1 — Portfolio baseline
Grain: transaction. Simple GROUP BY on `strftime`, `segment`, `corridor_group`, `product_category`. Base rates computed as scalar subqueries with explicit numerator/denominator (`COUNT(alerts)/COUNT(transactions)`).

## Area 2 — Alert concentration
Alerts pre-aggregated per `transaction_id` (`alert_per_txn` CTE) before joining to customer/counterparty/corridor/product/intermediary dimensions. Rate = `alerts_per_100_txn = 100 * SUM(n_alerts) / n_txn` at each dimension's grain. Applied minimum-n filters (`HAVING n_txn >= 10`) in counterparty/intermediary views to avoid small-sample noise.

## Area 3 — Claim/alert relationship
Two independent boolean flags per transaction (`has_alert`, `has_claim`) computed via `EXISTS` subqueries — no join fan-out possible since each flag is 0/1 per transaction. Cross-tabulated by segment. Explicitly labelled descriptive (Category 3), not causal.

## Area 4 — Payment/invoice consistency
`payments` pre-aggregated per transaction (`SUM(amount)`, `COUNT(*)`) before comparing to `invoice_value`. Third-party payer query is a direct filter (`paying_entity_type != 'customer'`) — no aggregation risk since each payment row is already atomic.

## Area 5 — Shipment/invoice consistency
`shipments` pre-aggregated per transaction (`SUM(declared_value)`, `SUM(declared_weight_kg)`) before comparison. Value-per-kg ratio benchmarked against product-category average (not a global threshold) — tested at 5 thresholds (3x/5x/10x/20x/50x) for sensitivity.

## Area 6 — Intermediary concentration
`transaction_intermediaries` de-duplicated to distinct (transaction_id, intermediary_id) pairs (`ti_distinct` CTE) before any COUNT/GROUP BY, preventing role/sequence_order fan-out. HHI concentration index computed as `SUM(share^2)` across intermediaries.

## Area 7 — Counterparty concentration
Direct GROUP BY on `transactions.counterparty_id` for value/count; alert and claim rates use the same pre-aggregation pattern as Area 2/3.

## Area 8 — Investigation queue candidates
All seven queues are either (a) dimension-level aggregates with a `HAVING` threshold and a fixed minimum sample size, or (b) row-level filters on already-atomic tables (payments, claims), or (c) self-joins on `counterparties` for exact shared-attribute matches (`c1.field = c2.field AND c1.id < c2.id` to avoid duplicate/reversed pairs and self-matches). No fuzzy matching used at this stage per instruction.
