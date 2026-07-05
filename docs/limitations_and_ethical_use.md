# Limitations and Ethical Use

## Fictional Project Boundary
This entire project - organisation, customers, counterparties, transactions, and all findings - is synthetic. No real entity, individual, or organisation is described, referenced, or implicated anywhere in this repository. No confidential, government, law-enforcement, sanctions-enforcement, or intelligence material was used, referenced, or implied at any stage.

## Statistical Limitations
- Small sub-strata (Corporate customer segment, several corridor cells) carry limited statistical power throughout; findings at that granularity are explicitly flagged as low-confidence rather than treated as robust.
- The value/weight anomaly threshold is sensitivity-dependent (candidate count ranges from 22 to 157 depending on method/threshold) - no single cut is presented as objectively correct.
- The priority-scoring framework (Stage 7) is analyst-calibrated, not empirically validated against confirmed real-world outcomes, because no such outcomes exist for a synthetic dataset.

## Methodological Limitations
- Declared-relationship provenance (regulatory-filing-sourced vs. self-reported) is not currently weighted differently in the scoring framework despite a demonstrated reliability difference between the two flagged cases - a known, documented gap for future iteration.
- Entity resolution relies on exact-match attributes (bank account hash, address string, name normalisation) - no fuzzy/probabilistic matching was used at the audit stage, by design, to avoid pre-resolving the analytical question before independent testing.
- All findings are correlational/descriptive by construction; no causal claim is made anywhere in this project.

## Evidential Discipline (see docs/findings_summary.md for full classification)
Every material claim is labelled as one of 8 evidence categories and never blurred. Priority score is explicitly not proof: review first is the ceiling meaning of any priority designation in this project.

## Appropriate Use of This Repository
This repository is intended as a portfolio demonstration of methodology - relational modelling, synthetic data engineering, SQL/Python investigation, entity resolution, explainable prioritisation, and claim-control discipline. It is not intended, and must not be used, as:
- A template for making determinations about real individuals or organisations without independent legal/compliance review.
- A validated risk-scoring product - the scoring logic is illustrative and transparent by design, not empirically calibrated.
- A source of guidance on real financial-crime detection thresholds, which require domain-specific regulatory input this project does not provide.

## Ground-Truth Handling
ground_truth/ground_truth.json is retained for transparency about the project's own construction (so a reviewer can verify the analytical pipeline is capable of recovering known planted patterns) but was never used to inform any Stage 3-9 finding. See ground_truth/README_DO_NOT_USE_FOR_ANALYSIS.md.
