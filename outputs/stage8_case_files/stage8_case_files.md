# Northbridge Trade Risk Investigation — Stage 8 Case Files
Fictional dataset. Analyst-facing data only. No ground truth consulted. No allegations made.

---

## CASE FILE A — CUST00135 + CL001 Counterparty Cluster (CPTY00002/45/148/156)

**B. Subject(s):** Customer CUST00135 (SME segment); counterparty cluster CPTY00002, CPTY00045, CPTY00148, CPTY00156.

**C. Why selected:** Highest Stage 7 priority score (9/10, High band). Selected via three independently-derived signals converging on the same subjects.

**D. Evidence summary:** CUST00135 conducted 38 transactions (£14.4M) over 2022–2024 — 100% of its recorded activity, entirely with these 4 counterparties, 0 transactions with any other counterparty. All 6 pairwise combinations within the cluster show a shared `bank_account_hash`; the cluster also shares one `registered_address`; 2 of 6 pairs additionally carry a declared `shared_director` relationship (source: regulatory_filing).

**E. Indicators triggered:** IND01 (alert concentration, customer alert rate 100%, p<10⁻³⁰), IND02 (exclusivity, 100% ≥95% threshold), IND03+IND04 (shared bank account + address/declared, Stage 6 STRONG classification).

**F. Transaction/value exposure:** 38 transactions, £14.4M total, 100% of customer's recorded volume.

**G. Alert exposure:** Customer-level 38/38 transactions alert-linked (100%); cluster counterparty-level alert rates range 46–53% individually (all statistically elevated above the 16% base rate, p<0.001 for each).

**H. Claim exposure:** 2 claims recorded against CPTY00002 within the cluster; 0 against the other three members.

**I. Entity-resolution evidence:** STRONG classification (Stage 6) — bank account is the primary linking attribute; does not match on contact_email/phone, which distinguishes it from the dataset's duplicate-data-entry signature pattern.

**J. Network evidence:** Direct transaction links (customer→each of 4 counterparties) are all first-degree, observed transactions — not inferred. The shared-bank-account link between counterparties is a direct attribute match, not a network-proximity inference.

**K. Plausible innocent explanations:** (i) Exclusive distributor/agency or franchise arrangement — legitimate for a small exporter to trade solely through one buyer group; (ii) the four counterparties may be legitimately related entities (subsidiaries/sister companies) sharing group treasury banking, which would explain both the shared bank account and the declared director relationship without implying anything about CUST00135's conduct; (iii) shared registered-agent/corporate-services provider producing the shared address independent of the banking link.

**L. Evidence supporting review priority:** Statistical robustness of the alert concentration (survives product-mix, corridor-mix, segment, and time controls per Stage 5); full transactional exclusivity is unusual relative to portfolio norms (median customer trades with several counterparties); convergence of three independently-computed signal types (monitoring alerts, network exclusivity, entity-resolution).

**M. Evidence reducing concern:** 2 of 6 cluster pairs have a *declared* (i.e. documented, not inferred) corporate relationship, which is consistent with a legitimate group structure rather than an undisclosed one; no sanctions-type indicators of any kind exist in this dataset; claim outcomes are low (2 of 38 transactions).

**N. Data-quality limitations:** Registration numbers are available for these counterparties (not part of the 38.4%-missing gap), which supports rather than limits resolution confidence here. No date-logic errors identified on this customer's own transactions specifically (not separately re-verified in this file — would require a targeted re-check).

**O. Confidence assessment:** High confidence in the *pattern* (statistically verified, network-confirmed, entity-resolution-confirmed). Low-to-none confidence in any interpretation of *cause* — the pattern is equally consistent with the innocent explanations in (K) as with any adverse hypothesis.

**P. What would increase concern:** Evidence that the "shared director" is a nominee/proxy rather than a genuine common owner; evidence the exclusive relationship began abruptly rather than reflecting a long-standing agency agreement; any documentary source (beyond this dataset) indicating the registered address is a mail-drop with no genuine operating presence.

