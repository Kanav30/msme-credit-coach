"""
Owner-facing endpoints for the score improvement coach.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from feature_engineering import BusinessCreditProfile, compute_overall_diagnostic, generate_action_plan
import logging_store as store

router = APIRouter(prefix="/owner", tags=["owner"])
store.init_db()

# Phase 1/2 mock profile store — replace with a real DB in a later phase
_MOCK_PROFILES = {
    "demo-owner-1": BusinessCreditProfile(
        on_time_payment_pct=0.80,
        has_recent_delinquency=True,
        credit_utilization=0.78,
        credit_tenure_years=3,
        business_age_years=6,
        industry_risk_category="medium",
    )
}


class LogActionRequest(BaseModel):
    factor: str
    description: str


def _get_profile_or_404(owner_id: str) -> BusinessCreditProfile:
    profile = _MOCK_PROFILES.get(owner_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"No profile found for owner_id={owner_id}")
    return profile


@router.get("/diagnostic/{owner_id}")
def get_diagnostic(owner_id: str):
    """Returns the factor-by-factor breakdown of what's affecting the owner's CMR."""
    profile = _get_profile_or_404(owner_id)
    return compute_overall_diagnostic(profile)


@router.get("/action-plan/{owner_id}")
def get_action_plan(owner_id: str, target_rank: int = 3):
    """Returns prioritized recommendations with specific advice text per factor."""
    profile = _get_profile_or_404(owner_id)
    return generate_action_plan(profile, target_rank)


@router.post("/log-action/{owner_id}")
def log_action(owner_id: str, action: LogActionRequest):
    """Owner logs an action taken (e.g. paid down a balance, corrected a report error)."""
    valid_factors = {"payment_history", "credit_utilization", "credit_tenure", "firm_profile"}
    if action.factor not in valid_factors:
        raise HTTPException(status_code=400, detail=f"factor must be one of {valid_factors}")
    return store.log_action(owner_id, action.factor, action.description)


@router.get("/log-history/{owner_id}")
def get_log_history(owner_id: str):
    """Returns all logged actions for this owner, most recent first."""
    return {"owner_id": owner_id, "actions": store.get_actions(owner_id)}


@router.get("/streak/{owner_id}")
def get_streak(owner_id: str):
    """Returns the current consecutive-week logging streak."""
    weeks = store.compute_streak_weeks(owner_id)
    return {"owner_id": owner_id, "streak_weeks": weeks}


@router.get("/prediction/{owner_id}")
def get_prediction(owner_id: str):
    """Returns projected rank movement and timeline based on logged actions."""
    raise NotImplementedError("Phase 3: connect to trajectory prediction model")
