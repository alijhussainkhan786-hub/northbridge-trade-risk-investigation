from pathlib import Path
import pandas as pd
OUT = "/home/claude/build/stage6_outputs"

reg = pd.read_csv("/home/claude/build/stage5_outputs/5i_anomaly_candidate_register.csv")

updates = {
    "AC001": dict(
        evidence=reg.loc[reg.candidate_id=="AC001","evidence"].values[0] + "; NETWORK CONFIRMED: 100% of CUST00135's 38 transactions (100% of value, £14.4M) are with the 4-member CL001 counterparty cluster, and 0 transactions with any other counterparty",
        confidence="High (statistical + network convergence: alert concentration AND full transactional exclusivity to a shared-bank-account cluster)",
        recommended_next_stage="Stage 7 - highest analytical priority; explicitly test exclusive-distributor-agreement alternative before any escalation"),
    "AC002": dict(
        evidence=reg.loc[reg.candidate_id=="AC002","evidence"].values[0] + "; NETWORK CONFIRMED: 100% of CUST00070's 37 transactions (100% of value, £14.0M) are with the 4-member CL002 cluster, 0 with any other counterparty",
        confidence="High (same convergence pattern as AC001)",
        recommended_next_stage="Stage 7 - highest analytical priority; same alternative-explanation test as AC001"),
    "AC003": dict(
        evidence=reg.loc[reg.candidate_id=="AC003","evidence"].values[0] + "; Stage 6: classified STRONG (bank+address, 2 pairs +declared relationship); does NOT match on email/phone (distinguishes from duplicate-data-entry pattern CL003)",
        confidence="Medium-High -> confirmed by entity-resolution bucket analysis + exclusive transaction link to CUST00135",
        recommended_next_stage="Stage 7 prioritisation framework"),
    "AC004": dict(
        evidence=reg.loc[reg.candidate_id=="AC004","evidence"].values[0] + "; Stage 6: classified STRONG (bank+address, 1 pair +declared relationship); does NOT match email/phone",
        confidence="Medium-High -> confirmed by entity-resolution bucket analysis + exclusive transaction link to CUST00070",
        recommended_next_stage="Stage 7 prioritisation framework"),
}
for cid, upd in updates.items():
    for k,v in upd.items():
        reg.loc[reg.candidate_id==cid, k] = v

# New candidate: intermediary hub CLEARED
new_row = dict(candidate_id="AC008", subject_type="intermediary", subject_id="INTM00038",
    anomaly_type="INTERMEDIARY_CONCENTRATION",
    evidence="66.5% share of transaction-intermediary bridge rows (3,360/9,600); touches all 180 customers and all 260 counterparties (max possible diversity); alert rate 16.01% and claim rate 3.04%, statistically indistinguishable from portfolio baseline (16.0%/3.0%)",
    baseline_comparison="Portfolio-wide alert/claim rates",
    severity_priority="CLEARED - do not prioritise for Stage 7",
    confidence="High confidence this is an ordinary large-scale freight-forwarder, not a risk hub",
    false_positive_risk="N/A (this is a clearance, not a flagged candidate) - the false-positive risk being avoided is treating graph centrality as risk by itself",
    recommended_next_stage="Document as a cleared/negative finding in Stage 7 - explicitly explain why high degree != risk here (uniform customer/counterparty diversity + baseline-matching alert/claim rates)")
reg = pd.concat([reg, pd.DataFrame([new_row])], ignore_index=True)

# New candidate: CL003 duplicate cluster explicitly downgraded/closed
new_row2 = dict(candidate_id="AC009", subject_type="counterparty_cluster", subject_id="15 pairs incl. CPTY00009/249, CPTY00072/252, CPTY00236/257 etc. (CL003)",
    anomaly_type="SHARED_ATTRIBUTE (all fields incl. email/phone)",
    evidence="Matches on bank+address+email+phone (+name for 3 pairs) - i.e. every generated field matches, including incidental fields unlikely to be shared by genuinely distinct entities",
    baseline_comparison="N/A",
    severity_priority="DOWNGRADED to data-quality remediation, not an investigative candidate",
    confidence="High confidence this is duplicate data entry, not a risk pattern",
    false_positive_risk="Low risk of being a true risk cluster given the all-fields-match signature",
    recommended_next_stage="Route to data-quality deduplication (Stage 3 issue register), not Stage 7 risk prioritisation")
reg = pd.concat([reg, pd.DataFrame([new_row2])], ignore_index=True)

reg.to_csv(f"{OUT}/6f_updated_anomaly_candidate_register.csv", index=False)
print(reg[["candidate_id","subject_type","subject_id","severity_priority","confidence"]].to_string(index=False))
