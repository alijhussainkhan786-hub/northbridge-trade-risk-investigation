# Stage 0 — Investigation Brief and Analytical Questions

## Organisation and Scenario (Fictional)
Northbridge Trade Finance & Insurance Group — a fictional UK-based trade finance/trade-credit insurance provider serving SME and mid-market exporters/importers across UK, EU, Middle East, and Southeast Asia corridors. The project simulates a Financial Crime & Trade Integrity (FCTI) analytics function conducting a structured portfolio review.

## Trigger
Simulated portfolio-level trigger: a rise in trade-credit claims and alert escalations in a specific counterparty cluster/corridor prompted a structured analytical review — **not** a confirmed incident.

## Decision-Maker and Audience
Primary: Head of Financial Crime & Trade Integrity. Secondary: CRO, Underwriting Director, Board Risk Committee (executive summary only).

## Exact Objective
Identify, prioritise, and evidentially characterise transactions/entities meriting further investigation while strictly preserving the distinction between risk indicators, investigative hypotheses, and proof of wrongdoing.

## 12 Investigation Questions (summary)
1. Alert concentration by counterparty vs. volume
2. Value/timing/routing inconsistency vs. stated purpose
3. Hidden entity linkage between nominally distinct counterparties
4. Intermediary/destination concentration
5. Invoice/shipment/payment consistency
6. Claims vs. alert-history correlation
7. Alert-to-investigation conversion by segment
8. Proportion of flags with plausible innocent explanation
9. Threshold sensitivity of indicators
10. Base rate / false-positive expectation
11. Data quality/coverage gaps
12. Evidence required to escalate a case

## Initial Hypotheses (H1–H5) and Guardrails
Five hypotheses were defined (alert concentration, intermediary hub legitimacy, entity fragmentation, invoice/corridor clustering, claim/alert correlation), each paired with a plausible alternative explanation from the outset. Guardrails: fully synthetic data; planted patterns documented separately from analyst-facing data (see `ground_truth/`); risk indicators, priority, and evidence of wrongdoing kept as distinct categories throughout; no claim reaches a report without passing the Stage 9 Claim-Control Gate.

## Success Criteria
A defensible data model; reproducible SQL/Python pipelines; an explainable, false-positive-aware prioritisation framework; a network analysis distinguishing real hubs from artefacts; a claim-control process that catches unsupported findings; an executive report a real risk committee could act on without overclaiming.

Full detail of this stage is preserved in the project conversation history; this document summarises the governing brief referenced by all subsequent stages.
