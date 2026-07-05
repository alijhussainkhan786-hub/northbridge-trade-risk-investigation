from pathlib import Path
import pandas as pd
OUT = "/home/claude/build/stage5_outputs"

rows = [
    # customer-level
    dict(candidate_id="AC001", subject_type="customer", subject_id="CUST00135",
         anomaly_type="ALERT_CONCENTRATION", evidence="100% alert rate across 38 txns, all 3 years (2022/23/24), p<0.000001 vs 16% base rate",
         baseline_comparison="Segment(SME) baseline 16.4%; product-mix-expected 16.0%; corridor-mix-expected 15.8%",
         severity_priority="High priority for review", confidence="High (survives volume/mix/segment/time controls)",
         false_positive_risk="Low for the statistical fact itself; risk lies in over-interpreting cause",
         recommended_next_stage="Stage 6 entity resolution + Stage 7 prioritisation"),
    dict(candidate_id="AC002", subject_type="customer", subject_id="CUST00070",
         anomaly_type="ALERT_CONCENTRATION", evidence="100% alert rate across 37 txns, all 3 years, p<0.000001 vs 16% base rate",
         baseline_comparison="Segment(SME) baseline 16.4%; product-mix-expected 16.1%; corridor-mix-expected 16.2%",
         severity_priority="High priority for review", confidence="High (survives volume/mix/segment/time controls)",
         false_positive_risk="Low for the statistical fact itself; risk lies in over-interpreting cause",
         recommended_next_stage="Stage 6 entity resolution + Stage 7 prioritisation"),
    # counterparty cluster
    dict(candidate_id="AC003", subject_type="counterparty_cluster", subject_id="CPTY00002/45/148/156",
         anomaly_type="ALERT_CONCENTRATION + SHARED_ATTRIBUTE", evidence="Rank 1,6,2,4 of 256 by alert rate (31-53%); ALL FOUR share one bank_account_hash; 3 share registered_address",
         baseline_comparison="Portfolio counterparty alert-rate distribution (median ~16%)",
         severity_priority="High priority for review", confidence="Medium-High (cross-queue convergence: alert + shared-attribute)",
         false_positive_risk="Medium - shared address alone could be coincidental (small address-string pool); shared bank account is stronger",
         recommended_next_stage="Stage 6 entity resolution (network analysis)"),
    dict(candidate_id="AC004", subject_type="counterparty_cluster", subject_id="CPTY00073/141/218/220",
         anomaly_type="ALERT_CONCENTRATION + SHARED_ATTRIBUTE", evidence="Rank 9,7,3,5 of 256 by alert rate (33-49%); ALL FOUR share one bank_account_hash and one registered_address",
         baseline_comparison="Portfolio counterparty alert-rate distribution (median ~16%)",
         severity_priority="High priority for review", confidence="Medium-High (cross-queue convergence)",
         false_positive_risk="Medium - same caveat as AC003",
         recommended_next_stage="Stage 6 entity resolution (network analysis)"),
    # value/weight
    dict(candidate_id="AC005", subject_type="transaction_set", subject_id="85 transactions (stable set, see 5e_vw_stable_candidates.csv)",
         anomaly_type="VALUE_WEIGHT_MISMATCH", evidence="Invoice value >5x category-average value-per-kg; consistent finding under ratio, robust z-score, and IQR methods (85 candidates common to all)",
         baseline_comparison="Product-category average value-per-kg (not a global threshold)",
         severity_priority="Medium priority - threshold-dependent", confidence="Medium (stable under 3 methods, but ratio method is the binding constraint, not truly independent triangulation)",
         false_positive_risk="Medium-High - legitimate high-value-low-weight goods exist (electronics, pharma); threshold choice materially changes candidate count (22 to 157 across thresholds tested)",
         recommended_next_stage="Stage 7 - product-specific plausibility review before any prioritisation weight assigned"),
    # third-party payer -- DOWNGRADED per claim-control
    dict(candidate_id="AC006", subject_type="transaction_set", subject_id="120 third-party-payer transactions",
         anomaly_type="THIRD_PARTY_PAYER", evidence="2.0% of portfolio; NOT concentrated in one counterparty (max 4 of 120 at any single counterparty); claim rate 5.0% vs 2.96% non-TP",
         baseline_comparison="Portfolio claim rate 3.0%",
         severity_priority="Low priority as standalone signal", confidence="Low - see claim-control note below (alert co-occurrence is circular, not corroborating)",
         false_positive_risk="High - third-party settlement is standard trade-finance practice; the apparent 100% alert co-occurrence is a monitoring-system artifact (alert_type='third_party_payment' restates the same fact), not independent evidence",
         recommended_next_stage="Do not carry the alert co-occurrence forward as a distinct signal; the underlying 2% TP-payer rate itself can go to Stage 6/7 as a standalone low-weight indicator only"),
    # claim/alert relationship (portfolio-level pattern, not a specific subject)
    dict(candidate_id="AC007", subject_type="portfolio_pattern", subject_id="N/A - descriptive relationship",
         anomaly_type="CLAIM_ALERT_COOCCURRENCE", evidence="Claim rate 7.50% when alerted vs 2.14% when not (chi2=77.7, p=1.2e-18); holds across SME/Mid-market segments and all value bands",
         baseline_comparison="Corporate segment (n=46 alerted) and small corridor cells show same direction but insufficient n for confidence",
         severity_priority="N/A - not an entity-level candidate, a portfolio-level relationship for Stage 7 framework design",
         confidence="Strong descriptive relationship (Category 3)",
         false_positive_risk="N/A - risk is in over-interpreting as causal; plausible confound is shared underlying complexity/exposure driving both alerts and claims",
         recommended_next_stage="Incorporate as a descriptive base-rate multiplier in Stage 7 framework, explicitly labelled non-causal"),
]

reg = pd.DataFrame(rows)
reg.to_csv(f"{OUT}/5i_anomaly_candidate_register.csv", index=False)
print(reg.to_string(index=False))
print(f"\nTotal candidates registered: {len(reg)}")
