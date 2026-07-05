# Stage 12 — Final QA Report

Performed against the built repository at northbridge-trade-risk-investigation/ prior to archiving.

## 1. Structural Integrity
- 135 files across README, LICENSE, docs/ (9 files), data/ (17 files), ground_truth/ (2 files), src/ (31 scripts across 7 stage-organised subfolders), outputs/ (8 subfolders, ~90 files), dashboard/ (2 files), manifest/ (2 files).
- No working-cache artefact (txn_enriched.pkl) shipped - confirmed removed from the package (it is a local build intermediate, regenerated per docs/reproducibility_guide.md).
- No duplicate filenames anywhere in the repository (automated check, see qa_audit.py logic below).

## 2. Ground-Truth Isolation (critical control)
- ground_truth.json exists only in ground_truth/, not duplicated into data/.
- Automated scan for ground-truth-exclusive entity/transaction IDs (i.e. IDs appearing in ground_truth.json but nowhere in the already-approved Stage 7-9 outputs) across README.md, docs/, dashboard/, and manifest/: zero exposures found. IDs that legitimately appear in both (e.g. CUST00135, CUST00070, INTM00038 - all publicly documented in approved Stage 8/9 case files) are expected and are not a leak, since they were already disclosed as named cases, not derived from the hidden file.
- ground_truth/README_DO_NOT_USE_FOR_ANALYSIS.md present and explicit.

## 3. Vocabulary and Framing
- Automated scan for the prohibited accusatory and determination vocabulary defined in `src/08_qa/qa_audit.py` across all public-facing documents: zero matches.
- Manually re-confirmed (this session) that INTM00038 is preserved as an explicit clearance (README Key Results, dashboard Network page, executive assessment) - not silently omitted.
- Manually re-confirmed the 15-pair duplicate cluster is preserved as data-quality remediation language throughout (README, findings summary, executive assessment) - never presented as an investigative lead.
- Manually re-confirmed Case C's "requires product-specialist input" framing is present in README, findings summary, and executive assessment - not silently dropped or upgraded to a decision.

## 4. Numerical Reconciliation
- Transaction count (6,000), alert rate (16.0%), and claim rate (3.0%) verified by direct query against data/northbridge.db and cross-checked against README.md and outputs/stage11_executive_assessment.md - all reconcile exactly.
- Case A/B transaction counts (38, 37) and priority scores (9/10) verified directly against outputs/stage7_prioritisation_framework/7c_priority_customer_level.csv - match all narrative documents referencing them.
- data_quality_issues table row count (12) verified against the register and the Stage 3 audit report.

## 5. Editorial Correction Applied
- Confirmed: "using a 10-stage analytical methodology" replaced with "using a staged analytical methodology" in outputs/stage11_executive_assessment.md, per the approved correction. No other wording, number, case decision, or recommendation was altered.

## 6. Path Integrity
- All file paths referenced in README.md resolve to existing files within the package.

## 7. Content Verification Method (transparency note)
Every check above was performed by either (a) directly querying data/northbridge.db with SQL, (b) running an automated Python scan (qa_audit.py) against the actual file contents, or (c) opening and reading the specific file section referenced. No check in this report is based on an assumption that a file "should" contain something without confirming it actually does.

## 8. Outstanding Items (not blocking, documented for transparency)
- Source scripts now resolve repository paths dynamically using pathlib.Path; no local OUT_DIR source edit is required.
- Stage 0-2 documents (docs/00_investigation_brief.md, 01_data_model.md, 02_synthetic_data_specification.md) are reconstructed summaries of approved conversation content rather than files that existed natively during those stages - noted for transparency, content matches what was approved at the time.

## Overall Result: PASS - repository approved for archiving.
