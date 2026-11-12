"""
Trajectory simulation for the MSME Credit Score Improvement Coach (Phase 3).

This projects a business's score forward in time under an assumed pattern of
monthly effort, reusing the SAME transparent factor formulas from
feature_engineering.py — not a separately trained black box. This simulator
is the source of truth; the regression model in trajectory_model.py exists
alongside it as a faster, ML-flavored approximation.

IMPORTANT CAVEAT, stated plainly for any report/demo: this simulates a
PLAUSIBLE trajectory based on documented assumptions about how fast payment
history and utilization respond to consistent effort. It is NOT validated
against real historical CMR movement data — that data isn't available to a
student project. Treat this as a calibrated estimate, not a guarantee.
"""

from typing import Optional, Dict, Any, List
import dataclasses
from feature_engineering import BusinessCreditProfile, compute_overall_diagnostic

# Assumed monthly improvement rates when the owner is actively logging
# consistent effort toward a factor. These are documented assumptions,
# not measured real-world rates — a clear target for future refinement
# once/if any real feedback data becomes available (see Phase 5).
MONTHLY_UTILIZATION_IMPROVEMENT = 0.08   # e.g. 78% -> 70% -> 62% ...
UTILIZATION_FLOOR = 0.30                 # realistic floor; businesses still use some credit
MONTHLY_PAYMENT_PCT_IMPROVEMENT = 0.03
DELINQUENCY_AGES_OUT_AFTER_MONTHS = 3    # a "recent" delinquency stops counting as recent


def simulate_trajectory(
    profile: BusinessCreditProfile,
    monthly_effort: dict,
    months: int,
    baseline_rank: Optional[int] = None,
) -> list:
    """
    monthly_effort: e.g. {"credit_utilization": True, "payment_history": True}
      — whether the owner is assumed to keep logging consistent effort on
      each actionable factor every month, going forward.
    baseline_rank: When provided (from uploaded CIR), the simulator calibrates its baseline
      and projects rank improvements smoothly starting from the CIR document's rank.

    Returns a list of {month, factor_scores, overall_score, estimated_cmr_rank}
    for month 0 (today) through `months`.
    """
    current = dataclasses.replace(profile)  # work on a copy, never mutate the input

    # If baseline_rank is provided, calculate initial calibration shift to apply smoothly
    shift = 0.0
    if baseline_rank is not None and 1 <= baseline_rank <= 10:
        init_diag = compute_overall_diagnostic(current)
        shift = (init_diag["estimated_cmr_rank"] - baseline_rank) * 10.0

    def _get_diag(prof):
        d = compute_overall_diagnostic(prof)
        if baseline_rank is not None and 1 <= baseline_rank <= 10:
            cal_score = round(max(0.0, min(100.0, d["overall_score"] + shift)), 1)
            cal_rank = 10 - min(int(cal_score // 10), 9)
            d["raw_overall_score"] = d["overall_score"]
            d["overall_score"] = cal_score
            d["estimated_cmr_rank"] = cal_rank
            d["is_calibrated"] = True
            d["calibration_baseline_rank"] = baseline_rank
        return d

    trajectory = [{"month": 0, **_get_diag(current)}]
    months_of_clean_payment_effort = 0

    for month in range(1, months + 1):
        # Time-based factors advance regardless of effort — these are just clocks
        current.credit_tenure_years += 1 / 12
        current.business_age_years += 1 / 12

        if monthly_effort.get("credit_utilization"):
            current.credit_utilization = max(
                UTILIZATION_FLOOR, current.credit_utilization - MONTHLY_UTILIZATION_IMPROVEMENT
            )

        if monthly_effort.get("payment_history"):
            months_of_clean_payment_effort += 1
            current.on_time_payment_pct = min(1.0, current.on_time_payment_pct + MONTHLY_PAYMENT_PCT_IMPROVEMENT)
            if current.has_recent_delinquency and months_of_clean_payment_effort >= DELINQUENCY_AGES_OUT_AFTER_MONTHS:
                current.has_recent_delinquency = False

        trajectory.append({"month": month, **_get_diag(current)})

    return trajectory


def predict_time_to_target(
    profile: BusinessCreditProfile,
    monthly_effort: dict,
    target_rank: int,
    max_months: int = 24,
    baseline_rank: Optional[int] = None,
) -> dict:
    """Walks the trajectory and reports the first month the target rank is reached, if ever."""
    trajectory = simulate_trajectory(profile, monthly_effort, max_months, baseline_rank=baseline_rank)
    for point in trajectory:
        if point["estimated_cmr_rank"] <= target_rank:
            return {
                "target_reached": True,
                "months_to_target": point["month"],
                "trajectory": trajectory[: point["month"] + 1],
            }
    return {
        "target_reached": False,
        "months_to_target": None,
        "trajectory": trajectory,
        "note": f"Target not reached within {max_months} months under this effort pattern.",
    }
