# Northbridge Trade Risk Investigation
## Executive Intelligence Assessment
**Prepared for:** Head of Financial Crime & Trade Integrity
**Basis:** Stage 9-approved claims and Stage 10 dashboard only. Fictional portfolio project — no real entities.

---

### 1. Executive Assessment

This review examined 6,000 transactions across a fictional trade finance/insurance portfolio (2022–2024) using a staged analytical methodology (data audit → SQL investigation → behavioural analysis → entity resolution → explainable prioritisation → case files → claim-control testing → dashboard). Two customer relationships are recommended for enhanced due diligence (EDD) review based on statistically robust, multiply-corroborated indicators. One additional pattern requires specialist input before a decision can be reached. Two initially-notable observations were tested and cleared. No finding in this assessment constitutes evidence of wrongdoing; all priority designations mean "review first," not "confirmed."

### 2. Portfolio Baseline

| Metric | Value |
|---|---|
| Transactions | 6,000 (£7.84B total value; median £36k — right-skewed) |
| Alert rate | 16.0% |
| Claim rate | 3.0% |
| Customers / Counterparties / Intermediaries | 180 / 260 / 45 |

Baseline rates are stable across segment, corridor, product, and month — no portfolio-wide confound explains any of the priority findings below.

### 3. Priority Cases for EDD Review

**Case A — Customer CUST00135 + a 4-member counterparty cluster.** 100% of this customer's transaction volume and value (38 transactions, £14.4M) runs exclusively through four counterparties that independently show a shared banking identifier and registered address; two of six pairwise links also carry a documented (regulatory-filing-sourced) corporate relationship. The customer's alert rate is 100% against a 16.0% portfolio base rate, and this holds after controlling for product mix, corridor, segment, and time period. **Plausible innocent explanation:** an exclusive distribution/agency arrangement with a related corporate family sharing group banking. Recommendation: refer for EDD review to confirm ownership structure and commercial basis.

**Case B — Customer CUST00070 + a separate 4-member counterparty cluster.** Structurally identical pattern (100% exclusivity, 37 transactions, £14.0M, 100% alert rate), arising independently elsewhere in the portfolio. The corresponding declared relationship here is self-reported rather than filing-sourced — a weaker corroboration than Case A, noted explicitly. Recommendation: refer for EDD review.

Both cases are supported by convergent, independently-derived evidence (statistical, network, and entity-resolution) rather than any single test.

### 4. Cases Requiring More Data

**Case C — 85-transaction value/weight pattern**, spread across 67 customers and 73 counterparties with no concentration in any single party. Confound and data-quality explanations have been actively tested and ruled out; the residual anomaly and its associated elevated alert rate cannot be resolved further without external product-specialist input on goods valuation. Not escalated, as there is no natural entity-level subject for referral.

### 5. Cleared / Downgraded Items

- **Intermediary INTM00038** — handles 66.5% of linked transaction volume but shows an alert rate (16.01%) and claim rate (3.04%) statistically identical to portfolio baseline, and serves the full breadth of customers and counterparties. Assessed as an ordinary large-scale service provider; cleared as likely benign, not silently dropped.
- **A 15-pair counterparty cluster** matching on every recorded attribute including incidental fields (email, phone) — consistent with duplicate data entry of the same underlying record rather than a distinct risk pattern. Routed to data-quality remediation, not investigation.
- **Third-party payment routing** (2.0% of portfolio) — an apparent 100% alert association with this factor was found to be circular (the alert type simply restates the payment-routing fact) and has been capped to low weight accordingly.

### 6. Key Evidence Gaps

- Independent corporate-registry confirmation of Cases A/B's counterparty ownership structures — outside this project's data scope.
- Contractual documentation (distribution/agency agreements) for both flagged customers.
- Product-specialist plausibility review for Case C.
- Declared-relationship provenance (filing-sourced vs. self-reported) is not currently weighted differently in the scoring framework — a documented design gap.

### 7. Methodology Confidence

High confidence in the statistical and structural findings themselves (independently reproduced in SQL and Python; stress-tested against confounders, thresholds, and single-indicator dominance). Low-to-none confidence in any causal interpretation — every priority finding remains equally consistent with a legitimate commercial explanation as with a concerning one, pending external verification.

### 8. Limitations

This is a fictional, synthetic dataset built for methodology demonstration; no finding describes any real entity. Small sub-groups (Corporate segment, several corridor cells) throughout the analysis have limited statistical power and are flagged rather than treated as robust. No sanctions, law-enforcement, or confidential source material was used or implied anywhere in this project.

### 9. Recommended Next Actions

1. Open EDD review files for Cases A and B; request independent ownership verification and commercial documentation.
2. Route Case C to a trade/product specialist for goods-valuation plausibility review.
3. Log the INTM00038 and duplicate-cluster clearances as closed, with review conditions documented (Stage 8) should future data change.
4. Address the declared-relationship provenance weighting gap in the next framework iteration.
