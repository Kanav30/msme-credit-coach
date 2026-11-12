"""
Owner-facing endpoints for the score improvement coach.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from feature_engineering import (
    BusinessCreditProfile,
    compute_overall_diagnostic,
    generate_action_plan,
    compute_gap_to_target,
    WEIGHTS,
)
from trajectory_simulator import predict_time_to_target, simulate_trajectory
from trajectory_model import train_trajectory_model, predict_score_with_model
from alternate_data import AlternateDataSignals, compute_supplementary_signal

try:
    from app.core import logging_store as store
    from app.core import security
except ModuleNotFoundError:
    import logging_store as store
    import security

# Trained once at startup — training is fast (~1 second) since it's synthetic
# data, so this doesn't need caching to disk. See trajectory_model.py for
# what this model does and does not validate.
_trajectory_model, _trajectory_model_metrics = train_trajectory_model()

router = APIRouter(prefix="/owner", tags=["owner"])
store.init_db()

# In-memory store for active MSME profiles (populated on signup or CIBIL PDF upload)
_MOCK_PROFILES: Dict[str, BusinessCreditProfile] = {}
_PROFILE_METADATA: Dict[str, Dict[str, Any]] = {}


def get_placeholder_diagnostic() -> Dict[str, Any]:
    """Clean placeholder diagnostic when no credit report has been loaded yet."""
    return {
        "has_data": False,
        "factor_scores": {
            "payment_history": None,
            "credit_utilization": None,
            "credit_tenure": None,
            "firm_profile": None,
        },
        "overall_score": None,
        "estimated_cmr_rank": None,
    }


def get_placeholder_action_plan(target_rank: int = 3) -> Dict[str, Any]:
    """Clean placeholder action plan displaying high-leverage guidance frameworks."""
    factors = [
        {
            "factor": "credit_utilization",
            "current_sub_score": None,
            "weight": 0.25,
            "improvement_headroom": None,
            "actionable_priority": None,
            "improvement_speed": "fast (can shift within 1 billing cycle)",
            "recommendation": "Maintain revolving credit utilization strictly under 60% of sanctioned limits.",
        },
        {
            "factor": "payment_history",
            "current_sub_score": None,
            "weight": 0.40,
            "improvement_headroom": None,
            "actionable_priority": None,
            "improvement_speed": "medium (weeks to a few months of consistent on-time payments)",
            "recommendation": "Automate NACH / ECS mandates 48 hours prior to due dates to preserve zero DPD.",
        },
        {
            "factor": "credit_tenure",
            "current_sub_score": None,
            "weight": 0.20,
            "improvement_headroom": None,
            "actionable_priority": None,
            "improvement_speed": "slow (only improves as time passes)",
            "recommendation": "Keep your oldest commercial loan or CC facility open and active to build vintage.",
        },
        {
            "factor": "firm_profile",
            "current_sub_score": None,
            "weight": 0.15,
            "improvement_headroom": None,
            "actionable_priority": None,
            "improvement_speed": "slow / mostly fixed",
            "recommendation": "Ensure trade name, GSTIN, and company PAN details match bank records exactly.",
        },
    ]
    return {
        "has_data": False,
        "current_rank": None,
        "target_rank": target_rank,
        "rank_gap": None,
        "overall_score": None,
        "prioritized_factors": factors,
    }


def get_placeholder_prediction(target_rank: int = 3) -> Dict[str, Any]:
    """Clean placeholder trajectory projection awaiting logged habits or CIBIL upload."""
    return {
        "has_data": False,
        "assumed_effort_pattern": {"credit_utilization": False, "payment_history": False},
        "note": "Awaiting CIBIL CIR report or logged improvement habits.",
        "target_rank": target_rank,
        "simulator_prediction": {
            "trajectory": [],
            "target_reached": False,
            "months_to_target": None,
        },
        "regression_model_6_month_estimate": {
            "predicted_score": None,
            "model_metrics": _trajectory_model_metrics,
            "caveat": "Awaiting active business profile data.",
        },
    }


class LogActionRequest(BaseModel):
    factor: str
    description: str
    logged_at: Optional[str] = None


class AlternateSignalRequest(BaseModel):
    gst_filing_regularity: float = Field(..., ge=0.0, le=1.0)
    upi_inflow_stability: float = Field(..., ge=0.0, le=1.0)


class ProfileUpdateRequest(BaseModel):
    name: str = "My MSME Business"
    archetype: Optional[str] = "Custom Profile"
    industry_name: Optional[str] = "Manufacturing / Services"
    on_time_payment_pct: float = Field(..., ge=0.0, le=1.0)
    has_recent_delinquency: bool
    credit_utilization: float = Field(..., ge=0.0, le=1.0)
    credit_tenure_years: float = Field(..., ge=0.0, le=50.0)
    business_age_years: float = Field(..., ge=0.0, le=100.0)
    industry_risk_category: str = Field(..., pattern="^(low|medium|high)$")
    target_rank: int = Field(3, ge=1, le=10)
    gst_filing_regularity: float = Field(0.80, ge=0.0, le=1.0)
    upi_inflow_stability: float = Field(0.80, ge=0.0, le=1.0)


class WhatIfSimulateRequest(BaseModel):
    monthly_effort: Dict[str, bool] = {"credit_utilization": True, "payment_history": True}
    target_rank: int = Field(3, ge=1, le=10)
    max_months: int = Field(24, ge=1, le=60)


def _get_profile_or_none(owner_id: str) -> Optional[BusinessCreditProfile]:
    if owner_id in _MOCK_PROFILES:
        return _MOCK_PROFILES[owner_id]
    db_p = store.get_business_profile(owner_id)
    if db_p and db_p.get("on_time_payment_pct") is not None:
        prof = BusinessCreditProfile(
            on_time_payment_pct=float(db_p["on_time_payment_pct"]),
            has_recent_delinquency=bool(db_p["has_recent_delinquency"]),
            credit_utilization=float(db_p["credit_utilization"]),
            credit_tenure_years=float(db_p["credit_tenure_years"]),
            business_age_years=float(db_p["business_age_years"]),
            industry_risk_category=db_p.get("industry_risk_category", "medium"),
        )
        _MOCK_PROFILES[owner_id] = prof
        return prof
    return None


@router.get("/profiles")
def list_profiles(current_user: Dict[str, Any] = Depends(security.get_current_user)):
    """Lists registered MSME profiles belonging to the authenticated owner."""
    owner_id = current_user["owner_id"]
    profile = _get_profile_or_none(owner_id)
    meta = _PROFILE_METADATA.get(owner_id, {
        "name": current_user.get("business_name", "My Business"),
        "archetype": "Registered Business",
        "industry_name": "Commercial MSME",
        "target_rank": current_user.get("target_rank", 3),
        "gst_filing_regularity": 0.8,
        "upi_inflow_stability": 0.8,
    })

    result = []
    reports = store.get_cibil_reports(owner_id)
    official_cmr = reports[0].get("official_cmr_rank") if reports else None
    illustrative_cmr = reports[0].get("illustrative_cmr_rank") if reports else None
    rank_source = reports[0].get("rank_source") if reports else None

    if profile:
        diag = compute_overall_diagnostic(profile)
        result.append({
            "owner_id": owner_id,
            "name": meta.get("name", current_user.get("business_name", owner_id)),
            "archetype": meta.get("archetype", "Registered Business"),
            "industry_name": meta.get("industry_name", "Commercial MSME"),
            "industry_risk_category": profile.industry_risk_category,
            "target_rank": meta.get("target_rank", current_user.get("target_rank", 3)),
            "official_cmr_rank": official_cmr,
            "illustrative_cmr_rank": illustrative_cmr,
            "rank_source": rank_source,
            "estimated_cmr_rank": diag["estimated_cmr_rank"],
            "overall_score": diag["overall_score"],
            "on_time_payment_pct": profile.on_time_payment_pct,
            "has_recent_delinquency": profile.has_recent_delinquency,
            "credit_utilization": profile.credit_utilization,
            "credit_tenure_years": profile.credit_tenure_years,
            "business_age_years": profile.business_age_years,
            "gst_filing_regularity": meta.get("gst_filing_regularity", 0.8),
            "upi_inflow_stability": meta.get("upi_inflow_stability", 0.8),
        })
    else:
        result.append({
            "owner_id": owner_id,
            "name": current_user.get("business_name", "My Business"),
            "archetype": "Awaiting CIBIL Report",
            "industry_name": "Commercial MSME",
            "industry_risk_category": current_user.get("industry_category", "medium"),
            "target_rank": current_user.get("target_rank", 3),
            "official_cmr_rank": official_cmr,
            "illustrative_cmr_rank": illustrative_cmr,
            "rank_source": rank_source,
            "estimated_cmr_rank": None,
            "overall_score": None,
            "on_time_payment_pct": None,
            "has_recent_delinquency": None,
            "credit_utilization": None,
            "credit_tenure_years": None,
            "business_age_years": None,
            "gst_filing_regularity": 0.8,
            "upi_inflow_stability": 0.8,
        })

    return {"profiles": result}


@router.get("/profile/{owner_id}")
def get_profile(owner_id: str, current_user: Dict[str, Any] = Depends(security.get_current_user)):
    """Returns the full configuration and metadata for a specific owner, or placeholder if none loaded."""
    security.verify_owner_access(owner_id, current_user)
    profile = _get_profile_or_none(owner_id)
    reports = store.get_cibil_reports(owner_id)
    official_cmr = reports[0].get("official_cmr_rank") if reports else None
    illustrative_cmr = reports[0].get("illustrative_cmr_rank") if reports else None
    rank_source = reports[0].get("rank_source") if reports else None

    if profile is None:
        user = store.get_user_by_owner_id(owner_id)
        biz_name = user["business_name"] if user else current_user.get("business_name", "My Business")
        return {
            "owner_id": owner_id,
            "has_data": False,
            "metadata": {
                "name": biz_name,
                "archetype": "Awaiting CIBIL Report",
                "industry_name": "Commercial MSME",
                "target_rank": current_user.get("target_rank", 3),
                "gst_filing_regularity": 0.80,
                "upi_inflow_stability": 0.80,
            },
            "profile": None,
            "diagnostic_preview": get_placeholder_diagnostic(),
            "official_cmr_rank": official_cmr,
            "illustrative_cmr_rank": illustrative_cmr,
            "rank_source": rank_source,
        }

    meta = _PROFILE_METADATA.get(owner_id, {
        "name": current_user.get("business_name", owner_id),
        "archetype": "Custom MSME",
        "industry_name": "MSME Enterprise",
        "target_rank": current_user.get("target_rank", 3),
        "gst_filing_regularity": 0.80,
        "upi_inflow_stability": 0.80,
    })
    diag = compute_overall_diagnostic(profile)
    return {
        "owner_id": owner_id,
        "has_data": True,
        "metadata": meta,
        "profile": {
            "on_time_payment_pct": profile.on_time_payment_pct,
            "has_recent_delinquency": profile.has_recent_delinquency,
            "credit_utilization": profile.credit_utilization,
            "credit_tenure_years": profile.credit_tenure_years,
            "business_age_years": profile.business_age_years,
            "industry_risk_category": profile.industry_risk_category,
        },
        "diagnostic_preview": diag,
        "official_cmr_rank": official_cmr,
        "illustrative_cmr_rank": illustrative_cmr,
        "rank_source": rank_source,
    }


@router.post("/profile/{owner_id}")
@router.put("/profile/{owner_id}")
def save_or_update_profile(
    owner_id: str,
    req: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Create or update an MSME profile parameters."""
    security.verify_owner_access(owner_id, current_user)
    profile = BusinessCreditProfile(
        on_time_payment_pct=req.on_time_payment_pct,
        has_recent_delinquency=req.has_recent_delinquency,
        credit_utilization=req.credit_utilization,
        credit_tenure_years=req.credit_tenure_years,
        business_age_years=req.business_age_years,
        industry_risk_category=req.industry_risk_category,
    )
    _MOCK_PROFILES[owner_id] = profile
    _PROFILE_METADATA[owner_id] = {
        "name": req.name,
        "archetype": req.archetype or "Custom Profile",
        "industry_name": req.industry_name or "General Business",
        "target_rank": req.target_rank,
        "gst_filing_regularity": req.gst_filing_regularity,
        "upi_inflow_stability": req.upi_inflow_stability,
    }
    diag = compute_overall_diagnostic(profile)
    try:
        store.save_business_profile(
            owner_id,
            {
                "on_time_payment_pct": req.on_time_payment_pct,
                "has_recent_delinquency": req.has_recent_delinquency,
                "credit_utilization": req.credit_utilization,
                "credit_tenure_years": req.credit_tenure_years,
                "business_age_years": req.business_age_years,
                "industry_risk_category": req.industry_risk_category,
                "estimated_cmr_rank": diag["estimated_cmr_rank"],
                "overall_proxy_score": diag["overall_score"],
                "source": "manual_sandbox",
            },
        )
        store.save_alternate_signals(
            owner_id,
            req.gst_filing_regularity,
            req.upi_inflow_stability,
            "Moderate Cash-Flow Stability",
        )
    except Exception as e:
        print(f"[Warning] Could not persist profile to DB: {e}")

    return {
        "status": "success",
        "owner_id": owner_id,
        "message": f"Profile '{req.name}' successfully updated.",
        "estimated_cmr_rank": diag["estimated_cmr_rank"],
        "overall_score": diag["overall_score"],
    }


