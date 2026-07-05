# Stage 10 — Investigation Dashboard Build Plan
Design only. No dashboard built yet. All content sourced from Stage 9-approved/qualified claims only.

## 1. Dashboard Title and Intended User
**Title:** Northbridge Trade Integrity — Investigation Triage Dashboard (Fictional)
**Intended user:** Head of Financial Crime & Trade Integrity (primary); CRO/Underwriting Director/Board Risk Committee (executive summary view only, per Stage 0's audience definition).
**Purpose statement to display on the landing page:** "A review-prioritisation tool. Priority = review first, not confirmed wrongdoing. All figures are descriptive or statistical unless labelled otherwise."

## 2. Sheet/Page Structure
1. **Landing / Portfolio Baseline** — KPI cards, portfolio-level charts
2. **Priority Cases** — case priority table + evidence matrix (drill-through)
3. **Case Detail** — one page template, parameterised by case_id (CL-A, CL-B, CL-C, CL-D1/D2, CL-F, CL-G)
4. **Claim-Control Status** — the 8-claim register, visualised
5. **Network & Cluster Summary** — customer-counterparty and counterparty-counterparty views, INTM00038 clearance
6. **Evidence Gaps & Data Quality** — open gaps + DQ issue register
7. **Methodology & Limitations** (static, always-visible footer content duplicated here for reference)

## 3. KPI Cards (Landing Page)
| KPI | Value | Source stage |
|---|---|---|
| Total transactions | 6,000 | Stage 4/5 |
| Total portfolio value | £7.84B | Stage 4 |
| Portfolio alert rate | 16.0% | Stage 4/5 |
| Portfolio claim rate | 3.0% | Stage 4/5 |
| Open EDD-referral cases | 2 (CL-A, CL-B) | Stage 8/9 |
| Cases requiring more data | 1 (CL-C) | Stage 9 |
| Cases cleared as likely benign | 2 (CL-F: INTM00038; CL-G: CL003 cluster) | Stage 9 |
| Data-quality issues logged | 12 | Stage 3 |

Each KPI card must show: value, definition on hover, numerator/denominator, and a link to the source table. No KPI is a "risk score" — all are counts or rates.

## 4. Required Charts/Tables
**Landing page:**
- Bar: transactions by month (Stage 4, `1a_txn_by_year_month`)
- Bar: alert rate by corridor / by product category (Stage 4, `2c`/`2d`) — labelled "descriptive, not a risk ranking"
- Table: portfolio baseline by segment (Stage 5, `5b_baseline_segment`)

**Priority Cases page:**
- Table: Case priority table (see §9)
- Stacked bar: indicator contribution per case (from Stage 7 scoring breakdown — IND01/02/03-04/etc. as segments, capped visually at each indicator's max so no bar segment misleadingly dominates)

**Network & Cluster Summary page:**
- Node-link diagram: CL001 and CL002 clusters only (customer + 4 counterparties each) — NOT a full portfolio network graph, to avoid implying every node is under review
- Table: entity-resolution classification summary (STRONG/MEDIUM/WEAK counts, Stage 6)
- Callout box: INTM00038 clearance card (see §9 dedicated design)

**Claim-Control Status page:**
- Table: all 8 claims with status badges (Carry forward / Requires more data)
- No claim ever shown as "Confirmed" — the status vocabulary is limited to Stage 9's four categories

**Evidence Gaps page:**
- Table: evidence-gap register (Stage 8, `8d`)
- Table: DQ issue register (Stage 3, severity-coded)

## 5. Finding-to-Visual Map
| Finding (Stage 9 claim) | Visual | Page |
|---|---|---|
| CL-A: CUST00135/CL001 | Case row + detail page + network diagram | Priority Cases, Case Detail, Network |
| CL-B: CUST00070/CL002 | Case row + detail page + network diagram | Priority Cases, Case Detail, Network |
| CL-C: Value/weight set | Case row (band: "Requires more data") + specialist-review note | Priority Cases, Case Detail |
| CL-D: Third-party payer | KPI-level footnote only (2.0% of portfolio, capped weight) - NOT a standalone chart, to avoid overweighting per Stage 9 | Landing footnote |
| CL-E: Claim/prior-alert | Single descriptive chart (claim rate, alert vs no-alert) with "non-causal" label | Landing or Priority Cases |
| CL-F: INTM00038 | Dedicated clearance card | Network & Cluster Summary |
| CL-G: CL003 cluster | Row in evidence-gap/DQ table, NOT in priority case table | Evidence Gaps |
| CL-H: Framework design | Persistent footnote on every page showing a score | All scored pages |

## 6. Data Sources for Each Visual
All visuals point to a **validated summary layer**, never raw tables, per instruction:
- `stage4_outputs/*.csv` (SQL baselines) -> Landing KPIs/charts
- `stage5_outputs/5b_baseline_*.csv` -> Landing baseline table
- `stage6_outputs/6a_entity_resolution_pairs.csv`, `6b/6d_network_*.csv` -> Network page
- `stage7_outputs/7c_priority_*_level.csv` -> Priority Cases page
- `stage8_outputs/8b/8c/8d/8e_*.csv` -> Case Detail, evidence-gap tables
- `stage9_outputs/9b_claim_control_register.csv` -> Claim-Control Status page
- `data_quality_issues` table (Stage 3, logged Stage 4) -> Evidence Gaps page

No visual queries `transactions`, `payments`, `shipments`, or any raw analyst-facing table directly.

## 7. Filters/Slicers
- Segment (SME / Mid-market / Corporate)
- Corridor group
- Product category
- Priority band (High / Medium / Cleared / Requires more data) - **not** a numeric score slider, to discourage over-precision on an explainable-but-not-validated score
- Date range (2022-2024)
- Case status (Escalate / Continue monitoring / Requires more data / Closed benign)

Filters apply only to descriptive/baseline visuals; the 6 named cases (A/B/C/D1/D2/F/G-equivalent) remain fixed, individually-documented rows regardless of filter state, so a filter can never accidentally hide or fabricate a case.

## 8. Mandatory Footnotes and Warnings
- **Every page:** "This is a fictional portfolio project. All entities are synthetic. No finding constitutes evidence of wrongdoing."
- **Every scored visual:** "Priority score = review-ordering tool only. See Stage 7 indicator dictionary for full calculation logic."
- **Claim-Control page header:** "Status reflects testing performed to date, not a final determination."
- **CL-C section:** "Confound and data-quality explanations have been tested and ruled out. Product-specialist input is still required before this can be closed."
- **Network diagrams:** "Node proximity reflects a specific documented attribute (labelled on each edge). It does not imply relationship strength or common control beyond that attribute."

## 9. Case Priority Display Design
Table columns (fixed, no column ever hidden by a filter):
`Case ID | Subjects | Indicators Triggered | Priority Band | Confidence | Evidence Summary (1-line) | Plausible Innocent Explanation (1-line) | Decision Category | Link to full case file`

Priority Band uses **words, not colour-only red/amber/green** (colour is supplementary, not the sole encoding) to avoid a "traffic light = guilt" reading. Bands: **High priority for review / Medium priority / Requires more data / Cleared**. "High priority for review" is the ceiling label - the word "risk" alone is avoided as a column header.

**INTM00038 clearance card** (dedicated, in Network page not Priority Cases page, since it is cleared, not a case): shows degree share (66.5%), own alert/claim rate vs baseline (16.01%/3.04% vs 16.0%/3.0%), client-diversity stat (180/180 customers, 260/260 counterparties), and one line: "High volume alone was tested and did not meet the bar for review priority."

## 10. Evidence-Gap Display Design
Table: `Case ID | Gap Description | Why It Matters | How to Close | Category (Intelligence gap / Analytical gap - addressable now / None outstanding)`. Sorted with "None outstanding" (CL-F) always shown at the bottom as a positive contrast, not omitted.

## 11. Claim-Control Display Design
Table: `Claim ID | Claim Statement | Confidence Rating | Final Status | Link to full test detail`. Status badge vocabulary restricted to exactly: **Carry forward / Carry forward (capped) / Requires more data**. No "Confirmed," "Verified," or "True" badge exists in the design - even CL-F/CL-G's high-confidence clearances are labelled "Carry forward as documented clearance," not "Confirmed benign."

## 12. QA Checks Before Build
1. Every number on every visual traces to a specific Stage 4-9 output file - no manual re-entry.
2. Re-run Stage 4/5 control totals (row counts, alert/claim rates, reconciliation) against the summary layer immediately before build to confirm no drift.
3. Confirm no visual reads from a raw table (Section 6).
4. Confirm every scored visual displays alongside its evidence/alternative-explanation text, per CL-H's mandatory pairing rule - reject any layout that separates score from context onto different pages without a direct link.
5. Spell-check for banned words (Section 13) across all static text.
6. Confirm filters cannot hide the 6 fixed case rows (Section 7).
7. Confirm CL-C's specialist-review requirement is visible without drilling in (not buried three clicks deep).

## 13. What Not to Show or Say
- No use of "fraud," "guilty," "criminal," "sanctioned," "confirmed," "proven," or "suspicious" (unqualified) anywhere in the dashboard.
- No red/traffic-light colour used as the sole signal of a case's status without accompanying text.
- No portfolio-wide network graph showing all 260 counterparties (implies universal suspicion) - only the two named clusters are diagrammed.
- No display of priority score without its evidence/confidence/alternative-explanation context on the same view.
- No merging of CL003 (data-quality duplicates) into the same visual category as CL001/CL002 (genuine candidate clusters) - they must remain visually and categorically distinct.
- No implication that INTM00038's clearance is permanent - the "what would increase concern" condition (Stage 8) should appear in its detail view.

## 14. Recommended Build Format
**Combination:** validated summary tables in a lightweight SQLite/CSV layer (already built, Stages 4-9) feeding an **HTML/React artifact** for the interactive triage dashboard (best for the filter/drill-through behaviour and word-based priority bands described above), with an **Excel workbook** export of the same summary tables as a secondary, offline-shareable deliverable for the Board Risk Committee audience who may prefer static review. Power BI-style mockup is not recommended as the primary build target here since this is a portfolio artifact intended to run standalone; React/HTML avoids requiring a BI license to demonstrate.

---
DECISION: Adopt this structure as the Stage 10 build plan; no dashboard built yet.
EVIDENCE: This plan is a design document (Category N/A) - it makes no new analytical claims, only re-references Stage 9-approved/qualified claims.
ASSUMPTIONS: React/HTML is an acceptable primary format for a portfolio deliverable; the Board Risk Committee audience is comfortable with a static Excel companion rather than requiring live BI tooling.
RISKS: If build execution drifts from this plan (e.g. a developer adds a raw-table-connected chart under time pressure), the "no raw data behind executive charts" principle could be silently violated - the QA checklist (Section 12) exists specifically to catch this before ship.
UNRESOLVED QUESTIONS: Whether the Board Risk Committee view should be a fully separate simplified page or a filtered version of the same dashboard - recommend deciding this at build time based on final page count.
NEXT ACTION: Awaiting your approval of this build plan before proceeding to Stage 10 execution (actual dashboard build).
