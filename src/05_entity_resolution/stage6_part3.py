from pathlib import Path
import pandas as pd
OUT = "/home/claude/build/stage6_outputs"

# ---------------------------------------------------------------------------
# DELIVERABLE C: Cluster candidate table
# ---------------------------------------------------------------------------
clusters = [
    dict(cluster_id="CL001", members="CPTY00002, CPTY00045, CPTY00148, CPTY00156",
         linked_customer="CUST00135", linking_attribute="bank_account_hash (all 4 identical) + registered_address (all 4 identical); 2 of 6 pairs also have a declared shared_director relationship",
         link_type="DIRECT (transaction-confirmed) + DIRECT (attribute-confirmed)",
         txn_exposure="38 transactions, 100% of CUST00135's total activity, £14.4M",
         alert_exposure="27 of 38 txns alerted (71%); customer-level rate 100% (38/38, since alerts attach at transaction not counterparty level in this dataset -- see note)",
         claim_exposure="4 claims (2 on CPTY00002, 0 on others)",
         confidence="Medium-High", 
         innocent_explanation="Group restructuring, common registered-agent/corporate-service address, exclusive distributor/agency arrangement with a related corporate family",
         false_positive_risk="Medium - shared bank account is a stronger signal than address alone, but does not itself prove common beneficial control without further (non-SQL/pandas) verification"),
    dict(cluster_id="CL002", members="CPTY00073, CPTY00141, CPTY00218, CPTY00220",
         linked_customer="CUST00070", linking_attribute="bank_account_hash (all 4 identical) + registered_address (all 4 identical); 1 of 6 pairs also has a declared parent_subsidiary relationship",
         link_type="DIRECT (transaction-confirmed) + DIRECT (attribute-confirmed)",
         txn_exposure="37 transactions, 100% of CUST00070's total activity, £14.0M",
         alert_exposure="19 of 37 txns alerted directly; customer-level rate 100% (37/37)",
         claim_exposure="5 claims across the cluster",
         confidence="Medium-High",
         innocent_explanation="Same as CL001",
         false_positive_risk="Medium - same caveat as CL001"),
    dict(cluster_id="CL003", members="15 pairs incl. e.g. CPTY00009/CPTY00249, CPTY00072/CPTY00252, CPTY00236/CPTY00257 (+ 1 three-way group CPTY00097/99/254)",
         linked_customer="Not customer-specific - spread across many unrelated customers",
         linking_attribute="ALL of: bank_account_hash + registered_address + contact_email + contact_phone identical (+near-duplicate name for 3 pairs)",
         link_type="Not a transaction pattern - a DATA-QUALITY duplicate signature",
         txn_exposure="Not concentrated - these counterparties' transactions are unremarkable individually",
         alert_exposure="Not elevated as a group",
         claim_exposure="Not elevated as a group",
         confidence="High confidence this is DUPLICATE DATA ENTRY, not an investigative cluster",
         innocent_explanation="Same real-world entity recorded twice under a slightly different name/ID (classic onboarding duplicate)",
         false_positive_risk="Low risk of being a genuine risk cluster - matching on incidental fields (email/phone) that would not plausibly be shared by distinct legitimate entities is the discriminating signal"),
]
cluster_df = pd.DataFrame(clusters)
cluster_df.to_csv(f"{OUT}/6e_cluster_candidate_table.csv", index=False)
print(cluster_df.to_string(index=False))
