"""
Owner-facing endpoints — the prescriptive health card view.
Phase 4 stubs: wire these up to the scoring engine once ml/ is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/owner", tags=["owner"])


@router.get("/health-card/{owner_id}")
def get_health_card(owner_id: str):
    """
    Returns the pillar-wise score + prescriptive tips for the MSME owner.
    Should NEVER expose lender-side risk-tier thresholds or internal policy logic.
    """
    raise NotImplementedError("Phase 4: connect to ScoreEngine output")
