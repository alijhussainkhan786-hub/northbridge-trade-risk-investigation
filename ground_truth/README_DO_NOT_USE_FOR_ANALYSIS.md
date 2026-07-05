# ⚠️ VALIDATION-ONLY — DO NOT USE FOR ANALYSIS

`ground_truth.json` in this folder is a **Category 8 (Simulated ground truth)** artefact created solely to validate, after the fact, whether the analytical pipeline (Stages 4–8) correctly recovered the patterns deliberately planted during synthetic data generation (Stage 2).

**Rules governing this folder:**
1. This file was **never** consulted during Stages 3–9 analysis. Every finding in `outputs/` was derived independently from the analyst-facing data in `data/` only.
2. It must **not** be joined, merged, or cross-referenced with any file in `data/` or `outputs/` in downstream use of this repository.
3. It exists **only** to demonstrate, transparently, that the project's methodology can recover known planted patterns — this is a methodology-validation artefact, not an investigative input.
4. No entity ID, cluster label, or pattern description from this file appears anywhere in `README.md`, `docs/`, `outputs/`, or `dashboard/`.
5. If you are extending this project, do not read this file before performing your own independent analysis, or you will contaminate the exercise the same way consulting an answer key would invalidate a test.

See `docs/02_synthetic_data_specification.md` for the full planted-pattern design methodology (pattern types, injection rates) without exposing specific IDs.
