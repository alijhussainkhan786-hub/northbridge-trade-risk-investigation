from pathlib import Path
"""
Northbridge Trade Risk Investigation - Stage 2B Controlled Synthetic Data Generation
Fictional portfolio project. No real entities, no real cases.
Seed = 42 for full reproducibility.
"""
import numpy as np
import pandas as pd
import sqlite3
import os
import json
import hashlib
from datetime import date, timedelta

SEED = 42
rng = np.random.default_rng(SEED)

OUT_DIR = str(Path(__file__).resolve().parents[3])
CSV_DIR = os.path.join(OUT_DIR, "csv_exports")
GT_DIR = os.path.join(OUT_DIR, "ground_truth")
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(GT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 0. REFERENCE / HELPER DATA
# ---------------------------------------------------------------------------

WINDOW_START = date(2022, 1, 1)
WINDOW_END = date(2024, 12, 31)
WINDOW_DAYS = (WINDOW_END - WINDOW_START).days

def rand_date(start, end, n=1):
    delta = (end - start).days
    offsets = rng.integers(0, delta + 1, size=n)
    return [start + timedelta(days=int(o)) for o in offsets]

FIRST_WORDS = ["Meridian","Ashford","Blue Anchor","Northfield","Crestline","Silverline","Oakbridge",
    "Harborview","Kestrel","Redwood","Amber","Vantage","Coldwell","Ironwood","Brightwater",
    "Fenwick","Delta","Marlow","Copperfield","Highgate","Westbrook","Larkspur","Stonebridge",
    "Falcon","Greystone","Rosewood","Wintercroft","Sable","Thornfield","Elmsworth"]
SECOND_WORDS = ["Trading","Textiles","Logistics","Overseas","Commodities","Freight","Imports",
    "Exports","Manufacturing","Distribution","Industries","Group","Holdings","Supplies","Global"]
SUFFIXES_UK = ["Ltd","Limited","LLP"]
SUFFIXES_INTL = ["LLC","FZE","Pte Ltd","Sdn Bhd","GmbH","SA","Inc","Co"]

def make_name(rgen, suffix_pool):
    return f"{rgen.choice(FIRST_WORDS)} {rgen.choice(SECOND_WORDS)} {rgen.choice(suffix_pool)}"

# Countries / corridor design (Section 5)
COUNTRIES = [
    # (code, name, region, corridor)
    ("DE","Germany","Europe","Corridor_A"),("FR","France","Europe","Corridor_A"),
    ("NL","Netherlands","Europe","Corridor_A"),("IE","Ireland","Europe","Corridor_A"),
    ("IT","Italy","Europe","Corridor_A"),("ES","Spain","Europe","Corridor_A"),
    ("GB","United Kingdom","Europe","Corridor_B"),
    ("AE","United Arab Emirates","Middle East","Corridor_C"),
    ("SA","Saudi Arabia","Middle East","Corridor_C"),
    ("QA","Qatar","Middle East","Corridor_C"),
    ("SG","Singapore","Southeast Asia","Corridor_D"),
    ("MY","Malaysia","Southeast Asia","Corridor_D"),
    ("VN","Vietnam","Southeast Asia","Corridor_D"),
    ("TH","Thailand","Southeast Asia","Corridor_D"),
    ("NG","Nigeria","Sub-Saharan Africa","Corridor_E"),
    ("KE","Kenya","Sub-Saharan Africa","Corridor_E"),
    ("GH","Ghana","Sub-Saharan Africa","Corridor_E"),
    ("US","United States","Other","Corridor_F"),("CA","Canada","Other","Corridor_F"),
    ("BR","Brazil","Other","Corridor_F"),("AU","Australia","Other","Corridor_F"),
    ("PL","Poland","Europe","Corridor_F"),("PT","Portugal","Europe","Corridor_F"),
    ("TR","Turkey","Other","Corridor_F"),("EG","Egypt","Other","Corridor_F"),
    ("ZA","South Africa","Sub-Saharan Africa","Corridor_F"),
    ("IN","India","Other","Corridor_F"),("CN","China","Other","Corridor_F"),
    ("JP","Japan","Other","Corridor_F"),("KR","South Korea","Other","Corridor_F"),
]
destinations = pd.DataFrame(COUNTRIES, columns=["country_id","country_name","region","corridor_group"])
assert len(destinations) == 30

# Products (Section 7) - 18 categories, generic non-controlled goods
PRODUCTS = [
    ("textiles_finished","Textiles - finished garments","HS61",5,45,0.3,2.0),
    ("textiles_raw","Textiles - raw/unfinished fabric","HS52",2,15,0.5,3.0),
    ("electronics_components","Electronics - components","HS8541",1,120,0.01,5.0),
    ("electronics_consumer","Electronics - consumer goods","HS8517",20,400,0.2,3.0),
    ("machinery_parts","Machinery parts","HS8483",10,300,1.0,50.0),
    ("machinery_industrial","Industrial machinery","HS8479",500,15000,50.0,2000.0),
    ("food_agri","Food & agricultural commodities","HS1006",0.3,3,1.0,1000.0),
    ("beverages","Beverages (non-alcoholic)","HS2202",0.5,4,0.5,20.0),
    ("chemicals_generic","Chemicals - generic industrial","HS3824",1,25,1.0,500.0),
    ("building_materials","Building materials","HS6810",0.2,8,5.0,2000.0),
    ("furniture","Furniture","HS9403",30,900,5.0,80.0),
    ("packaging","Packaging materials","HS4819",0.1,5,1.0,500.0),
    ("automotive_parts","Automotive parts","HS8708",5,600,0.2,40.0),
    ("pharma_generic","Pharmaceuticals - generic OTC","HS3004",2,60,0.05,1.0),
    ("toys","Toys & consumer leisure","HS9503",2,50,0.1,5.0),
    ("footwear","Footwear","HS6403",8,90,0.2,1.5),
    ("plastics_raw","Plastics - raw materials","HS3901",0.8,3,1.0,1000.0),
    ("paper_products","Paper products","HS4802",0.3,4,1.0,1000.0),
]
products = pd.DataFrame(PRODUCTS, columns=["product_category","product_label","hs_code_group",
    "typical_unit_value_min","typical_unit_value_max","typical_weight_min_kg","typical_weight_max_kg"])
products.insert(0, "product_id", [f"PROD{str(i+1).zfill(4)}" for i in range(len(products))])
assert len(products) == 18

print("Reference tables built:", len(destinations), "destinations,", len(products), "products")

# ---------------------------------------------------------------------------
# 1. CUSTOMERS (180)
# ---------------------------------------------------------------------------
N_CUST = 180
SEGMENT_PROBS = [0.65, 0.28, 0.07]  # SME, Mid-market, Corporate
segments = rng.choice(["SME","Mid-market","Corporate"], size=N_CUST, p=SEGMENT_PROBS)
cust_ids = [f"CUST{str(i+1).zfill(5)}" for i in range(N_CUST)]
onboarding_dates = rand_date(date(2015,1,1), date(2023,6,30), N_CUST)

customers = pd.DataFrame({
    "customer_id": cust_ids,
    "legal_name": [make_name(rng, SUFFIXES_UK) for _ in range(N_CUST)],
    "registration_number": [f"UK{rng.integers(10000000,99999999)}" for _ in range(N_CUST)],
    "incorporation_country": "GB",
    "segment": segments,
    "onboarding_date": onboarding_dates,
    "registered_address": [f"{rng.integers(1,200)} {rng.choice(['High St','Kings Rd','Mill Lane','Station Ave','Park Row'])}, UK" for _ in range(N_CUST)],
    "primary_contact_email": [f"contact{i+1}@customer{i+1}.co.uk" for i in range(N_CUST)],
    "primary_contact_phone": [f"+44 20 {rng.integers(1000,9999)} {rng.integers(1000,9999)}" for _ in range(N_CUST)],
    "relationship_manager": rng.choice(["A. Whitfield","M. Osei","J. Carrington","R. Nakamura","S. Bello","T. Ferreira"], size=N_CUST),
})

# ---------------------------------------------------------------------------
# 2. COUNTERPARTIES (260, including 15 noise duplicates)
# ---------------------------------------------------------------------------
N_CPTY_BASE = 245
country_pool = destinations["country_id"].tolist()
cpty_countries = rng.choice(country_pool, size=N_CPTY_BASE)
cpty_ids = [f"CPTY{str(i+1).zfill(5)}" for i in range(N_CPTY_BASE)]

cpty_names = []
for c in cpty_countries:
    suffix_pool = SUFFIXES_UK if c == "GB" else SUFFIXES_INTL
    cpty_names.append(make_name(rng, suffix_pool))

entity_types = rng.choice(["buyer","supplier","agent"], size=N_CPTY_BASE, p=[0.55,0.40,0.05])
first_seen = rand_date(date(2020,1,1), date(2024,10,1), N_CPTY_BASE)

def make_bank_hash(seed_str):
    return hashlib.sha256(seed_str.encode()).hexdigest()[:16]

reg_numbers = []
addresses = []
bank_hashes = []
for i in range(N_CPTY_BASE):
    is_gb = cpty_countries[i] == "GB"
    if is_gb:
        reg = f"UK{rng.integers(10000000,99999999)}"
    else:
        reg = None if rng.random() < 0.35 else f"{cpty_countries[i]}{rng.integers(100000,999999)}"
    reg_numbers.append(reg)
    addresses.append(f"Unit {rng.integers(1,50)}, {rng.choice(['Industrial Zone','Free Trade Ave','Harbour Rd','Commerce Blvd'])}, {cpty_countries[i]}")
    bank_hashes.append(make_bank_hash(f"{cpty_ids[i]}-{i}"))

counterparties = pd.DataFrame({
    "counterparty_id": cpty_ids,
    "legal_name": cpty_names,
    "registration_number": reg_numbers,
    "country": cpty_countries,
    "entity_type": entity_types,
    "first_seen_date": first_seen,
    "registered_address": addresses,
    "contact_email": [f"info{i+1}@cpty{i+1}.com" for i in range(N_CPTY_BASE)],
    "contact_phone": [f"+{rng.integers(1,99)} {rng.integers(100,999)} {rng.integers(1000,9999)}" for _ in range(N_CPTY_BASE)],
    "bank_account_hash": bank_hashes,
})

dup_source_idx = rng.choice(N_CPTY_BASE, size=15, replace=False)
dup_rows = counterparties.iloc[dup_source_idx].copy()
new_dup_ids = [f"CPTY{str(N_CPTY_BASE + i + 1).zfill(5)}" for i in range(15)]
dup_rows["counterparty_id"] = new_dup_ids
dup_rows["legal_name"] = dup_rows["legal_name"].apply(lambda n: n.replace("Ltd","Limited").replace("LLC","L.L.C.") if ("Ltd" in n or "LLC" in n) else n + " (2)")
counterparties = pd.concat([counterparties, dup_rows], ignore_index=True)
assert len(counterparties) == 260, len(counterparties)

# ---------------------------------------------------------------------------
# 3. INTERMEDIARIES (45)
# ---------------------------------------------------------------------------
N_INTM = 45
intm_ids = [f"INTM{str(i+1).zfill(5)}" for i in range(N_INTM)]
intm_countries = rng.choice(country_pool, size=N_INTM)
intm_roles = rng.choice(["freight_forwarder","agent","correspondent_bank","payment_processor"], size=N_INTM, p=[0.45,0.25,0.20,0.10])
intm_first_seen = rand_date(date(2018,1,1), date(2024,6,1), N_INTM)

intermediaries = pd.DataFrame({
    "intermediary_id": intm_ids,
    "legal_name": [make_name(rng, SUFFIXES_INTL if intm_countries[i] != "GB" else SUFFIXES_UK) for i in range(N_INTM)],
    "role_type": intm_roles,
    "country": intm_countries,
    "first_seen_date": intm_first_seen,
    "contact_email": [f"ops{i+1}@intermediary{i+1}.com" for i in range(N_INTM)],
})

ff_idx = intermediaries.index[intermediaries["role_type"] == "freight_forwarder"].tolist()
HUB_INTERMEDIARY_ID = intermediaries.loc[rng.choice(ff_idx), "intermediary_id"]

print("Customers:", len(customers), "| Counterparties:", len(counterparties), "| Intermediaries:", len(intermediaries))
print("Pattern 4 decoy hub intermediary:", HUB_INTERMEDIARY_ID)

# ---------------------------------------------------------------------------
# PATTERN 1 - Counterparty Fragmentation (2 clusters x 4 counterparties, 2 customers)
# Ground truth only: which counterparties/customers are involved.
# Analyst-facing signal: shared address/bank_account_hash across "distinct" counterparties,
# collectively representing high share of one customer's export volume.
# ---------------------------------------------------------------------------
non_dup_idx = counterparties.index[counterparties["counterparty_id"].isin(cpty_ids)].tolist()
cluster_choice = rng.choice(non_dup_idx, size=8, replace=False)
cluster_A_idx = cluster_choice[:4]
cluster_B_idx = cluster_choice[4:8]

shared_addr_A = "Unit 7, Sheikh Zayed Business Centre, AE"
shared_bank_A = make_bank_hash("PATTERN1-CLUSTER-A")
shared_addr_B = "Level 3, Marina Commercial Tower, SG"
shared_bank_B = make_bank_hash("PATTERN1-CLUSTER-B")

for idx in cluster_A_idx:
    counterparties.loc[idx, "registered_address"] = shared_addr_A
    counterparties.loc[idx, "bank_account_hash"] = shared_bank_A
    counterparties.loc[idx, "country"] = "AE"
for idx in cluster_B_idx:
    counterparties.loc[idx, "registered_address"] = shared_addr_B
    counterparties.loc[idx, "bank_account_hash"] = shared_bank_B
    counterparties.loc[idx, "country"] = "SG"

pattern1_cpty_A = counterparties.loc[cluster_A_idx, "counterparty_id"].tolist()
pattern1_cpty_B = counterparties.loc[cluster_B_idx, "counterparty_id"].tolist()

# The two customers whose export volume will be concentrated through these clusters (assigned later at txn gen)
pattern1_customers = list(rng.choice(cust_ids, size=2, replace=False))

# ---------------------------------------------------------------------------
# ENTITY_ATTRIBUTES (1,400 rows) - feeds entity resolution (Stage 6)
# Includes the Pattern 1 shared attributes (already embedded above) plus general
# attribute rows for a sample of entities, plus deliberate formatting-only near-duplicates
# (noise, unrelated to any pattern).
# ---------------------------------------------------------------------------
attr_rows = []
attr_counter = 1

def add_attr(entity_id, entity_type, attribute_type, value, src_date):
    global attr_counter
    attr_rows.append({
        "attribute_id": f"ATTR{str(attr_counter).zfill(6)}",
        "entity_id": entity_id, "entity_type": entity_type,
        "attribute_type": attribute_type, "attribute_value": value,
        "source_date": src_date,
    })
    attr_counter += 1

# Pattern 1 explicit attribute rows (address + bank_account) for the 8 clustered counterparties
for cid in pattern1_cpty_A:
    add_attr(cid, "counterparty", "registered_address", shared_addr_A, date(2023,1,15))
    add_attr(cid, "counterparty", "bank_account", shared_bank_A, date(2023,1,15))
for cid in pattern1_cpty_B:
    add_attr(cid, "counterparty", "registered_address", shared_addr_B, date(2023,3,10))
    add_attr(cid, "counterparty", "bank_account", shared_bank_B, date(2023,3,10))

# General attribute population: sample entities and log address/phone/email attributes
all_entities = (
    [(c, "customer") for c in customers["customer_id"]] +
    [(c, "counterparty") for c in counterparties["counterparty_id"]] +
    [(c, "intermediary") for c in intermediaries["intermediary_id"]]
)
n_general_needed = 1400 - len(attr_rows)
sampled_entities = [all_entities[i] for i in rng.choice(len(all_entities), size=n_general_needed, replace=True)]
attr_types = ["address","phone","email","registered_agent"]
for eid, etype in sampled_entities:
    atype = rng.choice(attr_types)
    if atype == "address":
        val = f"{rng.integers(1,300)} {rng.choice(['Commerce Rd','Trade St','Harbour Way','Dock Ln'])}"
    elif atype == "phone":
        val = f"+{rng.integers(1,99)} {rng.integers(1000000,9999999)}"
    elif atype == "email":
        val = f"contact{rng.integers(1000,9999)}@{eid.lower()}.com"
    else:
        val = rng.choice(["Formation Agents Ltd","Global Registrars Inc","Corporate Nominee Services"])
    add_attr(eid, etype, atype, val, rand_date(date(2020,1,1), date(2024,12,1), 1)[0])

entity_attributes = pd.DataFrame(attr_rows)
assert len(entity_attributes) == 1400, len(entity_attributes)

# ---------------------------------------------------------------------------
# ENTITY_RELATIONSHIPS (70 declared edges) - explicit/documented links only.
# A minority overlap with Pattern 1 (declared corporate link corroborating the
# fragmentation cluster) to allow Stage 6 to test declared-vs-inferred convergence;
# most are unrelated ordinary declared relationships (shared director etc.)
# ---------------------------------------------------------------------------
rel_rows = []
rel_counter = 1

def add_rel(e1, t1, e2, t2, rel_type, source, confidence):
    global rel_counter
    rel_rows.append({
        "relationship_id": f"REL{str(rel_counter).zfill(6)}",
        "entity_id_1": e1, "entity_type_1": t1, "entity_id_2": e2, "entity_type_2": t2,
        "relationship_type": rel_type, "source": source, "confidence": confidence,
    })
    rel_counter += 1

# 3 declared links within cluster A (not all 4, to reflect imperfect documentation)
for i in range(3):
    add_rel(pattern1_cpty_A[i], "counterparty", pattern1_cpty_A[i+1], "counterparty",
             "shared_director", "regulatory_filing", "high")
# 2 declared links within cluster B
add_rel(pattern1_cpty_B[0], "counterparty", pattern1_cpty_B[1], "counterparty",
         "shared_director", "regulatory_filing", "high")
add_rel(pattern1_cpty_B[2], "counterparty", pattern1_cpty_B[3], "counterparty",
         "parent_subsidiary", "declared", "medium")

# Remaining 65 ordinary declared relationships, randomly distributed, unrelated to any pattern
rel_types = ["shared_director","parent_subsidiary","shared_address","shared_registered_agent"]
sources = ["declared","regulatory_filing"]
for _ in range(70 - len(rel_rows)):
    kind = rng.choice(["cust-cpty","cpty-cpty","intm-cpty"])
    if kind == "cust-cpty":
        e1, t1 = rng.choice(cust_ids), "customer"
        e2, t2 = rng.choice(counterparties["counterparty_id"]), "counterparty"
    elif kind == "cpty-cpty":
        pair = rng.choice(counterparties["counterparty_id"], size=2, replace=False)
        e1, t1, e2, t2 = pair[0], "counterparty", pair[1], "counterparty"
    else:
        e1, t1 = rng.choice(intm_ids), "intermediary"
        e2, t2 = rng.choice(counterparties["counterparty_id"]), "counterparty"
    add_rel(e1, t1, e2, t2, rng.choice(rel_types), rng.choice(sources), rng.choice(["high","medium","low"]))

entity_relationships = pd.DataFrame(rel_rows)
assert len(entity_relationships) == 70, len(entity_relationships)

print("Entity_Attributes:", len(entity_attributes), "| Entity_Relationships:", len(entity_relationships))
print("Pattern 1 clusters -> A:", pattern1_cpty_A, "B:", pattern1_cpty_B, "| customers:", pattern1_customers)

# ---------------------------------------------------------------------------
# 4. TRANSACTIONS (6,000)
# ---------------------------------------------------------------------------
N_TXN = 6000
txn_ids = [f"TXN{str(i+1).zfill(7)}" for i in range(N_TXN)]

cust_lookup = customers.set_index("customer_id")
seg_of = cust_lookup["segment"].to_dict()

# Base random assignment
txn_customers = rng.choice(cust_ids, size=N_TXN,
                            p=None)  # uniform draw first, will overweight pattern1 customers below
txn_counterparties = rng.choice(counterparties["counterparty_id"], size=N_TXN)
txn_products = rng.choice(products["product_id"], size=N_TXN)
txn_destcountry = rng.choice(country_pool, size=N_TXN)
txn_dates = rand_date(WINDOW_START, WINDOW_END, N_TXN)
directions = rng.choice(["export","import"], size=N_TXN, p=[0.6,0.4])
incoterms = rng.choice(["FOB","CIF","EXW","DAP","FCA"], size=N_TXN)
currencies = rng.choice(["GBP","USD","EUR"], size=N_TXN, p=[0.5,0.35,0.15])

# Product value lookup for plausible invoice values
prod_lookup = products.set_index("product_id")

invoice_values = []
for i in range(N_TXN):
    pid = txn_products[i]
    lo, hi = prod_lookup.loc[pid, "typical_unit_value_min"], prod_lookup.loc[pid, "typical_unit_value_max"]
    units = rng.integers(50, 5000)
    unit_val = rng.uniform(lo, hi)
    invoice_values.append(round(units * unit_val, 2))

stated_purposes = rng.choice(
    ["Commercial goods sale","Wholesale supply agreement","Distribution contract","Standard trade shipment",
     "Bulk commodity sale","Component supply order"], size=N_TXN)

transactions = pd.DataFrame({
    "transaction_id": txn_ids,
    "customer_id": txn_customers,
    "counterparty_id": txn_counterparties,
    "product_id": txn_products,
    "destination_country_id": txn_destcountry,
    "transaction_date": txn_dates,
    "invoice_value": invoice_values,
    "currency": currencies,
    "incoterm": incoterms,
    "direction": directions,
    "stated_purpose": stated_purposes,
})

# --- PATTERN 1 overlay: concentrate volume of the 2 designated customers through their cluster counterparties ---
# For each pattern-1 customer, re-point ~40 of their existing transactions to their cluster's counterparties,
# and re-date them within a plausible window, so the cluster represents a disproportionate share of that
# customer's export volume without being the customer's *only* activity (preserves alternative explanations).
pattern1_txn_ids = {"A": [], "B": []}
for cust, cluster_ids, key in [(pattern1_customers[0], pattern1_cpty_A, "A"), (pattern1_customers[1], pattern1_cpty_B, "B")]:
    cust_txn_idx = transactions.index[transactions["customer_id"] == cust].tolist()
    n_reassign = min(40, len(cust_txn_idx))
    reassign_idx = rng.choice(cust_txn_idx, size=n_reassign, replace=False)
    reassigned_cpty = rng.choice(cluster_ids, size=n_reassign)
    transactions.loc[reassign_idx, "counterparty_id"] = reassigned_cpty
    transactions.loc[reassign_idx, "direction"] = "export"
    pattern1_txn_ids[key] = transactions.loc[reassign_idx, "transaction_id"].tolist()

# --- PATTERN 2 overlay: Value/Weight Implausibility - 25 transactions ---
# Select 25 random transactions and inflate invoice_value far beyond product-category norms
# relative to what will become a low declared shipment weight (weight logic applied at shipment stage).
pattern2_idx = rng.choice(transactions.index, size=25, replace=False)
for idx in pattern2_idx:
    pid = transactions.loc[idx, "product_id"]
    lo, hi = prod_lookup.loc[pid, "typical_unit_value_min"], prod_lookup.loc[pid, "typical_unit_value_max"]
    # invoice value set to 6-10x the category's normal high-end unit value * plausible units,
    # while shipment weight (assigned later) stays within normal low range -> value/weight mismatch signal
    inflated = round(rng.uniform(6, 10) * hi * rng.integers(200, 800), 2)
    transactions.loc[idx, "invoice_value"] = inflated
pattern2_txn_ids = transactions.loc[pattern2_idx, "transaction_id"].tolist()

assert len(transactions) == 6000
print("Transactions:", len(transactions))
print("Pattern 1 reassigned txns -> A:", len(pattern1_txn_ids["A"]), "B:", len(pattern1_txn_ids["B"]))
print("Pattern 2 txns:", len(pattern2_txn_ids))

# ---------------------------------------------------------------------------
# 5. SHIPMENTS (6,090 rows: 5,850 txns x1, 120 txns x2, 30 txns x0)
# ---------------------------------------------------------------------------
all_txn_idx = list(transactions.index)
zero_ship_idx = set(rng.choice(all_txn_idx, size=30, replace=False))
remaining_idx = [i for i in all_txn_idx if i not in zero_ship_idx]
split_ship_idx = set(rng.choice(remaining_idx, size=120, replace=False))
single_ship_idx = [i for i in remaining_idx if i not in split_ship_idx]

assert len(zero_ship_idx) + len(split_ship_idx) + len(single_ship_idx) == 6000

ship_rows = []
ship_counter = 1
modes = ["sea","air","road"]

def make_shipment(txn_row, weight_override=None):
    global ship_counter
    dep = txn_row["transaction_date"] + timedelta(days=int(rng.integers(2,10)))
    arr = dep + timedelta(days=int(rng.integers(5,35)))
    pid = txn_row["product_id"]
    wlo, whi = prod_lookup.loc[pid, "typical_weight_min_kg"], prod_lookup.loc[pid, "typical_weight_max_kg"]
    weight = weight_override if weight_override is not None else round(rng.uniform(wlo, whi) * rng.integers(50,5000), 1)
    sid = f"SHIP{str(ship_counter).zfill(7)}"
    ship_counter += 1
    return {
        "shipment_id": sid, "transaction_id": txn_row["transaction_id"],
        "origin_country_id": "GB" if txn_row["direction"]=="export" else txn_row["destination_country_id"],
        "destination_country_id": txn_row["destination_country_id"] if txn_row["direction"]=="export" else "GB",
        "departure_date": dep, "arrival_date": arr,
        "declared_weight_kg": weight, "declared_value": txn_row["invoice_value"],
        "mode": rng.choice(modes, p=[0.55,0.25,0.20]),
        "container_ref": f"CNT{rng.integers(100000,999999)}",
    }

pattern2_set = set(pattern2_txn_ids)
for idx in single_ship_idx:
    row = transactions.loc[idx]
    weight_override = None
    if row["transaction_id"] in pattern2_set:
        # deliberately low declared weight relative to inflated invoice value -> value/weight mismatch
        pid = row["product_id"]
        wlo = prod_lookup.loc[pid, "typical_weight_min_kg"]
        weight_override = round(wlo * rng.uniform(0.5, 1.0) * rng.integers(1,5), 1)
    ship_rows.append(make_shipment(row, weight_override))

for idx in split_ship_idx:
    row = transactions.loc[idx]
    s1 = make_shipment(row)
    s2 = make_shipment(row)
    # split shipment: halve declared weight/value roughly across the two legs (legitimate split)
    s1["declared_weight_kg"] = round(s1["declared_weight_kg"]/2, 1)
    s2["declared_weight_kg"] = round(s2["declared_weight_kg"]/2, 1)
    s1["declared_value"] = round(row["invoice_value"]/2, 2)
    s2["declared_value"] = round(row["invoice_value"]/2, 2)
    ship_rows.extend([s1, s2])

shipments = pd.DataFrame(ship_rows)
assert len(shipments) == 5850 + 240, len(shipments)  # 6090

# Missing arrival_date: 2% of shipments (in-transit)
miss_arr_idx = rng.choice(shipments.index, size=int(round(len(shipments)*0.02)), replace=False)
shipments.loc[miss_arr_idx, "arrival_date"] = None

# Date-logic errors: 1% of shipments arrival < departure (data entry error)
remaining_for_error = [i for i in shipments.index if i not in set(miss_arr_idx)]
err_idx = rng.choice(remaining_for_error, size=int(round(len(shipments)*0.01)), replace=False)
for idx in err_idx:
    dep = shipments.loc[idx, "departure_date"]
    shipments.loc[idx, "arrival_date"] = dep - timedelta(days=int(rng.integers(1,5)))

print("Shipments:", len(shipments), "| missing arrival:", len(miss_arr_idx), "| date errors:", len(err_idx))

# ---------------------------------------------------------------------------
# 6. PAYMENTS (7,020: 5,100 txns x1, 780 x2, 120 x3)
# ---------------------------------------------------------------------------
one_pay_idx = set(rng.choice(all_txn_idx, size=5100, replace=False))
remaining2 = [i for i in all_txn_idx if i not in one_pay_idx]
two_pay_idx = set(rng.choice(remaining2, size=780, replace=False))
three_pay_idx = [i for i in remaining2 if i not in two_pay_idx]
assert len(three_pay_idx) == 120

pay_rows = []
pay_counter = 1
methods = ["wire","letter_of_credit","documentary_collection"]

def make_payment(txn_row, amount, days_after, payer_id=None, payer_type=None, route="direct"):
    global pay_counter
    pdate = txn_row["transaction_date"] + timedelta(days=int(days_after))
    pid = f"PAY{str(pay_counter).zfill(7)}"
    pay_counter += 1
    return {
        "payment_id": pid, "transaction_id": txn_row["transaction_id"],
        "payment_date": pdate, "amount": round(amount,2), "currency": txn_row["currency"],
        "payment_method": rng.choice(methods, p=[0.6,0.25,0.15]),
        "paying_entity_id": payer_id or txn_row["customer_id"],
        "paying_entity_type": payer_type or "customer",
        "settlement_route": route,
    }

# Select Pattern 3 transactions (120 = 2% of 6000) for third-party payment routing, drawn from
# across the full transaction pool (not exclusively the multi-payment group), tests H4/H6.
pattern3_idx = rng.choice(all_txn_idx, size=120, replace=False)
pattern3_set = set(transactions.loc[pattern3_idx, "transaction_id"])

for idx in one_pay_idx:
    row = transactions.loc[idx]
    if row["transaction_id"] in pattern3_set:
        payer = rng.choice(intermediaries["intermediary_id"])  # unrelated third party settles
        pay_rows.append(make_payment(row, row["invoice_value"], rng.integers(10,45), payer, "intermediary", "third_party"))
    else:
        pay_rows.append(make_payment(row, row["invoice_value"], rng.integers(10,45)))

for idx in two_pay_idx:
    row = transactions.loc[idx]
    split1 = round(row["invoice_value"]*0.5, 2)
    split2 = round(row["invoice_value"] - split1, 2)
    if row["transaction_id"] in pattern3_set:
        payer = rng.choice(intermediaries["intermediary_id"])
        pay_rows.append(make_payment(row, split1, rng.integers(5,20)))
        pay_rows.append(make_payment(row, split2, rng.integers(25,50), payer, "intermediary", "third_party"))
    else:
        pay_rows.append(make_payment(row, split1, rng.integers(5,20)))
        pay_rows.append(make_payment(row, split2, rng.integers(25,50)))

for idx in three_pay_idx:
    row = transactions.loc[idx]
    s1 = round(row["invoice_value"]*0.34, 2)
    s2 = round(row["invoice_value"]*0.33, 2)
    s3 = round(row["invoice_value"] - s1 - s2, 2)
    if row["transaction_id"] in pattern3_set:
        payer = rng.choice(intermediaries["intermediary_id"])
        pay_rows.append(make_payment(row, s1, rng.integers(5,15)))
        pay_rows.append(make_payment(row, s2, rng.integers(16,30)))
        pay_rows.append(make_payment(row, s3, rng.integers(31,50), payer, "intermediary", "third_party"))
    else:
        pay_rows.append(make_payment(row, s1, rng.integers(5,15)))
        pay_rows.append(make_payment(row, s2, rng.integers(16,30)))
        pay_rows.append(make_payment(row, s3, rng.integers(31,50)))

payments = pd.DataFrame(pay_rows)
assert len(payments) == 5100 + 780*2 + 120*3, len(payments)  # 7020

# Date-logic errors: 0.5% of payments predate their transaction date
n_pay_err = int(round(len(payments)*0.005))
pay_err_idx = rng.choice(payments.index, size=n_pay_err, replace=False)
txn_date_lookup = transactions.set_index("transaction_id")["transaction_date"].to_dict()
for idx in pay_err_idx:
    tdate = txn_date_lookup[payments.loc[idx,"transaction_id"]]
    payments.loc[idx, "payment_date"] = tdate - timedelta(days=int(rng.integers(1,10)))

print("Payments:", len(payments), "| Pattern 3 txns:", len(pattern3_set), "| date errors:", len(pay_err_idx))

# ---------------------------------------------------------------------------
# 7. TRANSACTION_INTERMEDIARIES (9,600 rows, avg 1.6/txn)
# Pattern 4: HUB_INTERMEDIARY_ID appears in 35% of these rows (decoy - legitimate high-degree node)
# ---------------------------------------------------------------------------
N_TI = 9600
N_HUB = int(round(N_TI * 0.35))  # 3360
N_OTHER = N_TI - N_HUB

other_intm_ids = [i for i in intm_ids if i != HUB_INTERMEDIARY_ID]
roles = ["freight_forwarder","broker","agent","correspondent_bank","payment_processor"]

ti_rows = []
ti_counter = 1

# Hub rows: spread across many different transactions and counterparties (structural centrality only)
hub_txn_sample = rng.choice(txn_ids, size=N_HUB, replace=True)
hub_txn_sample = pd.unique(hub_txn_sample)
# ensure exactly N_HUB rows by allowing repeats across different sequence_order where needed
while len(hub_txn_sample) < N_HUB:
    extra = rng.choice(txn_ids, size=N_HUB - len(hub_txn_sample), replace=True)
    hub_txn_sample = pd.unique(np.concatenate([hub_txn_sample, extra]))
hub_txn_sample = hub_txn_sample[:N_HUB]

for t in hub_txn_sample:
    ti_rows.append({
        "transaction_intermediary_id": f"TI{str(ti_counter).zfill(7)}", "transaction_id": t,
        "intermediary_id": HUB_INTERMEDIARY_ID, "intermediary_role": "freight_forwarder",
        "sequence_order": 1, "role_start_date": txn_date_lookup[t],
        "role_end_date": txn_date_lookup[t] + timedelta(days=int(rng.integers(5,30))),
        "source_confidence": "high",
    })
    ti_counter += 1

# Remaining rows: other intermediaries distributed across transactions
other_txn_sample = rng.choice(txn_ids, size=N_OTHER, replace=True)
other_intm_sample = rng.choice(other_intm_ids, size=N_OTHER, replace=True)
other_role_sample = rng.choice(roles, size=N_OTHER)
for i in range(N_OTHER):
    t = other_txn_sample[i]
    ti_rows.append({
        "transaction_intermediary_id": f"TI{str(ti_counter).zfill(7)}", "transaction_id": t,
        "intermediary_id": other_intm_sample[i], "intermediary_role": other_role_sample[i],
        "sequence_order": int(rng.integers(1,3)), "role_start_date": txn_date_lookup[t],
        "role_end_date": txn_date_lookup[t] + timedelta(days=int(rng.integers(5,30))),
        "source_confidence": rng.choice(["high","medium"], p=[0.8,0.2]),
    })
    ti_counter += 1

transaction_intermediaries = pd.DataFrame(ti_rows)
assert len(transaction_intermediaries) == 9600, len(transaction_intermediaries)
print("Transaction_Intermediaries:", len(transaction_intermediaries), "| hub rows:", N_HUB)

# ---------------------------------------------------------------------------
# 8. ALERTS (960 = 16% of transactions), 70% genuine noise / 30% pattern-linked
# ---------------------------------------------------------------------------
N_ALERT = 960
N_ALERT_NOISE = int(round(N_ALERT * 0.70))   # 672
N_ALERT_PATTERN = N_ALERT - N_ALERT_NOISE     # 288

alert_types = ["value_mismatch","late_shipment","documentation_gap","third_party_payment",
               "high_value_threshold","unusual_routing","repeat_counterparty_flag"]

alert_rows = []
alert_counter = 1

def add_alert(subject_type, subject_id, alert_date, atype, severity, disposition, notes):
    global alert_counter
    alert_rows.append({
        "alert_id": f"ALRT{str(alert_counter).zfill(7)}", "alert_date": alert_date,
        "alert_type": atype, "severity": severity, "subject_type": subject_type,
        "subject_id": subject_id, "disposition": disposition, "analyst_notes": notes,
    })
    alert_counter += 1

sev_probs = [0.55,0.32,0.13]
sev_choices = ["low","medium","high"]
dispositions = ["open","closed","escalated"]

# Noise alerts: random transactions, no relation to any planted pattern
all_pattern_txns = pattern1_txn_ids["A"] + pattern1_txn_ids["B"] + pattern2_txn_ids + list(pattern3_set)
non_pattern_txn_pool = [t for t in txn_ids if t not in set(all_pattern_txns)]
noise_txn_sample = rng.choice(non_pattern_txn_pool, size=N_ALERT_NOISE, replace=False)
for t in noise_txn_sample:
    tdate = txn_date_lookup[t]
    adate = tdate + timedelta(days=int(rng.integers(1,60)))
    add_alert("transaction", t, adate, rng.choice(alert_types), rng.choice(sev_choices,p=sev_probs),
               rng.choice(dispositions), "Routine system-generated alert; no further linkage identified.")

# Pattern-linked alerts (288): drawn from pattern txns AND their related customers/counterparties,
# but NOT covering every pattern transaction (asymmetry preserved per Stage 2 spec)
pattern_pool = list(set(all_pattern_txns))
n_from_pattern = min(N_ALERT_PATTERN, len(pattern_pool))
pattern_alert_txn_sample = rng.choice(pattern_pool, size=n_from_pattern, replace=False)
for t in pattern_alert_txn_sample:
    tdate = txn_date_lookup[t]
    adate = tdate + timedelta(days=int(rng.integers(1,60)))
    if t in set(pattern3_set):
        atype = "third_party_payment"
    elif t in set(pattern2_txn_ids):
        atype = "value_mismatch"
    else:
        atype = rng.choice(["repeat_counterparty_flag","unusual_routing"])
    add_alert("transaction", t, adate, atype, rng.choice(sev_choices,p=[0.35,0.40,0.25]),
               rng.choice(dispositions), "Pattern observed; alternative explanation not yet assessed.")

# fill remaining pattern-alert quota (if pattern_pool < N_ALERT_PATTERN) with additional noise
shortfall = N_ALERT_PATTERN - n_from_pattern
if shortfall > 0:
    extra_pool = [t for t in non_pattern_txn_pool if t not in set(noise_txn_sample)]
    extra_sample = rng.choice(extra_pool, size=shortfall, replace=False)
    for t in extra_sample:
        tdate = txn_date_lookup[t]
        adate = tdate + timedelta(days=int(rng.integers(1,60)))
        add_alert("transaction", t, adate, rng.choice(alert_types), rng.choice(sev_choices,p=sev_probs),
                   rng.choice(dispositions), "Routine system-generated alert; no further linkage identified.")

alerts = pd.DataFrame(alert_rows)
assert len(alerts) == 960, len(alerts)

# ---------------------------------------------------------------------------
# 9. CLAIMS (180 = 3% of transactions); Pattern 5: 72 (40%) preceded by prior alert
# ---------------------------------------------------------------------------
N_CLAIM = 180
N_CLAIM_ALERTLINKED = 72
N_CLAIM_INDEPENDENT = 108

# transactions that already have an alert (any type) - candidate pool for alert-linked claims
alerted_txns = set(alerts[alerts["subject_type"]=="transaction"]["subject_id"])
alerted_pool = list(alerted_txns)
non_alerted_pool = [t for t in txn_ids if t not in alerted_txns]

claim_alertlinked_txns = rng.choice(alerted_pool, size=N_CLAIM_ALERTLINKED, replace=False)
claim_independent_txns = rng.choice(non_alerted_pool, size=N_CLAIM_INDEPENDENT, replace=False)
claim_txns = list(claim_alertlinked_txns) + list(claim_independent_txns)

claim_reasons = ["non-payment_by_buyer","insolvency","dispute","other"]
claim_reason_probs = [0.60,0.20,0.15,0.05]
statuses = ["paid","rejected","pending"]

claim_rows = []
for i, t in enumerate(claim_txns):
    row = transactions[transactions["transaction_id"]==t].iloc[0]
    cdate = row["transaction_date"] + timedelta(days=int(rng.integers(30,180)))
    claim_rows.append({
        "claim_id": f"CLM{str(i+1).zfill(7)}", "transaction_id": t, "customer_id": row["customer_id"],
        "claim_date": cdate, "claim_amount": round(row["invoice_value"]*rng.uniform(0.7,1.0),2),
        "claim_reason": rng.choice(claim_reasons, p=claim_reason_probs),
        "status": rng.choice(statuses, p=[0.55,0.25,0.20]),
    })

claims = pd.DataFrame(claim_rows)
assert len(claims) == 180, len(claims)

print("Alerts:", len(alerts), "(noise:", N_ALERT_NOISE, "pattern-linked:", n_from_pattern+shortfall-shortfall if shortfall==0 else n_from_pattern, ")")
print("Claims:", len(claims), "| alert-linked:", N_CLAIM_ALERTLINKED, "| independent:", N_CLAIM_INDEPENDENT)

# ---------------------------------------------------------------------------
# 10. Empty schema tables (populated in later stages, not at generation)
# ---------------------------------------------------------------------------
case_review_log = pd.DataFrame(columns=["review_id","review_date","subject_type","subject_id",
    "reviewer","evidence_category","linked_hypothesis_id","finding_summary","status"])
data_quality_issues = pd.DataFrame(columns=["issue_id","table_name","record_id","issue_type",
    "original_value","resolution_applied","resolution_method","confidence_label","date_logged"])

# ---------------------------------------------------------------------------
# 11. WRITE OUTPUTS - analyst-facing tables (no fraud/guilty/risk label column anywhere)
# ---------------------------------------------------------------------------
ANALYST_TABLES = {
    "customers": customers,
    "counterparties": counterparties,
    "intermediaries": intermediaries,
    "products": products,
    "destinations": destinations,
    "transactions": transactions,
    "shipments": shipments,
    "payments": payments,
    "transaction_intermediaries": transaction_intermediaries,
    "alerts": alerts,
    "claims": claims,
    "entity_relationships": entity_relationships,
    "entity_attributes": entity_attributes,
    "case_review_log": case_review_log,
    "data_quality_issues": data_quality_issues,
}

# Verify no forbidden columns exist anywhere
FORBIDDEN = {"fraud","guilty","risk_score","is_suspicious","risk_label","fraud_flag"}
for tname, df in ANALYST_TABLES.items():
    cols = set(c.lower() for c in df.columns)
    bad = cols & FORBIDDEN
    assert not bad, f"Forbidden column found in {tname}: {bad}"

db_path = os.path.join(OUT_DIR, "northbridge.db")
if os.path.exists(db_path):
    os.remove(db_path)
conn = sqlite3.connect(db_path)
for tname, df in ANALYST_TABLES.items():
    df_out = df.copy()
    for col in df_out.columns:
        if df_out[col].dtype == object:
            df_out[col] = df_out[col].apply(lambda x: x.isoformat() if hasattr(x, "isoformat") else x)
    df_out.to_sql(tname, conn, if_exists="replace", index=False)
    df_out.to_csv(os.path.join(CSV_DIR, f"{tname}.csv"), index=False)
conn.commit()
conn.close()

print("\nWritten analyst-facing tables to SQLite + CSV.")

# ---------------------------------------------------------------------------
# 12. GROUND TRUTH FILE (hidden, separate folder, validation-only)
# ---------------------------------------------------------------------------
ground_truth = {
    "_label": "Category 8 - Simulated ground truth. Validation use only. Do NOT reference during Stage 4-8 analysis.",
    "generation_seed": SEED,
    "patterns": [
        {
            "pattern_name": "Counterparty Fragmentation",
            "hypothesis_tested": "H1 / H3",
            "cluster_A": {"customer": pattern1_customers[0], "counterparties": pattern1_cpty_A,
                          "shared_address": shared_addr_A, "shared_bank_hash": shared_bank_A,
                          "reassigned_transactions": pattern1_txn_ids["A"]},
            "cluster_B": {"customer": pattern1_customers[1], "counterparties": pattern1_cpty_B,
                          "shared_address": shared_addr_B, "shared_bank_hash": shared_bank_B,
                          "reassigned_transactions": pattern1_txn_ids["B"]},
            "intended_signal": "Shared address/bank_account_hash across nominally distinct counterparties, concentrating share of designated customer's export volume.",
            "expected_stage6_outcome": "Entity resolution should independently recover both clusters from Entity_Attributes.",
        },
        {
            "pattern_name": "Value/Weight Implausibility",
            "hypothesis_tested": "H4 (Q2/Q5)",
            "affected_transactions": pattern2_txn_ids,
            "intended_signal": "Invoice value inflated 6-10x category norm while declared shipment weight remains within normal low range.",
            "expected_stage6_outcome": "Should surface under product-category-normalised value/weight ratio test at reasonable thresholds.",
        },
        {
            "pattern_name": "Third-Party Payment Routing",
            "hypothesis_tested": "H4 / H6",
            "affected_transactions": sorted(pattern3_set),
            "intended_signal": "Final settlement leg paid by an intermediary entity not party to the underlying transaction.",
            "expected_stage6_outcome": "Should surface as unusual paying_entity_type; NOT automatically confirmed by any declared Entity_Relationship.",
        },
        {
            "pattern_name": "Intermediary Hub (DECOY - no wrongdoing signal)",
            "hypothesis_tested": "H2 (negative/trap case)",
            "intermediary_id": HUB_INTERMEDIARY_ID,
            "share_of_transaction_intermediary_rows": 0.35,
            "intended_signal": "High graph degree from ordinary large-scale freight-forwarding activity only.",
            "expected_stage6_outcome": "Correctly disciplined analysis must clear this node as an ordinary service-provider hub, not flag it as a risk hub. This is the primary test of evidential discipline in the project.",
        },
        {
            "pattern_name": "Alert/Claim Co-occurrence",
            "hypothesis_tested": "H5",
            "alert_linked_claims": sorted(claim_alertlinked_txns.tolist()),
            "independent_claims": sorted(claim_independent_txns.tolist()),
            "intended_signal": "40% of claims preceded by a prior alert vs. base population; correlation only, no embedded causal mechanism.",
            "expected_stage6_outcome": "Should show as a weak-to-moderate descriptive relationship requiring a matched-volume control group before further weight is given.",
        },
    ],
    "noise_elements": {
        "duplicate_counterparty_ids": new_dup_ids,
        "note": "These duplicates are unrelated to any pattern above - pure data-quality noise."
    }
}

gt_path = os.path.join(GT_DIR, "ground_truth.json")
with open(gt_path, "w") as f:
    json.dump(ground_truth, f, indent=2, default=str)

print("Ground truth written to:", gt_path)
