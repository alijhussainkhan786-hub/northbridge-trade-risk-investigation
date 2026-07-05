# Stage 9 — Claim-Control and Robustness Gate: Summary

## C. Robustness Summary
All 8 major claims re-tested per the Claim-Control Gate procedure (independent recalculation, alternative denominators, sample-size check, threshold sensitivity, confounder search, contradictory-evidence search). Full detail in `9b_claim_control_register.csv`. No claim was found unsupported outright; all either carry forward as-is, carry forward with an explicit caveat/cap, or remain open pending external data.

## D. Claims Approved for Dashboard/Report (carry forward)
- **CL-A** — CUST00135/CL001 EDD referral (High statistical confidence, low cause-confidence — report as "review priority," not a finding)
- **CL-B** — CUST00070/CL002 EDD referral (same, with explicit lower-provenance caveat on its declared relationship)
- **CL-D** — Third-party payer indicator, capped low weight, circularity documented
- **CL-E** — Claim/prior-alert relationship, labelled non-causal, Corporate segment excluded from headline figures
- **CL-F** — INTM00038 clearance (documented negative finding, not silently dropped)
- **CL-G** — CL003 duplicate cluster (routed to data-quality remediation, removed from investigative lists)
- **CL-H** — Priority-score framework design claim (mandatory pairing of score with evidence/alternative-explanation columns in any display)

## E. Claims Downgraded or Requiring More Data
- **CL-C** — Case C value/weight set: **remains "Requires more data"** — narrowed this session from a general gap to one specific remaining question (product-specialist plausibility review), with confound and DQ explanations now actively ruled out rather than merely untested. Confidence raised from Stage 8's unqualified "Medium" to "Medium, with the confound-ruled-out basis now stated explicitly," but capped pending the specialist input and the newly-identified partial alert-circularity caveat.

No claim was removed outright in this pass — all 8 survived testing in some form, though CL-C's status remains the least resolved.

## F. Remaining Limitations (portfolio-wide)
1. **CL-C** cannot be closed without external product-specialist input — outside this dataset's scope.
2. **CL-A/CL-B** cannot be confirmed or refuted as to cause (legitimate group structure vs. undisclosed control) without external corporate-registry data — outside this dataset's scope by design (fictional project boundary).
3. Declared-relationship provenance (`source` field) is not differentially weighted in the current framework despite a demonstrated reliability difference between CL-A and CL-B — a known framework gap, not yet remediated.
4. Small-n sub-strata (Corporate segment, several corridor cells) throughout the project limit confidence in any figure computed at that granularity — these are consistently flagged rather than reported as if robust.
5. This is a fictional, synthetic dataset with programmatically-planted patterns; no finding in this project should be read as a statement about any real entity, individual, or organisation.
