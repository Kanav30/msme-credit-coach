"""
Owner-facing endpoints for the score improvement coach.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))

from fastapi import APIRouter, HTTPException
from feature_engineering import BusinessCreditProfile, compute_overall_diagnostic, compute_gap_to_target

router = APIRouter(prefix="/owner", tags=["owner"])

# Phase 1 mock store — replace with a real DB in a later phase
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
    """Returns prioritized recommendations, ranked by improvement headroom and speed."""
    profile = _get_profile_or_404(owner_id)
    return compute_gap_to_target(profile, target_rank)


@router.post("/log-action/{owner_id}")
def log_action(owner_id: str, action: dict):
    """Owner logs an action taken (e.g. paid down a balance, corrected a report error)."""
    raise NotImplementedError("Phase 2: store logged action + update streak")


@router.get("/prediction/{owner_id}")
def get_prediction(owner_id: str):
    """Returns projected rank movement and timeline based on logged actions."""
    raise NotImplementedError("Phase 3: connect to trajectory prediction model")
