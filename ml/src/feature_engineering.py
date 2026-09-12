"""
Diagnostic engine for the MSME Credit Score Improvement Coach.

Unlike a trained ML classifier, this is intentionally RULE-BASED — it should
mirror the known, public CMR scoring factor weights so the diagnostic is
transparent and explainable, not a black box. Phase 1 stubs below.
"""

import pandas as pd


def score_payment_history(df: pd.DataFrame) -> pd.Series:
    """~40% of CMR weight. Based on on-time vs. late payment history."""
    raise NotImplementedError("Phase 1: implement using logged/reported payment history")


def score_credit_utilization(df: pd.DataFrame) -> pd.Series:
    """Utilization above ~75% is a red flag; under ~60% is considered healthy."""
    raise NotImplementedError("Phase 1: implement using reported credit limit vs. usage")


def score_credit_tenure(df: pd.DataFrame) -> pd.Series:
    """Longer, well-maintained credit history improves this factor."""
    raise NotImplementedError("Phase 1: implement using years in operation / credit age")


def score_firm_profile(df: pd.DataFrame) -> pd.Series:
    """Business age, ownership type, industry risk category."""
    raise NotImplementedError("Phase 1: implement using firm profile inputs")


def compute_gap_to_target(current_rank: int, target_rank: int) -> dict:
    """
    Phase 1: given current CMR (1-10, lower is better) and a target rank,
    return which factors are contributing most to the gap, ranked by
    estimated impact and how quickly each can realistically be improved.
    """
    raise NotImplementedError("Phase 1: implement gap analysis using the factor scores above")
