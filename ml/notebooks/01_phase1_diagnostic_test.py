"""
Phase 1 — testing the diagnostic engine on realistic example profiles.
Run with: python 01_phase1_diagnostic_test.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from feature_engineering import BusinessCreditProfile, compute_overall_diagnostic, compute_gap_to_target
import json


def print_diagnostic(name, profile, target_rank):
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    diag = compute_overall_diagnostic(profile)
    print(f"Overall proxy score: {diag['overall_score']}/100")
    print(f"Estimated CMR rank: {diag['estimated_cmr_rank']}")

    gap = compute_gap_to_target(profile, target_rank)
    print(f"Target rank: {target_rank}  |  Rank gap: {gap['rank_gap']}")
    print("\nPrioritized factors (biggest improvement opportunity first):")
    for f in gap["prioritized_factors"]:
        print(f"  - {f['factor']:20s} sub-score={f['current_sub_score']:5.1f}  "
              f"headroom={f['improvement_headroom']:5.1f}  speed={f['improvement_speed']}")


# Example 1: the exact scenario discussed — CMR-6-ish business wanting CMR-3
profile_1 = BusinessCreditProfile(
    on_time_payment_pct=0.80,
    has_recent_delinquency=True,
    credit_utilization=0.78,
    credit_tenure_years=3,
    business_age_years=6,
    industry_risk_category="medium",
)
print_diagnostic("Example 1: struggling MSME wanting a better loan rate", profile_1, target_rank=3)

# Example 2: a healthier business, small gap to close
profile_2 = BusinessCreditProfile(
    on_time_payment_pct=0.97,
    has_recent_delinquency=False,
    credit_utilization=0.45,
    credit_tenure_years=8,
    business_age_years=12,
    industry_risk_category="low",
)
print_diagnostic("Example 2: healthier MSME, minor gap", profile_2, target_rank=2)

# Example 3: new business, thin credit file
profile_3 = BusinessCreditProfile(
    on_time_payment_pct=1.0,
    has_recent_delinquency=False,
    credit_utilization=0.20,
    credit_tenure_years=0.5,
    business_age_years=1,
    industry_risk_category="medium",
)
print_diagnostic("Example 3: new-to-credit MSME, thin file", profile_3, target_rank=4)
