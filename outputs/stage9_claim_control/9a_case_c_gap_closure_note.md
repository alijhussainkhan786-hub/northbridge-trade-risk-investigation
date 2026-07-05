# Case C Gap-Closure Note (pre-Stage 9)

**Subject:** 85-transaction value/weight stable anomaly set (Stage 5/8 Case C).

## 1. Data-Quality Cross-Check Results

| Check | Case C overlap | Portfolio rate | Read |
|---|---|---|---|
| Shipment date-logic errors | 0/85 (0.0%) | 61/6090 (1.0%) | Below baseline - rules out this DQ issue as an explanation |
| Payment date-logic errors | 0/85 (0.0%) | 35/6000 (0.6%) | Below baseline - ruled out |
| Missing arrival_date | 3/85 (3.5%) | 122/6090 (2.0%) | Mildly elevated, n=3 too small to be meaningful |
| Split shipments | 0/85 (0.0%) | 120/6000 (2.0%) | Below baseline - ruled out |
| Zero-shipment transactions | 0/85 (0.0%) | 30/6000 (0.5%) | Mechanically 0% by construction (ratio requires a shipment) - not a finding |
| Partial-payment transactions | 16/85 (18.8%) | 900/6000 (15.0%) | Mildly elevated, not dramatic on n=85 |
| Entity-resolution cluster overlap | 20/73 counterparties (27.4%) | 75/260 counterparties (28.8%) | **Matches baseline almost exactly - no elevation** |

**Conclusion:** No data-quality issue or entity-resolution overlap explains the Case C pattern. The set is not a byproduct of known DQ problems.

## 2. Stratified Robustness Test Results

- **Alert rate:** 38.8% (Case C) vs 15.7% (rest-of-portfolio base rate), binomial p=2.17e-07. **Holds directionally in every product category, corridor, and segment stratum tested** (e.g. Mid-market 58% vs 15.6% baseline; Corridor_F 45% vs 15.5%; Corporate 50% vs 13.1%) — not explained away by any single confound, though most individual strata have small n (1-3) and are directionally consistent rather than independently significant.
- **Claim rate:** 3.5% vs 3.0% portfolio — not meaningfully elevated.
- **Median invoice value:** £74,840 (Case C) vs £35,996 (portfolio) — elevated, but this is an expected mechanical consequence of how the value/weight ratio was constructed (numerator is invoice value), not an independent finding. Value-band distribution is concentrated in Q2-Q4 (24/31/21) rather than exclusively Q4 as initially assumed — **correcting an assumption made before running the check.**
- **Payment/shipment reconciliation:** Perfect (0 mismatches of 85) — the anomaly is confined to the weight dimension only; no accompanying financial inconsistency.
- **New finding this session — partial circularity check:** Of 33 alerts on Case C transactions, 23 (70%) are typed `value_mismatch` — plausibly related to the same underlying ratio calculation (a *partial* circularity risk, weaker than the fully-circular IND07/third-party-payer case where 100% of alerts shared one type). The remaining 30% are independent alert types.

## 3. Decision Update

**Case C status: REQUIRES MORE DATA before decision** (narrowed, not resolved). Confound-based and data-quality-based alternative explanations are now ruled out by direct test. The one remaining substantive gap is a **product-specialist plausibility review** of the goods value/weight combinations, alongside acknowledging the alert-rate figure carries a partial circularity caveat. No customer/counterparty concentration exists, so there is no natural entity-level subject for EDD referral — this remains a portfolio-level pattern requiring domain expertise, not further internal data analysis, to resolve.

---
