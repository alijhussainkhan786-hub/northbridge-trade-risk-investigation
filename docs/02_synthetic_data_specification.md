# Stage 2 — Synthetic Dataset Specification (Public Summary)

**Note:** This document describes the *methodology* used to generate the dataset. It intentionally omits the specific entity IDs and exact pattern locations, which are recorded only in `ground_truth/ground_truth.json` (validation-only, not for analysis — see that folder's README).

## Generation Parameters
- Random seed: `42` (fully reproducible — see `src/01_generation/generate_northbridge.py`)
- Scale: 25,853 total rows across 15 tables (180 customers, 260 counterparties, 45 intermediaries, 6,000 transactions — see `data/generation_manifest.md` for full breakdown)
- Time window: 2022-01-01 to 2024-12-31

## Two-Layer Design (critical control)
1. **Analyst-facing dataset** (`data/`) — contains no fraud/guilt/risk-label column of any kind. Patterns exist only as statistically detectable structure.
2. **Hidden ground-truth file** (`ground_truth/`) — records which entities/transactions carry each planted pattern, used *only* at the Stage 9 Claim-Control Gate to validate that the pipeline could recover known signal, and never consulted during Stages 3-8 analysis.

## Planted Pattern Types (methodology only - no IDs)
Five pattern types were embedded, each with a defined hypothesis, expected observable signal, plausible innocent explanation, and false-positive risk:
1. **Counterparty fragmentation** - a small number of nominally distinct counterparties sharing core identifiers (bank account, address), concentrating a customer's trade volume.
2. **Value/weight implausibility** - invoice value inconsistent with declared shipment weight relative to product-category norms.
3. **Third-party payment routing** - final settlement by an entity other than the transacting customer.
4. **Intermediary hub (deliberate decoy)** - one intermediary handling disproportionate volume, designed to test whether the methodology correctly avoids treating network centrality as risk.
5. **Alert/claim co-occurrence** - a portion of claims preceded by prior alerts, with an intentionally incomplete (not 100%) overlap to preserve a genuine base-rate test.

## Deliberately Embedded Data-Quality Issues
Near-duplicate counterparty names, shared addresses/attributes from a limited string-generation space, missing registration numbers (~35% of non-GB counterparties), date-logic errors (~1% shipments, ~0.5% payments), and pure noise duplicates unrelated to any pattern - see `outputs/stage3_data_quality_audit/` for the independently-discovered audit of these issues.

## Validation
All Stage 4-9 findings in this repository were produced **without reference to** `ground_truth.json`. Its role is exclusively retrospective validation of methodology soundness, documented in project correspondence but not exposed here as it would compromise the "blind analysis" premise for anyone re-running this project as a learning exercise.
