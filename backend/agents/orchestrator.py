"""
Orchestrator: chains all agents for a full forecast cycle run.
Returns structured output for SSE streaming to frontend.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.trigger_router import run_trigger_router
from agents.exception_triage import run_exception_triage
from agents.rca_diagnostic import run_rca_diagnostic
from agents.retrain_override import run_retrain_override
from agents.eval_agent import run_eval_agent


def run_full_cycle(scenario: dict, user_role: str = "DS") -> dict:
    """
    Full agent chain for one forecast cycle.
    scenario keys: forecast_summary, config, escalation_flag,
                   prior_accuracy, sku_exceptions, pipeline_data
    """
    results = {}

    # Step 1: Trigger Router
    print("Running Trigger Router...")
    routing = run_trigger_router(
        forecast_summary=scenario["forecast_summary"],
        config=scenario["config"],
        escalation_flag=scenario.get("escalation_flag", False),
        prior_accuracy=scenario["prior_accuracy"],
    )
    results["trigger_router"] = routing

    client_id       = routing["client_id"]
    agents_activated = routing.get("agents_activated", [])
    priority_segs   = routing.get("priority_segments", [])

    # Step 2: Exception Triage (always runs if activated)
    if any("exception_triage" in a.lower() for a in agents_activated):
        print("Running Exception Triage...")
        triage = run_exception_triage(
            cycle_id=routing["cycle_id"],
            client_id=client_id,
            priority_segments=priority_segs,
            sku_exceptions=scenario.get("sku_exceptions", []),
            user_role=user_role,
        )
        results["exception_triage"] = triage

    # Step 3: RCA Diagnostic
    if any("rca_diagnostic" in a.lower() for a in agents_activated):
        print("Running RCA Diagnostic...")
        rca = run_rca_diagnostic(
            cycle_id=routing["cycle_id"],
            client_id=client_id,
            degraded_segment=priority_segs[0] if priority_segs else "unknown",
            degradation_summary=scenario.get(
                "degradation_summary",
                scenario["forecast_summary"]
                    .get("segments_with_accuracy_breach", [{}])[0]
            ),
            pipeline_data=scenario.get("pipeline_data", {}),
            user_role=user_role,
        )
        results["rca_diagnostic"] = rca

        # Step 4: Eval on RCA
        print("Running Eval on RCA...")
        rca_eval = run_eval_agent("rca_diagnostic", rca)
        results["rca_eval"] = rca_eval

        # Step 5: Retrain/Override if RCA triggers it
        if rca.get("downstream_trigger") in ("retrain", "override"):
            print("Running Retrain/Override Agent...")
            retrain = run_retrain_override(
                cycle_id=routing["cycle_id"],
                client_id=client_id,
                rca_output=rca,
                degradation_history=scenario.get("degradation_history", []),
                user_role=user_role,
            )
            results["retrain_override"] = retrain

            print("Running Eval on Retrain/Override...")
            retrain_eval = run_eval_agent("retrain_override", retrain)
            results["retrain_override_eval"] = retrain_eval

    return results


# ── Demo scenario: Hersheys cycle 47 ────────────────────────────────────────
HERSHEYS_DEMO = {
    "forecast_summary": {
        "cycle_id": "hersheys_cycle_47",
        "client_id": "HERSHEYS",
        "total_skus": 2400,
        "skus_with_delta_above_threshold": 23,
        "segments_with_accuracy_breach": [
            {"segment": "chocolate_seasonal",
             "wMAPE_prior": 11.2, "wMAPE_current": 14.8, "bias": 0.21}
        ],
        "data_quality_flags": 2,
        "trade_calendar_events": ["Valentine's Day promo week 6"],
    },
    "config": {
        "delta_threshold": 0.15,
        "bias_threshold": 0.15,
        "degradation_threshold_wMAPE": 2.0,
        "sustained_degradation_cycles": 3,
    },
    "escalation_flag": False,
    "prior_accuracy": {"wMAPE": 11.2, "bias": 0.08},
    "sku_exceptions": [
        {
            "sku_id": "choc_seas_group",
            "location_id": "ALL",
            "forecast_delta_pct": 22,
            "bias_history": [0.09, 0.18, 0.21],
            "data_quality_score": 0.83,
            "trade_calendar_event": "Valentine's Day promo week 6",
        },
        {
            "sku_id": "choc_seas_kroger_001",
            "location_id": "KROGER",
            "forecast_delta_pct": 45,
            "bias_history": [0.18, 0.24, 0.31],
            "data_quality_score": 0.38,
            "trade_calendar_event": None,
        },
    ],
    "degradation_summary": {
        "wMAPE_prior": 11.2, "wMAPE_current": 14.8,
        "bias_current": 0.21, "bias_trend": [0.09, 0.18, 0.21],
        "cycles_degraded": 2,
    },
    "pipeline_data": {
        "feed_freshness": {
            "WALMART": "2 hours ago — fresh",
            "TARGET": "3 hours ago — fresh",
            "KROGER": "11 days ago — STALE",
            "COSTCO": "1 hour ago — fresh",
        },
        "pipeline_failures": [
            "Argo job kroger_pos_ingest: connection timeout. "
            "18 chocolate_seasonal SKUs at KROGER missing 11 days of actuals."
        ],
        "data_quality_scores": {
            "chocolate_seasonal_walmart": 0.91,
            "chocolate_seasonal_target": 0.88,
            "chocolate_seasonal_kroger": 0.38,
        },
        "feature_drift": {
            "acv_weighted_distribution": 0.22,
            "promo_flag_consistency": 0.97,
        },
        "model_metadata": {
            "model_id": "hersheys_autogluon_v11",
            "last_trained": "2024-01-15",
        },
        "trade_calendar": ["Valentine's Day promo week 6 — lift +18-24%"],
    },
    "degradation_history": [
        {"cycle": 45, "wMAPE": 11.4, "bias": 0.09},
        {"cycle": 46, "wMAPE": 12.8, "bias": 0.18},
        {"cycle": 47, "wMAPE": 14.8, "bias": 0.21},
    ],
}

# ── Demo scenario: Corning cycle 47 ─────────────────────────────────────────
CORNING_DEMO = {
    "forecast_summary": {
        "cycle_id": "corning_cycle_47",
        "client_id": "CORNING",
        "total_skus": 850,
        "skus_with_delta_above_threshold": 240,
        "segments_with_accuracy_breach": [
            {"segment": "industrial_sku_group",
             "wMAPE_prior": 9.1, "wMAPE_current": 13.2, "bias": 0.23}
        ],
        "data_quality_flags": 0,
        "trade_calendar_events": [],
    },
    "config": {
        "delta_threshold": 0.15,
        "bias_threshold": 0.15,
        "degradation_threshold_wMAPE": 2.0,
        "sustained_degradation_cycles": 3,
    },
    "escalation_flag": False,
    "prior_accuracy": {"wMAPE": 9.1, "bias": 0.11},
    "sku_exceptions": [
        {
            "sku_id": "industrial_group_all",
            "location_id": "DIRECT_B2B",
            "forecast_delta_pct": 30,
            "bias_history": [0.11, 0.14, 0.19, 0.23],
            "data_quality_score": 0.91,
            "trade_calendar_event": None,
        },
    ],
    "degradation_summary": {
        "wMAPE_prior": 9.1, "wMAPE_current": 13.2,
        "bias_current": 0.23, "bias_trend": [0.11, 0.14, 0.19, 0.23],
        "cycles_degraded": 4,
    },
    "pipeline_data": {
        "feed_freshness": {"DIRECT_B2B": "1 hour ago — fresh"},
        "pipeline_failures": [],
        "data_quality_scores": {"industrial_sku_group": 0.91},
        "feature_drift": {
            "acv_weighted_distribution": 0.81,
            "promo_flag_consistency": 0.98,
        },
        "model_metadata": {
            "model_id": "corning_autogluon_v12",
            "last_trained": "2023-08-01",
        },
        "trade_calendar": [],
    },
    "degradation_history": [
        {"cycle": 44, "wMAPE": 9.1,  "bias": 0.11},
        {"cycle": 45, "wMAPE": 10.3, "bias": 0.14},
        {"cycle": 46, "wMAPE": 11.8, "bias": 0.19},
        {"cycle": 47, "wMAPE": 13.2, "bias": 0.23},
    ],
}

# ── Demo scenario: Michelin cycle 47 ─────────────────────────────────────────
MICHELIN_DEMO = {
    "forecast_summary": {
        "cycle_id": "MCH-2024-047",
        "client_id": "MICHELIN",
        "total_skus": 1800,
        "skus_with_delta_above_threshold": 14,
        "segments_with_accuracy_breach": [
            {
                "segment": "commercial_truck_tires",
                "wMAPE_prior": 10.1,
                "wMAPE_current": 13.8,
                "bias": 0.19
            }
        ],
        "data_quality_flags": 1,
        "trade_calendar_events": ["Q4 fleet replacement cycle"],
    },
    "config": {
        "delta_threshold": 0.15,
        "bias_threshold": 0.15,
        "degradation_threshold_wMAPE": 2.0,
        "sustained_degradation_cycles": 3,
    },
    "escalation_flag": False,
    "prior_accuracy": {"wMAPE": 10.1, "bias": 0.07},
    "sku_exceptions": [
        {
            "sku_id": "MCH-TRUCK-SEASONAL-GROUP",
            "location_id": "ALL",
            "forecast_delta_pct": 0.25,
            "bias_history": [0.08, 0.13, 0.19],
            "data_quality_score": 0.86,
            "trade_calendar_event": "Q4 fleet replacement cycle",
        },
        {
            "sku_id": "MCH-FLEET-REPLACE-Q4",
            "location_id": "ALL",
            "forecast_delta_pct": 0.22,
            "bias_history": [0.06, 0.09, 0.14],
            "data_quality_score": 0.81,
            "trade_calendar_event": "Q4 fleet replacement cycle",
        },
        {
            "sku_id": "MCH-RETAIL-CARREFOUR-GROUP",
            "location_id": "FR",
            "forecast_delta_pct": 0.18,
            "bias_history": [0.11, 0.16, 0.21],
            "data_quality_score": 0.44,
            "trade_calendar_event": None,
        },
    ],
    "pipeline_data": {
        "feed_freshness": {
            "MICHELIN_DIST_EUROPE": "6 days ago",
            "MICHELIN_FLEET_DIRECT": "2 hours ago",
            "MICHELIN_RETAIL_FR": "fresh",
        },
        "pipeline_failures": ["MICHELIN_DIST_EUROPE: connection timeout 6 days ago"],
        "data_quality_scores": {
            "commercial_truck_tires": 0.86,
            "fleet_replacement": 0.81,
            "retail_fr": 0.44,
        },
        "feature_drift": {
            "fleet_age_distribution": 0.78,
        },
        "model_metadata": {
            "model_id": "michelin_autogluon_v8",
            "last_trained": "2024-05-15",
            "training_window": "24 months",
        },
        "trade_calendar": {
            "Q4 fleet replacement cycle": {
                "week": 44,
                "prior_year_uplift_range": "0.20-0.28",
            }
        },
    },
    "degradation_summary": {
        "wMAPE_prior": 10.1,
        "wMAPE_current": 13.8,
        "bias_current": 0.19,
        "bias_trend": "worsening",
        "cycles_degraded": 3,
    },
    "degradation_history": [
        {"cycle": 44, "wMAPE": 10.1, "bias": 0.08},
        {"cycle": 45, "wMAPE": 11.4, "bias": 0.13},
        {"cycle": 46, "wMAPE": 12.6, "bias": 0.16},
        {"cycle": 47, "wMAPE": 13.8, "bias": 0.19},
    ],
}

DEMO_SCENARIOS = {
    "hersheys_cycle_47": HERSHEYS_DEMO,
    "corning_cycle_47":  CORNING_DEMO,
    "michelin_cycle_47": MICHELIN_DEMO,
}


def get_scenarios() -> dict:
    return DEMO_SCENARIOS


if __name__ == "__main__":
    import json
    print("=" * 60)
    print("Running Hersheys Cycle 47 demo (DS role)...")
    print("=" * 60)
    results = run_full_cycle(HERSHEYS_DEMO, user_role="DS")
    print(json.dumps(results, indent=2))
