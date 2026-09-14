"""
Diagnostic engine for the MSME Credit Score Improvement Coach.

IMPORTANT — read this before touching the weights below:
The real CMR formula is proprietary to TransUnion CIBIL. Nobody outside the
bureau knows the exact weights. What IS publicly documented (see docs/PROJECT_PITCH.md
sources) is the general factor breakdown and rough thresholds:
  - Payment history is the single biggest factor (~40% of the calculation)
  - Credit utilization above ~75% is a red flag; under ~60% is considered healthy
  - Longer, well-maintained credit tenure helps
  - Firm profile (age, industry risk, ownership) plays a smaller role

So this module builds a REASONABLE, TRANSPARENT APPROXIMATION of CMR behavior
using those public data points — not a reverse-engineered copy of the real
formula. Be upfront about that distinction in any report/demo: this is a
"proxy diagnostic," not the official score.
"""

from dataclasses import dataclass


# ---- Weights (documented assumption, not CIBIL's actual weights) ----
WEIGHTS = {
    "payment_history": 0.40,
    "credit_utilization": 0.25,
    "credit_tenure": 0.20,
    "firm_profile": 0.15,
}

# How quickly each factor can realistically be improved — used later to
# prioritize "quick wins" vs "slow fixes" in the action plan.
IMPROVEMENT_SPEED = {
    "payment_history": "medium (weeks to a few months of consistent on-time payments)",
    "credit_utilization": "fast (can shift within 1 billing cycle)",
    "credit_tenure": "slow (only improves as time passes)",
    "firm_profile": "slow / mostly fixed",
}

# Numeric actionability weight matching the speed labels above. This is what
# actually drives ranking — raw headroom alone is misleading, since a factor
# like "firm_profile" can show large headroom but there's nothing the owner
# can DO about it in the short term. Fast-moving factors are weighted up,
# slow/fixed ones weighted down, so the action plan leads with what's
# actually actionable rather than what's theoretically largest.
ACTIONABILITY_WEIGHT = {
    "payment_history": 0.6,
    "credit_utilization": 1.0,
    "credit_tenure": 0.15,
    "firm_profile": 0.15,
}


@dataclass
class BusinessCreditProfile:
    on_time_payment_pct: float       # 0-1, share of payments made on time (last 12 months)
    has_recent_delinquency: bool     # a late payment in the last ~3 months
    credit_utilization: float        # 0-1, current utilization ratio
    credit_tenure_years: float       # years of credit history
    business_age_years: float        # years in operation
    industry_risk_category: str      # "low", "medium", or "high"


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_payment_history(profile: BusinessCreditProfile) -> float:
    """~40% of weight. Even one recent delinquency causes a meaningful drop."""
    score = profile.on_time_payment_pct * 100
    if profile.has_recent_delinquency:
        score -= 20
    return _clamp(score)


def score_credit_utilization(profile: BusinessCreditProfile) -> float:
    """Piecewise: <=30% is ideal, 60% is the healthy ceiling, 75%+ is a red flag."""
    u = profile.credit_utilization
    if u <= 0.30:
        score = 100
    elif u <= 0.60:
        score = 100 - (u - 0.30) / 0.30 * 20        # 100 -> 80
    elif u <= 0.75:
        score = 80 - (u - 0.60) / 0.15 * 30          # 80 -> 50
    else:
        score = 50 - min((u - 0.75) / 0.25, 1) * 50  # 50 -> 0 at 100% utilization
    return _clamp(score)


def score_credit_tenure(profile: BusinessCreditProfile) -> float:
    """Diminishing returns after ~10 years of credit history."""
    return _clamp(min(profile.credit_tenure_years / 10, 1) * 100)


def score_firm_profile(profile: BusinessCreditProfile) -> float:
    """Business age + industry risk multiplier."""
    age_component = min(profile.business_age_years / 15, 1) * 100
    risk_multiplier = {"low": 1.0, "medium": 0.85, "high": 0.65}.get(
        profile.industry_risk_category, 0.85
    )
    return _clamp(age_component * risk_multiplier)


FACTOR_FUNCTIONS = {
    "payment_history": score_payment_history,
    "credit_utilization": score_credit_utilization,
    "credit_tenure": score_credit_tenure,
    "firm_profile": score_firm_profile,
}


def compute_overall_diagnostic(profile: BusinessCreditProfile) -> dict:
    """
    Returns each factor's sub-score, its weighted contribution, the overall
    proxy score (0-100), and an estimated CMR-like rank (1=best, 10=worst).
    """
    factor_scores = {name: fn(profile) for name, fn in FACTOR_FUNCTIONS.items()}
    overall_score = sum(factor_scores[name] * WEIGHTS[name] for name in WEIGHTS)

    # Map 0-100 proxy score to a CMR-like 1-10 rank (10-point buckets)
    estimated_rank = 10 - min(int(overall_score // 10), 9)

    return {
        "factor_scores": factor_scores,
        "overall_score": round(overall_score, 1),
        "estimated_cmr_rank": estimated_rank,
    }


def compute_gap_to_target(profile: BusinessCreditProfile, target_rank: int) -> dict:
    """
    Given a business's current profile and a target CMR-like rank, return
    factors ranked by how much headroom (potential score gain) each has,
    weighted by importance, plus how fast each factor can realistically move.
    """
    diagnostic = compute_overall_diagnostic(profile)
    current_rank = diagnostic["estimated_cmr_rank"]

    factor_breakdown = []
    for name, sub_score in diagnostic["factor_scores"].items():
        headroom = (100 - sub_score) * WEIGHTS[name]  # max possible weighted gain
        actionable_priority = headroom * ACTIONABILITY_WEIGHT[name]
        factor_breakdown.append({
            "factor": name,
            "current_sub_score": round(sub_score, 1),
            "weight": WEIGHTS[name],
            "improvement_headroom": round(headroom, 1),
            "actionable_priority": round(actionable_priority, 2),
            "improvement_speed": IMPROVEMENT_SPEED[name],
        })

    # Rank by actionable_priority (headroom weighted by how fast it can move),
    # NOT raw headroom — see ACTIONABILITY_WEIGHT comment above for why.
    factor_breakdown.sort(key=lambda f: f["actionable_priority"], reverse=True)

    return {
        "current_rank": current_rank,
        "target_rank": target_rank,
        "rank_gap": max(current_rank - target_rank, 0),
        "overall_score": diagnostic["overall_score"],
        "prioritized_factors": factor_breakdown,
    }
