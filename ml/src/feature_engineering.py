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
from typing import Optional, Dict, Any


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


def compute_overall_diagnostic(
    profile: BusinessCreditProfile,
    baseline_rank: Optional[int] = None,
) -> dict:
    """
    Returns each factor's sub-score, its weighted contribution, the overall
    proxy score (0-100), and an estimated CMR-like rank (1=best, 10=worst).
    When baseline_rank (from an uploaded CIR report, official or illustrative)
    is provided, the proxy baseline is calibrated to align closely with the CIR document.
    """
    factor_scores = {name: fn(profile) for name, fn in FACTOR_FUNCTIONS.items()}
    raw_score = sum(factor_scores[name] * WEIGHTS[name] for name in WEIGHTS)
    raw_rank = 10 - min(int(raw_score // 10), 9)

    if baseline_rank is not None and 1 <= baseline_rank <= 10:
        shift = (raw_rank - baseline_rank) * 10.0
        calibrated_score = round(max(0.0, min(100.0, raw_score + shift)), 1)
        estimated_rank = 10 - min(int(calibrated_score // 10), 9)
        # Ensure exact match if right at border
        if estimated_rank != baseline_rank:
            estimated_rank = baseline_rank
            band_min = (10 - baseline_rank) * 10.0
            calibrated_score = round(band_min + (raw_score % 10.0), 1)
        is_calibrated = True
    else:
        calibrated_score = round(raw_score, 1)
        estimated_rank = raw_rank
        is_calibrated = False

    return {
        "factor_scores": factor_scores,
        "overall_score": calibrated_score,
        "raw_overall_score": round(raw_score, 1),
        "estimated_cmr_rank": estimated_rank,
        "is_calibrated": is_calibrated,
        "calibration_baseline_rank": baseline_rank if is_calibrated else None,
    }


def compute_gap_to_target(
    profile: BusinessCreditProfile,
    target_rank: int,
    baseline_rank: Optional[int] = None,
) -> dict:
    """
    Given a business's current profile and a target CMR-like rank, return
    factors ranked by how much headroom (potential score gain) each has,
    weighted by importance, plus how fast each factor can realistically move.
    """
    diagnostic = compute_overall_diagnostic(profile, baseline_rank=baseline_rank)
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


def generate_recommendation_text(factor: str, profile: BusinessCreditProfile, sub_score: float) -> str:
    """
    Phase 2: turns a factor + its current state into a specific, human-readable
    recommendation. Kept as explicit if/else logic (not templated strings with
    generic filler) so each message reflects the business's actual numbers.
    """
    if factor == "payment_history":
        if profile.has_recent_delinquency:
            return (
                "You have a recent late payment, which is actively hurting your score right now. "
                "Set up autopay or reminders immediately — a second recent delinquency compounds the damage."
            )
        elif profile.on_time_payment_pct < 1.0:
            pct = round(profile.on_time_payment_pct * 100)
            return (
                f"You're paying on time {pct}% of the time. Push this to 100% for the next 3-6 months — "
                "payment history is the single biggest factor in your score."
            )
        return "Your payment history is excellent. This is your strongest asset — keep it that way."

    if factor == "credit_utilization":
        pct = round(profile.credit_utilization * 100)
        if profile.credit_utilization > 0.75:
            return (
                f"Your credit utilization is {pct}%, well above the 75% danger threshold. "
                "Pay down balances or request a credit limit increase to get under 60% — "
                "this is your fastest lever, results can show within a single billing cycle."
            )
        elif profile.credit_utilization > 0.60:
            return f"Your utilization ({pct}%) is above the ideal 60% threshold. Bringing it down would meaningfully help."
        return "Your utilization is in a healthy range. Maintain this."

    if factor == "credit_tenure":
        if sub_score < 50:
            years_to_strong = max(round(10 * (1 - sub_score / 100)), 1)
            return (
                f"Your credit history is still building (equivalent to a {sub_score:.0f}/100 tenure score). "
                f"There's no shortcut here — keep accounts open and active, and expect roughly "
                f"{years_to_strong} more year(s) before this stops being a drag on your score."
            )
        return "Your credit tenure is solid and continuing to help you."

    if factor == "firm_profile":
        if sub_score < 50:
            if profile.industry_risk_category == "high":
                return (
                    "Your industry is classified as higher-risk, and your firm profile score "
                    "reflects that. Diversifying revenue sources or building a longer operating "
                    "track record can help offset this over time."
                )
            return (
                f"Your firm profile score ({sub_score:.0f}/100) is being held back mainly by "
                "business age — this improves naturally over time, there's no faster fix here."
            )
        return "Your firm profile is in reasonable shape."

    return ""


def generate_action_plan(
    profile: BusinessCreditProfile,
    target_rank: int,
    baseline_rank: Optional[int] = None,
) -> dict:
    """
    Phase 2: the full action plan an owner actually sees — gap analysis plus
    specific recommendation text per factor, still ordered by actionable priority.
    Calibrates baseline rank and gap to baseline_rank if provided.
    """
    gap = compute_gap_to_target(profile, target_rank, baseline_rank=baseline_rank)
    for factor_entry in gap["prioritized_factors"]:
        factor_entry["recommendation"] = generate_recommendation_text(
            factor_entry["factor"], profile, factor_entry["current_sub_score"]
        )
    return gap
