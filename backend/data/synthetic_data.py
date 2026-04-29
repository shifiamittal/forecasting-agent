"""
Synthetic knowledge base data for the Forecasting Agent.
Covers 3 tenants: HERSHEYS, CORNING, MICHELIN
Document types: incident_records, readiness_reports, override_decisions,
                retrain_decisions, trade_calendar
Each document includes full metadata for catalog + permission graph.
"""

SYNTHETIC_DOCUMENTS = [

    # ─── INCIDENT RECORDS ───────────────────────────────────────────────────

    {
        "doc_id": "INC-001",
        "source_type": "incident_record",
        "client_id": "HERSHEYS",
        "date": "2024-03-15",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["KROGER"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-001: Kroger POS feed failure for chocolate seasonal SKUs. "
            "Symptom: wMAPE degraded 3.8 points on chocolate_seasonal segment, cycle 31. "
            "Investigation: Kroger POS ingestion job failed due to connection timeout in Argo workflow. "
            "Feed was stale for 11 days. 18 chocolate seasonal SKUs missing actuals. "
            "Root cause: network timeout in Argo job kroger_pos_ingest, no retry logic. "
            "Resolution: manual actuals backfill from Kroger portal. wMAPE recovered within 1 cycle. "
            "Action taken: engineering added retry logic with 3 attempts and 48-hour staleness alert."
        ),
    },
    {
        "doc_id": "INC-002",
        "source_type": "incident_record",
        "client_id": "HERSHEYS",
        "date": "2024-06-20",
        "segment": "chocolate_everyday",
        "retailer_scope": ["WALMART", "TARGET"],
        "severity": "tier_2",
        "root_cause_layer": "feature",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-002: ACV distribution drift on chocolate everyday SKUs. "
            "Symptom: bias trending positive for 3 consecutive cycles, reaching +0.24. "
            "Investigation: feature drift analysis showed ACV weighted distribution shift score 0.78. "
            "Walmart reset planogram in May, changing shelf placement for 12 chocolate everyday SKUs. "
            "Root cause: ACV data not refreshed after planogram reset. Model trained on stale distribution. "
            "Resolution: ACV data refresh from Nielsen, partial retrain on affected SKU group. "
            "wMAPE improved 2.1 points within 2 cycles post-retrain."
        ),
    },
    {
        "doc_id": "INC-003",
        "source_type": "incident_record",
        "client_id": "HERSHEYS",
        "date": "2024-11-01",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["WALMART", "TARGET", "KROGER"],
        "severity": "tier_2",
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Incident INC-003: Halloween promotional lift underforecast. "
            "Symptom: forecast delta +31% vs actuals on chocolate seasonal week 43. "
            "Investigation: trade calendar showed Halloween promo registered but lift multiplier "
            "was set at prior year value of 1.18x. Actual lift came in at 1.34x due to expanded "
            "display placement at Walmart and Target. "
            "Root cause: promo lift multiplier not updated for expanded display. "
            "Resolution: planner override applied, lift multiplier updated in trade calendar registry. "
            "Recommendation: DS to review promo lift multipliers each cycle against confirmed display plans."
        ),
    },
    {
        "doc_id": "INC-004",
        "source_type": "incident_record",
        "client_id": "HERSHEYS",
        "date": "2024-01-10",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["TARGET"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-004: Target schema change broke POS ingestion. "
            "Symptom: 0 actuals ingested for Target chocolate seasonal, cycles 2-3. "
            "Investigation: Target updated their POS export format, renaming column "
            "'units_sold' to 'qty_sold'. Schema validation in Great Expectations flagged "
            "BLOCKED verdict on Target feed but alert was missed. "
            "Root cause: schema registry not updated after Target contract renewal. "
            "Resolution: schema registry updated with new column mapping. "
            "INC-004 established protocol: retailer contract renewals trigger mandatory "
            "schema registry review within 48 hours."
        ),
    },
    {
        "doc_id": "INC-005",
        "source_type": "incident_record",
        "client_id": "CORNING",
        "date": "2024-05-18",
        "segment": "industrial_sku_group",
        "retailer_scope": ["DIRECT_B2B"],
        "severity": "tier_2",
        "root_cause_layer": "model",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-005: Corning industrial SKU model degradation after product line expansion. "
            "Symptom: wMAPE increased from 9.1 to 13.2 over 4 cycles on industrial_sku_group. "
            "Investigation: Corning added 23 new industrial SKUs in Q1 without triggering retrain. "
            "New SKUs had no historical demand and were initialized with category averages. "
            "Root cause: new SKU onboarding process did not include model scope update. "
            "Resolution: retrain with expanded SKU scope, 18-month window, new SKU cold-start "
            "logic added using category hierarchy priors. wMAPE recovered to 9.4 within 2 cycles."
        ),
    },
    {
        "doc_id": "INC-006",
        "source_type": "incident_record",
        "client_id": "CORNING",
        "date": "2024-08-22",
        "segment": "industrial_sku_group",
        "retailer_scope": ["DIRECT_B2B"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-006: Corning ERP feed duplicate records causing inflated actuals. "
            "Symptom: bias score dropped to -0.31 on industrial_sku_group, cycle 34. "
            "Investigation: pipeline logs showed duplicate ingestion records for 8 SKUs. "
            "Corning ERP system generated duplicate export files during system upgrade window. "
            "Root cause: deduplication logic in Bronze layer did not handle same-day duplicates "
            "with identical timestamps. "
            "Resolution: deduplication logic updated to use composite key "
            "(sku_id + date + retailer_id). Actuals corrected via backfill. "
            "Bias recovered to -0.04 next cycle."
        ),
    },
    {
        "doc_id": "INC-007",
        "source_type": "incident_record",
        "client_id": "MICHELIN",
        "date": "2024-07-05",
        "segment": "tire_replacement_seasonal",
        "retailer_scope": ["WALMART", "COSTCO"],
        "severity": "tier_2",
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Incident INC-007: Michelin summer tire season demand spike not captured. "
            "Symptom: forecast delta -28% vs actuals on tire_replacement_seasonal, weeks 26-28. "
            "Investigation: unusual heatwave in Northeast US drove early summer tire demand. "
            "Macro signal flag was not registered in trade calendar. "
            "Root cause: macro weather events not systematically monitored as demand signals. "
            "Resolution: planner applied override for weeks 26-28. "
            "Recommendation: integrate weather API signal into external signal layer. "
            "DS to evaluate feasibility of weather-correlated demand features for tire SKUs."
        ),
    },
    {
        "doc_id": "INC-008",
        "source_type": "incident_record",
        "client_id": "MICHELIN",
        "date": "2024-02-14",
        "segment": "tire_replacement_seasonal",
        "retailer_scope": ["COSTCO"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Incident INC-008: Costco membership data feed outage affecting Michelin tire forecasts. "
            "Symptom: data quality score dropped to 0.41 for Costco channel, cycle 7. "
            "Investigation: Costco membership renewal data used as proxy for tire replacement "
            "propensity was not refreshed for 3 cycles. Feed authentication token expired. "
            "Root cause: API token rotation not automated. "
            "Resolution: token rotated manually, automation added for 90-day renewal. "
            "Costco channel forecasts suppressed for 2 cycles until feed stabilized."
        ),
    },

    # ─── DATA READINESS REPORTS ─────────────────────────────────────────────

    {
        "doc_id": "RR-001",
        "source_type": "readiness_report",
        "client_id": "HERSHEYS",
        "date": "2024-03-14",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["WALMART", "TARGET", "KROGER", "COSTCO"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "planner", "engineering"],
        "content": (
            "Data Readiness Report RR-001 | Run: hersheys_cycle_31 | "
            "Verdict: BLOCKED. "
            "Schema validation: APPROVED. Feed freshness: BLOCKED — "
            "Kroger POS feed stale 11 days. "
            "Temporal integrity: BLOCKED — 18 chocolate seasonal SKUs missing "
            "11 days of actuals at Kroger. "
            "Feature completeness: CONDITIONAL — ACV data 6 weeks old for Kroger channel. "
            "Hierarchy coherence: APPROVED. "
            "Statistical distribution: CONDITIONAL — Kroger channel showing "
            "distribution shift due to missing data. "
            "Recommended action: block cycle 31 training until Kroger actuals backfill confirmed. "
            "Affected SKUs: choc_seas_001 through choc_seas_018 at Kroger."
        ),
    },
    {
        "doc_id": "RR-002",
        "source_type": "readiness_report",
        "client_id": "HERSHEYS",
        "date": "2024-06-19",
        "segment": "chocolate_everyday",
        "retailer_scope": ["WALMART", "TARGET"],
        "severity": "tier_2",
        "root_cause_layer": "feature",
        "visible_to": ["DS", "planner"],
        "content": (
            "Data Readiness Report RR-002 | Run: hersheys_cycle_44 | "
            "Verdict: CONDITIONAL. "
            "Schema validation: APPROVED. Feed freshness: APPROVED. "
            "Temporal integrity: APPROVED. "
            "Feature completeness: CONDITIONAL — ACV weighted distribution "
            "last refreshed 6 months ago. Current drift score: 0.78. "
            "Hierarchy coherence: APPROVED. "
            "Statistical distribution: CONDITIONAL — Walmart channel shows "
            "distribution shift score 0.71 on ACV feature. "
            "Recommended action: proceed with training but flag ACV staleness "
            "for DS review. Schedule ACV refresh before next cycle."
        ),
    },
    {
        "doc_id": "RR-003",
        "source_type": "readiness_report",
        "client_id": "CORNING",
        "date": "2024-08-21",
        "segment": "industrial_sku_group",
        "retailer_scope": ["DIRECT_B2B"],
        "severity": "tier_1",
        "root_cause_layer": "data",
        "visible_to": ["DS", "engineering"],
        "content": (
            "Data Readiness Report RR-003 | Run: corning_cycle_34 | "
            "Verdict: BLOCKED. "
            "Schema validation: APPROVED. Feed freshness: BLOCKED — "
            "duplicate records detected in ERP export for 8 SKUs. "
            "Temporal integrity: BLOCKED — actuals inflated 2x for "
            "affected SKUs due to duplicate ingestion. "
            "Feature completeness: APPROVED. Hierarchy coherence: APPROVED. "
            "Statistical distribution: BLOCKED — bias score -0.31, "
            "outside acceptable range. "
            "Recommended action: halt training. Trigger deduplication fix "
            "and actuals backfill before proceeding."
        ),
    },

    # ─── OVERRIDE DECISIONS ─────────────────────────────────────────────────

    {
        "doc_id": "OVR-001",
        "source_type": "override_decision",
        "client_id": "HERSHEYS",
        "date": "2024-11-02",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["WALMART", "TARGET", "KROGER"],
        "severity": "tier_2",
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Override Decision OVR-001 | Approved by: planner_hersheys_lead | "
            "Segment: chocolate_seasonal | Cycles: 43-44 | "
            "Correction: +18% applied to all chocolate seasonal SKUs at Walmart and Target. "
            "Rationale: Halloween expanded display placement confirmed by trade team. "
            "Prior year lift was 1.18x, confirmed display expansion supports 1.34x. "
            "Expiry: end of week 44. "
            "Outcome: forecast error reduced from +31% to +4% for week 43. "
            "Planner note: recommend updating promo lift multiplier in trade calendar "
            "registry before next Halloween cycle."
        ),
    },
    {
        "doc_id": "OVR-002",
        "source_type": "override_decision",
        "client_id": "MICHELIN",
        "date": "2024-07-06",
        "segment": "tire_replacement_seasonal",
        "retailer_scope": ["WALMART", "COSTCO"],
        "severity": "tier_2",
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Override Decision OVR-002 | Approved by: planner_michelin_lead | "
            "Segment: tire_replacement_seasonal | Cycles: 26-28 | "
            "Correction: +22% applied to summer tire SKUs at Walmart and Costco. "
            "Rationale: Northeast heatwave drove early summer tire replacement demand. "
            "No model feature captures weather-correlated demand spikes. "
            "Expiry: end of week 28. "
            "Outcome: forecast error reduced from -28% to -6% for weeks 26-28. "
            "DS note: evaluate weather API integration for tire SKU feature pipeline."
        ),
    },
    {
        "doc_id": "OVR-003",
        "source_type": "override_decision",
        "client_id": "HERSHEYS",
        "date": "2024-02-08",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["WALMART", "TARGET"],
        "severity": "tier_2",
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Override Decision OVR-003 | Approved by: planner_hersheys_lead | "
            "Segment: chocolate_seasonal | Cycle: 6 | "
            "Correction: +16% applied to Valentine's Day chocolate SKUs. "
            "Rationale: Valentine's Day promo week 6 confirmed by trade calendar. "
            "Prior year uplift range: +18-24%. Model underforecast by 19%. "
            "Expiry: end of week 6. "
            "Outcome: forecast error reduced from -19% to -3%. "
            "Note: model consistently underforecasts Valentine's week — "
            "consider adding Valentine's Day indicator feature to model."
        ),
    },

    # ─── RETRAIN DECISIONS ──────────────────────────────────────────────────

    {
        "doc_id": "RTR-001",
        "source_type": "retrain_decision",
        "client_id": "CORNING",
        "date": "2023-06-15",
        "segment": "industrial_sku_group",
        "retailer_scope": ["DIRECT_B2B"],
        "severity": "tier_2",
        "root_cause_layer": "feature",
        "visible_to": ["DS"],
        "content": (
            "Retrain Decision RTR-001 | Approved by: DS_corning_lead | "
            "Model: corning_autogluon_v10 | "
            "Trigger: ACV distribution staleness — drift score 0.81. "
            "ACV data last refreshed 6 months prior. "
            "Training window: 18 months. Feature refresh: acv_weighted_distribution. "
            "SKU scope: industrial_sku_group. Compute: 6.5 hours. "
            "Outcome: wMAPE improved 2.1 points (from 13.2 to 11.1) within 2 cycles. "
            "Bias recovered from +0.23 to +0.06. "
            "Lesson: ACV data freshness should be monitored monthly. "
            "Added ACV staleness check to Data Readiness Agent."
        ),
    },
    {
        "doc_id": "RTR-002",
        "source_type": "retrain_decision",
        "client_id": "HERSHEYS",
        "date": "2024-07-10",
        "segment": "chocolate_everyday",
        "retailer_scope": ["WALMART", "TARGET"],
        "severity": "tier_2",
        "root_cause_layer": "feature",
        "visible_to": ["DS"],
        "content": (
            "Retrain Decision RTR-002 | Approved by: DS_hersheys_lead | "
            "Model: hersheys_autogluon_v8 | "
            "Trigger: ACV distribution drift post-Walmart planogram reset. "
            "Drift score 0.78 on ACV feature for Walmart channel. "
            "Training window: 24 months. Feature refresh: acv_weighted_distribution "
            "for Walmart channel. SKU scope: chocolate_everyday. Compute: 5 hours. "
            "Outcome: wMAPE improved 2.1 points on chocolate_everyday. "
            "Bias recovered from +0.24 to +0.07 within 2 cycles."
        ),
    },

    # ─── TRADE CALENDAR ─────────────────────────────────────────────────────

    {
        "doc_id": "TC-001",
        "source_type": "trade_calendar",
        "client_id": "HERSHEYS",
        "date": "2024-01-01",
        "segment": "chocolate_seasonal",
        "retailer_scope": ["WALMART", "TARGET", "KROGER", "COSTCO"],
        "severity": None,
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Trade Calendar TC-001 | Client: HERSHEYS | Year: 2024 | "
            "Valentine's Day promo: week 6, all retailers. "
            "Expected lift: +18-24% on chocolate seasonal SKUs. "
            "Display type: endcap + checkout lane placement. "
            "Easter promo: weeks 13-14, all retailers. Expected lift: +22-28%. "
            "Halloween promo: week 43, Walmart and Target expanded display. "
            "Expected lift: +28-34% (updated from prior year 18-24% "
            "due to confirmed expanded placement). "
            "Christmas promo: weeks 50-52, all retailers. Expected lift: +35-42%. "
            "Note: lift multipliers reviewed and confirmed with Hersheys trade team "
            "on 2024-01-01."
        ),
    },
    {
        "doc_id": "TC-002",
        "source_type": "trade_calendar",
        "client_id": "MICHELIN",
        "date": "2024-01-01",
        "segment": "tire_replacement_seasonal",
        "retailer_scope": ["WALMART", "COSTCO"],
        "severity": None,
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Trade Calendar TC-002 | Client: MICHELIN | Year: 2024 | "
            "Winter tire season: weeks 40-48, Walmart and Costco. "
            "Expected lift: +18-22% on winter tire SKUs. "
            "Summer tire season: weeks 20-28. Expected lift: +12-16%. "
            "Note: weather-correlated demand spikes not currently modeled. "
            "DS recommendation: integrate NOAA weather API for regional demand signals. "
            "Black Friday promo: week 47, Costco only. Expected lift: +25-30%."
        ),
    },
    {
        "doc_id": "TC-003",
        "source_type": "trade_calendar",
        "client_id": "CORNING",
        "date": "2024-01-01",
        "segment": "industrial_sku_group",
        "retailer_scope": ["DIRECT_B2B"],
        "severity": None,
        "root_cause_layer": "external",
        "visible_to": ["DS", "planner"],
        "content": (
            "Trade Calendar TC-003 | Client: CORNING | Year: 2024 | "
            "Q1 industrial orders: weeks 1-13. Typical demand pattern: "
            "front-loaded due to capital budget cycles. "
            "Q2 slowdown: weeks 14-26. Seasonal demand dip of 8-12% expected. "
            "Q3 recovery: weeks 27-39. Recovery of 6-10% as H2 budgets release. "
            "Q4 year-end push: weeks 40-52. Elevated demand +15-20% as clients "
            "exhaust annual capital budgets. "
            "New product launch: industrial_sku_NEW_001 through 023 added Q1. "
            "Cold-start logic applied using category hierarchy priors."
        ),
    },
]

if __name__ == "__main__":
    print(f"Total documents: {len(SYNTHETIC_DOCUMENTS)}")
    from collections import Counter
    types = Counter(d["source_type"] for d in SYNTHETIC_DOCUMENTS)
    clients = Counter(d["client_id"] for d in SYNTHETIC_DOCUMENTS)
    print(f"By type: {dict(types)}")
    print(f"By client: {dict(clients)}")
