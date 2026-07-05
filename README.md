# Northbridge Trade Risk Investigation (Fictional Portfolio Project)

A fictional, end-to-end cross-border trade risk investigation demonstrating relational data modelling, synthetic dataset engineering, SQL investigation, Python behavioural/anomaly analysis, entity resolution, network analysis, explainable investigation prioritisation, case-file development, claim-control testing, and executive reporting.

**This is a synthetic project.** No real entity, individual, or organisation is described anywhere in this repository. No confidential, government, law-enforcement, or intelligence material was used at any stage. See `docs/limitations_and_ethical_use.md`.

## Live Interactive Dashboard

Explore the investigation dashboard: [Open the Northbridge Trade Risk Dashboard](https://alijhussainkhan786-hub.github.io/northbridge-trade-risk-investigation/dashboard/dashboard.html)

## Portfolio Scale
6,000 transactions (GBP 7.84B total invoice value), 180 customers, 260 counterparties, 45 intermediaries, 2022-01-01 to 2024-12-31. Portfolio alert rate 16.0%, claim rate 3.0%. Full baseline: `outputs/stage4_sql_investigation/`.

## What this project demonstrates
A 12-stage (Stage 0-11) methodology run with an explicit approval gate after every stage, evidential-category discipline (8 evidence types, never blurred), and a Claim-Control Gate that every major finding had to survive before reaching a dashboard or executive report. Full workflow: docs/methodology.md.

## Repository Structure
```
docs/           Investigation brief, data model, synthetic-data spec, methodology,
                data dictionary, findings summary, reproducibility guide,
                limitations/ethics, skills mapping
data/           northbridge.db (SQLite) + per-table CSV exports + generation manifest
ground_truth/   Validation-only planted-pattern record -- NEVER used in analysis (see its README)
src/            Reproducible Python source, organised by stage (01_generation ... 07_claim_control)
outputs/        Stage 3-9, 11 analytical outputs (CSV registers + markdown reports)
dashboard/      Self-contained interactive HTML investigation triage dashboard
manifest/       Final file manifest and QA report for this package
```

## Key Results (headline, evidence-qualified -- full detail in outputs/stage11_executive_assessment.md)
- 2 customer relationships referred for enhanced due diligence review, each showing 100% transactional exclusivity to a small, entity-resolution-linked counterparty cluster, surviving independent statistical, network, and stress testing.
- 1 pattern requires further data -- an 85-transaction value/weight anomaly with no entity concentration, pending product-specialist input.
- 2 items cleared/downgraded -- the portfolio's highest-volume intermediary (cleared after its own alert/claim rate matched baseline exactly) and a 15-pair counterparty cluster (identified as duplicate data entry, not a lead).

Every finding is paired with a plausible innocent explanation and an evidence-gap register. Priority = review first, never proof. See docs/findings_summary.md for the full 8-category evidence breakdown.

## Quick Start
See docs/reproducibility_guide.md for environment setup, execution order, and validation controls. All analysis is deterministic (seed=42) and requires no external network access.

## Dashboard
Open dashboard/dashboard.html directly in any browser -- a self-contained investigation triage view (portfolio baseline, priority cases, case detail, claim-control status, network/cluster summary, evidence gaps, methodology) built only from validated Stage 4-9 summary outputs, never connected to raw tables.

## License / Attribution
Portfolio demonstration project. See LICENSE.md.