**Q. What would reduce concern:** Confirmation (e.g. companies-house-equivalent lookup, outside this dataset's scope) that the four counterparties are formally registered subsidiaries of one holding company with normal group banking; confirmation the agency/distribution arrangement predates the observation window and is documented in a supply contract.

**R. Recommended next investigative step:** Request/obtain independent corporate registry confirmation of the counterparty cluster's ownership structure (outside this dataset); interview relationship manager for context on the nature of the customer relationship; do not take any action based on the data alone.

**S. Decision category: Escalate to EDD review** (highest Stage 7 priority; convergent evidence warrants a documented enhanced-due-diligence look, not an accusation).

---

## CASE FILE B — CUST00070 + CPTY00073/141/218/220 Cluster

**B. Subject(s):** Customer CUST00070 (SME); counterparty cluster CPTY00073, CPTY00141, CPTY00218, CPTY00220.

**C. Why selected:** Second-highest Stage 7 priority score (9/10, High band) — structurally identical pattern to Case File A, independently arising in a different part of the portfolio.

**D. Evidence summary:** 37 transactions (£14.0M), 100% of CUST00070's recorded activity, entirely with these 4 counterparties. All 6 pairs share `bank_account_hash` and `registered_address`; 1 of 6 pairs carries a declared `parent_subsidiary` relationship (source: declared, i.e. self-reported rather than regulatory-filing-sourced — a lower-reliability provenance than Case File A's regulatory_filing source).

**E. Indicators triggered:** IND01 (100% alert rate, p<10⁻²⁹), IND02 (100% exclusivity), IND03+IND04 (STRONG entity resolution).

**F. Transaction/value exposure:** 37 transactions, £14.0M, 100% of recorded customer volume.

**G. Alert exposure:** Customer-level 37/37 (100%); individual cluster counterparties range 33–49% alert rate.

**H. Claim exposure:** 5 claims across the cluster (higher count than Case File A, spread across 3 of 4 members).

**I. Entity-resolution evidence:** STRONG classification; does not match email/phone (rules out duplicate-entry explanation).

**J. Network evidence:** Direct, observed transaction links; direct attribute-match for shared banking.

**K. Plausible innocent explanations:** Same three categories as Case File A. Note the declared relationship here is self-reported (`source='declared'`), which is a weaker provenance than Case File A's regulatory-filing source — this should temper (not eliminate) the reassurance value of that declared link.

**L. Evidence supporting review priority:** Identical structural logic to Case File A; independently arising (different customer, different counterparties, no overlap between the two clusters per Stage 6 cross-check) — this strengthens the case that the *pattern type* (exclusive-cluster-plus-shared-banking) is a meaningful thing to look for in this portfolio, without saying anything about either specific case being confirmed.

**M. Evidence reducing concern:** A declared relationship exists (even if lower-provenance); no other indicator (value/weight mismatch, third-party payer) co-occurs with this cluster's transactions at an elevated rate beyond the alert signal itself.

**N. Data-quality limitations:** The `source='declared'` (self-reported) relationship carries lower evidentiary weight than a regulatory filing — flagged explicitly as a limitation of IND05 in the Stage 7 dictionary.

**O. Confidence assessment:** High confidence in the pattern; no confidence in cause.

**P. What would increase concern:** Same as Case File A; additionally, verification that the self-reported "parent_subsidiary" declaration cannot be corroborated by any independent filing.

**Q. What would reduce concern:** Independent corroboration of the parent-subsidiary declaration; evidence of a long-standing, documented distribution agreement.

**R. Recommended next investigative step:** Same as Case File A — independent corporate registry check; relationship-manager interview.

**S. Decision category: Escalate to EDD review.**

---

## CASE FILE C — Value/Weight Stable Anomaly Set (85 transactions)

**B. Subject(s):** 85 transactions spanning 67 distinct customers and 73 distinct counterparties (no concentration — max 3 transactions from any one customer, max 2 from any one counterparty).

**C. Why selected:** Only transactions flagged consistently across all three independent detection methods tested in Stage 5 (ratio-vs-category-average >5x, robust z-score >5, IQR k=3) — the most defensible subset given known threshold sensitivity (raw candidate counts ranged 22–157 depending on method/cut).

**D. Evidence summary:** Combined invoice value £122.3M across the 85 transactions. Alert rate for this set is 38.8% (vs 16.0% portfolio baseline) — meaningfully elevated. Claim rate 3.5% — close to baseline, not meaningfully elevated. Spread across 17 of 18 product categories (packaging, toys, food_agri, furniture, and textiles_finished contribute the most transactions, but none dominates — no single category exceeds 19% of the set).

**E. Indicators triggered:** IND06 only (value/weight implausibility, 2 points, capped).

**F. Transaction/value exposure:** 85 transactions, £122.3M combined.

**G. Alert exposure:** 38.8% vs 16.0% baseline — notably elevated, though this set was not independently robustness-tested against product/corridor/segment mix the way the customer-level alert finding was in Stage 5; that stratified test has not been performed for this specific transaction set and is an acknowledged gap.

