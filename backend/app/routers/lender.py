"""
Lender-facing endpoints — the risk dashboard view.
Phase 4 stubs: wire these up to the scoring engine once ml/ is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/lender", tags=["lender"])


@router.get("/risk-dashboard/{owner_id}")
def get_risk_dashboard(owner_id: str):
    """
    Returns risk tier, PD estimate, SHAP explainability panel, and audit trail.
    Should only receive the score + explanation, never raw GST/UPI/EPFO data
    beyond what the owner consented to share (data minimization principle).
    """
    raise NotImplementedError("Phase 4: connect to ScoreEngine + SHAP output")