@router.get("/diagnostic/{owner_id}")
def get_diagnostic(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Returns the factor-by-factor breakdown of what's affecting the owner's CMR."""
    security.verify_owner_access(owner_id, current_user)
    profile = _get_profile_or_none(owner_id)
    reports = store.get_cibil_reports(owner_id)
    official_cmr = reports[0].get("official_cmr_rank") if reports else None
    illustrative_cmr = reports[0].get("illustrative_cmr_rank") if reports else None
    rank_source = reports[0].get("rank_source") if reports else None

    if profile is None:
        placeholder = get_placeholder_diagnostic()
        placeholder["official_cmr_rank"] = official_cmr
        placeholder["illustrative_cmr_rank"] = illustrative_cmr
        placeholder["rank_source"] = rank_source
        return placeholder

    diag = compute_overall_diagnostic(profile)
    diag["has_data"] = True
    diag["official_cmr_rank"] = official_cmr
    diag["illustrative_cmr_rank"] = illustrative_cmr
    diag["rank_source"] = rank_source
    if reports:
        diag["report_date"] = reports[0].get("report_date")
        diag["rcn"] = reports[0].get("rcn")
        diag["company_name"] = reports[0].get("company_name")
    return diag


@router.get("/action-plan/{owner_id}")
def get_action_plan(
    owner_id: str,
    target_rank: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Returns prioritized recommendations with specific advice text per factor."""
    security.verify_owner_access(owner_id, current_user)
    profile = _get_profile_or_none(owner_id)
    meta = _PROFILE_METADATA.get(owner_id, {})
    eff_target = target_rank if target_rank is not None else meta.get("target_rank", current_user.get("target_rank", 3))
    if profile is None:
        return get_placeholder_action_plan(eff_target)
    plan = generate_action_plan(profile, eff_target)
    plan["has_data"] = True
    return plan


@router.post("/log-action/{owner_id}")
def log_action(
    owner_id: str,
    action: LogActionRequest,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Owner logs an action taken (e.g. paid down a balance, corrected a report error)."""
    security.verify_owner_access(owner_id, current_user)
    valid_factors = {"payment_history", "credit_utilization", "credit_tenure", "firm_profile"}
    if action.factor not in valid_factors:
        raise HTTPException(status_code=400, detail=f"factor must be one of {valid_factors}")
    return store.log_action(owner_id, action.factor, action.description, action.logged_at)


@router.delete("/action/{action_id}")
def delete_action(
    action_id: int,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Deletes an action record by ID with strict ownership validation."""
    success = store.delete_action(action_id, owner_id=current_user["owner_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found or you do not have permission to delete it.",
        )
    return {"status": "deleted", "id": action_id}


@router.get("/log-history/{owner_id}")
def get_log_history(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Returns all logged actions for this owner, most recent first."""
    security.verify_owner_access(owner_id, current_user)
    return {"owner_id": owner_id, "actions": store.get_actions(owner_id)}


@router.post("/reset-history/{owner_id}")
def reset_owner_history(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Clears all logged actions for a specific owner to test streak building from scratch."""
    security.verify_owner_access(owner_id, current_user)
    store.reset_actions_for_owner(owner_id)
    return {"status": "cleared", "owner_id": owner_id, "actions": []}


@router.post("/reset-profile/{owner_id}")
def reset_profile(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Clears any uploaded profile and actions for this owner and resets to clean placeholder state."""
    security.verify_owner_access(owner_id, current_user)
    _MOCK_PROFILES.pop(owner_id, None)
    _PROFILE_METADATA.pop(owner_id, None)
    store.reset_actions_for_owner(owner_id)
    return {"status": "cleared", "owner_id": owner_id}


@router.get("/streak/{owner_id}")
def get_streak(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """Returns the current consecutive-week logging streak."""
    security.verify_owner_access(owner_id, current_user)
    weeks = store.compute_streak_weeks(owner_id)
    return {"owner_id": owner_id, "streak_weeks": weeks}


@router.get("/prediction/{owner_id}")
def get_prediction(
    owner_id: str,
    target_rank: Optional[int] = None,
    max_months: int = 24,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Projects rank movement using the factors the owner has ACTUALLY been
    logging effort toward (from Phase 2 history) — not a generic what-if.
    Returns both the deterministic simulator's answer (source of truth) and
    the regression model's estimate.
    """
    security.verify_owner_access(owner_id, current_user)
    profile = _get_profile_or_none(owner_id)
    meta = _PROFILE_METADATA.get(owner_id, {})
    eff_target = target_rank if target_rank is not None else meta.get("target_rank", current_user.get("target_rank", 3))

    if profile is None:
        return get_placeholder_prediction(eff_target)

    logged_actions = store.get_actions(owner_id)
    logged_factors = {a["factor"] for a in logged_actions}
    monthly_effort = {
        "credit_utilization": "credit_utilization" in logged_factors,
        "payment_history": "payment_history" in logged_factors,
    }

    simulator_result = predict_time_to_target(profile, monthly_effort, eff_target, max_months)
    model_estimate_6mo = predict_score_with_model(_trajectory_model, profile, monthly_effort, months_horizon=6)

    return {
        "has_data": True,
        "assumed_effort_pattern": monthly_effort,
        "note": (
            "assumed_effort_pattern is derived from factors you've logged actions "
            "for at least once — it assumes you keep up similar consistent effort going forward."
        ),
        "target_rank": eff_target,
        "simulator_prediction": simulator_result,
        "regression_model_6_month_estimate": {
            "predicted_score": model_estimate_6mo,
            "model_metrics": _trajectory_model_metrics,
            "caveat": "Trained on synthetic simulator data — validates the model learned the "
                      "simulator's logic, not real-world CMR accuracy.",
        },
    }


@router.post("/simulate-what-if/{owner_id}")
def simulate_what_if(
    owner_id: str,
    req: WhatIfSimulateRequest,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Interactive 'What-If' sandbox projection: simulates trajectory given explicit
    hypothetical effort toggles without requiring logged actions in database.
    """
    security.verify_owner_access(owner_id, current_user)
    profile = _get_profile_or_none(owner_id)
    if profile is None:
        # Default baseline for interactive what-if simulation when no profile is loaded
        profile = BusinessCreditProfile(
            on_time_payment_pct=0.80,
            has_recent_delinquency=True,
            credit_utilization=0.75,
            credit_tenure_years=2.0,
            business_age_years=3.0,
            industry_risk_category="medium",
        )

    simulator_result = predict_time_to_target(profile, req.monthly_effort, req.target_rank, req.max_months)
    model_estimate_6mo = predict_score_with_model(_trajectory_model, profile, req.monthly_effort, months_horizon=6)

    return {
        "assumed_effort_pattern": req.monthly_effort,
        "target_rank": req.target_rank,
        "simulator_prediction": simulator_result,
        "regression_model_6_month_estimate": {
            "predicted_score": model_estimate_6mo,
            "model_metrics": _trajectory_model_metrics,
        },
    }


@router.post("/alternate-signal/{owner_id}")
def get_alternate_signal(
    owner_id: str,
    signals: AlternateSignalRequest,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Phase 4 (stretch goal): a SEPARATE supplementary early-indicator layer
    from GST/UPI patterns. Deliberately does not touch or blend into the
    core diagnostic, action plan, or prediction above — see alternate_data.py
    for why.
    """
    security.verify_owner_access(owner_id, current_user)
    return compute_supplementary_signal(
        AlternateDataSignals(
            gst_filing_regularity=signals.gst_filing_regularity,
            upi_inflow_stability=signals.upi_inflow_stability,
        )
    )
    return compute_supplementary_signal(
        AlternateDataSignals(
            gst_filing_regularity=signals.gst_filing_regularity,
            upi_inflow_stability=signals.upi_inflow_stability,
        )
    )