**H. Claim exposure:** 3.5% vs 3.0% baseline — not meaningfully different from portfolio norm.

**I. Entity-resolution evidence:** Not applicable — no shared-attribute testing performed at transaction level for this set.

**J. Network evidence:** Not applicable — no customer/counterparty concentration found (spread evenly).

**K. Plausible innocent explanations:** Legitimate high-value/low-weight goods within a category that also contains bulkier low-value items (e.g. furniture spans flat-pack items to solid hardwood pieces at very different value-per-kg); unit or currency entry variance; premium/bespoke product variants; incomplete shipment weight capture inflating the apparent ratio for otherwise ordinary transactions.

**L. Evidence supporting review priority:** Stable under three independent statistical methods (not just one threshold's artifact); elevated alert rate for the set as a whole.

**M. Evidence reducing concern:** No customer/counterparty concentration (rules out a single bad actor driving this pattern); claim rate is normal; spread across nearly all product categories suggests a general data/valuation phenomenon rather than a targeted pattern.

**N. Data-quality limitations:** Value-per-kg is inherently noisy for categories with wide legitimate unit-value ranges (Stage 5 finding); this set has not been cross-checked against the Stage 3 date-logic-error log for overlap, which is a specific, addressable gap.

**O. Confidence assessment:** Medium confidence that this set contains genuine outliers worth product-specific review; low confidence that the outlier status reflects anything beyond ordinary category-level value variance, given the lack of customer/counterparty concentration.

**P. What would increase concern:** If a sub-cluster within these 85 shared a common counterparty or customer (currently absent); if product-specific manual review found the declared weight physically implausible for the stated goods description.

**Q. What would reduce concern:** Confirmation from a product specialist that the specific goods variant justifies the value/weight ratio (e.g. confirming premium vs standard-grade goods).

**R. Recommended next investigative step:** Route to product/trade-desk specialist review of a sample (not all 85) before any further prioritisation weight is assigned; do not treat threshold choice as settled.

**S. Decision category: Requires further data before decision** (specifically: product-specialist input on plausibility of declared value/weight combinations).

---

## CASE FILE D — Two Highest-Scoring Individual Transactions

**B. Subject(s):** TXN0004921 (CUST00117 / CPTY00137); TXN0003415 (CUST00104 / CPTY00185).

**C. Why selected:** Only two transactions in the portfolio reach the maximum observed transaction-level score (3/10) by combining two independent indicators each.

### D1. TXN0004921
**D. Evidence summary:** Furniture export, £2,521,419.14, 21-May-2024. Shipment: 6,257kg (value/weight ratio flagged in the Stage 5 stable set). One low-severity `documentation_gap` alert, disposition escalated. One claim: £2,150,446.99, reason `non-payment_by_buyer`, status paid.
**E. Indicators triggered:** IND06 (value/weight, 2 pts) + IND08 (claim with prior alert, 1 pt) = 3.
**F/G/H:** £2.52M exposure; 1 alert (low severity); 1 claim (paid, 85% of invoice value).
**K. Plausible innocent explanation:** Furniture category spans a very wide value range (flat-pack to solid hardwood/bespoke) — a legitimately high-value shipment at modest weight is plausible; the alert is a low-severity documentation gap, not a value-based flag; the claim reason (buyer non-payment) is a common, unremarkable trade-credit-insurance event unrelated to the value/weight observation.
**L/M:** Supporting: two independent indicators co-occur. Reducing: alert severity is low, not high; claim reason is a standard commercial dispute type, not indicative of the value/weight issue itself.
**N.** No date-logic error on this specific transaction's shipment/payment records (not separately re-verified here).
**O. Confidence:** Low-medium — two indicators co-occurring on one transaction is a small-sample coincidence risk (only 2 of 6,000 reach this combination).
**P/Q:** Increase: if the claim were denied specifically citing goods-value dispute. Decrease: confirmation of goods description/grade from shipment documentation.
**S. Decision: Continue monitoring** (illustrative combined-indicator case, insufficient standalone weight for EDD escalation).

### D2. TXN0003415
**D. Evidence summary:** Food/agricultural commodity import, £9,512.77, 11-Sep-2022. Shipment: 55,459kg — very low value-per-kg (£0.17/kg), 8.7x the category's realized average (in the low-value direction, i.e. unusually cheap per kg relative to category, not expensive — a distinct anomaly type from Case File C's typical high-ratio cases, though it registered on the same >5x deviation test). Payment made by an intermediary (third-party payer). One low-severity `third_party_payment` alert, disposition escalated. No claim.
**E. Indicators triggered:** IND06 (value/weight, 2 pts) + IND07 (third-party payer, 1 pt) = 3.
**F/G/H:** £9,512.77 exposure (immaterial in absolute terms); 1 alert; 0 claims.
**K. Plausible innocent explanation:** Bulk low-value agricultural commodity shipped at high weight is entirely ordinary (e.g. grain, bulk foodstuffs); third-party payment is standard factoring/treasury practice.
**L/M:** Supporting: two indicators co-occur. Reducing per Stage 5's explicit finding — **the alert here is circular** (alert_type='third_party_payment' simply restates the payment field, not independent corroboration); absolute value exposure is immaterial (£9.5k).
**N.** None identified specific to this transaction.
**O. Confidence:** Low — the value/weight signal here reflects a very ordinary bulk-commodity profile, and the "alert" is definitionally the same fact as IND07, so this is not truly two independent pieces of evidence.
**P/Q:** Increase: unlikely to increase without new evidence — this looks like a benign bulk-commodity transaction. Decrease: none needed; already low concern.
**S. Decision: Close as likely benign / data-quality artifact of the scoring rule** (illustrates why IND07-IND01 circularity matters — this case would score higher than it should if the framework hadn't already discounted it).

---

## CASE FILE E — INTM00038 Hub Clearance

**B. Subject:** Intermediary INTM00038 (freight_forwarder, Vietnam).

**C. Why selected:** Highest network centrality in the portfolio (66.5% of all distinct linked transactions) — exactly the profile that a naive, centrality-only approach would incorrectly flag as a risk hub. Included specifically to document why it is being **cleared**, not escalated.

**D. Evidence summary:** 3,360 of 9,600 transaction-intermediary bridge rows (35.0% of the table; 66.5% of distinct linked transactions). Touches all 180 customers and all 260 counterparties — the maximum possible diversity in this portfolio. Own alert rate: 16.01%. Own claim rate: 3.04%. Both are statistically indistinguishable from the portfolio-wide baseline (16.0% / 3.0%).

**E. Indicators triggered:** IND10 evaluated — gate condition (elevated own alert/claim rate) explicitly **fails**. **0 points scored.**

**F. Transaction/value exposure:** 3,360 distinct transactions touched — but this reflects service breadth, not concentration of risk-relevant activity.

**G. Alert exposure:** 16.01% — matches baseline exactly (portfolio 16.0%).

**H. Claim exposure:** 3.04% — matches baseline exactly (portfolio 3.0%).

**I. Entity-resolution evidence:** Not applicable — INTM00038 does not appear in any shared-attribute cluster from Stage 6.

**J. Network evidence:** Co-occurs with nearly every other intermediary in the portfolio (top intermediary-pair co-occurrence counts are all INTM00038 pairs) — consistent with a general-purpose logistics provider used across the client base, not a narrow circle of specific counterparties.

**K. Plausible innocent explanation (the leading explanation here, not an afterthought):** An ordinary large-scale freight-forwarder that happens to be Northbridge's most widely-used logistics partner. High volume is exactly what would be expected of the market-leading forwarder for this trade corridor.

**L. Evidence supporting further review:** None identified beyond raw volume, which by design is explicitly excluded from scoring in this framework.

**M. Evidence reducing concern:** Alert and claim rates identical to baseline despite massive volume; maximum customer/counterparty diversity (not serving a narrow client circle); no entity-resolution links to any flagged cluster.

**N. Data-quality limitations:** None specific to this intermediary identified.

**O. Confidence assessment:** High confidence this is an ordinary high-volume service provider, based on the convergence of (i) baseline-matching alert/claim rates and (ii) maximum-diversity client reach — both of which are the opposite of what a genuine risk hub would typically show.

**P. What would increase concern:** If a future data refresh showed its alert/claim rate rising above baseline, or if its customer/counterparty base narrowed toward a specific cluster (especially one already flagged, e.g. CL001/CL002).

**Q. What would reduce concern further:** Nothing further needed — already at the lowest concern level the framework supports.

**R. Recommended next investigative step:** None required. Document as a cleared node in the executive report specifically to demonstrate the methodology correctly avoided a centrality-as-risk false positive.

**S. Decision category: Close as likely benign** (explicitly on the basis of tested evidence, not simply "not flagged").

---
