# Findings Summary — Evidence-Classified

Every finding below is labelled with its evidence category. Categories are never blurred.

## 1. Observed Facts (direct data facts, no interpretation)
- Portfolio: 6,000 transactions, 2022-01-01 to 2024-12-31, GBP 7.84B total invoice value.
- Alert rate 16.0% (960/6,000); claim rate 3.0% (180/6,000).
- Payment and shipment values reconcile to invoice value with 0 mismatches once pre-aggregated to transaction grain.

## 2. Derived Analytical Facts (computed from source data, not requiring interpretation)
- Two customers each show 100% transactional/value exclusivity (38 and 37 transactions respectively) to a distinct 4-member counterparty cluster.
- Both linked counterparty clusters are classified "STRONG" under entity resolution (shared bank_account_hash + at least one independent attribute), and do not match on incidental fields (email/phone) - distinguishing them from a separate 15-pair cluster that does match on all fields.
- Intermediary INTM00038 handles 66.5% of linked-transaction volume; its own alert rate (16.01%) and claim rate (3.04%) match portfolio baseline (16.0%/3.0%) almost exactly.
- 85 transactions are flagged as a value/weight anomaly stable across three independent detection methods (ratio, robust z-score, IQR).

## 3. Descriptive Relationships (statistically tested, non-causal)
- Claim rate is 7.50% for alerted transactions vs. 2.14% for non-alerted (chi2=77.7, p=1.2e-18), holding across SME/Mid-market segments and all value quartiles. Explicitly non-causal - a plausible shared confound (transaction/counterparty complexity) is not ruled out.
- The 85-transaction value/weight set shows an elevated alert rate (38.8% vs. 15.7% base) that persists across every product/corridor/segment stratum tested - but a partial circularity caveat applies (70% of associated alerts share a plausibly-related alert type).

## 4. Investigative Hypotheses (require further evidence to confirm or refute)
- The two flagged customer-cluster relationships may reflect undisclosed common control rather than a disclosed commercial structure.
- The value/weight anomaly set may reflect systematic mis-valuation rather than ordinary category variance.

## 5. Alternative (Plausible Innocent) Explanations - given equal prominence throughout
- Exclusive distributor/agency arrangements with a related corporate family sharing group treasury banking (for both flagged customer clusters).
- Ordinary within-category value variance, premium vs. standard-grade goods (for the value/weight set).
- Large-scale, broad-client-base freight forwarding (for INTM00038's volume).
- Duplicate data entry of the same real-world counterparty (for the 15-pair cluster).

## 6. Intelligence Gaps (cannot be resolved with available data)
- No external corporate-registry data to confirm or refute ownership structure behind either flagged cluster.
- No product-specialist input yet on the value/weight set's goods plausibility.
- Declared-relationship provenance (regulatory filing vs. self-reported) is not differentially weighted in the current scoring framework.

## 7. Client-Confirmed Information
None - this is a fictional project with no external client input beyond the project owner's stage-by-stage approvals.

## 8. Simulated Ground Truth (validation-only)
Held exclusively in ground_truth/ground_truth.json, never referenced in Stages 3-9 analysis. Used only to confirm, after the full pipeline ran, that planted patterns were structurally recoverable by the methodology - not exposed in this document, the dashboard, or the executive assessment.
