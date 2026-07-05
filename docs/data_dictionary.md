# Northbridge Trade Risk Investigation — Data Dictionary
Fictional portfolio dataset. Seed = 42. Generated per Stage 2 approved specification.

Format per field: `field_name | type | nullable | description | example | source | validation_rule`

## customers (180 rows)
- customer_id | text | N | PK, prefix CUST+5digits | CUST00042 | generated | unique
- legal_name | text | N | fictional company name | "Meridian Textiles Ltd" | generated | —
- registration_number | text | N | UK company number (fictional) | UK14829031 | generated | —
- incorporation_country | text | N | always GB | GB | generated | = 'GB'
- segment | text | N | SME / Mid-market / Corporate | SME | generated | in enum
- onboarding_date | date | N | date customer onboarded | 2019-03-11 | generated | <= transaction dates
- registered_address | text | N | UK address | "42 High St, UK" | generated | —
- primary_contact_email | text | N | fictional email | contact1@customer1.co.uk | generated | —
- primary_contact_phone | text | N | fictional UK phone | +44 20 1234 5678 | generated | —
- relationship_manager | text | N | RM name | A. Whitfield | generated | —

## counterparties (260 rows, incl. 15 noise duplicates)
- counterparty_id | text | N | PK, prefix CPTY+5digits | CPTY00187 | generated | unique
- legal_name | text | N | fictional name | "Delta Overseas Trading FZE" | generated | —
- registration_number | text | Y | null for ~35% of non-GB entities | AE482910 | generated | intelligence gap if null
- country | text | N | ISO-2 | AE | generated | FK destinations
- entity_type | text | N | buyer/supplier/agent | buyer | generated | in enum
- first_seen_date | date | N | — | 2021-06-02 | generated | —
- registered_address | text | N | shared across Pattern 1 clusters | "Unit 7, Sheikh Zayed..." | generated | —
- contact_email | text | N | — | info1@cpty1.com | generated | —
- contact_phone | text | N | — | +971 4 1234 | generated | —
- bank_account_hash | text | N | hashed identifier; shared across Pattern 1 clusters | a1b2c3... | generated | —

## intermediaries (45 rows)
- intermediary_id | text | N | PK, prefix INTM+5digits | INTM00023 | generated | unique
- legal_name, role_type (freight_forwarder/agent/correspondent_bank/payment_processor), country, first_seen_date, contact_email

## products (18 rows)
- product_id | text | N | PK, PROD+4digits
- product_category, product_label, hs_code_group, typical_unit_value_min/max, typical_weight_min/max_kg — used only for plausibility benchmarking, not risk scoring

## destinations (30 rows)
- country_id (ISO-2, PK), country_name, region, corridor_group (Corridor_A..F, analyst grouping only, NOT a risk ranking)

## transactions (6,000 rows)
- transaction_id | PK, TXN+7digits
- customer_id, counterparty_id, product_id, destination_country_id | FKs
- transaction_date, invoice_value, currency, incoterm, direction, stated_purpose

## shipments (6,090 rows)
- shipment_id | PK | transaction_id FK (0, 1, or 2 rows per transaction by design)
- origin/destination_country_id, departure_date, arrival_date (nullable, ~2% missing), declared_weight_kg, declared_value, mode, container_ref
- Known date-logic errors embedded (~1%): arrival_date < departure_date — NOT auto-corrected, logged for Stage 3.

## payments (7,020 rows)
- payment_id | PK | transaction_id FK (1-3 rows per transaction by design)
- payment_date (0.5% predate transaction_date — embedded error), amount, currency, payment_method
- paying_entity_id / paying_entity_type — polymorphic; usually customer, occasionally intermediary (third-party routing)
- settlement_route: direct / third_party

## transaction_intermediaries (9,600 rows) — bridge table
- transaction_intermediary_id | PK
- transaction_id, intermediary_id | FKs
- intermediary_role, sequence_order, role_start_date, role_end_date, source_confidence

## alerts (960 rows)
- alert_id | PK | subject_type + subject_id (polymorphic, currently always 'transaction')
- alert_date, alert_type, severity (low/medium/high), disposition (open/closed/escalated), analyst_notes

## claims (180 rows)
- claim_id | PK | transaction_id, customer_id | FKs
- claim_date, claim_amount, claim_reason, status (paid/rejected/pending)

## entity_relationships (70 rows) — declared/documented links only
- relationship_id | PK
- entity_id_1/entity_type_1, entity_id_2/entity_type_2 | polymorphic
- relationship_type, source (declared/regulatory_filing), confidence (high/medium/low)

## entity_attributes (1,400 rows) — raw attribute observations, input to entity resolution
- attribute_id | PK | entity_id/entity_type polymorphic
- attribute_type (address/phone/email/registered_agent/bank_account), attribute_value, source_date

## case_review_log (0 rows at generation — populated Stage 4 onward)
- review_id, review_date, subject_type, subject_id, reviewer, evidence_category, linked_hypothesis_id, finding_summary, status

## data_quality_issues (0 rows at generation — populated at Stage 3 audit)
- issue_id, table_name, record_id, issue_type, original_value, resolution_applied, resolution_method, confidence_label, date_logged

---
**Note:** No table in this analyst-facing dataset contains a fraud/guilt/risk-score/risk-label column of any kind. All patterns are embedded as statistically detectable structure only. See `/ground_truth/ground_truth.json` (separate folder) for the validation-only record of planted patterns — not to be referenced during Stages 3-8 analysis.
