"""
Owner-facing endpoints for the score improvement coach.
Phase 2 stubs — wire these up once the diagnostic engine (ml/) is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/owner", tags=["owner"])


@router.get("/diagnostic/{owner_id}")
def get_diagnostic(owner_id: str):
    """Returns the factor-by-factor breakdown of what's affecting the owner's CMR."""
    raise NotImplementedError("Phase 1-2: connect to diagnostic engine")


@router.get("/action-plan/{owner_id}")
def get_action_plan(owner_id: str):
    """Returns prioritized recommendations, ranked by impact and speed."""
    raise NotImplementedError("Phase 2: connect to recommendation engine")


@router.post("/log-action/{owner_id}")
def log_action(owner_id: str, action: dict):
    """Owner logs an action taken (e.g. paid down a balance, corrected a report error)."""
    raise NotImplementedError("Phase 2: store logged action + update streak")


@router.get("/prediction/{owner_id}")
def get_prediction(owner_id: str):
    """Returns projected rank movement and timeline based on logged actions."""
    raise NotImplementedError("Phase 3: connect to trajectory prediction model")
