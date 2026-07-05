# Methodology — Stage 0 to Stage 11 Workflow

## Overview
This project runs a 12-stage (Stage 0-11) fictional investigation methodology end-to-end, with an explicit approval gate after every stage and no stage skipped or reordered.

| Stage | Name | Core output |
|---|---|---|
| 0 | Investigation brief & analytical questions | docs/00_investigation_brief.md |
| 1 | Relational data model | docs/01_data_model.md, docs/data_dictionary.md |
| 2 | Synthetic dataset spec & controlled generation | docs/02_synthetic_data_specification.md, data/, ground_truth/ |
| 3 | Data quality audit | outputs/stage3_data_quality_audit/ |
| 4 | SQL investigation | outputs/stage4_sql_investigation/ |
| 5 | Python behavioural & anomaly analysis | outputs/stage5_python_analysis/ |
| 6 | Entity resolution & network analysis | outputs/stage6_network_entity_resolution/ |
| 7 | Explainable prioritisation framework | outputs/stage7_prioritisation_framework/ |
| 8 | Case-file development & alternative-hypothesis testing | outputs/stage8_case_files/ |
| 9 | Claim-control & robustness gate | outputs/stage9_claim_control/ |
| 10 | Investigation dashboard | dashboard/dashboard.html |
| 11 | Executive intelligence assessment | outputs/stage11_executive_assessment.md |

## Governing Principles (applied at every stage)
1. Evidential-category discipline - every material claim classified as one of 8 categories (observed fact through simulated ground truth); never blurred. See docs/findings_summary.md.
2. No black-box scoring - the Stage 7 framework is fully explainable: every point traces to a named indicator, source field, and calculation rule (outputs/stage7_prioritisation_framework/7a_indicator_dictionary.csv).
3. Claim-Control Gate before reporting - no finding reached the dashboard/executive report without independent recalculation, alternative-denominator testing, confounder search, and an explicit carry-forward/downgrade/remove decision (Stage 9).
4. Ground-truth isolation - the hidden validation file was never consulted during Stages 3-8; used only to check methodology soundness after the fact.
5. Priority is not proof - every prioritised case is paired with a plausible innocent explanation and a decision category from a fixed vocabulary (Escalate to EDD / Continue monitoring / Requires more data / Close as likely benign) - never a determination of guilt.

## Key Analytical Chain (worked example)
The project's central worked example - two customers (Stage 5/7 output, referred to as Case A / Case B per the executive assessment) each showing 100% transactional exclusivity to a small counterparty cluster - was tested at every stage:
- Stage 4 (SQL): alert-concentration query flagged both customers among top-ranked entities.
- Stage 5 (Python): binomial testing confirmed statistical significance (p<10^-29) surviving product-mix, corridor, segment, and time-period controls.
- Stage 6 (network/entity resolution): confirmed 100% transactional exclusivity and a STRONG entity-resolution classification (shared bank account + address) for the linked counterparty cluster - distinguished analytically from an unrelated duplicate-data-entry cluster by checking whether incidental fields (email/phone) also matched.
- Stage 7 (prioritisation): scored under a capped, explainable framework; a scoring artifact (incidental low-exposure customers inheriting entity-resolution points) was caught and fixed during application.
- Stage 8 (case files): documented with plausible innocent explanations (exclusive agency arrangement, shared group treasury) given equal prominence to concern-supporting evidence.
- Stage 9 (claim-control): re-tested; survived every stress test (removing alert indicators, removing entity-resolution indicators, threshold variation) - carried forward as an EDD referral, explicitly not a finding.

## Negative Findings Preserved as First-Class Results
Two "nothing found" results are documented with the same rigor as positive findings:
- INTM00038 (highest-volume intermediary, 66.5% of linked transactions) - cleared because its own alert/claim rate matches portfolio baseline exactly despite massive volume.
- A 15-pair counterparty cluster matching on every attribute including incidental fields (email, phone) - classified as duplicate data entry, not an investigative lead, and routed to data-quality remediation instead.
