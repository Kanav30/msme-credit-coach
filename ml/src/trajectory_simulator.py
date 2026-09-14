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


def simulate_trajectory(profile: BusinessCreditProfile, monthly_effort: dict, months: int) -> list:
    """
    monthly_effort: e.g. {"credit_utilization": True, "payment_history": True}
      — whether the owner is assumed to keep logging consistent effort on
      each actionable factor every month, going forward.

    Returns a list of {month, factor_scores, overall_score, estimated_cmr_rank}
    for month 0 (today) through `months`.
    """
    current = dataclasses.replace(profile)  # work on a copy, never mutate the input
    trajectory = [{"month": 0, **compute_overall_diagnostic(current)}]

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

        trajectory.append({"month": month, **compute_overall_diagnostic(current)})

    return trajectory


def predict_time_to_target(profile: BusinessCreditProfile, monthly_effort: dict,
                            target_rank: int, max_months: int = 24) -> dict:
    """Walks the trajectory and reports the first month the target rank is reached, if ever."""
    trajectory = simulate_trajectory(profile, monthly_effort, max_months)
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
